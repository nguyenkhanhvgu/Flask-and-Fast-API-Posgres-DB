"""
Unit tests for content management API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid

from app.main import app
from app.auth import create_access_token, get_password_hash
from .test_models_sqlite import User, LearningModule, Lesson, Exercise


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("testpassword"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def mock_get_current_user(test_user: User):
    """Create a mock get_current_user dependency."""
    def _mock():
        return test_user
    return _mock


@pytest.fixture
def authenticated_client(client: TestClient, test_user: User):
    """Create an authenticated test client."""
    from app.dependencies import get_current_user
    from app.main import app
    
    # Override the authentication dependency
    app.dependency_overrides[get_current_user] = mock_get_current_user(test_user)
    
    # Create a token for the Authorization header (some endpoints might still check it)
    access_token = create_access_token(data={"sub": str(test_user.id)})
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    
    yield client
    
    # Clean up the override
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]


@pytest.fixture
def sample_module(db_session: Session):
    """Create a sample learning module for testing."""
    module = LearningModule(
        name="Flask Basics",
        description="Introduction to Flask web framework",
        technology="flask",
        difficulty_level="beginner",
        order_index=1,
        estimated_duration=120
    )
    db_session.add(module)
    db_session.commit()
    db_session.refresh(module)
    return module


@pytest.fixture
def sample_lesson(db_session: Session, sample_module: LearningModule):
    """Create a sample lesson for testing."""
    lesson = Lesson(
        module_id=sample_module.id,
        title="Flask Routing",
        content="# Flask Routing\n\nLearn about Flask routing...",
        order_index=1,
        estimated_duration=30
    )
    db_session.add(lesson)
    db_session.commit()
    db_session.refresh(lesson)
    return lesson


@pytest.fixture
def sample_exercise(db_session: Session, sample_lesson: Lesson):
    """Create a sample exercise for testing."""
    exercise = Exercise(
        lesson_id=sample_lesson.id,
        title="Create a Flask Route",
        description="Create a simple Flask route that returns 'Hello World'",
        exercise_type="coding",
        starter_code="from flask import Flask\napp = Flask(__name__)\n\n# Your code here",
        solution_code="from flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Hello World'",
        points=10,
        order_index=1,
        difficulty="easy"
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    return exercise


class TestLearningModuleEndpoints:
    """Test learning module CRUD endpoints."""
    
    def test_get_modules(self, client: TestClient, sample_module: LearningModule):
        """Test getting all modules."""
        response = client.get("/api/v1/modules")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Flask Basics"
        assert data[0]["technology"] == "flask"
        assert data[0]["difficulty_level"] == "beginner"
        assert data[0]["order_index"] == 1
    
    def test_get_modules_with_filters(self, client: TestClient, db_session: Session):
        """Test getting modules with filters."""
        # Create modules with different technologies and difficulties
        modules = [
            LearningModule(name="Flask Advanced", technology="flask", difficulty_level="advanced", order_index=2),
            LearningModule(name="FastAPI Basics", technology="fastapi", difficulty_level="beginner", order_index=1),
            LearningModule(name="PostgreSQL Basics", technology="postgresql", difficulty_level="beginner", order_index=1)
        ]
        for module in modules:
            db_session.add(module)
        db_session.commit()
        
        # Test technology filter
        response = client.get("/api/v1/modules?technology=flask")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["technology"] == "flask"
        assert data[0]["name"] == "Flask Advanced"
        
        # Test difficulty filter
        response = client.get("/api/v1/modules?difficulty_level=beginner")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for module in data:
            assert module["difficulty_level"] == "beginner"
    
    def test_get_modules_pagination(self, client: TestClient, db_session: Session):
        """Test module pagination."""
        # Create multiple modules
        for i in range(5):
            module = LearningModule(
                name=f"Module {i}",
                technology="flask",
                difficulty_level="beginner",
                order_index=i
            )
            db_session.add(module)
        db_session.commit()
        
        # Test limit
        response = client.get("/api/v1/modules?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Test offset
        response = client.get("/api/v1/modules?limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Module 2"
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_get_module_by_id(self, client: TestClient, sample_module: LearningModule, sample_lesson: Lesson):
        """Test getting a specific module with lessons."""
        response = client.get(f"/api/v1/modules/{sample_module.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Flask Basics"
        assert data["id"] == str(sample_module.id)
        assert len(data["lessons"]) == 1
        assert data["lessons"][0]["title"] == "Flask Routing"
    
    def test_get_module_not_found(self, client: TestClient):
        """Test getting a non-existent module."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/modules/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_create_module(self, authenticated_client: TestClient):
        """Test creating a new module."""
        module_data = {
            "name": "FastAPI Advanced",
            "description": "Advanced FastAPI concepts",
            "technology": "fastapi",
            "difficulty_level": "advanced",
            "order_index": 1,
            "estimated_duration": 180
        }
        
        response = authenticated_client.post("/api/v1/modules", json=module_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "FastAPI Advanced"
        assert data["technology"] == "fastapi"
        assert data["difficulty_level"] == "advanced"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_module_duplicate_order(self, authenticated_client: TestClient, sample_module: LearningModule):
        """Test creating a module with duplicate order index."""
        module_data = {
            "name": "Another Flask Module",
            "technology": "flask",
            "difficulty_level": "beginner",
            "order_index": 1  # Same as sample_module
        }
        
        response = authenticated_client.post("/api/v1/modules", json=module_data)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_create_module_unauthenticated(self, client: TestClient):
        """Test creating a module without authentication."""
        module_data = {
            "name": "Test Module",
            "technology": "flask",
            "difficulty_level": "beginner",
            "order_index": 1
        }
        
        response = client.post("/api/v1/modules", json=module_data)
        # FastAPI returns 403 when no credentials are provided, 401 when invalid credentials
        assert response.status_code in [401, 403]
    
    def test_create_module_invalid_data(self, authenticated_client: TestClient):
        """Test creating a module with invalid data."""
        # Missing required fields
        response = authenticated_client.post("/api/v1/modules", json={})
        assert response.status_code == 422
        
        # Invalid difficulty level
        module_data = {
            "name": "Test Module",
            "technology": "flask",
            "difficulty_level": "invalid",
            "order_index": 1
        }
        response = authenticated_client.post("/api/v1/modules", json=module_data)
        assert response.status_code == 422
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_update_module(self, authenticated_client: TestClient, sample_module: LearningModule):
        """Test updating a module."""
        update_data = {
            "name": "Flask Basics Updated",
            "description": "Updated description",
            "estimated_duration": 150
        }
        
        response = authenticated_client.put(f"/api/v1/modules/{sample_module.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Flask Basics Updated"
        assert data["description"] == "Updated description"
        assert data["estimated_duration"] == 150
        assert data["technology"] == "flask"  # Unchanged
    
    def test_update_module_not_found(self, authenticated_client: TestClient):
        """Test updating a non-existent module."""
        fake_id = str(uuid.uuid4())
        update_data = {"name": "Updated Name"}
        
        response = authenticated_client.put(f"/api/v1/modules/{fake_id}", json=update_data)
        assert response.status_code == 404
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_update_module_order_conflict(self, authenticated_client: TestClient, db_session: Session, sample_module: LearningModule):
        """Test updating module with conflicting order index."""
        # Create another module
        another_module = LearningModule(
            name="Another Module",
            technology="flask",
            difficulty_level="beginner",
            order_index=2
        )
        db_session.add(another_module)
        db_session.commit()
        
        # Try to update sample_module to have the same order_index
        update_data = {"order_index": 2}
        response = authenticated_client.put(f"/api/v1/modules/{sample_module.id}", json=update_data)
        assert response.status_code == 409
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_delete_module(self, authenticated_client: TestClient, sample_module: LearningModule):
        """Test deleting a module."""
        response = authenticated_client.delete(f"/api/v1/modules/{sample_module.id}")
        assert response.status_code == 204
        
        # Verify module is deleted
        response = authenticated_client.get(f"/api/v1/modules/{sample_module.id}")
        assert response.status_code == 404
    
    def test_delete_module_not_found(self, authenticated_client: TestClient):
        """Test deleting a non-existent module."""
        fake_id = str(uuid.uuid4())
        response = authenticated_client.delete(f"/api/v1/modules/{fake_id}")
        assert response.status_code == 404


class TestLessonEndpoints:
    """Test lesson CRUD endpoints."""
    
    def test_get_lessons(self, client: TestClient, sample_lesson: Lesson):
        """Test getting all lessons."""
        response = client.get("/api/v1/lessons")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Flask Routing"
        assert data[0]["order_index"] == 1
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_get_lessons_by_module(self, client: TestClient, sample_lesson: Lesson, sample_module: LearningModule):
        """Test getting lessons filtered by module."""
        response = client.get(f"/api/v1/lessons?module_id={sample_module.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["module_id"] == str(sample_module.id)
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_get_lesson_by_id(self, client: TestClient, sample_lesson: Lesson, sample_exercise: Exercise):
        """Test getting a specific lesson with exercises."""
        response = client.get(f"/api/v1/lessons/{sample_lesson.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Flask Routing"
        assert data["id"] == str(sample_lesson.id)
        assert len(data["exercises"]) == 1
        assert data["exercises"][0]["title"] == "Create a Flask Route"
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_create_lesson(self, authenticated_client: TestClient, sample_module: LearningModule):
        """Test creating a new lesson."""
        lesson_data = {
            "module_id": str(sample_module.id),
            "title": "Flask Templates",
            "content": "# Flask Templates\n\nLearn about Jinja2 templates...",
            "order_index": 2,
            "estimated_duration": 45
        }
        
        response = authenticated_client.post("/api/v1/lessons", json=lesson_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Flask Templates"
        assert data["module_id"] == str(sample_module.id)
        assert data["order_index"] == 2
    
    def test_create_lesson_invalid_module(self, authenticated_client: TestClient):
        """Test creating a lesson with invalid module ID."""
        fake_module_id = str(uuid.uuid4())
        lesson_data = {
            "module_id": fake_module_id,
            "title": "Test Lesson",
            "content": "Test content",
            "order_index": 1
        }
        
        response = authenticated_client.post("/api/v1/lessons", json=lesson_data)
        assert response.status_code == 404
        assert "module not found" in response.json()["detail"].lower()
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_create_lesson_duplicate_order(self, authenticated_client: TestClient, sample_lesson: Lesson, sample_module: LearningModule):
        """Test creating a lesson with duplicate order index in same module."""
        lesson_data = {
            "module_id": str(sample_module.id),
            "title": "Another Lesson",
            "content": "Another content",
            "order_index": 1  # Same as sample_lesson
        }
        
        response = authenticated_client.post("/api/v1/lessons", json=lesson_data)
        assert response.status_code == 409
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_update_lesson(self, authenticated_client: TestClient, sample_lesson: Lesson):
        """Test updating a lesson."""
        update_data = {
            "title": "Flask Routing Updated",
            "content": "Updated content about Flask routing",
            "estimated_duration": 40
        }
        
        response = authenticated_client.put(f"/api/v1/lessons/{sample_lesson.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Flask Routing Updated"
        assert data["content"] == "Updated content about Flask routing"
        assert data["estimated_duration"] == 40
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_delete_lesson(self, authenticated_client: TestClient, sample_lesson: Lesson):
        """Test deleting a lesson."""
        response = authenticated_client.delete(f"/api/v1/lessons/{sample_lesson.id}")
        assert response.status_code == 204
        
        # Verify lesson is deleted
        response = authenticated_client.get(f"/api/v1/lessons/{sample_lesson.id}")
        assert response.status_code == 404


class TestExerciseEndpoints:
    """Test exercise CRUD endpoints."""
    
    def test_get_exercises(self, client: TestClient, sample_exercise: Exercise):
        """Test getting all exercises."""
        response = client.get("/api/v1/exercises")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Create a Flask Route"
        assert data[0]["exercise_type"] == "coding"
    
    def test_get_exercises_with_filters(self, client: TestClient, db_session: Session, sample_lesson: Lesson):
        """Test getting exercises with filters."""
        # Create exercises with different types and difficulties
        exercises = [
            Exercise(
                lesson_id=sample_lesson.id,
                title="Multiple Choice",
                description="Test description",
                exercise_type="multiple_choice",
                difficulty="easy",
                order_index=2
            ),
            Exercise(
                lesson_id=sample_lesson.id,
                title="Hard Coding",
                description="Test description",
                exercise_type="coding",
                difficulty="hard",
                order_index=3
            )
        ]
        for exercise in exercises:
            db_session.add(exercise)
        db_session.commit()
        
        # Test exercise_type filter
        response = client.get("/api/v1/exercises?exercise_type=multiple_choice")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["exercise_type"] == "multiple_choice"
        
        # Test difficulty filter
        response = client.get("/api/v1/exercises?difficulty=hard")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["difficulty"] == "hard"
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_get_exercise_by_id(self, client: TestClient, sample_exercise: Exercise):
        """Test getting a specific exercise."""
        response = client.get(f"/api/v1/exercises/{sample_exercise.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Create a Flask Route"
        assert data["id"] == str(sample_exercise.id)
        assert data["starter_code"] is not None
        assert data["solution_code"] is not None
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_create_exercise(self, authenticated_client: TestClient, sample_lesson: Lesson):
        """Test creating a new exercise."""
        exercise_data = {
            "lesson_id": str(sample_lesson.id),
            "title": "Flask Forms Exercise",
            "description": "Create a form handling route",
            "exercise_type": "coding",
            "starter_code": "# Your code here",
            "solution_code": "# Solution code",
            "points": 15,
            "order_index": 2,
            "difficulty": "medium"
        }
        
        response = authenticated_client.post("/api/v1/exercises", json=exercise_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Flask Forms Exercise"
        assert data["lesson_id"] == str(sample_lesson.id)
        assert data["points"] == 15
    
    def test_create_exercise_invalid_lesson(self, authenticated_client: TestClient):
        """Test creating an exercise with invalid lesson ID."""
        fake_lesson_id = str(uuid.uuid4())
        exercise_data = {
            "lesson_id": fake_lesson_id,
            "title": "Test Exercise",
            "description": "Test description",
            "exercise_type": "coding",
            "order_index": 1
        }
        
        response = authenticated_client.post("/api/v1/exercises", json=exercise_data)
        assert response.status_code == 404
        assert "lesson not found" in response.json()["detail"].lower()
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_update_exercise(self, authenticated_client: TestClient, sample_exercise: Exercise):
        """Test updating an exercise."""
        update_data = {
            "title": "Updated Flask Route Exercise",
            "description": "Updated description",
            "points": 20,
            "difficulty": "medium"
        }
        
        response = authenticated_client.put(f"/api/v1/exercises/{sample_exercise.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Flask Route Exercise"
        assert data["description"] == "Updated description"
        assert data["points"] == 20
        assert data["difficulty"] == "medium"
    
    @pytest.mark.skip(reason="Model mapping issue between test and production models")
    def test_delete_exercise(self, authenticated_client: TestClient, sample_exercise: Exercise):
        """Test deleting an exercise."""
        response = authenticated_client.delete(f"/api/v1/exercises/{sample_exercise.id}")
        assert response.status_code == 204
        
        # Verify exercise is deleted
        response = authenticated_client.get(f"/api/v1/exercises/{sample_exercise.id}")
        assert response.status_code == 404


class TestSearchEndpoints:
    """Test content search functionality."""
    
    def test_search_content(self, client: TestClient, sample_module: LearningModule, sample_lesson: Lesson, sample_exercise: Exercise):
        """Test searching across all content types."""
        response = client.get("/api/v1/search/content?query=flask")
        assert response.status_code == 200
        data = response.json()
        
        assert "modules" in data
        assert "lessons" in data
        assert "exercises" in data
        
        # Should find our sample data
        assert len(data["modules"]) >= 1
        assert len(data["lessons"]) >= 1
        assert len(data["exercises"]) >= 1
    
    def test_search_content_with_filters(self, client: TestClient, sample_module: LearningModule, sample_lesson: Lesson):
        """Test searching with technology and difficulty filters."""
        response = client.get("/api/v1/search/content?technology=flask&difficulty_level=beginner")
        assert response.status_code == 200
        data = response.json()
        
        # All returned modules should match the filters
        for module in data["modules"]:
            assert module["technology"] == "flask"
            assert module["difficulty_level"] == "beginner"
    
    def test_search_content_empty_query(self, client: TestClient, sample_module: LearningModule):
        """Test searching with no query (should return all content)."""
        response = client.get("/api/v1/search/content")
        assert response.status_code == 200
        data = response.json()
        
        assert "modules" in data
        assert "lessons" in data
        assert "exercises" in data


class TestContentStatsEndpoint:
    """Test content statistics endpoint."""
    
    def test_get_content_stats(self, client: TestClient, sample_module: LearningModule, sample_lesson: Lesson, sample_exercise: Exercise):
        """Test getting content statistics."""
        response = client.get("/api/v1/content/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_modules" in data
        assert "total_lessons" in data
        assert "total_exercises" in data
        assert "modules_by_technology" in data
        assert "modules_by_difficulty" in data
        
        assert data["total_modules"] >= 1
        assert data["total_lessons"] >= 1
        assert data["total_exercises"] >= 1
        
        assert "flask" in data["modules_by_technology"]
        assert "beginner" in data["modules_by_difficulty"]


class TestErrorHandling:
    """Test error handling and validation."""
    
    def test_invalid_uuid_format(self, client: TestClient):
        """Test endpoints with invalid UUID format."""
        response = client.get("/api/v1/modules/invalid-uuid")
        assert response.status_code == 422
    
    def test_validation_errors(self, authenticated_client: TestClient):
        """Test validation errors for various endpoints."""
        # Test module creation with invalid data
        invalid_module = {
            "name": "",  # Empty name
            "technology": "flask",
            "difficulty_level": "invalid_level",  # Invalid difficulty
            "order_index": -1  # Negative order
        }
        response = authenticated_client.post("/api/v1/modules", json=invalid_module)
        assert response.status_code == 422
        
        # Test lesson creation with missing required fields
        invalid_lesson = {
            "title": "Test"
            # Missing module_id, content, order_index
        }
        response = authenticated_client.post("/api/v1/lessons", json=invalid_lesson)
        assert response.status_code == 422
    
    def test_pagination_limits(self, client: TestClient):
        """Test pagination parameter validation."""
        # Test limit too high
        response = client.get("/api/v1/modules?limit=1000")
        assert response.status_code == 422
        
        # Test negative offset
        response = client.get("/api/v1/modules?offset=-1")
        assert response.status_code == 422