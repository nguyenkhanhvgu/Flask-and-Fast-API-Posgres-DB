import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect } from 'vitest';
import CodeControls from '../CodeControls';

describe('CodeControls', () => {
  const defaultProps = {
    onExecute: vi.fn(),
    onReset: vi.fn(),
    isExecuting: false,
    isValidating: false,
    showHints: false,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders execute and reset buttons', () => {
    render(<CodeControls {...defaultProps} />);
    
    expect(screen.getByText('Run Code')).toBeInTheDocument();
    expect(screen.getByText('Reset')).toBeInTheDocument();
  });

  it('renders validate button when onValidate is provided', () => {
    const onValidate = vi.fn();
    render(<CodeControls {...defaultProps} onValidate={onValidate} />);
    
    expect(screen.getByText('Submit Solution')).toBeInTheDocument();
  });

  it('renders hints button when onToggleHints is provided', () => {
    const onToggleHints = vi.fn();
    render(<CodeControls {...defaultProps} onToggleHints={onToggleHints} />);
    
    expect(screen.getByText('Show Hints')).toBeInTheDocument();
  });

  it('shows "Hide Hints" when hints are visible', () => {
    const onToggleHints = vi.fn();
    render(<CodeControls {...defaultProps} onToggleHints={onToggleHints} showHints={true} />);
    
    expect(screen.getByText('Hide Hints')).toBeInTheDocument();
  });

  it('calls onExecute when run button is clicked', async () => {
    const user = userEvent.setup();
    const onExecute = vi.fn();
    
    render(<CodeControls {...defaultProps} onExecute={onExecute} />);
    
    const runButton = screen.getByText('Run Code');
    await user.click(runButton);
    
    expect(onExecute).toHaveBeenCalledTimes(1);
  });

  it('calls onValidate when submit button is clicked', async () => {
    const user = userEvent.setup();
    const onValidate = vi.fn();
    
    render(<CodeControls {...defaultProps} onValidate={onValidate} />);
    
    const submitButton = screen.getByText('Submit Solution');
    await user.click(submitButton);
    
    expect(onValidate).toHaveBeenCalledTimes(1);
  });

  it('calls onToggleHints when hints button is clicked', async () => {
    const user = userEvent.setup();
    const onToggleHints = vi.fn();
    
    render(<CodeControls {...defaultProps} onToggleHints={onToggleHints} />);
    
    const hintsButton = screen.getByText('Show Hints');
    await user.click(hintsButton);
    
    expect(onToggleHints).toHaveBeenCalledTimes(1);
  });

  it('calls onReset when reset button is clicked', async () => {
    const user = userEvent.setup();
    const onReset = vi.fn();
    
    render(<CodeControls {...defaultProps} onReset={onReset} />);
    
    const resetButton = screen.getByText('Reset');
    await user.click(resetButton);
    
    expect(onReset).toHaveBeenCalledTimes(1);
  });

  it('disables buttons when executing', () => {
    render(<CodeControls {...defaultProps} isExecuting={true} />);
    
    expect(screen.getByText('Running...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /running/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /reset/i })).toBeDisabled();
  });

  it('disables buttons when validating', () => {
    const onValidate = vi.fn();
    render(<CodeControls {...defaultProps} onValidate={onValidate} isValidating={true} />);
    
    expect(screen.getByText('Validating...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /validating/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /run code/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /reset/i })).toBeDisabled();
  });

  it('shows loading spinner when executing', () => {
    render(<CodeControls {...defaultProps} isExecuting={true} />);
    
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('shows loading spinner when validating', () => {
    const onValidate = vi.fn();
    render(<CodeControls {...defaultProps} onValidate={onValidate} isValidating={true} />);
    
    const spinners = document.querySelectorAll('.animate-spin');
    expect(spinners.length).toBeGreaterThan(0);
  });

  it('applies correct styling for hints button when hints are shown', () => {
    const onToggleHints = vi.fn();
    render(<CodeControls {...defaultProps} onToggleHints={onToggleHints} showHints={true} />);
    
    const hintsButton = screen.getByText('Hide Hints');
    expect(hintsButton).toHaveClass('bg-yellow-100', 'text-yellow-800');
  });

  it('applies correct styling for hints button when hints are hidden', () => {
    const onToggleHints = vi.fn();
    render(<CodeControls {...defaultProps} onToggleHints={onToggleHints} showHints={false} />);
    
    const hintsButton = screen.getByText('Show Hints');
    expect(hintsButton).toHaveClass('bg-gray-100', 'text-gray-700');
  });
});