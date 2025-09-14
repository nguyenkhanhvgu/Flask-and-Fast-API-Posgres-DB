import React, { useState, useEffect } from 'react';
import { Exercise, UserProgress } from '../../types/progress';
import { ExerciseValidationResult } from '../../types/codeEditor';
import { CodeEditor } from '../codeEditor';
import { apiClient } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { useProgress } from '../../contexts/ProgressContext';
import ExerciseHints from './ExerciseHints';
import ExerciseProgress from './ExerciseProgress';

interface ExerciseDisplayProps {
  exercise: Exercise;
  onComplete?: (result: ExerciseValidationResult) => void;
  onClose?: () => void;
}

const ExerciseDisplay: React.FC<ExerciseDisplayProps> = ({
  exercise,
  onComplete,
  onClose,
}) => {
  const [code, setCode] = useState(exercise.starter_code || '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationResult, setValidationResult] = useState<ExerciseValidationResult | null>(null);
  const [showHints, setShowHints] = useState(false);
  const [attempts, setAttempts] = useState(0);
  const [startTime] = useState(Date.now());
  const [timeSpent, setTimeSpent] = useState(0);

  const { user } = useAuth();
  const { submitExercise } = useProgress();

  useEffect(() => {
    // Track time spent on exercise
    const interval = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  const handleCodeChange = (newCode: string) => {
    setCode(newCode);
  };

  const handleSubmit = async () => {
    if (!user || !code.trim()) return;

    setIsSubmitting(true);
    setAttempts(prev => prev + 1);

    try {
      const result = await apiClient.validateExercise(exercise.id, code);
      setValidationResult(result);

      if (result.success) {
        // Submit exercise completion
        await submitExercise(exercise.id, code);
        onComplete?.(result);
      }
    } catch (error) {
      console.error('Error submitting exercise:', error);
      setValidationResult({
        success: false,
        passed_tests: 0,
        total_tests: 0,
        test_results: [],
        score: 0,
        feedback: 'Failed to validate exercise. Please try again.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setCode(exercise.starter_code || '');
    setValidationResult(null);
  };

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Exercise Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold mb-2">{exercise.title}</h2>
            <p className="text-blue-100 mb-4">{exercise.description}</p>
            <div className="flex items-center space-x-4 text-sm">
              <span className="bg-white bg-opacity-20 px-2 py-1 rounded">
                {exercise.difficulty}
              </span>
              <span className="bg-white bg-opacity-20 px-2 py-1 rounded">
                {exercise.points} points
              </span>
              <span className="bg-white bg-opacity-20 px-2 py-1 rounded">
                Time: {formatTime(timeSpent)}
              </span>
              <span className="bg-white bg-opacity-20 px-2 py-1 rounded">
                Attempts: {attempts}
              </span>
            </div>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      <div className="p-6">
        {/* Exercise Progress */}
        <ExerciseProgress
          validationResult={validationResult}
          attempts={attempts}
          timeSpent={timeSpent}
          maxPoints={exercise.points}
        />

        {/* Code Editor */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Your Solution</h3>
            <div className="flex space-x-2">
              <button
                onClick={() => setShowHints(!showHints)}
                className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                {showHints ? 'Hide Hints' : 'Show Hints'}
              </button>
              <button
                onClick={handleReset}
                className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Reset Code
              </button>
            </div>
          </div>

          <CodeEditor
            initialCode={code}
            language="python"
            height="400px"
            exerciseId={exercise.id}
            onCodeChange={handleCodeChange}
          />
        </div>

        {/* Hints Section */}
        {showHints && (
          <ExerciseHints
            exerciseId={exercise.id}
            hints={exercise.hints}
            attempts={attempts}
          />
        )}

        {/* Validation Results */}
        {validationResult && (
          <div className={`mb-6 p-4 rounded-lg ${
            validationResult.success 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-red-50 border border-red-200'
          }`}>
            <div className="flex items-center mb-2">
              {validationResult.success ? (
                <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              )}
              <h4 className={`font-semibold ${
                validationResult.success ? 'text-green-800' : 'text-red-800'
              }`}>
                {validationResult.success ? 'Exercise Completed!' : 'Tests Failed'}
              </h4>
            </div>
            
            <p className={`mb-3 ${
              validationResult.success ? 'text-green-700' : 'text-red-700'
            }`}>
              {validationResult.feedback}
            </p>

            <div className="text-sm">
              <p className={validationResult.success ? 'text-green-600' : 'text-red-600'}>
                Tests passed: {validationResult.passed_tests}/{validationResult.total_tests}
              </p>
              <p className={validationResult.success ? 'text-green-600' : 'text-red-600'}>
                Score: {validationResult.score}/{exercise.points}
              </p>
            </div>

            {/* Test Results Details */}
            {validationResult.test_results.length > 0 && (
              <div className="mt-4">
                <h5 className="font-medium text-gray-900 mb-2">Test Results:</h5>
                <div className="space-y-2">
                  {validationResult.test_results.map((test, index) => (
                    <div
                      key={index}
                      className={`p-2 rounded text-sm ${
                        test.passed 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      <div className="flex items-center">
                        {test.passed ? (
                          <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        ) : (
                          <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                          </svg>
                        )}
                        <span className="font-medium">{test.name}</span>
                      </div>
                      {!test.passed && (
                        <div className="ml-6 mt-1">
                          <p>Expected: {JSON.stringify(test.expected)}</p>
                          <p>Actual: {JSON.stringify(test.actual)}</p>
                          {test.error && <p>Error: {test.error}</p>}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSubmit}
            disabled={isSubmitting || !code.trim()}
            className={`px-6 py-3 rounded-md font-medium transition-colors ${
              isSubmitting || !code.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : validationResult?.success
                ? 'bg-green-600 hover:bg-green-700 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {isSubmitting ? (
              <div className="flex items-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Validating...
              </div>
            ) : validationResult?.success ? (
              'Completed ✓'
            ) : (
              'Submit Solution'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExerciseDisplay;