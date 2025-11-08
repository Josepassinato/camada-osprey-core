import React, { createContext, useContext, useState, useEffect } from 'react';

interface ProcessTypeContextType {
  processType: 'consular' | 'change_of_status' | null;
  setProcessType: (type: 'consular' | 'change_of_status') => void;
  clearProcessType: () => void;
  isConsular: boolean;
  isChangeOfStatus: boolean;
  getDisplayName: () => string;
  getIcon: () => string;
  getColor: () => string;
}

const ProcessTypeContext = createContext<ProcessTypeContextType | undefined>(undefined);

export const ProcessTypeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [processType, setProcessTypeState] = useState<'consular' | 'change_of_status' | null>(null);

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('osprey_process_type');
    if (saved === 'consular' || saved === 'change_of_status') {
      setProcessTypeState(saved);
    }
  }, []);

  const setProcessType = (type: 'consular' | 'change_of_status') => {
    setProcessTypeState(type);
    localStorage.setItem('osprey_process_type', type);
    console.log('🔖 Process type set:', type);
  };

  const clearProcessType = () => {
    setProcessTypeState(null);
    localStorage.removeItem('osprey_process_type');
    console.log('🔖 Process type cleared');
  };

  const isConsular = processType === 'consular';
  const isChangeOfStatus = processType === 'change_of_status';

  const getDisplayName = () => {
    if (processType === 'consular') return 'Processo Consular';
    if (processType === 'change_of_status') return 'Mudança de Status';
    return '';
  };

  const getIcon = () => {
    if (processType === 'consular') return '✈️';
    if (processType === 'change_of_status') return '🏠';
    return '';
  };

  const getColor = () => {
    if (processType === 'consular') return 'blue';
    if (processType === 'change_of_status') return 'orange';
    return 'gray';
  };

  const value = {
    processType,
    setProcessType,
    clearProcessType,
    isConsular,
    isChangeOfStatus,
    getDisplayName,
    getIcon,
    getColor,
  };

  return (
    <ProcessTypeContext.Provider value={value}>
      {children}
    </ProcessTypeContext.Provider>
  );
};

export const useProcessType = () => {
  const context = useContext(ProcessTypeContext);
  if (context === undefined) {
    throw new Error('useProcessType must be used within a ProcessTypeProvider');
  }
  return context;
};

export default ProcessTypeContext;
