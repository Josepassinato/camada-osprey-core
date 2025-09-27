import { useState, useEffect, useCallback, useRef } from 'react';
import { useLocation, useParams } from 'react-router-dom';

interface FieldState {
  name: string;
  label?: string;
  value?: string;
  valid: boolean;
  errors: string[];
  required: boolean;
}

interface SectionState {
  id: string;
  label: string;
  status: "todo" | "in_progress" | "complete";
  missing: string[];
  percent: number;
}

interface Snapshot {
  userId: string;
  formId: string;
  stepId: string;
  url: string;
  timestamp: string;
  sections: SectionState[];
  fields: FieldState[];
  siteVersionHash: string;
}

interface UseFormSnapshotOptions {
  enabled?: boolean;
  autoSend?: boolean;
  debounceMs?: number;
  onSnapshotSent?: (snapshot: Snapshot) => void;
  onError?: (error: string) => void;
}

export const useFormSnapshot = (
  formData: any,
  options: UseFormSnapshotOptions = {}
) => {
  const {
    enabled = true,
    autoSend = true,
    debounceMs = 1000,
    onSnapshotSent,
    onError
  } = options;

  const location = useLocation();
  const params = useParams();
  const [lastSnapshot, setLastSnapshot] = useState<Snapshot | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastFormDataRef = useRef<string>('');

  // Generate snapshot from current form state
  const generateSnapshot = useCallback((): Snapshot | null => {
    if (!enabled || !formData) {
      return null;
    }

    setIsGenerating(true);
    
    try {
      // Determine current step/form based on URL and params
      const stepId = getStepIdFromUrl(location.pathname);
      const formId = params.caseId || 'auto-application';
      const userId = getCurrentUserId();

      // Analyze form sections and fields
      const sections = analyzeSections(formData, stepId);
      const fields = analyzeFields(formData);

      const snapshot: Snapshot = {
        userId,
        formId,
        stepId,
        url: location.pathname,
        timestamp: new Date().toISOString(),
        sections,
        fields,
        siteVersionHash: "v1.0.0"
      };

      setLastSnapshot(snapshot);
      return snapshot;

    } catch (error) {
      console.error('Error generating snapshot:', error);
      onError?.('Erro ao gerar snapshot do formulário');
      return null;
    } finally {
      setIsGenerating(false);
    }
  }, [enabled, formData, location.pathname, params.caseId, onError]);

  // Send snapshot to voice agent or external service
  const sendSnapshot = useCallback((snapshot?: Snapshot) => {
    const snapshotToSend = snapshot || lastSnapshot;
    
    if (!snapshotToSend) {
      console.warn('No snapshot to send');
      return false;
    }

    try {
      // Send via custom event for VoiceMic component to listen
      window.dispatchEvent(new CustomEvent('formSnapshotUpdate', {
        detail: { snapshot: snapshotToSend }
      }));

      onSnapshotSent?.(snapshotToSend);
      console.log('Form snapshot sent:', snapshotToSend);
      return true;

    } catch (error) {
      console.error('Error sending snapshot:', error);
      onError?.('Erro ao enviar snapshot');
      return false;
    }
  }, [lastSnapshot, onSnapshotSent, onError]);

  // Auto-generate and send snapshot when form data changes
  useEffect(() => {
    if (!enabled || !autoSend) {
      return;
    }

    // Check if form data actually changed
    const currentFormDataStr = JSON.stringify(formData);
    if (currentFormDataStr === lastFormDataRef.current) {
      return;
    }
    lastFormDataRef.current = currentFormDataStr;

    // Clear existing timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    // Debounce snapshot generation and sending
    debounceTimeoutRef.current = setTimeout(() => {
      const snapshot = generateSnapshot();
      if (snapshot) {
        sendSnapshot(snapshot);
      }
    }, debounceMs);

    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [formData, enabled, autoSend, debounceMs, generateSnapshot, sendSnapshot]);

  return {
    snapshot: lastSnapshot,
    generateSnapshot,
    sendSnapshot,
    isGenerating
  };
};

// Helper functions

function getStepIdFromUrl(pathname: string): string {
  // Extract step ID from URL path
  if (pathname.includes('/basic-data')) return 'personal';
  if (pathname.includes('/documents')) return 'documents';
  if (pathname.includes('/story')) return 'story';
  if (pathname.includes('/friendly-form')) return 'form';
  if (pathname.includes('/review')) return 'review';
  if (pathname.includes('/payment')) return 'payment';
  
  // Default mappings
  const pathSegments = pathname.split('/').filter(Boolean);
  const lastSegment = pathSegments[pathSegments.length - 1];
  
  const stepMappings: { [key: string]: string } = {
    'select-form': 'selection',
    'basic-data': 'personal', 
    'documents': 'documents',
    'story': 'story',
    'friendly-form': 'form',
    'review': 'review',
    'payment': 'payment'
  };
  
  return stepMappings[lastSegment] || 'unknown';
}

function getCurrentUserId(): string {
  // Try to get user ID from session or localStorage
  const sessionToken = localStorage.getItem('osprey_session_token');
  
  if (sessionToken && sessionToken !== 'null') {
    return `session_${sessionToken.slice(-8)}`;
  }
  
  return 'anonymous_user';
}

function analyzeSections(formData: any, stepId: string): SectionState[] {
  const sections: SectionState[] = [];

  // Define section structure based on step
  const sectionDefinitions = getSectionDefinitions(stepId);

  sectionDefinitions.forEach(sectionDef => {
    const sectionData = formData[sectionDef.key] || {};
    const requiredFields = sectionDef.requiredFields || [];
    
    // Calculate missing required fields
    const missing = requiredFields.filter(field => {
      const value = sectionData[field];
      return !value || (typeof value === 'string' && value.trim() === '');
    });

    // Calculate completion percentage
    const totalFields = requiredFields.length;
    const completedFields = totalFields - missing.length;
    const percent = totalFields > 0 ? Math.round((completedFields / totalFields) * 100) : 100;

    // Determine status
    let status: "todo" | "in_progress" | "complete" = "todo";
    if (percent === 100) {
      status = "complete";
    } else if (percent > 0) {
      status = "in_progress";  
    }

    sections.push({
      id: sectionDef.id,
      label: sectionDef.label,
      status,
      missing,
      percent
    });
  });

  return sections;
}

function analyzeFields(formData: any): FieldState[] {
  const fields: FieldState[] = [];

  // Recursively analyze all form fields
  const analyzeObject = (obj: any, prefix: string = '') => {
    Object.entries(obj || {}).forEach(([key, value]) => {
      const fieldName = prefix ? `${prefix}.${key}` : key;
      
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        // Recursive analysis for nested objects
        analyzeObject(value, fieldName);
      } else {
        // Analyze individual field
        const field = analyzeField(fieldName, value);
        if (field) {
          fields.push(field);
        }
      }
    });
  };

  analyzeObject(formData);
  return fields;
}

