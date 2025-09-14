"""
Tests for exercise API endpoints.
"""
import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.models import User, Exercise, ExerciseTestCase
from app.dependencies import get_current_user, get_db


class TestExerciseAPI:
    """Test cases for exercise API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            is_active=True
        )
        return user
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def authenticated_client(self, client, mock_user, mock_db):
        """Create an authenticated test client."""
        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: mock_db
        
        yield client
        
        # Clean up overrides
        app.dependency_overrides.clear()
    
    def test_execute_code_success(self, authenticated_client):
        """Test successful code execution."""
        with patch('app.services.exercise_validation.exercise_validation_service') as mock_service:
            mock_service.execute_code = AsyncMock(return_value={
                "execution_id": "test_id",
                "success": True,
                "output": "Hello, World!\n",
                "error": None,
                "execution_time": 150,
                "exit_code": 0
            })
            
            response = authenticated_client.post(
                "/api/v1/exercises/execute",
                json={
                    "code": "print('Hello, World!')",
                    "timeout": 30
                }
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["output"] == "Hello, World!\n"
            assert data["execution_time"] == 150
    
    def test_execute_code_with_input(self, authenticated_client):
        """Test code execution with input data."""
        with patch('app.services.exercise_validation.exercise_validation_service') as mock_service:
            mock_service.execute_code = AsyncMock(return_value={
                "execution_id": "test_id",
                "success": True,
                "output": "Hello, Alice!\n",
                "error": None,
                "execution_time": 200,
                "exit_code": 0
            })
            
            response = authenticated_client.post(
                "/api/v1/exercises/execute",
                json={
                    "code": "name = input(); print(f'Hello, {name}!')",
                    "input_data": "Alice",
                    "timeout": 15
                }
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert "Alice" in data["output"]
    
    def test_execute_code_failure(self, authenticated_client):
        """Test code execution failure."""
        with patch('app.services.exercise_validation.exercise_validation_service') as mock_service:
            mock_service.execute_code = AsyncMock(side_effect=Exception("Execution failed"))
            
            response = authenticated_client.post(
                "/api/v1/exercises/execute",
                json={
                    "code": "print('test')",
                    "timeout": 30
                }
            )
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Code execution failed" in response.json()["detail"]
    
    def test_execute_code_invalid_request(self, authenticated_client):
        """Test code execution with invalid request data."""
        response = authenticated_client.post(
            "/api/v1/exercises/execute",
            json={
                "code": "",  # Empty code
                "timeout": 30
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_exercise_success(self, authenticated_client, mock_user):
        """Test successful exercise submission."""
        exercise_id = uuid.uuid4()
        submission_id = uuid.uuid4()
        
        with patch('app.services.exercise_validation.exercise_validation_service') as mock_service:
            mock_service.submit_exercise = AsyncMock(return_value={
                "submission_id": submission_id,
                "exercise_id": exercise_id,
                "is_correct": True,
                "score": 100,
                "total_tests": 2,
                "passed_tests": 2,
                "failed_tests": 0,
                "test_results": [
                    {
                        "test_case_id": 1,
                        "passed": True,
                        "input": "",
                        "expected_output": "Hello",
                        "actual_output": "Hello",
                        "execution_time": 100,
                        "error": None
                    }
                ],
                "execution_time": 200,
                "submitted_at": datetime.now()
            })
            
            response = authenticated_client.post(
                "/api/v1/exercises/submit",
                json={
                    "exercise_id": str(exercise_id),
                    "submitted_code": "print('Hello')"
                }
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["is_correct"] is True
            assert data["score"] == 100
            assert data["total_tests"] == 2
            assert len(data["test_results"]) == 1
    
    def test_submit_exercise_not_found(self, authenticated_client):
        """Test exercise submission with non-existent exercise."""
        with patch('app.services.exercise_validation.exercise_validation_service') as mock_service:
            mock_service.submit_exercise = AsyncMock(
                side_effect=ValueError("Exercise not found")
            )
            
            response = authenticated_client.post(
                "/api/v1/exercises/submit",
                json={
                    "exercise_id": str(uuid.uuid4()),
                    "submitted_code": "print('test')"
                }
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Exercise not found" in response.json()["detail"]
    
    def test_get_exercise_hints(self, authenticated_client, mock_user):
        """Test getting exercise hints."""
        exercise_id = uuid.uuid4()
        
        with patch('app.services.exercise_validation.exercise_validation_service') as mock_service:
            mock_service.get_exercise_hints = Mock(return_value=[
                {
                    "id": uuid.uuid4(),
                    "hint_text": "Try using the print function",
                    "order_index": 1,
                    "unlocked": True
                },
                {
                    "id": uuid.uuid4(),
                    "hint_text": "Hint 2 (unlocked after 2 attempts)",
                    "order_index": 2,
                    "unlocked": False
                }
            ])
            
            response = authenticated_client.get(
                f"/api/v1/exercises/{exercise_id}/hints"
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["unlocked"] is True
            assert data[1]["unlocked"] is False
    
    def test_get_exercise_hints_with_limit(self, authenticated_client):
        """Test getting exercise hints with limit."""
        exercise_id = uuid.uuid4()
        
        with patch('app.services.exercise_validation.exercise_validation_service') as mock_service:
            mock_service.get_exercise_hints = Mock(return_value=[
                {
                    "id": uuid.uuid4(),
                    "hint_text": "First hint",
                    "order_index": 1,
                    "unlocked": True
                }
            ])
            
            response = authenticated_client.get(
                f"/api/v1/exercises/{exercise_id}/hints?max_hints=1"
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            
            # Verify service was called with correct parameters
            mock_service.get_exercise_hints.assert_called_once()
            call_args = mock_service.get_exercise_hints.call_args
            assert call_args[1]["max_hints"] == 1
    
    def test_compare_with_solution_success(self, authenticated_client):
        """Test successful solution comparison."""
        exercise_id = uuid.uuid4()
        
        with patch('app.services.exercise_validation.exercise_validation_service') as mock_service:
            mock_service.compare_with_solution = AsyncMock(return_value={
                "exercise_id": exercise_id,
                "matches_reference": True,
                "submitted_score": 100,
                "reference_score": 100,
                "submitted_passed": 2,
                "reference_passed": 2,
                "total_tests": 2
            })
            
            response = authenticated_client.post(
                f"/api/v1/exercises/{exercise_id}/compare",
                json={
                    "code": "print('Hello, World!')",
                    "timeout": 30
                }
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["matches_reference"] is True
            assert data["submitted_score"] == 100
            assert data["reference_score"] == 100
    
    def test_compare_with_solution_not_found(self, authenticated_client):
        """Test solution comparison with non-existent exercise."""
        exercise_id = uuid.uuid4()
        
        with patch('app.services.exercise_validation.exercise_validation_service') as mock_service:
            mock_service.compare_with_solution = AsyncMock(
                side_effect=ValueError("Exercise not found")
            )
            
            response = authenticated_client.post(
                f"/api/v1/exercises/{exercise_id}/compare",
                json={
                    "code": "print('test')",
                    "timeout": 30
                }
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_user_submissions(self, authenticated_client, mock_user):
        """Test getting user submissions."""
        with patch('app.services.exercise_validation.exercise_validation_service') as mock_service:
            mock_service.get_user_submissions = Mock(return_value=[
                {
                    "id": uuid.uuid4(),
                    "exercise_id": uuid.uuid4(),
                    "submitted_code": "print('Hello')",
                    "is_correct": True,
                    "score": 100,
                    "execution_time": 150,
                    "error_message": None,
                    "submitted_at": datetime.now()
                }
            ])
            
            response = authenticated_client.get("/api/v1/exercises/submissions")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            assert data[0]["is_correct"] is True
            assert data[0]["score"] == 100
    
    def test_get_user_submissions_with_filter(self, authenticated_client):
        """Test getting user submissions with exercise filter."""
        exercise_id = uuid.uuid4()
        
        with patch('app.services.exercise_validation.exercise_validation_service') as mock_service:
            mock_service.get_user_submissions = Mock(return_value=[])
            
            response = authenticated_client.get(
                f"/api/v1/exercises/submissions?exercise_id={exercise_id}&limit=10"
            )
            
            assert response.status_code == status.HTTP_200_OK
            
            # Verify service was called with correct parameters
            mock_service.get_user_submissions.assert_called_once()
            call_args = mock_service.get_user_submissions.call_args
            assert call_args[1]["exercise_id"] == exercise_id
            assert call_args[1]["limit"] == 10
    
    def test_validate_exercise_setup_success(self, authenticated_client, mock_db):
        """Test exercise setup validation."""
        exercise_id = uuid.uuid4()
        
        # Mock exercise and test cases
        mock_exercise = Exercise(
            id=exercise_id,
            lesson_id=uuid.uuid4(),
            title="Test Exercise",
            description="Test",
            exercise_type="coding",
            solution_code="print('Hello')",
            points=10,
            order_index=1
        )
        
        mock_test_cases = [
            ExerciseTestCase(
                id=uuid.uuid4(),
                exercise_id=exercise_id,
                input_data="",
                expected_output="Hello",
                is_hidden=False,
                order_index=1
            )
        ]
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_exercise
        mock_db.query.return_value.filter.return_value.all.return_value = mock_test_cases
        
        with patch('app.services.exercise_validation.exercise_validation_service') as mock_service:
            mock_service.code_executor.validate_exercise_solution = AsyncMock(return_value={
                "overall_success": True,
                "score": 100
            })
            
            response = authenticated_client.get(
                f"/api/v1/exercises/{exercise_id}/validate"
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["has_test_cases"] is True
            assert data["test_case_count"] == 1
            assert data["has_solution"] is True
            assert data["solution_valid"] is True
            assert data["solution_score"] == 100
    
    def test_validate_exercise_setup_not_found(self, authenticated_client, mock_db):
        """Test exercise setup validation with non-existent exercise."""
        exercise_id = uuid.uuid4()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = authenticated_client.get(
            f"/api/v1/exercises/{exercise_id}/validate"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_unauthenticated_access(self, client):
        """Test that unauthenticated requests are rejected."""
        response = client.post(
            "/api/v1/exercises/execute",
            json={"code": "print('test')", "timeout": 30}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


if __name__ == "__main__":
    pytest.main([__file__])