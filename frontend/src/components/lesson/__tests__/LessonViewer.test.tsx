import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import LessonViewer from '../LessonViewer';
import { apiClient } from '../../../services/api';

// Mock the API client
vi.mock('../../../services/api', () => ({
  apiClient: {
    getLesson: vi.fn(),
    markLessonComplete: vi.fn(),
  },
}));

// Mock the contexts
vi.mock('../../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'user-1', email: 'test@example.com', username: 'testuser' },
    isAuthenticated: true,
  }),
}));

vi.mock('../../../contexts/ProgressContext', () => ({
  useProgress: () => ({
    updateLessonProgress: vi.fn(),
    getUserProgress: vi.fn().mockReturnValue({
      id: 'progress-1',
      user_id: 'user-1',
      lesson_id: 'lesson-1',
      status: 'in_progress',
      time_spent: 300,
      score: 0,
      attempts: 1,
    }),
  }),
}));

// Mock react-markdown
vi.mock('react-markdown', () => ({
  default: ({ children }: { children: string }) => <div data-testid="markdown-content">{children}</div>,
}));

// Mock the child components
vi.mock('../LessonNavigation', () => ({
  default: ({ onLessonChange }: { onLessonChange: (id: string) => void }) => (
    <div data-testid="lesson-navigation">
      <button onClick={() => onLessonChange('next-lesson')}>Next Lesson</button>
    </div>
  ),
}));

vi.mock('../ProgressTracker', () => ({
  default: ({ onComplete }: { onComplete: () => void }) => (
    <div data-testid="progress-tracker">
      <button onClick={onComplete} data-testid="mark-complete-btn">Mark Complete</button>
    </div>
  ),
}));

const mockLesson = {
  id: 'lesson-1',
  module_id: 'module-1',
  title: 'Introduction to Flask',
  content: '# Flask Basics\n\nThis is a lesson about Flask.\n\n```python\nfrom flask import Flask\napp = Flask(__name__)\n```',
  order_index: 1,
  learning_objectives: ['Understand Flask basics', 'Create a simple Flask app'],
  prerequisites: [],
  exercises: [
    {
      id: 'exercise-1',
      lesson_id: 'lesson-1',
      title: 'Create a Flask App',
      description: 'Create your first Flask application',
      exercise_type: 'coding' as const,
      starter_code: 'from flask import Flask',
      solution_code: 'from flask import Flask\napp = Flask(__name__)',
      hints: ['Import Flask', 'Create app instance'],
      difficulty: 'beginner',
      points: 10,
    },
  ],
  estimated_duration: 30,
};

const renderLessonViewer = (props = {}) => {
  const defaultProps = {
    lessonId: 'lesson-1',
    moduleId: 'module-1',
    ...props,
  };

  return render(<LessonViewer {...defaultProps} />);
};

describe('LessonViewer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (apiClient.getLesson as any).mockResolvedValue(mockLesson);
    (apiClient.markLessonComplete as any).mockResolvedValue({});
  });

  it('renders loading state initially', () => {
    const { container } = renderLessonViewer();
    
    // Look for loading spinner or loading text
    const loadingElement = container.querySelector('.animate-spin') || 
                          screen.queryByText(/loading/i);
    expect(loadingElement).toBeTruthy();
  });

  it('renders lesson content after loading', async () => {
    renderLessonViewer();

    await waitFor(() => {
      expect(screen.getByText('Introduction to Flask')).toBeInTheDocument();
    });

    expect(screen.getByTestId('markdown-content')).toBeInTheDocument();
    expect(screen.getByTestId('progress-tracker')).toBeInTheDocument();
    expect(screen.getByTestId('lesson-navigation')).toBeInTheDocument();
  });

  it('displays learning objectives when available', async () => {
    renderLessonViewer();

    await waitFor(() => {
      expect(screen.getByText('Learning Objectives')).toBeInTheDocument();
    });

    expect(screen.getByText('Understand Flask basics')).toBeInTheDocument();
    expect(screen.getByText('Create a simple Flask app')).toBeInTheDocument();
  });

  it('displays exercises section when exercises exist', async () => {
    renderLessonViewer();

    await waitFor(() => {
      expect(screen.getByText('Exercises')).toBeInTheDocument();
    });

    expect(screen.getByText('Create a Flask App')).toBeInTheDocument();
    expect(screen.getByText('Create your first Flask application')).toBeInTheDocument();
    expect(screen.getByText('beginner • 10 points')).toBeInTheDocument();
  });

  it('handles lesson completion', async () => {
    renderLessonViewer();

    await waitFor(() => {
      expect(screen.getByTestId('mark-complete-btn')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('mark-complete-btn'));

    await waitFor(() => {
      expect(apiClient.markLessonComplete).toHaveBeenCalledWith('lesson-1');
    });
  });

  it('handles API errors gracefully', async () => {
    (apiClient.getLesson as any).mockRejectedValue(new Error('API Error'));
    
    renderLessonViewer();

    await waitFor(() => {
      expect(screen.getByText('Failed to load lesson content')).toBeInTheDocument();
    });

    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('displays retry button and allows retrying after error', async () => {
    (apiClient.getLesson as any).mockRejectedValueOnce(new Error('API Error'));
    
    renderLessonViewer();

    await waitFor(() => {
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });

    // Mock successful retry
    (apiClient.getLesson as any).mockResolvedValue(mockLesson);
    
    fireEvent.click(screen.getByText('Retry'));

    await waitFor(() => {
      expect(screen.getByText('Introduction to Flask')).toBeInTheDocument();
    });
  });

  it('handles lesson not found', async () => {
    (apiClient.getLesson as any).mockResolvedValue(null);
    
    renderLessonViewer();

    await waitFor(() => {
      expect(screen.getByText('Lesson not found')).toBeInTheDocument();
    });
  });

  it('handles navigation to different lesson', async () => {
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
    
    renderLessonViewer();

    await waitFor(() => {
      expect(screen.getByText('Next Lesson')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Next Lesson'));

    expect(consoleSpy).toHaveBeenCalledWith('Navigate to lesson:', 'next-lesson');
    
    consoleSpy.mockRestore();
  });

  it('renders without learning objectives when not provided', async () => {
    const lessonWithoutObjectives = {
      ...mockLesson,
      learning_objectives: [],
    };
    
    (apiClient.getLesson as any).mockResolvedValue(lessonWithoutObjectives);
    
    renderLessonViewer();

    await waitFor(() => {
      expect(screen.getByText('Introduction to Flask')).toBeInTheDocument();
    });

    expect(screen.queryByText('Learning Objectives')).not.toBeInTheDocument();
  });

  it('renders without exercises when not provided', async () => {
    const lessonWithoutExercises = {
      ...mockLesson,
      exercises: [],
    };
    
    (apiClient.getLesson as any).mockResolvedValue(lessonWithoutExercises);
    
    renderLessonViewer();

    await waitFor(() => {
      expect(screen.getByText('Introduction to Flask')).toBeInTheDocument();
    });

    expect(screen.queryByText('Exercises')).not.toBeInTheDocument();
  });
});