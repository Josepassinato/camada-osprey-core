import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  ArrowLeft,
  FileText,
  CheckCircle,
  Clock,
  AlertCircle,
  User,
  Calendar,
  Edit,
  Upload,
  MessageSquare
} from "lucide-react";

interface Application {
  id: string;
  visa_type: string;
  status: string;
  progress_percentage: number;
  current_step: string;
  created_at: string;
  estimated_completion?: string;
  next_steps?: string[];
  documents_required?: string[];
}

const ApplicationDetail = () => {
  const { applicationId } = useParams();
  const navigate = useNavigate();
  const [application, setApplication] = useState<Application | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (applicationId) {
      fetchApplication();
    }
  }, [applicationId]);

  const fetchApplication = async () => {
    try {
      const token = localStorage.getItem('osprey_token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/applications/${applicationId}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setApplication(data.application);
      } else if (response.status === 404) {
        setError('Aplicação não encontrada');
      } else if (response.status === 401) {
        localStorage.removeItem('osprey_token');
        localStorage.removeItem('osprey_user');
        navigate('/login');
      } else {
        setError('Erro ao carregar aplicação');
      }
    } catch (error) {
      console.error('Application detail error:', error);
      setError('Erro de conexão');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      'draft': 'bg-gray-200 text-black',
      'in_progress': 'bg-gray-200 text-black',
      'document_review': 'bg-gray-300 text-black',
      'ready_to_submit': 'bg-gray-400 text-white',
      'submitted': 'bg-gray-500 text-white',
      'approved': 'bg-black text-white',
      'denied': 'bg-gray-600 text-white',
    };
    return colors[status as keyof typeof colors] || 'bg-gray-200 text-black';
  };

  const getStatusLabel = (status: string) => {
    const labels = {
      'draft': 'Rascunho',
      'in_progress': 'Em Andamento',
      'document_review': 'Revisão de Documentos',
      'ready_to_submit': 'Pronta para Envio',
      'submitted': 'Enviada',
      'approved': 'Aprovada',
      'denied': 'Negada',
    };
    return labels[status as keyof typeof labels] || status;
  };

  const getVisaTypeLabel = (type: string) => {
    const labels = {
      'h1b': 'H1-B (Trabalho Especializado)',
      'l1': 'L1 (Transferência)',
      'o1': 'O1 (Habilidade Extraordinária)',
      'f1': 'F1 (Estudante)',
      'b1b2': 'B1/B2 (Turismo/Negócios)',
      'family': 'Reunificação Familiar',
    };
    return labels[type as keyof typeof labels] || type.toUpperCase();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Carregando aplicação...</p>
        </div>
      </div>
    );
  }

  if (error || !application) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <Card className="glass border-0 max-w-md">
          <CardContent className="text-center p-8">
            <AlertCircle className="h-12 w-12 text-gray-700 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-foreground mb-2">
              {error || 'Aplicação não encontrada'}
            </h2>
            <p className="text-muted-foreground mb-6">
              A aplicação que você está procurando não existe ou você não tem permissão para acessá-la.
            </p>
            <Button onClick={() => navigate('/applications')}>
              Voltar às Aplicações
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
                onClick={() => navigate('/applications')}
                className="p-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Aplicações
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                  <FileText className="h-8 w-8 text-black" />
                  {getVisaTypeLabel(application.visa_type)}
                </h1>
                <p className="text-muted-foreground">
                  Criada em {formatDate(application.created_at)}
                </p>
              </div>
            </div>
            <Badge className={`${getStatusColor(application.status)} border`}>
              {getStatusLabel(application.status)}
            </Badge>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Progress Overview */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle>Progresso da Aplicação</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Completude</span>
                  <span className="text-sm text-muted-foreground">
                    {application.progress_percentage}%
                  </span>
                </div>
                <Progress value={application.progress_percentage} className="h-3" />
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3 mb-2">
                      <Clock className="h-5 w-5 text-gray-700" />
                      <span className="font-medium">Etapa Atual</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {application.current_step || 'Iniciando aplicação'}
                    </p>
                  </div>
                  
                  {application.estimated_completion && (
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3 mb-2">
                        <Calendar className="h-5 w-5 text-gray-700" />
                        <span className="font-medium">Conclusão Estimada</span>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(application.estimated_completion)}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Next Steps */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle>Próximos Passos</CardTitle>
              </CardHeader>
              <CardContent>
                {application.next_steps && application.next_steps.length > 0 ? (
                  <div className="space-y-3">
                    {application.next_steps.map((step, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                        <div className="w-6 h-6 bg-black text-white rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                          {index + 1}
                        </div>
                        <p className="text-sm text-foreground">{step}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <CheckCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-muted-foreground">
                      Aguardando definição dos próximos passos...
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Documents Required */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle>Documentos Necessários</CardTitle>
              </CardHeader>
              <CardContent>
                {application.documents_required && application.documents_required.length > 0 ? (
                  <div className="space-y-2">
                    {application.documents_required.map((doc, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 border border-gray-200 rounded-lg">
                        <FileText className="h-4 w-4 text-gray-700 mt-0.5" />
                        <p className="text-sm text-foreground">{doc}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-muted-foreground">
                      Lista de documentos será gerada baseada no tipo de visto...
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Application Info */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle>Informações</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-gray-700" />
                  <span className="text-sm">ID: {application.id.substring(0, 8)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-gray-700" />
                  <span className="text-sm">Criada: {formatDate(application.created_at)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-gray-700" />
                  <span className="text-sm">Tipo: {application.visa_type.toUpperCase()}</span>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle>Ações</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  className="w-full bg-black text-white hover:bg-gray-800"
                  onClick={() => navigate('/documents/upload')}
                >
                  <Upload className="h-4 w-4" />
                  Enviar Documentos
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => navigate('/chat')}
                >
                  <MessageSquare className="h-4 w-4" />
                  Chat com IA
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => navigate('/education')}
                >
                  <FileText className="h-4 w-4" />
                  Centro Educacional
                </Button>
              </CardContent>
            </Card>

            {/* Status History (Mock) */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle>Histórico</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-3 text-sm">
                    <div className="w-2 h-2 bg-black rounded-full"></div>
                    <span className="text-muted-foreground">
                      {formatDate(application.created_at)} - Aplicação criada
                    </span>
                  </div>
                  {application.status !== 'draft' && (
                    <div className="flex items-center gap-3 text-sm">
                      <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                      <span className="text-muted-foreground">
                        Status atualizado para {getStatusLabel(application.status)}
                      </span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApplicationDetail;