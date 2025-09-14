import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { Lesson, UserProgress } from '../../types/progress';
import { apiClient } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { useProgress } from '../../contexts/ProgressContext';
import LessonNavigation from './LessonNavigation';
import ProgressTracker from './ProgressTracker';
import { ExerciseManager } from '../exercise';

interface LessonViewerProps {
  lessonId: string;
  moduleId: string;
}

const LessonViewer: React.FC<LessonViewerProps> = ({ lessonId, moduleId }) => {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeSpent, setTimeSpent] = useState(0);
  const [startTime] = useState(Date.now());

  const { user } = useAuth();
  const { updateLessonProgress, getUserProgress } = useProgress();

  useEffect(() => {
    loadLesson();
  }, [lessonId]);

  useEffect(() => {
    // Track time spent on lesson
    const interval = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  const loadLesson = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const lessonData = await apiClient.getLesson(lessonId);
      setLesson(lessonData);
    } catch (err) {
      setError('Failed to load lesson content');
      console.error('Error loading lesson:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const markLessonComplete = async () => {
    if (!lesson || !user) return;

    try {
      await apiClient.markLessonComplete(lesson.id);
      await updateLessonProgress(lesson.id, {
        status: 'completed',
        time_spent: timeSpent,
        completion_date: new Date().toISOString(),
      });
    } catch (err) {
      console.error('Error marking lesson complete:', err);
    }
  };

  const handleLessonComplete = () => {
    markLessonComplete();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">{error}</div>
          <button
            onClick={loadLesson}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500 text-xl">Lesson not found</div>
      </div>
    );
  }

  const userProgress = getUserProgress(lesson.id);

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Lesson Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{lesson.title}</h1>
        
        {/* Progress Tracker */}
        <ProgressTracker
          lesson={lesson}
          userProgress={userProgress}
          timeSpent={timeSpent}
          onComplete={handleLessonComplete}
        />

        {/* Learning Objectives */}
        {lesson.learning_objectives && lesson.learning_objectives.length > 0 && (
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Learning Objectives</h3>
            <ul className="list-disc list-inside text-blue-800">
              {lesson.learning_objectives.map((objective, index) => (
                <li key={index}>{objective}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Lesson Content */}
      <div className="prose prose-lg max-w-none mb-8">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight]}
          components={{
            code: ({ node, inline, className, children, ...props }) => {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <pre className={`${className} rounded-lg p-4 overflow-x-auto`}>
                  <code className={className} {...props}>
                    {children}
                  </code>
                </pre>
              ) : (
                <code className="bg-gray-100 px-1 py-0.5 rounded text-sm" {...props}>
                  {children}
                </code>
              );
            },
            blockquote: ({ children }) => (
              <blockquote className="border-l-4 border-gray-300 pl-4 italic text-gray-600">
                {children}
              </blockquote>
            ),
            table: ({ children }) => (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  {children}
                </table>
              </div>
            ),
          }}
        >
          {lesson.content}
        </ReactMarkdown>
      </div>

      {/* Exercises Section */}
      {lesson.exercises && lesson.exercises.length > 0 && (
        <div className="mb-8">
          <ExerciseManager
            lessonId={lesson.id}
            exercises={lesson.exercises}
            onExerciseComplete={(exerciseId, result) => {
              console.log('Exercise completed:', exerciseId, result);
              // Optionally update lesson progress or show completion message
            }}
          />
        </div>
      )}

      {/* Navigation */}
      <LessonNavigation
        currentLessonId={lesson.id}
        moduleId={moduleId}
        onLessonChange={(newLessonId) => {
          // This will be handled by the parent component or router
          console.log('Navigate to lesson:', newLessonId);
        }}
      />
    </div>
  );
};

export default LessonViewer;