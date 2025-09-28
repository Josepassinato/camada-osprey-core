import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
  Plane
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
  const [selectedForm, setSelectedForm] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const uscisforms: USCISFormType[] = [
    {
      code: 'B-1/B-2',
      title: 'B-1/B-2: Visto de Negócios e Turismo',
      description: 'Para negócios, turismo, visitas familiares, tratamento médico ou eventos sociais nos EUA',
      icon: <Plane className="h-6 w-6" />,
      category: 'Turismo/Negócios',
      processingTime: '2-4 semanas',
      uscisfee: '$120',
      complexity: 'Básico',
      eligibility: [
        'Reuniões de negócios, turismo, visitas familiares',
        'Intenção de retornar ao Brasil',
        'Recursos financeiros para a viagem'
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
      code: 'L-1',
      title: 'L-1: Transferência Intracompanhia',
      description: 'Para executivos, gerentes ou especialistas transferidos entre empresas relacionadas',
      icon: <Building className="h-6 w-6" />,
      category: 'Trabalho',
      processingTime: '2-4 meses',
      uscisfee: '$555 + taxas',
      complexity: 'Avançado',
      eligibility: [
        '1 ano trabalhando na empresa no exterior',
        'Função executiva, gerencial ou especializada',
        'Empresa americana relacionada à estrangeira',
        'Transferência para posição similar'
      ]
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
      ],
      popular: false
    },
    {
      code: 'O-1',
      title: 'O-1: Habilidade Extraordinária',
      description: 'Para indivíduos com habilidades extraordinárias em sua área',
      icon: <GraduationCap className="h-6 w-6" />,
      category: 'Trabalho Especializado',
      processingTime: '2-4 meses',
      uscisfee: '$460',
      complexity: 'Avançado',
      eligibility: [
        'Habilidade extraordinária comprovada',
        'Reconhecimento nacional ou internacional',
        'Oferta de emprego ou contrato nos EUA',
        'Carta de consulta de organização apropriada'
      ],
      popular: false
    },
    {
      code: 'H-1B',
      title: 'H-1B: Trabalho Especializado',
      description: 'Para profissionais especializados com oferta de emprego',
      icon: <Briefcase className="h-6 w-6" />,
      category: 'Trabalho',
      processingTime: '3-8 meses',
      uscisfee: '$460+',
      complexity: 'Intermediário',
      eligibility: [
        'Diploma de bacharel ou equivalente',
        'Oferta de emprego em specialty occupation',
        'LCA (Labor Condition Application) aprovada',
        'Salário no nível prevalente da área'
      ],
      popular: true
    }
  ];

  const createCase = async (formCode: string) => {
    setIsLoading(true);
    setError("");

    try {
      const sessionToken = localStorage.getItem('osprey_session_token');
      
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          form_code: formCode,
          session_token: sessionToken
        }),
      });

      if (response.ok) {
        const data = await response.json();
        // Store case ID for anonymous access
        localStorage.setItem('osprey_current_case_id', data.case.case_id);
        navigate(`/auto-application/case/${data.case.case_id}/basic-data`);
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

              <Button 
                className={`w-full mt-4 ${
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
                    Começar {form.code}
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </Button>
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
                <ul className="space-y-1 text-sm text-muted-foreground">
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
                <ul className="space-y-1 text-sm text-muted-foreground">
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
    </div>
  );
};

export default SelectForm;