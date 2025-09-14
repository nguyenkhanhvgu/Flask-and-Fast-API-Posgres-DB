"""
Content management API endpoints for learning modules, lessons, and exercises.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, func
from typing import List, Optional
import uuid

from ..database import get_db
from ..models import LearningModule, Lesson, Exercise
from ..schemas import (
    LearningModuleCreate, LearningModuleUpdate, LearningModuleResponse, LearningModuleDetailResponse,
    LessonCreate, LessonUpdate, LessonResponse, LessonDetailResponse,
    ExerciseCreate, ExerciseUpdate, ExerciseResponse,
    ContentSearchParams
)
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["content"])


# Learning Module endpoints
@router.get("/modules", response_model=List[LearningModuleResponse])
async def get_modules(
    technology: Optional[str] = Query(None, description="Filter by technology"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    limit: int = Query(20, ge=1, le=100, description="Number of modules to return"),
    offset: int = Query(0, ge=0, description="Number of modules to skip"),
    db: Session = Depends(get_db)
):
    """Get all learning modules with optional filtering."""
    query = db.query(LearningModule)
    
    # Apply filters
    if technology:
        query = query.filter(LearningModule.technology == technology)
    if difficulty_level:
        query = query.filter(LearningModule.difficulty_level == difficulty_level)
    
    # Order by order_index and apply pagination
    modules = query.order_by(LearningModule.order_index).offset(offset).limit(limit).all()
    return modules


@router.get("/modules/{module_id}", response_model=LearningModuleDetailResponse)
async def get_module(module_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a specific learning module with its lessons."""
    module = db.query(LearningModule).options(
        selectinload(LearningModule.lessons)
    ).filter(LearningModule.id == module_id).first()
    
    if not module:
        raise HTTPException(status_code=404, detail="Learning module not found")
    
    return module


