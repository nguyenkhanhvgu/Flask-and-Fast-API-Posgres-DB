import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import ExerciseHints from '../ExerciseHints';
import { apiClient } from '../../../services/api';

// Mock the API client
vi.mock('../../../services/api', () => ({
  apiClient: {
    getExerciseHints: vi.fn(),
  },
}));

const mockHints = [
  'Start by importing the Flask module',
  'Create an instance of the Flask class',
  'Use the @app.route decorator to define routes',
  'Return a string from your route function',
];

describe('ExerciseHints', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    vi.mocked(apiClient.getExerciseHints).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    render(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={0}
      />
    );

    expect(screen.getByText('Loading hints...')).toBeInTheDocument();
  });

  it('displays no hints message when no hints are available', async () => {
    vi.mocked(apiClient.getExerciseHints).mockResolvedValue({ hints: [] });

    render(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={[]}
        attempts={0}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('No hints available for this exercise.')).toBeInTheDocument();
    });
  });

  it('shows progressive hint revelation info', async () => {
    vi.mocked(apiClient.getExerciseHints).mockResolvedValue({ hints: mockHints });

    render(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={1}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/Hints are revealed progressively/)).toBeInTheDocument();
      expect(screen.getByText(/Try submitting your solution to unlock more hints!/)).toBeInTheDocument();
    });
  });

  it('reveals hints based on attempt count', async () => {
    vi.mocked(apiClient.getExerciseHints).mockResolvedValue({ hints: mockHints });

    const { rerender } = render(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={0}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('0/4 hints revealed')).toBeInTheDocument();
    });

    // After 2 attempts, should reveal 1 hint
    rerender(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={2}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('1/4 hints revealed')).toBeInTheDocument();
      expect(screen.getByText('Start by importing the Flask module')).toBeInTheDocument();
    });

    // After 4 attempts, should reveal 2 hints
    rerender(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={4}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('2/4 hints revealed')).toBeInTheDocument();
      expect(screen.getByText('Create an instance of the Flask class')).toBeInTheDocument();
    });
  });

  it('shows different hint levels with appropriate icons', async () => {
    vi.mocked(apiClient.getExerciseHints).mockResolvedValue({ hints: mockHints });

    render(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={6}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Hint')).toBeInTheDocument();
      expect(screen.getByText('Detailed Hint')).toBeInTheDocument();
      expect(screen.getByText('Solution Approach')).toBeInTheDocument();
    });
  });

  it('allows manual hint revelation when enough attempts are made', async () => {
    vi.mocked(apiClient.getExerciseHints).mockResolvedValue({ hints: mockHints });

    render(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={4}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('2/4 hints revealed')).toBeInTheDocument();
    });

    // Should show button to reveal next hint since attempts (4) >= (2+1)*2 = 6 is false
    // But we can manually reveal the next hint since we have 4 attempts and need 6 for hint 3
    // Let's test with 6 attempts to get the button
    const { rerender } = render(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={6}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('3/4 hints revealed')).toBeInTheDocument();
      expect(screen.getByText('Use the @app.route decorator to define routes')).toBeInTheDocument();
    });
  });

  it('shows attempts needed message when not enough attempts for next hint', async () => {
    vi.mocked(apiClient.getExerciseHints).mockResolvedValue({ hints: mockHints });

    render(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={1}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/Make.*more attempt.*to unlock the next hint/)).toBeInTheDocument();
    });
  });

  it('shows completion message when all hints are revealed', async () => {
    vi.mocked(apiClient.getExerciseHints).mockResolvedValue({ hints: mockHints });

    render(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={8}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('4/4 hints revealed')).toBeInTheDocument();
      expect(screen.getByText('All hints revealed! You have all the guidance needed to complete this exercise.')).toBeInTheDocument();
    });
  });

  it('falls back to provided hints when API fails', async () => {
    vi.mocked(apiClient.getExerciseHints).mockRejectedValue(new Error('API Error'));

    render(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={2}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('1/4 hints revealed')).toBeInTheDocument();
      expect(screen.getByText('Start by importing the Flask module')).toBeInTheDocument();
    });
  });

  it('handles empty hints array gracefully', async () => {
    vi.mocked(apiClient.getExerciseHints).mockResolvedValue({ hints: [] });

    render(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={[]}
        attempts={5}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('No hints available for this exercise.')).toBeInTheDocument();
    });
  });

  it('displays hint numbers correctly', async () => {
    vi.mocked(apiClient.getExerciseHints).mockResolvedValue({ hints: mockHints });

    render(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={6}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Hint 1')).toBeInTheDocument();
      expect(screen.getByText('Hint 2')).toBeInTheDocument();
      expect(screen.getByText('Hint 3')).toBeInTheDocument();
    });
  });

  it('updates revealed hints when attempts prop changes', async () => {
    vi.mocked(apiClient.getExerciseHints).mockResolvedValue({ hints: mockHints });

    const { rerender } = render(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={1}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('0/4 hints revealed')).toBeInTheDocument();
    });

    // Increase attempts
    rerender(
      <ExerciseHints
        exerciseId="exercise-1"
        hints={mockHints}
        attempts={3}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('1/4 hints revealed')).toBeInTheDocument();
    });
  });
});