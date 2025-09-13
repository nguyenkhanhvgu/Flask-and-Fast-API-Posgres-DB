import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from .test_models_sqlite import (
    User, LearningModule, Lesson, Exercise, UserProgress,
    ExerciseTestCase, ExerciseHint, ExerciseSubmission, UserBookmark
)


class TestUserModel:
    """Test cases for User model."""
    
    def test_create_user(self, db_session):
        """Test creating a user with valid data."""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_unique_email(self, db_session):
        """Test that email must be unique."""
        user1 = User(email="test@example.com", username="user1", password_hash="hash1")
        user2 = User(email="test@example.com", username="user2", password_hash="hash2")
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_unique_username(self, db_session):
        """Test that username must be unique."""
        user1 = User(email="test1@example.com", username="testuser", password_hash="hash1")
        user2 = User(email="test2@example.com", username="testuser", password_hash="hash2")
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestLearningModuleModel:
    """Test cases for LearningModule model."""
    
    def test_create_learning_module(self, db_session):
        """Test creating a learning module with valid data."""
        module = LearningModule(
            name="Flask Basics",
            description="Introduction to Flask web framework",
            technology="flask",
            difficulty_level="beginner",
            order_index=1,
            estimated_duration=120
        )
        db_session.add(module)
        db_session.commit()
        
        assert module.id is not None
        assert module.name == "Flask Basics"
        assert module.technology == "flask"
        assert module.difficulty_level == "beginner"
        assert module.order_index == 1
        assert module.estimated_duration == 120
        assert module.created_at is not None
    
    def test_learning_module_relationships(self, db_session):
        """Test relationships between learning module and lessons."""
        module = LearningModule(
            name="Flask Basics",
            technology="flask",
            difficulty_level="beginner",
            order_index=1
        )
        db_session.add(module)
        db_session.commit()
        
        lesson = Lesson(
            module_id=module.id,
            title="Introduction to Flask",
            content="Flask is a web framework...",
            order_index=1
        )
        db_session.add(lesson)
        db_session.commit()
        
        assert len(module.lessons) == 1
        assert module.lessons[0].title == "Introduction to Flask"
        assert lesson.module == module


class TestLessonModel:
    """Test cases for Lesson model."""
    
    def test_create_lesson(self, db_session):
        """Test creating a lesson with valid data."""
        module = LearningModule(
            name="Flask Basics",
            technology="flask",
            difficulty_level="beginner",
            order_index=1
        )
        db_session.add(module)
        db_session.commit()
        
        lesson = Lesson(
            module_id=module.id,
            title="Flask Routing",
            content="Learn about Flask routing...",
            order_index=1,
            estimated_duration=30
        )
        db_session.add(lesson)
        db_session.commit()
        
        assert lesson.id is not None
        assert lesson.title == "Flask Routing"
        assert lesson.content == "Learn about Flask routing..."
        assert lesson.order_index == 1
        assert lesson.estimated_duration == 30
        assert lesson.module_id == module.id
    
    def test_lesson_cascade_delete(self, db_session):
        """Test that lessons are deleted when module is deleted."""
        module = LearningModule(
            name="Flask Basics",
            technology="flask",
            difficulty_level="beginner",
            order_index=1
        )
        db_session.add(module)
        db_session.commit()
        
        lesson = Lesson(
            module_id=module.id,
            title="Flask Routing",
            content="Learn about Flask routing...",
            order_index=1
        )
        db_session.add(lesson)
        db_session.commit()
        
        lesson_id = lesson.id
        db_session.delete(module)
        db_session.commit()
        
        # Lesson should be deleted due to cascade
        deleted_lesson = db_session.query(Lesson).filter(Lesson.id == lesson_id).first()
        assert deleted_lesson is None


