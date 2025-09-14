"""
Unit tests for search functionality and API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid

from app.main import app
from app.services.search import SearchService
from app.schemas import SearchResult, SearchResponse

# Import test models for SQLite compatibility
from .test_models_sqlite import User, LearningModule, Lesson, Exercise, UserProgress


class TestSearchService:
    """Test cases for SearchService."""
    
    def test_extract_search_terms(self, db_session: Session):
        """Test search term extraction."""
        search_service = SearchService(db_session)
        
        # Test basic term extraction
        terms = search_service._extract_search_terms("flask routing")
        assert "flask" in terms
        assert "routing" in terms
        
        # Test special character removal
        terms = search_service._extract_search_terms("flask-api & routing!")
        assert "flask" in terms
        assert "api" in terms
        assert "routing" in terms
        
        # Test minimum length filtering
        terms = search_service._extract_search_terms("a flask to do")
        assert "a" not in terms
        assert "to" not in terms
        assert "flask" in terms
    
    def test_calculate_module_relevance(self, db_session: Session, sample_module):
        """Test module relevance scoring."""
        search_service = SearchService(db_session)
        
        # Test exact title match
        score = search_service._calculate_module_relevance(sample_module, "Flask Basics")
        assert score > 0
        
        # Test technology match
        score = search_service._calculate_module_relevance(sample_module, "flask")
        assert score > 0
        
        # Test no match
        score = search_service._calculate_module_relevance(sample_module, "unrelated")
        assert score == 0
    
    def test_calculate_lesson_relevance(self, db_session: Session, sample_lesson):
        """Test lesson relevance scoring."""
        search_service = SearchService(db_session)
        
        # Test title match
        score = search_service._calculate_lesson_relevance(sample_lesson, "Introduction")
        assert score > 0
        
        # Test content match
        score = search_service._calculate_lesson_relevance(sample_lesson, "routing")
        assert score > 0
    
    def test_calculate_exercise_relevance(self, db_session: Session, sample_exercise):
        """Test exercise relevance scoring."""
        search_service = SearchService(db_session)
        
        # Test title match
        score = search_service._calculate_exercise_relevance(sample_exercise, "Hello World")
        assert score > 0
        
        # Test description match
        score = search_service._calculate_exercise_relevance(sample_exercise, "simple")
        assert score > 0
    
    def test_extract_description(self, db_session: Session):
        """Test description extraction from content."""
        search_service = SearchService(db_session)
        
        # Test basic extraction
        content = "This is the first paragraph.\n\nThis is the second paragraph."
        description = search_service._extract_description(content)
        assert description == "This is the first paragraph."
        
        # Test markdown removal
        content = "# Title\n\nThis is **bold** text with `code`."
        description = search_service._extract_description(content)
        assert "Title" in description
        assert "**" not in description
        assert "`" not in description
        
        # Test truncation
        long_content = "A" * 300
        description = search_service._extract_description(long_content, max_length=100)
        assert len(description) <= 103  # 100 + "..."
        assert description.endswith("...")
    
    def test_search_modules_basic(self, db_session: Session, sample_data):
        """Test basic module search."""
        search_service = SearchService(db_session)
        
        # Test search without query
        results = search_service.search_content(technology="flask")
        assert len(results.results) > 0
        assert all(r.technology == "flask" for r in results.results if r.content_type == "module")
        
        # Test search with query
        results = search_service.search_content(query="flask")
        assert len(results.results) > 0
        assert any("flask" in r.title.lower() for r in results.results)
    
    def test_search_lessons_basic(self, db_session: Session, sample_data):
        """Test basic lesson search."""
        search_service = SearchService(db_session)
        
        # Test search with query
        results = search_service.search_content(query="introduction")
        lesson_results = [r for r in results.results if r.content_type == "lesson"]
        assert len(lesson_results) > 0
    
    def test_search_exercises_basic(self, db_session: Session, sample_data):
        """Test basic exercise search."""
        search_service = SearchService(db_session)
        
        # Test search with query
        results = search_service.search_content(query="hello")
        exercise_results = [r for r in results.results if r.content_type == "exercise"]
        assert len(exercise_results) > 0
    
    def test_search_with_filters(self, db_session: Session, sample_data):
        """Test search with multiple filters."""
        search_service = SearchService(db_session)
        
        # Test technology filter
        results = search_service.search_content(technology="flask")
        assert all(r.technology == "flask" for r in results.results)
        
        # Test difficulty filter
        results = search_service.search_content(difficulty_level="beginner")
        assert all(r.difficulty_level == "beginner" for r in results.results)
        
        # Test combined filters
        results = search_service.search_content(
            technology="flask",
            difficulty_level="beginner"
        )
        assert all(
            r.technology == "flask" and r.difficulty_level == "beginner"
            for r in results.results
        )
    
    def test_search_with_user_progress(self, db_session: Session, sample_data, sample_user):
        """Test search with user progress filtering."""
        # Create some progress data
        lesson = db_session.query(Lesson).first()
        progress = UserProgress(
            user_id=sample_user.id,
            lesson_id=lesson.id,
            status="completed"
        )
        db_session.add(progress)
        db_session.commit()
        
        search_service = SearchService(db_session)
        
        # Test completed filter
        results = search_service.search_content(
            completion_status="completed",
            user_id=sample_user.id
        )
        assert len(results.results) > 0
        
        # Test not_started filter
        results = search_service.search_content(
            completion_status="not_started",
            user_id=sample_user.id
        )
        # Should return content without progress records
        assert isinstance(results, SearchResponse)
    
    def test_search_pagination(self, db_session: Session, sample_data):
        """Test search pagination."""
        search_service = SearchService(db_session)
        
        # Test limit
        results = search_service.search_content(limit=2)
        assert len(results.results) <= 2
        
        # Test offset
        all_results = search_service.search_content(limit=100)
        if len(all_results.results) > 2:
            offset_results = search_service.search_content(limit=2, offset=1)
            assert len(offset_results.results) <= 2
            # Results should be different due to offset
            if len(all_results.results) > 1:
                assert offset_results.results[0].id != all_results.results[0].id
    
    def test_search_relevance_ranking(self, db_session: Session, sample_data):
        """Test search result relevance ranking."""
        search_service = SearchService(db_session)
        
        results = search_service.search_content(query="flask")
        
        # Results should be sorted by relevance score (descending)
        if len(results.results) > 1:
            for i in range(len(results.results) - 1):
                assert results.results[i].relevance_score >= results.results[i + 1].relevance_score
    
    def test_get_content_filters(self, db_session: Session, sample_data):
        """Test getting available content filters."""
        search_service = SearchService(db_session)
        
        filters = search_service.get_content_filters()
        
        assert len(filters.technologies) > 0
        assert len(filters.difficulty_levels) > 0
        assert len(filters.exercise_types) > 0
        assert "not_started" in filters.completion_statuses
        assert "in_progress" in filters.completion_statuses
        assert "completed" in filters.completion_statuses
    
    def test_get_autocomplete_suggestions(self, db_session: Session, sample_data):
        """Test autocomplete suggestions."""
        search_service = SearchService(db_session)
        
        # Test with partial technology name
        suggestions = search_service.get_autocomplete_suggestions("fla")
        assert len(suggestions) > 0
        assert any("flask" in s.text.lower() for s in suggestions)
        
        # Test with partial lesson title
        suggestions = search_service.get_autocomplete_suggestions("intro")
        assert len(suggestions) > 0
    
    def test_generate_suggestions(self, db_session: Session, sample_data):
        """Test search suggestion generation."""
        search_service = SearchService(db_session)
        
        suggestions = search_service._generate_suggestions("fla")
        assert len(suggestions) > 0
        assert any("flask" in s.lower() for s in suggestions)
    
    def test_generate_facets(self, db_session: Session, sample_data):
        """Test facet generation for filtering."""
        search_service = SearchService(db_session)
        
        facets = search_service._generate_facets(None, None, None)
        
        assert "technologies" in facets
        assert "difficulty_levels" in facets
        assert "exercise_types" in facets
        
        # Each facet should have value and count
        for tech_facet in facets["technologies"]:
            assert "value" in tech_facet
            assert "count" in tech_facet
            assert tech_facet["count"] > 0


class TestSearchAPI:
    """Test cases for search API endpoints."""
    
    def test_search_content_endpoint(self, client: TestClient, sample_data):
        """Test main search endpoint."""
        # Test basic search
        response = client.get("/api/v1/search/?query=flask")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_count" in data
        assert "query" in data
        assert data["query"] == "flask"
        
        # Test search with filters
        response = client.get("/api/v1/search/?technology=flask&difficulty_level=beginner")
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["technology"] == "flask"
        assert data["filters"]["difficulty_level"] == "beginner"
    
    def test_search_content_validation(self, client: TestClient):
        """Test search endpoint validation."""
        # Test without any parameters
        response = client.get("/api/v1/search/")
        assert response.status_code == 400
        assert "At least one search parameter" in response.json()["detail"]
    
    def test_search_suggestions_endpoint(self, client: TestClient, sample_data):
        """Test search suggestions endpoint."""
        response = client.get("/api/v1/search/suggestions?query=fla")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            suggestion = data[0]
            assert "text" in suggestion
            assert "type" in suggestion
            assert "count" in suggestion
    
    def test_search_suggestions_validation(self, client: TestClient):
        """Test search suggestions validation."""
        # Test with too short query
        response = client.get("/api/v1/search/suggestions?query=a")
        assert response.status_code == 422  # Validation error
    
    def test_get_content_filters_endpoint(self, client: TestClient, sample_data):
        """Test content filters endpoint."""
        response = client.get("/api/v1/search/filters")
        assert response.status_code == 200
        data = response.json()
        
        assert "technologies" in data
        assert "difficulty_levels" in data
        assert "exercise_types" in data
        assert "completion_statuses" in data
        
        assert isinstance(data["technologies"], list)
        assert isinstance(data["difficulty_levels"], list)
        assert isinstance(data["exercise_types"], list)
        assert isinstance(data["completion_statuses"], list)
    
    def test_search_modules_endpoint(self, client: TestClient, sample_data):
        """Test module-specific search endpoint."""
        response = client.get("/api/v1/search/modules?query=flask")
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "total_count" in data
        
        # All results should be modules
        for result in data["results"]:
            assert result["content_type"] == "module"
    
    def test_search_lessons_endpoint(self, client: TestClient, sample_data):
        """Test lesson-specific search endpoint."""
        response = client.get("/api/v1/search/lessons?query=introduction")
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "total_count" in data
        
        # All results should be lessons
        for result in data["results"]:
            assert result["content_type"] == "lesson"
    
    def test_search_exercises_endpoint(self, client: TestClient, sample_data):
        """Test exercise-specific search endpoint."""
        response = client.get("/api/v1/search/exercises?query=hello")
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "total_count" in data
        
        # All results should be exercises
        for result in data["results"]:
            assert result["content_type"] == "exercise"
    
    def test_search_pagination_endpoints(self, client: TestClient, sample_data):
        """Test pagination in search endpoints."""
        # Test limit parameter
        response = client.get("/api/v1/search/?query=flask&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= 2
        
        # Test offset parameter
        response = client.get("/api/v1/search/?query=flask&limit=2&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= 2
    
    def test_popular_content_endpoint(self, client: TestClient, sample_data):
        """Test popular content endpoint."""
        response = client.get("/api/v1/search/popular")
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)
    
    def test_recent_content_endpoint(self, client: TestClient, sample_data):
        """Test recent content endpoint."""
        response = client.get("/api/v1/search/recent")
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)
    
    def test_search_with_authentication(self, client: TestClient, sample_data, auth_headers):
        """Test search with authenticated user."""
        response = client.get(
            "/api/v1/search/?query=flask",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
    
    def test_search_parameter_validation(self, client: TestClient):
        """Test search parameter validation."""
        # Test invalid limit
        response = client.get("/api/v1/search/?query=flask&limit=0")
        assert response.status_code == 422
        
        # Test invalid offset
        response = client.get("/api/v1/search/?query=flask&offset=-1")
        assert response.status_code == 422
        
        # Test limit too high
        response = client.get("/api/v1/search/?query=flask&limit=200")
        assert response.status_code == 422


# Fixtures for testing
@pytest.fixture
def sample_module(db_session: Session):
    """Create a sample learning module for testing."""
    module = LearningModule(
        name="Flask Basics",
        description="Learn the basics of Flask web framework",
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
def sample_lesson(db_session: Session, sample_module):
    """Create a sample lesson for testing."""
    lesson = Lesson(
        module_id=sample_module.id,
        title="Introduction to Flask",
        content="This lesson covers Flask routing and basic concepts.",
        order_index=1,
        estimated_duration=30
    )
    db_session.add(lesson)
    db_session.commit()
    db_session.refresh(lesson)
    return lesson


@pytest.fixture
def sample_exercise(db_session: Session, sample_lesson):
    """Create a sample exercise for testing."""
    exercise = Exercise(
        lesson_id=sample_lesson.id,
        title="Hello World Flask App",
        description="Create a simple Flask application that returns 'Hello World'",
        exercise_type="coding",
        starter_code="from flask import Flask\n\napp = Flask(__name__)",
        solution_code="from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Hello World'",
        points=10,
        order_index=1,
        difficulty="easy"
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    return exercise


@pytest.fixture
def sample_user(db_session: Session):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_data(db_session: Session):
    """Create comprehensive sample data for testing."""
    # Create modules
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
    
    db_session.add_all([flask_module, fastapi_module])
    db_session.commit()
    
    # Create lessons
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
    
    db_session.add_all([flask_lesson, fastapi_lesson])
    db_session.commit()
    
    # Create exercises
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
    
    db_session.add_all([flask_exercise, fastapi_exercise])
    db_session.commit()
    
    return {
        "modules": [flask_module, fastapi_module],
        "lessons": [flask_lesson, fastapi_lesson],
        "exercises": [flask_exercise, fastapi_exercise]
    }