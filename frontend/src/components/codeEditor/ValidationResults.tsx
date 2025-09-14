import React from 'react';
import { ExerciseValidationResult, TestResult } from '../../types/codeEditor';

interface ValidationResultsProps {
  result: ExerciseValidationResult;
}

const ValidationResults: React.FC<ValidationResultsProps> = ({ result }) => {
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 90) return 'bg-green-50 border-green-200';
    if (score >= 70) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const renderTestResult = (test: TestResult, index: number) => (
    <div
      key={index}
      className={`p-3 rounded-md border ${
        test.passed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          {test.passed ? (
            <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ) : (
            <svg className="h-4 w-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          )}
          <span className={`text-sm font-medium ${test.passed ? 'text-green-800' : 'text-red-800'}`}>
            {test.name}
          </span>
        </div>
        <span className={`text-xs px-2 py-1 rounded ${test.passed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {test.passed ? 'PASS' : 'FAIL'}
        </span>
      </div>

      {!test.passed && (
        <div className="space-y-2 text-sm">
          {test.error && (
            <div>
              <span className="font-medium text-red-700">Error:</span>
              <pre className="mt-1 text-red-600 font-mono text-xs bg-red-100 p-2 rounded overflow-x-auto">
                {test.error}
              </pre>
            </div>
          )}
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="font-medium text-gray-700">Expected:</span>
              <pre className="mt-1 text-gray-600 font-mono text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                {JSON.stringify(test.expected, null, 2)}
              </pre>
            </div>
            <div>
              <span className="font-medium text-gray-700">Actual:</span>
              <pre className="mt-1 text-gray-600 font-mono text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                {JSON.stringify(test.actual, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="border-t border-gray-200">
      {/* Validation Header */}
      <div className={`px-4 py-3 ${result.success ? 'bg-green-50' : 'bg-red-50'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {result.success ? (
              <svg className="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : (
              <svg className="h-5 w-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
            <span className={`text-sm font-medium ${result.success ? 'text-green-800' : 'text-red-800'}`}>
              {result.success ? 'All Tests Passed!' : 'Some Tests Failed'}
            </span>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              {result.passed_tests}/{result.total_tests} tests passed
            </span>
            <div className={`px-3 py-1 rounded-full border ${getScoreBgColor(result.score)}`}>
              <span className={`text-sm font-medium ${getScoreColor(result.score)}`}>
                Score: {result.score}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Validation Content */}
      <div className="p-4">
        {/* Feedback */}
        {result.feedback && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Feedback:</h4>
            <div className={`p-3 rounded-md ${result.success ? 'bg-blue-50 text-blue-800' : 'bg-orange-50 text-orange-800'}`}>
              {result.feedback}
            </div>
          </div>
        )}

        {/* Test Results */}
        {result.test_results.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Test Results:</h4>
            <div className="space-y-3">
              {result.test_results.map((test, index) => renderTestResult(test, index))}
            </div>
          </div>
        )}

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
            <span>Progress</span>
            <span>{result.passed_tests}/{result.total_tests}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${
                result.success ? 'bg-green-600' : 'bg-red-600'
              }`}
              style={{ width: `${(result.passed_tests / result.total_tests) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ValidationResults;