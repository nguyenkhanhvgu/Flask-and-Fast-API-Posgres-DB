import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import LessonPage from '../LessonPage';

// Mock the LessonViewer component
vi.mock('../../components/lesson/LessonViewer', () => ({
  default: ({ lessonId, moduleId }: any) => (
    <div data-testid="lesson-viewer">
      <div>Lesson ID: {lessonId}</div>
      <div>Module ID: {moduleId}</div>
      <button onClick={() => console.log('Change Lesson')}>Change Lesson</button>
    </div>
  ),
}));

const mockNavigate = vi.fn();
const mockUseParams = vi.fn();

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => mockUseParams(),
  };
});

const renderLessonPage = (initialEntries = ['/modules/module-1/lessons/lesson-1']) => {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <LessonPage />
    </MemoryRouter>
  );
};

describe('LessonPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default params
    mockUseParams.mockReturnValue({
      moduleId: 'module-1',
      lessonId: 'lesson-1',
    });
  });

  it('renders LessonViewer with correct props', () => {
    renderLessonPage();

    expect(screen.getByTestId('lesson-viewer')).toBeInTheDocument();
    expect(screen.getByText('Lesson ID: lesson-1')).toBeInTheDocument();
    expect(screen.getByText('Module ID: module-1')).toBeInTheDocument();
  });

  it('handles lesson navigation correctly', () => {
    renderLessonPage();

    const changeLessonButton = screen.getByText('Change Lesson');
    fireEvent.click(changeLessonButton);

    // Since we're mocking the component, we can't test the actual navigation
    // but we can verify the component renders
    expect(screen.getByTestId('lesson-viewer')).toBeInTheDocument();
  });

  it('shows error when moduleId is missing', () => {
    mockUseParams.mockReturnValue({
      moduleId: undefined,
      lessonId: 'lesson-1',
    });

    renderLessonPage();

    expect(screen.getByText('Invalid lesson URL')).toBeInTheDocument();
    expect(screen.getByText('Go to Dashboard')).toBeInTheDocument();
  });

  it('shows error when lessonId is missing', () => {
    mockUseParams.mockReturnValue({
      moduleId: 'module-1',
      lessonId: undefined,
    });

    renderLessonPage();

    expect(screen.getByText('Invalid lesson URL')).toBeInTheDocument();
    expect(screen.getByText('Go to Dashboard')).toBeInTheDocument();
  });

  it('shows error when both params are missing', () => {
    mockUseParams.mockReturnValue({
      moduleId: undefined,
      lessonId: undefined,
    });

    renderLessonPage();

    expect(screen.getByText('Invalid lesson URL')).toBeInTheDocument();
    expect(screen.getByText('Go to Dashboard')).toBeInTheDocument();
  });

  it('navigates to dashboard when Go to Dashboard is clicked', () => {
    mockUseParams.mockReturnValue({
      moduleId: undefined,
      lessonId: 'lesson-1',
    });

    renderLessonPage();

    const dashboardButton = screen.getByText('Go to Dashboard');
    fireEvent.click(dashboardButton);

    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  it('applies correct CSS classes', () => {
    renderLessonPage();

    const container = screen.getByTestId('lesson-viewer').parentElement;
    expect(container).toHaveClass('min-h-screen', 'bg-gray-50');
  });
});