import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Brain, 
  Zap, 
  Clock, 
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  Activity,
  Target
} from "lucide-react";

interface ModelPerformance {
  total_requests: number;
  average_response_time_ms: number;
  median_response_time_ms: number;
  success_rate: number;
  average_confidence_score?: number;
  p95_response_time_ms: number;
  error_count: number;
  requests_by_type: Record<string, number>;
}

interface AIAnalytics {
  total_requests: number;
  average_response_time_ms: number;
  success_rate: number;
  model_performance: Record<string, ModelPerformance>;
  error_distribution: Record<string, number>;
}

const AIPerformanceDashboard: React.FC<{ period: string }> = ({ period }) => {
  const [analytics, setAnalytics] = useState<AIAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAIAnalytics();
  }, [period]);

  const fetchAIAnalytics = async () => {
    setIsLoading(true);
    try {
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - (parseInt(period.replace('d', '')) * 24 * 60 * 60 * 1000))
        .toISOString().split('T')[0];

      const query = {
        start_date: startDate,
        end_date: endDate,
        group_by: 'model',
        metrics: ['response_time', 'success_rate', 'error_distribution']
      };

      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/analytics/ai/analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(query),
      });

      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      } else {
        // Mock data for development
        setAnalytics({
          total_requests: 15420,
          average_response_time_ms: 1850,
          success_rate: 96.8,
          model_performance: {
            'dr_paula': {
              total_requests: 5200,
              average_response_time_ms: 2100,
              median_response_time_ms: 1800,
              success_rate: 97.5,
              average_confidence_score: 0.89,
              p95_response_time_ms: 4200,
              error_count: 130,
              requests_by_type: { 'cover_letter': 3200, 'consultation': 2000 }
            },
            'document_validator': {
              total_requests: 8200,
              average_response_time_ms: 1600,
              median_response_time_ms: 1200,
              success_rate: 96.2,
              average_confidence_score: 0.85,
              p95_response_time_ms: 3100,
              error_count: 312,
              requests_by_type: { 'validation': 8200 }
            },
            'ocr_engine': {
              total_requests: 2020,
              average_response_time_ms: 1850,
              median_response_time_ms: 1400,
              success_rate: 97.1,
              average_confidence_score: 0.82,
              p95_response_time_ms: 3800,
              error_count: 59,
              requests_by_type: { 'text_extraction': 2020 }
            }
          },
          error_distribution: {
            'timeout': 145,
            'api_limit': 89,
            'validation_error': 167,
            'network_error': 100
          }
        });
      }
    } catch (error) {
      console.error('AI analytics error:', error);
      setError('Connection error');
    } finally {
      setIsLoading(false);
    }
  };

  const getModelName = (model: string) => {
    const names = {
      'dr_paula': 'Dra. Paula (Immigration Expert)',
      'document_validator': 'Document Validator',
      'ocr_engine': 'OCR Engine',
      'translation_service': 'Translation Service'
    };
    return names[model as keyof typeof names] || model;
  };

  const getPerformanceColor = (value: number, type: 'time' | 'success') => {
    if (type === 'time') {
      if (value < 1000) return 'text-green-600';
      if (value < 3000) return 'text-yellow-600';
      return 'text-red-600';
    }
    if (value >= 95) return 'text-green-600';
    if (value >= 90) return 'text-yellow-600';
    return 'text-red-600';
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

  if (error || !analytics) {
    return (
      <Card className="bg-white border-0 shadow-md">
        <CardContent className="p-6 text-center">
          <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading AI Analytics</h3>
          <p className="text-gray-600">{error || 'Failed to load AI performance analytics'}</p>
          <Button onClick={fetchAIAnalytics} className="mt-4">Retry</Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* AI Performance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-white border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Brain className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {analytics.total_requests.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Total AI Requests</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Zap className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <div className={`text-2xl font-bold ${getPerformanceColor(analytics.average_response_time_ms, 'time')}`}>
                  {(analytics.average_response_time_ms / 1000).toFixed(1)}s
                </div>
                <div className="text-sm text-gray-600">Avg Response Time</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <div className={`text-2xl font-bold ${getPerformanceColor(analytics.success_rate, 'success')}`}>
                  {analytics.success_rate.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Success Rate</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Activity className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {Object.keys(analytics.model_performance).length}
                </div>
                <div className="text-sm text-gray-600">Active Models</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Model Performance Breakdown */}
      <Card className="bg-white border-0 shadow-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Model Performance Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {Object.entries(analytics.model_performance).map(([model, performance]) => (
              <div key={model} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h4 className="font-semibold text-gray-900">{getModelName(model)}</h4>
                    <p className="text-sm text-gray-600">
                      {performance.total_requests.toLocaleString()} requests processed
                    </p>
                  </div>
                  <Badge 
                    variant="outline" 
                    className={`${getPerformanceColor(performance.success_rate, 'success')} border-current`}
                  >
                    {performance.success_rate.toFixed(1)}% success
                  </Badge>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="text-center">
                    <div className={`text-lg font-semibold ${getPerformanceColor(performance.average_response_time_ms, 'time')}`}>
                      {(performance.average_response_time_ms / 1000).toFixed(1)}s
                    </div>
                    <div className="text-xs text-gray-500">Avg Response</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {(performance.median_response_time_ms / 1000).toFixed(1)}s
                    </div>
                    <div className="text-xs text-gray-500">Median Response</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {(performance.p95_response_time_ms / 1000).toFixed(1)}s
                    </div>
                    <div className="text-xs text-gray-500">95th Percentile</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {performance.average_confidence_score ? 
                        `${(performance.average_confidence_score * 100).toFixed(1)}%` : 
                        'N/A'}
                    </div>
                    <div className="text-xs text-gray-500">Confidence</div>
                  </div>
                </div>

                {/* Request Type Distribution */}
                {Object.keys(performance.requests_by_type).length > 1 && (
                  <div className="space-y-2">
                    <h5 className="text-sm font-medium text-gray-700">Request Types</h5>
                    {Object.entries(performance.requests_by_type).map(([type, count]) => {
                      const percentage = (count / performance.total_requests) * 100;
                      return (
                        <div key={type} className="flex justify-between items-center">
                          <span className="text-sm text-gray-600 capitalize">{type.replace('_', ' ')}</span>
                          <div className="flex items-center gap-2">
                            <Progress value={percentage} className="h-2 w-20" />
                            <span className="text-xs text-gray-500 w-12">{percentage.toFixed(1)}%</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Error Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-white border-0 shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Error Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(analytics.error_distribution)
                .sort(([,a], [,b]) => b - a)
                .map(([errorType, count]) => {
                  const totalErrors = Object.values(analytics.error_distribution).reduce((a, b) => a + b, 0);
                  const percentage = (count / totalErrors) * 100;
                  
                  return (
                    <div key={errorType} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-gray-900 capitalize">
                          {errorType.replace('_', ' ')}
                        </span>
                        <span className="text-sm text-gray-600">
                          {count} errors ({percentage.toFixed(1)}%)
                        </span>
                      </div>
                      <Progress value={percentage} className="h-2" />
                    </div>
                  );
                })}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-0 shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Performance Targets
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Response Time Target */}
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Response Time Target</span>
                  <span className="text-xs text-gray-500">&lt; 2.0s</span>
                </div>
                <Progress 
                  value={Math.min((2000 / analytics.average_response_time_ms) * 100, 100)} 
                  className="h-2" 
                />
                <div className="text-xs text-gray-600 mt-1">
                  Current: {(analytics.average_response_time_ms / 1000).toFixed(1)}s
                </div>
              </div>

              {/* Success Rate Target */}
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Success Rate Target</span>
                  <span className="text-xs text-gray-500">{'≥ 98%'}</span>
                </div>
                <Progress value={analytics.success_rate} className="h-2" />
                <div className="text-xs text-gray-600 mt-1">
                  Current: {analytics.success_rate.toFixed(1)}%
                </div>
              </div>

              {/* Error Rate Target */}
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Error Rate Target</span>
                  <span className="text-xs text-gray-500">{'< 2%'}</span>
                </div>
                <Progress 
                  value={Math.max(100 - (100 - analytics.success_rate) * 50, 0)} 
                  className="h-2" 
                />
                <div className="text-xs text-gray-600 mt-1">
                  Current: {(100 - analytics.success_rate).toFixed(1)}%
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Performance Insights */}
      <Card className="bg-white border-0 shadow-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Performance Insights & Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {analytics.average_response_time_ms > 2000 && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <Clock className="h-5 w-5 text-yellow-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-yellow-800">Response Time Alert</h4>
                    <p className="text-sm text-yellow-700 mt-1">
                      Average response time ({(analytics.average_response_time_ms / 1000).toFixed(1)}s) 
                      exceeds target. Consider optimizing model inference or adding caching.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {analytics.success_rate < 95 && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-red-800">Success Rate Alert</h4>
                    <p className="text-sm text-red-700 mt-1">
                      Success rate ({analytics.success_rate.toFixed(1)}%) is below target. 
                      Review error patterns and improve error handling.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {analytics.success_rate >= 96 && analytics.average_response_time_ms <= 2000 && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-green-800">Excellent AI Performance!</h4>
                    <p className="text-sm text-green-700 mt-1">
                      All AI models are performing within target parameters. 
                      Great job maintaining high accuracy and fast response times!
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIPerformanceDashboard;