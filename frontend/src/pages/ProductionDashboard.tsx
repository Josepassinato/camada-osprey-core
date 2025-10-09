import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { makeApiCall } from "@/utils/api";
import { 
  Shield,
  Database,
  Activity,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
  BarChart3,
  Zap,
  Server,
  Lock,
  Unlock,
  Play,
  Square,
  RefreshCw,
  Trash2,
  TrendingUp,
  Users,
  Globe
} from "lucide-react";

interface SystemHealth {
  overall_status: string;
  timestamp: string;
  components: Record<string, any>;
}

interface DatabasePerformance {
  database: {
    collections: number;
    data_size_mb: number;
    storage_size_mb: number;
    indexes: number;
    index_size_mb: number;
  };
  query_performance: {
    avg_query_time_ms: number;
    slow_queries_count: number;
    total_recent_queries: number;
  };
  cache_performance: {
    overall_hit_rate: number;
    total_requests: number;
    redis_connected: boolean;
  };
}

interface SecurityStats {
  blocked_ips: number;
  suspicious_ips: number;
  total_security_events: number;
  recent_events_last_hour: number;
  events_by_severity: Record<string, number>;
}

interface LoadTestResult {
  test_name: string;
  total_requests: number;
  success_rate: number;
  avg_response_time: number;
  performance_grade: string;
}

const ProductionDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  
  // System state
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [dbPerformance, setDbPerformance] = useState<DatabasePerformance | null>(null);
  const [securityStats, setSecurityStats] = useState<SecurityStats | null>(null);
  const [securityEvents, setSecurityEvents] = useState<any[]>([]);
  
  // Load testing state
  const [availableTests, setAvailableTests] = useState<any[]>([]);
  const [activeLoadTests, setActiveLoadTests] = useState<string[]>([]);
  const [loadTestResults, setLoadTestResults] = useState<Record<string, any>>({});

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError('');

      // Load system health
      const healthResponse = await makeApiCall('/production/system/health');
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setSystemHealth(healthData.health);
      }

      // Load database performance
      const dbResponse = await makeApiCall('/production/performance/database');
      if (dbResponse.ok) {
        const dbData = await dbResponse.json();
        setDbPerformance(dbData.database_performance);
      }

      // Load security statistics
      const securityResponse = await makeApiCall('/production/security/statistics');
      if (securityResponse.ok) {
        const securityData = await securityResponse.json();
        setSecurityStats(securityData.security_statistics);
      }

      // Load recent security events
      const eventsResponse = await makeApiCall('/production/security/events?limit=20');
      if (eventsResponse.ok) {
        const eventsData = await eventsResponse.json();
        setSecurityEvents(eventsData.security_events || []);
      }

      // Load available load tests
      const testsResponse = await makeApiCall('/production/load-testing/available-tests');
      if (testsResponse.ok) {
        const testsData = await testsResponse.json();
        setAvailableTests(testsData.available_tests || []);
      }

    } catch (error) {
      console.error('Error loading production dashboard:', error);
      setError('Erro ao carregar dashboard de produção');
    } finally {
      setLoading(false);
    }
  };

  const startLoadTest = async (testType: string) => {
    try {
      const response = await makeApiCall('/production/load-testing/start', {
        method: 'POST',
        body: JSON.stringify({
          test_type: testType,
          base_url: window.location.origin
        })
      });

      if (response.ok) {
        const data = await response.json();
        setActiveLoadTests(prev => [...prev, data.test_id]);
        
        // Start monitoring this test
        monitorLoadTest(data.test_id);
      }
    } catch (error) {
      console.error('Error starting load test:', error);
      setError('Erro ao iniciar teste de carga');
    }
  };

  const monitorLoadTest = async (testId: string) => {
    const checkTest = async () => {
      try {
        const response = await makeApiCall(`/production/load-testing/${testId}/status`);
        if (response.ok) {
          const data = await response.json();
          
          if (data.status === 'completed') {
            setLoadTestResults(prev => ({...prev, [testId]: data.result}));
            setActiveLoadTests(prev => prev.filter(id => id !== testId));
          } else if (data.status === 'running') {
            // Continue monitoring
            setTimeout(checkTest, 5000);
          }
        }
      } catch (error) {
        console.error('Error monitoring test:', error);
      }
    };
    
    checkTest();
  };

  const optimizeDatabase = async () => {
    try {
      const response = await makeApiCall('/production/database/optimize', {
        method: 'POST'
      });

      if (response.ok) {
        alert('Otimização do banco iniciada com sucesso!');
        loadDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Error optimizing database:', error);
      setError('Erro ao otimizar banco de dados');
    }
  };

  const clearCache = async () => {
    try {
      const response = await makeApiCall('/production/cache/clear', {
        method: 'POST',
        body: JSON.stringify({})
      });

      if (response.ok) {
        alert('Cache limpo com sucesso!');
        loadDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Error clearing cache:', error);
      setError('Erro ao limpar cache');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'unhealthy': case 'degraded': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy': return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'unhealthy': case 'degraded': return <XCircle className="h-4 w-4 text-red-500" />;
      default: return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getPerformanceGradeColor = (grade: string) => {
    switch (grade) {
      case 'A+': case 'A': return 'bg-green-100 text-green-800';
      case 'B': return 'bg-blue-100 text-blue-800';
      case 'C': return 'bg-yellow-100 text-yellow-800';
      case 'D': return 'bg-orange-100 text-orange-800';
      case 'F': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading && !systemHealth) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#FF6B35]" />
          <p className="text-gray-600">Carregando dashboard de produção...</p>
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
            Dashboard de Produção
          </h1>
          <p className="text-gray-600">
            Performance, segurança e otimização - Phase 4B
          </p>
        </div>

        {error && (
          <Card className="mb-6 border-red-200 bg-red-50">
            <CardContent className="p-4">
              <div className="flex items-center space-x-2 text-red-800">
                <AlertTriangle className="h-5 w-5" />
                <span>{error}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* System Health Overview */}
        {systemHealth && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>Status Geral do Sistema</span>
                <Badge className={getStatusColor(systemHealth.overall_status)}>
                  {systemHealth.overall_status}
                </Badge>
              </CardTitle>
              <CardDescription>
                Última verificação: {new Date(systemHealth.timestamp).toLocaleString()}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(systemHealth.components).map(([component, data]: [string, any]) => (
                  <div key={component} className="flex items-center space-x-3 p-3 border rounded-lg">
                    {getStatusIcon(data.status)}
                    <div>
                      <div className="font-medium capitalize">{component.replace(/_/g, ' ')}</div>
                      <div className="text-sm text-gray-600">{data.status}</div>
                      {data.error && (
                        <div className="text-xs text-red-600">{data.error}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Visão Geral</TabsTrigger>
            <TabsTrigger value="database">Database</TabsTrigger>
            <TabsTrigger value="security">Segurança</TabsTrigger>
            <TabsTrigger value="load-testing">Testes de Carga</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Database Performance Summary */}
              {dbPerformance && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Performance do Banco</CardTitle>
                    <Database className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">Tempo médio de query:</span>
                        <span className="text-sm font-medium">
                          {dbPerformance.query_performance.avg_query_time_ms.toFixed(1)}ms
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Hit rate do cache:</span>
                        <span className="text-sm font-medium">
                          {(dbPerformance.cache_performance.overall_hit_rate * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Collections:</span>
                        <span className="text-sm font-medium">{dbPerformance.database.collections}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Security Summary */}
              {securityStats && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Segurança</CardTitle>
                    <Shield className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">IPs bloqueados:</span>
                        <span className="text-sm font-medium">{securityStats.blocked_ips}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Eventos recentes:</span>
                        <span className="text-sm font-medium">{securityStats.recent_events_last_hour}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Total de eventos:</span>
                        <span className="text-sm font-medium">{securityStats.total_security_events}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Load Testing Summary */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Testes de Carga</CardTitle>
                  <Zap className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Testes ativos:</span>
                      <span className="text-sm font-medium">{activeLoadTests.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Testes disponíveis:</span>
                      <span className="text-sm font-medium">{availableTests.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Resultados:</span>
                      <span className="text-sm font-medium">{Object.keys(loadTestResults).length}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Database Tab */}
          <TabsContent value="database" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Database Statistics */}
              {dbPerformance && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Database className="h-5 w-5" />
                      <span>Estatísticas do Banco</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-3 bg-blue-50 rounded-lg">
                          <div className="text-2xl font-bold text-blue-600">
                            {dbPerformance.database.data_size_mb.toFixed(1)} MB
                          </div>
                          <div className="text-sm text-blue-800">Dados</div>
                        </div>
                        <div className="text-center p-3 bg-green-50 rounded-lg">
                          <div className="text-2xl font-bold text-green-600">
                            {dbPerformance.database.indexes}
                          </div>
                          <div className="text-sm text-green-800">Índices</div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm text-gray-600">Cache Hit Rate</span>
                          <span className="text-sm font-medium">
                            {(dbPerformance.cache_performance.overall_hit_rate * 100).toFixed(1)}%
                          </span>
                        </div>
                        <Progress 
                          value={dbPerformance.cache_performance.overall_hit_rate * 100} 
                          className="h-2"
                        />
                      </div>

                      <div className="flex space-x-2">
                        <Button
                          onClick={optimizeDatabase}
                          className="bg-[#FF6B35] hover:bg-[#FF6B35]/90 flex-1"
                        >
                          <Database className="w-4 h-4 mr-2" />
                          Otimizar Banco
                        </Button>
                        <Button
                          onClick={clearCache}
                          variant="outline"
                          className="flex-1"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Limpar Cache
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Query Performance */}
              {dbPerformance && (
                <Card>
                  <CardHeader>
                    <CardTitle>Performance de Queries</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Tempo médio de query:</span>
                        <Badge variant="outline">
                          {dbPerformance.query_performance.avg_query_time_ms.toFixed(1)}ms
                        </Badge>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Queries lentas:</span>
                        <Badge 
                          variant="outline"
                          className={dbPerformance.query_performance.slow_queries_count > 0 ? 'border-yellow-500' : ''}
                        >
                          {dbPerformance.query_performance.slow_queries_count}
                        </Badge>
                      </div>

                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Redis conectado:</span>
                        <Badge 
                          variant="outline"
                          className={dbPerformance.cache_performance.redis_connected ? 'border-green-500' : 'border-red-500'}
                        >
                          {dbPerformance.cache_performance.redis_connected ? 'Sim' : 'Não'}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Security Statistics */}
              {securityStats && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Shield className="h-5 w-5" />
                      <span>Estatísticas de Segurança</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-3 bg-red-50 rounded-lg">
                          <div className="text-2xl font-bold text-red-600">
                            {securityStats.blocked_ips}
                          </div>
                          <div className="text-sm text-red-800">IPs Bloqueados</div>
                        </div>
                        <div className="text-center p-3 bg-yellow-50 rounded-lg">
                          <div className="text-2xl font-bold text-yellow-600">
                            {securityStats.recent_events_last_hour}
                          </div>
                          <div className="text-sm text-yellow-800">Eventos Recentes</div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Eventos por Severidade</h4>
                        <div className="space-y-2">
                          {Object.entries(securityStats.events_by_severity || {}).map(([severity, count]) => (
                            <div key={severity} className="flex justify-between items-center">
                              <span className="capitalize">{severity}</span>
                              <Badge variant="outline">{count}</Badge>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Recent Security Events */}
              <Card>
                <CardHeader>
                  <CardTitle>Eventos Recentes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {securityEvents.map((event, index) => (
                      <div key={index} className="border-l-4 border-gray-200 pl-4 py-2">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="font-medium">{event.event_type}</div>
                            <div className="text-sm text-gray-600">
                              IP: {event.ip_address} • {event.endpoint}
                            </div>
                            <div className="text-xs text-gray-500">
                              {new Date(event.timestamp).toLocaleString()}
                            </div>
                          </div>
                          <Badge 
                            variant="outline" 
                            className={
                              event.severity === 'critical' ? 'border-red-500 text-red-700' :
                              event.severity === 'high' ? 'border-orange-500 text-orange-700' :
                              event.severity === 'medium' ? 'border-yellow-500 text-yellow-700' :
                              'border-gray-500 text-gray-700'
                            }
                          >
                            {event.severity}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Load Testing Tab */}
          <TabsContent value="load-testing" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Available Tests */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Zap className="h-5 w-5" />
                    <span>Testes Disponíveis</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {availableTests.map((test, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex-1">
                          <div className="font-medium">{test.name}</div>
                          <div className="text-sm text-gray-600">
                            {test.concurrent_users} usuários • {test.duration_seconds}s
                          </div>
                          <div className="text-xs text-gray-500">{test.endpoint}</div>
                        </div>
                        <Button
                          onClick={() => startLoadTest(test.test_type)}
                          size="sm"
                          disabled={activeLoadTests.length > 0}
                          className="bg-[#FF6B35] hover:bg-[#FF6B35]/90"
                        >
                          <Play className="w-4 h-4 mr-1" />
                          Executar
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Test Results */}
              <Card>
                <CardHeader>
                  <CardTitle>Resultados dos Testes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {activeLoadTests.length > 0 && (
                      <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                          <span className="text-blue-800">
                            {activeLoadTests.length} teste(s) em execução...
                          </span>
                        </div>
                      </div>
                    )}

                    {Object.entries(loadTestResults).map(([testId, result]: [string, any]) => (
                      <div key={testId} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-medium">{result.test_name}</h4>
                          <Badge className={getPerformanceGradeColor(result.performance_grade)}>
                            {result.performance_grade}
                          </Badge>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Requests:</span>
                            <div className="font-medium">{result.total_requests}</div>
                          </div>
                          <div>
                            <span className="text-gray-600">Taxa de sucesso:</span>
                            <div className="font-medium">{(result.success_rate * 100).toFixed(1)}%</div>
                          </div>
                          <div>
                            <span className="text-gray-600">Tempo médio:</span>
                            <div className="font-medium">{result.avg_response_time.toFixed(0)}ms</div>
                          </div>
                          <div>
                            <span className="text-gray-600">RPS:</span>
                            <div className="font-medium">{result.requests_per_second.toFixed(1)}</div>
                          </div>
                        </div>
                      </div>
                    ))}

                    {Object.keys(loadTestResults).length === 0 && activeLoadTests.length === 0 && (
                      <div className="text-center py-8 text-gray-500">
                        <Zap className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                        <p>Nenhum teste executado ainda</p>
                        <p className="text-sm">Execute um teste para ver os resultados aqui</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ProductionDashboard;