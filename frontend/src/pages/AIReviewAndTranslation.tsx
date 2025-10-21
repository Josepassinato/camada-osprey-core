import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  ArrowLeft,
  ArrowRight,
  Brain,
  CheckCircle,
  AlertTriangle,
  Zap,
  FileText,
  Languages,
  Eye,
  RefreshCw,
  Clock,
  Sparkles,
  Shield,
  Lightbulb,
  Wand2
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

interface ValidationIssue {
  field: string;
  issue: string;
  severity: 'error' | 'warning' | 'info';
  suggestion: string;
}

interface SystemProcessingStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  details?: string;
  duration?: number;
}

const SystemReviewAndTranslation = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [case_, setCase] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [validationIssues, setValidationIssues] = useState<ValidationIssue[]>([]);
  const [processingSteps, setProcessingSteps] = useState<SystemProcessingStep[]>([
    {
      id: 'validation',
      title: 'Validação de Dados',
      description: 'Sistema verifica se todas as respostas fazem sentido e estão completas',
      status: 'pending'
    },
    {
      id: 'consistency',
      title: 'Verificação de Consistência',
      description: 'Sistema confirma que informações são consistentes entre si',
      status: 'pending'
    },
    {
      id: 'translation',
      title: 'Tradução Inteligente',
      description: 'Sistema traduz respostas para inglês jurídico adequado ao USCIS',
      status: 'pending'
    },
    {
      id: 'form_generation',
      title: 'Geração do Formulário Oficial',
      description: 'Sistema mapeia dados para formulário USCIS oficial',
      status: 'pending'
    },
    {
      id: 'final_review',
      title: 'Revisão Final',
      description: 'Sistema confirma que formulário está completo e pronto',
      status: 'pending'
    }
  ]);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [allCompleted, setAllCompleted] = useState(false);

  useEffect(() => {
    if (caseId) {
      fetchCase();
    }
  }, [caseId]);

  const fetchCase = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}`);
      if (response.ok) {
        const data = await response.json();
        setCase(data.case);
        
        // Check if system processing was already completed
        if (data.case.uscis_form_generated) {
          setAllCompleted(true);
          setProcessingSteps(prev => prev.map(step => ({ ...step, status: 'completed' })));
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

  const startSystemProcessing = async () => {
    setIsProcessing(true);
    setCurrentStepIndex(0);
    
    try {
      // Process each step sequentially
      for (let i = 0; i < processingSteps.length; i++) {
        setCurrentStepIndex(i);
        
        // Update step to processing
        setProcessingSteps(prev => prev.map((step, index) => 
          index === i ? { ...step, status: 'processing' } : step
        ));
        
        // Call system processing for this step
        const result = await processAIStep(processingSteps[i].id);
        
        if (result.success) {
          // Update step to completed
          setProcessingSteps(prev => prev.map((step, index) => 
            index === i ? { 
              ...step, 
              status: 'completed', 
              details: result.details,
              duration: result.duration 
            } : step
          ));
          
          // Add any validation issues found
          if (result.issues) {
            setValidationIssues(prev => [...prev, ...result.issues]);
          }
        } else {
          // Update step to error
          setProcessingSteps(prev => prev.map((step, index) => 
            index === i ? { ...step, status: 'error', details: result.error } : step
          ));
          throw new Error(result.error);
        }
        
        // Wait a bit between steps for better UX
        await new Promise(resolve => setTimeout(resolve, 1500));
      }
      
      setAllCompleted(true);
      toast({
        title: "Sucesso!",
        description: "Formulário USCIS gerado com sucesso pela IA",
      });
      
    } catch (error) {
      console.error('AI processing error:', error);
      toast({
        title: "Erro no Processamento",
        description: "Erro durante o processamento da IA. Tente novamente.",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const processAIStep = async (stepId: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/ai-processing/step`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_id: caseId,
          step_id: stepId,
          friendly_form_data: case_?.simplified_form_responses || {},
          basic_data: case_?.basic_data || {}
        }),
      });

      if (response.ok) {
        const data = await response.json();
        return {
          success: true,
          details: data.details,
          duration: data.duration,
          issues: data.validation_issues || []
        };
      } else {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || 'Erro no processamento'
        };
      }
    } catch (error) {
      return {
        success: false,
        error: 'Erro de conexão'
      };
    }
  };

  const continueToUSCISForm = () => {
    navigate(`/auto-application/case/${caseId}/uscis-form`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
            <span>Etapa 4 de 8</span>
            <span>•</span>
            <span>Processamento IA e Tradução</span>
          </div>
          
          <h1 className="text-3xl font-bold text-black mb-2">
            Revisão Inteligente e Tradução
          </h1>
          
          <p className="text-gray-600">
            Nossa IA está analisando suas respostas, verificando consistência e gerando 
            o formulário USCIS oficial em inglês.
          </p>
        </div>

        {/* Main Content */}
        <div className="space-y-6">
          {/* AI Processing Status */}
          <Card className="border-black">
            <CardHeader className="bg-black text-white">
              <CardTitle className="flex items-center gap-3">
                <Brain className="h-6 w-6" />
                Processamento da Inteligência Artificial
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              {!isProcessing && !allCompleted && (
                <div className="text-center py-8">
                  <Sparkles className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-semibold mb-2">Pronto para Processamento</h3>
                  <p className="text-gray-600 mb-6">
                    Clique no botão abaixo para iniciar o processamento inteligente do seu formulário.
                  </p>
                  <Button
                    onClick={startAIProcessing}
                    className="bg-black text-white hover:bg-gray-800 px-8 py-3"
                    size="lg"
                  >
                    <Wand2 className="h-5 w-5 mr-2" />
                    Iniciar Processamento IA
                  </Button>
                </div>
              )}

              {(isProcessing || allCompleted) && (
                <div className="space-y-4">
                  {processingSteps.map((step, index) => (
                    <div key={step.id} className="flex items-start gap-4 p-4 rounded-lg border">
                      <div className="flex-shrink-0 mt-1">
                        {step.status === 'pending' && (
                          <div className="w-6 h-6 rounded-full border-2 border-gray-300"></div>
                        )}
                        {step.status === 'processing' && (
                          <div className="w-6 h-6 rounded-full border-2 border-blue-500 border-t-transparent animate-spin"></div>
                        )}
                        {step.status === 'completed' && (
                          <CheckCircle className="w-6 h-6 text-green-500" />
                        )}
                        {step.status === 'error' && (
                          <AlertTriangle className="w-6 h-6 text-red-500" />
                        )}
                      </div>
                      
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">{step.title}</h4>
                        <p className="text-sm text-gray-600 mb-1">{step.description}</p>
                        
                        {step.details && (
                          <p className="text-xs text-gray-500">{step.details}</p>
                        )}
                        
                        {step.duration && (
                          <p className="text-xs text-gray-400">Concluído em {step.duration}s</p>
                        )}
                      </div>
                      
                      <div className="flex-shrink-0">
                        {step.status === 'processing' && (
                          <Badge variant="outline" className="bg-blue-50 text-blue-700">
                            Processando
                          </Badge>
                        )}
                        {step.status === 'completed' && (
                          <Badge className="bg-green-100 text-green-800">
                            Concluído
                          </Badge>
                        )}
                        {step.status === 'error' && (
                          <Badge variant="destructive">
                            Erro
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Validation Issues */}
          {validationIssues.length > 0 && (
            <Card className="border-blue-400 bg-blue-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-blue-800">
                  <AlertTriangle className="h-5 w-5" />
                  Pontos de Atenção Identificados
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {validationIssues.map((issue, index) => (
                    <Alert key={index} className="border-blue-200">
                      <AlertDescription className="text-blue-800">
                        <strong>{issue.field}:</strong> {issue.issue}
                        <br />
                        <span className="text-sm">💡 {issue.suggestion}</span>
                      </AlertDescription>
                    </Alert>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Success State */}
          {allCompleted && (
            <Card className="border-green-500 bg-green-50">
              <CardContent className="p-6">
                <div className="text-center">
                  <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-green-800 mb-2">
                    Formulário USCIS Gerado com Sucesso!
                  </h3>
                  <p className="text-green-700 mb-6">
                    Sua IA assistente analisou todas as respostas, verificou consistência, 
                    traduziu para inglês jurídico e gerou o formulário oficial do USCIS.
                  </p>
                  
                  <div className="grid md:grid-cols-3 gap-4 mb-6 text-sm">
                    <div className="bg-white p-3 rounded-lg border">
                      <Shield className="h-6 w-6 text-green-500 mx-auto mb-2" />
                      <p className="font-medium">Dados Validados</p>
                      <p className="text-gray-600">100% verificados</p>
                    </div>
                    <div className="bg-white p-3 rounded-lg border">
                      <Languages className="h-6 w-6 text-blue-500 mx-auto mb-2" />
                      <p className="font-medium">Tradução Profissional</p>
                      <p className="text-gray-600">Inglês jurídico</p>
                    </div>
                    <div className="bg-white p-3 rounded-lg border">
                      <FileText className="h-6 w-6 text-purple-500 mx-auto mb-2" />
                      <p className="font-medium">Formulário Oficial</p>
                      <p className="text-gray-600">Pronto para USCIS</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Navigation */}
          <div className="flex flex-col sm:flex-row gap-4 justify-between">
            <Button
              variant="outline"
              onClick={() => navigate(`/auto-application/case/${caseId}/friendly-form`)}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Voltar para Formulário
            </Button>

            {allCompleted && (
              <Button 
                onClick={continueToUSCISForm}
                className="bg-black text-white hover:bg-gray-800 flex items-center gap-2"
              >
                Revisar e Autorizar Formulário
                <ArrowRight className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIReviewAndTranslation;