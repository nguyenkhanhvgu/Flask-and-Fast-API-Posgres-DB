export interface SearchResult {
  id: string;
  title: string;
  description: string;
  content_type: 'module' | 'lesson' | 'exercise';
  technology: string;
  difficulty_level: string;
  relevance_score: number;
  url_path: string;
}

export interface SearchResponse {
  results: SearchResult[];
  total_count: number;
  query?: string;
  filters: SearchFilters;
  suggestions: string[];
  facets: SearchFacets;
}

export interface SearchFilters {
  technology?: string;
  difficulty_level?: string;
  exercise_type?: string;
  completion_status?: string;
}

export interface SearchFacets {
  technologies?: FacetItem[];
  difficulty_levels?: FacetItem[];
  exercise_types?: FacetItem[];
}

export interface FacetItem {
  value: string;
  count: number;
}

export interface SearchSuggestion {
  text: string;
  type: 'query' | 'technology' | 'difficulty';
  count: number;
}

export interface ContentFilter {
  technologies: string[];
  difficulty_levels: string[];
  exercise_types: string[];
  completion_statuses: string[];
}

export interface SearchParams {
  query?: string;
  technology?: string;
  difficulty_level?: string;
  exercise_type?: string;
  completion_status?: string;
  limit?: number;
  offset?: number;
}

export interface SearchState {
  query: string;
  filters: SearchFilters;
  results: SearchResult[];
  totalCount: number;
  loading: boolean;
  error: string | null;
  suggestions: SearchSuggestion[];
  availableFilters: ContentFilter | null;
}