import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  TrendingUp,
  Zap,
  Target,
  BarChart3
} from "lucide-react";

interface ValidatorPerformance {
  validator: string;
  total_processed: number;
  average_processing_time_ms: number;
  average_confidence_score: number;
  success_rate: number;
  average_fields_extracted: number;
  common_issues: [string, number][];
}

interface DocumentAnalytics {
  total_documents_processed: number;
  average_processing_time_ms: number;
  average_confidence_score: number;
  success_rate: number;
  validation_status_distribution: Record<string, number>;
  validator_performance: Record<string, ValidatorPerformance>;
  results: any[];
}

interface DocumentProcessingDashboardProps {
  period: string;
}

const DocumentProcessingDashboard: React.FC<DocumentProcessingDashboardProps> = ({ period }) => {
  const [analytics, setAnalytics] = useState<DocumentAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedValidator, setSelectedValidator] = useState<string | null>(null);

  useEffect(() => {
    fetchDocumentAnalytics();
  }, [period]);

  const fetchDocumentAnalytics = async () => {
    setIsLoading(true);
    try {
      // Calculate date range based on period
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - (parseInt(period.replace('d', '')) * 24 * 60 * 60 * 1000))
        .toISOString().split('T')[0];

      const query = {
        start_date: startDate,
        end_date: endDate,
        group_by: 'validator',
        metrics: ['processing_time', 'confidence_score', 'success_rate']
      };

      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/analytics/documents/analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(query),
      });

      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      } else {
        setError('Failed to fetch document analytics');
      }
    } catch (error) {
      console.error('Document analytics error:', error);
      setError('Connection error');
    } finally {
      setIsLoading(false);
    }
  };

  const getValidatorName = (validator: string) => {
    const names = {
      'social_security_card': 'Social Security Card',
      'tax_documents': 'Tax Documents',
      'medical_records': 'Medical Records',
      'utility_bills': 'Utility Bills',
      'passport': 'Passport',
      'birth_certificate': 'Birth Certificate',
      'i765': 'I-765 EAD',
      'driver_license': 'Driver License',
      'marriage_certificate': 'Marriage Certificate'
    };
    return names[validator as keyof typeof names] || validator;
  };

  const getPerformanceColor = (value: number, type: 'time' | 'confidence' | 'success') => {
    if (type === 'time') {
      if (value < 3000) return 'text-green-600';
      if (value < 8000) return 'text-yellow-600';
      return 'text-red-600';
    }
    if (type === 'confidence') {
      if (value >= 0.8) return 'text-green-600';
      if (value >= 0.6) return 'text-yellow-600';
      return 'text-red-600';
    }
    if (type === 'success') {
      if (value >= 90) return 'text-green-600';
      if (value >= 70) return 'text-yellow-600';
      return 'text-red-600';
    }
    return 'text-gray-600';
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
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Analytics</h3>
          <p className="text-gray-600">{error || 'Failed to load document processing analytics'}</p>
          <Button onClick={fetchDocumentAnalytics} className="mt-4">
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Documents */}
        <Card className="bg-white border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {analytics.total_documents_processed.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Documents Processed</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Average Processing Time */}
        <Card className="bg-white border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
              <div>
                <div className={`text-2xl font-bold ${getPerformanceColor(analytics.average_processing_time_ms, 'time')}`}>
                  {(analytics.average_processing_time_ms / 1000).toFixed(1)}s
                </div>
                <div className="text-sm text-gray-600">Avg Processing Time</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Average Confidence */}
        <Card className="bg-white border-0 shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Target className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <div className={`text-2xl font-bold ${getPerformanceColor(analytics.average_confidence_score, 'confidence')}`}>
                  {(analytics.average_confidence_score * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Avg Confidence</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Success Rate */}
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
      </div>

      {/* Validation Status Distribution */}
      <Card className="bg-white border-0 shadow-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Validation Status Distribution
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(analytics.validation_status_distribution).map(([status, count]) => {
              const percentage = (count / analytics.total_documents_processed) * 100;
              const statusColors = {
                'VALID': 'bg-green-500',
                'SUSPICIOUS': 'bg-yellow-500',
                'INVALID': 'bg-red-500'
              };
              
              return (
                <div key={status} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className={`${statusColors[status as keyof typeof statusColors]} text-white`}>
                        {status}
                      </Badge>
                      <span className="text-sm text-gray-600">{count} documents</span>
                    </div>
                    <span className="text-sm font-medium">{percentage.toFixed(1)}%</span>
                  </div>
                  <Progress value={percentage} className="h-2" />
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Validator Performance */}
      <Card className="bg-white border-0 shadow-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Validator Performance Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6">
            {Object.entries(analytics.validator_performance).map(([validator, performance]) => (
              <div 
                key={validator} 
                className={`p-4 rounded-lg border transition-all cursor-pointer ${
                  selectedValidator === validator 
                    ? 'border-black bg-gray-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedValidator(selectedValidator === validator ? null : validator)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-gray-900">{getValidatorName(validator)}</h4>
                    <p className="text-sm text-gray-600">
                      {performance.total_processed.toLocaleString()} documents processed
                    </p>
                  </div>
                  <Badge 
                    variant="outline" 
                    className={`${getPerformanceColor(performance.success_rate, 'success')} border-current`}
                  >
                    {performance.success_rate.toFixed(1)}% success
                  </Badge>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className={`text-lg font-semibold ${getPerformanceColor(performance.average_processing_time_ms, 'time')}`}>
                      {(performance.average_processing_time_ms / 1000).toFixed(1)}s
                    </div>
                    <div className="text-xs text-gray-500">Avg Time</div>
                  </div>
                  <div className="text-center">
                    <div className={`text-lg font-semibold ${getPerformanceColor(performance.average_confidence_score, 'confidence')}`}>
                      {(performance.average_confidence_score * 100).toFixed(1)}%
                    </div>
                    <div className="text-xs text-gray-500">Confidence</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {performance.average_fields_extracted.toFixed(1)}
                    </div>
                    <div className="text-xs text-gray-500">Fields Extracted</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {performance.common_issues.length}
                    </div>
                    <div className="text-xs text-gray-500">Common Issues</div>
                  </div>
                </div>

                {/* Expanded Details */}
                {selectedValidator === validator && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h5 className="font-medium text-gray-900 mb-2">Common Issues</h5>
                    <div className="space-y-2">
                      {performance.common_issues.slice(0, 5).map(([issue, count], index) => (
                        <div key={index} className="flex justify-between items-center text-sm">
                          <span className="text-gray-700">{issue}</span>
                          <Badge variant="outline" className="text-xs">
                            {count} occurrences
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Recommendations */}
      <Card className="bg-white border-0 shadow-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Performance Insights & Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Dynamic recommendations based on data */}
            {analytics.average_processing_time_ms > 5000 && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-yellow-800">Processing Time Alert</h4>
                    <p className="text-sm text-yellow-700 mt-1">
                      Average processing time is {(analytics.average_processing_time_ms / 1000).toFixed(1)}s, 
                      which is above the recommended 5s threshold. Consider optimizing OCR pipelines.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {analytics.average_confidence_score < 0.8 && (
              <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <Target className="h-5 w-5 text-orange-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-orange-800">Confidence Score Alert</h4>
                    <p className="text-sm text-orange-700 mt-1">
                      Average confidence score is {(analytics.average_confidence_score * 100).toFixed(1)}%, 
                      below the recommended 80%. Review document quality and OCR model tuning.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {analytics.success_rate < 90 && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-red-800">Success Rate Alert</h4>
                    <p className="text-sm text-red-700 mt-1">
                      Success rate is {analytics.success_rate.toFixed(1)}%, 
                      below the target 90%. Investigate validation failures and improve error handling.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Positive insights */}
            {analytics.success_rate >= 95 && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-green-800">Excellent Performance!</h4>
                    <p className="text-sm text-green-700 mt-1">
                      Success rate of {analytics.success_rate.toFixed(1)}% exceeds industry standards. 
                      Great job maintaining high validation accuracy!
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

export default DocumentProcessingDashboard;