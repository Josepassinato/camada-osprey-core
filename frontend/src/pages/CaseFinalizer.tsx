import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { makeApiCall } from "@/utils/api";
import PacketPreview from "@/components/PacketPreview";
import { 
  CheckCircle2, 
  AlertCircle, 
  FileText, 
  Loader2, 
  Download,
  Package,
  ClipboardList,
  Shield,
  ExternalLink,
  Eye
} from "lucide-react";

interface FinalizationJob {
  job_id: string;
  status: 'running' | 'needs_correction' | 'completed' | 'ready' | 'error';
  issues: string[];
  links: {
    master_packet?: string;
    instructions?: string;
    checklist?: string;
  };
  approval_status?: 'pending' | 'approved' | 'rejected';
  created_at?: string;
  completed_at?: string;
}

const CaseFinalizer: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [job, setJob] = useState<FinalizationJob | null>(null);
  const [scenario, setScenario] = useState('H-1B_basic');
  const [postage, setPostage] = useState('USPS');
  const [language, setLanguage] = useState('pt');
  const [consentAccepted, setConsentAccepted] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const consentText = `
CONSENTIMENTO PARA FINALIZAÇÃO DO PROCESSO

Ao aceitar este consentimento, você confirma que:

1. Revisou todos os documentos e informações fornecidas
2. Entende que este é um serviço informativo baseado em requisitos públicos do USCIS
3. Este sistema NÃO constitui aconselhamento jurídico
4. É recomendável consultar um advogado de imigração para orientação específica
5. Você é responsável por verificar a exatidão de todas as informações antes do envio
6. As taxas e endereços podem sofrer alterações - verifique o site oficial do USCIS

Ao prosseguir, você assume total responsabilidade pelo uso das informações geradas.
`;

  const generateConsentHash = (text: string): string => {
    // Implementação simples de hash (em produção usaria SHA-256)
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
      const char = text.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(16, '0').padEnd(64, '0');
  };

  const startFinalization = async () => {
    if (!caseId) return;
    
    try {
      setLoading(true);
      setError('');
      
      const response = await makeApiCall(`/cases/${caseId}/finalize/start`, {
        method: 'POST',
        body: JSON.stringify({
          scenario_key: scenario,
          postage: postage,
          language: language
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.job_id) {
          // Começar polling do status
          pollJobStatus(data.job_id);
        } else if (data.error) {
          setError(data.error);
        }
      } else {
        throw new Error('Falha ao iniciar finalização');
      }
    } catch (error) {
      console.error('Error starting finalization:', error);
      setError('Erro ao iniciar finalização. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const pollJobStatus = async (jobId: string) => {
    try {
      const response = await makeApiCall(`/cases/finalize/${jobId}/status`, {
        method: 'GET'
      });

      if (response.ok) {
        const jobData = await response.json();
        setJob({ ...jobData, job_id: jobId });
        
        if (jobData.status === 'completed') {
          setCurrentStep(3); // Vai para preview/aprovação
        } else if (jobData.status === 'needs_correction') {
          setCurrentStep(2);
          setError(`Correções necessárias: ${jobData.issues?.join(', ')}`);
        } else if (jobData.status === 'running') {
          // Continuar polling
          setTimeout(() => pollJobStatus(jobId), 2000);
        }
      }
    } catch (error) {
      console.error('Error polling job status:', error);
      setError('Erro ao verificar status da finalização');
    }
  };

  const acceptConsent = async () => {
    if (!caseId) return;
    
    try {
      setLoading(true);
      const consentHash = generateConsentHash(consentText);
      
      const response = await makeApiCall(`/cases/${caseId}/finalize/accept`, {
        method: 'POST',
        body: JSON.stringify({
          consent_hash: consentHash
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.accepted) {
          setConsentAccepted(true);
          setCurrentStep(4);
        }
      } else {
        throw new Error('Falha ao aceitar consentimento');
      }
    } catch (error) {
      console.error('Error accepting consent:', error);
      setError('Erro ao aceitar consentimento. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = (url: string, filename: string) => {
    // Placeholder para download
    alert(`Download ${filename}: ${url}\n\n(MVP - Em produção faria download real)`);
  };

  return (
    <div className="min-h-screen bg-white p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Finalização do Processo</h1>
          <p className="text-gray-600 mt-2">
            Auditoria, empacotamento e preparação para envio ao USCIS
          </p>
          <Badge variant="outline" className="mt-2">
            Caso: {caseId}
          </Badge>
        </div>

        {/* Progress indicator */}
        <div className="mb-8">
          <div className="flex items-center space-x-4">
            {[1, 2, 3, 4].map((step) => (
              <div key={step} className={`flex items-center ${step < 4 ? 'flex-1' : ''}`}>
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    currentStep >= step
                      ? 'bg-[#FF6B35] text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {step}
                </div>
                <div className="ml-2 text-sm">
                  {step === 1 && 'Configuração'}
                  {step === 2 && 'Auditoria'}
                  {step === 3 && 'Consentimento'}
                  {step === 4 && 'Downloads'}
                </div>
                {step < 4 && (
                  <div
                    className={`flex-1 h-0.5 ml-4 ${
                      currentStep > step ? 'bg-[#FF6B35]' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Error display */}
        {error && (
          <Card className="mb-6 border-red-200">
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
                <div className="text-red-700">{error}</div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 1: Configuration */}
        {currentStep === 1 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Package className="h-5 w-5 text-[#FF6B35]" />
                <span>Configuração da Finalização</span>
              </CardTitle>
              <CardDescription>
                Configure os parâmetros para preparação do seu pacote final
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Tipo de Processo</label>
                  <select 
                    value={scenario}
                    onChange={(e) => setScenario(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-md"
                  >
                    <option value="H-1B_basic">H-1B (Specialty Occupation)</option>
                    <option value="F-1_basic">F-1 (Student Visa)</option>
                    <option value="I-485_basic">I-485 (Adjustment of Status)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Método de Envio</label>
                  <select 
                    value={postage}
                    onChange={(e) => setPostage(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-md"
                  >
                    <option value="USPS">USPS (Correio Regular)</option>
                    <option value="FedEx">FedEx</option>
                    <option value="UPS">UPS</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Idioma das Instruções</label>
                  <select 
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-md"
                  >
                    <option value="pt">Português</option>
                    <option value="en">English</option>
                  </select>
                </div>

                <Button
                  onClick={startFinalization}
                  disabled={loading}
                  className="bg-[#FF6B35] hover:bg-[#FF6B35]/90 w-full"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Processando...
                    </>
                  ) : (
                    'Iniciar Finalização'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Issues (if any) */}
        {currentStep === 2 && job?.status === 'needs_correction' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-yellow-500" />
                <span>Correções Necessárias</span>
              </CardTitle>
              <CardDescription>
                Alguns itens precisam ser corrigidos antes de prosseguir
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {job.issues.map((issue, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg">
                    <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
                    <span className="text-yellow-800">{issue}</span>
                  </div>
                ))}
                
                <div className="mt-4">
                  <Button
                    variant="outline"
                    onClick={() => navigate(-1)}
                    className="mr-3"
                  >
                    Voltar para Correções
                  </Button>
                  <Button
                    onClick={startFinalization}
                    disabled={loading}
                  >
                    Tentar Novamente
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Consent */}
        {currentStep === 3 && job?.status === 'ready' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-[#FF6B35]" />
                <span>Consentimento e Responsabilidade</span>
              </CardTitle>
              <CardDescription>
                Leia atentamente antes de prosseguir com os downloads
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-lg max-h-60 overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700">
                    {consentText}
                  </pre>
                </div>

                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-blue-800 text-sm">
                    <strong>Importante:</strong> Este sistema gera documentos informativos baseados em requisitos públicos.
                    Sempre consulte um advogado de imigração para orientação específica do seu caso.
                  </p>
                </div>

                <Button
                  onClick={acceptConsent}
                  disabled={loading}
                  className="bg-[#FF6B35] hover:bg-[#FF6B35]/90 w-full"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Processando...
                    </>
                  ) : (
                    'Aceito os Termos e Prosseguir'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 4: Downloads */}
        {currentStep === 4 && consentAccepted && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                <span>Pacote Finalizado</span>
              </CardTitle>
              <CardDescription>
                Seus documentos estão prontos para download e envio
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Master Packet */}
                <div className="p-4 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-3 mb-3">
                    <FileText className="h-8 w-8 text-[#FF6B35]" />
                    <div>
                      <h3 className="font-medium">Pacote Principal</h3>
                      <p className="text-sm text-gray-600">PDF com todos os documentos</p>
                    </div>
                  </div>
                  <Button
                    onClick={() => downloadFile(job?.links.master_packet || '', 'master-packet.pdf')}
                    className="w-full"
                    size="sm"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                </div>

                {/* Instructions */}
                <div className="p-4 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-3 mb-3">
                    <ClipboardList className="h-8 w-8 text-blue-600" />
                    <div>
                      <h3 className="font-medium">Instruções de Envio</h3>
                      <p className="text-sm text-gray-600">Endereços, taxas e procedimentos</p>
                    </div>
                  </div>
                  <Button
                    onClick={() => downloadFile(job?.links.instructions || '', 'instructions.pdf')}
                    variant="outline"
                    className="w-full"
                    size="sm"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                </div>

                {/* Checklist */}
                <div className="p-4 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-3 mb-3">
                    <CheckCircle2 className="h-8 w-8 text-green-600" />
                    <div>
                      <h3 className="font-medium">Checklist Final</h3>
                      <p className="text-sm text-gray-600">Lista de verificação</p>
                    </div>
                  </div>
                  <Button
                    onClick={() => downloadFile(job?.links.checklist || '', 'checklist.pdf')}
                    variant="outline"
                    className="w-full"
                    size="sm"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                </div>
              </div>

              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <div className="flex items-start space-x-3">
                  <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
                  <div className="text-green-800">
                    <h4 className="font-medium">Processo Finalizado com Sucesso!</h4>
                    <p className="text-sm mt-1">
                      Seus documentos foram auditados e empacotados. Revise as instruções antes do envio.
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-4 flex space-x-3">
                <Button
                  variant="outline"
                  onClick={() => navigate('/dashboard')}
                >
                  Voltar ao Dashboard
                </Button>
                <Button
                  onClick={() => window.open('https://www.uscis.gov', '_blank')}
                  className="flex items-center"
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Site Oficial USCIS
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default CaseFinalizer;