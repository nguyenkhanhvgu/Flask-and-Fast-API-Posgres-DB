"""
Search and content discovery API endpoints.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from ..database import get_db
from ..services.search import SearchService
from ..schemas import (
    SearchResponse, SearchSuggestion, ContentFilter,
    ContentSearchParams
)
from ..dependencies import get_current_user_optional

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("/", response_model=SearchResponse)
async def search_content(
    query: Optional[str] = Query(None, description="Search query"),
    technology: Optional[str] = Query(None, description="Filter by technology"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    exercise_type: Optional[str] = Query(None, description="Filter by exercise type"),
    completion_status: Optional[str] = Query(None, description="Filter by completion status"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """
    Search across modules, lessons, and exercises with advanced filtering and ranking.
    """
    if not query and not any([technology, difficulty_level, exercise_type, completion_status]):
        raise HTTPException(
            status_code=400,
            detail="At least one search parameter (query or filter) must be provided"
        )
    
    search_service = SearchService(db)
    user_id = current_user.id if current_user else None
    
    return search_service.search_content(
        query=query,
        technology=technology,
        difficulty_level=difficulty_level,
        exercise_type=exercise_type,
        completion_status=completion_status,
        user_id=user_id,
        limit=limit,
        offset=offset
    )


@router.get("/suggestions", response_model=List[SearchSuggestion])
async def get_search_suggestions(
    query: str = Query(..., min_length=2, description="Partial search query"),
    limit: int = Query(10, ge=1, le=20, description="Number of suggestions to return"),
    db: Session = Depends(get_db)
):
    """
    Get autocomplete suggestions for search queries.
    """
    search_service = SearchService(db)
    return search_service.get_autocomplete_suggestions(query, limit)


@router.get("/filters", response_model=ContentFilter)
async def get_content_filters(db: Session = Depends(get_db)):
    """
    Get available filter options for content search.
    """
    search_service = SearchService(db)
    return search_service.get_content_filters()


@router.get("/modules")
async def search_modules(
    query: Optional[str] = Query(None, description="Search query"),
    technology: Optional[str] = Query(None, description="Filter by technology"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    completion_status: Optional[str] = Query(None, description="Filter by completion status"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """
    Search specifically for learning modules.
    """
    search_service = SearchService(db)
    user_id = current_user.id if current_user else None
    
    # Get full search results and filter for modules only
    full_results = search_service.search_content(
        query=query,
        technology=technology,
        difficulty_level=difficulty_level,
        completion_status=completion_status,
        user_id=user_id,
        limit=limit * 3,  # Get more to account for filtering
        offset=0
    )
    
    # Filter for modules only
    module_results = [r for r in full_results.results if r.content_type == "module"]
    
    # Apply pagination to filtered results
    paginated_modules = module_results[offset:offset + limit]
    
    return {
        "results": paginated_modules,
        "total_count": len(module_results),
        "query": query,
        "filters": {
            "technology": technology,
            "difficulty_level": difficulty_level,
            "completion_status": completion_status
        }
    }


@router.get("/lessons")
async def search_lessons(
    query: Optional[str] = Query(None, description="Search query"),
    technology: Optional[str] = Query(None, description="Filter by technology"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    completion_status: Optional[str] = Query(None, description="Filter by completion status"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """
    Search specifically for lessons.
    """
    search_service = SearchService(db)
    user_id = current_user.id if current_user else None
    
    # Get full search results and filter for lessons only
    full_results = search_service.search_content(
        query=query,
        technology=technology,
        difficulty_level=difficulty_level,
        completion_status=completion_status,
        user_id=user_id,
        limit=limit * 3,  # Get more to account for filtering
        offset=0
    )
    
    # Filter for lessons only
    lesson_results = [r for r in full_results.results if r.content_type == "lesson"]
    
    # Apply pagination to filtered results
    paginated_lessons = lesson_results[offset:offset + limit]
    
    return {
        "results": paginated_lessons,
        "total_count": len(lesson_results),
        "query": query,
        "filters": {
            "technology": technology,
            "difficulty_level": difficulty_level,
            "completion_status": completion_status
        }
    }


@router.get("/exercises")
async def search_exercises(
    query: Optional[str] = Query(None, description="Search query"),
    technology: Optional[str] = Query(None, description="Filter by technology"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    exercise_type: Optional[str] = Query(None, description="Filter by exercise type"),
    completion_status: Optional[str] = Query(None, description="Filter by completion status"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """
    Search specifically for exercises.
    """
    search_service = SearchService(db)
    user_id = current_user.id if current_user else None
    
    # Get full search results and filter for exercises only
    full_results = search_service.search_content(
        query=query,
        technology=technology,
        difficulty_level=difficulty_level,
        exercise_type=exercise_type,
        completion_status=completion_status,
        user_id=user_id,
        limit=limit * 3,  # Get more to account for filtering
        offset=0
    )
    
    # Filter for exercises only
    exercise_results = [r for r in full_results.results if r.content_type == "exercise"]
    
    # Apply pagination to filtered results
    paginated_exercises = exercise_results[offset:offset + limit]
    
    return {
        "results": paginated_exercises,
        "total_count": len(exercise_results),
        "query": query,
        "filters": {
            "technology": technology,
            "difficulty_level": difficulty_level,
            "exercise_type": exercise_type,
            "completion_status": completion_status
        }
    }


@router.get("/popular")
async def get_popular_content(
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    technology: Optional[str] = Query(None, description="Filter by technology"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """
    Get popular content based on user engagement metrics.
    """
    # This is a placeholder implementation
    # In a real system, you would track user engagement metrics
    search_service = SearchService(db)
    
    # For now, return content ordered by creation date (newest first)
    results = search_service.search_content(
        technology=technology,
        limit=limit
    )
    
    return {
        "results": results.results,
        "content_type": content_type,
        "technology": technology
    }


@router.get("/recent")
async def get_recent_content(
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    technology: Optional[str] = Query(None, description="Filter by technology"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """
    Get recently added content.
    """
    search_service = SearchService(db)
    
    # Return content ordered by creation date (newest first)
    results = search_service.search_content(
        technology=technology,
        limit=limit
    )
    
    return {
        "results": results.results,
        "content_type": content_type,
        "technology": technology
    }