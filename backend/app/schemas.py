"""
Pydantic schemas for API request/response models.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response (without password)."""
    id: uuid.UUID
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class TokenData(BaseModel):
    """Schema for token data."""
    user_id: Optional[str] = None


# Content Management Schemas

class LearningModuleBase(BaseModel):
    """Base learning module schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    technology: str = Field(..., min_length=1, max_length=50)
    difficulty_level: str = Field(..., pattern="^(beginner|intermediate|advanced)$")
    order_index: int = Field(..., ge=0)
    estimated_duration: Optional[int] = Field(None, ge=0)


class LearningModuleCreate(LearningModuleBase):
    """Schema for creating a learning module."""
    pass


class LearningModuleUpdate(BaseModel):
    """Schema for updating a learning module."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    technology: Optional[str] = Field(None, min_length=1, max_length=50)
    difficulty_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    order_index: Optional[int] = Field(None, ge=0)
    estimated_duration: Optional[int] = Field(None, ge=0)


class LearningModuleResponse(LearningModuleBase):
    """Schema for learning module response."""
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class LessonBase(BaseModel):
    """Base lesson schema."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    order_index: int = Field(..., ge=0)
    estimated_duration: Optional[int] = Field(None, ge=0)


class LessonCreate(LessonBase):
    """Schema for creating a lesson."""
    module_id: uuid.UUID


class LessonUpdate(BaseModel):
    """Schema for updating a lesson."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    order_index: Optional[int] = Field(None, ge=0)
    estimated_duration: Optional[int] = Field(None, ge=0)


class LessonResponse(LessonBase):
    """Schema for lesson response."""
    id: uuid.UUID
    module_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ExerciseBase(BaseModel):
    """Base exercise schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    exercise_type: str = Field(..., min_length=1, max_length=50)
    starter_code: Optional[str] = None
    solution_code: Optional[str] = None
    points: int = Field(default=0, ge=0)
    order_index: int = Field(..., ge=0)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")


class ExerciseCreate(ExerciseBase):
    """Schema for creating an exercise."""
    lesson_id: uuid.UUID


class ExerciseUpdate(BaseModel):
    """Schema for updating an exercise."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    exercise_type: Optional[str] = Field(None, min_length=1, max_length=50)
    starter_code: Optional[str] = None
    solution_code: Optional[str] = None
    points: Optional[int] = Field(None, ge=0)
    order_index: Optional[int] = Field(None, ge=0)
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")


class ExerciseResponse(ExerciseBase):
    """Schema for exercise response."""
    id: uuid.UUID
    lesson_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Detailed response schemas with relationships
class LearningModuleDetailResponse(LearningModuleResponse):
    """Detailed learning module response with lessons."""
    lessons: list[LessonResponse] = []


class LessonDetailResponse(LessonResponse):
    """Detailed lesson response with exercises."""
    exercises: list[ExerciseResponse] = []


# Search and filter schemas
class ContentSearchParams(BaseModel):
    """Schema for content search parameters."""
    query: Optional[str] = Field(None, min_length=1, max_length=255)
    technology: Optional[str] = Field(None, min_length=1, max_length=50)
    difficulty_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    exercise_type: Optional[str] = Field(None, min_length=1, max_length=50)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Progress tracking schemas
class UserProgressBase(BaseModel):
    """Base user progress schema."""
    status: str = Field(..., pattern="^(not_started|in_progress|completed)$")
    time_spent: int = Field(default=0, ge=0)
    score: int = Field(default=0, ge=0)
    attempts: int = Field(default=0, ge=0)


class UserProgressCreate(BaseModel):
    """Schema for creating user progress."""
    lesson_id: uuid.UUID
    status: str = Field(..., pattern="^(not_started|in_progress|completed)$")
    time_spent: int = Field(default=0, ge=0)
    score: int = Field(default=0, ge=0)


class UserProgressUpdate(BaseModel):
    """Schema for updating user progress."""
    status: Optional[str] = Field(None, pattern="^(not_started|in_progress|completed)$")
    time_spent: Optional[int] = Field(None, ge=0)
    score: Optional[int] = Field(None, ge=0)
    attempts: Optional[int] = Field(None, ge=0)


class UserProgressResponse(UserProgressBase):
    """Schema for user progress response."""
    id: uuid.UUID
    user_id: uuid.UUID
    lesson_id: uuid.UUID
    completion_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LessonProgressResponse(BaseModel):
    """Schema for lesson progress with lesson details."""
    lesson: LessonResponse
    progress: Optional[UserProgressResponse] = None

    class Config:
        from_attributes = True


class ModuleProgressResponse(BaseModel):
    """Schema for module progress with statistics."""
    module: LearningModuleResponse
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
    completion_percentage: float
    total_time_spent: int
    total_score: int

    class Config:
        from_attributes = True


class UserProgressStats(BaseModel):
    """Schema for user progress statistics."""
    total_modules: int
    completed_modules: int
    in_progress_modules: int
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
    total_exercises_attempted: int
    total_time_spent: int
    total_score: int
    completion_percentage: float
    modules_by_technology: dict[str, dict[str, int]]
    recent_activity: list[dict]


class ExerciseSubmissionCreate(BaseModel):
    """Schema for creating exercise submission."""
    exercise_id: uuid.UUID
    submitted_code: str = Field(..., min_length=1)


class ExerciseSubmissionResponse(BaseModel):
    """Schema for exercise submission response."""
    id: uuid.UUID
    exercise_id: uuid.UUID
    user_id: uuid.UUID
    submitted_code: str
    is_correct: bool
    score: int
    execution_time: Optional[int] = None
    error_message: Optional[str] = None
    submitted_at: datetime

    class Config:
        from_attributes = True


# Bookmark schemas
class UserBookmarkCreate(BaseModel):
    """Schema for creating user bookmark."""
    lesson_id: uuid.UUID


class UserBookmarkResponse(BaseModel):
    """Schema for user bookmark response."""
    id: uuid.UUID
    user_id: uuid.UUID
    lesson_id: uuid.UUID
    created_at: datetime
    lesson: LessonResponse

    class Config:
        from_attributes = True