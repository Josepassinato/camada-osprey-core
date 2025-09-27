import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  User, 
  FileText, 
  MessageSquare, 
  Globe, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Plus,
  ArrowRight,
  BarChart,
  Calendar,
  Bell,
  GraduationCap
} from "lucide-react";
import { useNavigate } from "react-router-dom";

interface DashboardData {
  user: {
    name: string;
    email: string;
  };
  stats: {
    total_applications: number;
    in_progress: number;
    completed: number;
    success_rate: number;
  };
  applications: Array<{
    id: string;
    visa_type: string;
    status: string;
    progress_percentage: number;
    current_step: string;
    created_at: string;
  }>;
  recent_activity: {
    chats: Array<{
      session_id: string;
      last_updated: string;
      messages: Array<{
        role: string;
        content: string;
        timestamp: string;
      }>;
    }>;
    translations: Array<{
      id: string;
      source_language: string;
      target_language: string;
      timestamp: string;
    }>;
  };
}

const Dashboard = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('osprey_token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else if (response.status === 401) {
        localStorage.removeItem('osprey_token');
        localStorage.removeItem('osprey_user');
        navigate('/login');
      } else {
        setError('Erro ao carregar dashboard');
      }
    } catch (error) {
      console.error('Dashboard error:', error);
      setError('Erro de conexão');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      'not_started': 'bg-gray-100 text-gray-800',
      'in_progress': 'bg-gray-200 text-black',
      'document_review': 'bg-gray-300 text-black',
      'ready_to_submit': 'bg-gray-400 text-white',
      'submitted': 'bg-gray-500 text-white',
      'approved': 'bg-black text-white',
      'denied': 'bg-gray-600 text-white',
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status: string) => {
    const icons = {
      'not_started': Clock,
      'in_progress': AlertCircle,
      'document_review': FileText,
      'ready_to_submit': ArrowRight,
      'submitted': CheckCircle,
      'approved': CheckCircle,
      'denied': AlertCircle,
    };
    const IconComponent = icons[status as keyof typeof icons] || Clock;
    return <IconComponent className="h-4 w-4" />;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const getVisaTypeLabel = (visaType: string) => {
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
    return labels[visaType as keyof typeof labels] || visaType.toUpperCase();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto" />
          <p className="text-destructive">{error || 'Erro ao carregar dashboard'}</p>
          <Button onClick={() => window.location.reload()}>
            Tentar novamente
          </Button>
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
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                Olá, {dashboardData.user.name.split(' ')[0]}! 👋
              </h1>
              <p className="text-muted-foreground">
                Bem-vindo ao seu painel de controle imigratório
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm" onClick={() => navigate('/profile')}>
                <User className="h-4 w-4" />
                Perfil
              </Button>
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
      </div>

      <div className="container-responsive section-padding">
        {/* Stats Overview */}
        <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <Card className="glass border-0 card-hover">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-black/10 rounded-lg flex items-center justify-center">
                  <FileText className="h-6 w-6 text-black" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-foreground">
                    {dashboardData.stats.total_applications}
                  </div>
                  <div className="text-sm text-muted-foreground">Total de Aplicações</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass border-0 card-hover">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                  <Clock className="h-6 w-6 text-gray-700" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-foreground">
                    {dashboardData.stats.in_progress}
                  </div>
                  <div className="text-sm text-muted-foreground">Em Andamento</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass border-0 card-hover">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-success/10 rounded-lg flex items-center justify-center">
                  <CheckCircle className="h-6 w-6 text-success" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-foreground">
                    {dashboardData.stats.completed}
                  </div>
                  <div className="text-sm text-muted-foreground">Finalizadas</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass border-0 card-hover">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                  <FileText className="h-6 w-6 text-accent" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-foreground">
                    {dashboardData.stats.total_documents || 0}
                  </div>
                  <div className="text-sm text-muted-foreground">Documentos</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass border-0 card-hover">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-gray-700" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-foreground">
                    {dashboardData.stats.document_completion_rate || 0}%
                  </div>
                  <div className="text-sm text-muted-foreground">Docs Aprovados</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Applications */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="glass border-0">
              <CardHeader className="flex flex-row items-center justify-between pb-4">
                <CardTitle className="text-xl font-semibold">Suas Aplicações</CardTitle>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => navigate('/applications')}
                >
                  Ver todas
                </Button>
              </CardHeader>
              <CardContent className="space-y-4">
                {dashboardData.applications.length === 0 ? (
                  <div className="text-center py-8 space-y-4">
                    <div className="w-16 h-16 bg-black/10 rounded-full flex items-center justify-center mx-auto">
                      <FileText className="h-8 w-8 text-black" />
                    </div>
                    <div>
                      <h3 className="font-medium text-foreground mb-2">
                        Nenhuma aplicação ainda
                      </h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Comece sua jornada imigratória criando sua primeira aplicação
                      </p>
                      <Button className="bg-black text-white hover:bg-gray-800" onClick={() => navigate('/applications/new')}>
                        <Plus className="h-4 w-4" />
                        Criar Aplicação
                      </Button>
                    </div>
                  </div>
                ) : (
                  dashboardData.applications.map((app) => (
                    <div 
                      key={app.id}
                      className="p-4 rounded-lg border border-white/20 hover:bg-white/50 transition-colors cursor-pointer"
                      onClick={() => navigate(`/applications/${app.id}`)}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-black/10 rounded-lg flex items-center justify-center">
                            {getStatusIcon(app.status)}
                          </div>
                          <div>
                            <h4 className="font-medium text-foreground">
                              {getVisaTypeLabel(app.visa_type)}
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              Criado em {formatDate(app.created_at)}
                            </p>
                          </div>
                        </div>
                        
                        <Badge className={`${getStatusColor(app.status)} border-0`}>
                          {app.current_step.replace('_', ' ')}
                        </Badge>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-muted-foreground">Progresso</span>
                          <span className="text-foreground font-medium">{app.progress_percentage}%</span>
                        </div>
                        <Progress value={app.progress_percentage} className="h-2" />
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="glass border-0">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg font-semibold">Ações Rápidas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => navigate('/chat')}
                >
                  <MessageSquare className="h-4 w-4" />
                  Chat com IA
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => navigate('/education')}
                >
                  <GraduationCap className="h-4 w-4" />
                  Centro Educacional
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => navigate('/translate')}
                >
                  <Globe className="h-4 w-4" />
                  Tradutor
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => navigate('/documents')}
                >
                  <FileText className="h-4 w-4" />
                  Meus Documentos
                </Button>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card className="glass border-0">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg font-semibold">Atividade Recente</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {dashboardData.recent_activity.chats.slice(0, 3).map((chat, index) => (
                  <div key={chat.session_id} className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-black/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <MessageSquare className="h-4 w-4 text-black" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-foreground line-clamp-2">
                        {chat.messages?.[chat.messages.length - 1]?.content?.substring(0, 60) || 'Chat session'}...
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(chat.last_updated)}
                      </p>
                    </div>
                  </div>
                ))}

                {dashboardData.recent_activity.translations.slice(0, 2).map((translation) => (
                  <div key={translation.id} className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <Globe className="h-4 w-4 text-accent" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-foreground">
                        Tradução {translation.source_language} → {translation.target_language}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(translation.timestamp)}
                      </p>
                    </div>
                  </div>
                ))}

                {dashboardData.recent_activity.chats.length === 0 && 
                 dashboardData.recent_activity.translations.length === 0 && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    Nenhuma atividade recente
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Document Expiration Alerts */}
            {dashboardData.upcoming_expirations && dashboardData.upcoming_expirations.length > 0 && (
              <Card className="glass border-0 border-l-4 border-l-orange-500">
                <CardHeader className="pb-4">
                  <CardTitle className="text-lg font-semibold flex items-center gap-2 text-orange-600">
                    <AlertCircle className="h-5 w-5" />
                    Documentos Expirando
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {dashboardData.upcoming_expirations.slice(0, 3).map((exp, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-gray-100 rounded-lg">
                      <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                        <FileText className="h-4 w-4 text-gray-700" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-black">
                          {exp.document_type.replace('_', ' ').toUpperCase()}
                        </p>
                        <p className="text-xs text-gray-700">
                          {exp.days_to_expire} dia{exp.days_to_expire !== 1 ? 's' : ''} restante{exp.days_to_expire !== 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>
                  ))}
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full mt-3 border-gray-300 text-black hover:bg-gray-200"
                    onClick={() => navigate('/documents')}
                  >
                    Ver Todos os Documentos
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;