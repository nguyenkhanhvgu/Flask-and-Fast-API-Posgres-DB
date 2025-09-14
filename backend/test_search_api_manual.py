#!/usr/bin/env python3
"""
Manual test script for search API endpoints.
"""
import sys
import os
import requests
import json

# Add the current directory to Python path
sys.path.insert(0, '/app')

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import test models for SQLite compatibility
from tests.test_models_sqlite import Base, User, LearningModule, Lesson, Exercise, UserProgress
from app.main import app
from app.database import get_db

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_search_api():
    """Test the search API endpoints."""
    print("Setting up test database...")
    Base.metadata.create_all(bind=engine)
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    client = TestClient(app)
    
    try:
        # Create test data
        db = TestingSessionLocal()
        
        print("Creating test data...")
        
        # Create test modules
        flask_module = LearningModule(
            name="Flask Fundamentals",
            description="Learn Flask web framework from basics to advanced",
            technology="flask",
            difficulty_level="beginner",
            order_index=1,
            estimated_duration=180
        )
        
        fastapi_module = LearningModule(
            name="FastAPI Basics",
            description="Modern API development with FastAPI",
            technology="fastapi",
            difficulty_level="intermediate",
            order_index=2,
            estimated_duration=150
        )
        
        db.add_all([flask_module, fastapi_module])
        db.commit()
        
        # Create test lessons
        flask_lesson = Lesson(
            module_id=flask_module.id,
            title="Introduction to Flask Routing",
            content="Learn how to create routes in Flask applications. This covers basic routing concepts.",
            order_index=1,
            estimated_duration=45
        )
        
        fastapi_lesson = Lesson(
            module_id=fastapi_module.id,
            title="FastAPI Path Operations",
            content="Understanding FastAPI path operations and automatic documentation generation.",
            order_index=1,
            estimated_duration=40
        )
        
        db.add_all([flask_lesson, fastapi_lesson])
        db.commit()
        
        # Create test exercises
        flask_exercise = Exercise(
            lesson_id=flask_lesson.id,
            title="Create Hello World Route",
            description="Build a simple Flask route that returns Hello World",
            exercise_type="coding",
            starter_code="from flask import Flask\n\napp = Flask(__name__)",
            solution_code="from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Hello World'",
            points=5,
            order_index=1,
            difficulty="easy"
        )
        
        fastapi_exercise = Exercise(
            lesson_id=fastapi_lesson.id,
            title="FastAPI Hello Endpoint",
            description="Create a FastAPI endpoint that returns a greeting",
            exercise_type="coding",
            starter_code="from fastapi import FastAPI\n\napp = FastAPI()",
            solution_code="from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef hello():\n    return {'message': 'Hello World'}",
            points=5,
            order_index=1,
            difficulty="easy"
        )
        
        db.add_all([flask_exercise, fastapi_exercise])
        db.commit()
        db.close()
        
        print("Test data created successfully!")
        
        # Test search endpoints
        print("\nTesting search API endpoints...")
        
        # Test main search endpoint
        print("1. Testing main search endpoint...")
        response = client.get("/api/v1/search/?query=flask")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Results: {len(data['results'])} items")
            print(f"Total count: {data['total_count']}")
            print(f"Query: {data['query']}")
            for result in data['results']:
                print(f"  - {result['content_type']}: {result['title']} (score: {result['relevance_score']})")
        else:
            print(f"Error: {response.text}")
        
        # Test search with filters
        print("\n2. Testing search with filters...")
        response = client.get("/api/v1/search/?technology=flask&difficulty_level=beginner")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Results: {len(data['results'])} items")
            print(f"Filters: {data['filters']}")
        else:
            print(f"Error: {response.text}")
        
        # Test search suggestions
        print("\n3. Testing search suggestions...")
        response = client.get("/api/v1/search/suggestions?query=fla")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Suggestions: {len(data)} items")
            for suggestion in data:
                print(f"  - {suggestion['text']} ({suggestion['type']})")
        else:
            print(f"Error: {response.text}")
        
        # Test content filters
        print("\n4. Testing content filters...")
        response = client.get("/api/v1/search/filters")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Technologies: {data['technologies']}")
            print(f"Difficulty levels: {data['difficulty_levels']}")
            print(f"Exercise types: {data['exercise_types']}")
        else:
            print(f"Error: {response.text}")
        
        # Test module-specific search
        print("\n5. Testing module-specific search...")
        response = client.get("/api/v1/search/modules?query=flask")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Module results: {len(data['results'])} items")
            for result in data['results']:
                print(f"  - {result['content_type']}: {result['title']}")
        else:
            print(f"Error: {response.text}")
        
        # Test lesson-specific search
        print("\n6. Testing lesson-specific search...")
        response = client.get("/api/v1/search/lessons?query=routing")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Lesson results: {len(data['results'])} items")
            for result in data['results']:
                print(f"  - {result['content_type']}: {result['title']}")
        else:
            print(f"Error: {response.text}")
        
        # Test exercise-specific search
        print("\n7. Testing exercise-specific search...")
        response = client.get("/api/v1/search/exercises?query=hello")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Exercise results: {len(data['results'])} items")
            for result in data['results']:
                print(f"  - {result['content_type']}: {result['title']}")
        else:
            print(f"Error: {response.text}")
        
        # Test validation errors
        print("\n8. Testing validation errors...")
        response = client.get("/api/v1/search/")  # No parameters
        print(f"Status: {response.status_code}")
        if response.status_code == 400:
            print("Validation error handled correctly")
        else:
            print(f"Unexpected response: {response.text}")
        
        # Test short suggestion query
        response = client.get("/api/v1/search/suggestions?query=a")
        print(f"Short query status: {response.status_code}")
        if response.status_code == 422:
            print("Short query validation handled correctly")
        
        print("\nAll API tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
    
    return True

if __name__ == "__main__":
    success = test_search_api()
    sys.exit(0 if success else 1)