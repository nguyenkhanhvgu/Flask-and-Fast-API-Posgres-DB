#!/usr/bin/env python3
"""
Script to verify that the database models and migration work correctly.
This script creates the tables and inserts some sample data.
"""

from app.database import engine, SessionLocal
from app.models import Base, User, LearningModule, Lesson, Exercise, UserProgress
from datetime import datetime

def main():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Create a session
    db = SessionLocal()
    
    try:
        print("\nInserting sample data...")
        
        # Create a user
        user = User(
            email="demo@example.com",
            username="demouser",
            password_hash="hashed_password_here"
        )
        db.add(user)
        db.commit()
        print(f"Created user: {user.username} (ID: {user.id})")
        
        # Create a learning module
        module = LearningModule(
            name="Flask Fundamentals",
            description="Learn the basics of Flask web framework",
            technology="flask",
            difficulty_level="beginner",
            order_index=1,
            estimated_duration=120
        )
        db.add(module)
        db.commit()
        print(f"Created module: {module.name} (ID: {module.id})")
        
        # Create a lesson
        lesson = Lesson(
            module_id=module.id,
            title="Introduction to Flask",
            content="Flask is a lightweight web framework for Python...",
            order_index=1,
            estimated_duration=30
        )
        db.add(lesson)
        db.commit()
        print(f"Created lesson: {lesson.title} (ID: {lesson.id})")
        
        # Create an exercise
        exercise = Exercise(
            lesson_id=lesson.id,
            title="Create Your First Flask App",
            description="Create a simple 'Hello World' Flask application",
            exercise_type="coding",
            starter_code="from flask import Flask\n\napp = Flask(__name__)\n\n# Your code here",
            solution_code="from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Hello World!'\n\nif __name__ == '__main__':\n    app.run()",
            points=10,
            order_index=1,
            difficulty="easy"
        )
        db.add(exercise)
        db.commit()
        print(f"Created exercise: {exercise.title} (ID: {exercise.id})")
        
        # Create user progress
        progress = UserProgress(
            user_id=user.id,
            lesson_id=lesson.id,
            status="completed",
            completion_date=datetime.utcnow(),
            time_spent=1800,  # 30 minutes
            score=85,
            attempts=1
        )
        db.add(progress)
        db.commit()
        print(f"Created progress record for user {user.username}")
        
        print("\n✅ All sample data inserted successfully!")
        print("\nDatabase schema verification complete!")
        
        # Query and display the data
        print("\n--- Sample Data ---")
        print(f"User: {user.username} ({user.email})")
        print(f"Module: {module.name} - {module.technology} ({module.difficulty_level})")
        print(f"Lesson: {lesson.title}")
        print(f"Exercise: {exercise.title} ({exercise.points} points)")
        print(f"Progress: {progress.status} - Score: {progress.score}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()