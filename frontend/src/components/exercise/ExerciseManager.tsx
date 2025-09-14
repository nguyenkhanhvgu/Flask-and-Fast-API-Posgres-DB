import React, { useState, useEffect } from 'react';
import { Exercise } from '../../types/progress';
import { ExerciseValidationResult } from '../../types/codeEditor';
import { apiClient } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { useProgress } from '../../contexts/ProgressContext';
import ExerciseDisplay from './ExerciseDisplay';

interface ExerciseManagerProps {
  lessonId: string;
  exercises: Exercise[];
  onExerciseComplete?: (exerciseId: string, result: ExerciseValidationResult) => void;
}

const ExerciseManager: React.FC<ExerciseManagerProps> = ({
  lessonId,
  exercises,
  onExerciseComplete,
}) => {
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);
  const [completedExercises, setCompletedExercises] = useState<Set<string>>(new Set());
  const [exerciseScores, setExerciseScores] = useState<Record<string, number>>({});
  const [isLoading, setIsLoading] = useState(false);

  const { user } = useAuth();
  const { getUserProgress } = useProgress();

  useEffect(() => {
    loadExerciseProgress();
  }, [lessonId, user]);

  const loadExerciseProgress = async () => {
    if (!user) return;

    try {
      setIsLoading(true);
      // Load user progress for exercises in this lesson
      const progress = await apiClient.getUserProgress(user.id);
      
      // Filter progress for exercises in this lesson
      const lessonExerciseIds = exercises.map(ex => ex.id);
      const exerciseProgress = progress.filter((p: any) => 
        lessonExerciseIds.includes(p.exercise_id) && p.status === 'completed'
      );

      const completed = new Set(exerciseProgress.map((p: any) => p.exercise_id));
      const scores: Record<string, number> = {};
      
      exerciseProgress.forEach((p: any) => {
        scores[p.exercise_id] = p.score || 0;
      });

      setCompletedExercises(completed);
      setExerciseScores(scores);
    } catch (error) {
      console.error('Failed to load exercise progress:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExerciseSelect = (exercise: Exercise) => {
    setSelectedExercise(exercise);
  };

  const handleExerciseComplete = (result: ExerciseValidationResult) => {
    if (!selectedExercise) return;

    // Update local state
    setCompletedExercises(prev => new Set([...prev, selectedExercise.id]));
    setExerciseScores(prev => ({
      ...prev,
      [selectedExercise.id]: result.score,
    }));

    // Notify parent component
    onExerciseComplete?.(selectedExercise.id, result);
  };

  const handleCloseExercise = () => {
    setSelectedExercise(null);
  };

  const getExerciseStatusIcon = (exercise: Exercise) => {
    if (completedExercises.has(exercise.id)) {
      return (
        <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      );
    }
    return (
      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    );
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCompletionRate = () => {
    if (exercises.length === 0) return 0;
    return Math.round((completedExercises.size / exercises.length) * 100);
  };

  const getTotalScore = () => {
    return Object.values(exerciseScores).reduce((sum, score) => sum + score, 0);
  };

  const getMaxPossibleScore = () => {
    return exercises.reduce((sum, exercise) => sum + exercise.points, 0);
  };

  if (selectedExercise) {
    return (
      <ExerciseDisplay
        exercise={selectedExercise}
        onComplete={handleExerciseComplete}
        onClose={handleCloseExercise}
      />
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6">
        <h2 className="text-2xl font-bold mb-2">Exercises</h2>
        <p className="text-purple-100 mb-4">
          Practice what you've learned with these hands-on coding exercises
        </p>
        
        {/* Progress Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white bg-opacity-20 rounded-lg p-3">
            <div className="text-sm text-purple-100">Completion Rate</div>
            <div className="text-2xl font-bold">{getCompletionRate()}%</div>
            <div className="text-sm text-purple-100">
              {completedExercises.size}/{exercises.length} exercises
            </div>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-3">
            <div className="text-sm text-purple-100">Total Score</div>
            <div className="text-2xl font-bold">{getTotalScore()}</div>
            <div className="text-sm text-purple-100">
              out of {getMaxPossibleScore()} points
            </div>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-3">
            <div className="text-sm text-purple-100">Average Score</div>
            <div className="text-2xl font-bold">
              {completedExercises.size > 0 
                ? Math.round(getTotalScore() / completedExercises.size) 
                : 0}
            </div>
            <div className="text-sm text-purple-100">points per exercise</div>
          </div>
        </div>
      </div>

      {/* Exercise List */}
      <div className="p-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
            <span className="ml-2 text-gray-600">Loading exercises...</span>
          </div>
        ) : exercises.length === 0 ? (
          <div className="text-center py-8">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Exercises Available</h3>
            <p className="text-gray-600">
              There are no exercises for this lesson yet. Check back later!
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {exercises.map((exercise, index) => (
              <div
                key={exercise.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleExerciseSelect(exercise)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className="text-sm font-medium text-gray-500 mr-2">
                        Exercise {index + 1}
                      </span>
                      {getExerciseStatusIcon(exercise)}
                      {completedExercises.has(exercise.id) && (
                        <span className="ml-2 text-sm text-green-600 font-medium">
                          Completed ({exerciseScores[exercise.id]} pts)
                        </span>
                      )}
                    </div>
                    
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {exercise.title}
                    </h3>
                    
                    <p className="text-gray-600 mb-3 line-clamp-2">
                      {exercise.description}
                    </p>
                    
                    <div className="flex items-center space-x-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(exercise.difficulty)}`}>
                        {exercise.difficulty}
                      </span>
                      <span className="text-sm text-gray-500">
                        {exercise.points} points
                      </span>
                      <span className="text-sm text-gray-500">
                        {exercise.exercise_type}
                      </span>
                    </div>
                  </div>
                  
                  <div className="ml-4 flex-shrink-0">
                    <button
                      className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                        completedExercises.has(exercise.id)
                          ? 'bg-green-100 text-green-700 hover:bg-green-200'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                      }`}
                    >
                      {completedExercises.has(exercise.id) ? 'Review' : 'Start Exercise'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ExerciseManager;