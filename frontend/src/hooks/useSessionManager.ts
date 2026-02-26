import { useState, useEffect, useCallback } from 'react';

interface SessionData {
  sessionToken: string;
  caseId: string | null;
  userId: string | null;
  currentStep: string;
  lastActivity: string;
  isAnonymous: boolean;
}

interface UseSessionManagerOptions {
  persistAcrossTabs?: boolean;
  sessionTimeoutMinutes?: number;
}

/**
 * Generate a cryptographically secure session token
 */
function generateSecureToken(): string {
  const array = new Uint8Array(24);
  crypto.getRandomValues(array);
  const hex = Array.from(array, b => b.toString(16).padStart(2, '0')).join('');
  return `sess_${hex}`;
}

export const useSessionManager = (options: UseSessionManagerOptions = {}) => {
  const {
    persistAcrossTabs = true,
    sessionTimeoutMinutes = 120
  } = options;

  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Choose storage type based on persistence preference
  const storage = persistAcrossTabs ? localStorage : sessionStorage;
  const STORAGE_KEY = 'osprey_session_data';

  // Initialize session from storage
  useEffect(() => {
    try {
      const stored = storage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as SessionData;

        // Check if session is expired
        const lastActivity = new Date(parsed.lastActivity);
        const now = new Date();
        const minutesSinceActivity = (now.getTime() - lastActivity.getTime()) / (1000 * 60);

        if (minutesSinceActivity < sessionTimeoutMinutes) {
          setSessionData(parsed);
        } else {
          storage.removeItem(STORAGE_KEY);
        }
      }
    } catch {
      storage.removeItem(STORAGE_KEY);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Sync session data to storage whenever it changes
  useEffect(() => {
    if (sessionData) {
      try {
        storage.setItem(STORAGE_KEY, JSON.stringify(sessionData));
      } catch {
        // Storage full or unavailable
      }
    }
  }, [sessionData]);

  // Create new session
  const createSession = useCallback((caseId?: string, userId?: string) => {
    const sessionToken = generateSecureToken();

    const newSession: SessionData = {
      sessionToken,
      caseId: caseId || null,
      userId: userId || null,
      currentStep: 'start',
      lastActivity: new Date().toISOString(),
      isAnonymous: !userId
    };

    setSessionData(newSession);

    // Also store legacy session token for backward compatibility
    storage.setItem('osprey_session_token', sessionToken);

    return newSession;
  }, []);

  // Update session data
  const updateSession = useCallback((updates: Partial<SessionData>) => {
    if (!sessionData) {
      return;
    }

    const updatedSession = {
      ...sessionData,
      ...updates,
      lastActivity: new Date().toISOString()
    };

    setSessionData(updatedSession);
  }, [sessionData]);

  // Set case ID
  const setCaseId = useCallback((caseId: string) => {
    updateSession({ caseId });
  }, [updateSession]);

  // Set current step
  const setCurrentStep = useCallback((step: string) => {
    updateSession({ currentStep: step });
  }, [updateSession]);

  // Update activity timestamp
  const updateActivity = useCallback(() => {
    if (sessionData) {
      updateSession({ lastActivity: new Date().toISOString() });
    }
  }, [sessionData, updateSession]);

  // Clear session
  const clearSession = useCallback(() => {
    setSessionData(null);
    storage.removeItem(STORAGE_KEY);
    storage.removeItem('osprey_session_token');
    storage.removeItem('osprey_anonymous_id');
  }, []);

  // Get session token for API calls
  const getSessionToken = useCallback(() => {
    return sessionData?.sessionToken || null;
  }, [sessionData]);

  // Get case ID
  const getCaseId = useCallback(() => {
    return sessionData?.caseId || null;
  }, [sessionData]);

  // Check if session is active
  const isSessionActive = useCallback(() => {
    return !!sessionData && !!sessionData.sessionToken;
  }, [sessionData]);

  // Auto-cleanup on page unload
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (sessionData && !persistAcrossTabs) {
        storage.removeItem(STORAGE_KEY);
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [sessionData, persistAcrossTabs]);

  return {
    sessionData,
    isLoading,
    createSession,
    updateSession,
    setCaseId,
    setCurrentStep,
    updateActivity,
    clearSession,
    getSessionToken,
    getCaseId,
    isSessionActive
  };
};

export default useSessionManager;