@router.post("/modules", response_model=LearningModuleResponse, status_code=201)
async def create_module(
    module_data: LearningModuleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new learning module."""
    # Check if order_index is already taken
    existing_module = db.query(LearningModule).filter(
        and_(
            LearningModule.technology == module_data.technology,
            LearningModule.order_index == module_data.order_index
        )
    ).first()
    
    if existing_module:
        raise HTTPException(
            status_code=409, 
            detail=f"Module with order_index {module_data.order_index} already exists for {module_data.technology}"
        )
    
    module = LearningModule(**module_data.model_dump())
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


@router.put("/modules/{module_id}", response_model=LearningModuleResponse)
async def update_module(
    module_id: uuid.UUID,
    module_data: LearningModuleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a learning module."""
    module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Learning module not found")
    
    # Check for order_index conflicts if updating
    if module_data.order_index is not None and module_data.order_index != module.order_index:
        technology = module_data.technology or module.technology
        existing_module = db.query(LearningModule).filter(
            and_(
                LearningModule.id != module_id,
                LearningModule.technology == technology,
                LearningModule.order_index == module_data.order_index
            )
        ).first()
        
        if existing_module:
            raise HTTPException(
                status_code=409,
                detail=f"Module with order_index {module_data.order_index} already exists for {technology}"
            )
    
    # Update fields
    update_data = module_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(module, field, value)
    
    db.commit()
    db.refresh(module)
    return module


@router.delete("/modules/{module_id}", status_code=204)
async def delete_module(
    module_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a learning module."""
    module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Learning module not found")
    
    db.delete(module)
    db.commit()


# Lesson endpoints
@router.get("/lessons", response_model=List[LessonResponse])
async def get_lessons(
    module_id: Optional[uuid.UUID] = Query(None, description="Filter by module ID"),
    limit: int = Query(20, ge=1, le=100, description="Number of lessons to return"),
    offset: int = Query(0, ge=0, description="Number of lessons to skip"),
    db: Session = Depends(get_db)
):
    """Get all lessons with optional filtering."""
    query = db.query(Lesson)
    
    if module_id:
        query = query.filter(Lesson.module_id == module_id)
    
    lessons = query.order_by(Lesson.order_index).offset(offset).limit(limit).all()
    return lessons


@router.get("/lessons/{lesson_id}", response_model=LessonDetailResponse)
async def get_lesson(lesson_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a specific lesson with its exercises."""
    lesson = db.query(Lesson).options(
        selectinload(Lesson.exercises)
    ).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    return lesson


@router.post("/lessons", response_model=LessonResponse, status_code=201)
async def create_lesson(
    lesson_data: LessonCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new lesson."""
    # Verify module exists
    module = db.query(LearningModule).filter(LearningModule.id == lesson_data.module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Learning module not found")
    
    # Check if order_index is already taken within the module
    existing_lesson = db.query(Lesson).filter(
        and_(
            Lesson.module_id == lesson_data.module_id,
            Lesson.order_index == lesson_data.order_index
        )
    ).first()
    
    if existing_lesson:
        raise HTTPException(
            status_code=409,
            detail=f"Lesson with order_index {lesson_data.order_index} already exists in this module"
        )
    
    lesson = Lesson(**lesson_data.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.put("/lessons/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: uuid.UUID,
    lesson_data: LessonUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a lesson."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check for order_index conflicts if updating
    if lesson_data.order_index is not None and lesson_data.order_index != lesson.order_index:
        existing_lesson = db.query(Lesson).filter(
            and_(
                Lesson.id != lesson_id,
                Lesson.module_id == lesson.module_id,
                Lesson.order_index == lesson_data.order_index
            )
        ).first()
        
        if existing_lesson:
            raise HTTPException(
                status_code=409,
                detail=f"Lesson with order_index {lesson_data.order_index} already exists in this module"
            )
    
    # Update fields
    update_data = lesson_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lesson, field, value)
    
    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete("/lessons/{lesson_id}", status_code=204)
async def delete_lesson(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a lesson."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    db.delete(lesson)
    db.commit()


# Exercise endpoints
@router.get("/exercises", response_model=List[ExerciseResponse])
async def get_exercises(
    lesson_id: Optional[uuid.UUID] = Query(None, description="Filter by lesson ID"),
    exercise_type: Optional[str] = Query(None, description="Filter by exercise type"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    limit: int = Query(20, ge=1, le=100, description="Number of exercises to return"),
    offset: int = Query(0, ge=0, description="Number of exercises to skip"),
    db: Session = Depends(get_db)
):
    """Get all exercises with optional filtering."""
    query = db.query(Exercise)
    
    if lesson_id:
        query = query.filter(Exercise.lesson_id == lesson_id)
    if exercise_type:
        query = query.filter(Exercise.exercise_type == exercise_type)
    if difficulty:
        query = query.filter(Exercise.difficulty == difficulty)
    
    exercises = query.order_by(Exercise.order_index).offset(offset).limit(limit).all()
    return exercises


@router.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(exercise_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a specific exercise."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    return exercise


@router.post("/exercises", response_model=ExerciseResponse, status_code=201)
async def create_exercise(
    exercise_data: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new exercise."""
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == exercise_data.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if order_index is already taken within the lesson
    existing_exercise = db.query(Exercise).filter(
        and_(
            Exercise.lesson_id == exercise_data.lesson_id,
            Exercise.order_index == exercise_data.order_index
        )
    ).first()
    
    if existing_exercise:
        raise HTTPException(
            status_code=409,
            detail=f"Exercise with order_index {exercise_data.order_index} already exists in this lesson"
        )
    
    exercise = Exercise(**exercise_data.model_dump())
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.put("/exercises/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: uuid.UUID,
    exercise_data: ExerciseUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an exercise."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    # Check for order_index conflicts if updating
    if exercise_data.order_index is not None and exercise_data.order_index != exercise.order_index:
        existing_exercise = db.query(Exercise).filter(
            and_(
                Exercise.id != exercise_id,
                Exercise.lesson_id == exercise.lesson_id,
                Exercise.order_index == exercise_data.order_index
            )
        ).first()
        
        if existing_exercise:
            raise HTTPException(
                status_code=409,
                detail=f"Exercise with order_index {exercise_data.order_index} already exists in this lesson"
            )
    
    # Update fields
    update_data = exercise_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exercise, field, value)
    
    db.commit()
    db.refresh(exercise)
    return exercise


@router.delete("/exercises/{exercise_id}", status_code=204)
async def delete_exercise(
    exercise_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete an exercise."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    db.delete(exercise)
    db.commit()





# Content statistics endpoint
@router.get("/content/stats")
async def get_content_stats(db: Session = Depends(get_db)):
    """Get content statistics."""
    stats = {
        "total_modules": db.query(func.count(LearningModule.id)).scalar(),
        "total_lessons": db.query(func.count(Lesson.id)).scalar(),
        "total_exercises": db.query(func.count(Exercise.id)).scalar(),
        "modules_by_technology": {},
        "modules_by_difficulty": {}
    }
    
    # Get modules by technology
    tech_stats = db.query(
        LearningModule.technology,
        func.count(LearningModule.id)
    ).group_by(LearningModule.technology).all()
    
    stats["modules_by_technology"] = {tech: count for tech, count in tech_stats}
    
    # Get modules by difficulty
    diff_stats = db.query(
        LearningModule.difficulty_level,
        func.count(LearningModule.id)
    ).group_by(LearningModule.difficulty_level).all()
    
    stats["modules_by_difficulty"] = {diff: count for diff, count in diff_stats}
    
    return stats