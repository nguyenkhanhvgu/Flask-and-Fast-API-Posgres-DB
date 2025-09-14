import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BookmarkManager } from '../BookmarkManager';
import { mockModules, mockBookmarks } from '../../../test/mocks';
import { ProgressProvider } from '../../../contexts/ProgressContext';
import { AuthProvider } from '../../../contexts/AuthContext';

import { vi } from 'vitest';

// Mock the progress context
const mockRemoveBookmark = vi.fn();
const mockAddBookmark = vi.fn();

vi.mock('../../../contexts/ProgressContext', () => ({
  ...vi.importActual('../../../contexts/ProgressContext'),
  useProgress: () => ({
    addBookmark: mockAddBookmark,
    removeBookmark: mockRemoveBookmark,
  }),
}));

describe('BookmarkManager', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays bookmark count correctly', () => {
    render(<BookmarkManager modules={mockModules} bookmarks={mockBookmarks} />);
    
    expect(screen.getByText('Bookmarks (2)')).toBeInTheDocument();
  });

  it('shows empty state when no bookmarks exist', () => {
    render(<BookmarkManager modules={mockModules} bookmarks={[]} />);
    
    expect(screen.getByText('No bookmarks yet')).toBeInTheDocument();
    expect(screen.getByText('Start bookmarking lessons and exercises to save them for later.')).toBeInTheDocument();
  });

  it('displays bookmarked lessons correctly', () => {
    render(<BookmarkManager modules={mockModules} bookmarks={mockBookmarks} />);
    
    // Should show the bookmarked lesson
    expect(screen.getByText('Introduction to Flask')).toBeInTheDocument();
    expect(screen.getByText('SQL Fundamentals')).toBeInTheDocument();
  });

  it('shows technology badges for bookmarked content', () => {
    render(<BookmarkManager modules={mockModules} bookmarks={mockBookmarks} />);
    
    expect(screen.getByText('FLASK')).toBeInTheDocument();
    expect(screen.getByText('POSTGRESQL')).toBeInTheDocument();
  });

  it('displays lesson information correctly', () => {
    render(<BookmarkManager modules={mockModules} bookmarks={mockBookmarks} />);
    
    // Check lesson details
    const flaskLesson = screen.getByText('Introduction to Flask').closest('div');
    expect(flaskLesson).toContainHTML('30 min');
    expect(flaskLesson).toContainHTML('1 exercises');
    
    const postgresqlLesson = screen.getByText('SQL Fundamentals').closest('div');
    expect(postgresqlLesson).toContainHTML('90 min');
    expect(postgresqlLesson).toContainHTML('0 exercises');
  });

  it('handles remove bookmark functionality', async () => {
    render(<BookmarkManager modules={mockModules} bookmarks={mockBookmarks} />);
    
    const removeButtons = screen.getAllByTitle('Remove bookmark');
    fireEvent.click(removeButtons[0]);
    
    await waitFor(() => {
      expect(mockRemoveBookmark).toHaveBeenCalledWith('lesson-1');
    });
  });

  it('handles open lesson functionality', () => {
    render(<BookmarkManager modules={mockModules} bookmarks={mockBookmarks} />);
    
    const openButtons = screen.getAllByText('Open');
    fireEvent.click(openButtons[0]);
    
    expect(window.open).toHaveBeenCalledWith('/lessons/lesson-1', '_blank');
  });

  it('shows expand/collapse functionality when there are many bookmarks', () => {
    const manyBookmarks = ['lesson-1', 'lesson-2', 'lesson-3', 'lesson-4'];
    render(<BookmarkManager modules={mockModules} bookmarks={manyBookmarks} />);
    
    // Should show "Show All" button when there are more than 3 bookmarks
    expect(screen.getByText('Show All')).toBeInTheDocument();
  });

  it('expands to show all bookmarks when "Show All" is clicked', () => {
    const manyBookmarks = ['lesson-1', 'lesson-2', 'lesson-3', 'lesson-4'];
    render(<BookmarkManager modules={mockModules} bookmarks={manyBookmarks} />);
    
    // Initially should show only 3 bookmarks
    expect(screen.getAllByText('Open')).toHaveLength(3);
    
    // Click "Show All"
    fireEvent.click(screen.getByText('Show All'));
    
    // Should now show all bookmarks
    expect(screen.getAllByText('Open')).toHaveLength(4);
    expect(screen.getByText('Show Less')).toBeInTheDocument();
  });

  it('collapses bookmarks when "Show Less" is clicked', () => {
    const manyBookmarks = ['lesson-1', 'lesson-2', 'lesson-3', 'lesson-4'];
    render(<BookmarkManager modules={mockModules} bookmarks={manyBookmarks} />);
    
    // Expand first
    fireEvent.click(screen.getByText('Show All'));
    expect(screen.getAllByText('Open')).toHaveLength(4);
    
    // Then collapse
    fireEvent.click(screen.getByText('Show Less'));
    expect(screen.getAllByText('Open')).toHaveLength(3);
    expect(screen.getByText('Show All')).toBeInTheDocument();
  });

  it('sorts bookmarked content alphabetically by title', () => {
    render(<BookmarkManager modules={mockModules} bookmarks={mockBookmarks} />);
    
    // Get lesson titles directly from the text content
    const lessonTitles = screen.getAllByText(/Introduction to Flask|SQL Fundamentals/);
    
    // Should be sorted: "Introduction to Flask" comes before "SQL Fundamentals"
    expect(lessonTitles[0]).toHaveTextContent('Introduction to Flask');
    expect(lessonTitles[1]).toHaveTextContent('SQL Fundamentals');
  });

  it('handles error when removing bookmark fails', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    mockRemoveBookmark.mockRejectedValueOnce(new Error('Network error'));
    
    render(<BookmarkManager modules={mockModules} bookmarks={mockBookmarks} />);
    
    const removeButtons = screen.getAllByTitle('Remove bookmark');
    fireEvent.click(removeButtons[0]);
    
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Failed to remove bookmark:', expect.any(Error));
    });
    
    consoleSpy.mockRestore();
  });
});