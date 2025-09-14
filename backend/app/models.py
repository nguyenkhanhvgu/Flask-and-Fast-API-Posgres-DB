from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, Index, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .database import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value


class User(Base):
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("UserBookmark", back_populates="user", cascade="all, delete-orphan")


class LearningModule(Base):
    __tablename__ = "learning_modules"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    technology = Column(String(50), nullable=False, index=True)
    difficulty_level = Column(String(20), nullable=False, index=True)
    order_index = Column(Integer, nullable=False)
    estimated_duration = Column(Integer)  # in minutes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.order_index")
    
    # Indexes
    __table_args__ = (
        Index('idx_module_tech_difficulty', 'technology', 'difficulty_level'),
        Index('idx_module_order', 'order_index'),
    )


class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    module_id = Column(GUID(), ForeignKey("learning_modules.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False)
    estimated_duration = Column(Integer)  # in minutes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    module = relationship("LearningModule", back_populates="lessons")
    exercises = relationship("Exercise", back_populates="lesson", cascade="all, delete-orphan", order_by="Exercise.order_index")
    progress = relationship("UserProgress", back_populates="lesson", cascade="all, delete-orphan")
    bookmarks = relationship("UserBookmark", back_populates="lesson", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_lesson_module_order', 'module_id', 'order_index'),
    )


class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(GUID(), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    exercise_type = Column(String(50), nullable=False, index=True)
    starter_code = Column(Text)
    solution_code = Column(Text)
    points = Column(Integer, default=0)
    order_index = Column(Integer, nullable=False)
    difficulty = Column(String(20), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    lesson = relationship("Lesson", back_populates="exercises")
    test_cases = relationship("ExerciseTestCase", back_populates="exercise", cascade="all, delete-orphan")
    hints = relationship("ExerciseHint", back_populates="exercise", cascade="all, delete-orphan", order_by="ExerciseHint.order_index")
    submissions = relationship("ExerciseSubmission", back_populates="exercise", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_exercise_lesson_order', 'lesson_id', 'order_index'),
        Index('idx_exercise_type_difficulty', 'exercise_type', 'difficulty'),
    )


class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(GUID(), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="not_started", index=True)
    completion_date = Column(DateTime(timezone=True))
    time_spent = Column(Integer, default=0)  # in seconds
    score = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('user_id', 'lesson_id', name='uq_user_lesson_progress'),
        Index('idx_progress_user_status', 'user_id', 'status'),
        Index('idx_progress_completion', 'completion_date'),
    )


class ExerciseTestCase(Base):
    __tablename__ = "exercise_test_cases"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    exercise_id = Column(GUID(), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    input_data = Column(Text)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False)
    order_index = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    exercise = relationship("Exercise", back_populates="test_cases")
    
    # Indexes
    __table_args__ = (
        Index('idx_testcase_exercise_order', 'exercise_id', 'order_index'),
    )


class ExerciseHint(Base):
    __tablename__ = "exercise_hints"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    exercise_id = Column(GUID(), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    hint_text = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    exercise = relationship("Exercise", back_populates="hints")
    
    # Indexes
    __table_args__ = (
        Index('idx_hint_exercise_order', 'exercise_id', 'order_index'),
    )


class ExerciseSubmission(Base):
    __tablename__ = "exercise_submissions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    exercise_id = Column(GUID(), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    submitted_code = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    score = Column(Integer, default=0)
    execution_time = Column(Integer)  # in milliseconds
    error_message = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    exercise = relationship("Exercise", back_populates="submissions")
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_submission_user_exercise', 'user_id', 'exercise_id'),
        Index('idx_submission_date', 'submitted_at'),
    )


class UserBookmark(Base):
    __tablename__ = "user_bookmarks"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(GUID(), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="bookmarks")
    lesson = relationship("Lesson", back_populates="bookmarks")
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('user_id', 'lesson_id', name='uq_user_lesson_bookmark'),
        Index('idx_bookmark_user', 'user_id'),
    )