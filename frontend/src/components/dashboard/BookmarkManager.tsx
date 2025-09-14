import React, { useState } from 'react';
import { LearningModule, Lesson } from '../../types/progress';
import { useProgress } from '../../contexts/ProgressContext';

interface BookmarkManagerProps {
  modules: LearningModule[];
  bookmarks: string[];
}

export const BookmarkManager: React.FC<BookmarkManagerProps> = ({ modules, bookmarks }) => {
  const { addBookmark, removeBookmark } = useProgress();
  const [isExpanded, setIsExpanded] = useState(false);

  const getBookmarkedContent = () => {
    const bookmarkedItems: Array<{ type: 'lesson'; item: Lesson; module: LearningModule }> = [];
    
    modules.forEach(module => {
      module.lessons.forEach(lesson => {
        if (bookmarks.includes(lesson.id)) {
          bookmarkedItems.push({ type: 'lesson', item: lesson, module });
        }
      });
    });

    return bookmarkedItems.sort((a, b) => a.item.title.localeCompare(b.item.title));
  };

  const handleRemoveBookmark = async (contentId: string) => {
    try {
      await removeBookmark(contentId);
    } catch (error) {
      console.error('Failed to remove bookmark:', error);
    }
  };

  const bookmarkedContent = getBookmarkedContent();

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Bookmarks ({bookmarks.length})
          </h3>
          {bookmarkedContent.length > 0 && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-sm text-indigo-600 hover:text-indigo-500 font-medium"
            >
              {isExpanded ? 'Show Less' : 'Show All'}
            </button>
          )}
        </div>

        {bookmarkedContent.length === 0 ? (
          <div className="text-center py-6">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No bookmarks yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Start bookmarking lessons and exercises to save them for later.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {bookmarkedContent.slice(0, isExpanded ? bookmarkedContent.length : 3).map(({ item, module }) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      module.technology === 'flask' ? 'bg-green-100 text-green-800' :
                      module.technology === 'fastapi' ? 'bg-blue-100 text-blue-800' :
                      'bg-purple-100 text-purple-800'
                    }`}>
                      {module.technology.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-500">{module.name}</span>
                  </div>
                  <p className="text-sm font-medium text-gray-900 mt-1 truncate">
                    {item.title}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {item.estimated_duration} min • {item.exercises.length} exercises
                  </p>
                </div>
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => window.open(`/lessons/${item.id}`, '_blank')}
                    className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
                  >
                    Open
                  </button>
                  <button
                    onClick={() => handleRemoveBookmark(item.id)}
                    className="text-red-600 hover:text-red-500 p-1"
                    title="Remove bookmark"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
            
            {!isExpanded && bookmarkedContent.length > 3 && (
              <div className="text-center pt-2">
                <button
                  onClick={() => setIsExpanded(true)}
                  className="text-sm text-indigo-600 hover:text-indigo-500 font-medium"
                >
                  Show {bookmarkedContent.length - 3} more bookmarks
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};