"""
Progress tracking API endpoints for user learning progress, bookmarks, and statistics.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import and_, func, desc, case
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from ..database import get_db
from ..models import (
    User, UserProgress, UserBookmark, LearningModule, Lesson, Exercise, 
    ExerciseSubmission
)
from ..schemas import (
    UserProgressCreate, UserProgressUpdate, UserProgressResponse,
    LessonProgressResponse, ModuleProgressResponse, UserProgressStats,
    ExerciseSubmissionCreate, ExerciseSubmissionResponse,
    UserBookmarkCreate, UserBookmarkResponse
)
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["progress"])


# User Progress endpoints
@router.get("/users/{user_id}/progress", response_model=List[UserProgressResponse])
async def get_user_progress(
    user_id: uuid.UUID,
    module_id: Optional[uuid.UUID] = Query(None, description="Filter by module ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=500, description="Number of progress records to return"),
    offset: int = Query(0, ge=0, description="Number of progress records to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user progress records."""
    # Users can only access their own progress unless they're admin
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(UserProgress).filter(UserProgress.user_id == user_id)
    
    if module_id:
        query = query.join(Lesson).filter(Lesson.module_id == module_id)
    
    if status:
        query = query.filter(UserProgress.status == status)
    
    progress_records = query.order_by(UserProgress.updated_at.desc()).offset(offset).limit(limit).all()
    return progress_records


@router.get("/users/{user_id}/progress/lessons/{lesson_id}", response_model=UserProgressResponse)
async def get_lesson_progress(
    user_id: uuid.UUID,
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user progress for a specific lesson."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    progress = db.query(UserProgress).filter(
        and_(UserProgress.user_id == user_id, UserProgress.lesson_id == lesson_id)
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    return progress


@router.post("/progress/lesson", response_model=UserProgressResponse, status_code=201)
async def create_or_update_lesson_progress(
    progress_data: UserProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update lesson progress."""
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == progress_data.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if progress already exists
    existing_progress = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == current_user.id,
            UserProgress.lesson_id == progress_data.lesson_id
        )
    ).first()
    
    if existing_progress:
        # Update existing progress
        existing_progress.status = progress_data.status
        existing_progress.time_spent += progress_data.time_spent
        existing_progress.score = max(existing_progress.score, progress_data.score)
        existing_progress.attempts += 1
        
        if progress_data.status == "completed" and not existing_progress.completion_date:
            existing_progress.completion_date = datetime.utcnow()
        
        db.commit()
        db.refresh(existing_progress)
        return existing_progress
    else:
        # Create new progress record
        progress = UserProgress(
            user_id=current_user.id,
            lesson_id=progress_data.lesson_id,
            status=progress_data.status,
            time_spent=progress_data.time_spent,
            score=progress_data.score,
            attempts=1,
            completion_date=datetime.utcnow() if progress_data.status == "completed" else None
        )
        
        db.add(progress)
        db.commit()
        db.refresh(progress)
        return progress


@router.put("/progress/lesson/{lesson_id}", response_model=UserProgressResponse)
async def update_lesson_progress(
    lesson_id: uuid.UUID,
    progress_data: UserProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update lesson progress."""
    progress = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == current_user.id,
            UserProgress.lesson_id == lesson_id
        )
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    # Update fields
    update_data = progress_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "time_spent" and value is not None:
            # Add to existing time instead of replacing
            progress.time_spent += value
        elif field == "score" and value is not None:
            # Keep the highest score
            progress.score = max(progress.score, value)
        elif field == "attempts" and value is not None:
            # Add to existing attempts
            progress.attempts += value
        else:
            setattr(progress, field, value)
    
    # Set completion date if status changed to completed
    if progress_data.status == "completed" and not progress.completion_date:
        progress.completion_date = datetime.utcnow()
    
    db.commit()
    db.refresh(progress)
    return progress


# Module Progress endpoints
@router.get("/users/{user_id}/progress/modules", response_model=List[ModuleProgressResponse])
async def get_user_module_progress(
    user_id: uuid.UUID,
    technology: Optional[str] = Query(None, description="Filter by technology"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user progress across all modules with statistics."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get modules with lesson counts and progress
    query = db.query(
        LearningModule,
        func.count(Lesson.id).label('total_lessons'),
        func.count(case((UserProgress.status == 'completed', 1))).label('completed_lessons'),
        func.count(case((UserProgress.status == 'in_progress', 1))).label('in_progress_lessons'),
        func.coalesce(func.sum(UserProgress.time_spent), 0).label('total_time_spent'),
        func.coalesce(func.sum(UserProgress.score), 0).label('total_score')
    ).outerjoin(Lesson, LearningModule.id == Lesson.module_id)\
     .outerjoin(UserProgress, and_(
         Lesson.id == UserProgress.lesson_id,
         UserProgress.user_id == user_id
     )).group_by(LearningModule.id)
    
    if technology:
        query = query.filter(LearningModule.technology == technology)
    if difficulty_level:
        query = query.filter(LearningModule.difficulty_level == difficulty_level)
    
    results = query.order_by(LearningModule.order_index).all()
    
    module_progress_list = []
    for module, total_lessons, completed_lessons, in_progress_lessons, total_time_spent, total_score in results:
        completion_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        module_progress_list.append(ModuleProgressResponse(
            module=module,
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            in_progress_lessons=in_progress_lessons,
            completion_percentage=round(completion_percentage, 2),
            total_time_spent=total_time_spent,
            total_score=total_score
        ))
    
    return module_progress_list


@router.get("/users/{user_id}/progress/modules/{module_id}/lessons", response_model=List[LessonProgressResponse])
async def get_module_lesson_progress(
    user_id: uuid.UUID,
    module_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user progress for all lessons in a specific module."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Verify module exists
    module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Get lessons with progress
    lessons_with_progress = db.query(Lesson).options(
        selectinload(Lesson.progress.and_(UserProgress.user_id == user_id))
    ).filter(Lesson.module_id == module_id).order_by(Lesson.order_index).all()
    
    result = []
    for lesson in lessons_with_progress:
        progress = lesson.progress[0] if lesson.progress else None
        result.append(LessonProgressResponse(
            lesson=lesson,
            progress=progress
        ))
    
    return result


# Progress Statistics endpoints
@router.get("/users/{user_id}/progress/stats", response_model=UserProgressStats)
async def get_user_progress_stats(
    user_id: uuid.UUID,
    days: int = Query(30, ge=1, le=365, description="Number of days for recent activity"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive user progress statistics."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get overall statistics
    total_modules = db.query(func.count(LearningModule.id)).scalar()
    total_lessons = db.query(func.count(Lesson.id)).scalar()
    
    # Get user progress statistics
    user_progress_stats = db.query(
        func.count(func.distinct(case((UserProgress.status == 'completed', Lesson.module_id)))).label('completed_modules'),
        func.count(func.distinct(case((UserProgress.status == 'in_progress', Lesson.module_id)))).label('in_progress_modules'),
        func.count(case((UserProgress.status == 'completed', 1))).label('completed_lessons'),
        func.count(case((UserProgress.status == 'in_progress', 1))).label('in_progress_lessons'),
        func.coalesce(func.sum(UserProgress.time_spent), 0).label('total_time_spent'),
        func.coalesce(func.sum(UserProgress.score), 0).label('total_score')
    ).select_from(UserProgress)\
     .join(Lesson, UserProgress.lesson_id == Lesson.id)\
     .filter(UserProgress.user_id == user_id).first()
    
    # Get exercise submission count
    total_exercises_attempted = db.query(func.count(func.distinct(ExerciseSubmission.exercise_id)))\
        .filter(ExerciseSubmission.user_id == user_id).scalar() or 0
    
    # Calculate completion percentage
    completion_percentage = (user_progress_stats.completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    # Get progress by technology
    tech_progress = db.query(
        LearningModule.technology,
        func.count(func.distinct(case((UserProgress.status == 'completed', LearningModule.id)))).label('completed'),
        func.count(func.distinct(case((UserProgress.status == 'in_progress', LearningModule.id)))).label('in_progress'),
        func.count(func.distinct(LearningModule.id)).label('total')
    ).select_from(LearningModule)\
     .outerjoin(Lesson, LearningModule.id == Lesson.module_id)\
     .outerjoin(UserProgress, and_(
         Lesson.id == UserProgress.lesson_id,
         UserProgress.user_id == user_id
     )).group_by(LearningModule.technology).all()
    
    modules_by_technology = {}
    for tech, completed, in_progress, total in tech_progress:
        modules_by_technology[tech] = {
            'completed': completed,
            'in_progress': in_progress,
            'total': total
        }
    
    # Get recent activity
    recent_date = datetime.utcnow() - timedelta(days=days)
    recent_activity = db.query(
        UserProgress.updated_at,
        UserProgress.status,
        Lesson.title.label('lesson_title'),
        LearningModule.name.label('module_name'),
        LearningModule.technology
    ).join(Lesson, UserProgress.lesson_id == Lesson.id)\
     .join(LearningModule, Lesson.module_id == LearningModule.id)\
     .filter(
         and_(
             UserProgress.user_id == user_id,
             UserProgress.updated_at >= recent_date
         )
     ).order_by(UserProgress.updated_at.desc()).limit(20).all()
    
    recent_activity_list = []
    for activity in recent_activity:
        recent_activity_list.append({
            'date': activity.updated_at,
            'status': activity.status,
            'lesson_title': activity.lesson_title,
            'module_name': activity.module_name,
            'technology': activity.technology
        })
    
    return UserProgressStats(
        total_modules=total_modules,
        completed_modules=user_progress_stats.completed_modules,
        in_progress_modules=user_progress_stats.in_progress_modules,
        total_lessons=total_lessons,
        completed_lessons=user_progress_stats.completed_lessons,
        in_progress_lessons=user_progress_stats.in_progress_lessons,
        total_exercises_attempted=total_exercises_attempted,
        total_time_spent=user_progress_stats.total_time_spent,
        total_score=user_progress_stats.total_score,
        completion_percentage=round(completion_percentage, 2),
        modules_by_technology=modules_by_technology,
        recent_activity=recent_activity_list
    )


# Exercise Submission endpoints
@router.post("/exercises/submit", response_model=ExerciseSubmissionResponse, status_code=201)
async def submit_exercise(
    submission_data: ExerciseSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit an exercise solution."""
    # Verify exercise exists
    exercise = db.query(Exercise).filter(Exercise.id == submission_data.exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    # Create submission record
    submission = ExerciseSubmission(
        exercise_id=submission_data.exercise_id,
        user_id=current_user.id,
        submitted_code=submission_data.submitted_code,
        is_correct=False,  # Will be updated by validation service
        score=0,  # Will be updated by validation service
        execution_time=None,  # Will be updated by validation service
        error_message=None  # Will be updated by validation service
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # TODO: Integrate with code execution service for validation
    # For now, return the submission as-is
    
    return submission


@router.get("/users/{user_id}/submissions", response_model=List[ExerciseSubmissionResponse])
async def get_user_submissions(
    user_id: uuid.UUID,
    exercise_id: Optional[uuid.UUID] = Query(None, description="Filter by exercise ID"),
    limit: int = Query(50, ge=1, le=200, description="Number of submissions to return"),
    offset: int = Query(0, ge=0, description="Number of submissions to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user exercise submissions."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(ExerciseSubmission).filter(ExerciseSubmission.user_id == user_id)
    
    if exercise_id:
        query = query.filter(ExerciseSubmission.exercise_id == exercise_id)
    
    submissions = query.order_by(ExerciseSubmission.submitted_at.desc()).offset(offset).limit(limit).all()
    return submissions


# Bookmark endpoints
@router.get("/users/{user_id}/bookmarks", response_model=List[UserBookmarkResponse])
async def get_user_bookmarks(
    user_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=500, description="Number of bookmarks to return"),
    offset: int = Query(0, ge=0, description="Number of bookmarks to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user bookmarks."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    bookmarks = db.query(UserBookmark).options(
        joinedload(UserBookmark.lesson)
    ).filter(UserBookmark.user_id == user_id)\
     .order_by(UserBookmark.created_at.desc())\
     .offset(offset).limit(limit).all()
    
    return bookmarks


@router.post("/bookmarks", response_model=UserBookmarkResponse, status_code=201)
async def create_bookmark(
    bookmark_data: UserBookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a bookmark for a lesson."""
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == bookmark_data.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if bookmark already exists
    existing_bookmark = db.query(UserBookmark).filter(
        and_(
            UserBookmark.user_id == current_user.id,
            UserBookmark.lesson_id == bookmark_data.lesson_id
        )
    ).first()
    
    if existing_bookmark:
        raise HTTPException(status_code=409, detail="Bookmark already exists")
    
    # Create bookmark
    bookmark = UserBookmark(
        user_id=current_user.id,
        lesson_id=bookmark_data.lesson_id
    )
    
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    
    # Load lesson relationship
    db.refresh(bookmark, ['lesson'])
    
    return bookmark


@router.delete("/bookmarks/{bookmark_id}", status_code=204)
async def delete_bookmark(
    bookmark_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a bookmark."""
    bookmark = db.query(UserBookmark).filter(
        and_(
            UserBookmark.id == bookmark_id,
            UserBookmark.user_id == current_user.id
        )
    ).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    db.delete(bookmark)
    db.commit()


@router.delete("/bookmarks/lesson/{lesson_id}", status_code=204)
async def delete_bookmark_by_lesson(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a bookmark by lesson ID."""
    bookmark = db.query(UserBookmark).filter(
        and_(
            UserBookmark.lesson_id == lesson_id,
            UserBookmark.user_id == current_user.id
        )
    ).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    db.delete(bookmark)
    db.commit()