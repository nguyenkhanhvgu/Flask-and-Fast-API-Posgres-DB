"""
Unit tests for progress tracking API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.main import app
from .test_models_sqlite import (
    User, UserProgress, UserBookmark, LearningModule, Lesson, Exercise, 
    ExerciseSubmission
)
from app.auth import create_access_token


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        username="testuser",
        password_hash="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_module(db_session: Session):
    """Create a test learning module."""
    module = LearningModule(
        name="Test Flask Module",
        description="Test module for Flask basics",
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
def test_lessons(db_session: Session, test_module):
    """Create test lessons."""
    lessons = []
    for i in range(3):
        lesson = Lesson(
            module_id=test_module.id,
            title=f"Test Lesson {i+1}",
            content=f"Content for lesson {i+1}",
            order_index=i+1,
            estimated_duration=30
        )
        db_session.add(lesson)
        lessons.append(lesson)
    
    db_session.commit()
    for lesson in lessons:
        db_session.refresh(lesson)
    return lessons


@pytest.fixture
def test_exercise(db_session: Session, test_lessons):
    """Create a test exercise."""
    exercise = Exercise(
        lesson_id=test_lessons[0].id,
        title="Test Exercise",
        description="Test exercise description",
        exercise_type="coding",
        starter_code="# Write your code here",
        solution_code="print('Hello, World!')",
        points=10,
        order_index=1,
        difficulty="easy"
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    return exercise


def mock_get_current_user(test_user):
    """Create a mock get_current_user dependency."""
    def _mock():
        return test_user
    return _mock


@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client."""
    from app.dependencies import get_current_user
    from app.main import app
    
    # Override the authentication dependency
    app.dependency_overrides[get_current_user] = mock_get_current_user(test_user)
    
    yield client
    
    # Clean up
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]


