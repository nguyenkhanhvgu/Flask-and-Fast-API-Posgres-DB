"""
Tests for exercise validation service.
"""
import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session

from app.services.exercise_validation import ExerciseValidationService
from app.models import Exercise, ExerciseTestCase, ExerciseHint, ExerciseSubmission, User


class TestExerciseValidationService:
    """Test cases for ExerciseValidationService."""
    
    @pytest.fixture
    def service(self):
        """Create an ExerciseValidationService instance for testing."""
        service = ExerciseValidationService()
        service.code_executor = Mock()
        return service
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_exercise(self):
        """Create a sample exercise for testing."""
        exercise = Exercise(
            id=uuid.uuid4(),
            lesson_id=uuid.uuid4(),
            title="Test Exercise",
            description="A test exercise",
            exercise_type="coding",
            starter_code="# Write your code here",
            solution_code="print('Hello, World!')",
            points=10,
            order_index=1,
            difficulty="easy"
        )
        return exercise
    
    @pytest.fixture
    def sample_test_cases(self, sample_exercise):
        """Create sample test cases for testing."""
        return [
            ExerciseTestCase(
                id=uuid.uuid4(),
                exercise_id=sample_exercise.id,
                input_data="",
                expected_output="Hello, World!",
                is_hidden=False,
                order_index=1
            ),
            ExerciseTestCase(
                id=uuid.uuid4(),
                exercise_id=sample_exercise.id,
                input_data="test",
                expected_output="Hello, World!",
                is_hidden=True,
                order_index=2
            )
        ]
    
    @pytest.fixture
    def sample_user(self):
        """Create a sample user for testing."""
        return User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
    
    @pytest.mark.asyncio
    async def test_submit_exercise_success(self, service, mock_db, sample_exercise, sample_test_cases, sample_user):
        """Test successful exercise submission."""
        # Setup mocks
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exercise
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = sample_test_cases
        
        # Mock code executor response
        service.code_executor.validate_exercise_solution = AsyncMock(return_value={
            "overall_success": True,
            "score": 100,
            "total_tests": 2,
            "passed_tests": 2,
            "failed_tests": 0,
            "test_results": [
                {
                    "test_case_id": 1,
                    "passed": True,
                    "input": "",
                    "expected_output": "Hello, World!",
                    "actual_output": "Hello, World!",
                    "execution_time": 100,
                    "error": None
                },
                {
                    "test_case_id": 2,
                    "passed": True,
                    "input": "[Hidden]",
                    "expected_output": "[Hidden]",
                    "actual_output": "Hello, World!",
                    "execution_time": 95,
                    "error": None
                }
            ],
            "total_execution_time": 195
        })
        
        # Mock database operations
        mock_submission = Mock()
        mock_submission.id = uuid.uuid4()
        mock_submission.submitted_at = datetime.now()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        with patch('app.services.exercise_validation.ExerciseSubmission', return_value=mock_submission):
            result = await service.submit_exercise(
                db=mock_db,
                exercise_id=sample_exercise.id,
                user_id=sample_user.id,
                submitted_code="print('Hello, World!')"
            )
        
        # Assertions
        assert result["is_correct"] is True
        assert result["score"] == 100
        assert result["total_tests"] == 2
        assert result["passed_tests"] == 2
        assert result["failed_tests"] == 0
        assert len(result["test_results"]) == 2
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_submit_exercise_not_found(self, service, mock_db, sample_user):
        """Test exercise submission with non-existent exercise."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="Exercise .* not found"):
            await service.submit_exercise(
                db=mock_db,
                exercise_id=uuid.uuid4(),
                user_id=sample_user.id,
                submitted_code="print('test')"
            )
    
    @pytest.mark.asyncio
    async def test_submit_exercise_no_test_cases(self, service, mock_db, sample_exercise, sample_user):
        """Test exercise submission with no test cases."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exercise
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        with pytest.raises(ValueError, match="No test cases found"):
            await service.submit_exercise(
                db=mock_db,
                exercise_id=sample_exercise.id,
                user_id=sample_user.id,
                submitted_code="print('test')"
            )
    
    @pytest.mark.asyncio
    async def test_execute_code(self, service):
        """Test code execution without validation."""
        service.code_executor.execute_code = AsyncMock(return_value={
            "execution_id": "test_id",
            "success": True,
            "output": "Hello, World!",
            "error": None,
            "execution_time": 100,
            "exit_code": 0
        })
        
        result = await service.execute_code("print('Hello, World!')", timeout=30)
        
        assert result["success"] is True
        assert result["output"] == "Hello, World!"
        service.code_executor.execute_code.assert_called_once_with(
            "print('Hello, World!')", None, 30
        )
    
    def test_get_exercise_hints_with_attempts(self, service, mock_db, sample_exercise, sample_user):
        """Test getting exercise hints based on user attempts."""
        # Mock user attempts
        mock_db.query.return_value.filter.return_value.count.return_value = 2
        
        # Mock hints
        hints = [
            ExerciseHint(
                id=uuid.uuid4(),
                exercise_id=sample_exercise.id,
                hint_text="Try using the print function",
                order_index=1
            ),
            ExerciseHint(
                id=uuid.uuid4(),
                exercise_id=sample_exercise.id,
                hint_text="Remember to include quotes around strings",
                order_index=2
            ),
            ExerciseHint(
                id=uuid.uuid4(),
                exercise_id=sample_exercise.id,
                hint_text="Check your syntax carefully",
                order_index=3
            )
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = hints
        
        result = service.get_exercise_hints(
            db=mock_db,
            exercise_id=sample_exercise.id,
            user_id=sample_user.id
        )
        
        # With 2 attempts, first 2 hints should be unlocked
        assert len(result) == 3
        assert result[0]["unlocked"] is True
        assert result[0]["hint_text"] == "Try using the print function"
        assert result[1]["unlocked"] is True
        assert result[1]["hint_text"] == "Remember to include quotes around strings"
        assert result[2]["unlocked"] is False
        assert "unlocked after 3 attempts" in result[2]["hint_text"]
    
    def test_get_exercise_hints_no_attempts(self, service, mock_db, sample_exercise, sample_user):
        """Test getting exercise hints with no attempts."""
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        
        hints = [
            ExerciseHint(
                id=uuid.uuid4(),
                exercise_id=sample_exercise.id,
                hint_text="First hint",
                order_index=1
            )
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = hints
        
        result = service.get_exercise_hints(
            db=mock_db,
            exercise_id=sample_exercise.id,
            user_id=sample_user.id
        )
        
        # No attempts, so no hints should be unlocked
        assert len(result) == 1
        assert result[0]["unlocked"] is False
        assert "unlocked after 1 attempts" in result[0]["hint_text"]
    
    @pytest.mark.asyncio
    async def test_compare_with_solution_success(self, service, mock_db, sample_exercise):
        """Test successful solution comparison."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exercise
        
        test_cases = [
            ExerciseTestCase(
                id=uuid.uuid4(),
                exercise_id=sample_exercise.id,
                input_data="",
                expected_output="Hello, World!",
                is_hidden=False,
                order_index=1
            )
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = test_cases
        
        service.code_executor.compare_with_solution = AsyncMock(return_value={
            "matches_reference": True,
            "submitted_solution": {
                "score": 100,
                "passed_tests": 1,
                "total_tests": 1
            },
            "reference_solution": {
                "score": 100,
                "passed_tests": 1,
                "total_tests": 1
            }
        })
        
        result = await service.compare_with_solution(
            db=mock_db,
            exercise_id=sample_exercise.id,
            submitted_code="print('Hello, World!')"
        )
        
        assert result["matches_reference"] is True
        assert result["submitted_score"] == 100
        assert result["reference_score"] == 100
        assert result["total_tests"] == 1
    
    @pytest.mark.asyncio
    async def test_compare_with_solution_no_exercise(self, service, mock_db):
        """Test solution comparison with non-existent exercise."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="Exercise .* not found"):
            await service.compare_with_solution(
                db=mock_db,
                exercise_id=uuid.uuid4(),
                submitted_code="print('test')"
            )
    
    @pytest.mark.asyncio
    async def test_compare_with_solution_no_reference(self, service, mock_db, sample_exercise):
        """Test solution comparison with no reference solution."""
        sample_exercise.solution_code = None
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exercise
        
        with pytest.raises(ValueError, match="No reference solution available"):
            await service.compare_with_solution(
                db=mock_db,
                exercise_id=sample_exercise.id,
                submitted_code="print('test')"
            )
    
    def test_get_user_submissions(self, service, mock_db, sample_user, sample_exercise):
        """Test getting user submissions."""
        submissions = [
            ExerciseSubmission(
                id=uuid.uuid4(),
                exercise_id=sample_exercise.id,
                user_id=sample_user.id,
                submitted_code="print('Hello')",
                is_correct=True,
                score=100,
                execution_time=150,
                error_message=None,
                submitted_at=datetime.now()
            )
        ]
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = submissions
        
        result = service.get_user_submissions(
            db=mock_db,
            user_id=sample_user.id,
            limit=50
        )
        
        assert len(result) == 1
        assert result[0]["is_correct"] is True
        assert result[0]["score"] == 100
        assert result[0]["submitted_code"] == "print('Hello')"
    
    def test_get_user_submissions_with_exercise_filter(self, service, mock_db, sample_user, sample_exercise):
        """Test getting user submissions filtered by exercise."""
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        
        service.get_user_submissions(
            db=mock_db,
            user_id=sample_user.id,
            exercise_id=sample_exercise.id,
            limit=50
        )
        
        # Verify that filter was called twice (once for user_id, once for exercise_id)
        assert mock_query.filter.call_count == 2
    
    def test_extract_error_message_success(self, service):
        """Test error message extraction from successful validation."""
        validation_result = {
            "overall_success": True,
            "test_results": []
        }
        
        error_message = service._extract_error_message(validation_result)
        assert error_message is None
    
    def test_extract_error_message_with_specific_error(self, service):
        """Test error message extraction with specific test error."""
        validation_result = {
            "overall_success": False,
            "failed_tests": 1,
            "total_tests": 2,
            "test_results": [
                {
                    "passed": True,
                    "error": None
                },
                {
                    "passed": False,
                    "error": "SyntaxError: invalid syntax"
                }
            ]
        }
        
        error_message = service._extract_error_message(validation_result)
        assert error_message == "SyntaxError: invalid syntax"
    
    def test_extract_error_message_general_failure(self, service):
        """Test error message extraction with general failure."""
        validation_result = {
            "overall_success": False,
            "failed_tests": 2,
            "total_tests": 3,
            "test_results": [
                {
                    "passed": False,
                    "error": None
                },
                {
                    "passed": False,
                    "error": None
                }
            ]
        }
        
        error_message = service._extract_error_message(validation_result)
        assert error_message == "Failed 2 out of 3 test cases"


if __name__ == "__main__":
    pytest.main([__file__])