import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Users, 
  CheckCircle2, 
  TrendingUp,
  Calendar,
  Award,
  Lightbulb,
  BarChart3,
  Info,
  ExternalLink,
  Heart
} from 'lucide-react';

interface SuccessCase {
  id: string;
  name_initial: string;
  age: number;
  country: string;
  situation: string;
  timeline_months: number;
  status: string;
  completeness_score: number;
  testimonial: string;
  top_tip: string;
  challenges: string;
  documents_key: string;
  approval_date: string;
}

interface Statistics {
  total_cases: number;
  avg_timeline_months: number;
  approval_rate: number;
  avg_completeness: number;
  common_rfe_reasons?: string[];
  timeline_distribution?: Record<string, number>;
  success_factors?: string[];
}

interface SocialProofDisplayProps {
  visaType: string;
  userProfile?: {
    country?: string;
    age?: number;
    situation?: string;
  };
  showStatistics?: boolean;
  limit?: number;
}

export const SocialProofDisplay: React.FC<SocialProofDisplayProps> = ({
  visaType,
  userProfile,
  showStatistics = true,
  limit = 3
}) => {
  const [cases, setCases] = useState<SuccessCase[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCase, setSelectedCase] = useState<string | null>(null);

  const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://agente-coruja-1.preview.emergentagent.com';

  useEffect(() => {
    if (visaType) {
      fetchSimilarCases();
      if (showStatistics) {
        fetchStatistics();
      }
    }
  }, [visaType, userProfile]);

  const fetchSimilarCases = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${backendUrl}/api/social-proof/similar-cases`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          visa_type: visaType,
          user_profile: userProfile,
          limit: limit
        })
      });

      if (!response.ok) {
        throw new Error('Falha ao carregar casos similares');
      }

      const data = await response.json();
      setCases(data.cases || []);
      if (data.statistics) {
        setStatistics(data.statistics);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/social-proof/statistics/${visaType}`);
      
      if (!response.ok) return;

      const data = await response.json();
      if (data.success) {
        setStatistics(data.statistics);
      }
    } catch (err) {
      console.error('Error fetching statistics:', err);
    }
  };

  const getStatusColor = (status: string) => {
    return status === 'approved' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800';
  };

  const getApprovalRateColor = (rate: number) => {
    if (rate >= 85) return 'text-green-600';
    if (rate >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center space-x-2">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span>Carregando casos similares...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert className="border-red-200 bg-red-50">
        <Info className="h-4 w-4" />
        <AlertTitle>Erro</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!cases || cases.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* Header Stats */}
      <Card className="border-2 border-blue-200 bg-blue-50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2 text-blue-900">
                <Users className="w-5 h-5" />
                <span>Pessoas Como Você</span>
              </CardTitle>
              <CardDescription className="text-blue-700 mt-2">
                {statistics && `${statistics.total_cases.toLocaleString()} pessoas já completaram ${visaType} com sucesso`}
              </CardDescription>
            </div>
            {statistics && (
              <div className="text-center">
                <div className={`text-4xl font-bold ${getApprovalRateColor(statistics.approval_rate)}`}>
                  {statistics.approval_rate}%
                </div>
                <div className="text-sm text-gray-600">Taxa de Aprovação</div>
              </div>
            )}
          </div>
        </CardHeader>
      </Card>

      <Tabs defaultValue="cases" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="cases">
            <Heart className="w-4 h-4 mr-2" />
            Histórias de Sucesso
          </TabsTrigger>
          <TabsTrigger value="stats">
            <BarChart3 className="w-4 h-4 mr-2" />
            Estatísticas
          </TabsTrigger>
        </TabsList>

        <TabsContent value="cases" className="space-y-4">
          {/* Success Stories */}
          {cases.map((caseData) => (
            <Card 
              key={caseData.id}
              className={`border-2 transition-all cursor-pointer ${
                selectedCase === caseData.id 
                  ? 'border-blue-500 shadow-lg' 
                  : 'border-gray-200 hover:border-blue-300'
              }`}
              onClick={() => setSelectedCase(selectedCase === caseData.id ? null : caseData.id)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-2xl">{caseData.country}</span>
                      <CardTitle className="text-lg">{caseData.name_initial}, {caseData.age} anos</CardTitle>
                      <Badge className={getStatusColor(caseData.status)}>
                        <CheckCircle2 className="w-3 h-3 mr-1" />
                        APROVADO
                      </Badge>
                    </div>
                    <CardDescription className="text-base">
                      {caseData.situation}
                    </CardDescription>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center space-x-1 text-sm text-gray-600">
                      <Calendar className="w-4 h-4" />
                      <span>{caseData.timeline_months} meses</span>
                    </div>
                    <div className="flex items-center space-x-1 text-sm text-gray-600 mt-1">
                      <Award className="w-4 h-4" />
                      <span>{caseData.completeness_score}% completo</span>
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                {/* Testimonial */}
                <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded mb-4">
                  <p className="text-sm italic text-gray-700">
                    "{caseData.testimonial}"
                  </p>
                </div>

                {/* Expanded Details */}
                {selectedCase === caseData.id && (
                  <div className="space-y-4 mt-4 pt-4 border-t">
                    {/* Top Tip */}
                    <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
                      <div className="flex items-start space-x-2">
                        <Lightbulb className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="font-medium text-yellow-900 mb-1">Dica Principal:</p>
                          <p className="text-sm text-yellow-800">{caseData.top_tip}</p>
                        </div>
                      </div>
                    </div>

                    {/* Challenges */}
                    <div>
                      <p className="font-medium text-gray-900 mb-2">Maior Desafio:</p>
                      <p className="text-sm text-gray-700">{caseData.challenges}</p>
                    </div>

                    {/* Key Documents */}
                    <div>
                      <p className="font-medium text-gray-900 mb-2">Documentos Chave:</p>
                      <p className="text-sm text-gray-700">{caseData.documents_key}</p>
                    </div>

                    {/* Approval Date */}
                    <div className="text-xs text-gray-500">
                      Aprovado em: {new Date(caseData.approval_date).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}
                    </div>
                  </div>
                )}

                {selectedCase !== caseData.id && (
                  <Button variant="link" className="p-0 h-auto text-blue-600">
                    Ver história completa →
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="stats" className="space-y-4">
          {statistics && (
            <>
              {/* Timeline Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Calendar className="w-5 h-5" />
                    <span>Tempo de Processamento</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center mb-6">
                    <div className="text-4xl font-bold text-blue-600">
                      {statistics.avg_timeline_months} meses
                    </div>
                    <div className="text-sm text-gray-600">Tempo médio</div>
                  </div>

                  {statistics.timeline_distribution && (
                    <div className="space-y-3">
                      {Object.entries(statistics.timeline_distribution).map(([range, percentage]) => (
                        <div key={range}>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm text-gray-700">{range}</span>
                            <span className="text-sm font-medium">{percentage}%</span>
                          </div>
                          <Progress value={percentage} className="h-2" />
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Success Factors */}
              {statistics.success_factors && statistics.success_factors.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <TrendingUp className="w-5 h-5 text-green-600" />
                      <span>O Que Aumenta Suas Chances</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {statistics.success_factors.map((factor, idx) => (
                        <div key={idx} className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                          <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                          <p className="text-sm text-gray-700">{factor}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Common Issues */}
              {statistics.common_rfe_reasons && statistics.common_rfe_reasons.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Info className="w-5 h-5 text-yellow-600" />
                      <span>Problemas Mais Comuns (RFEs)</span>
                    </CardTitle>
                    <CardDescription>
                      Evite estes erros para não receber pedido de mais documentos
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {statistics.common_rfe_reasons.map((reason, idx) => (
                        <div key={idx} className="flex items-start space-x-2 text-sm text-gray-700">
                          <span className="text-yellow-600 font-bold">•</span>
                          <span>{reason}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Overall Stats */}
              <Card className="bg-gradient-to-br from-blue-50 to-green-50">
                <CardContent className="pt-6">
                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div>
                      <div className="text-3xl font-bold text-blue-600">
                        {statistics.total_cases.toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-600">Casos Analisados</div>
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-green-600">
                        {statistics.avg_completeness}%
                      </div>
                      <div className="text-sm text-gray-600">Completude Média</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>
      </Tabs>

      {/* CTA */}
      <Alert className="border-blue-200 bg-blue-50">
        <Info className="h-4 w-4" />
        <AlertTitle>💡 Inspirado por essas histórias?</AlertTitle>
        <AlertDescription>
          Complete sua aplicação com atenção aos detalhes e você pode ser a próxima história de sucesso!
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default SocialProofDisplay;
