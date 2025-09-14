import React from 'react';
import { Link } from 'react-router-dom';
import { 
  BookOpenIcon, 
  CodeBracketIcon, 
  AcademicCapIcon,
  ClockIcon,
  StarIcon
} from '@heroicons/react/24/outline';
import { SearchResult } from '../../types/search';

interface SearchResultsProps {
  results: SearchResult[];
  totalCount: number;
  loading: boolean;
  error: string | null;
  query?: string;
  onLoadMore?: () => void;
  hasMore?: boolean;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  totalCount,
  loading,
  error,
  query,
  onLoadMore,
  hasMore = false
}) => {
  const getContentIcon = (contentType: string) => {
    switch (contentType) {
      case 'module':
        return <AcademicCapIcon className="h-5 w-5" />;
      case 'lesson':
        return <BookOpenIcon className="h-5 w-5" />;
      case 'exercise':
        return <CodeBracketIcon className="h-5 w-5" />;
      default:
        return <BookOpenIcon className="h-5 w-5" />;
    }
  };

  const getContentTypeColor = (contentType: string) => {
    switch (contentType) {
      case 'module':
        return 'bg-purple-100 text-purple-800';
      case 'lesson':
        return 'bg-blue-100 text-blue-800';
      case 'exercise':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'beginner':
        return 'bg-green-100 text-green-800';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading && results.length === 0) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, index) => (
          <div key={index} className="bg-white rounded-lg border border-gray-200 p-6 animate-pulse">
            <div className="flex items-start space-x-4">
              <div className="w-10 h-10 bg-gray-200 rounded-lg"></div>
              <div className="flex-1 space-y-3">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-full"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                <div className="flex space-x-2">
                  <div className="h-6 bg-gray-200 rounded w-16"></div>
                  <div className="h-6 bg-gray-200 rounded w-20"></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <div className="text-red-600 mb-2">Search Error</div>
        <div className="text-red-500 text-sm">{error}</div>
      </div>
    );
  }

  if (results.length === 0 && !loading) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
        <BookOpenIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
        <p className="text-gray-500">
          {query 
            ? `No content found for "${query}". Try adjusting your search terms or filters.`
            : "No content matches your current filters. Try adjusting your filter criteria."
          }
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Results header */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          {totalCount > 0 && (
            <>
              Showing {results.length} of {totalCount} results
              {query && <span> for "{query}"</span>}
            </>
          )}
        </div>
      </div>

      {/* Results list */}
      <div className="space-y-4">
        {results.map((result) => (
          <Link
            key={result.id}
            to={result.url_path}
            className="block bg-white rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all duration-200 p-6"
          >
            <div className="flex items-start space-x-4">
              {/* Content type icon */}
              <div className={`p-2 rounded-lg ${getContentTypeColor(result.content_type)}`}>
                {getContentIcon(result.content_type)}
              </div>

              {/* Content details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                      {result.title}
                    </h3>
                    <p className="text-gray-600 text-sm mb-3 line-clamp-3">
                      {result.description}
                    </p>
                  </div>
                  
                  {/* Relevance score (for debugging, can be removed in production) */}
                  {process.env.NODE_ENV === 'development' && (
                    <div className="ml-4 flex items-center text-xs text-gray-400">
                      <StarIcon className="h-3 w-3 mr-1" />
                      {result.relevance_score.toFixed(1)}
                    </div>
                  )}
                </div>

                {/* Tags and metadata */}
                <div className="flex items-center space-x-3 text-xs">
                  <span className={`px-2 py-1 rounded-full font-medium ${getContentTypeColor(result.content_type)}`}>
                    {result.content_type}
                  </span>
                  <span className="px-2 py-1 rounded-full bg-gray-100 text-gray-700 font-medium capitalize">
                    {result.technology}
                  </span>
                  <span className={`px-2 py-1 rounded-full font-medium ${getDifficultyColor(result.difficulty_level)}`}>
                    {result.difficulty_level}
                  </span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Load more button */}
      {hasMore && (
        <div className="text-center pt-6">
          <button
            onClick={onLoadMore}
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Loading...</span>
              </div>
            ) : (
              'Load More Results'
            )}
          </button>
        </div>
      )}

      {/* Loading indicator for additional results */}
      {loading && results.length > 0 && (
        <div className="text-center py-4">
          <div className="inline-flex items-center space-x-2 text-gray-500">
            <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
            <span>Loading more results...</span>
          </div>
        </div>
      )}
    </div>
  );
};