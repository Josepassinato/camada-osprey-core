import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Eye, 
  Download,
  ChevronLeft,
  ChevronRight,
  Star,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  Loader2
} from "lucide-react";
import { makeApiCall } from "@/utils/api";

interface DocumentSummary {
  name: string;
  type: string;
  pages: number;
  quality?: number;
  status: 'included' | 'referenced' | 'missing' | 'error';
  note?: string;
  error?: string;
}

interface PacketMetadata {
  case_id: string;
  visa_type: string;
  generated_at: string;
  packet_statistics: {
    total_documents_uploaded: number;
    documents_included: number;
    total_pages: number;
    avg_quality_score: number;
    forms_completed: number;
    letters_generated: number;
  };
  quality_assessment: {
    overall_score: number;
    completeness: string;
    critical_issues: number;
    total_issues: number;
    recommendation: string;
  };
  document_breakdown: Record<string, any>;
}

interface PacketPreviewProps {
  caseId: string;
  jobId: string;
  onApprove: () => void;
  onReject: (reason: string) => void;
  onDownload: () => void;
}

const PacketPreview: React.FC<PacketPreviewProps> = ({
  caseId,
  jobId,
  onApprove,
  onReject,
  onDownload
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [metadata, setMetadata] = useState<PacketMetadata | null>(null);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [currentDocIndex, setCurrentDocIndex] = useState(0);
  const [approvalState, setApprovalState] = useState<'pending' | 'approved' | 'rejected'>('pending');
  const [rejectionReason, setRejectionReason] = useState('');
  const [comments, setComments] = useState('');

  useEffect(() => {
    fetchPacketPreview();
  }, [caseId, jobId]);

  const fetchPacketPreview = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await makeApiCall(`/cases/finalize/${jobId}/preview`, {
        method: 'GET'
      });

      if (response.ok) {
        const data = await response.json();
        setMetadata(data.metadata);
        setDocuments(data.document_summary || []);
      } else {
        throw new Error('Failed to fetch packet preview');
      }
    } catch (error) {
      console.error('Error fetching packet preview:', error);
      setError('Erro ao carregar preview do pacote');
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentApproval = (docIndex: number, approved: boolean) => {
    const updatedDocs = [...documents];
    updatedDocs[docIndex] = {
      ...updatedDocs[docIndex],
      approved: approved
    };
    setDocuments(updatedDocs);
  };

  const handleFinalApproval = () => {
    setApprovalState('approved');
    onApprove();
  };

  const handleFinalRejection = () => {
    if (!rejectionReason.trim()) {
      setError('Por favor, forneça um motivo para rejeição');
      return;
    }
    setApprovalState('rejected');
    onReject(rejectionReason);
  };

  const getQualityColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'READY_FOR_SUBMISSION': return 'bg-green-100 text-green-800';
      case 'REVIEW_RECOMMENDED': return 'bg-yellow-100 text-yellow-800';
      case 'NEEDS_CORRECTION': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'included': return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'referenced': return <FileText className="h-4 w-4 text-blue-500" />;
      case 'missing': return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'error': return <AlertCircle className="h-4 w-4 text-orange-500" />;
      default: return <FileText className="h-4 w-4 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#FF6B35]" />
          <p className="text-gray-600">Carregando preview do pacote...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200">
        <CardContent className="p-6">
          <div className="flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
            <div className="text-red-700">{error}</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!metadata) {
    return null;
  }

  const currentDoc = documents[currentDocIndex];

  return (
    <div className="space-y-6">
      {/* Header com informações do pacote */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Preview do Pacote Final</span>
            <Badge 
              variant="outline" 
              className={getRecommendationColor(metadata.quality_assessment.recommendation)}
            >
              {metadata.quality_assessment.recommendation.replace(/_/g, ' ')}
            </Badge>
          </CardTitle>
          <CardDescription>
            Caso {metadata.case_id} • {metadata.visa_type} • {new Date(metadata.generated_at).toLocaleString()}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {metadata.packet_statistics.documents_included}
              </div>
              <div className="text-sm text-gray-600">Documentos</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {metadata.packet_statistics.total_pages}
              </div>
              <div className="text-sm text-gray-600">Páginas</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${getQualityColor(metadata.quality_assessment.overall_score)}`}>
                {metadata.quality_assessment.overall_score}%
              </div>
              <div className="text-sm text-gray-600">Qualidade</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {metadata.quality_assessment.critical_issues}
              </div>
              <div className="text-sm text-gray-600">Issues Críticos</div>
            </div>
          </div>

          <div className="mt-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Progresso de Qualidade</span>
              <span className="text-sm font-medium">{metadata.quality_assessment.overall_score}%</span>
            </div>
            <Progress 
              value={metadata.quality_assessment.overall_score} 
              className="h-2"
            />
          </div>
        </CardContent>
      </Card>

      {/* Navegação entre documentos */}
      {documents.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Revisão de Documentos</span>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentDocIndex(Math.max(0, currentDocIndex - 1))}
                  disabled={currentDocIndex === 0}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-sm text-gray-600">
                  {currentDocIndex + 1} de {documents.length}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentDocIndex(Math.min(documents.length - 1, currentDocIndex + 1))}
                  disabled={currentDocIndex === documents.length - 1}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {currentDoc && (
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    {getStatusIcon(currentDoc.status)}
                    <div>
                      <h4 className="font-medium text-gray-900">{currentDoc.name}</h4>
                      <p className="text-sm text-gray-600">
                        {currentDoc.type.toUpperCase()} • {currentDoc.pages} páginas
                      </p>
                      {currentDoc.quality && (
                        <div className="flex items-center space-x-2 mt-1">
                          <Star className={`h-4 w-4 ${getQualityColor(currentDoc.quality * 100)}`} />
                          <span className={`text-sm ${getQualityColor(currentDoc.quality * 100)}`}>
                            {Math.round(currentDoc.quality * 100)}% qualidade
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDocumentApproval(currentDocIndex, true)}
                      className={currentDoc.approved === true ? 'bg-green-50 border-green-300' : ''}
                    >
                      <ThumbsUp className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDocumentApproval(currentDocIndex, false)}
                      className={currentDoc.approved === false ? 'bg-red-50 border-red-300' : ''}
                    >
                      <ThumbsDown className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {currentDoc.note && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-800">{currentDoc.note}</p>
                  </div>
                )}

                {currentDoc.error && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-800">
                      <strong>Erro:</strong> {currentDoc.error}
                    </p>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Lista completa de documentos */}
      <Card>
        <CardHeader>
          <CardTitle>Inventário Completo</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {documents.map((doc, index) => (
              <div 
                key={index}
                className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-colors ${
                  index === currentDocIndex ? 'bg-blue-50 border-blue-300' : 'hover:bg-gray-50'
                }`}
                onClick={() => setCurrentDocIndex(index)}
              >
                <div className="flex items-center space-x-3">
                  {getStatusIcon(doc.status)}
                  <div>
                    <div className="font-medium text-gray-900">{doc.name}</div>
                    <div className="text-sm text-gray-600">
                      {doc.type.toUpperCase()} • {doc.pages} páginas
                    </div>
                  </div>
                </div>
                
                {doc.quality && (
                  <Badge variant="outline" className={getQualityColor(doc.quality * 100)}>
                    {Math.round(doc.quality * 100)}%
                  </Badge>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Comentários */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="h-5 w-5" />
            <span>Comentários de Revisão</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <textarea
            value={comments}
            onChange={(e) => setComments(e.target.value)}
            placeholder="Adicione comentários sobre a qualidade do pacote, documentos que precisam de atenção, ou observações gerais..."
            className="w-full p-3 border border-gray-300 rounded-lg resize-none"
            rows={4}
          />
        </CardContent>
      </Card>

      {/* Ações finais */}
      {approvalState === 'pending' && (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Decisão Final</h3>
              
              <div className="flex items-center space-x-4">
                <Button
                  onClick={handleFinalApproval}
                  className="bg-green-600 hover:bg-green-700 flex-1"
                  disabled={documents.some(d => d.approved === false)}
                >
                  <CheckCircle2 className="w-4 h-4 mr-2" />
                  Aprovar Pacote
                </Button>
                
                <Button
                  variant="outline"
                  onClick={onDownload}
                  className="flex-1"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Preview Completo
                </Button>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Motivo da rejeição (opcional)
                </label>
                <textarea
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  placeholder="Descreva os problemas que impedem a aprovação..."
                  className="w-full p-3 border border-gray-300 rounded-lg resize-none"
                  rows={3}
                />
                <Button
                  variant="destructive"
                  onClick={handleFinalRejection}
                  className="w-full"
                  disabled={!rejectionReason.trim()}
                >
                  <ThumbsDown className="w-4 h-4 mr-2" />
                  Rejeitar Pacote
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Estado de aprovação/rejeição */}
      {approvalState !== 'pending' && (
        <Card className={`border-2 ${approvalState === 'approved' ? 'border-green-300 bg-green-50' : 'border-red-300 bg-red-50'}`}>
          <CardContent className="p-6 text-center">
            {approvalState === 'approved' ? (
              <div>
                <CheckCircle2 className="h-12 w-12 text-green-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-green-800 mb-2">Pacote Aprovado</h3>
                <p className="text-green-700">O pacote foi aprovado e está pronto para download e envio.</p>
              </div>
            ) : (
              <div>
                <AlertCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-red-800 mb-2">Pacote Rejeitado</h3>
                <p className="text-red-700 mb-2">O pacote foi rejeitado pelos seguintes motivos:</p>
                <div className="p-3 bg-red-100 border border-red-300 rounded-lg text-left">
                  <p className="text-red-800">{rejectionReason}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PacketPreview;