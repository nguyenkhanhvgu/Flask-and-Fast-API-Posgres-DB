"""
Exercise validation service for managing exercise submissions and hints.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid
from datetime import datetime

from ..models import Exercise, ExerciseTestCase, ExerciseHint, ExerciseSubmission, User
from ..database import get_db
from .code_execution import code_execution_service


class ExerciseValidationService:
    """Service for validating exercise submissions and managing hints."""
    
    def __init__(self):
        self.code_executor = code_execution_service
    
    async def submit_exercise(
        self,
        db: Session,
        exercise_id: uuid.UUID,
        user_id: uuid.UUID,
        submitted_code: str
    ) -> Dict[str, Any]:
        """
        Submit and validate an exercise solution.
        
        Args:
            db: Database session
            exercise_id: Exercise identifier
            user_id: User identifier
            submitted_code: User's submitted code
            
        Returns:
            Dict containing submission results
        """
        # Get exercise with test cases
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            raise ValueError(f"Exercise {exercise_id} not found")
        
        # Get test cases
        test_cases = db.query(ExerciseTestCase).filter(
            ExerciseTestCase.exercise_id == exercise_id
        ).order_by(ExerciseTestCase.order_index).all()
        
        if not test_cases:
            raise ValueError(f"No test cases found for exercise {exercise_id}")
        
        # Convert test cases to format expected by code executor
        test_case_data = [
            {
                "input_data": tc.input_data or "",
                "expected_output": tc.expected_output,
                "is_hidden": tc.is_hidden
            }
            for tc in test_cases
        ]
        
        # Validate solution
        validation_result = await self.code_executor.validate_exercise_solution(
            str(exercise_id),
            submitted_code,
            test_case_data
        )
        
        # Create submission record
        submission = ExerciseSubmission(
            exercise_id=exercise_id,
            user_id=user_id,
            submitted_code=submitted_code,
            is_correct=validation_result["overall_success"],
            score=validation_result["score"],
            execution_time=validation_result["total_execution_time"],
            error_message=self._extract_error_message(validation_result)
        )
        
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        # Prepare response (hide hidden test case details)
        response_test_results = []
        for test_result in validation_result["test_results"]:
            response_test_results.append({
                "test_case_id": test_result["test_case_id"],
                "passed": test_result["passed"],
                "input": test_result["input"],
                "expected_output": test_result["expected_output"],
                "actual_output": test_result["actual_output"] if not test_result["input"] == "[Hidden]" else "[Hidden]",
                "execution_time": test_result["execution_time"],
                "error": test_result["error"]
            })
        
        return {
            "submission_id": submission.id,
            "exercise_id": exercise_id,
            "is_correct": validation_result["overall_success"],
            "score": validation_result["score"],
            "total_tests": validation_result["total_tests"],
            "passed_tests": validation_result["passed_tests"],
            "failed_tests": validation_result["failed_tests"],
            "test_results": response_test_results,
            "execution_time": validation_result["total_execution_time"],
            "submitted_at": submission.submitted_at
        }
    
    async def execute_code(
        self,
        code: str,
        input_data: Optional[str] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute code without validation (for testing/experimentation).
        
        Args:
            code: Python code to execute
            input_data: Optional input data
            timeout: Execution timeout in seconds
            
        Returns:
            Dict containing execution results
        """
        return await self.code_executor.execute_code(code, input_data, timeout)
    
    def get_exercise_hints(
        self,
        db: Session,
        exercise_id: uuid.UUID,
        user_id: uuid.UUID,
        max_hints: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get hints for an exercise based on user's progress.
        
        Args:
            db: Database session
            exercise_id: Exercise identifier
            user_id: User identifier
            max_hints: Maximum number of hints to return
            
        Returns:
            List of hints
        """
        # Get user's submission attempts for this exercise
        attempts = db.query(ExerciseSubmission).filter(
            and_(
                ExerciseSubmission.exercise_id == exercise_id,
                ExerciseSubmission.user_id == user_id
            )
        ).count()
        
        # Get hints for the exercise
        hints_query = db.query(ExerciseHint).filter(
            ExerciseHint.exercise_id == exercise_id
        ).order_by(ExerciseHint.order_index)
        
        if max_hints:
            hints_query = hints_query.limit(max_hints)
        
        hints = hints_query.all()
        
        # Progressive hint unlocking based on attempts
        available_hints = []
        for i, hint in enumerate(hints):
            # Unlock hints progressively: first hint after 1 attempt, second after 2, etc.
            if attempts > i:
                available_hints.append({
                    "id": hint.id,
                    "hint_text": hint.hint_text,
                    "order_index": hint.order_index,
                    "unlocked": True
                })
            else:
                available_hints.append({
                    "id": hint.id,
                    "hint_text": f"Hint {i + 1} (unlocked after {i + 1} attempts)",
                    "order_index": hint.order_index,
                    "unlocked": False
                })
        
        return available_hints
    
    async def compare_with_solution(
        self,
        db: Session,
        exercise_id: uuid.UUID,
        submitted_code: str
    ) -> Dict[str, Any]:
        """
        Compare submitted code with the reference solution.
        
        Args:
            db: Database session
            exercise_id: Exercise identifier
            submitted_code: User's submitted code
            
        Returns:
            Dict containing comparison results
        """
        # Get exercise with solution
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            raise ValueError(f"Exercise {exercise_id} not found")
        
        if not exercise.solution_code:
            raise ValueError(f"No reference solution available for exercise {exercise_id}")
        
        # Get test cases
        test_cases = db.query(ExerciseTestCase).filter(
            ExerciseTestCase.exercise_id == exercise_id
        ).order_by(ExerciseTestCase.order_index).all()
        
        test_case_data = [
            {
                "input_data": tc.input_data or "",
                "expected_output": tc.expected_output,
                "is_hidden": tc.is_hidden
            }
            for tc in test_cases
        ]
        
        # Compare solutions
        comparison_result = await self.code_executor.compare_with_solution(
            submitted_code,
            exercise.solution_code,
            test_case_data
        )
        
        return {
            "exercise_id": exercise_id,
            "matches_reference": comparison_result["matches_reference"],
            "submitted_score": comparison_result["submitted_solution"]["score"],
            "reference_score": comparison_result["reference_solution"]["score"],
            "submitted_passed": comparison_result["submitted_solution"]["passed_tests"],
            "reference_passed": comparison_result["reference_solution"]["passed_tests"],
            "total_tests": comparison_result["submitted_solution"]["total_tests"]
        }
    
    def get_user_submissions(
        self,
        db: Session,
        user_id: uuid.UUID,
        exercise_id: Optional[uuid.UUID] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get user's exercise submissions.
        
        Args:
            db: Database session
            user_id: User identifier
            exercise_id: Optional exercise filter
            limit: Maximum number of submissions to return
            
        Returns:
            List of submissions
        """
        query = db.query(ExerciseSubmission).filter(
            ExerciseSubmission.user_id == user_id
        )
        
        if exercise_id:
            query = query.filter(ExerciseSubmission.exercise_id == exercise_id)
        
        submissions = query.order_by(
            ExerciseSubmission.submitted_at.desc()
        ).limit(limit).all()
        
        return [
            {
                "id": sub.id,
                "exercise_id": sub.exercise_id,
                "submitted_code": sub.submitted_code,
                "is_correct": sub.is_correct,
                "score": sub.score,
                "execution_time": sub.execution_time,
                "error_message": sub.error_message,
                "submitted_at": sub.submitted_at
            }
            for sub in submissions
        ]
    
    def _extract_error_message(self, validation_result: Dict[str, Any]) -> Optional[str]:
        """Extract error message from validation result."""
        if validation_result["overall_success"]:
            return None
        
        # Find first failed test with error
        for test_result in validation_result["test_results"]:
            if not test_result["passed"] and test_result.get("error"):
                return test_result["error"]
        
        # If no specific error, return general failure message
        failed_count = validation_result["failed_tests"]
        total_count = validation_result["total_tests"]
        return f"Failed {failed_count} out of {total_count} test cases"


# Global instance
exercise_validation_service = ExerciseValidationService()