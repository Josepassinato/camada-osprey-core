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
      return 'https://immigration-helper-2.preview.emergentagent.com';
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
  return 'https://immigration-helper-2.preview.emergentagent.com';
};

export const getApiUrl = (endpoint: string): string => {
  const backendUrl = getBackendUrl();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${backendUrl}/api${cleanEndpoint}`;
};

// Helper for making API calls with proper error handling
export const makeApiCall = async (endpoint: string, method: string = 'GET', body?: any): Promise<any> => {
  const url = getApiUrl(endpoint);
  
  console.log('🔘 API Call:', url);
  
  const options: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  if (body && method !== 'GET') {
    options.body = JSON.stringify(body);
  }
  
  try {
    const response = await fetch(url, options);
    console.log('🔘 API Response:', response.status, response.statusText);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: response.statusText }));
      throw new Error(errorData.error || errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('🔘 API Error:', error);
    throw error;
  }
};