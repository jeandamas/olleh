const API_BASE_URL = 'http://localhost:8000';

// Token storage keys
const ACCESS_TOKEN_KEY = 'olleh_access_token';
const REFRESH_TOKEN_KEY = 'olleh_refresh_token';

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface ApiError {
  detail?: string;
  message?: string;
  [key: string]: unknown;
}

/**
 * Token management utilities
 */
export const tokenStorage = {
  getAccessToken: (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  },
  
  getRefreshToken: (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },
  
  setTokens: (tokens: TokenPair): void => {
    if (typeof window === 'undefined') return;
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
  },
  
  clearTokens: (): void => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
  
  hasTokens: (): boolean => {
    return !!tokenStorage.getAccessToken() && !!tokenStorage.getRefreshToken();
  },
};

/**
 * Refresh access token using refresh token
 */
async function refreshAccessToken(): Promise<TokenPair | null> {
  const refreshToken = tokenStorage.getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${API_BASE_URL}/auth/jwt/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      tokenStorage.clearTokens();
      return null;
    }

    const data = await response.json();
    const tokens: TokenPair = {
      access: data.access,
      refresh: refreshToken, // Refresh token doesn't change
    };
    
    tokenStorage.setTokens(tokens);
    return tokens;
  } catch (error) {
    tokenStorage.clearTokens();
    return null;
  }
}

/**
 * Main API client function
 */
export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const accessToken = tokenStorage.getAccessToken();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add JWT token if available
  if (accessToken) {
    headers['Authorization'] = `JWT ${accessToken}`;
  }

  let response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // If 401 and we have a refresh token, try to refresh
  if (response.status === 401 && tokenStorage.getRefreshToken()) {
    const newTokens = await refreshAccessToken();
    
    if (newTokens) {
      // Retry the original request with new token
      headers['Authorization'] = `JWT ${newTokens.access}`;
      response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });
    } else {
      // Refresh failed, clear tokens and throw error
      tokenStorage.clearTokens();
      throw new Error('Authentication failed. Please login again.');
    }
  }

  if (!response.ok) {
    let errorData: ApiError = {};
    try {
      errorData = await response.json();
    } catch {
      errorData = { detail: response.statusText };
    }
    
    const error = new Error(errorData.detail || errorData.message || 'An error occurred');
    (error as Error & { status?: number; data?: ApiError }).status = response.status;
    (error as Error & { status?: number; data?: ApiError }).data = errorData;
    throw error;
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

/**
 * Convenience methods for common HTTP verbs
 */
export const api = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    apiClient<T>(endpoint, { ...options, method: 'GET' }),
  
  post: <T>(endpoint: string, data?: unknown, options?: RequestInit) =>
    apiClient<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),
  
  put: <T>(endpoint: string, data?: unknown, options?: RequestInit) =>
    apiClient<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),
  
  patch: <T>(endpoint: string, data?: unknown, options?: RequestInit) =>
    apiClient<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    }),
  
  delete: <T>(endpoint: string, options?: RequestInit) =>
    apiClient<T>(endpoint, { ...options, method: 'DELETE' }),
};
