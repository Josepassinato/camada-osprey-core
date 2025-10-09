import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import OspreyOwlTutor from "@/components/OspreyOwlTutor";
import SaveAndContinueModal from "@/components/SaveAndContinueModal";
import { useFormSnapshot } from "@/hooks/useFormSnapshot";
import { useSessionManager } from "@/hooks/useSessionManager";
import { useToast } from "@/components/ui/use-toast";
import { 
  ArrowLeft,
  ArrowRight,
  FileText,
  AlertTriangle,
  CheckCircle,
  Save,
  Info,
  Download,
  ClipboardList,
  User,
  Calendar,
  MapPin,
  Building
} from "lucide-react";

interface USCISFormData {
  // Personal Information (from BasicData)
  firstName: string;
  middleName: string;
  lastName: string;
  dateOfBirth: string;
  countryOfBirth: string;
  currentAddress: string;
  city: string;
  state: string;
  zipCode: string;
  phone: string;
  email: string;
  
  // USCIS Form Specific Fields
  alienNumber: string;
  socialSecurityNumber: string;
  passportNumber: string;
  passportCountry: string;
  passportExpirationDate: string;
  
  // Employment Information (for H-1B, L-1, O-1)
  employerName: string;
  employerAddress: string;
  jobTitle: string;
  jobDescription: string;
  salaryAmount: string;
  startDate: string;
  
  // Education Information (for F-1, H-1B)
  schoolName: string;
  degreeLevel: string;
  fieldOfStudy: string;
  graduationDate: string;
  
  // Family Information (for I-130, I-485)
  maritalStatus: string;
  spouseName: string;
  spouseDateOfBirth: string;
  numberOfChildren: string;
  
  // Additional Questions
  previousUSVisits: boolean;
  previousVisaApplications: boolean;
  criminalHistory: boolean;
  additionalInfo: string;
}

