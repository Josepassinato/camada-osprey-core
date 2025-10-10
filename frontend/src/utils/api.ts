/**
 * Utility functions for API configuration
 * Ensures correct backend URL detection in all environments
 */

export const getBackendUrl = (): string => {
  // Always prioritize environment variable first
  if (import.meta.env.VITE_BACKEND_URL) {
    return import.meta.env.VITE_BACKEND_URL;
  }
  
  // PRODUCTION ERROR: Environment variable MUST be set for deployments
  console.error('❌ VITE_BACKEND_URL not set - deployment will fail');
  throw new Error('VITE_BACKEND_URL environment variable is required for production deployment');
};

export const getApiUrl = (endpoint: string): string => {
  const backendUrl = getBackendUrl();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${backendUrl}/api${cleanEndpoint}`;
};

// Helper for making API calls with proper error handling
export const makeApiCall = async (endpoint: string, options: RequestInit = {}): Promise<Response> => {
  const url = getApiUrl(endpoint);
  
  console.log('🔘 API Call:', url);
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };
  
  const finalOptions = { ...defaultOptions, ...options };
  
  try {
    const response = await fetch(url, finalOptions);
    console.log('🔘 API Response:', response.status, response.statusText);
    return response;
  } catch (error) {
    console.error('🔘 API Error:', error);
    throw error;
  }
};