class TestUserProgress:
    """Test user progress endpoints."""
    
    def test_create_lesson_progress(self, authenticated_client, db_session, test_user, test_lessons):
        """Test creating lesson progress."""
        lesson = test_lessons[0]
        progress_data = {
            "lesson_id": str(lesson.id),
            "status": "in_progress",
            "time_spent": 300,
            "score": 85
        }
        
        response = authenticated_client.post("/api/v1/progress/lesson", json=progress_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["lesson_id"] == str(lesson.id)
        assert data["user_id"] == str(test_user.id)
        assert data["status"] == "in_progress"
        assert data["time_spent"] == 300
        assert data["score"] == 85
        assert data["attempts"] == 1
        assert data["completion_date"] is None
    
    def test_create_completed_lesson_progress(self, authenticated_client, db_session, test_user, test_lessons):
        """Test creating completed lesson progress sets completion date."""
        lesson = test_lessons[0]
        progress_data = {
            "lesson_id": str(lesson.id),
            "status": "completed",
            "time_spent": 600,
            "score": 95
        }
        
        response = authenticated_client.post("/api/v1/progress/lesson", json=progress_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "completed"
        assert data["completion_date"] is not None
    
    def test_update_existing_lesson_progress(self, authenticated_client, db_session, test_user, test_lessons):
        """Test updating existing lesson progress."""
        lesson = test_lessons[0]
        
        # Create initial progress
        initial_progress = UserProgress(
            user_id=test_user.id,
            lesson_id=lesson.id,
            status="in_progress",
            time_spent=200,
            score=70,
            attempts=1
        )
        db_session.add(initial_progress)
        db_session.commit()
        
        # Update progress
        progress_data = {
            "lesson_id": str(lesson.id),
            "status": "completed",
            "time_spent": 300,
            "score": 90
        }
        
        response = authenticated_client.post("/api/v1/progress/lesson", json=progress_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "completed"
        assert data["time_spent"] == 500  # 200 + 300
        assert data["score"] == 90  # Higher score kept
        assert data["attempts"] == 2
        assert data["completion_date"] is not None
    
    def test_get_user_progress(self, authenticated_client, db_session, test_user, test_lessons):
        """Test getting user progress."""
        # Create some progress records
        for i, lesson in enumerate(test_lessons):
            progress = UserProgress(
                user_id=test_user.id,
                lesson_id=lesson.id,
                status="completed" if i < 2 else "in_progress",
                time_spent=(i + 1) * 300,
                score=(i + 1) * 30,
                attempts=1,
                completion_date=datetime.utcnow() if i < 2 else None
            )
            db_session.add(progress)
        db_session.commit()
        
        response = authenticated_client.get(f"/api/v1/users/{test_user.id}/progress")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(record["user_id"] == str(test_user.id) for record in data)
    
    def test_get_lesson_progress(self, authenticated_client, db_session, test_user, test_lessons):
        """Test getting progress for a specific lesson."""
        lesson = test_lessons[0]
        progress = UserProgress(
            user_id=test_user.id,
            lesson_id=lesson.id,
            status="completed",
            time_spent=450,
            score=88,
            attempts=2,
            completion_date=datetime.utcnow()
        )
        db_session.add(progress)
        db_session.commit()
        
        response = authenticated_client.get(f"/api/v1/users/{test_user.id}/progress/lessons/{lesson.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["lesson_id"] == str(lesson.id)
        assert data["status"] == "completed"
        assert data["time_spent"] == 450
        assert data["score"] == 88
    
    def test_update_lesson_progress(self, authenticated_client, db_session, test_user, test_lessons):
        """Test updating lesson progress via PUT endpoint."""
        lesson = test_lessons[0]
        progress = UserProgress(
            user_id=test_user.id,
            lesson_id=lesson.id,
            status="in_progress",
            time_spent=200,
            score=70,
            attempts=1
        )
        db_session.add(progress)
        db_session.commit()
        
        update_data = {
            "status": "completed",
            "time_spent": 150,
            "score": 85
        }
        
        response = authenticated_client.put(f"/api/v1/progress/lesson/{lesson.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["time_spent"] == 350  # 200 + 150
        assert data["score"] == 85  # Higher score kept
        assert data["completion_date"] is not None


class TestModuleProgress:
    """Test module progress endpoints."""
    
    def test_get_user_module_progress(self, authenticated_client, db_session, test_user, test_module, test_lessons):
        """Test getting user progress across modules."""
        # Create progress for some lessons
        for i, lesson in enumerate(test_lessons[:2]):
            progress = UserProgress(
                user_id=test_user.id,
                lesson_id=lesson.id,
                status="completed",
                time_spent=(i + 1) * 300,
                score=(i + 1) * 40,
                attempts=1,
                completion_date=datetime.utcnow()
            )
            db_session.add(progress)
        
        # One in progress
        progress = UserProgress(
            user_id=test_user.id,
            lesson_id=test_lessons[2].id,
            status="in_progress",
            time_spent=200,
            score=30,
            attempts=1
        )
        db_session.add(progress)
        db_session.commit()
        
        response = authenticated_client.get(f"/api/v1/users/{test_user.id}/progress/modules")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        module_progress = data[0]
        assert module_progress["module"]["id"] == str(test_module.id)
        assert module_progress["total_lessons"] == 3
        assert module_progress["completed_lessons"] == 2
        assert module_progress["in_progress_lessons"] == 1
        assert module_progress["completion_percentage"] == 66.67
        assert module_progress["total_time_spent"] == 800  # 300 + 600 + 200
        assert module_progress["total_score"] == 110  # 40 + 80 + 30
    
    def test_get_module_lesson_progress(self, authenticated_client, db_session, test_user, test_module, test_lessons):
        """Test getting lesson progress for a specific module."""
        # Create progress for first lesson only
        progress = UserProgress(
            user_id=test_user.id,
            lesson_id=test_lessons[0].id,
            status="completed",
            time_spent=400,
            score=90,
            attempts=1,
            completion_date=datetime.utcnow()
        )
        db_session.add(progress)
        db_session.commit()
        
        response = authenticated_client.get(f"/api/v1/users/{test_user.id}/progress/modules/{test_module.id}/lessons")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # First lesson should have progress
        assert data[0]["lesson"]["id"] == str(test_lessons[0].id)
        assert data[0]["progress"] is not None
        assert data[0]["progress"]["status"] == "completed"
        
        # Other lessons should have no progress
        assert data[1]["progress"] is None
        assert data[2]["progress"] is None


class TestProgressStats:
    """Test progress statistics endpoints."""
    
    def test_get_user_progress_stats(self, authenticated_client, db_session, test_user, test_module, test_lessons, test_exercise):
        """Test getting comprehensive user progress statistics."""
        # Create progress for lessons
        for i, lesson in enumerate(test_lessons):
            progress = UserProgress(
                user_id=test_user.id,
                lesson_id=lesson.id,
                status="completed" if i < 2 else "in_progress",
                time_spent=(i + 1) * 300,
                score=(i + 1) * 30,
                attempts=1,
                completion_date=datetime.utcnow() if i < 2 else None
            )
            db_session.add(progress)
        
        # Create exercise submission
        submission = ExerciseSubmission(
            exercise_id=test_exercise.id,
            user_id=test_user.id,
            submitted_code="print('Hello')",
            is_correct=True,
            score=10
        )
        db_session.add(submission)
        db_session.commit()
        
        response = authenticated_client.get(f"/api/v1/users/{test_user.id}/progress/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_modules"] == 1
        assert data["completed_modules"] == 1  # Module has completed lessons
        assert data["total_lessons"] == 3
        assert data["completed_lessons"] == 2
        assert data["in_progress_lessons"] == 1
        assert data["total_exercises_attempted"] == 1
        assert data["total_time_spent"] == 1800  # 300 + 600 + 900
        assert data["total_score"] == 180  # 30 + 60 + 90
        assert data["completion_percentage"] == 66.67
        
        # Check technology breakdown
        assert "flask" in data["modules_by_technology"]
        assert data["modules_by_technology"]["flask"]["total"] == 1
        
        # Check recent activity
        assert len(data["recent_activity"]) == 3


class TestExerciseSubmissions:
    """Test exercise submission endpoints."""
    
    def test_submit_exercise(self, authenticated_client, db_session, test_user, test_exercise):
        """Test submitting an exercise solution."""
        submission_data = {
            "exercise_id": str(test_exercise.id),
            "submitted_code": "print('Hello, World!')"
        }
        
        response = authenticated_client.post("/api/v1/exercises/submit", json=submission_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["exercise_id"] == str(test_exercise.id)
        assert data["user_id"] == str(test_user.id)
        assert data["submitted_code"] == "print('Hello, World!')"
        assert data["is_correct"] is False  # Default until validation
        assert data["score"] == 0  # Default until validation
    
    def test_get_user_submissions(self, authenticated_client, db_session, test_user, test_exercise):
        """Test getting user exercise submissions."""
        # Create some submissions
        for i in range(3):
            submission = ExerciseSubmission(
                exercise_id=test_exercise.id,
                user_id=test_user.id,
                submitted_code=f"print('Attempt {i+1}')",
                is_correct=i == 2,  # Last attempt is correct
                score=i * 5,
                submitted_at=datetime.utcnow() - timedelta(hours=i)
            )
            db_session.add(submission)
        db_session.commit()
        
        response = authenticated_client.get(f"/api/v1/users/{test_user.id}/submissions")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(sub["user_id"] == str(test_user.id) for sub in data)
        assert all(sub["exercise_id"] == str(test_exercise.id) for sub in data)
        
        # Should be ordered by submission date desc
        assert data[0]["score"] == 0  # Most recent (i=0)
        assert data[2]["score"] == 10  # Oldest (i=2)


class TestBookmarks:
    """Test bookmark endpoints."""
    
    def test_create_bookmark(self, authenticated_client, db_session, test_user, test_lessons):
        """Test creating a bookmark."""
        lesson = test_lessons[0]
        bookmark_data = {
            "lesson_id": str(lesson.id)
        }
        
        response = authenticated_client.post("/api/v1/bookmarks", json=bookmark_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["lesson_id"] == str(lesson.id)
        assert data["user_id"] == str(test_user.id)
        assert data["lesson"]["id"] == str(lesson.id)
        assert data["lesson"]["title"] == lesson.title
    
    def test_create_duplicate_bookmark(self, authenticated_client, db_session, test_user, test_lessons):
        """Test creating a duplicate bookmark fails."""
        lesson = test_lessons[0]
        
        # Create initial bookmark
        bookmark = UserBookmark(
            user_id=test_user.id,
            lesson_id=lesson.id
        )
        db_session.add(bookmark)
        db_session.commit()
        
        # Try to create duplicate
        bookmark_data = {
            "lesson_id": str(lesson.id)
        }
        
        response = authenticated_client.post("/api/v1/bookmarks", json=bookmark_data)
        
        assert response.status_code == 409
        assert response.json()["detail"] == "Bookmark already exists"
    
    def test_get_user_bookmarks(self, authenticated_client, db_session, test_user, test_lessons):
        """Test getting user bookmarks."""
        # Create bookmarks for first two lessons
        for lesson in test_lessons[:2]:
            bookmark = UserBookmark(
                user_id=test_user.id,
                lesson_id=lesson.id
            )
            db_session.add(bookmark)
        db_session.commit()
        
        response = authenticated_client.get(f"/api/v1/users/{test_user.id}/bookmarks")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(bookmark["user_id"] == str(test_user.id) for bookmark in data)
        assert all("lesson" in bookmark for bookmark in data)
    
    def test_delete_bookmark(self, authenticated_client, db_session, test_user, test_lessons):
        """Test deleting a bookmark."""
        lesson = test_lessons[0]
        bookmark = UserBookmark(
            user_id=test_user.id,
            lesson_id=lesson.id
        )
        db_session.add(bookmark)
        db_session.commit()
        db_session.refresh(bookmark)
        
        response = authenticated_client.delete(f"/api/v1/bookmarks/{bookmark.id}")
        
        assert response.status_code == 204
        
        # Verify bookmark is deleted
        deleted_bookmark = db_session.query(UserBookmark).filter(UserBookmark.id == bookmark.id).first()
        assert deleted_bookmark is None
    
    def test_delete_bookmark_by_lesson(self, authenticated_client, db_session, test_user, test_lessons):
        """Test deleting a bookmark by lesson ID."""
        lesson = test_lessons[0]
        bookmark = UserBookmark(
            user_id=test_user.id,
            lesson_id=lesson.id
        )
        db_session.add(bookmark)
        db_session.commit()
        
        response = authenticated_client.delete(f"/api/v1/bookmarks/lesson/{lesson.id}")
        
        assert response.status_code == 204
        
        # Verify bookmark is deleted
        deleted_bookmark = db_session.query(UserBookmark).filter(
            UserBookmark.user_id == test_user.id,
            UserBookmark.lesson_id == lesson.id
        ).first()
        assert deleted_bookmark is None


class TestValidation:
    """Test input validation and error handling."""
    
    def test_invalid_lesson_progress_status(self, authenticated_client, test_lessons):
        """Test creating progress with invalid status."""
        progress_data = {
            "lesson_id": str(test_lessons[0].id),
            "status": "invalid_status",
            "time_spent": 300,
            "score": 85
        }
        
        response = authenticated_client.post("/api/v1/progress/lesson", json=progress_data)
        
        assert response.status_code == 422
    
    def test_negative_time_spent(self, authenticated_client, test_lessons):
        """Test creating progress with negative time spent."""
        progress_data = {
            "lesson_id": str(test_lessons[0].id),
            "status": "in_progress",
            "time_spent": -100,
            "score": 85
        }
        
        response = authenticated_client.post("/api/v1/progress/lesson", json=progress_data)
        
        assert response.status_code == 422
    
    def test_nonexistent_lesson_progress(self, authenticated_client):
        """Test creating progress for nonexistent lesson."""
        progress_data = {
            "lesson_id": str(uuid.uuid4()),
            "status": "in_progress",
            "time_spent": 300,
            "score": 85
        }
        
        response = authenticated_client.post("/api/v1/progress/lesson", json=progress_data)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Lesson not found"
    
    def test_nonexistent_exercise_submission(self, authenticated_client):
        """Test submitting to nonexistent exercise."""
        submission_data = {
            "exercise_id": str(uuid.uuid4()),
            "submitted_code": "print('Hello')"
        }
        
        response = authenticated_client.post("/api/v1/exercises/submit", json=submission_data)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Exercise not found"
    
    def test_nonexistent_lesson_bookmark(self, authenticated_client):
        """Test bookmarking nonexistent lesson."""
        bookmark_data = {
            "lesson_id": str(uuid.uuid4())
        }
        
        response = authenticated_client.post("/api/v1/bookmarks", json=bookmark_data)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Lesson not found"