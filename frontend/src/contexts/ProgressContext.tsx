import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { ProgressState, LearningModule, UserProgress } from '../types/progress';
import { useAuth } from './AuthContext';
import apiClient from '../services/api';

interface ProgressContextType extends ProgressState {
  loadModules: () => Promise<void>;
  loadUserProgress: () => Promise<void>;
  markLessonComplete: (lessonId: string) => Promise<void>;
  submitExercise: (exerciseId: string, code: string) => Promise<void>;
  addBookmark: (contentId: string) => Promise<void>;
  removeBookmark: (contentId: string) => Promise<void>;
  refreshProgress: () => Promise<void>;
  updateLessonProgress: (lessonId: string, progressUpdate: Partial<UserProgress>) => Promise<void>;
  getUserProgress: (lessonId: string) => UserProgress | null;
}

const ProgressContext = createContext<ProgressContextType | undefined>(undefined);

type ProgressAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_MODULES'; payload: LearningModule[] }
  | { type: 'SET_USER_PROGRESS'; payload: Record<string, UserProgress> }
  | { type: 'UPDATE_LESSON_PROGRESS'; payload: UserProgress }
  | { type: 'SET_BOOKMARKS'; payload: string[] }
  | { type: 'ADD_BOOKMARK'; payload: string }
  | { type: 'REMOVE_BOOKMARK'; payload: string }
  | { type: 'CLEAR_PROGRESS' };

const progressReducer = (state: ProgressState, action: ProgressAction): ProgressState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_MODULES':
      return { ...state, modules: action.payload, isLoading: false };
    case 'SET_USER_PROGRESS':
      return { ...state, userProgress: action.payload };
    case 'UPDATE_LESSON_PROGRESS':
      return {
        ...state,
        userProgress: {
          ...state.userProgress,
          [action.payload.lesson_id]: action.payload,
        },
      };
    case 'SET_BOOKMARKS':
      return { ...state, bookmarks: action.payload };
    case 'ADD_BOOKMARK':
      return {
        ...state,
        bookmarks: [...state.bookmarks, action.payload],
      };
    case 'REMOVE_BOOKMARK':
      return {
        ...state,
        bookmarks: state.bookmarks.filter(id => id !== action.payload),
      };
    case 'CLEAR_PROGRESS':
      return {
        modules: [],
        userProgress: {},
        bookmarks: [],
        isLoading: false,
      };
    default:
      return state;
  }
};

const initialState: ProgressState = {
  modules: [],
  userProgress: {},
  bookmarks: [],
  isLoading: false,
};

interface ProgressProviderProps {
  children: ReactNode;
}

export const ProgressProvider: React.FC<ProgressProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(progressReducer, initialState);
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated && user) {
      loadModules();
      loadUserProgress();
      loadBookmarks();
    } else {
      dispatch({ type: 'CLEAR_PROGRESS' });
    }
  }, [isAuthenticated, user]);

  const loadModules = async (): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const modules = await apiClient.getModules();
      dispatch({ type: 'SET_MODULES', payload: modules });
    } catch (error) {
      console.error('Failed to load modules:', error);
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const loadUserProgress = async (): Promise<void> => {
    try {
      if (!user) return;
      
      const progressData = await apiClient.getUserProgress(user.id);
      const progressMap: Record<string, UserProgress> = {};
      
      progressData.forEach((progress: UserProgress) => {
        progressMap[progress.lesson_id] = progress;
      });
      
      dispatch({ type: 'SET_USER_PROGRESS', payload: progressMap });
    } catch (error) {
      console.error('Failed to load user progress:', error);
    }
  };

  const loadBookmarks = async (): Promise<void> => {
    try {
      if (!user) return;
      
      const bookmarks = await apiClient.getUserBookmarks(user.id);
      dispatch({ type: 'SET_BOOKMARKS', payload: bookmarks });
    } catch (error) {
      console.error('Failed to load bookmarks:', error);
    }
  };

  const markLessonComplete = async (lessonId: string): Promise<void> => {
    try {
      const progress = await apiClient.markLessonComplete(lessonId);
      dispatch({ type: 'UPDATE_LESSON_PROGRESS', payload: progress });
    } catch (error) {
      console.error('Failed to mark lesson complete:', error);
      throw error;
    }
  };

  const submitExercise = async (exerciseId: string, code: string): Promise<void> => {
    try {
      const result = await apiClient.submitExercise(exerciseId, code);
      if (result.progress) {
        dispatch({ type: 'UPDATE_LESSON_PROGRESS', payload: result.progress });
      }
    } catch (error) {
      console.error('Failed to submit exercise:', error);
      throw error;
    }
  };

  const addBookmark = async (contentId: string): Promise<void> => {
    try {
      // This would need to be implemented in the API
      // For now, just update local state
      dispatch({ type: 'ADD_BOOKMARK', payload: contentId });
    } catch (error) {
      console.error('Failed to add bookmark:', error);
      throw error;
    }
  };

  const removeBookmark = async (contentId: string): Promise<void> => {
    try {
      // This would need to be implemented in the API
      // For now, just update local state
      dispatch({ type: 'REMOVE_BOOKMARK', payload: contentId });
    } catch (error) {
      console.error('Failed to remove bookmark:', error);
      throw error;
    }
  };

  const refreshProgress = async (): Promise<void> => {
    await Promise.all([
      loadModules(),
      loadUserProgress(),
      loadBookmarks(),
    ]);
  };

  const updateLessonProgress = async (lessonId: string, progressUpdate: Partial<UserProgress>): Promise<void> => {
    try {
      const currentProgress = state.userProgress[lessonId];
      const updatedProgress: UserProgress = {
        id: currentProgress?.id || '',
        user_id: user?.id || '',
        lesson_id: lessonId,
        status: 'in_progress',
        time_spent: 0,
        score: 0,
        attempts: 0,
        ...currentProgress,
        ...progressUpdate,
      };
      
      dispatch({ type: 'UPDATE_LESSON_PROGRESS', payload: updatedProgress });
    } catch (error) {
      console.error('Failed to update lesson progress:', error);
      throw error;
    }
  };

  const getUserProgress = (lessonId: string): UserProgress | null => {
    return state.userProgress[lessonId] || null;
  };

  const value: ProgressContextType = {
    ...state,
    loadModules,
    loadUserProgress,
    markLessonComplete,
    submitExercise,
    addBookmark,
    removeBookmark,
    refreshProgress,
    updateLessonProgress,
    getUserProgress,
  };

  return <ProgressContext.Provider value={value}>{children}</ProgressContext.Provider>;
};

export const useProgress = (): ProgressContextType => {
  const context = useContext(ProgressContext);
  if (context === undefined) {
    throw new Error('useProgress must be used within a ProgressProvider');
  }
  return context;
};