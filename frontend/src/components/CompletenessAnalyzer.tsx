import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  AlertTriangle, 
  CheckCircle2, 
  AlertCircle, 
  Info,
  ChevronDown,
  ChevronUp,
  FileText,
  Shield
} from 'lucide-react';

interface FieldAnalysis {
  field: string;
  quality: string;
  score: number;
  feedback: string;
  suggestion: string;
  uscis_requirement: string;
}

interface CategoryAnalysis {
  category: string;
  category_key: string;
  description: string;
  score: number;
  fields_analyzed: number;
  field_details: FieldAnalysis[];
}

interface Issue {
  field: string;
  category: string;
  issue: string;
  suggestion: string;
}

interface Recommendation {
  priority: string;
  title: string;
  description: string;
  action: string;
}

interface CompletenessAnalysis {
  overall_score: number;
  level: 'critical' | 'warning' | 'good';
  level_message: string;
  level_description: string;
  visa_type: string;
  visa_name: string;
  total_fields_analyzed: number;
  critical_issues_count: number;
  warnings_count: number;
  categories: CategoryAnalysis[];
  critical_issues: Issue[];
  warnings: Issue[];
  recommendations: Recommendation[];
  analyzed_at: string;
  disclaimer: string;
}

interface CompletenessAnalyzerProps {
  visaType: string;
  userData: Record<string, any>;
  onAnalysisComplete?: (analysis: CompletenessAnalysis) => void;
  autoAnalyze?: boolean;
}

