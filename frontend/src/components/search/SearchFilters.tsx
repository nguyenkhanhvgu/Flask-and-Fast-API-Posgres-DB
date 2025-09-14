import React, { useState, useEffect } from 'react';
import { ChevronDownIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { SearchFilters as SearchFiltersType, ContentFilter } from '../../types/search';
import apiClient from '../../services/api';

interface SearchFiltersProps {
  filters: SearchFiltersType;
  onChange: (filters: SearchFiltersType) => void;
  className?: string;
}

export const SearchFilters: React.FC<SearchFiltersProps> = ({
  filters,
  onChange,
  className = ""
}) => {
  const [availableFilters, setAvailableFilters] = useState<ContentFilter | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['technology']));

  useEffect(() => {
    const fetchFilters = async () => {
      try {
        const filters = await apiClient.getContentFilters();
        setAvailableFilters(filters);
      } catch (error) {
        console.error('Failed to fetch content filters:', error);
      }
    };

    fetchFilters();
  }, []);

  const handleFilterChange = (key: keyof SearchFiltersType, value: string | undefined) => {
    onChange({
      ...filters,
      [key]: value
    });
  };

  const clearFilter = (key: keyof SearchFiltersType) => {
    handleFilterChange(key, undefined);
  };

  const clearAllFilters = () => {
    onChange({});
  };

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const hasActiveFilters = Object.values(filters).some(value => value !== undefined);

  if (!availableFilters) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-3 bg-gray-200 rounded w-3/4"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            <div className="h-3 bg-gray-200 rounded w-2/3"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
          {hasActiveFilters && (
            <button
              onClick={clearAllFilters}
              className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
            >
              Clear all
            </button>
          )}
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Active filters */}
        {hasActiveFilters && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Active Filters</h4>
            <div className="flex flex-wrap gap-2">
              {Object.entries(filters).map(([key, value]) => {
                if (!value) return null;
                return (
                  <span
                    key={key}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                  >
                    <span className="capitalize">{key.replace('_', ' ')}: {value}</span>
                    <button
                      onClick={() => clearFilter(key as keyof SearchFiltersType)}
                      className="ml-2 hover:text-blue-600"
                    >
                      <XMarkIcon className="h-3 w-3" />
                    </button>
                  </span>
                );
              })}
            </div>
          </div>
        )}

        {/* Technology filter */}
        <div>
          <button
            onClick={() => toggleSection('technology')}
            className="flex items-center justify-between w-full text-left"
          >
            <h4 className="text-sm font-medium text-gray-700">Technology</h4>
            <ChevronDownIcon
              className={`h-4 w-4 text-gray-500 transition-transform ${
                expandedSections.has('technology') ? 'rotate-180' : ''
              }`}
            />
          </button>
          {expandedSections.has('technology') && (
            <div className="mt-2 space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="technology"
                  checked={!filters.technology}
                  onChange={() => handleFilterChange('technology', undefined)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className="ml-2 text-sm text-gray-600">All Technologies</span>
              </label>
              {availableFilters.technologies.map((tech) => (
                <label key={tech} className="flex items-center">
                  <input
                    type="radio"
                    name="technology"
                    checked={filters.technology === tech}
                    onChange={() => handleFilterChange('technology', tech)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <span className="ml-2 text-sm text-gray-600 capitalize">{tech}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Difficulty level filter */}
        <div>
          <button
            onClick={() => toggleSection('difficulty')}
            className="flex items-center justify-between w-full text-left"
          >
            <h4 className="text-sm font-medium text-gray-700">Difficulty Level</h4>
            <ChevronDownIcon
              className={`h-4 w-4 text-gray-500 transition-transform ${
                expandedSections.has('difficulty') ? 'rotate-180' : ''
              }`}
            />
          </button>
          {expandedSections.has('difficulty') && (
            <div className="mt-2 space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="difficulty_level"
                  checked={!filters.difficulty_level}
                  onChange={() => handleFilterChange('difficulty_level', undefined)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className="ml-2 text-sm text-gray-600">All Levels</span>
              </label>
              {availableFilters.difficulty_levels.map((level) => (
                <label key={level} className="flex items-center">
                  <input
                    type="radio"
                    name="difficulty_level"
                    checked={filters.difficulty_level === level}
                    onChange={() => handleFilterChange('difficulty_level', level)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <span className="ml-2 text-sm text-gray-600 capitalize">{level}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Exercise type filter */}
        <div>
          <button
            onClick={() => toggleSection('exercise_type')}
            className="flex items-center justify-between w-full text-left"
          >
            <h4 className="text-sm font-medium text-gray-700">Exercise Type</h4>
            <ChevronDownIcon
              className={`h-4 w-4 text-gray-500 transition-transform ${
                expandedSections.has('exercise_type') ? 'rotate-180' : ''
              }`}
            />
          </button>
          {expandedSections.has('exercise_type') && (
            <div className="mt-2 space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="exercise_type"
                  checked={!filters.exercise_type}
                  onChange={() => handleFilterChange('exercise_type', undefined)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className="ml-2 text-sm text-gray-600">All Types</span>
              </label>
              {availableFilters.exercise_types.map((type) => (
                <label key={type} className="flex items-center">
                  <input
                    type="radio"
                    name="exercise_type"
                    checked={filters.exercise_type === type}
                    onChange={() => handleFilterChange('exercise_type', type)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <span className="ml-2 text-sm text-gray-600 capitalize">{type}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Completion status filter */}
        <div>
          <button
            onClick={() => toggleSection('completion')}
            className="flex items-center justify-between w-full text-left"
          >
            <h4 className="text-sm font-medium text-gray-700">Completion Status</h4>
            <ChevronDownIcon
              className={`h-4 w-4 text-gray-500 transition-transform ${
                expandedSections.has('completion') ? 'rotate-180' : ''
              }`}
            />
          </button>
          {expandedSections.has('completion') && (
            <div className="mt-2 space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="completion_status"
                  checked={!filters.completion_status}
                  onChange={() => handleFilterChange('completion_status', undefined)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className="ml-2 text-sm text-gray-600">All Status</span>
              </label>
              {availableFilters.completion_statuses.map((status) => (
                <label key={status} className="flex items-center">
                  <input
                    type="radio"
                    name="completion_status"
                    checked={filters.completion_status === status}
                    onChange={() => handleFilterChange('completion_status', status)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <span className="ml-2 text-sm text-gray-600 capitalize">
                    {status.replace('_', ' ')}
                  </span>
                </label>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};