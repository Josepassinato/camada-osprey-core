import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Clock, Info } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

interface Field {
  id: string;
  label: string;
  type: string;
  required: boolean;
  placeholder?: string;
  validation?: string;
  official_mapping?: string;
  help_text?: string;
  options?: string[];
  conditional?: string;
}

interface Section {
  id: string;
  title: string;
  description?: string;
  fields: Field[];
}

interface FormStructure {
  form_code: string;
  form_name: string;
  total_fields: number;
  estimated_time: string;
  warning?: string;
  sections: Section[];
}

interface DynamicFriendlyFormProps {
  visaType: string;
  caseId: string;
  onSubmitSuccess?: (result: any) => void;
}

export const DynamicFriendlyForm: React.FC<DynamicFriendlyFormProps> = ({
  visaType,
  caseId,
  onSubmitSuccess
}) => {
  const [structure, setStructure] = useState<FormStructure | null>(null);
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [currentSection, setCurrentSection] = useState(0);

  // Load form structure
  useEffect(() => {
    const loadStructure = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${BACKEND_URL}/api/friendly-form/structure/${visaType}`);
        
        if (!response.ok) {
          throw new Error('Não foi possível carregar a estrutura do formulário');
        }
        
        const data = await response.json();
        setStructure(data.structure);
        
        // Initialize form data with empty values
        const initialData: Record<string, any> = {};
        data.structure.sections.forEach((section: Section) => {
          section.fields.forEach((field: Field) => {
            initialData[field.id] = '';
          });
        });
        setFormData(initialData);
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    };

    loadStructure();
  }, [visaType]);

  const handleFieldChange = (fieldId: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [fieldId]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setSubmitting(true);
      setError(null);
      
      const response = await fetch(`${BACKEND_URL}/api/case/${caseId}/friendly-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          friendly_form_data: formData,
          basic_data: {
            applicant_name: formData.nome_completo,
            email: formData.email,
            passport_number: formData.numero_passaporte
          }
        })
      });
      
      if (!response.ok) {
        throw new Error('Erro ao enviar formulário');
      }
      
      const result = await response.json();
      setValidationResult(result);
      
      if (onSubmitSuccess) {
        onSubmitSuccess(result);
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao enviar formulário');
    } finally {
      setSubmitting(false);
    }
  };

  const renderField = (field: Field) => {
    const isRequired = field.required;
    const value = formData[field.id] || '';

    const commonProps = {
      id: field.id,
      value,
      onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => 
        handleFieldChange(field.id, e.target.value),
      placeholder: field.placeholder,
      required: isRequired
    };

    switch (field.type) {
      case 'text':
      case 'email':
      case 'tel':
      case 'date':
        return (
          <Input
            {...commonProps}
            type={field.type}
            className="w-full"
          />
        );
      
      case 'textarea':
        return (
          <Textarea
            {...commonProps}
            rows={4}
            className="w-full"
          />
        );
      
      case 'select':
      case 'country':
        return (
          <Select
            value={value}
            onValueChange={(val) => handleFieldChange(field.id, val)}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder={field.placeholder || "Selecione..."} />
            </SelectTrigger>
            <SelectContent>
              {field.options?.map(option => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );
      
      default:
        return <Input {...commonProps} type="text" />;
    }
  };

  const renderSection = (section: Section, index: number) => {
    if (currentSection !== index) return null;

    return (
      <Card key={section.id} className="mb-6">
        <CardHeader>
          <CardTitle className="text-2xl">{section.title}</CardTitle>
          {section.description && (
            <CardDescription>{section.description}</CardDescription>
          )}
        </CardHeader>
        <CardContent className="space-y-6">
          {section.fields.map(field => (
            <div key={field.id} className="space-y-2">
              <Label htmlFor={field.id} className="text-base font-medium">
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </Label>
              
              {renderField(field)}
              
              {field.help_text && (
                <div className="flex items-start gap-2 text-sm text-muted-foreground">
                  <Info className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>{field.help_text}</span>
                </div>
              )}
              
              {field.official_mapping && (
                <div className="text-xs text-muted-foreground">
                  Mapeado para: {field.official_mapping}
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Carregando formulário...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!structure) {
    return null;
  }

  const progress = ((currentSection + 1) / structure.sections.length) * 100;

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">{structure.form_name}</h1>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            <span>{structure.estimated_time}</span>
          </div>
          <div>
            {structure.total_fields} campos | {structure.sections.length} seções
          </div>
        </div>
        
        {structure.warning && (
          <Alert className="mt-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{structure.warning}</AlertDescription>
          </Alert>
        )}
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-muted-foreground mb-2">
          <span>Progresso</span>
          <span>{currentSection + 1} de {structure.sections.length}</span>
        </div>
        <div className="w-full bg-secondary rounded-full h-2">
          <div
            className="bg-primary h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Validation Result */}
      {validationResult && (
        <Alert className={validationResult.validation_status === 'approved' ? 'border-green-500' : 'border-yellow-500'}>
          {validationResult.validation_status === 'approved' ? (
            <CheckCircle className="h-4 w-4 text-green-500" />
          ) : (
            <AlertCircle className="h-4 w-4 text-yellow-500" />
          )}
          <AlertDescription>
            <div className="font-medium mb-2">{validationResult.message}</div>
            <div className="text-sm">
              Completude: {validationResult.completion_percentage}%
            </div>
            
            {validationResult.validation_issues?.length > 0 && (
              <div className="mt-4">
                <div className="font-medium mb-2">Problemas encontrados:</div>
                <ul className="list-disc list-inside space-y-1">
                  {validationResult.validation_issues.slice(0, 5).map((issue: any, idx: number) => (
                    <li key={idx} className="text-sm">
                      <strong>{issue.field_label || issue.field}:</strong> {issue.issue}
                      {issue.suggestion && (
                        <div className="ml-5 text-muted-foreground">
                          💡 {issue.suggestion}
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </AlertDescription>
        </Alert>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit}>
        {structure.sections.map((section, index) => 
          renderSection(section, index)
        )}

        {/* Navigation */}
        <div className="flex justify-between mt-8">
          <Button
            type="button"
            variant="outline"
            onClick={() => setCurrentSection(prev => Math.max(0, prev - 1))}
            disabled={currentSection === 0}
          >
            ← Anterior
          </Button>
          
          {currentSection < structure.sections.length - 1 ? (
            <Button
              type="button"
              onClick={() => setCurrentSection(prev => prev + 1)}
            >
              Próxima →
            </Button>
          ) : (
            <Button
              type="submit"
              disabled={submitting}
            >
              {submitting ? 'Enviando...' : 'Validar e Enviar'}
            </Button>
          )}
        </div>
      </form>
    </div>
  );
};

export default DynamicFriendlyForm;
