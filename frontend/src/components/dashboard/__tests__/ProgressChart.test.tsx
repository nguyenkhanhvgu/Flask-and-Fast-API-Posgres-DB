import { render, screen } from '@testing-library/react';
import { ProgressChart } from '../ProgressChart';
import { mockModules, mockUserProgress } from '../../../test/mocks';

describe('ProgressChart', () => {
  it('renders progress chart with correct title', () => {
    render(<ProgressChart modules={mockModules} userProgress={mockUserProgress} />);
    
    expect(screen.getByText('Progress by Technology')).toBeInTheDocument();
  });

  it('displays all modules with correct progress', () => {
    render(<ProgressChart modules={mockModules} userProgress={mockUserProgress} />);
    
    // Check if all module names are displayed
    expect(screen.getByText('Flask Basics')).toBeInTheDocument();
    expect(screen.getByText('FastAPI Basics')).toBeInTheDocument();
    expect(screen.getByText('PostgreSQL Basics')).toBeInTheDocument();
  });

  it('calculates and displays correct progress percentages', () => {
    render(<ProgressChart modules={mockModules} userProgress={mockUserProgress} />);
    
    // Flask: 1 out of 2 lessons completed = 50%
    const flaskSection = screen.getByText('Flask Basics').closest('div');
    expect(flaskSection).toContainHTML('50%');
    
    // FastAPI: 0 out of 1 lessons completed = 0%
    const fastapiSection = screen.getByText('FastAPI Basics').closest('div');
    expect(fastapiSection).toContainHTML('0%');
    
    // PostgreSQL: 0 out of 1 lessons completed = 0%
    const postgresqlSection = screen.getByText('PostgreSQL Basics').closest('div');
    expect(postgresqlSection).toContainHTML('0%');
  });

  it('displays correct lesson completion counts', () => {
    render(<ProgressChart modules={mockModules} userProgress={mockUserProgress} />);
    
    // Flask: 1 completed out of 2 total
    const flaskSection = screen.getByText('Flask Basics').closest('div')?.parentElement;
    expect(flaskSection).toContainHTML('1 / 2 lessons');
    
    // FastAPI: 0 completed out of 1 total
    const fastapiSection = screen.getByText('FastAPI Basics').closest('div')?.parentElement;
    expect(fastapiSection).toContainHTML('0 / 1 lessons');
    
    // PostgreSQL: 0 completed out of 1 total
    const postgresqlSection = screen.getByText('PostgreSQL Basics').closest('div')?.parentElement;
    expect(postgresqlSection).toContainHTML('0 / 1 lessons');
  });

  it('displays difficulty levels correctly', () => {
    render(<ProgressChart modules={mockModules} userProgress={mockUserProgress} />);
    
    expect(screen.getAllByText('beginner')).toHaveLength(2); // Flask and PostgreSQL
    expect(screen.getByText('intermediate')).toBeInTheDocument(); // FastAPI
  });

  it('uses correct technology icons', () => {
    render(<ProgressChart modules={mockModules} userProgress={mockUserProgress} />);
    
    // Check for technology icons
    expect(screen.getByText('F')).toBeInTheDocument(); // Flask
    expect(screen.getByText('API')).toBeInTheDocument(); // FastAPI
    expect(screen.getByText('DB')).toBeInTheDocument(); // PostgreSQL
  });

  it('applies correct CSS classes for technology colors', () => {
    render(<ProgressChart modules={mockModules} userProgress={mockUserProgress} />);
    
    // Flask should have green background
    const flaskIcon = screen.getByText('F');
    expect(flaskIcon).toHaveClass('bg-green-500');
    
    // FastAPI should have blue background
    const fastapiIcon = screen.getByText('API');
    expect(fastapiIcon).toHaveClass('bg-blue-500');
    
    // PostgreSQL should have purple background
    const postgresqlIcon = screen.getByText('DB');
    expect(postgresqlIcon).toHaveClass('bg-purple-500');
  });

  it('handles modules with no lessons gracefully', () => {
    const moduleWithNoLessons = [{
      ...mockModules[0],
      lessons: []
    }];
    
    render(<ProgressChart modules={moduleWithNoLessons} userProgress={mockUserProgress} />);
    
    const moduleSection = screen.getByText('Flask Basics').closest('div')?.parentElement;
    expect(moduleSection).toContainHTML('0%');
    expect(moduleSection).toContainHTML('0 / 0 lessons');
  });

  it('handles empty user progress gracefully', () => {
    render(<ProgressChart modules={mockModules} userProgress={{}} />);
    
    // All modules should show 0% progress
    const flaskSection = screen.getByText('Flask Basics').closest('div')?.parentElement;
    expect(flaskSection).toContainHTML('0%');
    expect(flaskSection).toContainHTML('0 / 2 lessons');
    
    const fastapiSection = screen.getByText('FastAPI Basics').closest('div')?.parentElement;
    expect(fastapiSection).toContainHTML('0%');
    expect(fastapiSection).toContainHTML('0 / 1 lessons');
    
    const postgresqlSection = screen.getByText('PostgreSQL Basics').closest('div')?.parentElement;
    expect(postgresqlSection).toContainHTML('0%');
    expect(postgresqlSection).toContainHTML('0 / 1 lessons');
  });

  it('handles unknown technology gracefully', () => {
    const moduleWithUnknownTech = [{
      ...mockModules[0],
      technology: 'unknown' as any
    }];
    
    render(<ProgressChart modules={moduleWithUnknownTech} userProgress={mockUserProgress} />);
    
    // Should use default icon and color
    expect(screen.getByText('?')).toBeInTheDocument();
    const unknownIcon = screen.getByText('?');
    expect(unknownIcon).toHaveClass('bg-gray-500');
  });
});