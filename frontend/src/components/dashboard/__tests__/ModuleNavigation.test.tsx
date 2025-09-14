import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ModuleNavigation } from '../ModuleNavigation';
import { mockModules, mockUserProgress } from '../../../test/mocks';

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('ModuleNavigation', () => {
  it('renders all modules with correct information', () => {
    renderWithRouter(<ModuleNavigation modules={mockModules} userProgress={mockUserProgress} />);
    
    // Check if all module names are displayed
    expect(screen.getByText('Flask Basics')).toBeInTheDocument();
    expect(screen.getByText('FastAPI Basics')).toBeInTheDocument();
    expect(screen.getByText('PostgreSQL Basics')).toBeInTheDocument();
    
    // Check if descriptions are displayed
    expect(screen.getByText('Learn the fundamentals of Flask web framework')).toBeInTheDocument();
    expect(screen.getByText('Learn the fundamentals of FastAPI')).toBeInTheDocument();
    expect(screen.getByText('Learn database fundamentals with PostgreSQL')).toBeInTheDocument();
  });

  it('displays correct progress for each module', () => {
    renderWithRouter(<ModuleNavigation modules={mockModules} userProgress={mockUserProgress} />);
    
    // Flask module should show 50% progress (1 out of 2 lessons completed)
    const flaskModule = screen.getByText('Flask Basics').closest('a');
    expect(flaskModule).toContainHTML('50% complete');
    
    // FastAPI module should show 0% progress
    const fastapiModule = screen.getByText('FastAPI Basics').closest('a');
    expect(fastapiModule).toContainHTML('0% complete');
    
    // PostgreSQL module should show 0% progress
    const postgresqlModule = screen.getByText('PostgreSQL Basics').closest('a');
    expect(postgresqlModule).toContainHTML('0% complete');
  });

  it('displays correct status badges', () => {
    renderWithRouter(<ModuleNavigation modules={mockModules} userProgress={mockUserProgress} />);
    
    // Flask should show "In Progress" status
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    
    // FastAPI and PostgreSQL should show "Not Started" status
    expect(screen.getAllByText('Not Started')).toHaveLength(2);
  });

  it('shows correct lesson counts and durations', () => {
    renderWithRouter(<ModuleNavigation modules={mockModules} userProgress={mockUserProgress} />);
    
    // Flask module: 2 lessons, 120 min
    const flaskModule = screen.getByText('Flask Basics').closest('a');
    expect(flaskModule).toContainHTML('2 lessons');
    expect(flaskModule).toContainHTML('120 min');
    
    // FastAPI module: 1 lesson, 180 min
    const fastapiModule = screen.getByText('FastAPI Basics').closest('a');
    expect(fastapiModule).toContainHTML('1 lessons');
    expect(fastapiModule).toContainHTML('180 min');
  });

  it('displays difficulty levels correctly', () => {
    renderWithRouter(<ModuleNavigation modules={mockModules} userProgress={mockUserProgress} />);
    
    expect(screen.getAllByText('beginner')).toHaveLength(2); // Flask and PostgreSQL
    expect(screen.getByText('intermediate')).toBeInTheDocument(); // FastAPI
  });

  it('creates correct navigation links', () => {
    renderWithRouter(<ModuleNavigation modules={mockModules} userProgress={mockUserProgress} />);
    
    const flaskLink = screen.getByText('Flask Basics').closest('a');
    expect(flaskLink).toHaveAttribute('href', '/modules/module-1');
    
    const fastapiLink = screen.getByText('FastAPI Basics').closest('a');
    expect(fastapiLink).toHaveAttribute('href', '/modules/module-2');
    
    const postgresqlLink = screen.getByText('PostgreSQL Basics').closest('a');
    expect(postgresqlLink).toHaveAttribute('href', '/modules/module-3');
  });

  it('sorts modules by order_index', () => {
    const unsortedModules = [...mockModules].reverse(); // Reverse the order
    renderWithRouter(<ModuleNavigation modules={unsortedModules} userProgress={mockUserProgress} />);
    
    const moduleElements = screen.getAllByRole('link');
    
    // Should still be in correct order despite input being reversed
    expect(moduleElements[0]).toHaveAttribute('href', '/modules/module-1');
    expect(moduleElements[1]).toHaveAttribute('href', '/modules/module-2');
    expect(moduleElements[2]).toHaveAttribute('href', '/modules/module-3');
  });

  it('handles modules with no lessons gracefully', () => {
    const moduleWithNoLessons = [{
      ...mockModules[0],
      lessons: []
    }];
    
    renderWithRouter(<ModuleNavigation modules={moduleWithNoLessons} userProgress={mockUserProgress} />);
    
    const moduleElement = screen.getByText('Flask Basics').closest('a');
    expect(moduleElement).toContainHTML('0 lessons');
    expect(moduleElement).toContainHTML('0% complete');
  });
});