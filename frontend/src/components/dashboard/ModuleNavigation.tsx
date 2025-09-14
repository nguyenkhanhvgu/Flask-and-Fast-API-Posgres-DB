import React from 'react';
import { Link } from 'react-router-dom';
import { LearningModule, UserProgress } from '../../types/progress';

interface ModuleNavigationProps {
  modules: LearningModule[];
  userProgress: Record<string, UserProgress>;
}

export const ModuleNavigation: React.FC<ModuleNavigationProps> = ({ modules, userProgress }) => {
  const getModuleProgress = (module: LearningModule) => {
    const totalLessons = module.lessons.length;
    if (totalLessons === 0) return 0;

    const completedLessons = module.lessons.filter(lesson => 
      userProgress[lesson.id]?.status === 'completed'
    ).length;

    return Math.round((completedLessons / totalLessons) * 100);
  };

  const getModuleStatus = (module: LearningModule) => {
    const progress = getModuleProgress(module);
    if (progress === 0) return 'not_started';
    if (progress === 100) return 'completed';
    return 'in_progress';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'in_progress':
        return 'In Progress';
      default:
        return 'Not Started';
    }
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

  const sortedModules = [...modules].sort((a, b) => a.order_index - b.order_index);

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
          Learning Modules
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {sortedModules.map((module) => {
            const progress = getModuleProgress(module);
            const status = getModuleStatus(module);
            
            return (
              <Link
                key={module.id}
                to={`/modules/${module.id}`}
                className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500 transition-all duration-200"
              >
                <div className="flex items-start space-x-3">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-white text-sm font-bold ${getTechnologyColor(module.technology)}`}>
                    {getTechnologyIcon(module.technology)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-medium text-gray-900 truncate">{module.name}</p>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                        {getStatusText(status)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mb-3 line-clamp-2">{module.description}</p>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>{module.lessons.length} lessons</span>
                        <span>{module.estimated_duration} min</span>
                      </div>
                      
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${getTechnologyColor(module.technology)}`}
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                      
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>{progress}% complete</span>
                        <span className="capitalize">{module.difficulty_level}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
};