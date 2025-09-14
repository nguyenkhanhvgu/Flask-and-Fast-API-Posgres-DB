import React from 'react';
import { LearningModule, UserProgress } from '../../types/progress';

interface ProgressStatisticsProps {
  modules: LearningModule[];
  userProgress: Record<string, UserProgress>;
}

export const ProgressStatistics: React.FC<ProgressStatisticsProps> = ({ modules, userProgress }) => {
  const getStatistics = () => {
    const totalLessons = modules.reduce((acc, module) => acc + module.lessons.length, 0);
    const totalExercises = modules.reduce((acc, module) => 
      acc + module.lessons.reduce((lessonAcc, lesson) => lessonAcc + lesson.exercises.length, 0), 0
    );
    
    const completedLessons = Object.values(userProgress).filter(p => p.status === 'completed').length;
    const inProgressLessons = Object.values(userProgress).filter(p => p.status === 'in_progress').length;
    
    const totalTimeSpent = Object.values(userProgress).reduce((acc, p) => acc + p.time_spent, 0);
    const averageScore = Object.values(userProgress).length > 0 
      ? Math.round(Object.values(userProgress).reduce((acc, p) => acc + p.score, 0) / Object.values(userProgress).length)
      : 0;

    const overallProgress = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;

    // Technology-specific progress
    const techProgress = modules.reduce((acc, module) => {
      const moduleCompletedLessons = module.lessons.filter(lesson => 
        userProgress[lesson.id]?.status === 'completed'
      ).length;
      const moduleProgress = module.lessons.length > 0 
        ? Math.round((moduleCompletedLessons / module.lessons.length) * 100) 
        : 0;

      if (!acc[module.technology]) {
        acc[module.technology] = { completed: 0, total: 0, progress: 0 };
      }
      acc[module.technology].completed += moduleCompletedLessons;
      acc[module.technology].total += module.lessons.length;
      acc[module.technology].progress = acc[module.technology].total > 0 
        ? Math.round((acc[module.technology].completed / acc[module.technology].total) * 100)
        : 0;

      return acc;
    }, {} as Record<string, { completed: number; total: number; progress: number }>);

    return {
      totalLessons,
      totalExercises,
      completedLessons,
      inProgressLessons,
      totalTimeSpent,
      averageScore,
      overallProgress,
      techProgress
    };
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const getTechnologyColor = (technology: string) => {
    switch (technology) {
      case 'flask':
        return 'text-green-600 bg-green-100';
      case 'fastapi':
        return 'text-blue-600 bg-blue-100';
      case 'postgresql':
        return 'text-purple-600 bg-purple-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const stats = getStatistics();

  return (
    <div className="space-y-6">
      {/* Overall Statistics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-indigo-500 rounded-md flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2-2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Overall Progress</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.overallProgress}%</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Completed</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.completedLessons}/{stats.totalLessons}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Time Spent</dt>
                  <dd className="text-lg font-medium text-gray-900">{formatTime(stats.totalTimeSpent)}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                  </svg>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Avg Score</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.averageScore}%</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Technology Progress */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Progress by Technology</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {Object.entries(stats.techProgress).map(([tech, data]) => (
            <div key={tech} className="text-center">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getTechnologyColor(tech)} mb-2`}>
                {tech.toUpperCase()}
              </div>
              <div className="text-2xl font-bold text-gray-900">{data.progress}%</div>
              <div className="text-sm text-gray-500">{data.completed}/{data.total} lessons</div>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    tech === 'flask' ? 'bg-green-500' :
                    tech === 'fastapi' ? 'bg-blue-500' :
                    'bg-purple-500'
                  }`}
                  style={{ width: `${data.progress}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};