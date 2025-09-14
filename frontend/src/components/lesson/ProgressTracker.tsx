import React, { useState } from 'react';
import { Lesson, UserProgress } from '../../types/progress';

interface ProgressTrackerProps {
  lesson: Lesson;
  userProgress: UserProgress | null;
  timeSpent: number;
  onComplete: () => void;
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  lesson,
  userProgress,
  timeSpent,
  onComplete,
}) => {
  const [isCompleting, setIsCompleting] = useState(false);

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = (): number => {
    if (!userProgress) return 0;
    
    switch (userProgress.status) {
      case 'completed':
        return 100;
      case 'in_progress':
        return 50;
      default:
        return 0;
    }
  };

  const handleMarkComplete = async () => {
    setIsCompleting(true);
    try {
      await onComplete();
    } catch (error) {
      console.error('Error marking lesson complete:', error);
    } finally {
      setIsCompleting(false);
    }
  };

  const isCompleted = userProgress?.status === 'completed';
  const progressPercentage = getProgressPercentage();

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4">
          {/* Progress Circle */}
          <div className="relative w-12 h-12">
            <svg className="w-12 h-12 transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-gray-200"
                stroke="currentColor"
                strokeWidth="3"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className={isCompleted ? 'text-green-500' : 'text-blue-500'}
                stroke="currentColor"
                strokeWidth="3"
                strokeDasharray={`${progressPercentage}, 100`}
                strokeLinecap="round"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              {isCompleted ? (
                <svg className="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : (
                <span className="text-xs font-semibold text-gray-600">
                  {progressPercentage}%
                </span>
              )}
            </div>
          </div>

          {/* Progress Info */}
          <div>
            <div className="flex items-center space-x-2">
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  isCompleted
                    ? 'bg-green-100 text-green-800'
                    : userProgress?.status === 'in_progress'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {isCompleted ? 'Completed' : userProgress?.status === 'in_progress' ? 'In Progress' : 'Not Started'}
              </span>
              {userProgress?.completion_date && (
                <span className="text-xs text-gray-500">
                  Completed on {new Date(userProgress.completion_date).toLocaleDateString()}
                </span>
              )}
            </div>
            <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
              <span>Time: {formatTime(timeSpent)}</span>
              {lesson.estimated_duration && (
                <span>Est. {lesson.estimated_duration} min</span>
              )}
              {userProgress?.score !== undefined && userProgress.score > 0 && (
                <span>Score: {userProgress.score}%</span>
              )}
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div>
          {!isCompleted ? (
            <button
              onClick={handleMarkComplete}
              disabled={isCompleting}
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white ${
                isCompleting
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
              }`}
            >
              {isCompleting ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Completing...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Mark Complete
                </>
              )}
            </button>
          ) : (
            <div className="inline-flex items-center px-4 py-2 text-sm font-medium text-green-700 bg-green-100 rounded-md">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              Completed
            </div>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${
            isCompleted ? 'bg-green-500' : 'bg-blue-500'
          }`}
          style={{ width: `${progressPercentage}%` }}
        />
      </div>

      {/* Additional Stats */}
      {userProgress && (
        <div className="flex justify-between items-center mt-3 text-xs text-gray-500">
          <span>
            {userProgress.attempts > 0 && `Attempts: ${userProgress.attempts}`}
          </span>
          <span>
            Total time: {formatTime(userProgress.time_spent)}
          </span>
        </div>
      )}
    </div>
  );
};

export default ProgressTracker;