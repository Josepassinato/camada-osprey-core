import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import VisaRequirements from "@/components/VisaRequirements";
import ProcessTypeSelector from "@/components/ProcessTypeSelector";
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
  const { processType, setProcessType } = useProcessType();
  const [selectedForm, setSelectedForm] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [showRequirements, setShowRequirements] = useState(false);
  const [selectedVisaType, setSelectedVisaType] = useState("");
  const [showProcessSelector, setShowProcessSelector] = useState(!processType);
  const [visaDetailsMap, setVisaDetailsMap] = useState<Record<string, any>>({});

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

  const handleProcessTypeSelect = (type: 'consular' | 'change_of_status') => {
    setProcessType(type);
    setShowProcessSelector(false);
  };

  // Load visa details when processType changes
  React.useEffect(() => {
    if (processType) {
      loadVisaDetails();
    }
  }, [processType]);

  const loadVisaDetails = async () => {
    if (!processType) return;
    
    const visaCodes = ['I-539', 'H-1B', 'F-1', 'B-1/B-2', 'I-130', 'O-1'];
    const detailsMap: Record<string, any> = {};
    
    for (const code of visaCodes) {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_BACKEND_URL}/api/visa-information/${code}?process_type=${processType}`
        );
        if (response.ok) {
          const data = await response.json();
          detailsMap[code] = data;
        }
      } catch (error) {
        console.error(`Error loading details for ${code}:`, error);
      }
    }
    
    setVisaDetailsMap(detailsMap);
  };

  const uscisforms: USCISFormType[] = [
    {
      code: 'B-1/B-2',
      title: 'B-1/B-2: Visto de Negócios e Turismo',
      description: 'Para negócios, turismo, visitas familiares, tratamento médico ou eventos sociais nos EUA',
      icon: <Plane className="h-6 w-6" />,
      category: 'Turismo/Negócios',
      processingTime: '2-4 semanas',
      uscisfee: '$185',
      complexity: 'Básico',
      eligibility: [
        'B-1: Reuniões de negócios, conferências, treinamentos',
        'B-2: Turismo, visitas familiares, tratamento médico',
        'Intenção de retornar ao Brasil',
        'Vínculos fortes com país de origem',
        'Recursos financeiros suficientes para a viagem'
      ],
      popular: true
    },
    {
      code: 'H-1B',
      title: 'H-1B: Trabalhador Especializado',
      description: 'Para profissionais com ensino superior em ocupação especializada nos EUA',
      icon: <Briefcase className="h-6 w-6" />,
      category: 'Trabalho',
      processingTime: '2-4 meses',
      uscisfee: '$555 + taxas',
      complexity: 'Avançado',
      eligibility: [
        'Diploma de ensino superior ou equivalente',
        'Oferta de trabalho em ocupação especializada',
        'Empregador americano patrocinador',
        'Qualificações específicas para a função'
      ],
      popular: true
    },
    {
      code: 'F-1',
      title: 'F-1: Visto de Estudante',
      description: 'Para estudos acadêmicos em instituições americanas aprovadas',
      icon: <GraduationCap className="h-6 w-6" />,
      category: 'Educação',
      processingTime: '2-6 semanas',
      uscisfee: '$185 + $350',
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
      code: 'O-1',
      title: 'O-1: Habilidade Extraordinária',
      description: 'Para indivíduos com habilidades extraordinárias em sua área',
      icon: <Star className="h-6 w-6" />,
      category: 'Trabalho',
      processingTime: '2-4 meses',
      uscisfee: '$555 + $1,440',
      complexity: 'Avançado',
      eligibility: [
        'Habilidade extraordinária comprovada',
        'Reconhecimento nacional/internacional',
        'Evidências de conquistas substanciais',
        'Continuação do trabalho na área'
      ]
    },
    {
      code: 'N-400',
      title: 'N-400: Pedido de Naturalização',
      description: 'Para residentes permanentes elegíveis que desejam se tornar cidadãos americanos',
      icon: <Users className="h-6 w-6" />,
      category: 'Cidadania',
      processingTime: '8-12 meses',
      uscisfee: '$725',
      complexity: 'Intermediário',
      eligibility: [
        'Residente permanente há pelo menos 5 anos (ou 3 se casado com cidadão)',
        'Fisicamente presente nos EUA pelo tempo requerido',
        'Conhecimento básico de inglês e história americana',
        'Bom caráter moral'
      ],
      popular: true
    },
    {
      code: 'I-130',
      title: 'I-130: Petição de Parente Estrangeiro',
      description: 'Para cidadãos e residentes permanentes peticionarem familiares',
      icon: <Heart className="h-6 w-6" />,
      category: 'Família',
      processingTime: '8-33 meses',
      uscisfee: '$535',
      complexity: 'Básico',
      eligibility: [
        'Ser cidadão americano ou residente permanente',
        'Comprovar relacionamento familiar elegível',
        'Cumprir requisitos de renda ou ter co-patrocinador',
        'Familiares elegíveis: cônjuge, filhos, pais, irmãos'
      ],
      popular: true
    },
    {
      code: 'I-765',
      title: 'I-765: Autorização de Trabalho',
      description: 'Para solicitar permissão de trabalho nos Estados Unidos',
      icon: <Briefcase className="h-6 w-6" />,
      category: 'Trabalho',
      processingTime: '3-5 meses',
      uscisfee: '$410',
      complexity: 'Básico',
      eligibility: [
        'Ter categoria elegível (estudante, asylum, TPS, etc.)',
        'Estar nos EUA legalmente',
        'Não ter autorização de trabalho automática',
        'Cumprir requisitos específicos da categoria'
      ],
      popular: true
    },
    {
      code: 'I-485',
      title: 'I-485: Ajuste de Status',
      description: 'Para ajustar status para residente permanente estando nos EUA',
      icon: <Home className="h-6 w-6" />,
      category: 'Green Card',
      processingTime: '8-24 meses',
      uscisfee: '$1,225',
      complexity: 'Avançado',
      eligibility: [
        'Ter petição aprovada ou ser elegível',
        'Estar fisicamente presente nos EUA',
        'Entrou legalmente nos EUA',
        'Visa disponível (se aplicável)'
      ]
    },
    {
      code: 'I-90',
      title: 'I-90: Renovação de Green Card',
      description: 'Para renovar ou substituir cartão de residente permanente',
      icon: <CreditCard className="h-6 w-6" />,
      category: 'Green Card',
      processingTime: '6-10 meses',
      uscisfee: '$540',
      complexity: 'Básico',
      eligibility: [
        'Ser residente permanente',
        'Cartão expirado, perdido, roubado ou danificado',
        'Mudança de informações (nome, gênero)',
        'Erro no cartão emitido pelo USCIS'
      ]
    },
    {
      code: 'I-751',
      title: 'I-751: Remoção de Condições',
      description: 'Para remover condições do status de residente permanente',
      icon: <FileText className="h-6 w-6" />,
      category: 'Green Card',
      processingTime: '12-18 meses',
      uscisfee: '$595',
      complexity: 'Intermediário',
      eligibility: [
        'Residente permanente condicional há quase 2 anos',
        'Baseado em casamento ou investimento',
        'Comprovar que o casamento é genuíno',
        'Arquivo dentro de 90 dias antes da expiração'
      ]
    },
    {
      code: 'I-589',
      title: 'I-589: Pedido de Asilo',
      description: 'Para pessoas que buscam proteção nos EUA devido à perseguição',
      icon: <Users className="h-6 w-6" />,
      category: 'Asilo',
      processingTime: '2-5 anos',
      uscisfee: '$0',
      complexity: 'Avançado',
      eligibility: [
        'Estar fisicamente presente nos EUA',
        'Aplicar dentro de 1 ano da chegada (salvo exceções)',
        'Demonstrar perseguição ou medo bem fundamentado',
        'Perseguição baseada em motivos protegidos',
        'Não ter cometido crimes graves'
      ]
    },
    {
      code: 'I-539',
      title: 'I-539: Extensão/Mudança de Status',
      description: 'Para estender ou mudar seu status de não-imigrante nos EUA',
      icon: <Clock className="h-6 w-6" />,
      category: 'Extensão',
      processingTime: '4-8 meses',
      uscisfee: '$370',
      complexity: 'Intermediário',
      eligibility: [
        'Estar legalmente nos EUA com status válido',
        'Não ter violado termos do status atual',
        'Aplicar antes do vencimento do status atual',
        'Ter motivo válido para extensão',
        'Comprovar recursos financeiros suficientes'
      ],
      popular: true
    }
  ];

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
            navigate(`/auto-application/case/${existingCaseId}/basic-data`);
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
          navigate(`/auto-application/case/${data.case.case_id}/basic-data`);
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

  return (
    <>
      {/* Show Process Type Selector first */}
      {showProcessSelector && (
        <ProcessTypeSelector onSelect={handleProcessTypeSelect} />
      )}

      {/* Show Form Selection after process type is chosen */}
      {!showProcessSelector && (
        <div className="min-h-screen bg-white">
      {/* Header - Mobile Optimized */}
      <div className="bg-white border-b border-black">
        <div className="px-4 py-4 sm:py-6">
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
                Selecione o tipo de formulário USCIS
              </p>
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
          {uscisforms.map((form) => (
            <div 
              key={form.code}
              className={`bg-white border-2 rounded-lg p-4 sm:p-6 cursor-pointer transition-all hover:shadow-lg ${
                selectedForm === form.code ? 'border-black shadow-lg' : 'border-gray-200'
              }`}
              onClick={() => setSelectedForm(form.code)}
            >
              {form.popular && (
                <div className="inline-block bg-black text-white text-xs px-2 py-1 rounded-full mb-3">
                  Popular
                </div>
              )}
              
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-black text-white rounded-lg flex items-center justify-center">
                    {form.icon}
                  </div>
                </div>
                <div className="bg-white border border-black px-2 py-1 rounded-full text-xs text-black">
                  {form.complexity}
                </div>
              </div>
              
              <h3 className="text-base sm:text-lg font-bold text-black mb-2">{form.title}</h3>
              
              <p className="text-xs sm:text-sm text-black mb-4 leading-tight">
                {form.description}
              </p>

              <div className="mb-3">
                <span className="inline-block bg-black text-white text-xs px-2 py-1 rounded">
                  {form.category}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs sm:text-sm mb-4">
                <div>
                  <div className="flex items-center gap-1 text-black mb-1">
                    <Clock className="h-3 w-3" />
                    <span>Prazo</span>
                  </div>
                  <div className="font-medium text-black">{form.processingTime}</div>
                </div>
                <div>
                  <div className="flex items-center gap-1 text-black mb-1">
                    <DollarSign className="h-3 w-3" />
                    <span>Taxa USCIS</span>
                  </div>
                  <div className="font-medium text-black">{form.uscisfee}</div>
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
                <Button 
                  className={`text-xs ${
                    selectedForm === form.code 
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
              </div>
            </div>
          ))}
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
      )}
    </>
  );
};

export default SelectForm;