import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';

interface OwlSession {
  session_id: string;
  visa_type: string;
  language: string;
  progress: number;
  current_field: string;
  responses: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface OwlSessionState {
  session: OwlSession | null;
  loading: boolean;
  error: string | null;
}

type OwlSessionAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_SESSION'; payload: OwlSession }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'UPDATE_PROGRESS'; payload: number }
  | { type: 'UPDATE_RESPONSES'; payload: Record<string, any> }
  | { type: 'CLEAR_SESSION' };

const initialState: OwlSessionState = {
  session: null,
  loading: false,
  error: null,
};

const owlSessionReducer = (state: OwlSessionState, action: OwlSessionAction): OwlSessionState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_SESSION':
      return { ...state, session: action.payload, loading: false, error: null };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'UPDATE_PROGRESS':
      return {
        ...state,
        session: state.session ? { ...state.session, progress: action.payload } : null,
      };
    case 'UPDATE_RESPONSES':
      return {
        ...state,
        session: state.session
          ? { ...state.session, responses: { ...state.session.responses, ...action.payload } }
          : null,
      };
    case 'CLEAR_SESSION':
      return initialState;
    default:
      return state;
  }
};

interface OwlSessionContextType {
  state: OwlSessionState;
  startSession: (visaType: string, language: string) => Promise<void>;
  getSession: (sessionId: string) => Promise<void>;
  saveResponse: (fieldId: string, value: any) => Promise<void>;
  updateProgress: (progress: number) => void;
  clearSession: () => void;
}

const OwlSessionContext = createContext<OwlSessionContextType | undefined>(undefined);

export const useOwlSession = () => {
  const context = useContext(OwlSessionContext);
  if (!context) {
    throw new Error('useOwlSession must be used within an OwlSessionProvider');
  }
  return context;
};

interface OwlSessionProviderProps {
  children: ReactNode;
}

export const OwlSessionProvider: React.FC<OwlSessionProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(owlSessionReducer, initialState);

  const getBackendUrl = () => {
    return import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://agente-coruja-1.preview.emergentagent.com';
  };

  const startSession = async (visaType: string, language: string) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      // Generate a unique case ID for the owl session
      const caseId = `OWL-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      
      const response = await fetch(`${getBackendUrl()}/api/owl-agent/start-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_id: caseId,
          visa_type: visaType,
          language: language,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to start session: ${response.statusText}`);
      }

      const data = await response.json();
      dispatch({ type: 'SET_SESSION', payload: data.session });
      
      // Store session ID in localStorage for persistence
      localStorage.setItem('owl_session_id', data.session.session_id);
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' });
    }
  };

  const getSession = async (sessionId: string) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const response = await fetch(`${getBackendUrl()}/api/owl-agent/session/${sessionId}`);

      if (!response.ok) {
        throw new Error(`Failed to get session: ${response.statusText}`);
      }

      const data = await response.json();
      dispatch({ type: 'SET_SESSION', payload: data.session });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' });
    }
  };

  const saveResponse = async (fieldId: string, value: any) => {
    if (!state.session) {
      throw new Error('No active session');
    }

    try {
      const response = await fetch(`${getBackendUrl()}/api/owl-agent/save-response`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: state.session.session_id,
          field_id: fieldId,
          user_response: value,
          validation_score: 100, // Default score, will be calculated by backend
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to save response: ${response.statusText}`);
      }

      const data = await response.json();
      dispatch({ type: 'UPDATE_RESPONSES', payload: { [fieldId]: value } });
      dispatch({ type: 'UPDATE_PROGRESS', payload: data.progress });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' });
    }
  };

  const updateProgress = (progress: number) => {
    dispatch({ type: 'UPDATE_PROGRESS', payload: progress });
  };

  const clearSession = () => {
    localStorage.removeItem('owl_session_id');
    dispatch({ type: 'CLEAR_SESSION' });
  };

  // Auto-restore session on mount
  useEffect(() => {
    const sessionId = localStorage.getItem('owl_session_id');
    if (sessionId && !state.session) {
      getSession(sessionId);
    }
  }, []);

  const contextValue: OwlSessionContextType = {
    state,
    startSession,
    getSession,
    saveResponse,
    updateProgress,
    clearSession,
  };

  return (
    <OwlSessionContext.Provider value={contextValue}>
      {children}
    </OwlSessionContext.Provider>
  );
};