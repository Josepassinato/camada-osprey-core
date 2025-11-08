import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Bell,
  X,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ArrowRight,
  Sparkles,
  TrendingUp,
  FileText,
  Calendar
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ProactiveAlert {
  id: string;
  type: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  icon: string;
  title: string;
  message: string;
  action: string;
  action_label: string;
  action_url?: string;
  details: Record<string, any>;
  created_at: string;
  dismissed: boolean;
}

interface ProactiveAlertsDisplayProps {
  caseId: string;
  autoRefresh?: boolean;
  refreshInterval?: number; // em segundos
  showDismissed?: boolean;
  compact?: boolean;
}

export const ProactiveAlertsDisplay: React.FC<ProactiveAlertsDisplayProps> = ({
  caseId,
  autoRefresh = false,
  refreshInterval = 300, // 5 minutos
  showDismissed = false,
  compact = false
}) => {
  const [alerts, setAlerts] = useState<ProactiveAlert[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://owlagent.preview.emergentagent.com';

  useEffect(() => {
    if (caseId) {
      fetchAlerts();
      fetchSummary();
    }

    if (autoRefresh && refreshInterval > 0) {
      const interval = setInterval(() => {
        fetchAlerts();
        fetchSummary();
      }, refreshInterval * 1000);

      return () => clearInterval(interval);
    }
  }, [caseId, showDismissed]);

  const fetchAlerts = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${backendUrl}/api/alerts/${caseId}?include_dismissed=${showDismissed}`
      );

      if (!response.ok) {
        throw new Error('Falha ao carregar alertas');
      }

      const data = await response.json();
      setAlerts(data.alerts || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/alerts/${caseId}/summary`);
      
      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      }
    } catch (err) {
      console.error('Error fetching summary:', err);
    }
  };

  const dismissAlert = async (alertId: string) => {
    try {
      const response = await fetch(
        `${backendUrl}/api/alerts/${caseId}/dismiss/${alertId}`,
        { method: 'POST' }
      );

      if (response.ok) {
        setAlerts(prev => prev.filter(alert => alert.id !== alertId));
        fetchSummary(); // Atualizar summary
      }
    } catch (err) {
      console.error('Error dismissing alert:', err);
    }
  };

  const handleAction = (alert: ProactiveAlert) => {
    if (alert.action_url) {
      if (alert.action_url.startsWith('http')) {
        window.open(alert.action_url, '_blank');
      } else {
        navigate(alert.action_url);
      }
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'border-red-500 bg-red-50';
      case 'high': return 'border-orange-500 bg-orange-50';
      case 'medium': return 'border-yellow-500 bg-yellow-50';
      case 'low': return 'border-blue-500 bg-blue-50';
      default: return 'border-gray-500 bg-gray-50';
    }
  };

  const getPriorityBadge = (priority: string) => {
    const colors = {
      urgent: 'bg-red-600 text-white',
      high: 'bg-orange-600 text-white',
      medium: 'bg-yellow-600 text-white',
      low: 'bg-blue-600 text-white'
    };

    const labels = {
      urgent: 'URGENTE',
      high: 'ALTA',
      medium: 'MÉDIA',
      low: 'BAIXA'
    };

    return (
      <Badge className={colors[priority as keyof typeof colors]}>
        {labels[priority as keyof typeof labels]}
      </Badge>
    );
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'document_expiring': return <Clock className="w-5 h-5" />;
      case 'incomplete_fields': return <FileText className="w-5 h-5" />;
      case 'opportunity': return <Sparkles className="w-5 h-5" />;
      case 'good_news': return <TrendingUp className="w-5 h-5" />;
      case 'deadline_approaching': return <Calendar className="w-5 h-5" />;
      default: return <Bell className="w-5 h-5" />;
    }
  };

  if (loading && alerts.length === 0) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center space-x-2">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span>Carregando alertas...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Erro ao Carregar Alertas</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (alerts.length === 0) {
    return (
      <Card className="border-2 border-green-200 bg-green-50">
        <CardContent className="p-6 text-center">
          <CheckCircle2 className="w-12 h-12 mx-auto text-green-600 mb-3" />
          <p className="text-green-900 font-medium">Tudo em dia!</p>
          <p className="text-sm text-green-700 mt-1">
            Nenhum alerta ativo no momento. Continue assim! 🎉
          </p>
        </CardContent>
      </Card>
    );
  }

  // Compact mode (for dashboard/header)
  if (compact) {
    const urgentCount = alerts.filter(a => a.priority === 'urgent').length;
    const highCount = alerts.filter(a => a.priority === 'high').length;

    return (
      <Button variant="outline" className="relative">
        <Bell className="w-4 h-4 mr-2" />
        <span>{alerts.length} Alertas</span>
        {urgentCount > 0 && (
          <Badge className="ml-2 bg-red-600 text-white">
            {urgentCount} urgente{urgentCount > 1 ? 's' : ''}
          </Badge>
        )}
      </Button>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary Card */}
      {summary && (
        <Card className="border-blue-200 bg-gradient-to-r from-blue-50 to-white">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Bell className="w-5 h-5 text-blue-600" />
                <CardTitle>Seus Alertas Inteligentes</CardTitle>
              </div>
              <Badge variant="outline">{summary.total_alerts} ativos</Badge>
            </div>
            <CardDescription>
              Sistema de guia proativo baseado em requisitos do USCIS
            </CardDescription>
          </CardHeader>
          {summary.urgent_count > 0 && (
            <CardContent>
              <Alert className="border-red-500 bg-red-50">
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle className="text-red-900">
                  {summary.urgent_count} Alerta{summary.urgent_count > 1 ? 's' : ''} Urgente{summary.urgent_count > 1 ? 's' : ''}!
                </AlertTitle>
                <AlertDescription className="text-red-800">
                  Requer atenção imediata para evitar problemas com sua aplicação.
                </AlertDescription>
              </Alert>
            </CardContent>
          )}
        </Card>
      )}

      {/* Alerts List */}
      <ScrollArea className="h-[600px]">
        <div className="space-y-3">
          {alerts.map((alert) => (
            <Card key={alert.id} className={`border-2 ${getPriorityColor(alert.priority)}`}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <div className="flex-shrink-0 mt-1">
                      {getAlertIcon(alert.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <CardTitle className="text-lg">{alert.title}</CardTitle>
                        {getPriorityBadge(alert.priority)}
                      </div>
                      <CardDescription className="text-base whitespace-pre-line">
                        {alert.message}
                      </CardDescription>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => dismissAlert(alert.id)}
                    className="flex-shrink-0"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-xs text-gray-600">
                    <span className="text-2xl mr-1">{alert.icon}</span>
                    {new Date(alert.created_at).toLocaleDateString('pt-BR')}
                  </div>
                  {alert.action_label && (
                    <Button
                      onClick={() => handleAction(alert)}
                      className="gap-2"
                    >
                      {alert.action_label}
                      <ArrowRight className="w-4 h-4" />
                    </Button>
                  )}
                </div>

                {/* Details Section */}
                {alert.details && Object.keys(alert.details).length > 0 && (
                  <div className="mt-4 p-3 bg-white rounded-lg border">
                    <p className="text-xs font-medium text-gray-700 mb-2">Detalhes:</p>
                    <div className="space-y-1">
                      {Object.entries(alert.details).map(([key, value]) => {
                        if (typeof value === 'object') return null;
                        return (
                          <div key={key} className="text-xs">
                            <span className="text-gray-600">{key}: </span>
                            <span className="text-gray-900 font-medium">{String(value)}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </ScrollArea>

      {/* Footer Info */}
      <Card className="border-gray-200 bg-gray-50">
        <CardContent className="pt-4">
          <div className="flex items-center space-x-2 text-xs text-gray-600">
            <Bell className="w-4 h-4" />
            <span>
              Alertas são gerados automaticamente baseados em dados do USCIS e no progresso da sua aplicação.
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Compact version for notifications badge
export const AlertsBadge: React.FC<{ caseId: string }> = ({ caseId }) => {
  const [count, setCount] = useState(0);
  const [urgentCount, setUrgentCount] = useState(0);

  const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://owlagent.preview.emergentagent.com';

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await fetch(`${backendUrl}/api/alerts/${caseId}/summary`);
        if (response.ok) {
          const data = await response.json();
          setCount(data.total_alerts);
          setUrgentCount(data.urgent_count);
        }
      } catch (err) {
        console.error('Error fetching alerts summary:', err);
      }
    };

    if (caseId) {
      fetchSummary();
      const interval = setInterval(fetchSummary, 60000); // Atualizar a cada minuto
      return () => clearInterval(interval);
    }
  }, [caseId]);

  if (count === 0) return null;

  return (
    <div className="relative inline-flex">
      <Bell className="w-5 h-5 text-gray-700" />
      {count > 0 && (
        <span className={`absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full text-xs font-bold text-white ${
          urgentCount > 0 ? 'bg-red-600' : 'bg-blue-600'
        }`}>
          {count > 9 ? '9+' : count}
        </span>
      )}
    </div>
  );
};

export default ProactiveAlertsDisplay;
