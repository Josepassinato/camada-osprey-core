import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  ArrowLeft,
  ArrowRight,
  Eye,
  CheckCircle,
  AlertTriangle,
  Save,
  RefreshCw,
  Info,
  Edit,
  FileText,
  Languages,
  Download,
  Flag,
  User,
  MapPin,
  Calendar,
  Briefcase
} from "lucide-react";

interface ComparisonField {
  label: string;
  portuguese: string;
  english: string;
  status: 'correct' | 'warning' | 'error';
  suggestion?: string;
}

interface FormSection {
  title: string;
  icon: any;
  fields: ComparisonField[];
  hasIssues: boolean;
}

const VisualReview = () => {
  const { caseId } = useParams();
  const navigate = useNavigate();
  
  const [case_, setCase] = useState<any>(null);
  const [visaSpecs, setVisaSpecs] = useState<any>(null);
  const [formSections, setFormSections] = useState<FormSection[]>([]);
  const [issues, setIssues] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState("");
  const [showPortuguese, setShowPortuguese] = useState(true);
  const [currentView, setCurrentView] = useState<'side-by-side' | 'english-only' | 'portuguese-only'>('side-by-side');

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
        
        if (data.case.form_code) {
          await fetchVisaSpecs(data.case.form_code);
        }
        
        generateFormComparison(data.case);
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

  const generateFormComparison = (caseData: any) => {
    const portugueseResponses = caseData.simplified_form_responses || {};
    const englishForm = caseData.official_form_data || {};
    const foundIssues: any[] = [];
    const hasOfficialForm = englishForm && Object.keys(englishForm).length > 0;

    const sections: FormSection[] = [
      {
        title: 'Informações Pessoais',
        icon: User,
        hasIssues: false,
        fields: [
          {
            label: 'Nome Completo',
            portuguese: portugueseResponses.personal?.full_name || 'Não informado',
            english: hasOfficialForm ? (englishForm.full_name || englishForm.applicant_name || 'Not provided') : 'Aguardando processamento IA',
            status: 'correct'
          },
          {
            label: 'Data de Nascimento',
            portuguese: portugueseResponses.personal?.date_of_birth || 'Não informado',
            english: hasOfficialForm ? (englishForm.date_of_birth || englishForm.birth_date || 'Not provided') : 'Aguardando processamento IA',
            status: 'correct'
          },
          {
            label: 'Local de Nascimento',
            portuguese: portugueseResponses.personal?.place_of_birth || 'Não informado',
            english: hasOfficialForm ? (englishForm.place_of_birth || englishForm.birth_place || 'Not provided') : 'Aguardando processamento IA',
            status: 'correct'
          },
          {
            label: 'Nacionalidade',
            portuguese: portugueseResponses.personal?.nationality || 'Não informado',
            english: hasOfficialForm ? (englishForm.nationality || englishForm.country_of_citizenship || 'Not provided') : 'Aguardando processamento IA',
            status: 'correct'
          }
        ]
      },
      {
        title: 'Informações de Endereço',
        icon: MapPin,
        hasIssues: false,
        fields: [
          {
            label: 'Endereço Atual',
            portuguese: portugueseResponses.address?.current_address || 'Não informado',
            english: hasOfficialForm ? (englishForm.current_address || englishForm.mailing_address || 'Not provided') : 'Aguardando processamento IA',
            status: 'correct'
          },
          {
            label: 'Telefone',
            portuguese: portugueseResponses.address?.phone || 'Não informado',
            english: hasOfficialForm ? (englishForm.phone_number || englishForm.telephone || 'Not provided') : 'Aguardando processamento IA',
            status: 'correct'
          },
          {
            label: 'E-mail',
            portuguese: portugueseResponses.address?.email || 'Não informado',
            english: englishForm.email_address || englishForm.email || 'Not provided',
            status: 'correct'
          }
        ]
      }
    ];

    // Add family section if available
    if (portugueseResponses.family || englishForm.spouse_name || englishForm.marital_status) {
      sections.push({
        title: 'Informações Familiares',
        icon: User,
        hasIssues: false,
        fields: [
          {
            label: 'Estado Civil',
            portuguese: portugueseResponses.family?.marital_status || 'Não informado',
            english: englishForm.marital_status || 'Not provided',
            status: 'correct'
          },
          {
            label: 'Nome do Cônjuge',
            portuguese: portugueseResponses.family?.spouse_name || 'Não informado',
            english: englishForm.spouse_name || englishForm.spouse_full_name || 'Not provided',
            status: 'correct'
          }
        ]
      });
    }

    // Add employment section if available
    if (portugueseResponses.employment || englishForm.employer_name || englishForm.current_job) {
      sections.push({
        title: 'Informações de Trabalho',
        icon: Briefcase,
        hasIssues: false,
        fields: [
          {
            label: 'Emprego Atual',
            portuguese: portugueseResponses.employment?.current_job || 'Não informado',
            english: englishForm.current_occupation || englishForm.job_title || 'Not provided',
            status: 'correct'
          },
          {
            label: 'Nome do Empregador',
            portuguese: portugueseResponses.employment?.employer_name || 'Não informado',
            english: englishForm.employer_name || englishForm.company_name || 'Not provided',
            status: 'correct'
          },
          {
            label: 'Salário',
            portuguese: portugueseResponses.employment?.salary || 'Não informado',
            english: englishForm.annual_salary || englishForm.salary || 'Not provided',
            status: 'correct'
          }
        ]
      });
    }

    // Simulate validation and flag issues
    sections.forEach(section => {
      section.fields.forEach(field => {
        // Check for missing information
        if (field.portuguese === 'Não informado' && field.english === 'Not provided') {
          field.status = 'error';
          section.hasIssues = true;
          foundIssues.push({
            section: section.title,
            field: field.label,
            issue: 'Informação não fornecida',
            severity: 'high'
          });
        }
        // Check for potential translation issues (length differences)
        else if (field.portuguese.length > 0 && field.english.length > 0) {
          const lengthRatio = field.english.length / field.portuguese.length;
          if (lengthRatio < 0.5 || lengthRatio > 2) {
            field.status = 'warning';
            field.suggestion = 'Tradução pode estar incompleta - verifique manualmente';
            foundIssues.push({
              section: section.title,
              field: field.label,
              issue: 'Possível inconsistência na tradução',
              severity: 'medium'
            });
          }
        }
        // Check for date format issues
        if (field.label.includes('Data') && field.english !== 'Not provided') {
          const dateRegex = /^\d{2}\/\d{2}\/\d{4}$/;
          if (!dateRegex.test(field.english) && field.english.includes('/')) {
            field.status = 'warning';
            field.suggestion = 'Formato de data deve ser MM/DD/YYYY';
            foundIssues.push({
              section: section.title,
              field: field.label,
              issue: 'Formato de data incorreto',
              severity: 'medium'
            });
          }
        }
      });
    });

    setFormSections(sections);
    setIssues(foundIssues);
  };

  const validateForms = async () => {
    setIsValidating(true);
    
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/validate-forms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_id: caseId,
          form_code: case_.form_code
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Update issues with validation results
        setIssues(data.validation_issues || []);
        
        // Re-generate comparison with validation results
        generateFormComparison(case_);
        
      } else {
        setError('Erro ao validar formulários');
      }
      
    } catch (error) {
      console.error('Validate forms error:', error);
      setError('Erro de conexão ao validar formulários');
    } finally {
      setIsValidating(false);
    }
  };

  const approveForPayment = async () => {
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
          status: 'reviewed'
        }),
      });

    } catch (error) {
      console.error('Approve error:', error);
    }
  };

  const getIssuesByLevel = (level: string) => {
    return issues.filter(issue => issue.severity === level);
  };

  const hasBlockingIssues = () => {
    return issues.some(issue => issue.severity === 'high');
  };

  const canContinue = () => {
    return !hasBlockingIssues();
  };

  const continueToNextStep = async () => {
    await approveForPayment();
    navigate(`/auto-application/case/${caseId}/payment`);
  };

  const renderFieldComparison = (field: ComparisonField, sectionIndex: number, fieldIndex: number) => {
    const getStatusColor = (status: string) => {
      switch (status) {
        case 'correct': return 'text-green-600';
        case 'warning': return 'text-yellow-600';
        case 'error': return 'text-red-600';
        default: return 'text-gray-600';
      }
    };

    const getStatusIcon = (status: string) => {
      switch (status) {
        case 'correct': return <CheckCircle className="h-4 w-4 text-green-600" />;
        case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
        case 'error': return <Flag className="h-4 w-4 text-red-600" />;
        default: return null;
      }
    };

    return (
      <div key={`${sectionIndex}-${fieldIndex}`} className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-foreground">{field.label}</label>
          <div className="flex items-center gap-1">
            {getStatusIcon(field.status)}
            <span className={`text-xs ${getStatusColor(field.status)}`}>
              {field.status === 'correct' && 'OK'}
              {field.status === 'warning' && 'Verificar'}
              {field.status === 'error' && 'Erro'}
            </span>
          </div>
        </div>

        {currentView === 'side-by-side' && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-muted-foreground mb-1">Português (Original)</p>
              <div className="p-2 bg-blue-50 rounded text-sm border">
                {field.portuguese}
              </div>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Inglês (USCIS)</p>
              <div className="p-2 bg-gray-50 rounded text-sm border">
                {field.english}
              </div>
            </div>
          </div>
        )}

        {currentView === 'portuguese-only' && (
          <div className="p-2 bg-blue-50 rounded text-sm border">
            {field.portuguese}
          </div>
        )}

        {currentView === 'english-only' && (
          <div className="p-2 bg-gray-50 rounded text-sm border">
            {field.english}
          </div>
        )}

        {field.suggestion && (
          <div className="text-xs text-amber-700 bg-amber-50 p-2 rounded">
            <Info className="h-3 w-3 inline mr-1" />
            {field.suggestion}
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Preparando revisão visual...</p>
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

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="glass border-b border-white/20">
        <div className="container-responsive py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate(`/auto-application/case/${caseId}/friendly-form`)}
                className="p-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Voltar
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                  <Eye className="h-8 w-8 text-black" />
                  {visaSpecs?.specifications.title || case_.form_code}
                </h1>
                <p className="text-muted-foreground">
                  Etapa 5 de 6: Revisão Visual • Caso: {case_.case_id}
                </p>
              </div>
            </div>
            <Badge className={`${hasBlockingIssues() ? 'bg-red-100 text-red-800 border-red-200' : issues.length > 0 ? 'bg-yellow-100 text-yellow-800 border-yellow-200' : 'bg-green-100 text-green-800 border-green-200'}`}>
              {hasBlockingIssues() ? 'Requer Atenção' : issues.length > 0 ? 'Verificar' : 'Aprovado'}
            </Badge>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-4 gap-8">
          
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            
            {/* View Controls */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold flex items-center gap-2">
                  <Eye className="h-5 w-5" />
                  Modo de Visualização
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  variant={currentView === 'side-by-side' ? 'default' : 'outline'}
                  onClick={() => setCurrentView('side-by-side')}
                  className="w-full justify-start"
                >
                  <Languages className="h-4 w-4 mr-2" />
                  Lado a Lado
                </Button>
                <Button
                  variant={currentView === 'english-only' ? 'default' : 'outline'}
                  onClick={() => setCurrentView('english-only')}
                  className="w-full justify-start"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Apenas Inglês
                </Button>
                <Button
                  variant={currentView === 'portuguese-only' ? 'default' : 'outline'}
                  onClick={() => setCurrentView('portuguese-only')}
                  className="w-full justify-start"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Apenas Português
                </Button>
              </CardContent>
            </Card>

            {/* Issues Summary */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold flex items-center gap-2">
                  <Flag className="h-5 w-5" />
                  Problemas Encontrados
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Críticos</span>
                    <Badge variant={getIssuesByLevel('high').length > 0 ? 'destructive' : 'outline'}>
                      {getIssuesByLevel('high').length}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Advertências</span>
                    <Badge variant={getIssuesByLevel('medium').length > 0 ? 'secondary' : 'outline'}>
                      {getIssuesByLevel('medium').length}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Informações</span>
                    <Badge variant="outline">
                      {getIssuesByLevel('low').length}
                    </Badge>
                  </div>
                </div>

                {issues.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h4 className="text-sm font-medium mb-2">Detalhes:</h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {issues.map((issue, index) => (
                        <div key={index} className="text-xs p-2 bg-gray-50 rounded">
                          <div className="font-medium">{issue.section} - {issue.field}</div>
                          <div className="text-gray-600">{issue.issue}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Progress Steps */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">Progresso da Aplicação</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-700 text-white rounded-full flex items-center justify-center text-xs font-bold">
                      ✓
                    </div>
                    <span className="text-sm text-gray-700">Dados Básicos</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-700 text-white rounded-full flex items-center justify-center text-xs font-bold">
                      ✓
                    </div>
                    <span className="text-sm text-gray-700">Upload de Documentos</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-700 text-white rounded-full flex items-center justify-center text-xs font-bold">
                      ✓
                    </div>
                    <span className="text-sm text-gray-700">Conte sua História</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gray-700 text-white rounded-full flex items-center justify-center text-xs font-bold">
                      ✓
                    </div>
                    <span className="text-sm text-gray-700">Formulário Amigável</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-black text-white rounded-full flex items-center justify-center text-xs font-bold">
                      5
                    </div>
                    <span className="text-sm font-medium">Revisão Visual</span>
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
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            
            {/* Actions */}
            <Card className="glass border-0 bg-gray-50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-foreground">Validação Final</h3>
                    <p className="text-sm text-muted-foreground">
                      Verifique se todas as informações estão corretas antes de prosseguir
                    </p>
                  </div>
                  <Button
                    onClick={validateForms}
                    disabled={isValidating}
                    variant="outline"
                  >
                    {isValidating ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <CheckCircle className="h-4 w-4" />
                    )}
                    Validar Novamente
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Form Sections */}
            <div className="space-y-6">
              {formSections.map((section, sectionIndex) => {
                const IconComponent = section.icon;
                return (
                  <Card key={section.title} className="glass border-0">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-3">
                        <IconComponent className="h-6 w-6 text-black" />
                        <span>{section.title}</span>
                        {section.hasIssues && (
                          <Flag className="h-4 w-4 text-red-500" />
                        )}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {section.fields.map((field, fieldIndex) => 
                        renderFieldComparison(field, sectionIndex, fieldIndex)
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Final Actions */}
            <div className="flex justify-between items-center">
              <div className="text-sm text-muted-foreground">
                {canContinue() ? (
                  <div className="flex items-center gap-2 text-gray-700">
                    <CheckCircle className="h-4 w-4" />
                    <span>Formulários revisados e aprovados para submissão</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <span className="text-red-600">
                      Existem {getIssuesByLevel('high').length} problema(s) crítico(s) que precisam ser corrigidos
                    </span>
                  </div>
                )}
              </div>

              <Button 
                onClick={continueToNextStep}
                disabled={!canContinue()}
                className="bg-black text-white hover:bg-gray-800 flex items-center gap-2"
              >
                Aprovar e Continuar
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VisualReview;