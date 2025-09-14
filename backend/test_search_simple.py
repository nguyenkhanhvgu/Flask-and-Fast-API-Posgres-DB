#!/usr/bin/env python3
"""
Simple test script for search functionality without FastAPI dependencies.
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

def test_search_comprehensive():
    """Comprehensive test of search functionality."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    try:
        print("Creating comprehensive test data...")
        
        # Create multiple modules with different technologies and difficulties
        modules = [
            LearningModule(
                name="Flask Fundamentals",
                description="Learn Flask web framework from basics to advanced concepts",
                technology="flask",
                difficulty_level="beginner",
                order_index=1,
                estimated_duration=180
            ),
            LearningModule(
                name="Flask Advanced Topics",
                description="Advanced Flask concepts including blueprints and testing",
                technology="flask",
                difficulty_level="advanced",
                order_index=2,
                estimated_duration=240
            ),
            LearningModule(
                name="FastAPI Basics",
                description="Modern API development with FastAPI and async programming",
                technology="fastapi",
                difficulty_level="intermediate",
                order_index=3,
                estimated_duration=150
            ),
            LearningModule(
                name="PostgreSQL Database Design",
                description="Database design and optimization with PostgreSQL",
                technology="postgresql",
                difficulty_level="intermediate",
                order_index=4,
                estimated_duration=200
            )
        ]
        
        db.add_all(modules)
        db.commit()
        
        # Create lessons for each module
        lessons = []
        for i, module in enumerate(modules):
            db.refresh(module)
            lesson = Lesson(
                module_id=module.id,
                title=f"Introduction to {module.technology.title()}",
                content=f"This lesson covers the fundamentals of {module.technology}. Learn about routing, configuration, and best practices.",
                order_index=1,
                estimated_duration=45
            )
            lessons.append(lesson)
        
        db.add_all(lessons)
        db.commit()
        
        # Create exercises for each lesson
        exercises = []
        for i, lesson in enumerate(lessons):
            db.refresh(lesson)
            exercise = Exercise(
                lesson_id=lesson.id,
                title=f"Hello World with {lesson.module.technology.title()}",
                description=f"Create a simple {lesson.module.technology} application that returns Hello World",
                exercise_type="coding",
                starter_code=f"# {lesson.module.technology.title()} starter code",
                solution_code=f"# {lesson.module.technology.title()} solution",
                points=10,
                order_index=1,
                difficulty="easy"
            )
            exercises.append(exercise)
        
        db.add_all(exercises)
        db.commit()
        
        print(f"Created {len(modules)} modules, {len(lessons)} lessons, {len(exercises)} exercises")
        
        # Initialize search service
        search_service = SearchService(db)
        
        # Test 1: Basic search functionality
        print("\n=== Test 1: Basic Search ===")
        results = search_service.search_content(query="flask")
        print(f"Search for 'flask': {len(results.results)} results, total: {results.total_count}")
        
        flask_results = [r for r in results.results if "flask" in r.title.lower() or "flask" in r.description.lower()]
        print(f"Flask-related results: {len(flask_results)}")
        
        # Test 2: Technology filtering
        print("\n=== Test 2: Technology Filtering ===")
        results = search_service.search_content(technology="fastapi")
        print(f"FastAPI technology filter: {len(results.results)} results")
        
        for result in results.results:
            assert result.technology == "fastapi", f"Expected fastapi, got {result.technology}"
        print("✓ All results have correct technology")
        
        # Test 3: Difficulty filtering
        print("\n=== Test 3: Difficulty Filtering ===")
        results = search_service.search_content(difficulty_level="beginner")
        print(f"Beginner difficulty filter: {len(results.results)} results")
        
        for result in results.results:
            assert result.difficulty_level == "beginner", f"Expected beginner, got {result.difficulty_level}"
        print("✓ All results have correct difficulty level")
        
        # Test 4: Combined filters
        print("\n=== Test 4: Combined Filters ===")
        results = search_service.search_content(
            query="flask",
            technology="flask",
            difficulty_level="beginner"
        )
        print(f"Combined filters (flask + beginner): {len(results.results)} results")
        
        # Test 5: Relevance scoring
        print("\n=== Test 5: Relevance Scoring ===")
        results = search_service.search_content(query="flask fundamentals")
        print("Relevance scores for 'flask fundamentals':")
        for result in results.results[:3]:  # Top 3 results
            print(f"  {result.content_type}: {result.title} - Score: {result.relevance_score:.2f}")
        
        # Verify results are sorted by relevance
        scores = [r.relevance_score for r in results.results]
        assert scores == sorted(scores, reverse=True), "Results should be sorted by relevance score"
        print("✓ Results are properly sorted by relevance")
        
        # Test 6: Content type filtering
        print("\n=== Test 6: Content Type Results ===")
        results = search_service.search_content(query="introduction")
        
        modules = [r for r in results.results if r.content_type == "module"]
        lessons = [r for r in results.results if r.content_type == "lesson"]
        exercises = [r for r in results.results if r.content_type == "exercise"]
        
        print(f"Results for 'introduction': {len(modules)} modules, {len(lessons)} lessons, {len(exercises)} exercises")
        
        # Test 7: Autocomplete suggestions
        print("\n=== Test 7: Autocomplete Suggestions ===")
        suggestions = search_service.get_autocomplete_suggestions("fla")
        print(f"Suggestions for 'fla': {[s.text for s in suggestions]}")
        
        suggestions = search_service.get_autocomplete_suggestions("post")
        print(f"Suggestions for 'post': {[s.text for s in suggestions]}")
        
        # Test 8: Content filters
        print("\n=== Test 8: Content Filters ===")
        filters = search_service.get_content_filters()
        print(f"Available technologies: {filters.technologies}")
        print(f"Available difficulty levels: {filters.difficulty_levels}")
        print(f"Available exercise types: {filters.exercise_types}")
        print(f"Available completion statuses: {filters.completion_statuses}")
        
        # Verify expected values
        assert "flask" in filters.technologies
        assert "fastapi" in filters.technologies
        assert "postgresql" in filters.technologies
        assert "beginner" in filters.difficulty_levels
        assert "intermediate" in filters.difficulty_levels
        assert "advanced" in filters.difficulty_levels
        print("✓ Content filters contain expected values")
        
        # Test 9: Search facets
        print("\n=== Test 9: Search Facets ===")
        results = search_service.search_content(query="flask")
        print(f"Facets for 'flask' search: {list(results.facets.keys())}")
        
        if "technologies" in results.facets:
            tech_facets = results.facets["technologies"]
            print(f"Technology facets: {[(f['value'], f['count']) for f in tech_facets]}")
        
        # Test 10: Pagination
        print("\n=== Test 10: Pagination ===")
        all_results = search_service.search_content(limit=100)
        page1 = search_service.search_content(limit=2, offset=0)
        page2 = search_service.search_content(limit=2, offset=2)
        
        print(f"Total results: {all_results.total_count}")
        print(f"Page 1 (limit=2, offset=0): {len(page1.results)} results")
        print(f"Page 2 (limit=2, offset=2): {len(page2.results)} results")
        
        if len(all_results.results) >= 4:
            assert page1.results[0].id != page2.results[0].id, "Pages should have different results"
            print("✓ Pagination works correctly")
        
        # Test 11: Empty search handling
        print("\n=== Test 11: Empty Search Handling ===")
        results = search_service.search_content(query="nonexistentterm12345")
        print(f"Search for non-existent term: {len(results.results)} results")
        assert len(results.results) == 0, "Should return no results for non-existent terms"
        print("✓ Empty search handled correctly")
        
        # Test 12: Search term extraction
        print("\n=== Test 12: Search Term Extraction ===")
        terms = search_service._extract_search_terms("flask-api & routing!")
        print(f"Extracted terms from 'flask-api & routing!': {terms}")
        assert "flask" in terms
        assert "api" in terms
        assert "routing" in terms
        print("✓ Search term extraction works correctly")
        
        print("\n🎉 All comprehensive tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
    
    return True

if __name__ == "__main__":
    success = test_search_comprehensive()
    sys.exit(0 if success else 1)