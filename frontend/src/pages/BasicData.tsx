import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import OspreyOwlTutor from "@/components/OspreyOwlTutor";
import SaveAndContinueModal from "@/components/SaveAndContinueModal";
import { useFormSnapshot } from "@/hooks/useFormSnapshot";
import { useSessionManager } from "@/hooks/useSessionManager";
import { 
  ArrowLeft,
  ArrowRight,
  FileText,
  AlertTriangle,
  CheckCircle,
  User,
  MapPin,
  Calendar,
  Phone,
  Mail,
  Save,
  Info
} from "lucide-react";

interface VisaSpecs {
  form_code: string;
  specifications: {
    title: string;
    category: string;
    description: string;
    uscis_fee: string;
    processing_time: string;
  };
  required_documents: string[];
  key_questions: string[];
  common_issues: string[];
}

interface BasicDataForm {
  // Personal Information
  firstName: string;
  middleName: string;
  lastName: string;
  dateOfBirth: string;
  countryOfBirth: string;
  gender: string;
  
  // Contact Information
  currentAddress: string;
  city: string;
  state: string;
  zipCode: string;
  phoneNumber: string;
  email: string;
  
  // Immigration Information
  alienNumber: string;
  socialSecurityNumber: string;
  currentStatus: string;
  statusExpiration: string;
}

