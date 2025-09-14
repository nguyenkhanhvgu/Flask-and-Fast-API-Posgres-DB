import React from 'react';
import { LearningModule, UserProgress } from '../../types/progress';

interface ProgressChartProps {
  modules: LearningModule[];
  userProgress: Record<string, UserProgress>;
}

export const ProgressChart: React.FC<ProgressChartProps> = ({ modules, userProgress }) => {
  const getModuleProgress = (module: LearningModule) => {
    const totalLessons = module.lessons.length;
    if (totalLessons === 0) return 0;

    const completedLessons = module.lessons.filter(lesson => 
      userProgress[lesson.id]?.status === 'completed'
    ).length;

    return Math.round((completedLessons / totalLessons) * 100);
  };

  const getTechnologyColor = (technology: string) => {
    switch (technology) {
      case 'flask':
        return 'bg-green-500';
      case 'fastapi':
        return 'bg-blue-500';
      case 'postgresql':
        return 'bg-purple-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getTechnologyIcon = (technology: string) => {
    switch (technology) {
      case 'flask':
        return 'F';
      case 'fastapi':
        return 'API';
      case 'postgresql':
        return 'DB';
      default:
        return '?';
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Progress by Technology</h3>
      <div className="space-y-4">
        {modules.map((module) => {
          const progress = getModuleProgress(module);
          return (
            <div key={module.id} className="flex items-center space-x-4">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white text-sm font-bold ${getTechnologyColor(module.technology)}`}>
                {getTechnologyIcon(module.technology)}
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium text-gray-900">{module.name}</span>
                  <span className="text-sm text-gray-500">{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${getTechnologyColor(module.technology)}`}
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>{module.lessons.filter(l => userProgress[l.id]?.status === 'completed').length} / {module.lessons.length} lessons</span>
                  <span>{module.difficulty_level}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};