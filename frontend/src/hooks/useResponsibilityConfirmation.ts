import { useState } from 'react';

interface ConfirmationData {
  type: 'document_authenticity' | 'form_data_review' | 'letter_verification' | 'final_declaration';
  confirmations: Record<string, boolean>;
  digitalSignature?: string;
  timestamp: string;
  userAgent: string;
  data?: any;
}

export const useResponsibilityConfirmation = () => {
  const [isConfirming, setIsConfirming] = useState(false);
  const [confirmationStatus, setConfirmationStatus] = useState<Record<string, boolean>>({});

  const recordConfirmation = async (caseId: string, confirmationData: ConfirmationData) => {
    try {
      setIsConfirming(true);

      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/responsibility/confirm`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          caseId,
          ...confirmationData
        }),
      });

      if (!response.ok) {
        throw new Error('Falha ao registrar confirmação');
      }

      const result = await response.json();
      
      // Update local status
      setConfirmationStatus(prev => ({
        ...prev,
        [confirmationData.type]: true
      }));

      return result;
    } catch (error) {
      console.error('Error recording confirmation:', error);
      throw error;
    } finally {
      setIsConfirming(false);
    }
  };

  const getConfirmationStatus = async (caseId: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/responsibility/status/${caseId}`);
      
      if (!response.ok) {
        throw new Error('Falha ao buscar status das confirmações');
      }

      const result = await response.json();
      setConfirmationStatus(result.status);
      
      return result;
    } catch (error) {
      console.error('Error getting confirmation status:', error);
      throw error;
    }
  };

  const isStepUnlocked = (step: string): boolean => {
    const stepRequirements: Record<string, string[]> = {
      'document_upload': [],
      'story_telling': ['document_authenticity'],
      'friendly_form': ['document_authenticity'],
      'visual_review': ['document_authenticity', 'form_data_review'],
      'payment': ['document_authenticity', 'form_data_review', 'letter_verification'],
      'download': ['document_authenticity', 'form_data_review', 'letter_verification', 'final_declaration']
    };

    const requirements = stepRequirements[step] || [];
    return requirements.every(requirement => confirmationStatus[requirement]);
  };

  const getRequiredConfirmations = (step: string): string[] => {
    const stepRequirements: Record<string, string[]> = {
      'document_upload': [],
      'story_telling': ['document_authenticity'],
      'friendly_form': ['document_authenticity'], 
      'visual_review': ['document_authenticity', 'form_data_review'],
      'payment': ['document_authenticity', 'form_data_review', 'letter_verification'],
      'download': ['document_authenticity', 'form_data_review', 'letter_verification', 'final_declaration']
    };

    const requirements = stepRequirements[step] || [];
    return requirements.filter(requirement => !confirmationStatus[requirement]);
  };

  const getProgressPercentage = (): number => {
    const totalSteps = ['document_authenticity', 'form_data_review', 'letter_verification', 'final_declaration'];
    const completedSteps = totalSteps.filter(step => confirmationStatus[step]);
    return (completedSteps.length / totalSteps.length) * 100;
  };

  return {
    isConfirming,
    confirmationStatus,
    recordConfirmation,
    getConfirmationStatus,
    isStepUnlocked,
    getRequiredConfirmations,
    getProgressPercentage
  };
};

export default useResponsibilityConfirmation;