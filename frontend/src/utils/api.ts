/**
 * Utility functions for API configuration
 * Ensures correct backend URL detection in all environments
 */

export const getBackendUrl = (): string => {
  // Always prioritize environment variable first
  const envBackendUrl = import.meta.env.VITE_BACKEND_URL;
  if (envBackendUrl) {
    return envBackendUrl;
  }
  
  // Browser environment detection as fallback
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    
    // Preview environment detection
    if (hostname.includes('preview.emergentagent.com')) {
      return 'https://owlagent.preview.emergentagent.com';
    }
    
    // Production environment - use production URL
    if (hostname.includes('emergentagent.com') && !hostname.includes('preview')) {
      return 'https://www.iaimmigration.com';
    }
    
    // Custom domain detection
    if (hostname === 'www.iaimmigration.com' || hostname === 'iaimmigration.com') {
      return 'https://www.iaimmigration.com';
    }
  }
  
  // Final fallback for development
  return 'https://owlagent.preview.emergentagent.com';
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