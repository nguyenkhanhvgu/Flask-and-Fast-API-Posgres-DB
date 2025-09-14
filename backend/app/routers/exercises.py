"""
API routes for exercise management, code execution, and validation.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..services.exercise_validation import exercise_validation_service
from ..schemas import (
    ExerciseSubmissionCreate,
    ExerciseSubmissionResponse
)
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/v1/exercises", tags=["exercises"])


# Request/Response schemas for exercise endpoints
class CodeExecutionRequest(BaseModel):
    """Schema for code execution request."""
    code: str = Field(..., min_length=1, description="Python code to execute")
    input_data: Optional[str] = Field(None, description="Optional input data for the code")
    timeout: int = Field(default=30, ge=1, le=60, description="Execution timeout in seconds")


class CodeExecutionResponse(BaseModel):
    """Schema for code execution response."""
    execution_id: str
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: int  # in milliseconds
    exit_code: int


class ExerciseValidationResponse(BaseModel):
    """Schema for exercise validation response."""
    submission_id: uuid.UUID
    exercise_id: uuid.UUID
    is_correct: bool
    score: int
    total_tests: int
    passed_tests: int
    failed_tests: int
    test_results: List[dict]
    execution_time: int
    submitted_at: str


class ExerciseHintResponse(BaseModel):
    """Schema for exercise hint response."""
    id: uuid.UUID
    hint_text: str
    order_index: int
    unlocked: bool


class SolutionComparisonResponse(BaseModel):
    """Schema for solution comparison response."""
    exercise_id: uuid.UUID
    matches_reference: bool
    submitted_score: int
    reference_score: int
    submitted_passed: int
    reference_passed: int
    total_tests: int


@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Execute Python code in a sandboxed environment.
    
    This endpoint allows users to test code snippets without submitting
    them as exercise solutions.
    """
    try:
        result = await exercise_validation_service.execute_code(
            code=request.code,
            input_data=request.input_data,
            timeout=request.timeout
        )
        
        return CodeExecutionResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code execution failed: {str(e)}"
        )


@router.post("/submit", response_model=ExerciseValidationResponse)
async def submit_exercise(
    submission: ExerciseSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit an exercise solution for validation.
    
    The submitted code will be tested against all test cases for the exercise.
    """
    try:
        result = await exercise_validation_service.submit_exercise(
            db=db,
            exercise_id=submission.exercise_id,
            user_id=current_user.id,
            submitted_code=submission.submitted_code
        )
        
        return ExerciseValidationResponse(
            submission_id=result["submission_id"],
            exercise_id=result["exercise_id"],
            is_correct=result["is_correct"],
            score=result["score"],
            total_tests=result["total_tests"],
            passed_tests=result["passed_tests"],
            failed_tests=result["failed_tests"],
            test_results=result["test_results"],
            execution_time=result["execution_time"],
            submitted_at=result["submitted_at"].isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Exercise submission failed: {str(e)}"
        )


@router.get("/{exercise_id}/hints", response_model=List[ExerciseHintResponse])
async def get_exercise_hints(
    exercise_id: uuid.UUID,
    max_hints: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get hints for an exercise.
    
    Hints are unlocked progressively based on the number of submission attempts.
    """
    try:
        hints = exercise_validation_service.get_exercise_hints(
            db=db,
            exercise_id=exercise_id,
            user_id=current_user.id,
            max_hints=max_hints
        )
        
        return [ExerciseHintResponse(**hint) for hint in hints]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hints: {str(e)}"
        )


@router.post("/{exercise_id}/compare", response_model=SolutionComparisonResponse)
async def compare_with_solution(
    exercise_id: uuid.UUID,
    request: CodeExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare submitted code with the reference solution.
    
    This endpoint runs both the submitted code and reference solution
    against all test cases and compares the results.
    """
    try:
        result = await exercise_validation_service.compare_with_solution(
            db=db,
            exercise_id=exercise_id,
            submitted_code=request.code
        )
        
        return SolutionComparisonResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Solution comparison failed: {str(e)}"
        )


@router.get("/submissions", response_model=List[ExerciseSubmissionResponse])
async def get_user_submissions(
    exercise_id: Optional[uuid.UUID] = None,
    limit: int = Field(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's exercise submissions.
    
    Optionally filter by exercise_id to get submissions for a specific exercise.
    """
    try:
        submissions = exercise_validation_service.get_user_submissions(
            db=db,
            user_id=current_user.id,
            exercise_id=exercise_id,
            limit=limit
        )
        
        return [
            ExerciseSubmissionResponse(
                id=sub["id"],
                exercise_id=sub["exercise_id"],
                user_id=current_user.id,
                submitted_code=sub["submitted_code"],
                is_correct=sub["is_correct"],
                score=sub["score"],
                execution_time=sub["execution_time"],
                error_message=sub["error_message"],
                submitted_at=sub["submitted_at"]
            )
            for sub in submissions
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get submissions: {str(e)}"
        )


@router.get("/{exercise_id}/validate", response_model=dict)
async def validate_exercise_setup(
    exercise_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate that an exercise is properly set up with test cases.
    
    This endpoint checks if the exercise has test cases and if the
    reference solution passes all tests.
    """
    try:
        from ..models import Exercise, ExerciseTestCase
        
        # Get exercise
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )
        
        # Get test cases
        test_cases = db.query(ExerciseTestCase).filter(
            ExerciseTestCase.exercise_id == exercise_id
        ).all()
        
        validation_result = {
            "exercise_id": exercise_id,
            "has_test_cases": len(test_cases) > 0,
            "test_case_count": len(test_cases),
            "has_solution": exercise.solution_code is not None,
            "solution_valid": False
        }
        
        # If exercise has solution and test cases, validate the solution
        if exercise.solution_code and test_cases:
            test_case_data = [
                {
                    "input_data": tc.input_data or "",
                    "expected_output": tc.expected_output,
                    "is_hidden": tc.is_hidden
                }
                for tc in test_cases
            ]
            
            solution_result = await exercise_validation_service.code_executor.validate_exercise_solution(
                str(exercise_id),
                exercise.solution_code,
                test_case_data
            )
            
            validation_result["solution_valid"] = solution_result["overall_success"]
            validation_result["solution_score"] = solution_result["score"]
        
        return validation_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )