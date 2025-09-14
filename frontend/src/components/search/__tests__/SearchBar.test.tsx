import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { SearchBar } from '../SearchBar';
import apiClient from '../../../services/api';

// Mock the API client
vi.mock('../../../services/api', () => ({
  default: {
    getSearchSuggestions: vi.fn(),
  },
}));

const mockApiClient = apiClient as any;

describe('SearchBar', () => {
  const defaultProps = {
    value: '',
    onChange: vi.fn(),
    onSearch: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with placeholder text', () => {
    render(<SearchBar {...defaultProps} />);
    
    expect(screen.getByPlaceholderText(/search lessons, exercises/i)).toBeInTheDocument();
  });

  it('displays the current value', () => {
    render(<SearchBar {...defaultProps} value="flask routing" />);
    
    expect(screen.getByDisplayValue('flask routing')).toBeInTheDocument();
  });

  it('calls onChange when input value changes', async () => {
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'flask');
    
    expect(defaultProps.onChange).toHaveBeenCalledWith('flask');
  });

  it('calls onSearch when form is submitted', async () => {
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} value="flask routing" />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, '{enter}');
    
    expect(defaultProps.onSearch).toHaveBeenCalledWith('flask routing');
  });

  it('shows clear button when value is not empty', () => {
    render(<SearchBar {...defaultProps} value="flask" />);
    
    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument();
  });

  it('clears input when clear button is clicked', async () => {
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} value="flask" />);
    
    const clearButton = screen.getByRole('button', { name: /clear/i });
    await user.click(clearButton);
    
    expect(defaultProps.onChange).toHaveBeenCalledWith('');
  });

  it('fetches and displays suggestions', async () => {
    const mockSuggestions = [
      { text: 'flask routing', type: 'query', count: 5 },
      { text: 'flask', type: 'technology', count: 10 },
    ];
    
    mockApiClient.getSearchSuggestions.mockResolvedValue(mockSuggestions);
    
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'fla');
    
    await waitFor(() => {
      expect(screen.getByText('flask routing')).toBeInTheDocument();
      expect(screen.getByText('flask')).toBeInTheDocument();
    });
  });

  it('handles suggestion click', async () => {
    const mockSuggestions = [
      { text: 'flask routing', type: 'query', count: 5 },
    ];
    
    mockApiClient.getSearchSuggestions.mockResolvedValue(mockSuggestions);
    
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'fla');
    
    await waitFor(() => {
      expect(screen.getByText('flask routing')).toBeInTheDocument();
    });
    
    await user.click(screen.getByText('flask routing'));
    
    expect(defaultProps.onChange).toHaveBeenCalledWith('flask routing');
    expect(defaultProps.onSearch).toHaveBeenCalledWith('flask routing');
  });

  it('hides suggestions when clicking outside', async () => {
    const mockSuggestions = [
      { text: 'flask routing', type: 'query', count: 5 },
    ];
    
    mockApiClient.getSearchSuggestions.mockResolvedValue(mockSuggestions);
    
    const user = userEvent.setup();
    render(
      <div>
        <SearchBar {...defaultProps} />
        <div data-testid="outside">Outside element</div>
      </div>
    );
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'fla');
    
    await waitFor(() => {
      expect(screen.getByText('flask routing')).toBeInTheDocument();
    });
    
    await user.click(screen.getByTestId('outside'));
    
    await waitFor(() => {
      expect(screen.queryByText('flask routing')).not.toBeInTheDocument();
    });
  });

  it('shows loading state while fetching suggestions', async () => {
    mockApiClient.getSearchSuggestions.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve([]), 100))
    );
    
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'fla');
    
    expect(screen.getByText('Loading suggestions...')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    mockApiClient.getSearchSuggestions.mockRejectedValue(new Error('API Error'));
    
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'fla');
    
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Failed to fetch suggestions:', expect.any(Error));
    });
    
    consoleSpy.mockRestore();
  });

  it('debounces API calls', async () => {
    mockApiClient.getSearchSuggestions.mockResolvedValue([]);
    
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByRole('textbox');
    
    // Type multiple characters quickly
    await user.type(input, 'flask');
    
    // Should only make one API call after debounce
    await waitFor(() => {
      expect(mockApiClient.getSearchSuggestions).toHaveBeenCalledTimes(1);
    });
  });

  it('does not fetch suggestions for short queries', async () => {
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'f');
    
    await waitFor(() => {
      expect(mockApiClient.getSearchSuggestions).not.toHaveBeenCalled();
    });
  });

  it('hides suggestions when pressing Escape', async () => {
    const mockSuggestions = [
      { text: 'flask routing', type: 'query', count: 5 },
    ];
    
    mockApiClient.getSearchSuggestions.mockResolvedValue(mockSuggestions);
    
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'fla');
    
    await waitFor(() => {
      expect(screen.getByText('flask routing')).toBeInTheDocument();
    });
    
    await user.keyboard('{Escape}');
    
    await waitFor(() => {
      expect(screen.queryByText('flask routing')).not.toBeInTheDocument();
    });
  });
});