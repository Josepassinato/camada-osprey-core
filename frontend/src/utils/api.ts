/**
 * Utility functions for API configuration
 * Ensures correct backend URL detection in all environments
 */

const isDev = import.meta.env.DEV;

export const getBackendUrl = (): string => {
  return import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001';
};

export const getApiUrl = (endpoint: string): string => {
  const backendUrl = getBackendUrl();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${backendUrl}/api${cleanEndpoint}`;
};

/**
 * Get auth token from localStorage
 */
const getAuthToken = (): string | null => {
  return localStorage.getItem('osprey_token');
};

/**
 * Authenticated fetch - automatically attaches auth token and handles 401
 */
export const authFetch = async (endpoint: string, method: string = 'GET', body?: any): Promise<any> => {
  const url = getApiUrl(endpoint);
  const token = getAuthToken();

  if (isDev) console.log('API Call:', method, endpoint);

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const options: RequestInit = { method, headers };

  if (body && method !== 'GET') {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);

  // Handle 401 globally - clear auth and redirect
  if (response.status === 401) {
    localStorage.removeItem('osprey_token');
    localStorage.removeItem('osprey_user');
    if (window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: response.statusText }));
    throw new Error(errorData.error || errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
};

// Helper for making API calls with proper error handling (legacy - no auth)
export const makeApiCall = async (endpoint: string, method: string = 'GET', body?: any): Promise<any> => {
  const url = getApiUrl(endpoint);

  if (isDev) console.log('API Call:', method, endpoint);

  const options: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (body && method !== 'GET') {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);

  if (isDev) console.log('API Response:', response.status);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: response.statusText }));
    throw new Error(errorData.error || errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
};