function analyzeField(name: string, value: any): FieldState | null {
  // Skip non-form fields
  if (name.startsWith('_') || ['timestamp', 'id', 'case_id'].includes(name)) {
    return null;
  }

  const stringValue = value?.toString() || '';
  const isRequired = isFieldRequired(name);
  
  // Validate field value
  const validation = validateFieldValue(name, stringValue);

  return {
    name,
    label: getFieldLabel(name),
    value: stringValue,
    valid: validation.isValid,
    errors: validation.errors,
    required: isRequired
  };
}

function getSectionDefinitions(stepId: string) {
  const definitions: { [key: string]: any[] } = {
    personal: [
      {
        id: 'personal_info',
        key: 'personal',
        label: 'Informações Pessoais',
        requiredFields: ['firstName', 'lastName', 'dateOfBirth', 'nationality']
      },
      {
        id: 'contact_info',
        key: 'contact',
        label: 'Informações de Contato', 
        requiredFields: ['email', 'phone']
      }
    ],
    documents: [
      {
        id: 'required_docs',
        key: 'documents',
        label: 'Documentos Obrigatórios',
        requiredFields: ['passport', 'photos']
      }
    ],
    form: [
      {
        id: 'personal',
        key: 'personal',
        label: 'Dados Pessoais',
        requiredFields: ['firstName', 'lastName', 'dateOfBirth']
      },
      {
        id: 'address',
        key: 'address', 
        label: 'Endereço',
        requiredFields: ['currentAddress', 'city', 'zipCode']
      },
      {
        id: 'employment',
        key: 'employment',
        label: 'Emprego',
        requiredFields: ['employerName', 'jobTitle']
      }
    ]
  };

  return definitions[stepId] || [
    {
      id: 'general',
      key: 'general',
      label: 'Informações Gerais',
      requiredFields: []
    }
  ];
}

function isFieldRequired(fieldName: string): boolean {
  const requiredFields = [
    'firstName', 'lastName', 'dateOfBirth', 'nationality',
    'email', 'phone', 'currentAddress', 'city', 'zipCode',
    'passport', 'photos', 'employerName', 'jobTitle'
  ];
  
  return requiredFields.some(required => 
    fieldName.includes(required) || fieldName.endsWith(required)
  );
}

function getFieldLabel(fieldName: string): string {
  const labelMappings: { [key: string]: string } = {
    firstName: 'Nome',
    lastName: 'Sobrenome', 
    dateOfBirth: 'Data de Nascimento',
    nationality: 'Nacionalidade',
    email: 'E-mail',
    phone: 'Telefone',
    currentAddress: 'Endereço Atual',
    city: 'Cidade',
    zipCode: 'CEP',
    employerName: 'Nome do Empregador',
    jobTitle: 'Cargo'
  };

  // Try exact match first
  if (labelMappings[fieldName]) {
    return labelMappings[fieldName];
  }

  // Try partial matches
  for (const [key, label] of Object.entries(labelMappings)) {
    if (fieldName.includes(key)) {
      return label;
    }
  }

  // Default: capitalize and clean field name
  return fieldName
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase())
    .trim();
}

function validateFieldValue(fieldName: string, value: string): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!value || value.trim() === '') {
    if (isFieldRequired(fieldName)) {
      errors.push('Campo obrigatório não preenchido');
    }
    return { isValid: errors.length === 0, errors };
  }

  // Email validation
  if (fieldName.includes('email') || fieldName.includes('Email')) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      errors.push('Formato de e-mail inválido');
    }
  }

  // Phone validation
  if (fieldName.includes('phone') || fieldName.includes('Phone')) {
    const phoneRegex = /[\d\s\-\(\)\+]{10,}/;
    if (!phoneRegex.test(value)) {
      errors.push('Formato de telefone inválido');
    }
  }

  // Date validation
  if (fieldName.includes('date') || fieldName.includes('Date')) {
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(value)) {
      errors.push('Data deve estar no formato YYYY-MM-DD');
    }
  }

  // Name validation
  if (fieldName.includes('name') || fieldName.includes('Name')) {
    if (value.length < 2) {
      errors.push('Nome deve ter pelo menos 2 caracteres');
    }
  }

  return { isValid: errors.length === 0, errors };
}

export default useFormSnapshot;