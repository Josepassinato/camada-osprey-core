import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, ArrowRight, Save, Languages } from 'lucide-react';
import { useOwlSession } from './OwlSessionManager';
import { OwlFieldGuide } from './OwlFieldGuide';
import { OwlProgressTracker } from './OwlProgressTracker';
import { OwlValidationFeedback } from './OwlValidationFeedback';

interface QuestionnaireField {
  id: string;
  type: 'text' | 'email' | 'phone' | 'address' | 'date' | 'select' | 'textarea';
  label: string;
  placeholder?: string;
  required: boolean;
  options?: string[];
  validation_rules?: Record<string, any>;
}

interface ValidationResult {
  score: number;
  status: 'valid' | 'warning' | 'invalid' | 'pending';
  message: string;
  suggestions?: string[];
}

export const OwlQuestionnaire: React.FC = () => {
  const { state, startSession, saveResponse } = useOwlSession();
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [validations, setValidations] = useState<Record<string, ValidationResult>>({});
  const [validatingField, setValidatingField] = useState<string | null>(null);
  const [language, setLanguage] = useState<'pt' | 'en'>('pt');
  
  // Sample questionnaire fields - in real app, these would come from the backend
  const questionnaireFields: QuestionnaireField[] = [
    {
      id: 'full_name',
      type: 'text',
      label: language === 'pt' ? 'Nome Completo' : 'Full Name',
      placeholder: language === 'pt' ? 'Digite seu nome completo' : 'Enter your full name',
      required: true,
    },
    {
      id: 'date_of_birth',
      type: 'date',
      label: language === 'pt' ? 'Data de Nascimento' : 'Date of Birth',
      required: true,
    },
    {
      id: 'place_of_birth',
      type: 'text',
      label: language === 'pt' ? 'Local de Nascimento' : 'Place of Birth',
      placeholder: language === 'pt' ? 'Cidade, Estado, País' : 'City, State, Country',
      required: true,
    },
    {
      id: 'current_address',
      type: 'textarea',
      label: language === 'pt' ? 'Endereço Atual' : 'Current Address',
      placeholder: language === 'pt' ? 'Endereço completo' : 'Complete address',
      required: true,
    },
    {
      id: 'email',
      type: 'email',
      label: language === 'pt' ? 'Email' : 'Email',
      placeholder: language === 'pt' ? 'seu@email.com' : 'your@email.com',
      required: true,
    },
    {
      id: 'phone',
      type: 'phone',
      label: language === 'pt' ? 'Telefone' : 'Phone',
      placeholder: language === 'pt' ? '+55 11 99999-9999' : '+1 555 123-4567',
      required: true,
    },
    {
      id: 'current_job',
      type: 'text',
      label: language === 'pt' ? 'Trabalho Atual' : 'Current Job',
      placeholder: language === 'pt' ? 'Cargo e empresa' : 'Position and company',
      required: true,
    },
    {
      id: 'highest_degree',
      type: 'select',
      label: language === 'pt' ? 'Maior Grau de Educação' : 'Highest Degree',
      required: true,
      options: language === 'pt' 
        ? ['Ensino Médio', 'Graduação', 'Pós-graduação', 'Mestrado', 'Doutorado']
        : ['High School', 'Bachelor\'s', 'Graduate', 'Master\'s', 'Doctorate'],
    },
    {
      id: 'marital_status',
      type: 'select',
      label: language === 'pt' ? 'Estado Civil' : 'Marital Status',
      required: true,
      options: language === 'pt'
        ? ['Solteiro(a)', 'Casado(a)', 'Divorciado(a)', 'Viúvo(a)']
        : ['Single', 'Married', 'Divorced', 'Widowed'],
    },
    {
      id: 'annual_income',
      type: 'text',
      label: language === 'pt' ? 'Renda Anual' : 'Annual Income',
      placeholder: language === 'pt' ? 'R$ 100.000' : '$50,000',
      required: true,
    },
  ];

  const getBackendUrl = () => {
    return import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  };

  // Initialize session when component mounts
  useEffect(() => {
    if (!state.session) {
      startSession('H-1B', language);
    }
  }, [language]);

  // Load existing responses into form data
  useEffect(() => {
    if (state.session?.responses) {
      setFormData(state.session.responses);
    }
  }, [state.session]);

  const validateField = async (fieldId: string, value: any) => {
    if (!state.session || !value) return;

    setValidatingField(fieldId);

    try {
      const response = await fetch(`${getBackendUrl()}/api/owl-agent/validate-field`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: state.session.session_id,
          field_id: fieldId,
          value: value,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setValidations(prev => ({
          ...prev,
          [fieldId]: {
            score: data.validation_score,
            status: data.validation_score >= 80 ? 'valid' : data.validation_score >= 60 ? 'warning' : 'invalid',
            message: data.feedback || 'Campo validado',
            suggestions: data.suggestions || [],
          },
        }));
      }
    } catch (error) {
      console.error('Validation error:', error);
    } finally {
      setValidatingField(null);
    }
  };

  const handleFieldChange = (fieldId: string, value: any) => {
    setFormData(prev => ({ ...prev, [fieldId]: value }));
    
    // Debounced validation
    setTimeout(() => {
      validateField(fieldId, value);
    }, 500);
  };

  const handleFieldBlur = async (fieldId: string, value: any) => {
    if (value && state.session) {
      await saveResponse(fieldId, value);
    }
  };

  const renderField = (field: QuestionnaireField) => {
    const value = formData[field.id] || '';
    const validation = validations[field.id];

    return (
      <div key={field.id} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor={field.id} className="text-sm font-medium">
            {field.label}
            {field.required && <span className="text-red-500 ml-1">*</span>}
          </Label>
          
          {field.type === 'text' && (
            <Input
              id={field.id}
              value={value}
              placeholder={field.placeholder}
              onChange={(e) => handleFieldChange(field.id, e.target.value)}
              onBlur={(e) => handleFieldBlur(field.id, e.target.value)}
              className="w-full"
            />
          )}
          
          {field.type === 'email' && (
            <Input
              id={field.id}
              type="email"
              value={value}
              placeholder={field.placeholder}
              onChange={(e) => handleFieldChange(field.id, e.target.value)}
              onBlur={(e) => handleFieldBlur(field.id, e.target.value)}
              className="w-full"
            />
          )}
          
          {field.type === 'phone' && (
            <Input
              id={field.id}
              type="tel"
              value={value}
              placeholder={field.placeholder}
              onChange={(e) => handleFieldChange(field.id, e.target.value)}
              onBlur={(e) => handleFieldBlur(field.id, e.target.value)}
              className="w-full"
            />
          )}
          
          {field.type === 'date' && (
            <Input
              id={field.id}
              type="date"
              value={value}
              onChange={(e) => handleFieldChange(field.id, e.target.value)}
              onBlur={(e) => handleFieldBlur(field.id, e.target.value)}
              className="w-full"
            />
          )}
          
          {field.type === 'textarea' && (
            <Textarea
              id={field.id}
              value={value}
              placeholder={field.placeholder}
              onChange={(e) => handleFieldChange(field.id, e.target.value)}
              onBlur={(e) => handleFieldBlur(field.id, e.target.value)}
              className="w-full min-h-[100px]"
            />
          )}
          
          {field.type === 'select' && (
            <Select
              value={value}
              onValueChange={(newValue) => {
                handleFieldChange(field.id, newValue);
                handleFieldBlur(field.id, newValue);
              }}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder={`Selecione ${field.label.toLowerCase()}`} />
              </SelectTrigger>
              <SelectContent>
                {field.options?.map((option) => (
                  <SelectItem key={option} value={option}>
                    {option}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>

        {/* Validation feedback */}
        <OwlValidationFeedback
          validation={validation}
          loading={validatingField === field.id}
          fieldName={field.label}
        />
      </div>
    );
  };

  const fieldsPerStep = 3;
  const totalSteps = Math.ceil(questionnaireFields.length / fieldsPerStep);
  const currentFields = questionnaireFields.slice(
    currentStep * fieldsPerStep,
    (currentStep + 1) * fieldsPerStep
  );

  const progress = (Object.keys(formData).length / questionnaireFields.length) * 100;

  const steps = questionnaireFields.map((field, index) => ({
    id: field.id,
    title: field.label,
    completed: !!formData[field.id],
    current: Math.floor(index / fieldsPerStep) === currentStep,
  }));

  const canGoNext = currentFields.every(field => !field.required || formData[field.id]);
  const canGoPrev = currentStep > 0;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-3xl">🦉</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900">
              {language === 'pt' ? 'Agente Coruja' : 'Owl Agent'}
            </h1>
          </div>
          <p className="text-gray-600 max-w-2xl mx-auto">
            {language === 'pt' 
              ? 'Sistema inteligente de questionários para aplicações de visto. Responda as perguntas e receba orientações em tempo real.'
              : 'Intelligent questionnaire system for visa applications. Answer questions and receive real-time guidance.'
            }
          </p>
          
          {/* Language toggle */}
          <div className="flex items-center justify-center gap-2 mt-4">
            <Button
              variant={language === 'pt' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setLanguage('pt')}
            >
              <Languages className="w-4 h-4 mr-1" />
              Português
            </Button>
            <Button
              variant={language === 'en' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setLanguage('en')}
            >
              <Languages className="w-4 h-4 mr-1" />
              English
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Progress tracker */}
          <div className="lg:col-span-1">
            <OwlProgressTracker
              progress={progress}
              currentStep={currentStep + 1}
              totalSteps={totalSteps}
              steps={steps}
            />
          </div>

          {/* Main questionnaire */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-xl">📝</span>
                  {language === 'pt' ? 'Questionário' : 'Questionnaire'} - 
                  {language === 'pt' ? 'Passo' : 'Step'} {currentStep + 1} {language === 'pt' ? 'de' : 'of'} {totalSteps}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {currentFields.map(renderField)}
              </CardContent>
            </Card>

            {/* Field guidance for current field */}
            {currentFields.length > 0 && (
              <OwlFieldGuide fieldId={currentFields[0].id} />
            )}

            {/* Navigation */}
            <div className="flex justify-between items-center">
              <Button
                variant="outline"
                onClick={() => setCurrentStep(prev => prev - 1)}
                disabled={!canGoPrev}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                {language === 'pt' ? 'Anterior' : 'Previous'}
              </Button>

              <div className="flex gap-2">
                <Button variant="outline" className="flex items-center gap-2">
                  <Save className="w-4 h-4" />
                  {language === 'pt' ? 'Salvar Progresso' : 'Save Progress'}
                </Button>

                {currentStep < totalSteps - 1 ? (
                  <Button
                    onClick={() => setCurrentStep(prev => prev + 1)}
                    disabled={!canGoNext}
                  >
                    {language === 'pt' ? 'Próximo' : 'Next'}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                ) : (
                  <Button
                    onClick={() => {
                      // Navigate to form generator
                      console.log('Questionnaire completed!');
                    }}
                    disabled={!canGoNext}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    {language === 'pt' ? 'Finalizar' : 'Complete'}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};