import React from 'react';
import { ExerciseValidationResult } from '../../types/codeEditor';

interface ExerciseProgressProps {
  validationResult: ExerciseValidationResult | null;
  attempts: number;
  timeSpent: number;
  maxPoints: number;
}

const ExerciseProgress: React.FC<ExerciseProgressProps> = ({
  validationResult,
  attempts,
  timeSpent,
  maxPoints,
}) => {
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = (): number => {
    if (!validationResult) return 0;
    return Math.round((validationResult.passed_tests / validationResult.total_tests) * 100);
  };

  const getScorePercentage = (): number => {
    if (!validationResult) return 0;
    return Math.round((validationResult.score / maxPoints) * 100);
  };

  const getAttemptColor = (): string => {
    if (attempts === 0) return 'text-gray-500';
    if (attempts <= 2) return 'text-green-600';
    if (attempts <= 5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTimeColor = (): string => {
    if (timeSpent < 300) return 'text-green-600'; // Under 5 minutes
    if (timeSpent < 900) return 'text-yellow-600'; // Under 15 minutes
    return 'text-red-600'; // Over 15 minutes
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Exercise Progress</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Attempts */}
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Attempts</p>
              <p className={`text-2xl font-bold ${getAttemptColor()}`}>
                {attempts}
              </p>
            </div>
            <div className="p-2 bg-blue-100 rounded-full">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
          <div className="mt-2">
            <div className="flex items-center text-xs text-gray-500">
              {attempts === 0 && <span>No attempts yet</span>}
              {attempts > 0 && attempts <= 2 && <span>Great start!</span>}
              {attempts > 2 && attempts <= 5 && <span>Keep trying!</span>}
              {attempts > 5 && <span>Consider reviewing hints</span>}
            </div>
          </div>
        </div>

        {/* Time Spent */}
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Time Spent</p>
              <p className={`text-2xl font-bold ${getTimeColor()}`}>
                {formatTime(timeSpent)}
              </p>
            </div>
            <div className="p-2 bg-green-100 rounded-full">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div className="mt-2">
            <div className="flex items-center text-xs text-gray-500">
              {timeSpent < 300 && <span>Quick work!</span>}
              {timeSpent >= 300 && timeSpent < 900 && <span>Good pace</span>}
              {timeSpent >= 900 && <span>Take your time</span>}
            </div>
          </div>
        </div>

        {/* Test Progress */}
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tests Passed</p>
              <p className="text-2xl font-bold text-purple-600">
                {validationResult ? `${validationResult.passed_tests}/${validationResult.total_tests}` : '0/0'}
              </p>
            </div>
            <div className="p-2 bg-purple-100 rounded-full">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div className="mt-2">
            {validationResult && (
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    getProgressPercentage() === 100 ? 'bg-green-500' : 'bg-purple-500'
                  }`}
                  style={{ width: `${getProgressPercentage()}%` }}
                ></div>
              </div>
            )}
            <div className="flex items-center text-xs text-gray-500 mt-1">
              {validationResult ? `${getProgressPercentage()}% complete` : 'Not tested yet'}
            </div>
          </div>
        </div>

        {/* Score */}
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Score</p>
              <p className="text-2xl font-bold text-yellow-600">
                {validationResult ? `${validationResult.score}/${maxPoints}` : `0/${maxPoints}`}
              </p>
            </div>
            <div className="p-2 bg-yellow-100 rounded-full">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </div>
          </div>
          <div className="mt-2">
            {validationResult && (
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    getScorePercentage() === 100 ? 'bg-green-500' : 'bg-yellow-500'
                  }`}
                  style={{ width: `${getScorePercentage()}%` }}
                ></div>
              </div>
            )}
            <div className="flex items-center text-xs text-gray-500 mt-1">
              {validationResult ? `${getScorePercentage()}% of max score` : 'No score yet'}
            </div>
          </div>
        </div>
      </div>

      {/* Overall Status */}
      {validationResult && (
        <div className="mt-4 p-3 rounded-lg border-l-4 border-l-blue-500 bg-blue-50">
          <div className="flex items-center">
            <div className="flex-1">
              <h4 className="text-sm font-medium text-blue-900">
                {validationResult.success ? 'Exercise Completed Successfully!' : 'Keep Working on It!'}
              </h4>
              <p className="text-sm text-blue-700 mt-1">
                {validationResult.success 
                  ? `Congratulations! You've completed this exercise with a score of ${validationResult.score}/${maxPoints} points.`
                  : `You're making progress! ${validationResult.passed_tests} out of ${validationResult.total_tests} tests are passing.`
                }
              </p>
            </div>
            {validationResult.success && (
              <div className="ml-4">
                <svg className="w-8 h-8 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ExerciseProgress;