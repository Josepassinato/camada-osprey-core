import { useState } from 'react';
import { makeApiCall } from '@/utils/api';

export interface UseDisclaimerProps {
  caseId: string;
  onSuccess?: (stage: string) => void;
  onError?: (error: string) => void;
}

export interface DisclaimerStatus {
  case_id: string;
  acceptances: Array<{
    id: string;
    stage: string;
    consent_hash: string;
    timestamp: string;
    ip_address?: string;
    user_id?: string;
  }>;
  validation: {
    all_required_accepted: boolean;
    missing_stages: string[];
    accepted_stages: string[];
    total_acceptances: number;
  };
  ready_for_final: boolean;
}

export const useDisclaimer = ({ caseId, onSuccess, onError }: UseDisclaimerProps) => {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<DisclaimerStatus | null>(null);

  const recordAcceptance = async (
    stage: 'documents' | 'forms' | 'cover_letter' | 'review' | 'final',
    consentHash: string,
    userId?: string,
    stageData?: Record<string, any>
  ) => {
    try {
      setLoading(true);
      
      const response = await makeApiCall('/disclaimer/record', {
        method: 'POST',
        body: JSON.stringify({
          case_id: caseId,
          stage: stage,
          consent_hash: consentHash,
          user_id: userId,
          ip_address: '', // Could be populated from client-side detection
          user_agent: navigator.userAgent,
          stage_data: {
            ...stageData,
            timestamp: new Date().toISOString()
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        onSuccess?.(stage);
        await loadStatus(); // Reload status after recording
        return data;
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Falha ao registrar aceite');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao registrar aceite';
      onError?.(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const loadStatus = async () => {
    try {
      setLoading(true);
      
      const response = await makeApiCall(`/disclaimer/status/${caseId}`, {
        method: 'GET'
      });

      if (response.ok) {
        const data = await response.json();
        setStatus(data);
        return data;
      } else {
        throw new Error('Falha ao carregar status dos disclaimers');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao carregar status';
      onError?.(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const validateCompliance = async () => {
    try {
      const response = await makeApiCall(`/disclaimer/validate/${caseId}`, {
        method: 'GET'
      });

      if (response.ok) {
        const data = await response.json();
        return data.compliance;
      } else {
        throw new Error('Falha ao validar compliance');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao validar compliance';
      onError?.(errorMessage);
      throw error;
    }
  };

  const checkStageRequired = async (stage: string) => {
    try {
      const response = await makeApiCall('/disclaimer/check-required', {
        method: 'POST',
        body: JSON.stringify({
          case_id: caseId,
          stage: stage
        })
      });

      if (response.ok) {
        const data = await response.json();
        return data.required;
      } else {
        throw new Error('Falha ao verificar requisito');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao verificar requisito';
      onError?.(errorMessage);
      throw error;
    }
  };

  const getDisclaimerText = async (stage: string) => {
    try {
      const response = await makeApiCall(`/disclaimer/text/${stage}`, {
        method: 'GET'
      });

      if (response.ok) {
        const data = await response.json();
        return data.disclaimer_text;
      } else {
        throw new Error('Falha ao buscar texto do disclaimer');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao buscar texto';
      onError?.(errorMessage);
      throw error;
    }
  };

  const generateComplianceReport = async () => {
    try {
      const response = await makeApiCall(`/disclaimer/compliance-report/${caseId}`, {
        method: 'GET'
      });

      if (response.ok) {
        const data = await response.json();
        return data.report;
      } else {
        throw new Error('Falha ao gerar relatório de compliance');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro ao gerar relatório';
      onError?.(errorMessage);
      throw error;
    }
  };

  // Helper functions
  const isStageAccepted = (stage: string): boolean => {
    if (!status) return false;
    return status.validation.accepted_stages.includes(stage);
  };

  const getMissingStages = (): string[] => {
    if (!status) return [];
    return status.validation.missing_stages;
  };

  const isReadyForFinal = (): boolean => {
    if (!status) return false;
    return status.ready_for_final;
  };

  const getAllRequiredAccepted = (): boolean => {
    if (!status) return false;
    return status.validation.all_required_accepted;
  };

  return {
    // State
    loading,
    status,
    
    // Actions
    recordAcceptance,
    loadStatus,
    validateCompliance,
    checkStageRequired,
    getDisclaimerText,
    generateComplianceReport,
    
    // Helpers
    isStageAccepted,
    getMissingStages,
    isReadyForFinal,
    getAllRequiredAccepted
  };
};