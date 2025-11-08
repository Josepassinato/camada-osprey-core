import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  CheckCircle,
  Download,
  Mail,
  Clock,
  Loader2,
  AlertTriangle,
  Shield,
  RefreshCw,
  FileText,
  Trash2
} from 'lucide-react';

export const OwlPaymentSuccessPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const stripeSessionId = searchParams.get('session_id');
  
  const [paymentStatus, setPaymentStatus] = useState<'loading' | 'success' | 'failed' | 'expired'>('loading');
  const [paymentData, setPaymentData] = useState<any>(null);
  const [downloadId, setDownloadId] = useState<string | null>(null);
  const [pollingAttempts, setPollingAttempts] = useState(0);
  const [downloading, setDownloading] = useState(false);

  const getBackendUrl = () => {
    return import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://owlagent.preview.emergentagent.com' || '';
  };

  useEffect(() => {
    if (stripeSessionId) {
      pollPaymentStatus();
    }
  }, [stripeSessionId]);

  const pollPaymentStatus = async (attempts: number = 0) => {
    const maxAttempts = 10;
    const pollInterval = 3000; // 3 seconds

    if (attempts >= maxAttempts) {
      setPaymentStatus('failed');
      return;
    }

    try {
      const response = await fetch(`${getBackendUrl()}/api/owl-agent/payment-status/${stripeSessionId}`);
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.payment_status === 'paid') {
          setPaymentStatus('success');
          setPaymentData(data.payment_data);
          
          // Check if download is ready
          if (data.payment_data?.download_id) {
            setDownloadId(data.payment_data.download_id);
          }
          return;
        } else if (data.session_status === 'expired') {
          setPaymentStatus('expired');
          return;
        }
        
        // Continue polling if still processing
        setPollingAttempts(attempts + 1);
        setTimeout(() => pollPaymentStatus(attempts + 1), pollInterval);
        
      } else {
        throw new Error('Failed to check payment status');
      }
      
    } catch (error) {
      console.error('Error checking payment status:', error);
      if (attempts < 3) {
        setTimeout(() => pollPaymentStatus(attempts + 1), pollInterval);
      } else {
        setPaymentStatus('failed');
      }
    }
  };

  const handleDownload = async () => {
    if (!downloadId) return;
    
    setDownloading(true);
    
    try {
      const response = await fetch(`${getBackendUrl()}/api/owl-agent/download/${downloadId}`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        
        // Get filename from response headers
        const contentDisposition = response.headers.get('content-disposition');
        let filename = 'USCIS_Form.pdf';
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
        a.download = filename;
        
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Show success message
        alert('Download iniciado com sucesso!');
        
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Download failed');
      }
      
    } catch (error) {
      console.error('Download error:', error);
      alert(`Erro no download: ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
    } finally {
      setDownloading(false);
    }
  };

  const getDeliveryMethodInfo = (method: string) => {
    switch (method) {
      case 'download':
        return { icon: <Download className="h-4 w-4" />, text: 'Download Imediato' };
      case 'email':
        return { icon: <Mail className="h-4 w-4" />, text: 'Envio por Email' };
      case 'both':
        return { 
          icon: <><Download className="h-3 w-3" /><Mail className="h-3 w-3" /></>, 
          text: 'Download + Email' 
        };
      default:
        return { icon: <Download className="h-4 w-4" />, text: 'Download' };
    }
  };

  if (!stripeSessionId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center text-red-600">Sessão Inválida</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="mb-4">Sessão de pagamento não encontrada.</p>
            <Button onClick={() => navigate('/owl-agent')}>
              Voltar ao Início
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (paymentStatus === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center text-blue-600 flex items-center justify-center">
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Verificando Pagamento
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <div className="text-6xl">🦉</div>
            <p className="text-gray-600">
              Aguarde enquanto verificamos seu pagamento...
            </p>
            <div className="flex items-center justify-center text-sm text-gray-500">
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              Tentativa {pollingAttempts + 1} de 10
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (paymentStatus === 'failed' || paymentStatus === 'expired') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center text-red-600 flex items-center justify-center">
              <AlertTriangle className="mr-2 h-5 w-5" />
              {paymentStatus === 'expired' ? 'Pagamento Expirado' : 'Falha no Pagamento'}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <div className="text-6xl">😔</div>
            <p className="text-gray-600">
              {paymentStatus === 'expired' 
                ? 'Sua sessão de pagamento expirou. Tente novamente.'
                : 'Não foi possível processar seu pagamento. Tente novamente.'
              }
            </p>
            <div className="space-y-2">
              <Button 
                onClick={() => window.location.reload()} 
                className="w-full"
                variant="outline"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Verificar Novamente
              </Button>
              <Button 
                onClick={() => navigate('/owl-agent')}
                className="w-full"
              >
                Voltar ao Início
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Success state
  const deliveryInfo = getDeliveryMethodInfo(paymentData?.delivery_method || 'download');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-3xl mx-auto">
        {/* Success Header */}
        <div className="text-center mb-8">
          <div className="text-8xl mb-4">🎉</div>
          <h1 className="text-3xl font-bold text-green-700 mb-2">
            Pagamento Confirmado!
          </h1>
          <p className="text-gray-600">
            Seu formulário USCIS está pronto para download
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Payment Success Card */}
            <Card className="border-green-200 bg-green-50">
              <CardHeader>
                <CardTitle className="text-green-800 flex items-center">
                  <CheckCircle className="mr-2 h-5 w-5" />
                  Pagamento Processado com Sucesso
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Valor pago:</span>
                    <div className="font-semibold">${paymentData?.amount || '0.00'}</div>
                  </div>
                  <div>
                    <span className="text-gray-600">Método de entrega:</span>
                    <div className="font-semibold flex items-center">
                      {deliveryInfo.icon}
                      <span className="ml-2">{deliveryInfo.text}</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-600">Tipo de visto:</span>
                    <Badge variant="outline">{paymentData?.visa_type}</Badge>
                  </div>
                  <div>
                    <span className="text-gray-600">Data do pagamento:</span>
                    <div className="font-semibold">
                      {new Date().toLocaleDateString('pt-BR')}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Download Section */}
            {(paymentData?.delivery_method === 'download' || paymentData?.delivery_method === 'both') && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Download className="mr-2 h-5 w-5 text-blue-600" />
                    Fazer Download do Formulário
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Alert>
                    <Clock className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Importante:</strong> Este link de download expira em 24 horas e permite até 3 downloads.
                    </AlertDescription>
                  </Alert>

                  {downloadId ? (
                    <Button
                      onClick={handleDownload}
                      disabled={downloading}
                      className="w-full h-12 bg-blue-600 hover:bg-blue-700"
                    >
                      {downloading ? (
                        <>
                          <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                          Baixando...
                        </>
                      ) : (
                        <>
                          <Download className="mr-2 h-5 w-5" />
                          Baixar Formulário USCIS
                        </>
                      )}
                    </Button>
                  ) : (
                    <div className="text-center py-4">
                      <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
                      <p className="text-gray-600">Preparando seu download...</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Email Section */}
            {(paymentData?.delivery_method === 'email' || paymentData?.delivery_method === 'both') && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Mail className="mr-2 h-5 w-5 text-green-600" />
                    Envio por Email
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Alert>
                    <Mail className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Email será enviado em até 24 horas para:</strong> {paymentData?.user_email}
                      <br />
                      Verifique também sua caixa de spam.
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Privacy Notice */}
            <Card className="border-red-200 bg-red-50">
              <CardHeader>
                <CardTitle className="text-sm text-red-800 flex items-center">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Política de Privacidade Osprey
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-red-700 space-y-2">
                <div className="space-y-1">
                  <p className="font-semibold">⚠️ ATENÇÃO IMPORTANTE:</p>
                  <ul className="space-y-1">
                    <li>• Seus dados serão DELETADOS após 24h</li>
                    <li>• Osprey NÃO mantém cópias dos formulários</li>
                    <li>• Este é seu único acesso ao documento</li>
                    <li>• Faça backup se necessário</li>
                    <li>• Responsabilidade transferida para você</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Security Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center">
                  <Shield className="mr-2 h-4 w-4 text-green-600" />
                  Segurança do Documento
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-gray-600 space-y-1">
                <div className="flex items-center">
                  <FileText className="mr-2 h-3 w-3" />
                  <span>Formulário oficial USCIS</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="mr-2 h-3 w-3 text-green-600" />
                  <span>Dados validados por sistema</span>
                </div>
                <div className="flex items-center">
                  <Shield className="mr-2 h-3 w-3 text-blue-600" />
                  <span>Criptografia end-to-end</span>
                </div>
              </CardContent>
            </Card>

            {/* Next Steps */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Próximos Passos</CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-gray-600 space-y-2">
                <div className="space-y-1">
                  <p className="font-semibold">1. Revise seu formulário</p>
                  <p className="font-semibold">2. Assine onde necessário</p>
                  <p className="font-semibold">3. Envie para o USCIS</p>
                </div>
                <Alert className="mt-3">
                  <AlertDescription className="text-xs">
                    <strong>Lembre-se:</strong> Você ainda precisa enviar o formulário oficialmente para o USCIS.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>

            {/* Back to Home */}
            <Button 
              onClick={() => navigate('/owl-agent')}
              variant="outline" 
              className="w-full"
            >
              Nova Aplicação
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};