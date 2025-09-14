import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import CodeEditor from '../CodeEditor';
import { apiClient } from '../../../services/api';

// Mock Monaco Editor
vi.mock('@monaco-editor/react', () => ({
  default: ({ value, onChange, loading }: any) => (
    <div data-testid="monaco-editor">
      {loading}
      <textarea
        data-testid="code-textarea"
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
      />
    </div>
  ),
}));

// Mock API client
vi.mock('../../../services/api', () => ({
  apiClient: {
    executeCode: vi.fn(),
    validateExercise: vi.fn(),
    getExerciseHints: vi.fn(),
  },
}));

const mockApiClient = apiClient as any;

describe('CodeEditor', () => {
  const defaultProps = {
    initialCode: 'print("Hello, World!")',
    language: 'python',
    height: '400px',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it('renders with initial code', () => {
    render(<CodeEditor {...defaultProps} />);
    
    expect(screen.getByDisplayValue('print("Hello, World!")')).toBeInTheDocument();
    expect(screen.getByText('Code Editor')).toBeInTheDocument();
    expect(screen.getByText('python')).toBeInTheDocument();
  });

  it('renders in read-only mode', () => {
    render(<CodeEditor {...defaultProps} readOnly />);
    
    expect(screen.getByText('Read Only')).toBeInTheDocument();
    expect(screen.queryByText('Run Code')).not.toBeInTheDocument();
  });

  it('calls onCodeChange when code is modified', async () => {
    const user = userEvent.setup();
    const onCodeChange = vi.fn();
    
    render(<CodeEditor {...defaultProps} onCodeChange={onCodeChange} />);
    
    const textarea = screen.getByTestId('code-textarea');
    await user.clear(textarea);
    await user.type(textarea, 'print("Modified code")');
    
    expect(onCodeChange).toHaveBeenCalledWith('print("Modified code")');
  });

  it('executes code successfully', async () => {
    const user = userEvent.setup();
    const mockResult = {
      success: true,
      output: 'Hello, World!',
      execution_time: 0.1,
    };
    
    mockApiClient.executeCode.mockResolvedValue(mockResult);
    
    render(<CodeEditor {...defaultProps} />);
    
    const runButton = screen.getByText('Run Code');
    await user.click(runButton);
    
    expect(mockApiClient.executeCode).toHaveBeenCalledWith('print("Hello, World!")', 'python');
    
    await waitFor(() => {
      expect(screen.getByText('Execution Successful')).toBeInTheDocument();
      expect(screen.getByText('Hello, World!')).toBeInTheDocument();
    });
  });

  it('handles code execution errors', async () => {
    const user = userEvent.setup();
    const mockResult = {
      success: false,
      output: '',
      error: 'SyntaxError: invalid syntax',
      execution_time: 0.05,
    };
    
    mockApiClient.executeCode.mockResolvedValue(mockResult);
    
    render(<CodeEditor {...defaultProps} />);
    
    const runButton = screen.getByText('Run Code');
    await user.click(runButton);
    
    await waitFor(() => {
      expect(screen.getByText('Execution Failed')).toBeInTheDocument();
      expect(screen.getByText('SyntaxError: invalid syntax')).toBeInTheDocument();
    });
  });

  it('validates exercise solution', async () => {
    const user = userEvent.setup();
    const mockResult = {
      success: true,
      passed_tests: 3,
      total_tests: 3,
      test_results: [
        { name: 'Test 1', passed: true, expected: 'Hello', actual: 'Hello' },
        { name: 'Test 2', passed: true, expected: 42, actual: 42 },
        { name: 'Test 3', passed: true, expected: true, actual: true },
      ],
      score: 100,
      feedback: 'Excellent work!',
    };
    
    mockApiClient.validateExercise.mockResolvedValue(mockResult);
    
    render(<CodeEditor {...defaultProps} exerciseId="exercise-123" />);
    
    const submitButton = screen.getByText('Submit Solution');
    await user.click(submitButton);
    
    expect(mockApiClient.validateExercise).toHaveBeenCalledWith('exercise-123', 'print("Hello, World!")');
    
    await waitFor(() => {
      expect(screen.getByText('All Tests Passed!')).toBeInTheDocument();
      expect(screen.getByText('Score: 100%')).toBeInTheDocument();
      expect(screen.getByText('Excellent work!')).toBeInTheDocument();
    });
  });

  it('handles validation failures', async () => {
    const user = userEvent.setup();
    const mockResult = {
      success: false,
      passed_tests: 1,
      total_tests: 3,
      test_results: [
        { name: 'Test 1', passed: true, expected: 'Hello', actual: 'Hello' },
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
      feedback: 'Some tests failed. Check your logic.',
    };
    
    mockApiClient.validateExercise.mockResolvedValue(mockResult);
    
    render(<CodeEditor {...defaultProps} exerciseId="exercise-123" />);
    
    const submitButton = screen.getByText('Submit Solution');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Some Tests Failed')).toBeInTheDocument();
      expect(screen.getByText('Score: 33%')).toBeInTheDocument();
      expect(screen.getByText('1/3 tests passed')).toBeInTheDocument();
    });
  });

  it('loads and displays hints', async () => {
    const user = userEvent.setup();
    const mockHints = [
      'Try using a for loop',
      'Remember to handle edge cases',
      'Consider using list comprehension',
    ];
    
    mockApiClient.getExerciseHints.mockResolvedValue(mockHints);
    
    render(<CodeEditor {...defaultProps} exerciseId="exercise-123" />);
    
    await waitFor(() => {
      expect(mockApiClient.getExerciseHints).toHaveBeenCalledWith('exercise-123');
    });
    
    const hintsButton = screen.getByText('Show Hints');
    await user.click(hintsButton);
    
    expect(screen.getByText('Hints:')).toBeInTheDocument();
    expect(screen.getByText('1. Try using a for loop')).toBeInTheDocument();
    expect(screen.getByText('2. Remember to handle edge cases')).toBeInTheDocument();
    expect(screen.getByText('3. Consider using list comprehension')).toBeInTheDocument();
    
    // Test hiding hints
    const hideHintsButton = screen.getByText('Hide Hints');
    await user.click(hideHintsButton);
    
    expect(screen.queryByText('Hints:')).not.toBeInTheDocument();
  });

  it('resets code to initial value', async () => {
    const user = userEvent.setup();
    const onCodeChange = vi.fn();
    
    render(<CodeEditor {...defaultProps} onCodeChange={onCodeChange} />);
    
    // Modify the code
    const textarea = screen.getByTestId('code-textarea');
    await user.clear(textarea);
    await user.type(textarea, 'modified code');
    
    // Reset the code
    const resetButton = screen.getByText('Reset');
    await user.click(resetButton);
    
    expect(onCodeChange).toHaveBeenLastCalledWith('print("Hello, World!")');
    expect(screen.getByDisplayValue('print("Hello, World!")')).toBeInTheDocument();
  });

  it('disables buttons during execution', async () => {
    const user = userEvent.setup();
    
    // Mock a delayed response
    mockApiClient.executeCode.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({
        success: true,
        output: 'Done',
        execution_time: 1.0,
      }), 100))
    );
    
    render(<CodeEditor {...defaultProps} exerciseId="exercise-123" />);
    
    const runButton = screen.getByText('Run Code');
    const submitButton = screen.getByText('Submit Solution');
    const resetButton = screen.getByText('Reset');
    
    await user.click(runButton);
    
    // Buttons should be disabled during execution
    expect(screen.getByText('Running...')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
    expect(resetButton).toBeDisabled();
    
    // Wait for execution to complete
    await waitFor(() => {
      expect(screen.getByText('Run Code')).toBeInTheDocument();
    });
    
    // Buttons should be enabled again
    expect(submitButton).not.toBeDisabled();
    expect(resetButton).not.toBeDisabled();
  });

  it('calls callback functions when provided', async () => {
    const user = userEvent.setup();
    const onExecute = vi.fn();
    const onValidate = vi.fn();
    
    const mockExecuteResult = {
      success: true,
      output: 'Hello',
      execution_time: 0.1,
    };
    
    const mockValidateResult = {
      success: true,
      passed_tests: 1,
      total_tests: 1,
      test_results: [],
      score: 100,
      feedback: 'Great!',
    };
    
    mockApiClient.executeCode.mockResolvedValue(mockExecuteResult);
    mockApiClient.validateExercise.mockResolvedValue(mockValidateResult);
    
    render(
      <CodeEditor 
        {...defaultProps} 
        exerciseId="exercise-123"
        onExecute={onExecute}
        onValidate={onValidate}
      />
    );
    
    // Test execute callback
    const runButton = screen.getByText('Run Code');
    await user.click(runButton);
    
    await waitFor(() => {
      expect(onExecute).toHaveBeenCalledWith(mockExecuteResult);
    });
    
    // Test validate callback
    const submitButton = screen.getByText('Submit Solution');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(onValidate).toHaveBeenCalledWith(mockValidateResult);
    });
  });

  it('handles API errors gracefully', async () => {
    const user = userEvent.setup();
    
    mockApiClient.executeCode.mockRejectedValue(new Error('Network error'));
    
    render(<CodeEditor {...defaultProps} />);
    
    const runButton = screen.getByText('Run Code');
    await user.click(runButton);
    
    await waitFor(() => {
      expect(screen.getByText('Execution Failed')).toBeInTheDocument();
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });
});