import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { SearchBar } from '../components/search/SearchBar';
import { SearchFilters } from '../components/search/SearchFilters';
import { SearchResults } from '../components/search/SearchResults';
import { SearchFilters as SearchFiltersType, SearchResult, SearchState } from '../types/search';
import apiClient from '../services/api';

const RESULTS_PER_PAGE = 20;

export const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [searchState, setSearchState] = useState<SearchState>({
    query: searchParams.get('q') || '',
    filters: {
      technology: searchParams.get('technology') || undefined,
      difficulty_level: searchParams.get('difficulty') || undefined,
      exercise_type: searchParams.get('type') || undefined,
      completion_status: searchParams.get('status') || undefined,
    },
    results: [],
    totalCount: 0,
    loading: false,
    error: null,
    suggestions: [],
    availableFilters: null,
  });

  const [currentPage, setCurrentPage] = useState(0);

  // Update URL when search state changes
  const updateURL = useCallback((query: string, filters: SearchFiltersType) => {
    const params = new URLSearchParams();
    
    if (query) params.set('q', query);
    if (filters.technology) params.set('technology', filters.technology);
    if (filters.difficulty_level) params.set('difficulty', filters.difficulty_level);
    if (filters.exercise_type) params.set('type', filters.exercise_type);
    if (filters.completion_status) params.set('status', filters.completion_status);
    
    setSearchParams(params);
  }, [setSearchParams]);

  // Perform search
  const performSearch = useCallback(async (
    query: string, 
    filters: SearchFiltersType, 
    page: number = 0,
    append: boolean = false
  ) => {
    // Don't search if no query and no filters
    if (!query && !Object.values(filters).some(v => v)) {
      return;
    }

    setSearchState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await apiClient.searchContent({
        query: query || undefined,
        ...filters,
        limit: RESULTS_PER_PAGE,
        offset: page * RESULTS_PER_PAGE,
      });

      setSearchState(prev => ({
        ...prev,
        results: append ? [...prev.results, ...response.results] : response.results,
        totalCount: response.total_count,
        loading: false,
      }));
    } catch (error) {
      console.error('Search failed:', error);
      setSearchState(prev => ({
        ...prev,
        loading: false,
        error: 'Search failed. Please try again.',
      }));
    }
  }, []);

  // Handle search query change
  const handleQueryChange = (query: string) => {
    setSearchState(prev => ({ ...prev, query }));
  };

  // Handle search submission
  const handleSearch = (query: string) => {
    setCurrentPage(0);
    setSearchState(prev => ({ ...prev, query }));
    updateURL(query, searchState.filters);
    performSearch(query, searchState.filters, 0, false);
  };

  // Handle filter changes
  const handleFiltersChange = (filters: SearchFiltersType) => {
    setCurrentPage(0);
    setSearchState(prev => ({ ...prev, filters }));
    updateURL(searchState.query, filters);
    performSearch(searchState.query, filters, 0, false);
  };

  // Handle load more
  const handleLoadMore = () => {
    const nextPage = currentPage + 1;
    setCurrentPage(nextPage);
    performSearch(searchState.query, searchState.filters, nextPage, true);
  };

  // Initial search on component mount or URL params change
  useEffect(() => {
    const query = searchParams.get('q') || '';
    const filters: SearchFiltersType = {
      technology: searchParams.get('technology') || undefined,
      difficulty_level: searchParams.get('difficulty') || undefined,
      exercise_type: searchParams.get('type') || undefined,
      completion_status: searchParams.get('status') || undefined,
    };

    setSearchState(prev => ({ ...prev, query, filters }));
    
    if (query || Object.values(filters).some(v => v)) {
      performSearch(query, filters, 0, false);
    }
  }, [searchParams, performSearch]);

  const hasMore = searchState.results.length < searchState.totalCount;
  const hasSearchCriteria = searchState.query || Object.values(searchState.filters).some(v => v);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Search Learning Content</h1>
          <p className="text-gray-600">
            Find lessons, exercises, and reference materials across Flask, FastAPI, and PostgreSQL
          </p>
        </div>

        {/* Search bar */}
        <div className="mb-8">
          <SearchBar
            value={searchState.query}
            onChange={handleQueryChange}
            onSearch={handleSearch}
            className="max-w-2xl"
          />
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters sidebar */}
          <div className="lg:w-80 flex-shrink-0">
            <SearchFilters
              filters={searchState.filters}
              onChange={handleFiltersChange}
            />
          </div>

          {/* Results */}
          <div className="flex-1">
            {hasSearchCriteria ? (
              <SearchResults
                results={searchState.results}
                totalCount={searchState.totalCount}
                loading={searchState.loading}
                error={searchState.error}
                query={searchState.query}
                onLoadMore={handleLoadMore}
                hasMore={hasMore}
              />
            ) : (
              <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                <div className="max-w-md mx-auto">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Start Your Search
                  </h3>
                  <p className="text-gray-500 mb-6">
                    Enter a search term or use the filters to find learning content that matches your needs.
                  </p>
                  <div className="space-y-4">
                    <div className="text-sm text-gray-600">
                      <strong>Popular searches:</strong>
                    </div>
                    <div className="flex flex-wrap gap-2 justify-center">
                      {['Flask routing', 'FastAPI async', 'PostgreSQL queries', 'Authentication', 'Database design'].map((term) => (
                        <button
                          key={term}
                          onClick={() => handleSearch(term)}
                          className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors"
                        >
                          {term}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};