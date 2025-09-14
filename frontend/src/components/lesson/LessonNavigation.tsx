import React, { useState, useEffect } from 'react';
import { LearningModule, Lesson } from '../../types/progress';
import { apiClient } from '../../services/api';

interface LessonNavigationProps {
  currentLessonId: string;
  moduleId: string;
  onLessonChange: (lessonId: string) => void;
}

const LessonNavigation: React.FC<LessonNavigationProps> = ({
  currentLessonId,
  moduleId,
  onLessonChange,
}) => {
  const [module, setModule] = useState<LearningModule | null>(null);
  const [currentLessonIndex, setCurrentLessonIndex] = useState(-1);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadModule();
  }, [moduleId]);

  useEffect(() => {
    if (module) {
      const index = module.lessons.findIndex(lesson => lesson.id === currentLessonId);
      setCurrentLessonIndex(index);
    }
  }, [module, currentLessonId]);

  const loadModule = async () => {
    try {
      setIsLoading(true);
      const moduleData = await apiClient.getModule(moduleId);
      // Sort lessons by order_index
      moduleData.lessons.sort((a: Lesson, b: Lesson) => a.order_index - b.order_index);
      setModule(moduleData);
    } catch (err) {
      console.error('Error loading module:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading || !module || currentLessonIndex === -1) {
    return null;
  }

  const previousLesson = currentLessonIndex > 0 ? module.lessons[currentLessonIndex - 1] : null;
  const nextLesson = currentLessonIndex < module.lessons.length - 1 ? module.lessons[currentLessonIndex + 1] : null;

  return (
    <div className="border-t border-gray-200 pt-6">
      <div className="flex justify-between items-center">
        {/* Previous Lesson */}
        <div className="flex-1">
          {previousLesson ? (
            <button
              onClick={() => onLessonChange(previousLesson.id)}
              className="group flex items-center text-left p-4 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors duration-200 max-w-md"
            >
              <div className="flex-shrink-0 mr-3">
                <svg
                  className="w-5 h-5 text-gray-400 group-hover:text-blue-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </div>
              <div className="min-w-0">
                <p className="text-sm text-gray-500 group-hover:text-blue-600">Previous</p>
                <p className="font-medium text-gray-900 group-hover:text-blue-700 truncate">
                  {previousLesson.title}
                </p>
              </div>
            </button>
          ) : (
            <div></div>
          )}
        </div>

        {/* Lesson Progress Indicator */}
        <div className="flex-shrink-0 mx-8">
          <div className="text-center">
            <p className="text-sm text-gray-500 mb-2">
              Lesson {currentLessonIndex + 1} of {module.lessons.length}
            </p>
            <div className="flex space-x-1">
              {module.lessons.map((_, index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full ${
                    index === currentLessonIndex
                      ? 'bg-blue-500'
                      : index < currentLessonIndex
                      ? 'bg-green-500'
                      : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Next Lesson */}
        <div className="flex-1 flex justify-end">
          {nextLesson ? (
            <button
              onClick={() => onLessonChange(nextLesson.id)}
              className="group flex items-center text-right p-4 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors duration-200 max-w-md"
            >
              <div className="min-w-0">
                <p className="text-sm text-gray-500 group-hover:text-blue-600">Next</p>
                <p className="font-medium text-gray-900 group-hover:text-blue-700 truncate">
                  {nextLesson.title}
                </p>
              </div>
              <div className="flex-shrink-0 ml-3">
                <svg
                  className="w-5 h-5 text-gray-400 group-hover:text-blue-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </button>
          ) : (
            <div className="text-center p-4">
              <div className="inline-flex items-center px-4 py-2 bg-green-100 text-green-800 rounded-lg">
                <svg
                  className="w-5 h-5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Module Complete!
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Module Navigation */}
      <div className="mt-6 pt-4 border-t border-gray-100">
        <div className="text-center">
          <p className="text-sm text-gray-500 mb-2">
            Module: <span className="font-medium text-gray-700">{module.name}</span>
          </p>
          <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
            ← Back to Module Overview
          </button>
        </div>
      </div>
    </div>
  );
};

export default LessonNavigation;