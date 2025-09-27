import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
  CreditCard
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
    }
  ];

  const createCase = async (formCode: string) => {
    setIsLoading(true);
    setError("");

    try {
      const token = localStorage.getItem('osprey_token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          form_code: formCode
        }),
      });

      if (response.ok) {
        const data = await response.json();
        navigate(`/auto-application/case/${data.case.case_id}/basic-data`);
      } else if (response.status === 400) {
        setError('Você precisa aceitar o aviso legal primeiro.');
        navigate('/auto-application/start');
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
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="glass border-b border-white/20">
        <div className="container-responsive py-6">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/auto-application/start')}
              className="p-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Voltar
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                <FileText className="h-8 w-8 text-black" />
                Escolha o Formulário USCIS
              </h1>
              <p className="text-muted-foreground">
                Selecione o tipo de formulário apropriado para sua situação
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        {error && (
          <Card className="glass border-0 mb-6 border-l-4 border-l-gray-600">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-6 w-6 text-gray-700" />
                <p className="text-foreground">{error}</p>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {uscisforms.map((form) => (
            <Card 
              key={form.code}
              className={`glass border-0 card-hover cursor-pointer relative ${
                selectedForm === form.code ? 'ring-2 ring-black' : ''
              }`}
              onClick={() => setSelectedForm(form.code)}
            >
              {form.popular && (
                <div className="absolute -top-2 -right-2 bg-black text-white text-xs px-2 py-1 rounded-full">
                  Popular
                </div>
              )}
              
              <CardHeader>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-gray-700">
                      {form.icon}
                    </div>
                    <div className="text-2xl">
                      {getCategoryIcon(form.category)}
                    </div>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs border ${getComplexityColor(form.complexity)}`}>
                    {form.complexity}
                  </div>
                </div>
                <CardTitle className="text-lg">{form.title}</CardTitle>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  {form.description}
                </p>

                <div className="space-y-2">
                  <Badge className="bg-gray-100 text-gray-700 border-gray-200">
                    {form.category}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      <span>Prazo</span>
                    </div>
                    <div className="font-medium">{form.processingTime}</div>
                  </div>
                  <div>
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <DollarSign className="h-3 w-3" />
                      <span>Taxa USCIS</span>
                    </div>
                    <div className="font-medium">{form.uscisfee}</div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-sm mb-2">Principais requisitos:</h4>
                  <ul className="space-y-1">
                    {form.eligibility.slice(0, 2).map((req, index) => (
                      <li key={index} className="text-xs text-muted-foreground flex items-start gap-1">
                        <div className="w-1 h-1 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                        {req}
                      </li>
                    ))}
                    {form.eligibility.length > 2 && (
                      <li className="text-xs text-muted-foreground">
                        ... e mais {form.eligibility.length - 2} requisitos
                      </li>
                    )}
                  </ul>
                </div>

                <Button 
                  className={`w-full ${
                    selectedForm === form.code 
                      ? 'bg-black text-white hover:bg-gray-800' 
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
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
              </CardContent>
            </Card>
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
                  O Que Você Receberá
                </h4>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  <li>• Formulário oficial preenchido em inglês</li>
                  <li>• Checklist de documentos personalizada</li>
                  <li>• Instruções detalhadas para envio</li>
                  <li>• Carta com informações de pagamento ao USCIS</li>
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