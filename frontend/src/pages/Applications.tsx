import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  ArrowLeft,
  Plus,
  FileText,
  Clock,
  CheckCircle,
  AlertCircle,
  Calendar,
  ArrowRight
} from "lucide-react";

interface Application {
  id: string;
  visa_type: string;
  status: string;
  progress_percentage: number;
  current_step: string;
  created_at: string;
  estimated_completion?: string;
}

const Applications = () => {
  const navigate = useNavigate();
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      const token = localStorage.getItem('osprey_token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/applications`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setApplications(data.applications || []);
      } else if (response.status === 401) {
        localStorage.removeItem('osprey_token');
        localStorage.removeItem('osprey_user');
        navigate('/login');
      } else {
        setError('Erro ao carregar aplicações');
      }
    } catch (error) {
      console.error('Applications error:', error);
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
      'h1b': 'H1-B (Trabalho)',
      'l1': 'L1 (Transferência)',
      'o1': 'O1 (Habilidade Extraordinária)',
      'eb5': 'EB-5 (Investidor)',
      'f1': 'F1 (Estudante)',
      'b1b2': 'B1/B2 (Turismo/Negócios)',
      'green_card': 'Green Card',
      'family': 'Reunificação Familiar',
    };
    return labels[type as keyof typeof labels] || type.toUpperCase();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Carregando aplicações...</p>
        </div>
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
                onClick={() => navigate('/dashboard')}
                className="p-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Dashboard
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                  <FileText className="h-8 w-8 text-black" />
                  Minhas Aplicações
                </h1>
                <p className="text-muted-foreground">
                  Acompanhe o progresso das suas aplicações de visto
                </p>
              </div>
            </div>
            <Button 
              className="bg-black text-white hover:bg-gray-800"
              onClick={() => navigate('/applications/new')}
            >
              <Plus className="h-4 w-4" />
              Nova Aplicação
            </Button>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        {error && (
          <Card className="glass border-0 mb-6 border-l-4 border-l-gray-600">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <AlertCircle className="h-6 w-6 text-gray-700" />
                <p className="text-foreground">{error}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {applications.length === 0 ? (
          <Card className="glass border-0">
            <CardContent className="text-center py-12">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <FileText className="h-8 w-8 text-gray-700" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">
                Nenhuma aplicação encontrada
              </h3>
              <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                Você ainda não iniciou nenhuma aplicação de visto. Comece sua jornada imigratória criando sua primeira aplicação.
              </p>
              <Button 
                className="bg-black text-white hover:bg-gray-800"
                onClick={() => navigate('/applications/new')}
              >
                <Plus className="h-4 w-4" />
                Criar Primeira Aplicação
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6">
            {applications.map((application) => (
              <Card 
                key={application.id} 
                className="glass border-0 card-hover cursor-pointer"
                onClick={() => navigate(`/applications/${application.id}`)}
              >
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                        <FileText className="h-6 w-6 text-gray-700" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-foreground mb-1">
                          {getVisaTypeLabel(application.visa_type)}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          Criada em {formatDate(application.created_at)}
                        </p>
                      </div>
                    </div>
                    <Badge className={`${getStatusColor(application.status)} border`}>
                      {getStatusLabel(application.status)}
                    </Badge>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-foreground">Progresso</span>
                        <span className="text-sm text-muted-foreground">
                          {application.progress_percentage}%
                        </span>
                      </div>
                      <Progress value={application.progress_percentage} className="h-2" />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Etapa atual:</p>
                        <p className="text-sm font-medium text-foreground">
                          {application.current_step}
                        </p>
                      </div>
                      
                      {application.estimated_completion && (
                        <div className="text-right">
                          <p className="text-sm text-muted-foreground">Conclusão estimada:</p>
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3 text-muted-foreground" />
                            <p className="text-sm font-medium text-foreground">
                              {formatDate(application.estimated_completion)}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-gray-200">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        <span>ID: {application.id.substring(0, 8)}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-black hover:text-gray-700"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/applications/${application.id}`);
                        }}
                      >
                        Ver detalhes
                        <ArrowRight className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Quick Actions */}
        <Card className="glass border-0 mt-8">
          <CardHeader>
            <CardTitle>Ações Rápidas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button 
                variant="outline" 
                className="h-auto p-4 flex flex-col gap-2"
                onClick={() => navigate('/applications/new')}
              >
                <Plus className="h-6 w-6" />
                <span>Nova Aplicação</span>
              </Button>
              <Button 
                variant="outline" 
                className="h-auto p-4 flex flex-col gap-2"
                onClick={() => navigate('/documents')}
              >
                <FileText className="h-6 w-6" />
                <span>Meus Documentos</span>
              </Button>
              <Button 
                variant="outline" 
                className="h-auto p-4 flex flex-col gap-2"
                onClick={() => navigate('/chat')}
              >
                <FileText className="h-6 w-6" />
                <span>Chat com sistema</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Applications;