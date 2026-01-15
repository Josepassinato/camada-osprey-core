/**
 * Utility functions for API configuration
 * Ensures correct backend URL detection in all environments
 */

export const getBackendUrl = (): string => {
  // DEPLOYMENT FIX: Read from environment variable only
  // Emergent will inject the correct backend URL automatically
  return import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001';
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
  
  const token = localStorage.getItem('osprey_token');
  
  const options: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
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