import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  ArrowLeft,
  ArrowRight,
  FileText,
  CheckCircle,
  AlertTriangle,
  Save,
  RefreshCw,
  Info,
  Edit,
  Eye,
  Languages,
  Zap,
  User,
  MapPin,
  Briefcase,
  GraduationCap,
  Heart,
  Plane
} from "lucide-react";

interface FormSection {
  id: string;
  title: string;
  description: string;
  icon: any;
  fields: FormField[];
  completed: boolean;
  required: boolean;
}

interface FormField {
  id: string;
  label: string;
  type: 'text' | 'date' | 'select' | 'textarea' | 'checkbox' | 'number';
  value: any;
  required: boolean;
  options?: string[];
  placeholder?: string;
  validation?: string;
  aiSuggestion?: string;
}

const FriendlyForm = () => {
  const { caseId } = useParams();
  const navigate = useNavigate();
  
  const [case_, setCase] = useState<any>(null);
  const [visaSpecs, setVisaSpecs] = useState<any>(null);
  const [formSections, setFormSections] = useState<FormSection[]>([]);
  const [responses, setResponses] = useState<any>({});
  const [currentSection, setCurrentSection] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (caseId) {
      fetchCase();
    }
  }, [caseId]);

  const fetchCase = async () => {
    try {
      const sessionToken = localStorage.getItem('osprey_session_token');
      
      let url = `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}`;
      if (sessionToken && sessionToken !== 'null') {
        url += `?session_token=${sessionToken}`;
      }
      
      const response = await fetch(url);

      if (response.ok) {
        const data = await response.json();
        setCase(data.case);
        
        // Load existing responses if available
        if (data.case.simplified_form_responses) {
          setResponses(data.case.simplified_form_responses);
        }
        
        if (data.case.form_code) {
          await fetchVisaSpecs(data.case.form_code);
          generateFormSections(data.case);
        }
      } else {
        setError('Caso não encontrado');
      }
    } catch (error) {
      console.error('Fetch case error:', error);
      setError('Erro de conexão');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchVisaSpecs = async (formCode: string) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/visa-specs/${formCode}`
      );

      if (response.ok) {
        const data = await response.json();
        setVisaSpecs(data);
      }
    } catch (error) {
      console.error('Fetch visa specs error:', error);
    }
  };

  const generateFormSections = (caseData: any) => {
    const extractedFacts = caseData.ai_extracted_facts || {};
    const formCode = caseData.form_code;
    
    let sections: FormSection[] = [];

    // Section 1: Personal Information
    sections.push({
      id: 'personal',
      title: 'Informações Pessoais',
      description: 'Dados básicos sobre você',
      icon: User,
      required: true,
      completed: false,
      fields: [
        {
          id: 'full_name',
          label: 'Nome Completo',
          type: 'text',
          required: true,
          value: extractedFacts.personal_info?.full_name || 
                 `${caseData.basic_data?.firstName || ''} ${caseData.basic_data?.middleName || ''} ${caseData.basic_data?.lastName || ''}`.trim() || 
                 '',
          placeholder: 'Seu nome completo como no passaporte',
          aiSuggestion: extractedFacts.personal_info?.full_name ? 
            `IA sugeriu: ${extractedFacts.personal_info.full_name}` : 
            (caseData.basic_data?.firstName ? `Dados básicos: ${caseData.basic_data.firstName} ${caseData.basic_data.lastName}` : undefined)
        },
        {
          id: 'date_of_birth',
          label: 'Data de Nascimento',
          type: 'date',
          required: true,
          value: extractedFacts.personal_info?.date_of_birth || caseData.basic_data?.dateOfBirth || '',
          aiSuggestion: extractedFacts.personal_info?.date_of_birth ? 
            `IA sugeriu: ${extractedFacts.personal_info.date_of_birth}` : 
            (caseData.basic_data?.dateOfBirth ? `Dados básicos: ${caseData.basic_data.dateOfBirth}` : undefined)
        },
        {
          id: 'place_of_birth',
          label: 'Local de Nascimento',
          type: 'text',
          required: true,
          value: extractedFacts.personal_info?.place_of_birth || caseData.basic_data?.countryOfBirth || '',
          placeholder: 'Cidade, Estado/Província, País',
          aiSuggestion: extractedFacts.personal_info?.place_of_birth ? 
            `IA sugeriu: ${extractedFacts.personal_info.place_of_birth}` : 
            (caseData.basic_data?.countryOfBirth ? `Dados básicos: ${caseData.basic_data.countryOfBirth}` : undefined)
        },
        {
          id: 'nationality',
          label: 'Nacionalidade',
          type: 'text',
          required: true,
          value: extractedFacts.personal_info?.nationality || caseData.basic_data?.nationality || '',
          aiSuggestion: extractedFacts.personal_info?.nationality ? `IA sugeriu: ${extractedFacts.personal_info.nationality}` : undefined
        }
      ]
    });

    // Section 2: Address Information
    sections.push({
      id: 'address',
      title: 'Informações de Endereço',
      description: 'Seus endereços atual e anterior',
      icon: MapPin,
      required: true,
      completed: false,
      fields: [
        {
          id: 'cep',
          label: 'CEP (se no Brasil)',
          type: 'text',
          required: false,
          value: caseData.basic_data?.zipCode?.replace(/[^0-9]/g, '') || '',
          placeholder: '00000000',
          validation: 'cep'
        },
        {
          id: 'street_address',
          label: 'Endereço (Rua, Número)',
          type: 'text',
          required: true,
          value: caseData.basic_data?.currentAddress || '',
          placeholder: 'Ex: Rua das Flores, 123, Apt 45'
        },
        {
          id: 'neighborhood',
          label: 'Bairro',
          type: 'text',
          required: false,
          value: '',
          placeholder: 'Ex: Centro, Vila Nova'
        },
        {
          id: 'city',
          label: 'Cidade',
          type: 'text',
          required: true,
          value: caseData.basic_data?.city || '',
          placeholder: 'Ex: São Paulo'
        },
        {
          id: 'state',
          label: 'Estado/Província',
          type: 'text',
          required: true,
          value: caseData.basic_data?.state || '',
          placeholder: 'Ex: SP, CA, NY'
        },
        {
          id: 'postal_code',
          label: 'CEP/ZIP Code',
          type: 'text',
          required: true,
          value: caseData.basic_data?.zipCode || '',
          placeholder: '00000-000 ou 12345'
        },
        {
          id: 'country',
          label: 'País',
          type: 'text',
          required: true,
          value: 'Brasil',
          placeholder: 'Brasil, Estados Unidos, etc.'
        },
        {
          id: 'phone',
          label: 'Telefone',
          type: 'text',
          required: true,
          value: extractedFacts.personal_info?.phone || caseData.basic_data?.phoneNumber || '',
          placeholder: '+55 11 99999-9999',
          aiSuggestion: extractedFacts.personal_info?.phone ? 
            `IA sugeriu: ${extractedFacts.personal_info.phone}` : 
            (caseData.basic_data?.phoneNumber ? `Dados básicos: ${caseData.basic_data.phoneNumber}` : undefined)
        },
        {
          id: 'email',
          label: 'E-mail',
          type: 'text',
          required: true,
          value: extractedFacts.personal_info?.email || caseData.basic_data?.email || '',
          placeholder: 'seu@email.com',
          aiSuggestion: extractedFacts.personal_info?.email ? 
            `IA sugeriu: ${extractedFacts.personal_info.email}` : 
            (caseData.basic_data?.email ? `Dados básicos: ${caseData.basic_data.email}` : undefined)
        }
      ]
    });

    // Section 3: Family Information (conditional)
    if (formCode === 'I-130' || formCode === 'I-485' || extractedFacts.family_details) {
      sections.push({
        id: 'family',
        title: 'Informações Familiares',
        description: 'Detalhes sobre família e relacionamentos',
        icon: Heart,
        required: formCode === 'I-130',
        completed: false,
        fields: [
          {
            id: 'marital_status',
            label: 'Estado Civil',
            type: 'select',
            required: true,
            value: extractedFacts.family_details?.marital_status || '',
            options: ['Solteiro(a)', 'Casado(a)', 'Divorciado(a)', 'Viúvo(a)', 'Separado(a)'],
            aiSuggestion: extractedFacts.family_details?.marital_status ? `IA sugeriu: ${extractedFacts.family_details.marital_status}` : undefined
          },
          {
            id: 'spouse_name',
            label: 'Nome do Cônjuge (se aplicável)',
            type: 'text',
            required: false,
            value: extractedFacts.family_details?.spouse_info?.name || '',
            placeholder: 'Nome completo do cônjuge',
            aiSuggestion: extractedFacts.family_details?.spouse_info ? `IA encontrou informações do cônjuge` : undefined
          },
          {
            id: 'children_count',
            label: 'Número de Filhos',
            type: 'number',
            required: false,
            value: extractedFacts.family_details?.children?.length || 0,
            aiSuggestion: extractedFacts.family_details?.children ? `IA sugeriu: ${extractedFacts.family_details.children.length} filho(s)` : undefined
          }
        ]
      });
    }

    // Section 4: Employment Information
    sections.push({
      id: 'employment',
      title: 'Informações de Trabalho',
      description: 'Seu emprego atual e histórico profissional',
      icon: Briefcase,
      required: formCode === 'H-1B' || formCode === 'O-1',
      completed: false,
      fields: [
        {
          id: 'current_job',
          label: 'Emprego Atual',
          type: 'text',
          required: formCode === 'H-1B' || formCode === 'O-1',
          value: extractedFacts.employment_info?.current_job || '',
          placeholder: 'Título do cargo atual',
          aiSuggestion: extractedFacts.employment_info?.current_job ? `IA sugeriu: ${extractedFacts.employment_info.current_job}` : undefined
        },
        {
          id: 'employer_name',
          label: 'Nome do Empregador',
          type: 'text',
          required: formCode === 'H-1B' || formCode === 'O-1',
          value: extractedFacts.employment_info?.employer_details?.name || '',
          placeholder: 'Nome da empresa/organização',
          aiSuggestion: extractedFacts.employment_info?.employer_details ? `IA encontrou detalhes do empregador` : undefined
        },
        {
          id: 'salary',
          label: 'Salário Anual',
          type: 'text',
          required: false,
          value: extractedFacts.employment_info?.salary || '',
          placeholder: '$50,000 USD',
          aiSuggestion: extractedFacts.employment_info?.salary ? `IA sugeriu: ${extractedFacts.employment_info.salary}` : undefined
        }
      ]
    });

    // Section 5: Education Information
    sections.push({
      id: 'education',
      title: 'Informações Educacionais',
      description: 'Sua formação acadêmica',
      icon: GraduationCap,
      required: formCode === 'H-1B' || formCode === 'O-1',
      completed: false,
      fields: [
        {
          id: 'highest_degree',
          label: 'Maior Grau de Educação',
          type: 'select',
          required: formCode === 'H-1B',
          value: extractedFacts.education?.degrees?.[0] || '',
          options: ['Ensino Médio', 'Bacharelado', 'Mestrado', 'Doutorado', 'Outro'],
          aiSuggestion: extractedFacts.education?.degrees ? `IA encontrou: ${extractedFacts.education.degrees.length} diploma(s)` : undefined
        },
        {
          id: 'school_name',
          label: 'Nome da Instituição',
          type: 'text',
          required: false,
          value: extractedFacts.education?.schools?.[0] || '',
          placeholder: 'Nome da universidade/escola',
          aiSuggestion: extractedFacts.education?.schools ? `IA sugeriu: ${extractedFacts.education.schools[0]}` : undefined
        },
        {
          id: 'graduation_date',
          label: 'Data de Formatura',
          type: 'date',
          required: false,
          value: extractedFacts.education?.graduation_dates?.[0] || '',
          aiSuggestion: extractedFacts.education?.graduation_dates ? `IA sugeriu: ${extractedFacts.education.graduation_dates[0]}` : undefined
        }
      ]
    });

    // Section 6: Travel History (for certain forms)
    if (formCode === 'N-400' || formCode === 'I-485' || extractedFacts.travel_history) {
      sections.push({
        id: 'travel',
        title: 'Histórico de Viagens',
        description: 'Suas viagens para fora dos EUA',
        icon: Plane,
        required: formCode === 'N-400',
        completed: false,
        fields: [
          {
            id: 'trips_outside_usa',
            label: 'Viagens Fora dos EUA (últimos 5 anos)',
            type: 'textarea',
            required: formCode === 'N-400',
            value: extractedFacts.travel_history?.trips_outside_usa || '',
            placeholder: 'Descreva suas viagens: data, destino, duração, propósito',
            aiSuggestion: extractedFacts.travel_history?.trips_outside_usa ? `IA encontrou informações de viagens` : undefined
          },
          {
            id: 'longest_trip',
            label: 'Maior Período Fora dos EUA',
            type: 'text',
            required: false,
            value: extractedFacts.travel_history?.duration || '',
            placeholder: 'Ex: 3 meses em 2022',
            aiSuggestion: extractedFacts.travel_history?.duration ? `IA sugeriu: ${extractedFacts.travel_history.duration}` : undefined
          }
        ]
      });
    }

    setFormSections(sections);
  };

  const handleFieldChange = (sectionId: string, fieldId: string, value: any) => {
    const newResponses = {
      ...responses,
      [sectionId]: {
        ...responses[sectionId],
        [fieldId]: value
      }
    };
    setResponses(newResponses);
    
    // Update field value in sections
    setFormSections(prev => prev.map(section => {
      if (section.id === sectionId) {
        return {
          ...section,
          fields: section.fields.map(field => 
            field.id === fieldId ? { ...field, value } : field
          )
        };
      }
      return section;
    }));
    
    // Check if section is completed
    updateSectionCompletion(sectionId);
  };

  const updateSectionCompletion = (sectionId: string) => {
    setFormSections(prev => prev.map(section => {
      if (section.id === sectionId) {
        const requiredFields = section.fields.filter(f => f.required);
        const completedFields = requiredFields.filter(f => 
          f.value && (typeof f.value === 'string' ? f.value.trim() !== '' : f.value !== 0)
        );
        
        return {
          ...section,
          completed: completedFields.length === requiredFields.length
        };
      }
      return section;
    }));
  };

  const generateOfficialForms = async () => {
    setIsGenerating(true);
    
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/generate-forms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_id: caseId,
          form_responses: responses,
          form_code: case_.form_code
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Update case with official form data
        await saveFormData();
        
        setError('');
      } else {
        setError('Erro ao gerar formulários oficiais');
      }
      
    } catch (error) {
      console.error('Generate forms error:', error);
      setError('Erro de conexão ao gerar formulários');
    } finally {
      setIsGenerating(false);
    }
  };

  const saveFormData = async () => {
    setIsSaving(true);
    
    try {
      const sessionToken = localStorage.getItem('osprey_session_token');
      
      let url = `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}`;
      if (sessionToken && sessionToken !== 'null') {
        url += `?session_token=${sessionToken}`;
      }

      await fetch(url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          simplified_form_responses: responses,
          status: 'form_filled'
        }),
      });
      
    } catch (error) {
      console.error('Save form data error:', error);
      setError('Erro ao salvar formulário');
    } finally {
      setIsSaving(false);
    }
  };

  const getCompletedSections = () => {
    return formSections.filter(section => section.completed).length;
  };

  const getRequiredSections = () => {
    return formSections.filter(section => section.required).length;
  };

  const canContinue = () => {
    const requiredSections = formSections.filter(section => section.required);
    const completedRequired = requiredSections.filter(section => section.completed);
    return completedRequired.length === requiredSections.length;
  };

  const continueToNextStep = () => {
    navigate(`/auto-application/case/${caseId}/ai-review`);
  };

  const renderField = (field: FormField, sectionId: string) => {
    const fieldValue = responses[sectionId]?.[field.id] || field.value || '';
    
    return (
      <div key={field.id} className="space-y-2">
        <label className="text-sm font-medium text-foreground">
          {field.label}
          {field.required && <span className="text-red-500 ml-1">*</span>}
        </label>
        
        {field.aiSuggestion && (
          <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
            <Zap className="h-3 w-3 inline mr-1" />
            {field.aiSuggestion}
          </div>
        )}
        
        {field.type === 'text' && (
          <input
            type="text"
            value={fieldValue}
            onChange={(e) => handleFieldChange(sectionId, field.id, e.target.value)}
            placeholder={field.placeholder}
            className="w-full p-2 text-sm border border-gray-200 rounded focus:ring-2 focus:ring-black focus:border-black"
          />
        )}
        
        {field.type === 'date' && (
          <input
            type="date"
            value={fieldValue}
            onChange={(e) => handleFieldChange(sectionId, field.id, e.target.value)}
            className="w-full p-2 text-sm border border-gray-200 rounded focus:ring-2 focus:ring-black focus:border-black"
          />
        )}
        
        {field.type === 'number' && (
          <input
            type="number"
            value={fieldValue}
            onChange={(e) => handleFieldChange(sectionId, field.id, parseInt(e.target.value) || 0)}
            placeholder={field.placeholder}
            min="0"
            className="w-full p-2 text-sm border border-gray-200 rounded focus:ring-2 focus:ring-black focus:border-black"
          />
        )}
        
        {field.type === 'select' && (
          <select
            value={fieldValue}
            onChange={(e) => handleFieldChange(sectionId, field.id, e.target.value)}
            className="w-full p-2 text-sm border border-gray-200 rounded focus:ring-2 focus:ring-black focus:border-black"
          >
            <option value="">Selecione...</option>
            {field.options?.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        )}
        
        {field.type === 'textarea' && (
          <textarea
            value={fieldValue}
            onChange={(e) => handleFieldChange(sectionId, field.id, e.target.value)}
            placeholder={field.placeholder}
            rows={3}
            className="w-full p-2 text-sm border border-gray-200 rounded focus:ring-2 focus:ring-black focus:border-black resize-none"
          />
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Gerando formulário personalizado...</p>
        </div>
      </div>
    );
  }

  if (error && !case_) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <Card className="glass border-0 max-w-md">
          <CardContent className="text-center p-8">
            <AlertTriangle className="h-12 w-12 text-gray-700 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-foreground mb-2">
              {error || 'Caso não encontrado'}
            </h2>
            <Button onClick={() => navigate('/auto-application/start')}>
              Voltar ao Início
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentSectionData = formSections[currentSection];

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="glass border-b border-white/20">
        <div className="container-responsive py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate(`/auto-application/case/${caseId}/ai-review`)}
                className="p-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Voltar
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                  <Edit className="h-8 w-8 text-black" />
                  {visaSpecs?.specifications.title || case_.form_code}
                </h1>
                <p className="text-muted-foreground">
                  Etapa 4 de 6: Formulário Amigável • Caso: {case_.case_id}
                </p>
              </div>
            </div>
            <Badge className="bg-gray-100 text-gray-800 border-gray-200">
              {getCompletedSections()}/{formSections.length} Seções
            </Badge>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-4 gap-8">
          
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <Card className="glass border-0 sticky top-6">
              <CardHeader>
                <CardTitle className="text-lg">Seções do Formulário</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {formSections.map((section, index) => {
                    const IconComponent = section.icon;
                    return (
                      <button
                        key={section.id}
                        onClick={() => setCurrentSection(index)}
                        className={`w-full text-left p-3 rounded-lg transition-colors ${
                          currentSection === index 
                            ? 'bg-black text-white' 
                            : 'bg-gray-50 hover:bg-gray-100'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <IconComponent className="h-4 w-4" />
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium">{section.title}</span>
                              {section.completed && (
                                <CheckCircle className="h-3 w-3 text-green-600" />
                              )}
                              {section.required && (
                                <Badge variant="outline" className="text-xs">Obrigatório</Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Form Content */}
          <div className="lg:col-span-3 space-y-6">
            
            {/* Progress */}
            <Card className="glass border-0">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-medium">Progresso do Formulário</span>
                  <span className="text-sm text-muted-foreground">
                    {getCompletedSections()}/{formSections.length} seções completas
                  </span>
                </div>
                <Progress 
                  value={(getCompletedSections() / Math.max(formSections.length, 1)) * 100} 
                  className="h-3" 
                />
              </CardContent>
            </Card>

            {/* Current Section */}
            {currentSectionData && (
              <Card className="glass border-0">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <currentSectionData.icon className="h-6 w-6 text-black" />
                    <div>
                      <CardTitle className="text-xl">{currentSectionData.title}</CardTitle>
                      <p className="text-sm text-muted-foreground">{currentSectionData.description}</p>
                    </div>
                    {currentSectionData.completed && (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  {currentSectionData.fields.map(field => renderField(field, currentSectionData.id))}
                  
                  {/* Section Navigation */}
                  <div className="flex justify-between items-center pt-4 border-t border-gray-200">
                    <Button
                      variant="outline"
                      onClick={() => setCurrentSection(Math.max(0, currentSection - 1))}
                      disabled={currentSection === 0}
                    >
                      <ArrowLeft className="h-4 w-4" />
                      Seção Anterior
                    </Button>
                    
                    <Button
                      onClick={() => setCurrentSection(Math.min(formSections.length - 1, currentSection + 1))}
                      disabled={currentSection === formSections.length - 1}
                      className="bg-black text-white hover:bg-gray-800"
                    >
                      Próxima Seção
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Actions */}
            <div className="space-y-4">
              <Card className="glass border-0 bg-gray-50">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <Languages className="h-5 w-5 text-gray-700 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-foreground mb-1">Conversão Automática</p>
                      <p className="text-xs text-muted-foreground mb-2">
                        Suas respostas serão automaticamente convertidas para o formato oficial do USCIS em inglês.
                      </p>
                      <Button
                        onClick={generateOfficialForms}
                        disabled={isGenerating || !canContinue()}
                        size="sm"
                        className="bg-black text-white hover:bg-gray-800"
                      >
                        {isGenerating ? (
                          <RefreshCw className="h-4 w-4 animate-spin" />
                        ) : (
                          <Languages className="h-4 w-4" />
                        )}
                        Gerar Formulários Oficiais
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="flex justify-between items-center">
                <div className="text-sm text-muted-foreground">
                  {canContinue() ? (
                    <div className="flex items-center gap-2 text-gray-700">
                      <CheckCircle className="h-4 w-4" />
                      <span>Todas as seções obrigatórias foram preenchidas</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-gray-700" />
                      <span>
                        Preencha {getRequiredSections() - getCompletedSections()} seção(ões) obrigatória(s)
                      </span>
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <Button
                    variant="outline"
                    onClick={saveFormData}
                    disabled={isSaving}
                  >
                    {isSaving ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                    Salvar
                  </Button>
                  
                  <Button 
                    onClick={continueToNextStep}
                    disabled={!canContinue()}
                    className="bg-black text-white hover:bg-gray-800 flex items-center gap-2"
                  >
                    Continuar para Processamento IA
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FriendlyForm;