const USCISFormFilling = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [formData, setFormData] = useState<USCISFormData>({
    firstName: '',
    middleName: '',
    lastName: '',
    dateOfBirth: '',
    countryOfBirth: '',
    currentAddress: '',
    city: '',
    state: '',
    zipCode: '',
    phone: '',
    email: '',
    alienNumber: '',
    socialSecurityNumber: '',
    passportNumber: '',
    passportCountry: '',
    passportExpirationDate: '',
    employerName: '',
    employerAddress: '',
    jobTitle: '',
    jobDescription: '',
    salaryAmount: '',
    startDate: '',
    schoolName: '',
    degreeLevel: '',
    fieldOfStudy: '',
    graduationDate: '',
    maritalStatus: '',
    spouseName: '',
    spouseDateOfBirth: '',
    numberOfChildren: '',
    previousUSVisits: false,
    previousVisaApplications: false,
    criminalHistory: false,
    additionalInfo: ''
  });

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [case_, setCase] = useState<any>(null);
  const [visaSpecs, setVisaSpecs] = useState<any>(null);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [activeSection, setActiveSection] = useState("personal");
  const [formReviewed, setFormReviewed] = useState(false);
  const [formAuthorized, setFormAuthorized] = useState(false);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [autoFilledData, setAutoFilledData] = useState<any>({});
  const [validationResult, setValidationResult] = useState<any>(null);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [isValidating, setIsValidating] = useState(false);

  // Session management
  const { 
    sessionData, 
    setCaseId, 
    setCurrentStep, 
    getCaseId,
    getSessionToken,
    isSessionActive 
  } = useSessionManager();

  // Form snapshot for AI analysis
  const { snapshot } = useFormSnapshot(formData, {
    enabled: true,
    autoGenerate: true,
    onSnapshotUpdate: (snapshot) => {
      console.log('🦉 USCIS Form snapshot updated:', snapshot);
    },
    onError: (error) => {
      console.error('🦉 USCIS Form snapshot error:', error);
    }
  });

  useEffect(() => {
    if (caseId) {
      fetchCase();
      fetchVisaSpecs();
      loadIntelligentSuggestions();
    }
  }, [caseId]);

  const fetchCase = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}`);
      if (response.ok) {
        const data = await response.json();
        setCase(data.case);
        
        // Pre-fill form with existing basic data
        if (data.case.basic_data) {
          const basicData = data.case.basic_data;
          setFormData(prev => ({
            ...prev,
            firstName: basicData.firstName || '',
            middleName: basicData.middleName || '',
            lastName: basicData.lastName || '',
            dateOfBirth: basicData.dateOfBirth || '',
            countryOfBirth: basicData.countryOfBirth || '',
            currentAddress: basicData.currentAddress || '',
            city: basicData.city || '',
            state: basicData.state || '',
            zipCode: basicData.zipCode || '',
            phone: basicData.phone || '',
            email: basicData.email || ''
          }));
        }
        
        // Load existing USCIS form data if available
        if (data.case.uscis_form_data) {
          setFormData(prev => ({
            ...prev,
            ...data.case.uscis_form_data
          }));
        }
      }
    } catch (error) {
      console.error('Error fetching case:', error);
      toast({
        title: "Erro",
        description: "Erro ao carregar dados do caso",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchVisaSpecs = async () => {
    try {
      if (!case_?.form_code) return;
      
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/visa-specs/${case_.form_code}`);
      if (response.ok) {
        const data = await response.json();
        setVisaSpecs(data.specifications);
      }
    } catch (error) {
      console.error('Error fetching visa specs:', error);
    }
  };

  const loadIntelligentSuggestions = async () => {
    if (!caseId || !case_?.form_code) return;
    
    setIsLoadingSuggestions(true);
    try {
      console.log('🤖 Carregando sugestões inteligentes...');
      
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/intelligent-forms/suggestions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_id: caseId,
          form_code: case_.form_code,
          current_form_data: formData
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
        console.log(`✅ ${data.suggestions?.length || 0} sugestões carregadas`);
        
        // Auto-preencher campos com alta confiança
        const highConfidenceSuggestions = data.suggestions?.filter((s: any) => s.confidence > 0.85) || [];
        if (highConfidenceSuggestions.length > 0) {
          autoFillFromSuggestions(highConfidenceSuggestions);
        }
      }
    } catch (error) {
      console.error('Erro ao carregar sugestões:', error);
    } finally {
      setIsLoadingSuggestions(false);
    }
  };

  const autoFillFromSuggestions = (suggestions: any[]) => {
    const autoFillData: any = {};
    
    suggestions.forEach(suggestion => {
      if (suggestion.confidence > 0.85 && suggestion.suggested_value) {
        autoFillData[suggestion.field_id] = suggestion.suggested_value;
      }
    });
    
    if (Object.keys(autoFillData).length > 0) {
      setFormData(prev => ({ ...prev, ...autoFillData }));
      setAutoFilledData(autoFillData);
      
      toast({
        title: "Preenchimento Automático",
        description: `${Object.keys(autoFillData).length} campos preenchidos automaticamente com base nos seus documentos`,
      });
    }
  };

  const validateFormWithAI = async () => {
    if (!case_?.form_code) return;
    
    setIsValidating(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/intelligent-forms/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          form_data: formData,
          visa_type: case_.form_code,
          step_id: "form_review"
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setValidationResult(data.validation_result);
        
        if (data.validation_result?.errors?.length > 0) {
          toast({
            title: "Problemas Encontrados",
            description: `${data.validation_result.errors.length} erro(s) detectado(s) pela Dra. Ana`,
            variant: "destructive",
          });
        } else {
          toast({
            title: "Formulário Validado",
            description: "Dra. Ana aprovou o formulário!",
          });
        }
      }
    } catch (error) {
      console.error('Erro na validação:', error);
      toast({
        title: "Erro na Validação",
        description: "Não foi possível validar o formulário",
        variant: "destructive",
      });
    } finally {
      setIsValidating(false);
    }
  };

  const handleInputChange = (field: keyof USCISFormData, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const saveUSCISFormData = async () => {
    if (!caseId) return;
    
    setIsSaving(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}/uscis-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          uscis_form_data: formData,
          completed_sections: getCompletedSections()
        }),
      });

      if (response.ok) {
        toast({
          title: "Sucesso",
          description: "Formulário USCIS salvo com sucesso",
        });
        setCurrentStep("uscis-form");
        return true;
      } else {
        throw new Error('Failed to save USCIS form data');
      }
    } catch (error) {
      console.error('Error saving USCIS form:', error);
      toast({
        title: "Erro",
        description: "Erro ao salvar formulário USCIS",
        variant: "destructive",
      });
      return false;
    } finally {
      setIsSaving(false);
    }
  };

  const getCompletedSections = () => {
    const sections = [];
    if (formData.firstName && formData.lastName && formData.dateOfBirth) {
      sections.push("personal");
    }
    if (formData.passportNumber && formData.passportCountry) {
      sections.push("passport");
    }
    if (formData.employerName && formData.jobTitle) {
      sections.push("employment");
    }
    if (formData.schoolName && formData.degreeLevel) {
      sections.push("education");
    }
    return sections;
  };

  const isFormAuthorized = () => {
    return formReviewed && formAuthorized;
  };

  const authorizeAndSaveForm = async () => {
    if (!isFormAuthorized()) return;
    
    setIsSaving(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}/authorize-uscis-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          form_reviewed: formReviewed,
          form_authorized: formAuthorized,
          generated_form_data: case_?.ai_generated_uscis_form || {},
          authorization_timestamp: new Date().toISOString()
        }),
      });

      if (response.ok) {
        toast({
          title: "Sucesso!",
          description: "Formulário USCIS autorizado e salvo automaticamente na sua pasta",
        });
        
        // Navigate to documents page
        navigate(`/auto-application/case/${caseId}/documents`);
      } else {
        throw new Error('Failed to authorize and save form');
      }
    } catch (error) {
      console.error('Error authorizing form:', error);
      toast({
        title: "Erro",
        description: "Erro ao autorizar formulário. Tente novamente.",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const renderPersonalSection = () => (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-4">
        <div className="relative">
          <Label htmlFor="firstName">Nome *</Label>
          <Input
            id="firstName"
            value={formData.firstName}
            onChange={(e) => handleInputChange('firstName', e.target.value)}
            placeholder="Primeiro nome"
            required
            className={autoFilledData.firstName ? 'border-blue-500 bg-blue-50' : ''}
          />
          {autoFilledData.firstName && (
            <div className="absolute -top-1 -right-1 w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-xs">IA</span>
            </div>
          )}
        </div>
        <div className="relative">
          <Label htmlFor="lastName">Sobrenome *</Label>
          <Input
            id="lastName"
            value={formData.lastName}
            onChange={(e) => handleInputChange('lastName', e.target.value)}
            placeholder="Último nome"
            required
            className={autoFilledData.lastName ? 'border-blue-500 bg-blue-50' : ''}
          />
          {autoFilledData.lastName && (
            <div className="absolute -top-1 -right-1 w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-xs">IA</span>
            </div>
          )}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="dateOfBirth">Data de Nascimento *</Label>
          <Input
            id="dateOfBirth"
            type="date"
            value={formData.dateOfBirth}
            onChange={(e) => handleInputChange('dateOfBirth', e.target.value)}
            required
          />
        </div>
        <div>
          <Label htmlFor="countryOfBirth">País de Nascimento *</Label>
          <Input
            id="countryOfBirth"
            value={formData.countryOfBirth}
            onChange={(e) => handleInputChange('countryOfBirth', e.target.value)}
            placeholder="Brasil"
            required
          />
        </div>
      </div>

      <div>
        <Label htmlFor="currentAddress">Endereço Atual *</Label>
        <Textarea
          id="currentAddress"
          value={formData.currentAddress}
          onChange={(e) => handleInputChange('currentAddress', e.target.value)}
          placeholder="Endereço completo"
          required
        />
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div>
          <Label htmlFor="city">Cidade *</Label>
          <Input
            id="city"
            value={formData.city}
            onChange={(e) => handleInputChange('city', e.target.value)}
            placeholder="Cidade"
            required
          />
        </div>
        <div>
          <Label htmlFor="state">Estado/Província *</Label>
          <Input
            id="state"
            value={formData.state}
            onChange={(e) => handleInputChange('state', e.target.value)}
            placeholder="Estado"
            required
          />
        </div>
        <div>
          <Label htmlFor="zipCode">CEP *</Label>
          <Input
            id="zipCode"
            value={formData.zipCode}
            onChange={(e) => handleInputChange('zipCode', e.target.value)}
            placeholder="00000-000"
            required
          />
        </div>
      </div>
    </div>
  );

  const renderPassportSection = () => (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="passportNumber">Número do Passaporte *</Label>
          <Input
            id="passportNumber"
            value={formData.passportNumber}
            onChange={(e) => handleInputChange('passportNumber', e.target.value)}
            placeholder="BR1234567"
            required
          />
        </div>
        <div>
          <Label htmlFor="passportCountry">País Emissor *</Label>
          <Input
            id="passportCountry"
            value={formData.passportCountry}
            onChange={(e) => handleInputChange('passportCountry', e.target.value)}
            placeholder="Brasil"
            required
          />
        </div>
      </div>
      
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="passportExpirationDate">Data de Expiração *</Label>
          <Input
            id="passportExpirationDate"
            type="date"
            value={formData.passportExpirationDate}
            onChange={(e) => handleInputChange('passportExpirationDate', e.target.value)}
            required
          />
        </div>
        <div>
          <Label htmlFor="alienNumber">Alien Number (se aplicável)</Label>
          <Input
            id="alienNumber"
            value={formData.alienNumber}
            onChange={(e) => handleInputChange('alienNumber', e.target.value)}
            placeholder="123456789"
          />
        </div>
      </div>
    </div>
  );

  const renderEmploymentSection = () => (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="employerName">Nome do Empregador</Label>
          <Input
            id="employerName"
            value={formData.employerName}
            onChange={(e) => handleInputChange('employerName', e.target.value)}
            placeholder="Nome da empresa"
          />
        </div>
        <div>
          <Label htmlFor="jobTitle">Título do Cargo</Label>
          <Input
            id="jobTitle"
            value={formData.jobTitle}
            onChange={(e) => handleInputChange('jobTitle', e.target.value)}
            placeholder="Software Engineer"
          />
        </div>
      </div>

      <div>
        <Label htmlFor="jobDescription">Descrição do Trabalho</Label>
        <Textarea
          id="jobDescription"
          value={formData.jobDescription}
          onChange={(e) => handleInputChange('jobDescription', e.target.value)}
          placeholder="Descreva as principais responsabilidades..."
          rows={4}
        />
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="salaryAmount">Salário Anual (USD)</Label>
          <Input
            id="salaryAmount"
            value={formData.salaryAmount}
            onChange={(e) => handleInputChange('salaryAmount', e.target.value)}
            placeholder="85000"
          />
        </div>
        <div>
          <Label htmlFor="startDate">Data de Início</Label>
          <Input
            id="startDate"
            type="date"
            value={formData.startDate}
            onChange={(e) => handleInputChange('startDate', e.target.value)}
          />
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
            <span>Etapa 5 de 8</span>
            <span>•</span>
            <span>Revisão e Autorização do Formulário USCIS</span>
          </div>
          
          <h1 className="text-3xl font-bold text-black mb-2">
            Revisar Formulário USCIS {case_?.form_code}
          </h1>
          
          <p className="text-gray-600">
            ✅ Formulário oficial gerado pela IA com base nas suas respostas. 
            Revise cuidadosamente e autorize para salvar automaticamente na sua pasta.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Intelligent Suggestions Banner */}
            {suggestions.length > 0 && (
              <Card className="border-blue-500 bg-blue-50">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                        <span className="text-white text-sm font-bold">IA</span>
                      </div>
                      <div>
                        <h4 className="font-semibold text-blue-800">Preenchimento Inteligente</h4>
                        <p className="text-sm text-blue-600">
                          {suggestions.length} sugestões baseadas nos seus documentos validados
                        </p>
                      </div>
                    </div>
                    {isLoadingSuggestions && (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    )}
                  </div>
                  
                  {Object.keys(autoFilledData).length > 0 && (
                    <div className="mt-3 p-3 bg-white rounded-lg border border-blue-200">
                      <p className="text-sm font-medium text-blue-800">
                        ✅ {Object.keys(autoFilledData).length} campos preenchidos automaticamente
                      </p>
                      <p className="text-xs text-blue-600 mt-1">
                        Baseado na análise dos seus documentos com alta confiança (85%+)
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* AI Validation Results */}
            {validationResult && (
              <Card className={`border-2 ${validationResult.is_valid ? 'border-green-500 bg-green-50' : 'border-orange-500 bg-orange-50'}`}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${validationResult.is_valid ? 'bg-green-600' : 'bg-orange-600'}`}>
                        {validationResult.is_valid ? (
                          <CheckCircle className="h-4 w-4 text-white" />
                        ) : (
                          <AlertTriangle className="h-4 w-4 text-white" />
                        )}
                      </div>
                      <div>
                        <h4 className={`font-semibold ${validationResult.is_valid ? 'text-green-800' : 'text-orange-800'}`}>
                          Dra. Ana - Validação
                        </h4>
                        <p className={`text-sm ${validationResult.is_valid ? 'text-green-600' : 'text-orange-600'}`}>
                          Completude: {validationResult.completeness_score}% | {validationResult.errors?.length || 0} erro(s)
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={validateFormWithAI}
                      disabled={isValidating}
                      className="ml-auto"
                    >
                      {isValidating ? 'Validando...' : 'Revalidar'}
                    </Button>
                  </div>
                  
                  {validationResult.errors?.length > 0 && (
                    <div className="mt-3">
                      <h5 className="font-medium text-orange-800 mb-2">Problemas Encontrados:</h5>
                      <ul className="space-y-1">
                        {validationResult.errors.map((error: any, index: number) => (
                          <li key={index} className="text-sm text-orange-700 flex items-start gap-2">
                            <AlertTriangle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                            {error.message || error}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Progress */}
            <Card className="border-black">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold">Progresso do Formulário</h3>
                  <Badge variant="outline">{getCompletedSections().length}/4 seções</Badge>
                </div>
                
                <div className="grid grid-cols-4 gap-2">
                  {[
                    { id: 'personal', label: 'Pessoal', icon: User },
                    { id: 'passport', label: 'Passaporte', icon: FileText },
                    { id: 'employment', label: 'Emprego', icon: Building },
                    { id: 'education', label: 'Educação', icon: ClipboardList }
                  ].map(({ id, label, icon: Icon }) => (
                    <button
                      key={id}
                      onClick={() => setActiveSection(id)}
                      className={`p-3 rounded-lg border text-sm font-medium transition-colors ${
                        activeSection === id
                          ? 'bg-black text-white border-black'
                          : 'bg-white text-gray-700 border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <Icon className="h-4 w-4 mx-auto mb-1" />
                      {label}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Form Sections */}
            <Card className="border-black">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  {activeSection === 'personal' && 'Informações Pessoais'}
                  {activeSection === 'passport' && 'Informações do Passaporte'}
                  {activeSection === 'employment' && 'Informações de Emprego'}
                  {activeSection === 'education' && 'Informações Educacionais'}
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                {activeSection === 'personal' && renderPersonalSection()}
                {activeSection === 'passport' && renderPassportSection()}
                {activeSection === 'employment' && renderEmploymentSection()}
                {activeSection === 'education' && (
                  <div className="text-center py-8 text-gray-500">
                    <ClipboardList className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Seção educacional em desenvolvimento</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Authorization Section */}
            <Card className="border-green-500 bg-green-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-800">
                  <CheckCircle className="h-5 w-5" />
                  Autorização do Formulário
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-white p-4 rounded-lg border">
                  <div className="flex items-start gap-3">
                    <Checkbox 
                      id="form-review"
                      className="mt-1"
                      checked={formReviewed}
                      onCheckedChange={(checked) => setFormReviewed(checked as boolean)}
                    />
                    <div className="flex-1">
                      <Label htmlFor="form-review" className="text-sm font-medium cursor-pointer">
                        Revisão Completa
                      </Label>
                      <p className="text-sm text-gray-600 mt-1">
                        Confirmo que revisei cuidadosamente todas as informações no formulário USCIS 
                        e elas estão corretas e completas.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-4 rounded-lg border">
                  <div className="flex items-start gap-3">
                    <Checkbox 
                      id="form-authorize"
                      className="mt-1"
                      checked={formAuthorized}
                      onCheckedChange={(checked) => setFormAuthorized(checked as boolean)}
                    />
                    <div className="flex-1">
                      <Label htmlFor="form-authorize" className="text-sm font-medium cursor-pointer">
                        Autorização de Salvamento Automático
                      </Label>
                      <p className="text-sm text-gray-600 mt-1">
                        Autorizo o sistema a salvar automaticamente este formulário na minha pasta 
                        de documentos, eliminando a necessidade de download e upload manual.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-4 justify-between">
              <Button
                variant="outline"
                onClick={() => navigate(`/auto-application/case/${caseId}/ai-review`)}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Voltar para Processamento IA
              </Button>

              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  variant="outline"
                  onClick={() => setShowSaveModal(true)}
                  className="flex items-center gap-2 border-blue-500 text-blue-600 hover:bg-blue-50"
                >
                  <Save className="h-4 w-4" />
                  Salvar e Continuar Depois
                </Button>

                <Button 
                  onClick={authorizeAndSaveForm}
                  disabled={!isFormAuthorized() || isSaving}
                  className="bg-green-600 hover:bg-green-700 text-white flex items-center gap-2"
                >
                  <CheckCircle className="h-4 w-4" />
                  {isSaving ? 'Salvando...' : 'Autorizar e Salvar Automaticamente'}
                </Button>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Form Info */}
            {visaSpecs && (
              <Card className="border-black">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Info className="h-5 w-5" />
                    Sobre o Formulário {case_?.form_code}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-600">{visaSpecs.description}</p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="font-medium text-gray-700">Taxa USCIS</p>
                      <p className="text-black">{visaSpecs.uscis_fee}</p>
                    </div>
                    <div>
                      <p className="font-medium text-gray-700">Processamento</p>
                      <p className="text-black">{visaSpecs.processing_time}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Important Note */}
            <Alert className="border-orange-400 bg-orange-50">
              <AlertTriangle className="h-4 w-4 text-orange-600" />
              <AlertDescription className="text-orange-800">
                <strong>Importante:</strong> As informações preenchidas aqui serão utilizadas 
                para gerar automaticamente o formulário USCIS oficial. Certifique-se de que 
                todos os dados estão corretos.
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </div>

      {/* Osprey Owl Tutor */}
      <OspreyOwlTutor
        currentStage="uscis-form"
        formData={formData}
        onValidationRequest={async (validationData) => {
          console.log('🦉 USCIS Form validation requested:', validationData);
        }}
        isEnabled={!!case_?.case_id}
        position="bottom-right"
      />

      {/* Save and Continue Later Modal */}
      <SaveAndContinueModal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        caseId={caseId || ''}
        currentStage="Formulário USCIS"
        onSuccess={(userData) => {
          console.log('User authenticated:', userData);
          navigate('/dashboard');
        }}
      />
    </div>
  );
};

export default USCISFormFilling;