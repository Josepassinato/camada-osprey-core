import { useState, useEffect } from "react";
import { BarChart3, TrendingUp, Zap, Target, Users } from "lucide-react";

interface ABTestingData {
  pipeline: {
    total_documents: number;
    success_rate: number;
    avg_processing_time_ms: number;
    avg_confidence_pct: number;
  };
  legacy: {
    total_documents: number;
    success_rate: number;
    avg_processing_time_ms: number;
    avg_confidence_pct: number;
  };
  improvements: {
    processing_time_improvement_pct: number;
    confidence_improvement_points: number;
    success_rate_improvement_points: number;
  };
  test_config: {
    pipeline_enabled: boolean;
    pipeline_percentage: number;
    force_pipeline_for_passports: boolean;
  };
}

const ABTestingDashboard = () => {
  const [abData, setAbData] = useState<ABTestingData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchABData = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/ab-testing/comparison`);
        if (response.ok) {
          const data = await response.json();
          setAbData(data);
        }
      } catch (error) {
        console.error("Error fetching A/B testing data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchABData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchABData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!abData) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
          <Users className="h-5 w-5" />
          A/B Testing - Indisponível
        </h3>
        <p className="text-muted-foreground">Sistema de A/B testing não disponível.</p>
      </div>
    );
  }

  const totalDocuments = abData.pipeline.total_documents + abData.legacy.total_documents;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
          <Users className="h-5 w-5 text-blue-500" />
          A/B Testing: Pipeline vs Legacy
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{abData.pipeline.total_documents}</div>
            <div className="text-sm text-muted-foreground">Pipeline</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-600">{abData.legacy.total_documents}</div>
            <div className="text-sm text-muted-foreground">Legacy</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{totalDocuments}</div>
            <div className="text-sm text-muted-foreground">Total</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{abData.test_config.pipeline_percentage}%</div>
            <div className="text-sm text-muted-foreground">Pipeline Split</div>
          </div>
        </div>

        {/* Test Configuration */}
        <div className="flex flex-wrap gap-2">
          <span className={`px-2 py-1 text-xs rounded ${abData.test_config.pipeline_enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            Pipeline: {abData.test_config.pipeline_enabled ? 'Ativo' : 'Inativo'}
          </span>
          <span className={`px-2 py-1 text-xs rounded ${abData.test_config.force_pipeline_for_passports ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
            Passaportes: {abData.test_config.force_pipeline_for_passports ? 'Força Pipeline' : 'A/B Normal'}
          </span>
        </div>
      </div>

      {/* Performance Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Success Rate */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-foreground">Taxa de Sucesso</h4>
            <Target className="h-5 w-5 text-green-500" />
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-blue-600">Pipeline</span>
              <span className="font-bold text-blue-600">
                {(abData.pipeline.success_rate * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Legacy</span>
              <span className="font-bold text-gray-600">
                {(abData.legacy.success_rate * 100).toFixed(1)}%
              </span>
            </div>
            <div className="pt-2 border-t">
              <div className={`text-sm font-medium ${abData.improvements.success_rate_improvement_points >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {abData.improvements.success_rate_improvement_points >= 0 ? '+' : ''}
                {abData.improvements.success_rate_improvement_points.toFixed(1)} pontos
              </div>
            </div>
          </div>
        </div>

        {/* Processing Time */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-foreground">Tempo de Processamento</h4>
            <Zap className="h-5 w-5 text-yellow-500" />
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-blue-600">Pipeline</span>
              <span className="font-bold text-blue-600">
                {abData.pipeline.avg_processing_time_ms.toFixed(0)}ms
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Legacy</span>
              <span className="font-bold text-gray-600">
                {abData.legacy.avg_processing_time_ms.toFixed(0)}ms
              </span>
            </div>
            <div className="pt-2 border-t">
              <div className={`text-sm font-medium ${abData.improvements.processing_time_improvement_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {abData.improvements.processing_time_improvement_pct >= 0 ? '+' : ''}
                {abData.improvements.processing_time_improvement_pct.toFixed(1)}% melhor
              </div>
            </div>
          </div>
        </div>

        {/* Confidence */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-foreground">Confiança Média</h4>
            <TrendingUp className="h-5 w-5 text-purple-500" />
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-blue-600">Pipeline</span>
              <span className="font-bold text-blue-600">
                {abData.pipeline.avg_confidence_pct.toFixed(1)}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Legacy</span>
              <span className="font-bold text-gray-600">
                {abData.legacy.avg_confidence_pct.toFixed(1)}%
              </span>
            </div>
            <div className="pt-2 border-t">
              <div className={`text-sm font-medium ${abData.improvements.confidence_improvement_points >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {abData.improvements.confidence_improvement_points >= 0 ? '+' : ''}
                {abData.improvements.confidence_improvement_points.toFixed(1)} pontos
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Summary */}
      {totalDocuments > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200 p-6">
          <h4 className="font-semibold text-foreground mb-3 flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Resumo do Teste A/B
          </h4>
          <div className="text-sm text-muted-foreground space-y-1">
            <p>• <strong>{totalDocuments} documentos</strong> processados no teste A/B</p>
            <p>• Pipeline modular processou <strong>{abData.pipeline.total_documents} documentos</strong></p>
            <p>• Sistema legado processou <strong>{abData.legacy.total_documents} documentos</strong></p>
            {abData.improvements.success_rate_improvement_points > 0 && (
              <p>• Pipeline tem <strong>{abData.improvements.success_rate_improvement_points.toFixed(1)} pontos</strong> melhor taxa de sucesso</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ABTestingDashboard;