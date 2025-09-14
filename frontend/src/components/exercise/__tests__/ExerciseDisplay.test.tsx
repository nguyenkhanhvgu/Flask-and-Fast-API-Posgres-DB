import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import ExerciseDisplay from '../ExerciseDisplay';
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
    validateExercise: vi.fn(),
    getExerciseHints: vi.fn(),
  },
}));

// Mock the CodeEditor component
vi.mock('../../codeEditor', () => ({
  CodeEditor: ({ onCodeChange, initialCode }: any) => (
    <textarea
      data-testid="code-editor"
      defaultValue={initialCode}
      onChange={(e) => onCodeChange?.(e.target.value)}
    />
  ),
}));

const mockExercise: Exercise = {
  id: 'exercise-1',
  lesson_id: 'lesson-1',
  title: 'Create a Flask App',
  description: 'Create your first Flask application with routing',
  exercise_type: 'coding',
  starter_code: 'from flask import Flask\n\n# Your code here',
  solution_code: 'from flask import Flask\napp = Flask(__name__)\n\n@app.route("/")\ndef hello():\n    return "Hello, World!"',
  hints: ['Import Flask', 'Create an app instance', 'Add a route decorator'],
  difficulty: 'easy',
  points: 10,
};

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

const renderExerciseDisplay = (props: Partial<React.ComponentProps<typeof ExerciseDisplay>> = {}) => {
  // Mock the hooks to return our mock data
  vi.mocked(useAuth).mockReturnValue(mockAuthContext);
  vi.mocked(useProgress).mockReturnValue(mockProgressContext);
  
  return render(
    <ExerciseDisplay
      exercise={mockExercise}
      {...props}
    />
  );
};

