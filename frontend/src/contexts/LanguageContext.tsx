import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type LanguageMode = 'simple' | 'technical';

interface LanguageContextType {
  mode: LanguageMode;
  setMode: (mode: LanguageMode) => void;
  toggleMode: () => void;
  texts: Record<string, Record<string, string>>;
  loadTexts: (context: string) => Promise<void>;
  getText: (context: string, key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

interface LanguageProviderProps {
  children: ReactNode;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
  const [mode, setModeState] = useState<LanguageMode>(() => {
    // Load from localStorage or default to 'simple'
    const saved = localStorage.getItem('language_mode');
    return (saved as LanguageMode) || 'simple';
  });

  const [texts, setTexts] = useState<Record<string, Record<string, string>>>({});

  const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://agente-coruja-1.preview.emergentagent.com';

  // Save to localStorage whenever mode changes
  useEffect(() => {
    localStorage.setItem('language_mode', mode);
  }, [mode]);

  const setMode = (newMode: LanguageMode) => {
    setModeState(newMode);
  };

  const toggleMode = () => {
    setModeState(prev => prev === 'simple' ? 'technical' : 'simple');
  };

  const loadTexts = async (context: string) => {
    try {
      const response = await fetch(`${backendUrl}/api/adaptive-texts/${context}?mode=${mode}`);
      
      if (!response.ok) {
        console.error('Failed to load adaptive texts');
        return;
      }

      const data = await response.json();
      
      if (data.success) {
        setTexts(prev => ({
          ...prev,
          [context]: data.texts
        }));
      }
    } catch (error) {
      console.error('Error loading adaptive texts:', error);
    }
  };

  const getText = (context: string, key: string): string => {
    return texts[context]?.[key] || `[${key}]`;
  };

  return (
    <LanguageContext.Provider 
      value={{ 
        mode, 
        setMode, 
        toggleMode, 
        texts, 
        loadTexts, 
        getText 
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};

// Custom hook to use language context
export const useLanguage = () => {
  const context = useContext(LanguageContext);
  
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  
  return context;
};

// Hook to load and use texts for a specific context
export const useAdaptiveTexts = (context: string) => {
  const { mode, texts, loadTexts, getText } = useLanguage();

  useEffect(() => {
    if (!texts[context]) {
      loadTexts(context);
    }
  }, [context, mode]);

  // Reload texts when mode changes
  useEffect(() => {
    loadTexts(context);
  }, [mode]);

  const t = (key: string) => getText(context, key);

  return { texts: texts[context] || {}, t, mode };
};

export default LanguageContext;
