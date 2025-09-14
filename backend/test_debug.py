"""
Debug test to check what's happening
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.main import app
from tests.test_models_sqlite import (
    User, UserProgress, UserBookmark, LearningModule, Lesson, Exercise, 
    ExerciseSubmission
)
from app.auth import create_access_token
from tests.conftest import db_session


def mock_get_current_user(test_user):
    """Create a mock get_current_user dependency."""
    def _mock():
        return test_user
    return _mock


def test_debug():
    # Create test data
    from tests.conftest import TestingSessionLocal, Base, engine
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        # Create test user
        user = User(
            email="testuser@example.com",
            username="testuser",
            password_hash="hashed_password",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create test module
        module = LearningModule(
            name="Test Flask Module",
            description="Test module for Flask basics",
            technology="flask",
            difficulty_level="beginner",
            order_index=1,
            estimated_duration=120
        )
        db.add(module)
        db.commit()
        db.refresh(module)
        
        # Create test lesson
        lesson = Lesson(
            module_id=module.id,
            title="Test Lesson 1",
            content="Content for lesson 1",
            order_index=1,
            estimated_duration=30
        )
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        
        print(f"Created user: {user.id}")
        print(f"Created module: {module.id}")
        print(f"Created lesson: {lesson.id}")
        
        # Set up client
        from app.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = mock_get_current_user(user)
        
        client = TestClient(app)
        
        # Test the endpoint
        progress_data = {
            "lesson_id": str(lesson.id),
            "status": "in_progress",
            "time_spent": 300,
            "score": 85
        }
        
        response = client.post("/api/v1/progress/lesson", json=progress_data)
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code != 201:
            print("ERROR: Expected 201, got", response.status_code)
        else:
            print("SUCCESS: Got 201 as expected")
            
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]


if __name__ == "__main__":
    test_debug()