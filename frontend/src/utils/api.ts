/**
 * Utility functions for API configuration
 * Ensures correct backend URL detection in all environments
 */

export const getBackendUrl = (): string => {
  // Check if we're in preview environment
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    
    // Preview environment detection
    if (hostname.includes('preview.emergentagent.com')) {
      return 'https://visa-genius-2.preview.emergentagent.com';
    }
    
    // Production environment detection  
    if (hostname.includes('emergentagent.com') && !hostname.includes('preview')) {
      return 'https://visa-genius-2.preview.emergentagent.com'; // Will be updated for production
    }
  }
  
  // Fallback to environment variable or preview URL
  return import.meta.env.VITE_BACKEND_URL || 'https://visa-genius-2.preview.emergentagent.com';
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