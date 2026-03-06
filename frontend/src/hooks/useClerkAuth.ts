import { useAuth, useUser } from "@clerk/clerk-react";
import { useEffect } from "react";

/**
 * Custom hook to integrate Clerk authentication with Osprey backend
 * 
 * This hook provides:
 * - Clerk authentication state
 * - User information
 * - Token for API calls
 * 
 * Usage:
 * ```typescript
 * const { isSignedIn, user, token, isLoading } = useClerkAuth();
 * ```
 */
export function useClerkAuth() {
  const { isLoaded: authLoaded, isSignedIn, getToken } = useAuth();
  const { isLoaded: userLoaded, user } = useUser();

  const isLoading = !authLoaded || !userLoaded;

  useEffect(() => {
    // Sync Clerk auth state with localStorage for backward compatibility
    if (authLoaded && isSignedIn && user) {
      // Store user info in localStorage (for legacy code compatibility)
      const userData = {
        id: user.id,
        email: user.primaryEmailAddress?.emailAddress,
        name: user.fullName,
        firstName: user.firstName,
        lastName: user.lastName,
      };
      localStorage.setItem('osprey_user', JSON.stringify(userData));
    } else if (authLoaded && !isSignedIn) {
      // Clear localStorage when signed out
      localStorage.removeItem('osprey_user');
      localStorage.removeItem('osprey_token');
    }
  }, [authLoaded, isSignedIn, user]);

  /**
   * Get Clerk session token for API calls
   * This token should be sent in the Authorization header
   */
  const getAuthToken = async (): Promise<string | null> => {
    if (!isSignedIn) return null;
    try {
      return await getToken();
    } catch (error) {
      console.error("Failed to get Clerk token:", error);
      return null;
    }
  };

  return {
    isLoading,
    isSignedIn: isSignedIn ?? false,
    user: user ?? null,
    getAuthToken,
    // Convenience properties
    userId: user?.id ?? null,
    email: user?.primaryEmailAddress?.emailAddress ?? null,
    fullName: user?.fullName ?? null,
  };
}
