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
          console.log('🔐 Session restored:', { 
            caseId: parsed.caseId, 
            step: parsed.currentStep,
            minutes: Math.round(minutesSinceActivity)
          });
        } else {
          console.log('🔐 Session expired, clearing storage');
          storage.removeItem(STORAGE_KEY);
        }
      }
    } catch (error) {
      console.error('🔐 Error loading session:', error);
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
        console.log('🔐 Session saved:', { caseId: sessionData.caseId, step: sessionData.currentStep });
      } catch (error) {
        console.error('🔐 Error saving session:', error);
      }
    }
  }, [sessionData]);

  // Create new session
  const createSession = useCallback((caseId?: string, userId?: string) => {
    const sessionToken = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
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
    
    console.log('🔐 New session created:', { 
      sessionToken: sessionToken.slice(-8),
      caseId,
      userId: userId || 'anonymous'
    });
    
    return newSession;
  }, []);

  // Update session data
  const updateSession = useCallback((updates: Partial<SessionData>) => {
    if (!sessionData) {
      console.warn('🔐 Cannot update session: no active session');
      return;
    }

    const updatedSession = {
      ...sessionData,
      ...updates,
      lastActivity: new Date().toISOString()
    };

    setSessionData(updatedSession);
    
    console.log('🔐 Session updated:', { 
      caseId: updatedSession.caseId,
      step: updatedSession.currentStep,
      updates: Object.keys(updates)
    });
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
    console.log('🔐 Session cleared');
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