class TestExerciseModel:
    """Test cases for Exercise model."""
    
    def test_create_exercise(self, db_session):
        """Test creating an exercise with valid data."""
        module = LearningModule(
            name="Flask Basics",
            technology="flask",
            difficulty_level="beginner",
            order_index=1
        )
        db_session.add(module)
        db_session.commit()
        
        lesson = Lesson(
            module_id=module.id,
            title="Flask Routing",
            content="Learn about Flask routing...",
            order_index=1
        )
        db_session.add(lesson)
        db_session.commit()
        
        exercise = Exercise(
            lesson_id=lesson.id,
            title="Create a Flask Route",
            description="Create a simple Flask route that returns 'Hello World'",
            exercise_type="coding",
            starter_code="from flask import Flask\napp = Flask(__name__)",
            solution_code="from flask import Flask\napp = Flask(__name__)\n@app.route('/')\ndef hello():\n    return 'Hello World'",
            points=10,
            order_index=1,
            difficulty="easy"
        )
        db_session.add(exercise)
        db_session.commit()
        
        assert exercise.id is not None
        assert exercise.title == "Create a Flask Route"
        assert exercise.exercise_type == "coding"
        assert exercise.points == 10
        assert exercise.difficulty == "easy"
        assert exercise.lesson_id == lesson.id


class TestUserProgressModel:
    """Test cases for UserProgress model."""
    
    def test_create_user_progress(self, db_session):
        """Test creating user progress with valid data."""
        user = User(email="test@example.com", username="testuser", password_hash="hash")
        module = LearningModule(
            name="Flask Basics",
            technology="flask",
            difficulty_level="beginner",
            order_index=1
        )
        db_session.add_all([user, module])
        db_session.commit()
        
        lesson = Lesson(
            module_id=module.id,
            title="Flask Routing",
            content="Learn about Flask routing...",
            order_index=1
        )
        db_session.add(lesson)
        db_session.commit()
        
        progress = UserProgress(
            user_id=user.id,
            lesson_id=lesson.id,
            status="completed",
            completion_date=datetime.utcnow(),
            time_spent=1800,  # 30 minutes
            score=85,
            attempts=2
        )
        db_session.add(progress)
        db_session.commit()
        
        assert progress.id is not None
        assert progress.status == "completed"
        assert progress.time_spent == 1800
        assert progress.score == 85
        assert progress.attempts == 2
        assert progress.user_id == user.id
        assert progress.lesson_id == lesson.id
    
    def test_user_progress_unique_constraint(self, db_session):
        """Test that user can only have one progress record per lesson."""
        user = User(email="test@example.com", username="testuser", password_hash="hash")
        module = LearningModule(
            name="Flask Basics",
            technology="flask",
            difficulty_level="beginner",
            order_index=1
        )
        db_session.add_all([user, module])
        db_session.commit()
        
        lesson = Lesson(
            module_id=module.id,
            title="Flask Routing",
            content="Learn about Flask routing...",
            order_index=1
        )
        db_session.add(lesson)
        db_session.commit()
        
        progress1 = UserProgress(user_id=user.id, lesson_id=lesson.id, status="in_progress")
        progress2 = UserProgress(user_id=user.id, lesson_id=lesson.id, status="completed")
        
        db_session.add(progress1)
        db_session.commit()
        
        db_session.add(progress2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestExerciseTestCaseModel:
    """Test cases for ExerciseTestCase model."""
    
    def test_create_test_case(self, db_session):
        """Test creating an exercise test case."""
        module = LearningModule(
            name="Flask Basics",
            technology="flask",
            difficulty_level="beginner",
            order_index=1
        )
        db_session.add(module)
        db_session.commit()
        
        lesson = Lesson(
            module_id=module.id,
            title="Flask Routing",
            content="Learn about Flask routing...",
            order_index=1
        )
        db_session.add(lesson)
        db_session.commit()
        
        exercise = Exercise(
            lesson_id=lesson.id,
            title="Create a Flask Route",
            description="Create a simple Flask route",
            exercise_type="coding",
            order_index=1
        )
        db_session.add(exercise)
        db_session.commit()
        
        test_case = ExerciseTestCase(
            exercise_id=exercise.id,
            input_data="GET /",
            expected_output="Hello World",
            is_hidden=False,
            order_index=1
        )
        db_session.add(test_case)
        db_session.commit()
        
        assert test_case.id is not None
        assert test_case.input_data == "GET /"
        assert test_case.expected_output == "Hello World"
        assert test_case.is_hidden is False
        assert test_case.order_index == 1
        assert test_case.exercise_id == exercise.id


class TestUserBookmarkModel:
    """Test cases for UserBookmark model."""
    
    def test_create_bookmark(self, db_session):
        """Test creating a user bookmark."""
        user = User(email="test@example.com", username="testuser", password_hash="hash")
        module = LearningModule(
            name="Flask Basics",
            technology="flask",
            difficulty_level="beginner",
            order_index=1
        )
        db_session.add_all([user, module])
        db_session.commit()
        
        lesson = Lesson(
            module_id=module.id,
            title="Flask Routing",
            content="Learn about Flask routing...",
            order_index=1
        )
        db_session.add(lesson)
        db_session.commit()
        
        bookmark = UserBookmark(
            user_id=user.id,
            lesson_id=lesson.id
        )
        db_session.add(bookmark)
        db_session.commit()
        
        assert bookmark.id is not None
        assert bookmark.user_id == user.id
        assert bookmark.lesson_id == lesson.id
        assert bookmark.created_at is not None
    
    def test_bookmark_unique_constraint(self, db_session):
        """Test that user can only bookmark a lesson once."""
        user = User(email="test@example.com", username="testuser", password_hash="hash")
        module = LearningModule(
            name="Flask Basics",
            technology="flask",
            difficulty_level="beginner",
            order_index=1
        )
        db_session.add_all([user, module])
        db_session.commit()
        
        lesson = Lesson(
            module_id=module.id,
            title="Flask Routing",
            content="Learn about Flask routing...",
            order_index=1
        )
        db_session.add(lesson)
        db_session.commit()
        
        bookmark1 = UserBookmark(user_id=user.id, lesson_id=lesson.id)
        bookmark2 = UserBookmark(user_id=user.id, lesson_id=lesson.id)
        
        db_session.add(bookmark1)
        db_session.commit()
        
        db_session.add(bookmark2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestModelRelationships:
    """Test complex model relationships and cascades."""
    
    def test_complete_data_hierarchy(self, db_session):
        """Test creating a complete data hierarchy with all relationships."""
        # Create user
        user = User(email="test@example.com", username="testuser", password_hash="hash")
        
        # Create module
        module = LearningModule(
            name="Flask Basics",
            technology="flask",
            difficulty_level="beginner",
            order_index=1
        )
        
        db_session.add_all([user, module])
        db_session.commit()
        
        # Create lesson
        lesson = Lesson(
            module_id=module.id,
            title="Flask Routing",
            content="Learn about Flask routing...",
            order_index=1
        )
        
        db_session.add(lesson)
        db_session.commit()
        
        # Create exercise
        exercise = Exercise(
            lesson_id=lesson.id,
            title="Create a Flask Route",
            description="Create a simple Flask route",
            exercise_type="coding",
            order_index=1
        )
        
        db_session.add(exercise)
        db_session.commit()
        
        # Create related data
        progress = UserProgress(user_id=user.id, lesson_id=lesson.id, status="in_progress")
        bookmark = UserBookmark(user_id=user.id, lesson_id=lesson.id)
        test_case = ExerciseTestCase(
            exercise_id=exercise.id,
            expected_output="Hello World",
            order_index=1
        )
        hint = ExerciseHint(
            exercise_id=exercise.id,
            hint_text="Use @app.route decorator",
            order_index=1
        )
        submission = ExerciseSubmission(
            exercise_id=exercise.id,
            user_id=user.id,
            submitted_code="@app.route('/')\ndef hello():\n    return 'Hello World'",
            is_correct=True,
            score=100
        )
        
        db_session.add_all([progress, bookmark, test_case, hint, submission])
        db_session.commit()
        
        # Verify relationships
        assert len(user.progress) == 1
        assert len(user.bookmarks) == 1
        assert len(module.lessons) == 1
        assert len(lesson.exercises) == 1
        assert len(exercise.test_cases) == 1
        assert len(exercise.hints) == 1
        assert len(exercise.submissions) == 1
        
        # Test cascade deletes
        db_session.delete(module)
        db_session.commit()
        
        # All related data should be deleted
        assert db_session.query(Lesson).count() == 0
        assert db_session.query(Exercise).count() == 0
        assert db_session.query(ExerciseTestCase).count() == 0
        assert db_session.query(ExerciseHint).count() == 0
        assert db_session.query(UserProgress).count() == 0
        assert db_session.query(UserBookmark).count() == 0
        
        # User and submissions should still exist (no cascade from module)
        assert db_session.query(User).count() == 1
        # Note: ExerciseSubmission should be deleted due to exercise cascade