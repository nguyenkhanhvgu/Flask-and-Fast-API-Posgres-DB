import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ValidationResults from '../ValidationResults';
import { ExerciseValidationResult } from '../../../types/codeEditor';

describe('ValidationResults', () => {
  it('renders successful validation result', () => {
    const result: ExerciseValidationResult = {
      success: true,
      passed_tests: 3,
      total_tests: 3,
      test_results: [
        { name: 'Test 1', passed: true, expected: 'hello', actual: 'hello' },
        { name: 'Test 2', passed: true, expected: 42, actual: 42 },
        { name: 'Test 3', passed: true, expected: true, actual: true },
      ],
      score: 100,
      feedback: 'Excellent work! All tests passed.',
    };

    render(<ValidationResults result={result} />);

    expect(screen.getByText('All Tests Passed!')).toBeInTheDocument();
    expect(screen.getByText('3/3 tests passed')).toBeInTheDocument();
    expect(screen.getByText('Score: 100%')).toBeInTheDocument();
    expect(screen.getByText('Excellent work! All tests passed.')).toBeInTheDocument();
  });

  it('renders failed validation result', () => {
    const result: ExerciseValidationResult = {
      success: false,
      passed_tests: 1,
      total_tests: 3,
      test_results: [
        { name: 'Test 1', passed: true, expected: 'hello', actual: 'hello' },
        { 
          name: 'Test 2', 
          passed: false, 
          expected: 42, 
          actual: 24,
          error: 'Expected 42 but got 24'
        },
        { 
          name: 'Test 3', 
          passed: false, 
          expected: true, 
          actual: false,
          error: 'Expected true but got false'
        },
      ],
      score: 33,
      feedback: 'Some tests failed. Please review your solution.',
    };

    render(<ValidationResults result={result} />);

    expect(screen.getByText('Some Tests Failed')).toBeInTheDocument();
    expect(screen.getByText('1/3 tests passed')).toBeInTheDocument();
    expect(screen.getByText('Score: 33%')).toBeInTheDocument();
    expect(screen.getByText('Some tests failed. Please review your solution.')).toBeInTheDocument();
  });

  it('renders individual test results correctly', () => {
    const result: ExerciseValidationResult = {
      success: false,
      passed_tests: 1,
      total_tests: 2,
      test_results: [
        { name: 'Passing Test', passed: true, expected: 'success', actual: 'success' },
        { 
          name: 'Failing Test', 
          passed: false, 
          expected: 'expected_value', 
          actual: 'actual_value',
          error: 'Values do not match'
        },
      ],
      score: 50,
      feedback: 'Mixed results',
    };

    render(<ValidationResults result={result} />);

    // Check passing test
    expect(screen.getByText('Passing Test')).toBeInTheDocument();
    expect(screen.getByText('PASS')).toBeInTheDocument();

    // Check failing test
    expect(screen.getByText('Failing Test')).toBeInTheDocument();
    expect(screen.getByText('FAIL')).toBeInTheDocument();
    expect(screen.getByText('Values do not match')).toBeInTheDocument();
    expect(screen.getByText('"expected_value"')).toBeInTheDocument();
    expect(screen.getByText('"actual_value"')).toBeInTheDocument();
  });

  it('applies correct score colors', () => {
    // Test high score (green)
    const highScoreResult: ExerciseValidationResult = {
      success: true,
      passed_tests: 3,
      total_tests: 3,
      test_results: [],
      score: 95,
      feedback: 'Great!',
    };

    const { rerender } = render(<ValidationResults result={highScoreResult} />);
    let scoreElement = screen.getByText('Score: 95%');
    expect(scoreElement).toHaveClass('text-green-600');

    // Test medium score (yellow)
    const mediumScoreResult: ExerciseValidationResult = {
      success: false,
      passed_tests: 2,
      total_tests: 3,
      test_results: [],
      score: 75,
      feedback: 'Good',
    };

    rerender(<ValidationResults result={mediumScoreResult} />);
    scoreElement = screen.getByText('Score: 75%');
    expect(scoreElement).toHaveClass('text-yellow-600');

    // Test low score (red)
    const lowScoreResult: ExerciseValidationResult = {
      success: false,
      passed_tests: 1,
      total_tests: 3,
      test_results: [],
      score: 30,
      feedback: 'Needs work',
    };

    rerender(<ValidationResults result={lowScoreResult} />);
    scoreElement = screen.getByText('Score: 30%');
    expect(scoreElement).toHaveClass('text-red-600');
  });

  it('renders progress bar correctly', () => {
    const result: ExerciseValidationResult = {
      success: false,
      passed_tests: 2,
      total_tests: 4,
      test_results: [],
      score: 50,
      feedback: 'Half way there',
    };

    render(<ValidationResults result={result} />);

    expect(screen.getByText('Progress')).toBeInTheDocument();
    expect(screen.getByText('2/4')).toBeInTheDocument();

    const progressBar = document.querySelector('.bg-red-600');
    expect(progressBar).toHaveStyle({ width: '50%' });
  });

  it('handles empty test results', () => {
    const result: ExerciseValidationResult = {
      success: true,
      passed_tests: 0,
      total_tests: 0,
      test_results: [],
      score: 100,
      feedback: 'No tests to run',
    };

    render(<ValidationResults result={result} />);

    expect(screen.getByText('All Tests Passed!')).toBeInTheDocument();
    expect(screen.getByText('0/0 tests passed')).toBeInTheDocument();
    expect(screen.getByText('No tests to run')).toBeInTheDocument();
  });

  it('handles missing feedback', () => {
    const result: ExerciseValidationResult = {
      success: true,
      passed_tests: 1,
      total_tests: 1,
      test_results: [
        { name: 'Test 1', passed: true, expected: 'ok', actual: 'ok' },
      ],
      score: 100,
      feedback: '',
    };

    render(<ValidationResults result={result} />);

    expect(screen.getByText('All Tests Passed!')).toBeInTheDocument();
    expect(screen.queryByText('Feedback:')).not.toBeInTheDocument();
  });

  it('formats JSON values correctly in test results', () => {
    const result: ExerciseValidationResult = {
      success: false,
      passed_tests: 0,
      total_tests: 1,
      test_results: [
        { 
          name: 'Complex Test', 
          passed: false, 
          expected: { key: 'value', number: 42, array: [1, 2, 3] }, 
          actual: { key: 'different', number: 24, array: [1, 2] },
          error: 'Objects do not match'
        },
      ],
      score: 0,
      feedback: 'Check your object structure',
    };

    render(<ValidationResults result={result} />);

    // Check that JSON is formatted (should contain newlines and proper indentation)
    expect(screen.getByText(/"key": "value",/)).toBeInTheDocument();
    expect(screen.getByText(/"number": 42,/)).toBeInTheDocument();
    expect(screen.getByText(/"array": \[/)).toBeInTheDocument();
  });

  it('applies correct styling for successful validation', () => {
    const result: ExerciseValidationResult = {
      success: true,
      passed_tests: 1,
      total_tests: 1,
      test_results: [],
      score: 100,
      feedback: 'Success!',
    };

    render(<ValidationResults result={result} />);

    const header = screen.getByText('All Tests Passed!').closest('div');
    expect(header).toHaveClass('bg-green-50');

    const progressBar = document.querySelector('.bg-green-600');
    expect(progressBar).toBeInTheDocument();
  });

  it('applies correct styling for failed validation', () => {
    const result: ExerciseValidationResult = {
      success: false,
      passed_tests: 0,
      total_tests: 1,
      test_results: [],
      score: 0,
      feedback: 'Failed!',
    };

    render(<ValidationResults result={result} />);

    const header = screen.getByText('Some Tests Failed').closest('div');
    expect(header).toHaveClass('bg-red-50');

    const progressBar = document.querySelector('.bg-red-600');
    expect(progressBar).toBeInTheDocument();
  });
});