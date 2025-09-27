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
  autoGenerate?: boolean;
  debounceMs?: number;
  onSnapshotUpdate?: (snapshot: Snapshot) => void;
  onError?: (error: string) => void;
}

export const useFormSnapshot = (
  formData: any,
  options: UseFormSnapshotOptions = {}
) => {
  const {
    enabled = true,
    autoGenerate = true,
    debounceMs = 500,
    onSnapshotUpdate,
    onError
  } = options;

  const location = useLocation();
  const params = useParams();
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
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
      const formId = params.caseId || 'osprey-self-app-v1';
      const userId = getCurrentUserId();

      // Analyze form sections and fields
      const sections = analyzeSections(formData, stepId);
      const fields = analyzeFields(formData, stepId);

      const newSnapshot: Snapshot = {
        userId,
        formId,
        stepId,
        url: location.pathname,
        timestamp: new Date().toISOString(),
        sections,
        fields,
        siteVersionHash: "v1.0.0"
      };

      setSnapshot(newSnapshot);
      onSnapshotUpdate?.(newSnapshot);
      return newSnapshot;

    } catch (error) {
      console.error('Error generating snapshot:', error);
      onError?.('Erro ao gerar snapshot do formulário');
      return null;
    } finally {
      setIsGenerating(false);
    }
  }, [enabled, formData, location.pathname, params.caseId, onSnapshotUpdate, onError]);

  // Auto-generate snapshot when form data changes
  useEffect(() => {
    if (!enabled || !autoGenerate || !formData) {
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

    // Debounce snapshot generation
    debounceTimeoutRef.current = setTimeout(() => {
      generateSnapshot();
    }, debounceMs);

    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [formData, enabled, autoGenerate, debounceMs, generateSnapshot]);

  return {
    snapshot,
    generateSnapshot,
    isGenerating
  };
};

// Helper functions

function getStepIdFromUrl(pathname: string): string {
  // Map URL paths to step IDs
  if (pathname.includes('/basic-data')) return 'personal';
  if (pathname.includes('/documents')) return 'documents';
  if (pathname.includes('/story')) return 'story';
  if (pathname.includes('/friendly-form')) return 'form';
  if (pathname.includes('/review')) return 'review';
  if (pathname.includes('/payment')) return 'payment';
  
  // Default fallback
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
  // Get user ID from session or generate anonymous ID
  const sessionToken = localStorage.getItem('osprey_session_token');
  
  if (sessionToken && sessionToken !== 'null') {
    return `user_${sessionToken.slice(-8)}`;
  }
  
  // Generate anonymous user ID
  let anonymousId = localStorage.getItem('osprey_anonymous_id');
  if (!anonymousId) {
    anonymousId = `anon_${Date.now().toString(36)}_${Math.random().toString(36).substr(2, 5)}`;
    localStorage.setItem('osprey_anonymous_id', anonymousId);
  }
  
  return anonymousId;
}

function analyzeSections(formData: any, stepId: string): SectionState[] {
  const sections: SectionState[] = [];

  // Define section structure based on current step
  const sectionDefinitions = getSectionDefinitions(stepId);

  sectionDefinitions.forEach(sectionDef => {
    const sectionData = getSectionData(formData, sectionDef.dataPath);
    const requiredFields = sectionDef.requiredFields || [];
    
    // Calculate missing required fields
    const missing = requiredFields.filter(field => {
      const value = getNestedValue(sectionData, field);
      return !value || (typeof value === 'string' && value.trim() === '');
    });

    // Calculate completion percentage
    const totalFields = requiredFields.length || 1;
    const completedFields = totalFields - missing.length;
    const percent = Math.round((completedFields / totalFields) * 100);

    // Determine status
    let status: "todo" | "in_progress" | "complete" = "todo";
    if (percent === 100) {
      status = "complete";
    } else if (percent > 0 || Object.keys(sectionData || {}).length > 0) {
      status = "in_progress";  
    }

    sections.push({
      id: sectionDef.id,
      label: sectionDef.label,
      status,
      missing: missing.map(field => sectionDef.fieldLabels?.[field] || field),
      percent
    });
  });

  return sections;
}

function analyzeFields(formData: any, stepId: string): FieldState[] {
  const fields: FieldState[] = [];
  
  // Get field definitions for current step
  const fieldDefinitions = getFieldDefinitions(stepId);
  
  fieldDefinitions.forEach(fieldDef => {
    const value = getNestedValue(formData, fieldDef.path);
    const stringValue = value?.toString() || '';
    
    // Validate field value
    const validation = validateFieldValue(fieldDef, stringValue);
    
    fields.push({
      name: fieldDef.path,
      label: fieldDef.label,
      value: stringValue,
      valid: validation.isValid,
      errors: validation.errors,
      required: fieldDef.required || false
    });
  });

  return fields;
}

function getSectionDefinitions(stepId: string) {
  const definitions: { [key: string]: any[] } = {
    personal: [
      {
        id: 'personal_info',
        label: 'Informações Pessoais',
        dataPath: '',
        requiredFields: ['firstName', 'lastName', 'dateOfBirth', 'nationality'],
        fieldLabels: {
          firstName: 'Nome',
          lastName: 'Sobrenome',
          dateOfBirth: 'Data de Nascimento',
          nationality: 'Nacionalidade'
        }
      },
      {
        id: 'contact_info',
        label: 'Contato',
        dataPath: '',
        requiredFields: ['email', 'phone'],
        fieldLabels: {
          email: 'E-mail',
          phone: 'Telefone'
        }
      }
    ],
    documents: [
      {
        id: 'required_docs',
        label: 'Documentos Obrigatórios',
        dataPath: 'documents',
        requiredFields: ['passport', 'photos'],
        fieldLabels: {
          passport: 'Passaporte',
          photos: 'Fotos'
        }
      }
    ],
    form: [
      {
        id: 'personal',
        label: 'Dados Pessoais',
        dataPath: 'personal',
        requiredFields: ['firstName', 'lastName', 'dateOfBirth'],
        fieldLabels: {
          firstName: 'Nome',
          lastName: 'Sobrenome', 
          dateOfBirth: 'Data de Nascimento'
        }
      },
      {
        id: 'address',
        label: 'Endereço',
        dataPath: 'address',
        requiredFields: ['currentAddress', 'city', 'zipCode'],
        fieldLabels: {
          currentAddress: 'Endereço Atual',
          city: 'Cidade',
          zipCode: 'CEP'
        }
      }
    ]
  };

  return definitions[stepId] || [
    {
      id: 'general',
      label: 'Informações Gerais',
      dataPath: '',
      requiredFields: []
    }
  ];
}

function getFieldDefinitions(stepId: string) {
  const definitions: { [key: string]: any[] } = {
    personal: [
      { path: 'firstName', label: 'Nome', required: true, type: 'name' },
      { path: 'lastName', label: 'Sobrenome', required: true, type: 'name' },
      { path: 'middleName', label: 'Nome do Meio', required: false, type: 'name' },
      { path: 'dateOfBirth', label: 'Data de Nascimento', required: true, type: 'date' },
      { path: 'nationality', label: 'Nacionalidade', required: true, type: 'text' },
      { path: 'email', label: 'E-mail', required: true, type: 'email' },
      { path: 'phone', label: 'Telefone', required: true, type: 'phone' }
    ],
    form: [
      { path: 'personal.firstName', label: 'Nome', required: true, type: 'name' },
      { path: 'personal.lastName', label: 'Sobrenome', required: true, type: 'name' },
      { path: 'personal.dateOfBirth', label: 'Data de Nascimento', required: true, type: 'date' },
      { path: 'address.currentAddress', label: 'Endereço Atual', required: true, type: 'address' },
      { path: 'address.city', label: 'Cidade', required: true, type: 'text' },
      { path: 'address.zipCode', label: 'CEP', required: true, type: 'zip' }
    ]
  };

  return definitions[stepId] || [];
}

function getSectionData(formData: any, dataPath: string) {
  if (!dataPath) return formData;
  return getNestedValue(formData, dataPath);
}

function getNestedValue(obj: any, path: string): any {
  if (!path || !obj) return obj;
  
  const keys = path.split('.');
  let current = obj;
  
  for (const key of keys) {
    if (current && typeof current === 'object' && key in current) {
      current = current[key];
    } else {
      return undefined;
    }
  }
  
  return current;
}

function validateFieldValue(fieldDef: any, value: string): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Required field validation
  if (fieldDef.required && (!value || value.trim() === '')) {
    errors.push('Campo obrigatório');
    return { isValid: false, errors };
  }

  // Skip other validations if empty and not required
  if (!value || value.trim() === '') {
    return { isValid: true, errors: [] };
  }

  // Type-specific validation
  switch (fieldDef.type) {
    case 'email':
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        errors.push('Formato de e-mail inválido');
      }
      break;

    case 'phone':
      const phoneRegex = /[\d\s\-\(\)\+]{10,}/;
      if (!phoneRegex.test(value)) {
        errors.push('Formato de telefone inválido');
      }
      break;

    case 'date':
      const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
      if (!dateRegex.test(value)) {
        errors.push('Data deve estar no formato YYYY-MM-DD');
      } else {
        const date = new Date(value);
        const today = new Date();
        if (date > today) {
          errors.push('Data não pode ser no futuro');
        }
      }
      break;

    case 'zip':
      const cleanZip = value.replace(/\D/g, '');
      if (cleanZip.length !== 5) {
        errors.push('CEP deve ter 5 dígitos');
      }
      break;

    case 'name':
      if (value.length < 2) {
        errors.push('Nome deve ter pelo menos 2 caracteres');
      }
      if (!/^[A-Za-zÀ-ÿ\s'-]+$/.test(value)) {
        errors.push('Nome deve conter apenas letras');
      }
      break;
  }

  return { isValid: errors.length === 0, errors };
}

export default useFormSnapshot;