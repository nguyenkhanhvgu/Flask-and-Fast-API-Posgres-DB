import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import ExerciseManager from '../ExerciseManager';
import { Exercise } from '../../../types/progress';
import { ExerciseValidationResult } from '../../../types/codeEditor';
import { AuthContext, useAuth } from '../../../contexts/AuthContext';
import { ProgressContext, useProgress } from '../../../contexts/ProgressContext';

// Mock the hooks
vi.mock('../../../contexts/AuthContext', () => ({
  AuthContext: { Provider: ({ children, value }: any) => children },
  useAuth: vi.fn(),
}));

vi.mock('../../../contexts/ProgressContext', () => ({
  ProgressContext: { Provider: ({ children, value }: any) => children },
  useProgress: vi.fn(),
}));
import { apiClient } from '../../../services/api';

// Mock the API client
vi.mock('../../../services/api', () => ({
  apiClient: {
    getUserProgress: vi.fn(),
  },
}));

// Mock the ExerciseDisplay component
vi.mock('../ExerciseDisplay', () => ({
  default: ({ exercise, onComplete, onClose }: any) => (
    <div data-testid="exercise-display">
      <h2>{exercise.title}</h2>
      <button onClick={() => onComplete?.({ success: true, score: exercise.points })}>
        Complete Exercise
      </button>
      <button onClick={onClose}>Close</button>
    </div>
  ),
}));

const mockExercises: Exercise[] = [
  {
    id: 'exercise-1',
    lesson_id: 'lesson-1',
    title: 'Flask Basics',
    description: 'Learn Flask fundamentals',
    exercise_type: 'coding',
    starter_code: 'from flask import Flask',
    hints: ['Import Flask', 'Create app instance'],
    difficulty: 'easy',
    points: 10,
  },
  {
    id: 'exercise-2',
    lesson_id: 'lesson-1',
    title: 'Flask Routing',
    description: 'Create routes in Flask',
    exercise_type: 'coding',
    starter_code: '@app.route("/")',
    hints: ['Use @app.route decorator'],
    difficulty: 'medium',
    points: 15,
  },
  {
    id: 'exercise-3',
    lesson_id: 'lesson-1',
    title: 'Flask Templates',
    description: 'Work with Flask templates',
    exercise_type: 'coding',
    starter_code: 'render_template',
    hints: ['Import render_template'],
    difficulty: 'hard',
    points: 20,
  },
];

const mockUser = {
  id: 'user-1',
  email: 'test@example.com',
  username: 'testuser',
};

const mockAuthContext = {
  user: mockUser,
  login: vi.fn(),
  logout: vi.fn(),
  register: vi.fn(),
  isLoading: false,
};

const mockProgressContext = {
  state: {
    modules: [],
    userProgress: {},
    bookmarks: [],
    isLoading: false,
  },
  loadUserProgress: vi.fn(),
  markLessonComplete: vi.fn(),
  submitExercise: vi.fn(),
  getUserProgress: vi.fn(),
  addBookmark: vi.fn(),
  removeBookmark: vi.fn(),
  updateLessonProgress: vi.fn(),
};

const renderExerciseManager = (props: Partial<React.ComponentProps<typeof ExerciseManager>> = {}) => {
  // Mock the hooks to return our mock data
  vi.mocked(useAuth).mockReturnValue(mockAuthContext);
  vi.mocked(useProgress).mockReturnValue(mockProgressContext);
  
  return render(
    <ExerciseManager
      lessonId="lesson-1"
      exercises={mockExercises}
      {...props}
    />
  );
};

