import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  FileText, 
  Brain, 
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Target,
  PieChart,
  LineChart,
  RefreshCw
} from "lucide-react";
import { useNavigate } from "react-router-dom";

// Sub-components for individual dashboards
import DocumentProcessingDashboard from './analytics/DocumentProcessingDashboard';
import UserJourneyDashboard from './analytics/UserJourneyDashboard';
import AIPerformanceDashboard from './analytics/AIPerformanceDashboard';
import BusinessIntelligenceDashboard from './analytics/BusinessIntelligenceDashboard';
import SystemHealthDashboard from './analytics/SystemHealthDashboard';

interface SystemHealthMetrics {
  overall_status: string;
  cpu_usage: number;
  memory_usage: number;
  active_requests: number;
  requests_per_minute: number;
  error_rate: number;
  services: Record<string, string>;
  alerts: string[];
}

interface QuickMetrics {
  documents_today: number;
  active_sessions: number;
  ai_requests_hour: number;
  system_health: SystemHealthMetrics;
  last_updated: string;
}

const AdvancedAnalytics = () => {
  const navigate = useNavigate();
  const [quickMetrics, setQuickMetrics] = useState<QuickMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState('7d');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchQuickMetrics();
    
    // Auto-refresh every 30 seconds if enabled
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(fetchQuickMetrics, 30000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const fetchQuickMetrics = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/analytics/system/realtime`);
      
      if (response.ok) {
        const data = await response.json();
        setQuickMetrics({
          documents_today: 25, // Would come from API
          active_sessions: data.system_health?.active_requests || 0,
          ai_requests_hour: Math.floor(data.system_health?.requests_per_minute * 60) || 0,
          system_health: {
            overall_status: data.system_health?.status || 'unknown',
            cpu_usage: data.system_health?.cpu_usage || 0,
            memory_usage: data.system_health?.memory_usage || 0,
            active_requests: data.system_health?.active_requests || 0,
            requests_per_minute: data.system_health?.requests_per_minute || 0,
            error_rate: data.system_health?.error_rate || 0,
            services: data.services || {},
            alerts: data.alerts || []
          },
          last_updated: data.timestamp
        });
      } else {
        setError('Failed to fetch metrics');
      }
    } catch (error) {
      console.error('Metrics fetch error:', error);
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
      'unknown': 'bg-gray-100 text-gray-800 border-gray-200'
    };
    return colors[status as keyof typeof colors] || colors.unknown;
  };

  const getStatusIcon = (status: string) => {
    const icons = {
      'healthy': CheckCircle,
      'warning': AlertTriangle,
      'degraded': AlertTriangle,
      'critical': AlertTriangle,
      'unknown': Clock
    };
    const IconComponent = icons[status as keyof typeof icons] || Clock;
    return <IconComponent className="h-4 w-4" />;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto"></div>
          <p className="text-gray-600">Carregando analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                <BarChart3 className="h-8 w-8" />
                Advanced Analytics
              </h1>
              <p className="text-gray-600 mt-1">
                Dashboards detalhados de performance e insights de negócio
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={autoRefresh ? 'bg-green-50 border-green-200' : ''}
              >
                <RefreshCw className={`h-4 w-4 ${autoRefresh ? 'animate-pulse' : ''}`} />
                Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
              </Button>
              
              <Button
                variant="outline"
                onClick={() => navigate('/dashboard')}
              >
                ← Voltar ao Dashboard
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Quick Overview Cards */}
        {quickMetrics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* System Health */}
            <Card className="bg-white border-0 shadow-md">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      quickMetrics.system_health.overall_status === 'healthy' ? 'bg-green-100' : 'bg-yellow-100'
                    }`}>
                      {getStatusIcon(quickMetrics.system_health.overall_status)}
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">System Status</div>
                      <div className="text-lg font-semibold text-gray-900">
                        {quickMetrics.system_health.overall_status.toUpperCase()}
                      </div>
                    </div>
                  </div>
                  <Badge className={getStatusColor(quickMetrics.system_health.overall_status)}>
                    {quickMetrics.system_health.alerts.length} alerts
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* Documents Today */}
            <Card className="bg-white border-0 shadow-md">
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <FileText className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Docs Processados Hoje</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {quickMetrics.documents_today}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Active Sessions */}
            <Card className="bg-white border-0 shadow-md">
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Users className="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Sessões Ativas</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {quickMetrics.active_sessions}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* AI Requests/Hour */}
            <Card className="bg-white border-0 shadow-md">
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                    <Brain className="h-5 w-5 text-orange-600" />
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Requests IA/Hora</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {quickMetrics.ai_requests_hour}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Analytics Tabs */}
        <Tabs defaultValue="documents" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 bg-white border border-gray-200 p-1">
            <TabsTrigger 
              value="documents" 
              className="flex items-center gap-2 data-[state=active]:bg-black data-[state=active]:text-white"
            >
              <FileText className="h-4 w-4" />
              Documentos
            </TabsTrigger>
            <TabsTrigger 
              value="journey"
              className="flex items-center gap-2 data-[state=active]:bg-black data-[state=active]:text-white"
            >
              <TrendingUp className="h-4 w-4" />
              Jornada
            </TabsTrigger>
            <TabsTrigger 
              value="ai"
              className="flex items-center gap-2 data-[state=active]:bg-black data-[state=active]:text-white"
            >
              <Brain className="h-4 w-4" />
              IA Performance
            </TabsTrigger>
            <TabsTrigger 
              value="business"
              className="flex items-center gap-2 data-[state=active]:bg-black data-[state=active]:text-white"
            >
              <PieChart className="h-4 w-4" />
              Business
            </TabsTrigger>
            <TabsTrigger 
              value="system"
              className="flex items-center gap-2 data-[state=active]:bg-black data-[state=active]:text-white"
            >
              <Activity className="h-4 w-4" />
              Sistema
            </TabsTrigger>
          </TabsList>

          {/* Document Processing Analytics */}
          <TabsContent value="documents" className="space-y-6">
            <DocumentProcessingDashboard period={selectedPeriod} />
          </TabsContent>

          {/* User Journey Analytics */}
          <TabsContent value="journey" className="space-y-6">
            <UserJourneyDashboard period={selectedPeriod} />
          </TabsContent>

          {/* AI Performance Analytics */}
          <TabsContent value="ai" className="space-y-6">
            <AIPerformanceDashboard period={selectedPeriod} />
          </TabsContent>

          {/* Business Intelligence */}
          <TabsContent value="business" className="space-y-6">
            <BusinessIntelligenceDashboard period={selectedPeriod} />
          </TabsContent>

          {/* System Health & Real-time Monitoring */}
          <TabsContent value="system" className="space-y-6">
            <SystemHealthDashboard realTimeData={quickMetrics} />
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-gray-500">
          <p>
            Last updated: {quickMetrics?.last_updated ? 
              new Date(quickMetrics.last_updated).toLocaleString('pt-BR') : 
              'Never'
            }
          </p>
          <p className="mt-1">
            Advanced Analytics powered by OSPREY Intelligence Engine
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdvancedAnalytics;