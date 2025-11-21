import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import VisaRequirements from "@/components/VisaRequirements";
import { useProcessType } from "@/contexts/ProcessTypeContext";
import { 
  ArrowLeft,
  ArrowRight,
  FileText,
  Clock,
  DollarSign,
  AlertTriangle,
  Users,
  GraduationCap,
  Heart,
  Briefcase,
  Home,
  CreditCard,
  Building,
  Star,
  CheckCircle,
  Plane,
  Shield,
  Info
} from "lucide-react";

interface USCISFormType {
  code: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  category: string;
  processingTime: string;
  uscisfee: string;
  eligibility: string[];
  popular?: boolean;
  complexity: 'Básico' | 'Intermediário' | 'Avançado';
}

const SelectForm = () => {
  const navigate = useNavigate();
  const { processType, setProcessType, clearProcessType } = useProcessType();
  const [selectedForm, setSelectedForm] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [showRequirements, setShowRequirements] = useState(false);
  const [selectedVisaType, setSelectedVisaType] = useState("");
  const [visaDetailsMap, setVisaDetailsMap] = useState<Record<string, any>>({});

  // Set process type to always be "change_of_status" (application is only for people already in USA)
  React.useEffect(() => {
    setProcessType('change_of_status');
  }, []);

  // Listen for start application event from VisaRequirements component
  React.useEffect(() => {
    const handleStartApplication = (event: CustomEvent) => {
      const { visaType } = event.detail;
      setShowRequirements(false);
      createCase(visaType);
    };

    window.addEventListener('startApplication', handleStartApplication as EventListener);
    return () => window.removeEventListener('startApplication', handleStartApplication as EventListener);
  }, []);

  // Load visa details for change of status
  React.useEffect(() => {
    loadVisaDetails();
  }, []);

  const loadVisaDetails = async () => {
    // Load visas for LAUNCH - 7 vistos + 1 sob consulta
    const visaCodes = ['I-539', 'F-1', 'I-130', 'I-765', 'I-90', 'EB-2 NIW', 'EB-1A', 'I-589'];
    
    const detailsMap: Record<string, any> = {};
    
    for (const code of visaCodes) {
      try {
        const encodedCode = encodeURIComponent(code);
        const response = await fetch(
          `${import.meta.env.VITE_BACKEND_URL}/api/visa-detailed-info/${encodedCode}?process_type=change_of_status`
        );
        if (response.ok) {
          const data = await response.json();
          detailsMap[code] = data.information;
        }
      } catch (error) {
        console.error(`Error loading details for ${code}:`, error);
      }
    }
    
    setVisaDetailsMap(detailsMap);
  };

  // Define all available forms (for people already in USA - change of status only)
  // LANÇAMENTO: 7 vistos para venda + 1 sob consulta
  const uscisforms: USCISFormType[] = [
    {
      code: 'I-539',
      title: 'I-539: Extensão de Turista',
      description: 'Para estender sua permanência como turista (B-1/B-2) nos Estados Unidos',
      icon: <Plane className="h-6 w-6" />,
      category: 'Turismo',
      processingTime: '6-10 meses',
      uscisfee: '$370 + $85',
      complexity: 'Básico',
      eligibility: [
        'Atualmente nos EUA com visto de turista válido',
        'Razão válida para extensão',
        'Meios financeiros suficientes',
        'Não trabalhar durante extensão'
      ],
      popular: true
    },
    {
      code: 'F-1',
      title: 'F-1: Visto de Estudante',
      description: 'Para estudos acadêmicos em instituições americanas aprovadas',
      icon: <GraduationCap className="h-6 w-6" />,
      category: 'Educação',
      processingTime: '3-5 meses',
      uscisfee: '$370 + $350',
      complexity: 'Intermediário',
      eligibility: [
        'Aceito em instituição aprovada pelo SEVP',
        'Programa acadêmico ou de idiomas',
        'Recursos financeiros para estudos',
        'Intenção de retornar após estudos'
      ],
      popular: true
    },
    {
      code: 'I-130',
      title: 'I-130: Petição para Familiar (Casamento)',
      description: 'Para petição de cônjuge ou familiar imediato para Green Card',
      icon: <Heart className="h-6 w-6" />,
      category: 'Família',
      processingTime: '10-24 meses',
      uscisfee: '$535',
      complexity: 'Intermediário',
      eligibility: [
        'Peticionário cidadão americano ou residente permanente',
        'Relação familiar qualificante (cônjuge, filho, pai/mãe)',
        'Evidências de relacionamento genuíno',
        'Capacidade financeira do peticionário'
      ],
      popular: true
    },
    {
      code: 'I-765',
      title: 'I-765: Autorização de Trabalho (EAD)',
      description: 'Para obter autorização de trabalho nos Estados Unidos',
      icon: <Briefcase className="h-6 w-6" />,
      category: 'Trabalho',
      processingTime: '3-8 meses',
      uscisfee: '$410 + $85',
      complexity: 'Básico',
      eligibility: [
        'Status elegível para EAD (asylum, OPT, ajuste de status, etc)',
        'Documentação do status atual',
        'Formulário I-94 válido',
        'Motivo válido para autorização de trabalho'
      ]
    },
    {
      code: 'I-90',
      title: 'I-90: Renovação de Green Card',
      description: 'Para renovar ou substituir seu Green Card',
      icon: <CreditCard className="h-6 w-6" />,
      category: 'Green Card',
      processingTime: '8-12 meses',
      uscisfee: '$455 + $85',
      complexity: 'Básico',
      eligibility: [
        'Green Card expirado ou expirando em 6 meses',
        'Green Card perdido, roubado ou danificado',
        'Mudança de nome ou informações',
        'Green Card emitido antes dos 14 anos (para atualizar)'
      ]
    },
    {
      code: 'EB-2 NIW',
      title: 'EB-2 NIW: Green Card por Interesse Nacional',
      description: 'Para profissionais altamente qualificados com mestrado ou superior',
      icon: <Star className="h-6 w-6" />,
      category: 'Green Card Premium',
      processingTime: '12-18 meses',
      uscisfee: '$700 + $85',
      complexity: 'Avançado',
      eligibility: [
        'Mestrado ou superior (ou bacharelado + 5 anos de experiência)',
        'Trabalho de interesse substancial para os EUA',
        'Evidências de contribuições significativas',
        'Dispensar oferta de emprego e certificação trabalhista'
      ],
      popular: true
    },
    {
      code: 'EB-1A',
      title: 'EB-1A: Habilidade Extraordinária',
      description: 'Para pessoas com habilidade extraordinária reconhecida nacionalmente/internacionalmente',
      icon: <Star className="h-6 w-6" />,
      category: 'Green Card Premium',
      processingTime: '8-12 meses',
      uscisfee: '$700 + $85',
      complexity: 'Avançado',
      eligibility: [
        'Reconhecimento nacional ou internacional',
        'Atender 3 de 10 critérios EB-1A',
        'Prêmios, publicações, contribuições importantes',
        'Não necessita patrocinador ou oferta de emprego'
      ],
      popular: true
    },
    {
      code: 'I-589',
      title: 'I-589: Pedido de Asilo',
      description: 'SOB CONSULTA - Caso complexo que requer avaliação individual',
      icon: <Shield className="h-6 w-6" />,
      category: 'Proteção',
      processingTime: '2-7 anos',
      uscisfee: '$0 (Gratuito)',
      complexity: 'Especial',
      eligibility: [
        'Perseguição ou medo fundamentado de perseguição',
        'Baseado em raça, religião, nacionalidade, opinião política ou grupo social',
        'Aplicar dentro de 1 ano da chegada aos EUA',
        'Evidências de perseguição no país de origem'
      ]
    }
    
    /* 
    ============================================================
    VISTOS DESATIVADOS - Comentados abaixo
    Serão reativados após lançamento inicial
    ============================================================
    
    Demais vistos: H-1B, O-1, N-400, I-485, I-751
    FIM DOS VISTOS DESATIVADOS 
    ============================================================
    */
  ];

  // Forms are already filtered for change of status (no B-1/B-2)

  const createStripeCheckout = async (visaCode: string, caseId: string) => {
    try {
      console.log('💳 Creating Stripe checkout session...');
      
      const backendUrl = import.meta.env.VITE_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/payment/create-checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          visa_code: visaCode,
          case_id: caseId
        }),
      });

      const data = await response.json();
      
      if (data.success && data.checkout_url) {
        console.log('✅ Stripe checkout created, redirecting...');
        // Redirect to Stripe Checkout
        window.location.href = data.checkout_url;
      } else {
        throw new Error(data.error || 'Erro ao criar sessão de pagamento');
      }
    } catch (error: any) {
      console.error('❌ Erro ao criar checkout Stripe:', error);
      setError(error.message || 'Erro ao processar pagamento. Tente novamente.');
      setIsLoading(false);
    }
  };

  const createCase = async (formCode: string) => {
    setIsLoading(true);
    setError("");

    try {
      const sessionToken = localStorage.getItem('osprey_session_token');
      
      // Check if we have an existing case ID from the start flow
      const existingCaseId = localStorage.getItem('osprey_current_case_id');
      
      if (existingCaseId) {
        // Update existing case with form_code and process_type
        console.log('🔄 Updating existing case with form_code:', formCode, 'and process_type:', processType);
        console.log('🔄 Session token:', sessionToken);
        console.log('🔄 Existing case ID:', existingCaseId);
        
        const updateResponse = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${existingCaseId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            form_code: formCode,
            process_type: processType,
            session_token: sessionToken
          }),
        });
        
        if (updateResponse.ok) {
          const updateData = await updateResponse.json();
          console.log('✅ Case updated successfully:', updateData);
          
          // Verify the update was successful
          if (updateData.case && updateData.case.form_code === formCode) {
            // Create Stripe checkout session and redirect directly
            await createStripeCheckout(formCode, existingCaseId);
            return;
          } else {
            console.log('⚠️ Form code mismatch after update, creating new case');
          }
        } else {
          console.log('❌ Failed to update case, creating new one');
        }
      }
      
      // Create new case with form_code and process_type
      console.log('🆕 Creating new case with form_code:', formCode, 'and process_type:', processType);
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          form_code: formCode,
          process_type: processType,
          session_token: sessionToken
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ New case created:', data);
        
        // Verify form_code was set correctly
        if (data.case && data.case.form_code === formCode) {
          console.log('✅ Form code verified:', data.case.form_code);
          // Store case ID for anonymous access
          localStorage.setItem('osprey_current_case_id', data.case.case_id);
          // Create Stripe checkout session and redirect directly
          await createStripeCheckout(formCode, data.case.case_id);
        } else {
          console.error('❌ Form code mismatch!', {
            expected: formCode,
            actual: data.case?.form_code,
            fullResponse: data
          });
          setError(`Erro: form_code incorreto (esperado: ${formCode}, recebido: ${data.case?.form_code})`);
        }
      } else {
        setError('Erro ao criar caso. Tente novamente.');
      }
    } catch (error) {
      console.error('Create case error:', error);
      setError('Erro de conexão. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  const getComplexityColor = (complexity: string) => {
    const colors = {
      'Básico': 'bg-gray-100 text-gray-800 border-gray-200',
      'Intermediário': 'bg-gray-200 text-gray-900 border-gray-300',
      'Avançado': 'bg-gray-300 text-black border-gray-400',
    };
    return colors[complexity as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getCategoryIcon = (category: string) => {
    const icons = {
      'Cidadania': '🇺🇸',
      'Família': '👨‍👩‍👧‍👦',
      'Trabalho': '💼',
      'Green Card': '🏠',
    };
    return icons[category as keyof typeof icons] || '📄';
  };

  // Get visa details for change of status
  const getVisaDetails = (formCode: string) => {
    const details = visaDetailsMap[formCode];
    if (!details) return null;
    
    const processDetails = details.change_of_status;
    if (!processDetails) return null;
    
    return {
      processingTime: processDetails.tempo_processamento || 'Consulte USCIS',
      fee: processDetails.taxas?.total || 'Varia',
      requirements: details.criterios_elegibilidade || []
    };
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header - Mobile Optimized */}
      <div className="bg-white border-b border-black">
        <div className="px-4 py-4 sm:py-6">
          <div className="flex items-center justify-between gap-3 sm:gap-4">
            <div className="flex items-center gap-3 sm:gap-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/auto-application/start')}
                className="p-2 hover:bg-gray-100"
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <div>
                <h1 className="text-lg sm:text-2xl font-bold text-black">
                  Escolha seu Formulário
                </h1>
                <p className="text-sm text-black hidden sm:block">
                  Mudança de Status - Para pessoas já nos Estados Unidos
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="px-4 py-6 sm:px-6 sm:py-8">
        {error && (
          <div className="bg-white border border-black rounded-lg mb-6 p-4">
            <div className="flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 text-black" />
              <p className="text-black text-sm">{error}</p>
            </div>
          </div>
        )}

        <div className="grid gap-4 sm:gap-6 sm:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto">
          {uscisforms.map((form) => {
            // Identificar vistos premium
            const isPremium = ['EB-2 NIW', 'EB-1A', 'I-765'].includes(form.code);
            const premiumColors = isPremium 
              ? 'bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-300 hover:border-purple-500' 
              : 'bg-white border-gray-200';
            const selectedColors = selectedForm === form.code 
              ? 'border-purple-600 shadow-2xl shadow-purple-200' 
              : '';
            
            return (
            <div 
              key={form.code}
              className={`border-2 rounded-lg p-4 sm:p-6 cursor-pointer transition-all hover:shadow-lg ${
                isPremium ? premiumColors : 'bg-white'
              } ${selectedColors || (isPremium ? '' : selectedForm === form.code ? 'border-black shadow-lg' : 'border-gray-200')}`}
              onClick={() => setSelectedForm(form.code)}
            >
              {isPremium && (
                <div className="inline-block bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-xs px-3 py-1 rounded-full mb-3 font-semibold shadow-md">
                  ⭐ Premium
                </div>
              )}
              {form.popular && !isPremium && (
                <div className="inline-block bg-black text-white text-xs px-2 py-1 rounded-full mb-3">
                  Popular
                </div>
              )}
              
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-lg flex items-center justify-center ${
                    isPremium 
                      ? 'bg-gradient-to-br from-purple-600 to-indigo-600 shadow-lg shadow-purple-300' 
                      : 'bg-black'
                  } text-white`}>
                    {form.icon}
                  </div>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs ${
                  isPremium 
                    ? 'bg-purple-600 text-white font-semibold' 
                    : 'bg-white border border-black text-black'
                }`}>
                  {form.complexity}
                </div>
              </div>
              
              <h3 className="text-base sm:text-lg font-bold text-black mb-2">{form.title}</h3>
              
              <p className="text-xs sm:text-sm text-black mb-4 leading-tight">
                {form.description}
              </p>

              <div className="mb-3">
                <span className={`inline-block text-xs px-2 py-1 rounded font-medium ${
                  isPremium 
                    ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white' 
                    : 'bg-black text-white'
                }`}>
                  {form.category}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs sm:text-sm mb-4">
                <div>
                  <div className="flex items-center gap-1 text-black mb-1">
                    <Clock className="h-3 w-3" />
                    <span>Prazo</span>
                  </div>
                  <div className="font-medium text-black">
                    {getVisaDetails(form.code)?.processingTime || form.processingTime}
                  </div>
                </div>
                <div>
                  <div className="flex items-center gap-1 text-black mb-1">
                    <DollarSign className="h-3 w-3" />
                    <span>Taxa USCIS</span>
                  </div>
                  <div className="font-medium text-black">
                    {getVisaDetails(form.code)?.fee || form.uscisfee}
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-xs sm:text-sm text-black mb-2">Principais requisitos:</h4>
                <ul className="space-y-1">
                  {form.eligibility.slice(0, 2).map((req, index) => (
                    <li key={index} className="text-xs text-black flex items-start gap-2">
                      <CheckCircle className="h-3 w-3 text-black flex-shrink-0 mt-0.5" />
                      <span className="leading-tight">{req}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="grid grid-cols-2 gap-2 mt-4">
                <Button 
                  variant="outline"
                  className="text-xs border-black text-black hover:bg-gray-50"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedVisaType(form.code);
                    setShowRequirements(true);
                  }}
                >
                  <Info className="h-3 w-3 mr-1" />
                  Ver Detalhes
                </Button>
                {form.code === 'I-589' ? (
                  <Button 
                    className="text-xs bg-black text-white hover:bg-gray-800"
                    onClick={(e) => {
                      e.stopPropagation();
                      window.location.href = 'mailto:contato@agentecorujalaw.com?subject=Consulta sobre Asilo (I-589)&body=Olá, gostaria de mais informações sobre o processo de asilo (I-589).';
                    }}
                  >
                    Solicitar Consulta
                  </Button>
                ) : (
                  <Button 
                    className={`text-xs ${
                      isPremium
                        ? selectedForm === form.code
                          ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 shadow-lg'
                          : 'bg-white border-2 border-purple-600 text-purple-600 hover:bg-purple-50'
                        : selectedForm === form.code 
                          ? 'bg-black text-white hover:bg-gray-800' 
                          : 'bg-white border border-black text-black hover:bg-gray-50'
                    }`}
                    onClick={(e) => {
                      e.stopPropagation();
                      createCase(form.code);
                    }}
                    disabled={isLoading && selectedForm === form.code}
                  >
                    {isLoading && selectedForm === form.code ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <>
                        Começar
                        <ArrowRight className="h-3 w-3 ml-1" />
                      </>
                    )}
                  </Button>
                )}
              </div>
            </div>
            );
          })}
        </div>

        {/* Info Section */}
        <Card className="glass border-0 mt-8">
          <CardHeader>
            <CardTitle>Informações Importantes</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-gray-700" />
                  Antes de Começar
                </h4>
                <ul className="space-y-1 text-sm text-gray-900">
                  <li>• Verifique se você atende aos requisitos básicos</li>
                  <li>• Tenha todos os documentos necessários em mãos</li>
                  <li>• O processo pode levar várias sessões para ser concluído</li>
                  <li>• Suas informações são salvas automaticamente</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <FileText className="h-4 w-4 text-gray-700" />
                  O Que Você Receberá para Sua Auto-Aplicação
                </h4>
                <ul className="space-y-1 text-sm text-gray-900">
                  <li>• Formulário oficial organizado com suas informações</li>
                  <li>• Checklist de documentos personalizada</li>
                  <li>• Instruções detalhadas para sua auto-aplicação</li>
                  <li>• Carta com informações sobre taxas do USCIS</li>
                  <li>• Você revisa tudo e faz sua própria aplicação</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Visa Requirements Dialog */}
      <Dialog open={showRequirements} onOpenChange={setShowRequirements}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Requisitos Detalhados do Visto</DialogTitle>
          </DialogHeader>
          {selectedVisaType && (
            <VisaRequirements 
              visaType={selectedVisaType} 
              onClose={() => setShowRequirements(false)} 
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default SelectForm;