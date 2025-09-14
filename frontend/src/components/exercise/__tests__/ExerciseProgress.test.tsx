import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ExerciseProgress from '../ExerciseProgress';
import { ExerciseValidationResult } from '../../../types/codeEditor';

const mockValidationResult: ExerciseValidationResult = {
  success: true,
  passed_tests: 8,
  total_tests: 10,
  test_results: [
    { name: 'Test 1', passed: true, expected: 'Hello', actual: 'Hello' },
    { name: 'Test 2', passed: false, expected: 'World', actual: 'world' },
  ],
  score: 80,
  feedback: 'Good progress! Most tests are passing.',
};

describe('ExerciseProgress', () => {
  it('renders all progress metrics', () => {
    render(
      <ExerciseProgress
        validationResult={mockValidationResult}
        attempts={3}
        timeSpent={450} // 7:30
        maxPoints={100}
      />
    );

    expect(screen.getByText('Exercise Progress')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument(); // attempts
    expect(screen.getByText('7:30')).toBeInTheDocument(); // time spent
    expect(screen.getByText('8/10')).toBeInTheDocument(); // tests passed
    expect(screen.getByText('80/100')).toBeInTheDocument(); // score
  });

  it('displays correct attempt status messages', () => {
    const { rerender } = render(
      <ExerciseProgress
        validationResult={null}
        attempts={0}
        timeSpent={0}
        maxPoints={100}
      />
    );

    expect(screen.getByText('No attempts yet')).toBeInTheDocument();

    rerender(
      <ExerciseProgress
        validationResult={null}
        attempts={2}
        timeSpent={0}
        maxPoints={100}
      />
    );

    expect(screen.getByText('Great start!')).toBeInTheDocument();

    rerender(
      <ExerciseProgress
        validationResult={null}
        attempts={4}
        timeSpent={0}
        maxPoints={100}
      />
    );

    expect(screen.getByText('Keep trying!')).toBeInTheDocument();

    rerender(
      <ExerciseProgress
        validationResult={null}
        attempts={7}
        timeSpent={0}
        maxPoints={100}
      />
    );

    expect(screen.getByText('Consider reviewing hints')).toBeInTheDocument();
  });

  it('displays correct time status messages', () => {
    const { rerender } = render(
      <ExerciseProgress
        validationResult={null}
        attempts={1}
        timeSpent={200} // 3:20 - under 5 minutes
        maxPoints={100}
      />
    );

    expect(screen.getByText('Quick work!')).toBeInTheDocument();

    rerender(
      <ExerciseProgress
        validationResult={null}
        attempts={1}
        timeSpent={600} // 10:00 - between 5-15 minutes
        maxPoints={100}
      />
    );

    expect(screen.getByText('Good pace')).toBeInTheDocument();

    rerender(
      <ExerciseProgress
        validationResult={null}
        attempts={1}
        timeSpent={1200} // 20:00 - over 15 minutes
        maxPoints={100}
      />
    );

    expect(screen.getByText('Take your time')).toBeInTheDocument();
  });

  it('formats time correctly', () => {
    const { rerender } = render(
      <ExerciseProgress
        validationResult={null}
        attempts={1}
        timeSpent={65} // 1:05
        maxPoints={100}
      />
    );

    expect(screen.getByText('1:05')).toBeInTheDocument();

    rerender(
      <ExerciseProgress
        validationResult={null}
        attempts={1}
        timeSpent={3661} // 61:01
        maxPoints={100}
      />
    );

    expect(screen.getByText('61:01')).toBeInTheDocument();
  });

  it('shows progress bars for tests and score', () => {
    render(
      <ExerciseProgress
        validationResult={mockValidationResult}
        attempts={3}
        timeSpent={450}
        maxPoints={100}
      />
    );

    // Check for progress percentages
    expect(screen.getByText('80% complete')).toBeInTheDocument(); // tests: 8/10 = 80%
    expect(screen.getByText('80% of max score')).toBeInTheDocument(); // score: 80/100 = 80%
  });

  it('displays default values when no validation result', () => {
    render(
      <ExerciseProgress
        validationResult={null}
        attempts={0}
        timeSpent={0}
        maxPoints={100}
      />
    );

    expect(screen.getByText('0/0')).toBeInTheDocument(); // tests
    expect(screen.getByText('0/100')).toBeInTheDocument(); // score
    expect(screen.getByText('Not tested yet')).toBeInTheDocument();
    expect(screen.getByText('No score yet')).toBeInTheDocument();
  });

  it('shows success status when exercise is completed', () => {
    const successResult: ExerciseValidationResult = {
      ...mockValidationResult,
      success: true,
      passed_tests: 10,
      total_tests: 10,
      score: 100,
    };

    render(
      <ExerciseProgress
        validationResult={successResult}
        attempts={2}
        timeSpent={300}
        maxPoints={100}
      />
    );

    expect(screen.getByText('Exercise Completed Successfully!')).toBeInTheDocument();
    expect(screen.getByText(/Congratulations! You've completed this exercise with a score of 100\/100 points/)).toBeInTheDocument();
  });

  it('shows progress status when exercise is not completed', () => {
    const progressResult: ExerciseValidationResult = {
      ...mockValidationResult,
      success: false,
      passed_tests: 6,
      total_tests: 10,
    };

    render(
      <ExerciseProgress
        validationResult={progressResult}
        attempts={3}
        timeSpent={450}
        maxPoints={100}
      />
    );

    expect(screen.getByText('Keep Working on It!')).toBeInTheDocument();
    expect(screen.getByText(/You're making progress! 6 out of 10 tests are passing/)).toBeInTheDocument();
  });

  it('applies correct color classes based on attempt count', () => {
    const { rerender } = render(
      <ExerciseProgress
        validationResult={null}
        attempts={1}
        timeSpent={0}
        maxPoints={100}
      />
    );

    // Check if the attempts number has green color (good attempts)
    let attemptsElement = screen.getByText('1');
    expect(attemptsElement).toHaveClass('text-green-600');

    rerender(
      <ExerciseProgress
        validationResult={null}
        attempts={4}
        timeSpent={0}
        maxPoints={100}
      />
    );

    // Check if the attempts number has yellow color (moderate attempts)
    attemptsElement = screen.getByText('4');
    expect(attemptsElement).toHaveClass('text-yellow-600');

    rerender(
      <ExerciseProgress
        validationResult={null}
        attempts={8}
        timeSpent={0}
        maxPoints={100}
      />
    );

    // Check if the attempts number has red color (many attempts)
    attemptsElement = screen.getByText('8');
    expect(attemptsElement).toHaveClass('text-red-600');
  });

  it('applies correct color classes based on time spent', () => {
    const { rerender } = render(
      <ExerciseProgress
        validationResult={null}
        attempts={1}
        timeSpent={200} // under 5 minutes
        maxPoints={100}
      />
    );

    // Check if the time has green color (quick)
    let timeElement = screen.getByText('3:20');
    expect(timeElement).toHaveClass('text-green-600');

    rerender(
      <ExerciseProgress
        validationResult={null}
        attempts={1}
        timeSpent={600} // 5-15 minutes
        maxPoints={100}
      />
    );

    // Check if the time has yellow color (moderate)
    timeElement = screen.getByText('10:00');
    expect(timeElement).toHaveClass('text-yellow-600');

    rerender(
      <ExerciseProgress
        validationResult={null}
        attempts={1}
        timeSpent={1200} // over 15 minutes
        maxPoints={100}
      />
    );

    // Check if the time has red color (slow)
    timeElement = screen.getByText('20:00');
    expect(timeElement).toHaveClass('text-red-600');
  });

  it('shows green progress bar when all tests pass', () => {
    const perfectResult: ExerciseValidationResult = {
      ...mockValidationResult,
      success: true,
      passed_tests: 10,
      total_tests: 10,
      score: 100,
    };

    render(
      <ExerciseProgress
        validationResult={perfectResult}
        attempts={1}
        timeSpent={300}
        maxPoints={100}
      />
    );

    expect(screen.getByText('100% complete')).toBeInTheDocument();
    expect(screen.getByText('100% of max score')).toBeInTheDocument();
  });
});