const BasicData = () => {
  const { caseId } = useParams();
  const navigate = useNavigate();
  
  const [visaSpecs, setVisaSpecs] = useState<VisaSpecs | null>(null);
  const [formData, setFormData] = useState<BasicDataForm>({
    firstName: '',
    middleName: '',
    lastName: '',
    dateOfBirth: '',
    countryOfBirth: '',
    gender: '',
    currentAddress: '',
    city: '',
    state: '',
    zipCode: '',
    phoneNumber: '',
    email: '',
    alienNumber: '',
    socialSecurityNumber: '',
    currentStatus: '',
    statusExpiration: ''
  });
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [case_, setCase] = useState<any>(null);
  const [showSaveModal, setShowSaveModal] = useState(false);

  // Session management  
  const { 
    sessionData, 
    setCaseId, 
    setCurrentStep, 
    getCaseId,
    getSessionToken,
    isSessionActive 
  } = useSessionManager();

  // Osprey Owl Tutor integration
  const { snapshot } = useFormSnapshot(formData, {
    enabled: true,
    autoGenerate: true,
    onSnapshotUpdate: (snapshot) => {
      console.log('🦉 Form snapshot updated:', snapshot);
    },
    onError: (error) => {
      console.error('🦉 Form snapshot error:', error);
      setError(error);
    }
  });

  useEffect(() => {
    if (caseId) {
      fetchCase();
    }
  }, [caseId]);

  const fetchCase = async () => {
    try {
      const sessionToken = localStorage.getItem('osprey_session_token');
      const caseIdStored = localStorage.getItem('osprey_current_case_id');
      
      // Build query string
      let url = `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}`;
      if (sessionToken && sessionToken !== 'null') {
        url += `?session_token=${sessionToken}`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCase(data.case);
        
        // Load existing basic data if available
        if (data.case.basic_data) {
          setFormData(data.case.basic_data);
        }
        
        // Fetch visa specifications
        if (data.case.form_code) {
          await fetchVisaSpecs(data.case.form_code);
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

  const handleInputChange = (field: keyof BasicDataForm, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const saveData = async (autoSave = false) => {
    if (!autoSave) setIsSaving(true);
    
    try {
      const sessionToken = localStorage.getItem('osprey_session_token');
      
      // Build query string
      let url = `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}`;
      if (sessionToken && sessionToken !== 'null') {
        url += `?session_token=${sessionToken}`;
      }
      
      const response = await fetch(url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          basic_data: formData,
          status: 'basic_data'
        }),
      });

      if (response.ok) {
        if (!autoSave) {
          // Show success feedback
          console.log('Dados salvos com sucesso');
        }
      } else {
        if (!autoSave) {
          setError('Erro ao salvar dados');
        }
      }
    } catch (error) {
      console.error('Save error:', error);
      if (!autoSave) {
        setError('Erro de conexão');
      }
    } finally {
      if (!autoSave) setIsSaving(false);
    }
  };

  // Auto-save every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (formData.firstName || formData.lastName) {
        saveData(true);
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [formData]);

  const continueToNextStep = () => {
    saveData();
    navigate(`/auto-application/case/${caseId}/uscis-form`);
  };

  const isFormValid = () => {
    return formData.firstName && formData.lastName && formData.dateOfBirth && 
           formData.currentAddress && formData.city && formData.zipCode;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto"></div>
          <p className="text-black">Carregando informações...</p>
        </div>
      </div>
    );
  }

  if (error || !case_) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center px-4">
        <div className="bg-white border border-black rounded-lg p-6 max-w-sm w-full text-center">
          <AlertTriangle className="h-8 w-8 text-black mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-black mb-2">
            {error || 'Caso não encontrado'}
          </h2>
          <Button 
            onClick={() => navigate('/auto-application/start')}
            className="bg-black text-white hover:bg-gray-800 w-full"
          >
            Voltar ao Início
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header - Mobile Optimized */}
      <div className="bg-white border-b border-black">
        <div className="px-4 py-4 sm:py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/auto-application/select-form')}
                className="p-2 hover:bg-gray-100"
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <div>
                <h1 className="text-lg sm:text-xl font-bold text-black">
                  {visaSpecs?.specifications.title || case_.form_code}
                </h1>
                <p className="text-xs sm:text-sm text-black">
                  Dados Básicos • {case_.case_id}
                </p>
              </div>
            </div>
            <div className="bg-black text-white text-xs px-2 py-1 rounded">
              100%
            </div>
          </div>
        </div>
      </div>

      {/* Osprey Owl Tutor - positioned fixed */}

      <div className="px-4 py-6 sm:px-6 sm:py-8">
        <div className="max-w-4xl mx-auto lg:grid lg:grid-cols-3 lg:gap-8">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Personal Information */}
            <div className="bg-white border border-black rounded-lg p-4 sm:p-6">
              <h2 className="text-lg font-semibold text-black mb-4 flex items-center gap-2">
                <User className="h-5 w-5" />
                Informações Pessoais
              </h2>
              <div className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      Nome <span className="text-black">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.firstName}
                      onChange={(e) => handleInputChange('firstName', e.target.value)}
                      placeholder="Primeiro nome"
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      Nome do Meio
                    </label>
                    <input
                      type="text"
                      value={formData.middleName}
                      onChange={(e) => handleInputChange('middleName', e.target.value)}
                      placeholder="Nome do meio"
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      Sobrenome <span className="text-black">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.lastName}
                      onChange={(e) => handleInputChange('lastName', e.target.value)}
                      placeholder="Sobrenome"
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      Data de Nascimento <span className="text-black">*</span>
                    </label>
                    <input
                      type="date"
                      value={formData.dateOfBirth}
                      onChange={(e) => handleInputChange('dateOfBirth', e.target.value)}
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      País de Nascimento
                    </label>
                    <input
                      type="text"
                      value={formData.countryOfBirth}
                      onChange={(e) => handleInputChange('countryOfBirth', e.target.value)}
                      placeholder="Ex: Brasil"
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      Gênero
                    </label>
                    <select
                      value={formData.gender}
                      onChange={(e) => handleInputChange('gender', e.target.value)}
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    >
                      <option value="">Selecione</option>
                      <option value="Male">Masculino</option>
                      <option value="Female">Feminino</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            {/* Contact Information */}
            <div className="bg-white border border-black rounded-lg p-4 sm:p-6">
              <h2 className="text-lg font-semibold text-black mb-4 flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Informações de Contato
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-black mb-2">
                    Endereço Atual <span className="text-black">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.currentAddress}
                    onChange={(e) => handleInputChange('currentAddress', e.target.value)}
                    placeholder="Rua, número, apartamento"
                    className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                  />
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      Cidade <span className="text-black">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.city}
                      onChange={(e) => handleInputChange('city', e.target.value)}
                      placeholder="Cidade"
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      Estado
                    </label>
                    <input
                      type="text"
                      value={formData.state}
                      onChange={(e) => handleInputChange('state', e.target.value)}
                      placeholder="Estado"
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      CEP/ZIP <span className="text-black">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.zipCode}
                      onChange={(e) => handleInputChange('zipCode', e.target.value)}
                      placeholder="00000-000"
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      Telefone
                    </label>
                    <input
                      type="tel"
                      value={formData.phoneNumber}
                      onChange={(e) => handleInputChange('phoneNumber', e.target.value)}
                      placeholder="+1 (555) 123-4567"
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      placeholder="seu@email.com"
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Immigration Information */}
            <div className="bg-white border border-black rounded-lg p-4 sm:p-6">
              <h2 className="text-lg font-semibold text-black mb-4 flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Informações de Imigração
              </h2>
              <div className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      A-Number (se aplicável)
                    </label>
                    <input
                      type="text"
                      value={formData.alienNumber}
                      onChange={(e) => handleInputChange('alienNumber', e.target.value)}
                      placeholder="A123456789"
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      SSN (se aplicável)
                    </label>
                    <input
                      type="text"
                      value={formData.socialSecurityNumber}
                      onChange={(e) => handleInputChange('socialSecurityNumber', e.target.value)}
                      placeholder="000-00-0000"
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      Status Atual nos EUA
                    </label>
                    <input
                      type="text"
                      value={formData.currentStatus}
                      onChange={(e) => handleInputChange('currentStatus', e.target.value)}
                      placeholder="Ex: F-1, H-1B, Residente Permanente"
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-black mb-2">
                      Expiração do Status
                    </label>
                    <input
                      type="date"
                      value={formData.statusExpiration}
                      onChange={(e) => handleInputChange('statusExpiration', e.target.value)}
                      className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-black text-black"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-4 justify-between">
              <Button
                variant="outline"
                onClick={() => navigate(-1)}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Voltar
              </Button>

              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  variant="outline"
                  onClick={() => saveData()}
                  disabled={isSaving}
                  className="flex items-center gap-2"
                >
                  <Save className="h-4 w-4" />
                  {isSaving ? 'Salvando...' : 'Salvar Progresso'}
                </Button>

                <Button
                  variant="outline"
                  onClick={() => setShowSaveModal(true)}
                  className="flex items-center gap-2 border-blue-500 text-blue-600 hover:bg-blue-50"
                >
                  <Save className="h-4 w-4" />
                  Salvar e Continuar Depois
                </Button>

                <Button 
                  onClick={continueToNextStep}
                  disabled={!isFormValid() || isSaving}
                  className="bg-black text-white hover:bg-gray-800 flex items-center gap-2"
                >
                  Continuar para Documentos
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Form Requirements */}
            {visaSpecs && (
              <div className="bg-white border border-black rounded-lg p-4 sm:p-6">
                <h3 className="text-lg font-semibold text-black mb-4 flex items-center gap-2">
                  <Info className="h-5 w-5" />
                  Sobre {visaSpecs.specifications.title}
                </h3>
                <div className="space-y-4">
                  <p className="text-sm text-black">
                    {visaSpecs.specifications.description}
                  </p>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-black">Taxa USCIS:</span>
                      <div className="font-medium text-black">{visaSpecs.specifications.uscis_fee}</div>
                    </div>
                    <div>
                      <span className="text-black">Prazo:</span>
                      <div className="font-medium text-black">{visaSpecs.specifications.processing_time}</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Progress */}
            <div className="bg-white border border-black rounded-lg p-4 sm:p-6">
              <h3 className="text-lg font-semibold text-black mb-4">Progresso da Aplicação</h3>
              <div>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-black text-white rounded-full flex items-center justify-center text-xs font-bold">
                      1
                    </div>
                    <span className="text-sm font-medium">Dados Básicos</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      2
                    </div>
                    <span className="text-sm text-black">Upload de Documentos</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      3
                    </div>
                    <span className="text-sm text-black">Conte sua História</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      4
                    </div>
                    <span className="text-sm text-black">Formulário Amigável</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      5
                    </div>
                    <span className="text-sm text-black">Revisão Final</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      6
                    </div>
                    <span className="text-sm text-black">Pagamento & Download</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Auto Save Info */}
            <div className="bg-gray-50 border border-black rounded-lg p-4">
              <div className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-black" />
                <div>
                  <p className="text-sm font-medium text-black">Salvamento Automático</p>
                  <p className="text-xs text-black">
                    Suas informações são salvas automaticamente a cada 30 segundos
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Osprey Owl Tutor - Debug Version */}
      <div className="fixed bottom-4 right-4 z-50">
        <div className="bg-red-100 border border-red-300 rounded p-2 text-xs">
          <p>🦉 Debug: Case ID: {case_?.case_id}</p>
          <p>🦉 Debug: Snapshot: {snapshot ? 'exists' : 'null'}</p>
          <p>🦉 Debug: Enabled: {!!case_?.case_id ? 'yes' : 'no'}</p>
        </div>
      </div>
      
      <OspreyOwlTutor 
        snapshot={snapshot}
        onAction={async (event, payload) => {
          console.log('🦉 Tutor action:', event, payload);
          
          // Integration with Dra. Paula B2C for expert validation
          if (event === 'validate_form') {
            try {
              const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/immigration-expert/validate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  formData: formData,
                  visaType: 'H-1B',
                  stepId: 'personal'
                })
              });
              
              if (response.ok) {
                const expertAnalysis = await response.json();
                console.log('🦉 Dra. Paula analysis:', expertAnalysis);
                
                // Display expert analysis in Owl Tutor
                if (expertAnalysis.success && expertAnalysis.expert_analysis) {
                  // You can handle the expert analysis here
                  console.log('✅ Expert validation completed by Dra. Paula B2C');
                }
              }
            } catch (error) {
              console.error('❌ Error calling Dra. Paula:', error);
            }
          }
        }}
        isEnabled={!!case_?.case_id}
        position="bottom-right"
      />

      {/* Save and Continue Later Modal */}
      <SaveAndContinueModal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        caseId={caseId || ''}
        currentStage="Dados Básicos"
        onSuccess={(userData) => {
          console.log('User authenticated:', userData);
          navigate('/dashboard');
        }}
      />
    </div>
  );
};

export default BasicData;