describe('ExerciseDisplay', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders exercise information correctly', () => {
    renderExerciseDisplay();

    expect(screen.getByText('Create a Flask App')).toBeInTheDocument();
    expect(screen.getByText('Create your first Flask application with routing')).toBeInTheDocument();
    expect(screen.getByText('easy')).toBeInTheDocument();
    expect(screen.getByText('10 points')).toBeInTheDocument();
  });

  it('displays starter code in the editor', () => {
    renderExerciseDisplay();

    const codeEditor = screen.getByTestId('code-editor');
    expect(codeEditor).toHaveValue('from flask import Flask\n\n# Your code here');
  });

  it('shows and hides hints when button is clicked', async () => {
    renderExerciseDisplay();

    const hintsButton = screen.getByText('Show Hints');
    fireEvent.click(hintsButton);

    await waitFor(() => {
      expect(screen.getByText('Hide Hints')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Hide Hints'));

    await waitFor(() => {
      expect(screen.getByText('Show Hints')).toBeInTheDocument();
    });
  });

  it('resets code when reset button is clicked', () => {
    renderExerciseDisplay();

    const codeEditor = screen.getByTestId('code-editor');
    fireEvent.change(codeEditor, { target: { value: 'modified code' } });

    const resetButton = screen.getByText('Reset Code');
    fireEvent.click(resetButton);

    expect(codeEditor).toHaveValue('from flask import Flask\n\n# Your code here');
  });

  it('submits exercise and shows validation results', async () => {
    const mockValidationResult: ExerciseValidationResult = {
      success: true,
      passed_tests: 3,
      total_tests: 3,
      test_results: [
        { name: 'Test 1', passed: true, expected: 'Hello, World!', actual: 'Hello, World!' },
        { name: 'Test 2', passed: true, expected: 200, actual: 200 },
        { name: 'Test 3', passed: true, expected: true, actual: true },
      ],
      score: 10,
      feedback: 'Excellent work! All tests passed.',
    };

    vi.mocked(apiClient.validateExercise).mockResolvedValue(mockValidationResult);

    const onComplete = vi.fn();
    renderExerciseDisplay({ onComplete });

    const codeEditor = screen.getByTestId('code-editor');
    fireEvent.change(codeEditor, { target: { value: 'from flask import Flask\napp = Flask(__name__)' } });

    const submitButton = screen.getByText('Submit Solution');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Exercise Completed!')).toBeInTheDocument();
    });

    expect(screen.getByText('Excellent work! All tests passed.')).toBeInTheDocument();
    expect(screen.getByText('Tests passed: 3/3')).toBeInTheDocument();
    expect(screen.getByText('Score: 10/10')).toBeInTheDocument();
    expect(onComplete).toHaveBeenCalledWith(mockValidationResult);
  });

  it('shows failed validation results', async () => {
    const mockValidationResult: ExerciseValidationResult = {
      success: false,
      passed_tests: 1,
      total_tests: 3,
      test_results: [
        { name: 'Test 1', passed: true, expected: 'Hello, World!', actual: 'Hello, World!' },
        { name: 'Test 2', passed: false, expected: 200, actual: 404, error: 'Route not found' },
        { name: 'Test 3', passed: false, expected: true, actual: false },
      ],
      score: 3,
      feedback: 'Some tests failed. Check your route definition.',
    };

    vi.mocked(apiClient.validateExercise).mockResolvedValue(mockValidationResult);

    renderExerciseDisplay();

    const codeEditor = screen.getByTestId('code-editor');
    fireEvent.change(codeEditor, { target: { value: 'incomplete code' } });

    const submitButton = screen.getByText('Submit Solution');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Tests Failed')).toBeInTheDocument();
    });

    expect(screen.getByText('Some tests failed. Check your route definition.')).toBeInTheDocument();
    expect(screen.getByText('Tests passed: 1/3')).toBeInTheDocument();
    expect(screen.getByText('Score: 3/10')).toBeInTheDocument();
  });

  it('disables submit button when no code is entered', () => {
    renderExerciseDisplay();

    const codeEditor = screen.getByTestId('code-editor');
    fireEvent.change(codeEditor, { target: { value: '' } });

    const submitButton = screen.getByText('Submit Solution');
    expect(submitButton).toBeDisabled();
  });

  it('shows loading state during submission', async () => {
    vi.mocked(apiClient.validateExercise).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    renderExerciseDisplay();

    const codeEditor = screen.getByTestId('code-editor');
    fireEvent.change(codeEditor, { target: { value: 'some code' } });

    const submitButton = screen.getByText('Submit Solution');
    fireEvent.click(submitButton);

    expect(screen.getByText('Validating...')).toBeInTheDocument();
  });

  it('tracks time spent on exercise', async () => {
    vi.useFakeTimers();
    renderExerciseDisplay();

    // Fast-forward time by 65 seconds
    vi.advanceTimersByTime(65000);

    await waitFor(() => {
      expect(screen.getByText(/Time: 1:05/)).toBeInTheDocument();
    });

    vi.useRealTimers();
  });

  it('tracks attempt count', async () => {
    const mockValidationResult: ExerciseValidationResult = {
      success: false,
      passed_tests: 0,
      total_tests: 3,
      test_results: [],
      score: 0,
      feedback: 'Try again.',
    };

    vi.mocked(apiClient.validateExercise).mockResolvedValue(mockValidationResult);

    renderExerciseDisplay();

    const codeEditor = screen.getByTestId('code-editor');
    fireEvent.change(codeEditor, { target: { value: 'attempt 1' } });

    const submitButton = screen.getByText('Submit Solution');
    
    // First attempt
    fireEvent.click(submitButton);
    await waitFor(() => {
      expect(screen.getByText(/Attempts: 1/)).toBeInTheDocument();
    });

    // Second attempt
    fireEvent.change(codeEditor, { target: { value: 'attempt 2' } });
    fireEvent.click(submitButton);
    await waitFor(() => {
      expect(screen.getByText(/Attempts: 2/)).toBeInTheDocument();
    });
  });

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn();
    renderExerciseDisplay({ onClose });

    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalled();
  });

  it('handles API errors gracefully', async () => {
    vi.mocked(apiClient.validateExercise).mockRejectedValue(new Error('API Error'));

    renderExerciseDisplay();

    const codeEditor = screen.getByTestId('code-editor');
    fireEvent.change(codeEditor, { target: { value: 'some code' } });

    const submitButton = screen.getByText('Submit Solution');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Failed to validate exercise. Please try again.')).toBeInTheDocument();
    });
  });
});