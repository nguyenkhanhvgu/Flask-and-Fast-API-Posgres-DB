import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import LessonNavigation from '../LessonNavigation';
import { apiClient } from '../../../services/api';

// Mock the API client
vi.mock('../../../services/api', () => ({
  apiClient: {
    getModule: vi.fn(),
  },
}));

const mockModule = {
  id: 'module-1',
  name: 'Flask Fundamentals',
  description: 'Learn Flask basics',
  technology: 'flask' as const,
  difficulty_level: 'beginner' as const,
  order_index: 1,
  estimated_duration: 120,
  lessons: [
    {
      id: 'lesson-1',
      module_id: 'module-1',
      title: 'Introduction to Flask',
      content: 'Flask intro content',
      order_index: 1,
      learning_objectives: [],
      prerequisites: [],
      exercises: [],
      estimated_duration: 30,
    },
    {
      id: 'lesson-2',
      module_id: 'module-1',
      title: 'Flask Routing',
      content: 'Flask routing content',
      order_index: 2,
      learning_objectives: [],
      prerequisites: [],
      exercises: [],
      estimated_duration: 45,
    },
    {
      id: 'lesson-3',
      module_id: 'module-1',
      title: 'Flask Templates',
      content: 'Flask templates content',
      order_index: 3,
      learning_objectives: [],
      prerequisites: [],
      exercises: [],
      estimated_duration: 60,
    },
  ],
};

const renderLessonNavigation = (props = {}) => {
  const defaultProps = {
    currentLessonId: 'lesson-2',
    moduleId: 'module-1',
    onLessonChange: vi.fn(),
    ...props,
  };

  return render(<LessonNavigation {...defaultProps} />);
};

describe('LessonNavigation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (apiClient.getModule as any).mockResolvedValue(mockModule);
  });

  it('renders navigation with previous and next lessons', async () => {
    const onLessonChange = vi.fn();
    renderLessonNavigation({ onLessonChange });

    await waitFor(() => {
      expect(screen.getByText('Introduction to Flask')).toBeInTheDocument();
      expect(screen.getByText('Flask Templates')).toBeInTheDocument();
    });

    expect(screen.getByText('Previous')).toBeInTheDocument();
    expect(screen.getByText('Next')).toBeInTheDocument();
  });

  it('handles previous lesson navigation', async () => {
    const onLessonChange = vi.fn();
    renderLessonNavigation({ onLessonChange });

    await waitFor(() => {
      expect(screen.getByText('Introduction to Flask')).toBeInTheDocument();
    });

    const previousButton = screen.getByText('Introduction to Flask').closest('button');
    fireEvent.click(previousButton!);

    expect(onLessonChange).toHaveBeenCalledWith('lesson-1');
  });

  it('handles next lesson navigation', async () => {
    const onLessonChange = vi.fn();
    renderLessonNavigation({ onLessonChange });

    await waitFor(() => {
      expect(screen.getByText('Flask Templates')).toBeInTheDocument();
    });

    const nextButton = screen.getByText('Flask Templates').closest('button');
    fireEvent.click(nextButton!);

    expect(onLessonChange).toHaveBeenCalledWith('lesson-3');
  });

  it('shows progress indicator with correct lesson position', async () => {
    const { container } = renderLessonNavigation();

    await waitFor(() => {
      expect(screen.getByText('Lesson 2 of 3')).toBeInTheDocument();
    });

    // Check progress dots
    const progressDots = container.querySelectorAll('.w-2.h-2.rounded-full');
    expect(progressDots).toHaveLength(3);
    
    // First dot should be green (completed)
    expect(progressDots[0]).toHaveClass('bg-green-500');
    // Second dot should be blue (current)
    expect(progressDots[1]).toHaveClass('bg-blue-500');
    // Third dot should be gray (not started)
    expect(progressDots[2]).toHaveClass('bg-gray-300');
  });

  it('hides previous button on first lesson', async () => {
    renderLessonNavigation({ currentLessonId: 'lesson-1' });

    await waitFor(() => {
      expect(screen.getByText('Lesson 1 of 3')).toBeInTheDocument();
    });

    expect(screen.queryByText('Previous')).not.toBeInTheDocument();
    expect(screen.getByText('Next')).toBeInTheDocument();
  });

  it('shows module complete message on last lesson', async () => {
    renderLessonNavigation({ currentLessonId: 'lesson-3' });

    await waitFor(() => {
      expect(screen.getByText('Module Complete!')).toBeInTheDocument();
    });

    expect(screen.getByText('Previous')).toBeInTheDocument();
    expect(screen.queryByText('Next')).not.toBeInTheDocument();
  });

  it('displays module name and back to overview link', async () => {
    renderLessonNavigation();

    await waitFor(() => {
      expect(screen.getByText('Flask Fundamentals')).toBeInTheDocument();
    });

    expect(screen.getByText('← Back to Module Overview')).toBeInTheDocument();
  });

  it('handles API error gracefully', async () => {
    (apiClient.getModule as any).mockRejectedValue(new Error('API Error'));
    
    const { container } = renderLessonNavigation();

    // Component should not render anything when there's an error
    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });

  it('handles loading state', () => {
    const { container } = renderLessonNavigation();

    // During loading, component should not render navigation
    expect(container.firstChild).toBeNull();
  });

  it('handles lesson not found in module', async () => {
    const { container } = renderLessonNavigation({ currentLessonId: 'non-existent-lesson' });

    await waitFor(() => {
      // Component should not render when lesson is not found
      expect(container.firstChild).toBeNull();
    });
  });

  it('sorts lessons by order_index', async () => {
    const unsortedModule = {
      ...mockModule,
      lessons: [
        { ...mockModule.lessons[2], order_index: 3 },
        { ...mockModule.lessons[0], order_index: 1 },
        { ...mockModule.lessons[1], order_index: 2 },
      ],
    };

    (apiClient.getModule as any).mockResolvedValue(unsortedModule);
    
    renderLessonNavigation();

    await waitFor(() => {
      expect(screen.getByText('Lesson 2 of 3')).toBeInTheDocument();
    });

    // Should still show correct previous/next lessons after sorting
    expect(screen.getByText('Introduction to Flask')).toBeInTheDocument();
    expect(screen.getByText('Flask Templates')).toBeInTheDocument();
  });

  it('handles single lesson module', async () => {
    const singleLessonModule = {
      ...mockModule,
      lessons: [mockModule.lessons[0]],
    };

    (apiClient.getModule as any).mockResolvedValue(singleLessonModule);
    
    renderLessonNavigation({ currentLessonId: 'lesson-1' });

    await waitFor(() => {
      expect(screen.getByText('Lesson 1 of 1')).toBeInTheDocument();
    });

    expect(screen.queryByText('Previous')).not.toBeInTheDocument();
    expect(screen.getByText('Module Complete!')).toBeInTheDocument();
  });
});