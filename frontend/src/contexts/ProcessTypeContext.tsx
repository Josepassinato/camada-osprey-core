import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type ProcessType = 'consular' | 'change_of_status' | null;

interface ProcessTypeContextType {
  processType: ProcessType;
  setProcessType: (type: ProcessType) => void;
  clearProcessType: () => void;
}

const ProcessTypeContext = createContext<ProcessTypeContextType | undefined>(undefined);

export const ProcessTypeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [processType, setProcessTypeState] = useState<ProcessType>(() => {
    // Initialize from localStorage on mount
    const stored = localStorage.getItem('osprey_process_type');
    return stored ? (stored as ProcessType) : null;
  });

  const setProcessType = (type: ProcessType) => {
    console.log('🔔 ProcessTypeContext: setProcessType called with', type);
    setProcessTypeState(type);
    if (type) {
      localStorage.setItem('osprey_process_type', type);
      console.log('✅ ProcessTypeContext: Saved to localStorage', localStorage.getItem('osprey_process_type'));
    } else {
      localStorage.removeItem('osprey_process_type');
    }
  };

  const clearProcessType = () => {
    setProcessTypeState(null);
    localStorage.removeItem('osprey_process_type');
  };

  // Listen for case data and update process type
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'osprey_process_type') {
        setProcessTypeState(e.newValue as ProcessType);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return (
    <ProcessTypeContext.Provider value={{ processType, setProcessType, clearProcessType }}>
      {children}
    </ProcessTypeContext.Provider>
  );
};

export const useProcessType = () => {
  const context = useContext(ProcessTypeContext);
  if (!context) {
    throw new Error('useProcessType must be used within ProcessTypeProvider');
  }
  return context;
};
