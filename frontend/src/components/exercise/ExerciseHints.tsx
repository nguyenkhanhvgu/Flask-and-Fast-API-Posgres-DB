import React, { useState, useEffect } from 'react';
import { apiClient } from '../../services/api';

interface ExerciseHintsProps {
  exerciseId: string;
  hints: string[];
  attempts: number;
}

const ExerciseHints: React.FC<ExerciseHintsProps> = ({
  exerciseId,
  hints,
  attempts,
}) => {
  const [availableHints, setAvailableHints] = useState<string[]>([]);
  const [revealedHints, setRevealedHints] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadHints();
  }, [exerciseId]);

  useEffect(() => {
    // Progressive hint revelation based on attempts
    const hintsToReveal = Math.min(Math.floor(attempts / 2), availableHints.length);
    setRevealedHints(hintsToReveal);
  }, [attempts, availableHints.length]);

  const loadHints = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.getExerciseHints(exerciseId);
      // Handle both direct array response and object with hints property
      const hintsData = Array.isArray(response) ? response : (response?.hints || hints);
      setAvailableHints(hintsData);
    } catch (error) {
      console.error('Failed to load hints:', error);
      // Fallback to provided hints
      setAvailableHints(hints);
    } finally {
      setIsLoading(false);
    }
  };

  const revealNextHint = () => {
    if (revealedHints < availableHints.length) {
      setRevealedHints(prev => prev + 1);
    }
  };

  const getHintIcon = (index: number) => {
    if (index === 0) {
      return (
        <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
        </svg>
      );
    } else if (index === 1) {
      return (
        <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
        </svg>
      );
    } else {
      return (
        <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
        </svg>
      );
    }
  };

  const getHintLevel = (index: number) => {
    if (index === 0) return 'Basic Hint';
    if (index === 1) return 'Detailed Hint';
    return 'Solution Approach';
  };

  if (isLoading) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <div className="flex items-center">
          <svg className="animate-spin h-5 w-5 text-yellow-500 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-yellow-700">Loading hints...</span>
        </div>
      </div>
    );
  }

  if (availableHints.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
        <p className="text-gray-600 text-center">No hints available for this exercise.</p>
      </div>
    );
  }

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-semibold text-yellow-800 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
          </svg>
          Hints & Help
        </h4>
        <span className="text-sm text-yellow-600">
          {revealedHints}/{availableHints.length} hints revealed
        </span>
      </div>

      {/* Progressive Hint System Info */}
      <div className="bg-yellow-100 rounded-md p-3 mb-4">
        <p className="text-sm text-yellow-700">
          💡 Hints are revealed progressively as you make attempts. 
          {attempts < 2 && ' Try submitting your solution to unlock more hints!'}
        </p>
      </div>

      {/* Revealed Hints */}
      <div className="space-y-3">
        {availableHints.slice(0, revealedHints).map((hint, index) => (
          <div
            key={index}
            className="bg-white border border-yellow-200 rounded-md p-3 shadow-sm"
          >
            <div className="flex items-start">
              <div className="flex-shrink-0 mr-3 mt-0.5">
                {getHintIcon(index)}
              </div>
              <div className="flex-1">
                <div className="flex items-center mb-1">
                  <span className="text-sm font-medium text-gray-700">
                    {getHintLevel(index)}
                  </span>
                  <span className="ml-2 text-xs text-gray-500">
                    Hint {index + 1}
                  </span>
                </div>
                <p className="text-gray-800">{hint}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Next Hint Button */}
      {revealedHints < availableHints.length && (
        <div className="mt-4 text-center">
          {attempts >= (revealedHints + 1) * 2 ? (
            <button
              onClick={revealNextHint}
              className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Reveal Next Hint ({revealedHints + 1}/{availableHints.length})
            </button>
          ) : (
            <div className="text-sm text-yellow-600">
              Make {(revealedHints + 1) * 2 - attempts} more attempt{(revealedHints + 1) * 2 - attempts !== 1 ? 's' : ''} to unlock the next hint
            </div>
          )}
        </div>
      )}

      {/* All Hints Revealed */}
      {revealedHints === availableHints.length && availableHints.length > 0 && (
        <div className="mt-4 p-3 bg-green-100 border border-green-200 rounded-md">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="text-sm font-medium text-green-700">
              All hints revealed! You have all the guidance needed to complete this exercise.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExerciseHints;