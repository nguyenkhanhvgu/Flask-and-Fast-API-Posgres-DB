import { LearningModule, UserProgress } from '../types/progress';

export const mockModules: LearningModule[] = [
  {
    id: 'module-1',
    name: 'Flask Basics',
    description: 'Learn the fundamentals of Flask web framework',
    technology: 'flask',
    difficulty_level: 'beginner',
    order_index: 1,
    estimated_duration: 120,
    lessons: [
      {
        id: 'lesson-1',
        module_id: 'module-1',
        title: 'Introduction to Flask',
        content: 'Flask basics content',
        order_index: 1,
        learning_objectives: ['Understand Flask basics'],
        prerequisites: [],
        exercises: [
          {
            id: 'exercise-1',
            lesson_id: 'lesson-1',
            title: 'Hello World Flask App',
            description: 'Create your first Flask application',
            exercise_type: 'coding',
            starter_code: 'from flask import Flask',
            solution_code: 'from flask import Flask\napp = Flask(__name__)',
            hints: ['Import Flask', 'Create app instance'],
            difficulty: 'easy',
            points: 10
          }
        ],
        estimated_duration: 30
      },
      {
        id: 'lesson-2',
        module_id: 'module-1',
        title: 'Flask Routing',
        content: 'Flask routing content',
        order_index: 2,
        learning_objectives: ['Understand routing'],
        prerequisites: ['lesson-1'],
        exercises: [],
        estimated_duration: 45
      }
    ]
  },
  {
    id: 'module-2',
    name: 'FastAPI Basics',
    description: 'Learn the fundamentals of FastAPI',
    technology: 'fastapi',
    difficulty_level: 'intermediate',
    order_index: 2,
    estimated_duration: 180,
    lessons: [
      {
        id: 'lesson-3',
        module_id: 'module-2',
        title: 'Introduction to FastAPI',
        content: 'FastAPI basics content',
        order_index: 1,
        learning_objectives: ['Understand FastAPI basics'],
        prerequisites: [],
        exercises: [],
        estimated_duration: 60
      }
    ]
  },
  {
    id: 'module-3',
    name: 'PostgreSQL Basics',
    description: 'Learn database fundamentals with PostgreSQL',
    technology: 'postgresql',
    difficulty_level: 'beginner',
    order_index: 3,
    estimated_duration: 240,
    lessons: [
      {
        id: 'lesson-4',
        module_id: 'module-3',
        title: 'SQL Fundamentals',
        content: 'SQL basics content',
        order_index: 1,
        learning_objectives: ['Understand SQL'],
        prerequisites: [],
        exercises: [],
        estimated_duration: 90
      }
    ]
  }
];

export const mockUserProgress: Record<string, UserProgress> = {
  'lesson-1': {
    id: 'progress-1',
    user_id: 'user-1',
    lesson_id: 'lesson-1',
    status: 'completed',
    completion_date: '2024-01-15T10:30:00Z',
    time_spent: 1800, // 30 minutes
    score: 85,
    attempts: 2
  },
  'lesson-2': {
    id: 'progress-2',
    user_id: 'user-1',
    lesson_id: 'lesson-2',
    status: 'in_progress',
    completion_date: undefined,
    time_spent: 900, // 15 minutes
    score: 0,
    attempts: 1
  }
};

export const mockBookmarks = ['lesson-1', 'lesson-4'];

export const mockUser = {
  id: 'user-1',
  username: 'testuser',
  email: 'test@example.com'
};