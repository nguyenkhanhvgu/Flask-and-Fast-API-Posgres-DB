import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import CodeOutput from '../CodeOutput';
import { CodeExecutionResult } from '../../../types/codeEditor';

describe('CodeOutput', () => {
  it('renders successful execution result', () => {
    const result: CodeExecutionResult = {
      success: true,
      output: 'Hello, World!',
      execution_time: 0.123,
      memory_usage: 1024,
    };

    render(<CodeOutput result={result} />);

    expect(screen.getByText('Execution Successful')).toBeInTheDocument();
    expect(screen.getByText('Hello, World!')).toBeInTheDocument();
    expect(screen.getByText('Time: 123ms')).toBeInTheDocument();
    expect(screen.getByText('Memory: 1.0KB')).toBeInTheDocument();
  });

  it('renders failed execution result', () => {
    const result: CodeExecutionResult = {
      success: false,
      output: '',
      error: 'SyntaxError: invalid syntax',
      execution_time: 0.05,
    };

    render(<CodeOutput result={result} />);

    expect(screen.getByText('Execution Failed')).toBeInTheDocument();
    expect(screen.getByText('SyntaxError: invalid syntax')).toBeInTheDocument();
    expect(screen.getByText('Time: 50ms')).toBeInTheDocument();
  });

  it('renders both output and error when present', () => {
    const result: CodeExecutionResult = {
      success: false,
      output: 'Some output before error',
      error: 'RuntimeError: something went wrong',
      execution_time: 0.25,
    };

    render(<CodeOutput result={result} />);

    expect(screen.getByText('Execution Failed')).toBeInTheDocument();
    expect(screen.getByText('Some output before error')).toBeInTheDocument();
    expect(screen.getByText('RuntimeError: something went wrong')).toBeInTheDocument();
  });

  it('shows message when no output and successful', () => {
    const result: CodeExecutionResult = {
      success: true,
      output: '',
      execution_time: 0.01,
    };

    render(<CodeOutput result={result} />);

    expect(screen.getByText('Execution Successful')).toBeInTheDocument();
    expect(screen.getByText('Code executed successfully with no output.')).toBeInTheDocument();
  });

  it('formats execution time correctly for different ranges', () => {
    // Test milliseconds
    const msResult: CodeExecutionResult = {
      success: true,
      output: 'test',
      execution_time: 0.123,
    };

    const { rerender } = render(<CodeOutput result={msResult} />);
    expect(screen.getByText('Time: 123ms')).toBeInTheDocument();

    // Test seconds
    const secResult: CodeExecutionResult = {
      success: true,
      output: 'test',
      execution_time: 1.234,
    };

    rerender(<CodeOutput result={secResult} />);
    expect(screen.getByText('Time: 1.23s')).toBeInTheDocument();
  });

  it('formats memory usage correctly for different ranges', () => {
    // Test bytes
    const bytesResult: CodeExecutionResult = {
      success: true,
      output: 'test',
      execution_time: 0.1,
      memory_usage: 512,
    };

    const { rerender } = render(<CodeOutput result={bytesResult} />);
    expect(screen.getByText('Memory: 512B')).toBeInTheDocument();

    // Test kilobytes
    const kbResult: CodeExecutionResult = {
      success: true,
      output: 'test',
      execution_time: 0.1,
      memory_usage: 2048,
    };

    rerender(<CodeOutput result={kbResult} />);
    expect(screen.getByText('Memory: 2.0KB')).toBeInTheDocument();

    // Test megabytes
    const mbResult: CodeExecutionResult = {
      success: true,
      output: 'test',
      execution_time: 0.1,
      memory_usage: 2097152, // 2MB
    };

    rerender(<CodeOutput result={mbResult} />);
    expect(screen.getByText('Memory: 2.0MB')).toBeInTheDocument();
  });

  it('does not show memory usage when not provided', () => {
    const result: CodeExecutionResult = {
      success: true,
      output: 'test',
      execution_time: 0.1,
    };

    render(<CodeOutput result={result} />);

    expect(screen.queryByText(/Memory:/)).not.toBeInTheDocument();
  });

  it('applies correct styling for successful execution', () => {
    const result: CodeExecutionResult = {
      success: true,
      output: 'Success!',
      execution_time: 0.1,
    };

    render(<CodeOutput result={result} />);

    const header = screen.getByText('Execution Successful').closest('div');
    expect(header).toHaveClass('bg-green-50');
  });

  it('applies correct styling for failed execution', () => {
    const result: CodeExecutionResult = {
      success: false,
      output: '',
      error: 'Error!',
      execution_time: 0.1,
    };

    render(<CodeOutput result={result} />);

    const header = screen.getByText('Execution Failed').closest('div');
    expect(header).toHaveClass('bg-red-50');
  });

  it('preserves whitespace in output and error messages', () => {
    const result: CodeExecutionResult = {
      success: false,
      output: 'Line 1\nLine 2\n  Indented line',
      error: 'Error line 1\n  Error line 2',
      execution_time: 0.1,
    };

    render(<CodeOutput result={result} />);

    const outputPre = screen.getByText('Line 1\nLine 2\n  Indented line');
    const errorPre = screen.getByText('Error line 1\n  Error line 2');

    expect(outputPre).toHaveClass('whitespace-pre-wrap');
    expect(errorPre).toHaveClass('whitespace-pre-wrap');
  });
});