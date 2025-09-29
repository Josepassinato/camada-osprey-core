import { useState, useEffect, useCallback } from 'react';

interface GuidanceRecord {
  id: string;
  userId: string;
  visaType: string;
  step: string;
  guidanceType: 'tip' | 'warning' | 'error' | 'achievement' | 'chat';
  message: string;
  timestamp: Date;
  source: 'dra_paula' | 'owl_tutor' | 'dr_miguel' | 'system';
  metadata?: {
    documentType?: string;
    fieldName?: string;
    severity?: string;
    actionTaken?: string;
  };
}

interface UserProfile {
  id: string;
  preferredLanguage: 'pt' | 'en';
  visaHistory: string[];
  commonErrors: string[];
  completedSteps: string[];
  personalizedTips: string[];
  learningProgress: {
    documentsKnowledge: number;
    formsKnowledge: number;
    processKnowledge: number;
  };
}

interface UseUserGuidanceHistoryOptions {
  userId?: string;
  visaType?: string;
  maxRecords?: number;
  enablePersonalization?: boolean;
}

export const useUserGuidanceHistory = (options: UseUserGuidanceHistoryOptions = {}) => {
  const {
    userId = 'anonymous',
    visaType = 'H-1B',
    maxRecords = 100,
    enablePersonalization = true
  } = options;

  const [guidanceHistory, setGuidanceHistory] = useState<GuidanceRecord[]>([]);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user guidance history from localStorage/API
  useEffect(() => {
    const loadGuidanceHistory = async () => {
      try {
        // Try to load from localStorage first
        const localHistory = localStorage.getItem(`guidance_history_${userId}`);
        if (localHistory) {
          const parsed = JSON.parse(localHistory);
          setGuidanceHistory(parsed.map((record: any) => ({
            ...record,
            timestamp: new Date(record.timestamp)
          })));
        }

        // Load user profile
        const localProfile = localStorage.getItem(`user_profile_${userId}`);
        if (localProfile) {
          setUserProfile(JSON.parse(localProfile));
        } else {
          // Create default profile
          const defaultProfile: UserProfile = {
            id: userId,
            preferredLanguage: 'pt',
            visaHistory: [visaType],
            commonErrors: [],
            completedSteps: [],
            personalizedTips: [],
            learningProgress: {
              documentsKnowledge: 0,
              formsKnowledge: 0,
              processKnowledge: 0
            }
          };
          setUserProfile(defaultProfile);
          localStorage.setItem(`user_profile_${userId}`, JSON.stringify(defaultProfile));
        }

      } catch (error) {
        console.error('Error loading guidance history:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadGuidanceHistory();
  }, [userId, visaType]);

  // Save guidance history to localStorage
  const saveGuidanceHistory = useCallback((history: GuidanceRecord[]) => {
    try {
      localStorage.setItem(`guidance_history_${userId}`, JSON.stringify(history));
    } catch (error) {
      console.error('Error saving guidance history:', error);
    }
  }, [userId]);

  // Save user profile
  const saveUserProfile = useCallback((profile: UserProfile) => {
    try {
      localStorage.setItem(`user_profile_${userId}`, JSON.stringify(profile));
      setUserProfile(profile);
    } catch (error) {
      console.error('Error saving user profile:', error);
    }
  }, [userId]);

  // Add new guidance record
  const addGuidanceRecord = useCallback((
    guidanceType: GuidanceRecord['guidanceType'],
    message: string,
    source: GuidanceRecord['source'],
    step: string,
    metadata?: GuidanceRecord['metadata']
  ) => {
    const newRecord: GuidanceRecord = {
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      userId,
      visaType,
      step,
      guidanceType,
      message,
      timestamp: new Date(),
      source,
      metadata
    };

    setGuidanceHistory(prev => {
      const updated = [newRecord, ...prev].slice(0, maxRecords);
      saveGuidanceHistory(updated);
      return updated;
    });

    // Update user profile based on guidance
    if (userProfile && enablePersonalization) {
      updateUserProfile(newRecord);
    }

    return newRecord;
  }, [userId, visaType, maxRecords, userProfile, enablePersonalization, saveGuidanceHistory]);

  // Update user profile based on guidance patterns
  const updateUserProfile = useCallback((record: GuidanceRecord) => {
    if (!userProfile) return;

    const updatedProfile = { ...userProfile };

    // Track common errors
    if (record.guidanceType === 'error') {
      const errorPattern = `${record.step}_${record.metadata?.fieldName || 'unknown'}`;
      if (!updatedProfile.commonErrors.includes(errorPattern)) {
        updatedProfile.commonErrors.push(errorPattern);
      }
    }

    // Track completed steps
    if (record.guidanceType === 'achievement') {
      if (!updatedProfile.completedSteps.includes(record.step)) {
        updatedProfile.completedSteps.push(record.step);
      }
    }

    // Update learning progress
    switch (record.step) {
      case 'documents':
        updatedProfile.learningProgress.documentsKnowledge = Math.min(
          updatedProfile.learningProgress.documentsKnowledge + 1,
          100
        );
        break;
      case 'friendly_form':
      case 'uscis_form':
        updatedProfile.learningProgress.formsKnowledge = Math.min(
          updatedProfile.learningProgress.formsKnowledge + 1,
          100
        );
        break;
      case 'ai_review':
      case 'payment':
        updatedProfile.learningProgress.processKnowledge = Math.min(
          updatedProfile.learningProgress.processKnowledge + 1,
          100
        );
        break;
    }

    saveUserProfile(updatedProfile);
  }, [userProfile, saveUserProfile]);

  // Get personalized tips based on history
  const getPersonalizedTips = useCallback((currentStep: string): string[] => {
    if (!userProfile || !enablePersonalization) return [];

    const tips: string[] = [];

    // Tips based on common errors
    userProfile.commonErrors.forEach(errorPattern => {
      const [step, field] = errorPattern.split('_');
      if (step === currentStep) {
        switch (field) {
          case 'full_name':
            tips.push('💡 Lembre-se: o nome deve ser idêntico ao passaporte');
            break;
          case 'date_of_birth':
            tips.push('📅 Formato de data: MM/DD/YYYY para formulários USCIS');
            break;
          case 'passport':
            tips.push('📔 Verifique se o passaporte tem pelo menos 6 meses de validade');
            break;
        }
      }
    });

    // Tips based on visa history
    if (userProfile.visaHistory.length > 1) {
      tips.push('🎯 Dica: Você já tem experiência com outros vistos. Aproveite esse conhecimento!');
    }

    // Tips based on learning progress
    if (userProfile.learningProgress.documentsKnowledge < 50 && currentStep === 'documents') {
      tips.push('📚 Dica: Revise os requisitos específicos de documentos para seu tipo de visto');
    }

    return tips.slice(0, 3); // Max 3 personalized tips
  }, [userProfile, enablePersonalization]);

  // Get guidance statistics
  const getGuidanceStats = useCallback(() => {
    if (!guidanceHistory.length) return null;

    const stats = {
      totalGuidances: guidanceHistory.length,
      byType: {} as Record<string, number>,
      bySource: {} as Record<string, number>,
      byStep: {} as Record<string, number>,
      mostCommonErrors: [] as string[],
      learningProgress: userProfile?.learningProgress || {
        documentsKnowledge: 0,
        formsKnowledge: 0,
        processKnowledge: 0
      }
    };

    guidanceHistory.forEach(record => {
      // Count by type
      stats.byType[record.guidanceType] = (stats.byType[record.guidanceType] || 0) + 1;
      
      // Count by source
      stats.bySource[record.source] = (stats.bySource[record.source] || 0) + 1;
      
      // Count by step
      stats.byStep[record.step] = (stats.byStep[record.step] || 0) + 1;
    });

    // Get most common errors
    if (userProfile) {
      stats.mostCommonErrors = userProfile.commonErrors.slice(0, 5);
    }

    return stats;
  }, [guidanceHistory, userProfile]);

  // Clear guidance history
  const clearGuidanceHistory = useCallback(() => {
    setGuidanceHistory([]);
    localStorage.removeItem(`guidance_history_${userId}`);
  }, [userId]);

  // Export guidance history
  const exportGuidanceHistory = useCallback(() => {
    const exportData = {
      userProfile,
      guidanceHistory,
      exportDate: new Date().toISOString(),
      stats: getGuidanceStats()
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `guidance_history_${userId}_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [userId, userProfile, guidanceHistory, getGuidanceStats]);

  return {
    // State
    guidanceHistory,
    userProfile,
    isLoading,

    // Actions
    addGuidanceRecord,
    updateUserProfile,
    clearGuidanceHistory,
    exportGuidanceHistory,

    // Computed
    getPersonalizedTips,
    getGuidanceStats
  };
};

export default useUserGuidanceHistory;