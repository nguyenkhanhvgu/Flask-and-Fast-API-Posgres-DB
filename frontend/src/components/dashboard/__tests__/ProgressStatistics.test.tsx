import { render, screen } from '@testing-library/react';
import { ProgressStatistics } from '../ProgressStatistics';
import { mockModules, mockUserProgress } from '../../../test/mocks';

describe('ProgressStatistics', () => {
  it('renders overall progress statistics correctly', () => {
    render(<ProgressStatistics modules={mockModules} userProgress={mockUserProgress} />);
    
    // Check if overall progress is calculated correctly
    // 1 completed lesson out of 4 total lessons = 25%
    expect(screen.getByText('25%')).toBeInTheDocument();
    
    // Check completed lessons count
    expect(screen.getByText('1/4')).toBeInTheDocument();
    
    // Check time spent formatting (1800 + 900 = 2700 seconds = 45 minutes)
    expect(screen.getByText('45m')).toBeInTheDocument();
    
    // Check average score (85% from one completed lesson, 0% from in-progress = 43% average)
    expect(screen.getByText('43%')).toBeInTheDocument();
  });

  it('displays technology-specific progress correctly', () => {
    render(<ProgressStatistics modules={mockModules} userProgress={mockUserProgress} />);
    
    // Flask should show 50% progress (1 out of 2 lessons completed)
    const flaskSection = screen.getByText('FLASK').closest('div')?.parentElement;
    expect(flaskSection).toContainHTML('50%');
    expect(flaskSection).toContainHTML('1/2 lessons');
    
    // FastAPI should show 0% progress (0 out of 1 lessons completed)
    const fastapiSection = screen.getByText('FASTAPI').closest('div')?.parentElement;
    expect(fastapiSection).toContainHTML('0%');
    expect(fastapiSection).toContainHTML('0/1 lessons');
    
    // PostgreSQL should show 0% progress (0 out of 1 lessons completed)
    const postgresqlSection = screen.getByText('POSTGRESQL').closest('div')?.parentElement;
    expect(postgresqlSection).toContainHTML('0%');
    expect(postgresqlSection).toContainHTML('0/1 lessons');
  });

  it('handles empty progress data gracefully', () => {
    render(<ProgressStatistics modules={mockModules} userProgress={{}} />);
    
    // Should show 0% overall progress - use getAllByText since there are multiple 0% elements
    expect(screen.getAllByText('0%')).toHaveLength(5); // Overall + 3 technologies + avg score
    
    // Should show 0 completed lessons
    expect(screen.getByText('0/4')).toBeInTheDocument();
    
    // Should show 0 time spent
    expect(screen.getByText('0m')).toBeInTheDocument();
  });

  it('formats time correctly for hours and minutes', () => {
    const progressWithLongTime = {
      'lesson-1': {
        ...mockUserProgress['lesson-1'],
        time_spent: 7200 // 2 hours
      }
    };
    
    render(<ProgressStatistics modules={mockModules} userProgress={progressWithLongTime} />);
    
    expect(screen.getByText('2h 0m')).toBeInTheDocument();
  });

  it('renders all required statistics cards', () => {
    render(<ProgressStatistics modules={mockModules} userProgress={mockUserProgress} />);
    
    expect(screen.getByText('Overall Progress')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('Time Spent')).toBeInTheDocument();
    expect(screen.getByText('Avg Score')).toBeInTheDocument();
  });
});