#!/usr/bin/env python3
"""
Manual test script for search functionality.
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, '/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import test models for SQLite compatibility
from tests.test_models_sqlite import Base, User, LearningModule, Lesson, Exercise, UserProgress
from app.services.search import SearchService

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_search_service():
    """Test the search service functionality."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    try:
        print("Creating test data...")
        
        # Create a test module
        flask_module = LearningModule(
            name="Flask Fundamentals",
            description="Learn Flask web framework from basics to advanced",
            technology="flask",
            difficulty_level="beginner",
            order_index=1,
            estimated_duration=180
        )
        db.add(flask_module)
        db.commit()
        db.refresh(flask_module)
        
        # Create a test lesson
        flask_lesson = Lesson(
            module_id=flask_module.id,
            title="Introduction to Flask Routing",
            content="Learn how to create routes in Flask applications. This covers basic routing concepts.",
            order_index=1,
            estimated_duration=45
        )
        db.add(flask_lesson)
        db.commit()
        db.refresh(flask_lesson)
        
        # Create a test exercise
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
        db.add(flask_exercise)
        db.commit()
        
        print("Test data created successfully!")
        
        # Test search service
        print("\nTesting SearchService...")
        search_service = SearchService(db)
        
        # Test search term extraction
        print("Testing search term extraction...")
        terms = search_service._extract_search_terms("flask routing")
        print(f"Search terms for 'flask routing': {terms}")
        assert "flask" in terms
        assert "routing" in terms
        
        # Test search with query
        print("Testing search with query...")
        results = search_service.search_content(query="flask")
        print(f"Search results for 'flask': {len(results.results)} results")
        print(f"Total count: {results.total_count}")
        
        for result in results.results:
            print(f"  - {result.content_type}: {result.title} (score: {result.relevance_score})")
        
        # Test search with filters
        print("Testing search with filters...")
        results = search_service.search_content(technology="flask")
        print(f"Search results for technology='flask': {len(results.results)} results")
        
        # Test content filters
        print("Testing content filters...")
        filters = search_service.get_content_filters()
        print(f"Available technologies: {filters.technologies}")
        print(f"Available difficulty levels: {filters.difficulty_levels}")
        print(f"Available exercise types: {filters.exercise_types}")
        
        # Test autocomplete suggestions
        print("Testing autocomplete suggestions...")
        suggestions = search_service.get_autocomplete_suggestions("fla")
        print(f"Suggestions for 'fla': {[s.text for s in suggestions]}")
        
        print("\nAll tests passed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
    
    return True

if __name__ == "__main__":
    success = test_search_service()
    sys.exit(0 if success else 1)