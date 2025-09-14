import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import ProgressTracker from '../ProgressTracker';
import { Lesson, UserProgress } from '../../../types/progress';

const mockLesson: Lesson = {
  id: 'lesson-1',
  module_id: 'module-1',
  title: 'Introduction to Flask',
  content: 'Flask content',
  order_index: 1,
  learning_objectives: [],
  prerequisites: [],
  exercises: [],
  estimated_duration: 30,
};

const mockProgressNotStarted: UserProgress = {
  id: 'progress-1',
  user_id: 'user-1',
  lesson_id: 'lesson-1',
  status: 'not_started',
  time_spent: 0,
  score: 0,
  attempts: 0,
};

const mockProgressInProgress: UserProgress = {
  id: 'progress-1',
  user_id: 'user-1',
  lesson_id: 'lesson-1',
  status: 'in_progress',
  time_spent: 300,
  score: 75,
  attempts: 2,
};

const mockProgressCompleted: UserProgress = {
  id: 'progress-1',
  user_id: 'user-1',
  lesson_id: 'lesson-1',
  status: 'completed',
  completion_date: '2023-12-01T10:00:00Z',
  time_spent: 600,
  score: 95,
  attempts: 3,
};

const renderProgressTracker = (props = {}) => {
  const defaultProps = {
    lesson: mockLesson,
    userProgress: mockProgressInProgress,
    timeSpent: 120,
    onComplete: vi.fn(),
    ...props,
  };

  return render(<ProgressTracker {...defaultProps} />);
};

describe('ProgressTracker', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders progress information correctly', () => {
    renderProgressTracker();

    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('Time: 2:00')).toBeInTheDocument();
    expect(screen.getByText('Est. 30 min')).toBeInTheDocument();
    expect(screen.getByText('Score: 75%')).toBeInTheDocument();
  });

  it('displays not started status correctly', () => {
    renderProgressTracker({ userProgress: mockProgressNotStarted, timeSpent: 0 });

    expect(screen.getByText('Not Started')).toBeInTheDocument();
    expect(screen.getByText('0%')).toBeInTheDocument();
    expect(screen.getByText('Mark Complete')).toBeInTheDocument();
  });

  it('displays completed status correctly', () => {
    renderProgressTracker({ userProgress: mockProgressCompleted });

    expect(screen.getAllByText('Completed')).toHaveLength(2); // Status badge and button
    expect(screen.getByText('Completed on 12/1/2023')).toBeInTheDocument();
    // The 100% is shown as a checkmark for completed lessons, not as text
    expect(screen.queryByText('100%')).not.toBeInTheDocument();
  });

  it('formats time correctly', () => {
    renderProgressTracker({ timeSpent: 65 });

    expect(screen.getByText('Time: 1:05')).toBeInTheDocument();
  });

  it('formats time with leading zeros', () => {
    renderProgressTracker({ timeSpent: 5 });

    expect(screen.getByText('Time: 0:05')).toBeInTheDocument();
  });

  it('handles mark complete action', async () => {
    const onComplete = vi.fn();
    renderProgressTracker({ onComplete });

    const markCompleteButton = screen.getByText('Mark Complete');
    fireEvent.click(markCompleteButton);

    expect(onComplete).toHaveBeenCalledTimes(1);
  });

  it('shows loading state during completion', async () => {
    const onComplete = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    renderProgressTracker({ onComplete });

    const markCompleteButton = screen.getByText('Mark Complete');
    fireEvent.click(markCompleteButton);

    expect(screen.getByText('Completing...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /completing/i })).toBeDisabled();

    await waitFor(() => {
      expect(screen.queryByText('Completing...')).not.toBeInTheDocument();
    });
  });

  it('handles completion error gracefully', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const onComplete = vi.fn().mockRejectedValue(new Error('Completion failed'));
    
    renderProgressTracker({ onComplete });

    const markCompleteButton = screen.getByText('Mark Complete');
    fireEvent.click(markCompleteButton);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Error marking lesson complete:', expect.any(Error));
    });

    // Button should be enabled again after error
    expect(screen.getByText('Mark Complete')).not.toBeDisabled();
    
    consoleSpy.mockRestore();
  });

  it('displays progress circle with correct percentage', () => {
    renderProgressTracker({ userProgress: mockProgressInProgress });

    // Check that the progress circle shows 50% for in_progress
    expect(screen.getByText('50%')).toBeInTheDocument();
  });

  it('displays completed progress circle with checkmark', () => {
    const { container } = renderProgressTracker({ userProgress: mockProgressCompleted });

    // Should show checkmark instead of percentage
    const checkmark = container.querySelector('svg path[fill-rule="evenodd"]');
    expect(checkmark).toBeInTheDocument();
  });

  it('displays additional stats when available', () => {
    renderProgressTracker({ userProgress: mockProgressInProgress });

    expect(screen.getByText('Attempts: 2')).toBeInTheDocument();
    expect(screen.getByText('Total time: 5:00')).toBeInTheDocument();
  });

  it('handles null user progress', () => {
    renderProgressTracker({ userProgress: null });

    expect(screen.getByText('Not Started')).toBeInTheDocument();
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('does not show score when score is 0', () => {
    const progressWithoutScore = { ...mockProgressInProgress, score: 0 };
    renderProgressTracker({ userProgress: progressWithoutScore });

    expect(screen.queryByText(/Score:/)).not.toBeInTheDocument();
  });

  it('does not show attempts when attempts is 0', () => {
    const progressWithoutAttempts = { ...mockProgressInProgress, attempts: 0 };
    renderProgressTracker({ userProgress: progressWithoutAttempts });

    expect(screen.queryByText(/Attempts:/)).not.toBeInTheDocument();
  });

  it('shows correct progress bar width', () => {
    const { container } = renderProgressTracker({ userProgress: mockProgressInProgress });

    const progressBar = container.querySelector('.h-2.rounded-full.transition-all');
    expect(progressBar).toHaveStyle({ width: '50%' });
  });

  it('shows green progress bar for completed lessons', () => {
    const { container } = renderProgressTracker({ userProgress: mockProgressCompleted });

    const progressBar = container.querySelector('.bg-green-500');
    expect(progressBar).toBeInTheDocument();
  });

  it('shows blue progress bar for in-progress lessons', () => {
    const { container } = renderProgressTracker({ userProgress: mockProgressInProgress });

    const progressBar = container.querySelector('.bg-blue-500');
    expect(progressBar).toBeInTheDocument();
  });

  it('handles lesson without estimated duration', () => {
    const lessonWithoutDuration = { ...mockLesson, estimated_duration: undefined };
    renderProgressTracker({ lesson: lessonWithoutDuration });

    expect(screen.queryByText(/Est\./)).not.toBeInTheDocument();
  });
});