export const CompletenessAnalyzer: React.FC<CompletenessAnalyzerProps> = ({
  visaType,
  userData,
  onAnalysisComplete,
  autoAnalyze = true
}) => {
  const [analysis, setAnalysis] = useState<CompletenessAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [showDetails, setShowDetails] = useState(false);

  const backendUrl = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    if (autoAnalyze && visaType && userData) {
      analyzeCompleteness();
    }
  }, [visaType, userData, autoAnalyze]);

  const analyzeCompleteness = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${backendUrl}/api/analyze-completeness`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          visa_type: visaType,
          user_data: userData,
          context: 'User application form'
        })
      });

      if (!response.ok) {
        throw new Error('Falha ao analisar completude');
      }

      const data = await response.json();
      setAnalysis(data.analysis);
      
      if (onAnalysisComplete) {
        onAnalysisComplete(data.analysis);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleCategory = (categoryKey: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryKey)) {
      newExpanded.delete(categoryKey);
    } else {
      newExpanded.add(categoryKey);
    }
    setExpandedCategories(newExpanded);
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'good': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'critical': return <AlertCircle className="w-5 h-5" />;
      case 'warning': return <AlertTriangle className="w-5 h-5" />;
      case 'good': return <CheckCircle2 className="w-5 h-5" />;
      default: return <Info className="w-5 h-5" />;
    }
  };

  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'missing': return 'bg-red-100 text-red-800';
      case 'incomplete': return 'bg-orange-100 text-orange-800';
      case 'vague': return 'bg-yellow-100 text-yellow-800';
      case 'adequate': return 'bg-blue-100 text-blue-800';
      case 'complete': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center space-x-2">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span>Analisando completude da aplicação...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Erro na Análise</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!analysis) {
    return (
      <Card>
        <CardContent className="p-6">
          <Button onClick={analyzeCompleteness}>
            Analisar Completude
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Score Geral */}
      <Card className={`border-2 ${getLevelColor(analysis.level)}`}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getLevelIcon(analysis.level)}
              <CardTitle className="text-xl">{analysis.level_message}</CardTitle>
            </div>
            <div className="text-3xl font-bold">{analysis.overall_score}%</div>
          </div>
          <CardDescription className="text-base mt-2">
            {analysis.level_description}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Progress value={analysis.overall_score} className="h-3" />
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold">{analysis.total_fields_analyzed}</div>
              <div className="text-sm text-gray-600">Campos Analisados</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-600">{analysis.critical_issues_count}</div>
              <div className="text-sm text-gray-600">Problemas Críticos</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-600">{analysis.warnings_count}</div>
              <div className="text-sm text-gray-600">Avisos</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recomendações */}
      {analysis.recommendations && analysis.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileText className="w-5 h-5" />
              <span>Recomendações</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {analysis.recommendations.map((rec, idx) => (
              <Alert key={idx} className="border-blue-200 bg-blue-50">
                <Info className="h-4 w-4" />
                <AlertTitle className="flex items-center justify-between">
                  <span>{rec.title}</span>
                  <Badge className={getPriorityColor(rec.priority)}>
                    {rec.priority === 'high' ? 'Alta' : rec.priority === 'medium' ? 'Média' : 'Baixa'}
                  </Badge>
                </AlertTitle>
                <AlertDescription className="mt-2">
                  <p>{rec.description}</p>
                  <p className="mt-2 font-medium">→ {rec.action}</p>
                </AlertDescription>
              </Alert>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Problemas Críticos */}
      {analysis.critical_issues && analysis.critical_issues.length > 0 && (
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-red-600">
              <AlertCircle className="w-5 h-5" />
              <span>Informações Obrigatórias Faltando</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {analysis.critical_issues.map((issue, idx) => (
              <div key={idx} className="p-4 bg-red-50 rounded-lg border border-red-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="font-medium text-red-900">
                      {issue.category} - {issue.field}
                    </div>
                    <div className="text-sm text-red-700 mt-1">{issue.issue}</div>
                    <div className="mt-2 p-2 bg-white rounded border border-red-300">
                      <div className="text-sm font-medium text-gray-700">💡 Sugestão:</div>
                      <div className="text-sm text-gray-600 mt-1">{issue.suggestion}</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Avisos */}
      {analysis.warnings && analysis.warnings.length > 0 && (
        <Card className="border-yellow-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-yellow-600">
              <AlertTriangle className="w-5 h-5" />
              <span>Campos que Podem Ser Melhorados</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {analysis.warnings.map((warning, idx) => (
              <div key={idx} className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="font-medium text-yellow-900">
                      {warning.category} - {warning.field}
                    </div>
                    <div className="text-sm text-yellow-700 mt-1">{warning.issue}</div>
                    <div className="mt-2 p-2 bg-white rounded border border-yellow-300">
                      <div className="text-sm font-medium text-gray-700">💡 Sugestão:</div>
                      <div className="text-sm text-gray-600 mt-1">{warning.suggestion}</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Detalhes por Categoria */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Análise Detalhada por Categoria</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowDetails(!showDetails)}
            >
              {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              {showDetails ? 'Ocultar' : 'Mostrar'} Detalhes
            </Button>
          </div>
        </CardHeader>
        {showDetails && (
          <CardContent className="space-y-4">
            {analysis.categories.map((category) => (
              <div key={category.category_key} className="border rounded-lg overflow-hidden">
                <button
                  onClick={() => toggleCategory(category.category_key)}
                  className="w-full p-4 bg-gray-50 hover:bg-gray-100 transition-colors text-left flex items-center justify-between"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium">{category.category}</span>
                      <Badge variant="outline">{category.score}%</Badge>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">{category.description}</div>
                  </div>
                  {expandedCategories.has(category.category_key) ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </button>
                
                {expandedCategories.has(category.category_key) && (
                  <div className="p-4 space-y-3 bg-white">
                    {category.field_details.map((field, idx) => (
                      <div key={idx} className="p-3 border rounded">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-sm">{field.field}</span>
                          <Badge className={getQualityColor(field.quality)}>
                            {field.quality}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-600 mb-2">{field.feedback}</div>
                        {field.quality !== 'complete' && (
                          <div className="p-2 bg-blue-50 rounded text-sm">
                            <div className="font-medium text-blue-900">💡 {field.suggestion}</div>
                            <div className="text-blue-700 mt-1">
                              📚 USCIS requer: {field.uscis_requirement}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        )}
      </Card>

      {/* Disclaimer */}
      <Alert className="border-gray-200 bg-gray-50">
        <Shield className="h-4 w-4" />
        <AlertTitle>Aviso Importante</AlertTitle>
        <AlertDescription className="text-xs">
          {analysis.disclaimer}
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default CompletenessAnalyzer;
