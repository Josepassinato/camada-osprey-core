/**
 * Enhanced API utility with Clerk authentication support
 * Provides backward compatibility with legacy auth while supporting Clerk tokens
 */

import { getBackendUrl } from './api';

export const getApiUrl = (endpoint: string): string => {
  const backendUrl = getBackendUrl();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${backendUrl}/api${cleanEndpoint}`;
};

interface MakeApiCallOptions {
  method?: string;
  body?: any;
  clerkToken?: string | null;
  useLegacyAuth?: boolean;
}

/**
 * Enhanced makeApiCall with Clerk authentication support
 * 
 * Usage:
 * ```typescript
 * // With Clerk token
 * const { getAuthToken } = useClerkAuth();
 * const token = await getAuthToken();
 * const data = await makeApiCall('/cases', { method: 'GET', clerkToken: token });
 * 
 * // Legacy auth (backward compatible)
 * const data = await makeApiCall('/cases', { method: 'GET', useLegacyAuth: true });
 * ```
 */
export const makeApiCall = async (
  endpoint: string,
  options: MakeApiCallOptions = {}
): Promise<any> => {
  const {
    method = 'GET',
    body,
    clerkToken,
    useLegacyAuth = false
  } = options;

  const url = getApiUrl(endpoint);
  
  console.log('🔘 API Call:', method, url);
  
  // Determine which token to use
  let authToken: string | null = null;
  
  if (clerkToken) {
    // Use Clerk token if provided
    authToken = clerkToken;
    console.log('🔐 Using Clerk authentication');
  } else if (useLegacyAuth) {
    // Use legacy token from localStorage
    authToken = localStorage.getItem('osprey_token');
    console.log('🔐 Using legacy authentication');
  }
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  
  const fetchOptions: RequestInit = {
    method,
    headers,
  };
  
  if (body && method !== 'GET') {
    fetchOptions.body = JSON.stringify(body);
  }
  
  try {
    const response = await fetch(url, fetchOptions);
    console.log('🔘 API Response:', response.status, response.statusText);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ 
        error: response.statusText 
      }));
      
      // Handle authentication errors
      if (response.status === 401) {
        console.error('🔐 Authentication failed - token may be expired');
        // Clear legacy token if it failed
        if (useLegacyAuth) {
          localStorage.removeItem('osprey_token');
          localStorage.removeItem('osprey_user');
        }
      }
      
      throw new Error(
        errorData.error || 
        errorData.detail || 
        `HTTP ${response.status}: ${response.statusText}`
      );
    }
    
    const data = await response.json();
    return data;
  } catch (error: any) {
    console.error('🔘 API Error:', error);
    throw error;
  }
};

/**
 * Simplified API call function for backward compatibility
 * Automatically uses legacy auth from localStorage
 */
export const makeApiCallLegacy = async (
  endpoint: string,
  method: string = 'GET',
  body?: any
): Promise<any> => {
  return makeApiCall(endpoint, {
    method,
    body,
    useLegacyAuth: true
  });
};