describe('ExerciseManager', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(apiClient.getUserProgress).mockResolvedValue([]);
  });

  it('renders exercise list with correct information', async () => {
    renderExerciseManager();

    await waitFor(() => {
      expect(screen.getByText('Exercises')).toBeInTheDocument();
    });

    expect(screen.getByText('Flask Basics')).toBeInTheDocument();
    expect(screen.getByText('Flask Routing')).toBeInTheDocument();
    expect(screen.getByText('Flask Templates')).toBeInTheDocument();

    expect(screen.getByText('Learn Flask fundamentals')).toBeInTheDocument();
    expect(screen.getByText('10 points')).toBeInTheDocument();
    expect(screen.getByText('15 points')).toBeInTheDocument();
    expect(screen.getByText('20 points')).toBeInTheDocument();
  });

  it('displays progress summary correctly', async () => {
    renderExerciseManager();

    await waitFor(() => {
      expect(screen.getByText('0%')).toBeInTheDocument(); // completion rate
      expect(screen.getByText('0/3 exercises')).toBeInTheDocument();
      expect(screen.getByText('out of 45 points')).toBeInTheDocument(); // total possible points
    });
  });

  it('shows difficulty badges with correct colors', async () => {
    renderExerciseManager();

    await waitFor(() => {
      const easyBadge = screen.getByText('easy');
      const mediumBadge = screen.getByText('medium');
      const hardBadge = screen.getByText('hard');

      expect(easyBadge).toHaveClass('bg-green-100', 'text-green-800');
      expect(mediumBadge).toHaveClass('bg-yellow-100', 'text-yellow-800');
      expect(hardBadge).toHaveClass('bg-red-100', 'text-red-800');
    });
  });

  it('opens exercise display when exercise is selected', async () => {
    renderExerciseManager();

    await waitFor(() => {
      const startButton = screen.getAllByText('Start Exercise')[0];
      fireEvent.click(startButton);
    });

    expect(screen.getByTestId('exercise-display')).toBeInTheDocument();
    expect(screen.getByText('Flask Basics')).toBeInTheDocument();
  });

  it('closes exercise display when close button is clicked', async () => {
    renderExerciseManager();

    await waitFor(() => {
      const startButton = screen.getAllByText('Start Exercise')[0];
      fireEvent.click(startButton);
    });

    const closeButton = screen.getByText('Close');
    fireEvent.click(closeButton);

    expect(screen.queryByTestId('exercise-display')).not.toBeInTheDocument();
    expect(screen.getByText('Exercises')).toBeInTheDocument();
  });

  it('updates progress when exercise is completed', async () => {
    const onExerciseComplete = vi.fn();
    renderExerciseManager({ onExerciseComplete });

    await waitFor(() => {
      const startButton = screen.getAllByText('Start Exercise')[0];
      fireEvent.click(startButton);
    });

    const completeButton = screen.getByText('Complete Exercise');
    fireEvent.click(completeButton);

    expect(onExerciseComplete).toHaveBeenCalledWith('exercise-1', {
      success: true,
      score: 10,
    });
  });

  it('loads and displays completed exercises', async () => {
    const mockProgress = [
      {
        exercise_id: 'exercise-1',
        status: 'completed',
        score: 8,
      },
      {
        exercise_id: 'exercise-2',
        status: 'completed',
        score: 12,
      },
    ];

    vi.mocked(apiClient.getUserProgress).mockResolvedValue(mockProgress);

    renderExerciseManager();

    await waitFor(() => {
      expect(screen.getByText('67%')).toBeInTheDocument(); // 2/3 = 67%
      expect(screen.getByText('2/3 exercises')).toBeInTheDocument();
      expect(screen.getByText('Completed (8 pts)')).toBeInTheDocument();
      expect(screen.getByText('Completed (12 pts)')).toBeInTheDocument();
    });

    // Check that completed exercises show "Review" button
    const reviewButtons = screen.getAllByText('Review');
    expect(reviewButtons).toHaveLength(2);
  });

  it('calculates average score correctly', async () => {
    const mockProgress = [
      {
        exercise_id: 'exercise-1',
        status: 'completed',
        score: 8,
      },
      {
        exercise_id: 'exercise-2',
        status: 'completed',
        score: 12,
      },
    ];

    vi.mocked(apiClient.getUserProgress).mockResolvedValue(mockProgress);

    renderExerciseManager();

    await waitFor(() => {
      expect(screen.getByText('10')).toBeInTheDocument(); // (8 + 12) / 2 = 10
      expect(screen.getByText('points per exercise')).toBeInTheDocument();
    });
  });

  it('shows loading state while fetching progress', () => {
    vi.mocked(apiClient.getUserProgress).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    renderExerciseManager();

    expect(screen.getByText('Loading exercises...')).toBeInTheDocument();
  });

  it('displays empty state when no exercises are provided', async () => {
    renderExerciseManager({ exercises: [] });

    await waitFor(() => {
      expect(screen.getByText('No Exercises Available')).toBeInTheDocument();
      expect(screen.getByText('There are no exercises for this lesson yet. Check back later!')).toBeInTheDocument();
    });
  });

  it('shows correct completion icons', async () => {
    const mockProgress = [
      {
        exercise_id: 'exercise-1',
        status: 'completed',
        score: 10,
      },
    ];

    vi.mocked(apiClient.getUserProgress).mockResolvedValue(mockProgress);

    renderExerciseManager();

    await waitFor(() => {
      // First exercise should have a checkmark (completed)
      const completedIcon = screen.getAllByRole('img', { hidden: true })[0];
      expect(completedIcon).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    vi.mocked(apiClient.getUserProgress).mockRejectedValue(new Error('API Error'));

    renderExerciseManager();

    // Should still render the exercise list even if progress loading fails
    await waitFor(() => {
      expect(screen.getByText('Flask Basics')).toBeInTheDocument();
      expect(screen.getByText('0%')).toBeInTheDocument(); // fallback to 0% completion
    });
  });

  it('filters progress for current lesson exercises only', async () => {
    const mockProgress = [
      {
        exercise_id: 'exercise-1',
        status: 'completed',
        score: 10,
      },
      {
        exercise_id: 'other-exercise',
        status: 'completed',
        score: 5,
      },
    ];

    vi.mocked(apiClient.getUserProgress).mockResolvedValue(mockProgress);

    renderExerciseManager();

    await waitFor(() => {
      // Should only count exercise-1 (which is in mockExercises)
      expect(screen.getByText('33%')).toBeInTheDocument(); // 1/3 = 33%
      expect(screen.getByText('1/3 exercises')).toBeInTheDocument();
      expect(screen.getByText('10')).toBeInTheDocument(); // total score should be 10, not 15
    });
  });

  it('updates local state when exercise is completed', async () => {
    renderExerciseManager();

    await waitFor(() => {
      const startButton = screen.getAllByText('Start Exercise')[0];
      fireEvent.click(startButton);
    });

    const completeButton = screen.getByText('Complete Exercise');
    fireEvent.click(completeButton);

    // Should update the UI to show completion
    await waitFor(() => {
      expect(screen.getByText('33%')).toBeInTheDocument(); // 1/3 completed
      expect(screen.getByText('1/3 exercises')).toBeInTheDocument();
    });
  });
});