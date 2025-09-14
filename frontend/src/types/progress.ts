export interface LearningModule {
  id: string;
  name: string;
  description: string;
  technology: 'flask' | 'fastapi' | 'postgresql';
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  order_index: number;
  estimated_duration: number;
  lessons: Lesson[];
}

export interface Lesson {
  id: string;
  module_id: string;
  title: string;
  content: string;
  order_index: number;
  learning_objectives: string[];
  prerequisites: string[];
  exercises: Exercise[];
  estimated_duration: number;
}

export interface Exercise {
  id: string;
  lesson_id: string;
  title: string;
  description: string;
  exercise_type: 'coding' | 'multiple_choice' | 'fill_blank';
  starter_code?: string;
  solution_code?: string;
  hints: string[];
  difficulty: string;
  points: number;
}

export interface UserProgress {
  id: string;
  user_id: string;
  lesson_id: string;
  status: 'not_started' | 'in_progress' | 'completed';
  completion_date?: string;
  time_spent: number;
  score: number;
  attempts: number;
}

export interface ProgressState {
  modules: LearningModule[];
  userProgress: Record<string, UserProgress>;
  bookmarks: string[];
  isLoading: boolean;
}