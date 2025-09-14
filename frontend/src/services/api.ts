import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { AuthTokens, LoginCredentials, RegisterCredentials, User } from '../types/auth';

class ApiClient {
  private client: AxiosInstance;
  private tokens: AuthTokens | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.loadTokensFromStorage();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.tokens?.access_token) {
          config.headers.Authorization = `Bearer ${this.tokens.access_token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            await this.refreshToken();
            return this.client(originalRequest);
          } catch (refreshError) {
            this.clearTokens();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  private loadTokensFromStorage() {
    const storedTokens = localStorage.getItem('auth_tokens');
    if (storedTokens) {
      try {
        this.tokens = JSON.parse(storedTokens);
      } catch (error) {
        console.error('Failed to parse stored tokens:', error);
        localStorage.removeItem('auth_tokens');
      }
    }
  }

  private saveTokensToStorage(tokens: AuthTokens) {
    this.tokens = tokens;
    localStorage.setItem('auth_tokens', JSON.stringify(tokens));
  }

  private clearTokens() {
    this.tokens = null;
    localStorage.removeItem('auth_tokens');
  }

  // Authentication methods
  async login(credentials: LoginCredentials): Promise<{ user: User; tokens: AuthTokens }> {
    const response = await this.client.post('/auth/login', credentials);
    const { user, ...tokens } = response.data;
    this.saveTokensToStorage(tokens);
    return { user, tokens };
  }

  async register(credentials: RegisterCredentials): Promise<{ user: User; tokens: AuthTokens }> {
    const response = await this.client.post('/auth/register', credentials);
    const { user, ...tokens } = response.data;
    this.saveTokensToStorage(tokens);
    return { user, tokens };
  }

  async refreshToken(): Promise<AuthTokens> {
    if (!this.tokens?.refresh_token) {
      throw new Error('No refresh token available');
    }

    const response = await this.client.post('/auth/refresh', {
      refresh_token: this.tokens.refresh_token,
    });

    const tokens = response.data;
    this.saveTokensToStorage(tokens);
    return tokens;
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/auth/logout');
    } finally {
      this.clearTokens();
    }
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Content methods
  async getModules() {
    const response = await this.client.get('/modules');
    return response.data;
  }

  async getModule(moduleId: string) {
    const response = await this.client.get(`/modules/${moduleId}`);
    return response.data;
  }

  async getLesson(lessonId: string) {
    const response = await this.client.get(`/lessons/${lessonId}`);
    return response.data;
  }

  async getExercise(exerciseId: string) {
    const response = await this.client.get(`/exercises/${exerciseId}`);
    return response.data;
  }

  // Progress methods
  async getUserProgress(userId: string) {
    const response = await this.client.get(`/users/${userId}/progress`);
    return response.data;
  }

  async markLessonComplete(lessonId: string) {
    const response = await this.client.post('/progress/lesson', { lesson_id: lessonId });
    return response.data;
  }

  async submitExercise(exerciseId: string, code: string) {
    const response = await this.client.post('/progress/exercise', {
      exercise_id: exerciseId,
      code,
    });
    return response.data;
  }

  async getUserBookmarks(userId: string) {
    const response = await this.client.get(`/users/${userId}/bookmarks`);
    return response.data;
  }

  // Exercise validation methods
  async validateExercise(exerciseId: string, code: string) {
    const response = await this.client.post('/exercises/validate', {
      exercise_id: exerciseId,
      code,
    });
    return response.data;
  }

  async executeCode(code: string, language: string = 'python') {
    const response = await this.client.post('/code/execute', {
      code,
      language,
    });
    return response.data;
  }

  async getExerciseHints(exerciseId: string) {
    const response = await this.client.get(`/exercises/${exerciseId}/hints`);
    return response.data;
  }

  // Search methods
  async searchContent(params: {
    query?: string;
    technology?: string;
    difficulty_level?: string;
    exercise_type?: string;
    completion_status?: string;
    limit?: number;
    offset?: number;
  }) {
    const response = await this.client.get('/search/', { params });
    return response.data;
  }

  async getSearchSuggestions(query: string, limit: number = 10) {
    const response = await this.client.get('/search/suggestions', {
      params: { query, limit }
    });
    return response.data;
  }

  async getContentFilters() {
    const response = await this.client.get('/search/filters');
    return response.data;
  }

  async searchModules(params: {
    query?: string;
    technology?: string;
    difficulty_level?: string;
    completion_status?: string;
    limit?: number;
    offset?: number;
  }) {
    const response = await this.client.get('/search/modules', { params });
    return response.data;
  }

  async searchLessons(params: {
    query?: string;
    technology?: string;
    difficulty_level?: string;
    completion_status?: string;
    limit?: number;
    offset?: number;
  }) {
    const response = await this.client.get('/search/lessons', { params });
    return response.data;
  }

  async searchExercises(params: {
    query?: string;
    technology?: string;
    difficulty_level?: string;
    exercise_type?: string;
    completion_status?: string;
    limit?: number;
    offset?: number;
  }) {
    const response = await this.client.get('/search/exercises', { params });
    return response.data;
  }

  async getPopularContent(params: {
    content_type?: string;
    technology?: string;
    limit?: number;
  }) {
    const response = await this.client.get('/search/popular', { params });
    return response.data;
  }

  async getRecentContent(params: {
    content_type?: string;
    technology?: string;
    limit?: number;
  }) {
    const response = await this.client.get('/search/recent', { params });
    return response.data;
  }

  // Generic request method for custom requests
  async request<T = any>(config: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.request(config);
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.tokens?.access_token;
  }

  // Get current tokens
  getTokens(): AuthTokens | null {
    return this.tokens;
  }
}

export const apiClient = new ApiClient();
export default apiClient;