import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  ArrowLeft,
  FileText,
  CheckCircle,
  ArrowRight,
  Clock,
  DollarSign,
  Users,
  GraduationCap
} from "lucide-react";

interface VisaType {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  difficulty: string;
  timeframe: string;
  cost: string;
  requirements: string[];
  popular?: boolean;
}

const NewApplication = () => {
  const navigate = useNavigate();
  const [selectedVisa, setSelectedVisa] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const visaTypes: VisaType[] = [
    {
      id: 'h1b',
      title: 'H1-B (Trabalho Especializado)',
      description: 'Para profissionais especializados com oferta de emprego nos EUA',
      icon: <FileText className="h-6 w-6" />,
      difficulty: 'Intermediário',
      timeframe: '3-6 meses',
      cost: '$1,500+',
      requirements: ['Diploma universitário', 'Oferta de emprego', 'Especialização na área'],
      popular: true
    },
    {
      id: 'f1',
      title: 'F1 (Estudante)',
      description: 'Para estudantes internacionais matriculados em instituições americanas',
      icon: <GraduationCap className="h-6 w-6" />,
      difficulty: 'Iniciante',
      timeframe: '2-4 meses',
      cost: '$350+',
      requirements: ['Aceitação em instituição', 'Comprovante financeiro', 'Vínculos com país de origem'],
      popular: true
    },
    {
      id: 'family',
      title: 'Reunificação Familiar',
      description: 'Para familiares de cidadãos ou residentes permanentes dos EUA',
      icon: <Users className="h-6 w-6" />,
      difficulty: 'Intermediário',
      timeframe: '6-18 meses',
      cost: '$1,200+',
      requirements: ['Parentesco comprovado', 'Petição aprovada', 'Documentos familiares'],
      popular: false
    },
    {
      id: 'b1b2',
      title: 'B1/B2 (Turismo/Negócios)',
      description: 'Para viagens temporárias de turismo ou negócios',
      icon: <CheckCircle className="h-6 w-6" />,
      difficulty: 'Iniciante',
      timeframe: '2-4 semanas',
      cost: '$160+',
      requirements: ['Vínculos com país de origem', 'Recursos financeiros', 'Propósito da viagem'],
      popular: true
    },
    {
      id: 'l1',
      title: 'L1 (Transferência Interna)',
      description: 'Para executivos transferidos por empresas multinacionais',
      icon: <DollarSign className="h-6 w-6" />,
      difficulty: 'Avançado',
      timeframe: '2-4 meses',
      cost: '$1,500+',
      requirements: ['Experiência na empresa', 'Cargo executivo/especializado', 'Relação entre empresas'],
      popular: false
    },
    {
      id: 'o1',
      title: 'O1 (Habilidade Extraordinária)',
      description: 'Para indivíduos com habilidades extraordinárias em sua área',
      icon: <CheckCircle className="h-6 w-6" />,
      difficulty: 'Avançado',
      timeframe: '3-6 meses',
      cost: '$2,000+',
      requirements: ['Prêmios/reconhecimentos', 'Publicações/mídia', 'Cartas de recomendação'],
      popular: false
    }
  ];

  const createApplication = async (visaType: string) => {
    setIsLoading(true);
    setError("");

    try {
      const token = localStorage.getItem('osprey_token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/applications`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          visa_type: visaType,
          status: 'draft'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        navigate(`/applications/${data.application.id}`);
      } else {
        setError('Erro ao criar aplicação. Tente novamente.');
      }
    } catch (error) {
      console.error('Create application error:', error);
      setError('Erro de conexão. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  const getDifficultyColor = (level: string) => {
    const colors = {
      'Iniciante': 'bg-gray-100 text-gray-800 border-gray-200',
      'Intermediário': 'bg-gray-200 text-gray-900 border-gray-300',
      'Avançado': 'bg-gray-300 text-black border-gray-400',
    };
    return colors[level as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="glass border-b border-white/20">
        <div className="container-responsive py-6">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/applications')}
              className="p-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Voltar
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                <FileText className="h-8 w-8 text-black" />
                Nova Aplicação
              </h1>
              <p className="text-muted-foreground">
                Escolha o tipo de visto para iniciar sua aplicação
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        {error && (
          <Card className="glass border-0 mb-6 border-l-4 border-l-gray-600">
            <CardContent className="p-4">
              <p className="text-foreground">{error}</p>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {visaTypes.map((visa) => (
            <Card 
              key={visa.id}
              className={`glass border-0 card-hover cursor-pointer relative ${
                selectedVisa === visa.id ? 'ring-2 ring-black' : ''
              }`}
              onClick={() => setSelectedVisa(visa.id)}
            >
              {visa.popular && (
                <div className="absolute -top-2 -right-2 bg-black text-white text-xs px-2 py-1 rounded-full">
                  Popular
                </div>
              )}
              
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-gray-700">
                    {visa.icon}
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs border ${getDifficultyColor(visa.difficulty)}`}>
                    {visa.difficulty}
                  </div>
                </div>
                <CardTitle className="text-lg">{visa.title}</CardTitle>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  {visa.description}
                </p>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      <span>Prazo</span>
                    </div>
                    <div className="font-medium">{visa.timeframe}</div>
                  </div>
                  <div>
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <DollarSign className="h-3 w-3" />
                      <span>Custo</span>
                    </div>
                    <div className="font-medium">{visa.cost}</div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-sm mb-2">Principais requisitos:</h4>
                  <ul className="space-y-1">
                    {visa.requirements.map((req, index) => (
                      <li key={index} className="text-xs text-muted-foreground flex items-start gap-1">
                        <div className="w-1 h-1 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                        {req}
                      </li>
                    ))}
                  </ul>
                </div>

                <Button 
                  className={`w-full ${
                    selectedVisa === visa.id 
                      ? 'bg-black text-white hover:bg-gray-800' 
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  onClick={(e) => {
                    e.stopPropagation();
                    createApplication(visa.id);
                  }}
                  disabled={isLoading}
                >
                  {isLoading && selectedVisa === visa.id ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <>
                      Iniciar Aplicação
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Information Section */}
        <Card className="glass border-0 mt-8">
          <CardHeader>
            <CardTitle>Informações Importantes</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-2">📋 O que você receberá:</h4>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  <li>• Guia passo a passo personalizado</li>
                  <li>• Lista de documentos necessários</li>
                  <li>• Acompanhamento do progresso</li>
                  <li>• Suporte de IA especializado</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2">⚖️ Aviso Legal:</h4>
                <p className="text-sm text-muted-foreground">
                  Este serviço oferece orientação educacional para auto-aplicação. 
                  Para questões complexas ou representação legal, consulte sempre um advogado especializado.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default NewApplication;