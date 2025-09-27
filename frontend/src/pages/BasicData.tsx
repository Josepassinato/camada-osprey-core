import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");
  const [case_, setCase] = useState<any>(null);

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
    navigate(`/auto-application/case/${caseId}/documents`);
  };

  const isFormValid = () => {
    return formData.firstName && formData.lastName && formData.dateOfBirth && 
           formData.currentAddress && formData.city && formData.zipCode;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Carregando informações...</p>
        </div>
      </div>
    );
  }

  if (error || !case_) {
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
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Data de Nascimento <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      value={formData.dateOfBirth}
                      onChange={(e) => handleInputChange('dateOfBirth', e.target.value)}
                      className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      País de Nascimento
                    </label>
                    <input
                      type="text"
                      value={formData.countryOfBirth}
                      onChange={(e) => handleInputChange('countryOfBirth', e.target.value)}
                      placeholder="Ex: Brasil"
                      className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Gênero
                    </label>
                    <select
                      value={formData.gender}
                      onChange={(e) => handleInputChange('gender', e.target.value)}
                      className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
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
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Endereço Atual <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.currentAddress}
                    onChange={(e) => handleInputChange('currentAddress', e.target.value)}
                    placeholder="Rua, número, apartamento"
                    className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                  />
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Cidade <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.city}
                      onChange={(e) => handleInputChange('city', e.target.value)}
                      placeholder="Cidade"
                      className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Estado
                    </label>
                    <input
                      type="text"
                      value={formData.state}
                      onChange={(e) => handleInputChange('state', e.target.value)}
                      placeholder="Estado"
                      className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      CEP/ZIP <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.zipCode}
                      onChange={(e) => handleInputChange('zipCode', e.target.value)}
                      placeholder="00000-000"
                      className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Telefone
                    </label>
                    <input
                      type="tel"
                      value={formData.phoneNumber}
                      onChange={(e) => handleInputChange('phoneNumber', e.target.value)}
                      placeholder="+1 (555) 123-4567"
                      className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      placeholder="seu@email.com"
                      className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
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
                    <label className="block text-sm font-medium text-foreground mb-2">
                      A-Number (se aplicável)
                    </label>
                    <input
                      type="text"
                      value={formData.alienNumber}
                      onChange={(e) => handleInputChange('alienNumber', e.target.value)}
                      placeholder="A123456789"
                      className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      SSN (se aplicável)
                    </label>
                    <input
                      type="text"
                      value={formData.socialSecurityNumber}
                      onChange={(e) => handleInputChange('socialSecurityNumber', e.target.value)}
                      placeholder="000-00-0000"
                      className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Status Atual nos EUA
                    </label>
                    <input
                      type="text"
                      value={formData.currentStatus}
                      onChange={(e) => handleInputChange('currentStatus', e.target.value)}
                      placeholder="Ex: F-1, H-1B, Residente Permanente"
                      className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Expiração do Status
                    </label>
                    <input
                      type="date"
                      value={formData.statusExpiration}
                      onChange={(e) => handleInputChange('statusExpiration', e.target.value)}
                      className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-between items-center">
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
                onClick={continueToNextStep}
                disabled={!isFormValid() || isSaving}
                className="bg-black text-white hover:bg-gray-800 flex items-center gap-2"
              >
                Continuar para Documentos
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Form Requirements */}
            {visaSpecs && (
              <Card className="glass border-0">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold flex items-center gap-2">
                    <Info className="h-5 w-5 text-black" />
                    Sobre {visaSpecs.specifications.title}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    {visaSpecs.specifications.description}
                  </p>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Taxa USCIS:</span>
                      <div className="font-medium">{visaSpecs.specifications.uscis_fee}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Prazo:</span>
                      <div className="font-medium">{visaSpecs.specifications.processing_time}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Progress */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">Progresso da Aplicação</CardTitle>
              </CardHeader>
              <CardContent>
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
                    <span className="text-sm text-muted-foreground">Upload de Documentos</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      3
                    </div>
                    <span className="text-sm text-muted-foreground">Conte sua História</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      4
                    </div>
                    <span className="text-sm text-muted-foreground">Formulário Amigável</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      5
                    </div>
                    <span className="text-sm text-muted-foreground">Revisão Final</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                      6
                    </div>
                    <span className="text-sm text-muted-foreground">Pagamento & Download</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Auto Save Info */}
            <Card className="glass border-0 bg-gray-50">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-gray-700" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Salvamento Automático</p>
                    <p className="text-xs text-muted-foreground">
                      Suas informações são salvas automaticamente a cada 30 segundos
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BasicData;