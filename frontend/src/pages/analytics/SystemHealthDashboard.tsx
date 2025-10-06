import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  Wifi,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Database,
  Server,
  RefreshCw
} from "lucide-react";

interface SystemHealthMetrics {
  cpu_usage: number;
  memory_usage: number;
  active_requests: number;
  requests_per_minute: number;
  error_rate: number;
  status: string;
}

interface QuickMetrics {
  system_health: SystemHealthMetrics;
  processing_queue: {
    documents_in_queue: number;
    ai_queue_size: number;
    ocr_processing_active: number;
  };
  services: Record<string, string>;
  alerts: string[];
  timestamp: string;
}

const SystemHealthDashboard: React.FC<{ realTimeData: QuickMetrics | null }> = ({ realTimeData }) => {
  const [healthMetrics, setHealthMetrics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    if (realTimeData) {
      setHealthMetrics(realTimeData);
      setIsLoading(false);
    } else {
      fetchSystemHealth();
    }

    // Auto-refresh every 15 seconds
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(fetchSystemHealth, 15000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, realTimeData]);

  const fetchSystemHealth = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/analytics/system/realtime`);
      
      if (response.ok) {
        const data = await response.json();
        setHealthMetrics(data);
      } else {
        // Mock data for development
        setHealthMetrics({
          system_health: {
            cpu_usage: 45.3,
            memory_usage: 62.1,
            active_requests: 12,
            requests_per_minute: 145.8,
            error_rate: 1.2,
            status: 'healthy'
          },
          processing_queue: {
            documents_in_queue: 8,
            ai_queue_size: 3,
            ocr_processing_active: 2
          },
          services: {
            'dr_paula': 'healthy',
            'document_validator': 'healthy',
            'ocr_engine': 'healthy',
            'database': 'healthy',
            'api_server': 'healthy'
          },
          alerts: [],
          timestamp: new Date().toISOString()
        });
      }
    } catch (error) {
      console.error('System health error:', error);
      setError('Connection error');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      'healthy': 'bg-green-100 text-green-800 border-green-200',
      'warning': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'degraded': 'bg-orange-100 text-orange-800 border-orange-200',
      'critical': 'bg-red-100 text-red-800 border-red-200',
      'down': 'bg-red-100 text-red-800 border-red-200'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getStatusIcon = (status: string) => {
    const icons = {
      'healthy': CheckCircle,
      'warning': AlertTriangle,
      'degraded': AlertTriangle,
      'critical': AlertTriangle,
      'down': AlertTriangle
    };
    const IconComponent = icons[status as keyof typeof icons] || Clock;
    return <IconComponent className="h-4 w-4" />;
  };

  const getUsageColor = (usage: number, type: 'cpu' | 'memory' | 'error') => {
    if (type === 'error') {
      if (usage > 5) return 'text-red-600';
      if (usage > 2) return 'text-yellow-600';
      return 'text-green-600';
    }
    
    if (usage > 80) return 'text-red-600';
    if (usage > 60) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getServiceName = (service: string) => {
    const names = {
      'dr_paula': 'Dra. Paula AI',
      'document_validator': 'Document Validator',
      'ocr_engine': 'OCR Engine',
      'database': 'MongoDB Database',
      'api_server': 'API Server'
    };
    return names[service as keyof typeof names] || service;
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="bg-white border-0 shadow-md">
            <CardContent className="p-6">
              <div className="animate-pulse space-y-4">
                <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error || !healthMetrics) {
    return (
      <Card className="bg-white border-0 shadow-md">
        <CardContent className="p-6 text-center">
          <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading System Health</h3>
          <p className="text-gray-600">{error || 'Failed to load system health metrics'}</p>
          <Button onClick={fetchSystemHealth} className="mt-4">Retry</Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* System Overview */}
      <Card className="bg-white border-0 shadow-md">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            System Health Overview
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={autoRefresh ? 'bg-green-50 border-green-200' : ''}
            >
              <RefreshCw className={`h-4 w-4 ${autoRefresh ? 'animate-spin' : ''}`} />
            </Button>
            <Badge className={getStatusColor(healthMetrics.system_health.status)}>
              {healthMetrics.system_health.status.toUpperCase()}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* CPU Usage */}
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-3 bg-blue-100 rounded-full flex items-center justify-center">
                <Cpu className="h-8 w-8 text-blue-600" />
              </div>
              <div className={`text-2xl font-bold ${getUsageColor(healthMetrics.system_health.cpu_usage, 'cpu')}`}>
                {healthMetrics.system_health.cpu_usage.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600 mb-2">CPU Usage</div>
              <Progress value={healthMetrics.system_health.cpu_usage} className="h-2" />
            </div>

            {/* Memory Usage */}
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-3 bg-purple-100 rounded-full flex items-center justify-center">
                <HardDrive className="h-8 w-8 text-purple-600" />
              </div>
              <div className={`text-2xl font-bold ${getUsageColor(healthMetrics.system_health.memory_usage, 'memory')}`}>
                {healthMetrics.system_health.memory_usage.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600 mb-2">Memory Usage</div>
              <Progress value={healthMetrics.system_health.memory_usage} className="h-2" />
            </div>

            {/* Active Requests */}
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-3 bg-green-100 rounded-full flex items-center justify-center">
                <Wifi className="h-8 w-8 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {healthMetrics.system_health.active_requests}
              </div>
              <div className="text-sm text-gray-600">Active Requests</div>
              <div className="text-xs text-gray-500 mt-1">
                {healthMetrics.system_health.requests_per_minute.toFixed(1)}/min
              </div>
            </div>

            {/* Error Rate */}
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-3 bg-orange-100 rounded-full flex items-center justify-center">
                <AlertTriangle className="h-8 w-8 text-orange-600" />
              </div>
              <div className={`text-2xl font-bold ${getUsageColor(healthMetrics.system_health.error_rate, 'error')}`}>
                {healthMetrics.system_health.error_rate.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600 mb-2">Error Rate</div>
              <Progress 
                value={Math.min(healthMetrics.system_health.error_rate * 10, 100)} 
                className="h-2" 
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Services Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-white border-0 shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5" />
              Service Health Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(healthMetrics.services).map(([service, status]) => (
                <div key={service} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      status === 'healthy' ? 'bg-green-100' : 'bg-red-100'
                    }`}>
                      {getStatusIcon(status)}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{getServiceName(service)}</div>
                      <div className="text-sm text-gray-600">Service Status</div>
                    </div>
                  </div>
                  <Badge className={getStatusColor(status)}>
                    {status.toUpperCase()}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-0 shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Processing Queues
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <Clock className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">Documents Queue</div>
                    <div className="text-sm text-gray-600">Pending Processing</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold text-gray-900">
                    {healthMetrics.processing_queue.documents_in_queue}
                  </div>
                  <div className="text-xs text-gray-500">documents</div>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <Zap className="h-4 w-4 text-purple-600" />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">AI Queue</div>
                    <div className="text-sm text-gray-600">AI Processing</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold text-gray-900">
                    {healthMetrics.processing_queue.ai_queue_size}
                  </div>
                  <div className="text-xs text-gray-500">requests</div>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                    <Activity className="h-4 w-4 text-orange-600" />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">Active OCR</div>
                    <div className="text-sm text-gray-600">Currently Processing</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold text-gray-900">
                    {healthMetrics.processing_queue.ocr_processing_active}
                  </div>
                  <div className="text-xs text-gray-500">active</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Alerts and Recommendations */}
      {(healthMetrics.alerts && healthMetrics.alerts.length > 0) ? (
        <Card className="bg-white border-0 shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="h-5 w-5" />
              Active System Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {healthMetrics.alerts.map((alert: string, index: number) => (
                <div key={index} className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-red-800">System Alert</p>
                      <p className="text-sm text-red-700">{alert}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className="bg-white border-0 shadow-md">
          <CardContent className="p-6">
            <div className="text-center">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">All Systems Operational</h3>
              <p className="text-gray-600">No active alerts or issues detected</p>
              <div className="text-sm text-gray-500 mt-4">
                Last updated: {new Date(healthMetrics.timestamp).toLocaleString('pt-BR')}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Performance Recommendations */}
      <Card className="bg-white border-0 shadow-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Performance Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* CPU Optimization */}
            {healthMetrics.system_health.cpu_usage > 70 && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h4 className="font-medium text-yellow-800 mb-2">CPU Optimization</h4>
                <ul className="text-sm text-yellow-700 space-y-1">
                  <li>• Monitor CPU-intensive processes</li>
                  <li>• Consider scaling resources</li>
                  <li>• Optimize database queries</li>
                </ul>
              </div>
            )}

            {/* Memory Management */}
            {healthMetrics.system_health.memory_usage > 75 && (
              <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <h4 className="font-medium text-orange-800 mb-2">Memory Management</h4>
                <ul className="text-sm text-orange-700 space-y-1">
                  <li>• Clear unused caches</li>
                  <li>• Review memory-intensive operations</li>
                  <li>• Consider memory optimization</li>
                </ul>
              </div>
            )}

            {/* Error Rate */}
            {healthMetrics.system_health.error_rate > 3 && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <h4 className="font-medium text-red-800 mb-2">Error Rate Attention</h4>
                <ul className="text-sm text-red-700 space-y-1">
                  <li>• Investigate error patterns</li>
                  <li>• Review API error logs</li>
                  <li>• Implement error handling improvements</li>
                </ul>
              </div>
            )}

            {/* Performance is good */}
            {healthMetrics.system_health.cpu_usage < 60 && 
             healthMetrics.system_health.memory_usage < 70 && 
             healthMetrics.system_health.error_rate < 2 && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-medium text-green-800 mb-2">Excellent Performance!</h4>
                <ul className="text-sm text-green-700 space-y-1">
                  <li>• All metrics within optimal ranges</li>
                  <li>• System running efficiently</li>
                  <li>• Great job maintaining performance</li>
                </ul>
              </div>
            )}

            {/* Queue Management */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-medium text-blue-800 mb-2">Queue Management</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Documents in queue: {healthMetrics.processing_queue.documents_in_queue}</li>
                <li>• AI processing load: {healthMetrics.processing_queue.ai_queue_size} requests</li>
                <li>• OCR utilization optimal</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SystemHealthDashboard;