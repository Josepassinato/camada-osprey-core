import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { makeApiCall } from "@/utils/api";
import { 
  Play,
  Pause,
  RefreshCw,
  Bell,
  Workflow,
  AlertCircle,
  CheckCircle2,
  Clock,
  Loader2,
  BarChart3,
  Settings,
  User,
  Mail,
  Phone,
  Calendar
} from "lucide-react";

interface WorkflowExecution {
  execution_id: string;
  workflow_name: string;
  case_id: string;
  status: string;
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error?: string;
  steps: WorkflowStep[];
}

interface WorkflowStep {
  step_id: string;
  name: string;
  status: string;
  attempts: number;
  error?: string;
}

interface NotificationStats {
  total_notifications: number;
  by_status: Record<string, number>;
  by_channel: Record<string, number>;
  templates_available: number;
  email_config_valid: boolean;
  sms_config_valid: boolean;
}

interface RetryStats {
  active_operations: number;
  operation_types: string[];
  configurations: Record<string, any>;
}

const AutomationDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('workflows');
  
  // Workflow state
  const [workflows, setWorkflows] = useState<string[]>([]);
  const [activeExecutions, setActiveExecutions] = useState<WorkflowExecution[]>([]);
  const [selectedExecution, setSelectedExecution] = useState<WorkflowExecution | null>(null);
  
  // Notification state
  const [notificationStats, setNotificationStats] = useState<NotificationStats | null>(null);
  const [templates, setTemplates] = useState<any[]>([]);
  
  // Retry state
  const [retryStats, setRetryStats] = useState<RetryStats | null>(null);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError('');

      // Load workflows
      const workflowsResponse = await makeApiCall('/automation/workflows/available');
      if (workflowsResponse.ok) {
        const workflowsData = await workflowsResponse.json();
        setWorkflows(workflowsData.workflows || []);
      }

      // Load notification stats
      const notificationResponse = await makeApiCall('/automation/notifications/statistics');
      if (notificationResponse.ok) {
        const notificationData = await notificationResponse.json();
        setNotificationStats(notificationData.notification_statistics);
      }

      // Load retry stats
      const retryResponse = await makeApiCall('/automation/retry/statistics');
      if (retryResponse.ok) {
        const retryData = await retryResponse.json();
        setRetryStats(retryData.retry_statistics);
      }

      // Load notification templates
      const templatesResponse = await makeApiCall('/automation/notifications/templates');
      if (templatesResponse.ok) {
        const templatesData = await templatesResponse.json();
        setTemplates(templatesData.templates || []);
      }

    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setError('Erro ao carregar dados do dashboard');
    } finally {
      setLoading(false);
    }
  };

  const startWorkflow = async (workflowName: string) => {
    try {
      const response = await makeApiCall('/automation/workflows/start', {
        method: 'POST',
        body: JSON.stringify({
          workflow_name: workflowName,
          case_id: 'demo-case-123',
          context: {
            user_data: {
              name: 'Demo User',
              email: 'demo@example.com'
            }
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Workflow started:', data);
        loadDashboardData(); // Refresh data
      } else {
        throw new Error('Failed to start workflow');
      }
    } catch (error) {
      console.error('Error starting workflow:', error);
      setError('Erro ao iniciar workflow');
    }
  };

  const sendTestNotification = async (templateId: string) => {
    try {
      const response = await makeApiCall('/automation/notifications/send', {
        method: 'POST',
        body: JSON.stringify({
          template_id: templateId,
          recipient: {
            user_id: 'demo-user',
            name: 'Demo User',
            email: 'demo@example.com',
            language: 'pt'
          },
          variables: {
            case_id: 'demo-case-123',
            documents_count: 5,
            quality_score: 95,
            issues_count: 0
          },
          case_id: 'demo-case-123'
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Notification sent:', data);
      } else {
        throw new Error('Failed to send notification');
      }
    } catch (error) {
      console.error('Error sending notification:', error);
      setError('Erro ao enviar notificação');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'running': return 'text-blue-600 bg-blue-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'cancelled': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return <CheckCircle2 className="h-4 w-4" />;
      case 'running': return <Loader2 className="h-4 w-4 animate-spin" />;
      case 'pending': return <Clock className="h-4 w-4" />;
      case 'failed': return <AlertCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  if (loading && !notificationStats) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#FF6B35]" />
          <p className="text-gray-600">Carregando dashboard de automação...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Dashboard de Automação
          </h1>
          <p className="text-gray-600">
            Sistema de workflow automation, retry system e notificações - Phase 4D
          </p>
        </div>

        {error && (
          <Card className="mb-6 border-red-200 bg-red-50">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2 text-red-800">
                <AlertCircle className="h-5 w-5" />
                <span>{error}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Statistics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Workflows Disponíveis</CardTitle>
              <Workflow className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{workflows.length}</div>
              <p className="text-xs text-muted-foreground">Processos automatizados</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Notificações Ativas</CardTitle>
              <Bell className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{notificationStats?.total_notifications || 0}</div>
              <p className="text-xs text-muted-foreground">{templates.length} templates disponíveis</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Operações Retry</CardTitle>
              <RefreshCw className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{retryStats?.active_operations || 0}</div>
              <p className="text-xs text-muted-foreground">{retryStats?.operation_types.length || 0} tipos configurados</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList>
            <TabsTrigger value="workflows">Workflows</TabsTrigger>
            <TabsTrigger value="notifications">Notificações</TabsTrigger>
            <TabsTrigger value="retry">Sistema de Retry</TabsTrigger>
          </TabsList>

          {/* Workflows Tab */}
          <TabsContent value="workflows" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Available Workflows */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Workflow className="h-5 w-5" />
                    <span>Workflows Disponíveis</span>
                  </CardTitle>
                  <CardDescription>
                    Processos automatizados para diferentes tipos de visto
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {workflows.map((workflow, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">{workflow.replace(/_/g, ' ').toUpperCase()}</div>
                          <div className="text-sm text-gray-600">
                            {workflow.includes('h1b') && 'H-1B Complete Process'}
                            {workflow.includes('f1') && 'F-1 Student Visa Process'}
                            {workflow.includes('i485') && 'I-485 Adjustment Process'}
                            {workflow.includes('error') && 'Error Recovery Process'}
                          </div>
                        </div>
                        <Button
                          onClick={() => startWorkflow(workflow)}
                          size="sm"
                          className="bg-[#FF6B35] hover:bg-[#FF6B35]/90"
                        >
                          <Play className="w-4 h-4 mr-1" />
                          Start
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Workflow Execution Details */}
              <Card>
                <CardHeader>
                  <CardTitle>Execuções Recentes</CardTitle>
                  <CardDescription>
                    Status das execuções de workflow mais recentes
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {activeExecutions.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <Workflow className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>Nenhuma execução ativa</p>
                      <p className="text-sm">Inicie um workflow para ver detalhes aqui</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {activeExecutions.map((execution) => (
                        <div key={execution.execution_id} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              {getStatusIcon(execution.status)}
                              <span className="font-medium">{execution.workflow_name}</span>
                            </div>
                            <Badge className={getStatusColor(execution.status)}>
                              {execution.status}
                            </Badge>
                          </div>
                          
                          <div className="text-sm text-gray-600 mb-2">
                            Case: {execution.case_id}
                          </div>
                          
                          <Progress value={execution.progress} className="h-2 mb-2" />
                          
                          <div className="text-xs text-gray-500">
                            Progresso: {execution.progress.toFixed(1)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Notification Statistics */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <BarChart3 className="h-5 w-5" />
                    <span>Estatísticas de Notificações</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {notificationStats && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-3 bg-blue-50 rounded-lg">
                          <div className="text-2xl font-bold text-blue-600">
                            {notificationStats.total_notifications}
                          </div>
                          <div className="text-sm text-blue-800">Total</div>
                        </div>
                        <div className="text-center p-3 bg-green-50 rounded-lg">
                          <div className="text-2xl font-bold text-green-600">
                            {notificationStats.templates_available}
                          </div>
                          <div className="text-sm text-green-800">Templates</div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Por Status</h4>
                        <div className="space-y-2">
                          {Object.entries(notificationStats.by_status || {}).map(([status, count]) => (
                            <div key={status} className="flex justify-between items-center">
                              <span className="capitalize">{status}</span>
                              <Badge variant="outline">{count}</Badge>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Por Canal</h4>
                        <div className="space-y-2">
                          {Object.entries(notificationStats.by_channel || {}).map(([channel, count]) => (
                            <div key={channel} className="flex justify-between items-center">
                              <div className="flex items-center space-x-2">
                                {channel === 'email' && <Mail className="h-4 w-4" />}
                                {channel === 'sms' && <Phone className="h-4 w-4" />}
                                <span className="capitalize">{channel}</span>
                              </div>
                              <Badge variant="outline">{count}</Badge>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Notification Templates */}
              <Card>
                <CardHeader>
                  <CardTitle>Templates de Notificação</CardTitle>
                  <CardDescription>
                    Templates disponíveis para diferentes eventos
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {templates.map((template, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex-1">
                          <div className="font-medium">{template.name}</div>
                          <div className="text-sm text-gray-600 flex items-center space-x-2">
                            <Badge variant="outline" className="text-xs">
                              {template.channel}
                            </Badge>
                            <span>{template.language}</span>
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            Variables: {template.variables.join(', ')}
                          </div>
                        </div>
                        <Button
                          onClick={() => sendTestNotification(template.template_id)}
                          size="sm"
                          variant="outline"
                        >
                          <Bell className="w-4 h-4 mr-1" />
                          Test
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Retry System Tab */}
          <TabsContent value="retry" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <RefreshCw className="h-5 w-5" />
                  <span>Sistema de Retry Automático</span>
                </CardTitle>
                <CardDescription>
                  Configurações e estatísticas do sistema de retry
                </CardDescription>
              </CardHeader>
              <CardContent>
                {retryStats && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-yellow-50 rounded-lg">
                        <div className="text-2xl font-bold text-yellow-600">
                          {retryStats.active_operations}
                        </div>
                        <div className="text-sm text-yellow-800">Operações Ativas</div>
                      </div>
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {retryStats.operation_types.length}
                        </div>
                        <div className="text-sm text-blue-800">Tipos Configurados</div>
                      </div>
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {Object.keys(retryStats.configurations).length}
                        </div>
                        <div className="text-sm text-green-800">Configurações</div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-4">Configurações por Tipo de Operação</h4>
                      <div className="space-y-3">
                        {Object.entries(retryStats.configurations).map(([type, config]: [string, any]) => (
                          <div key={type} className="border rounded-lg p-4">
                            <div className="flex justify-between items-start mb-2">
                              <h5 className="font-medium capitalize">{type.replace('_', ' ')}</h5>
                              <Badge variant="outline">{config.strategy}</Badge>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <span className="text-gray-600">Max Attempts:</span>
                                <div className="font-medium">{config.max_attempts}</div>
                              </div>
                              <div>
                                <span className="text-gray-600">Base Delay:</span>
                                <div className="font-medium">{config.base_delay}s</div>
                              </div>
                              <div>
                                <span className="text-gray-600">Max Delay:</span>
                                <div className="font-medium">{config.max_delay}s</div>
                              </div>
                              <div>
                                <span className="text-gray-600">Strategy:</span>
                                <div className="font-medium">{config.strategy}</div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AutomationDashboard;