import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { 
  Download,
  Mail, 
  CreditCard,
  Shield,
  CheckCircle,
  AlertTriangle,
  Loader2,
  FileText,
  DollarSign,
  Clock,
  Eye
} from 'lucide-react';

interface Package {
  amount: number;
  name: string;
  description: string;
}

export const OwlPaymentPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const sessionId = searchParams.get('session_id');
  const [deliveryMethod, setDeliveryMethod] = useState<string>('download');
  const [loading, setLoading] = useState(false);
  const [sessionData, setSessionData] = useState<any>(null);
  const [packages, setPackages] = useState<{ [key: string]: Package }>({
    download_only: { amount: 29.99, name: 'Download Formulário USCIS', description: 'Download imediato do formulário preenchido' },
    download_email: { amount: 34.99, name: 'Download + Email', description: 'Download + envio por email' },
    email_only: { amount: 24.99, name: 'Envio por Email', description: 'Formulário enviado por email' }
  });

  const getBackendUrl = () => {
    return import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://smart-visa-helper-1.preview.emergentagent.com' || '';
  };

  useEffect(() => {
    if (sessionId) {
      fetchSessionData();
    }
  }, [sessionId]);

  const fetchSessionData = async () => {
    try {
      const response = await fetch(`${getBackendUrl()}/api/owl-agent/session/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setSessionData(data.session_data);
      }
    } catch (error) {
      console.error('Error fetching session data:', error);
    }
  };

  const handlePayment = async () => {
    if (!sessionId) return;

    setLoading(true);

    try {
      const originUrl = window.location.origin;
      
      const response = await fetch(`${getBackendUrl()}/api/owl-agent/initiate-payment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          delivery_method: deliveryMethod,
          origin_url: originUrl,
          user_email: sessionData?.user_email || ''
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.checkout_url) {
          // Redirect to Stripe checkout
          window.location.href = data.checkout_url;
        } else {
          throw new Error('No checkout URL received');
        }
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Payment initiation failed');
      }
      
    } catch (error) {
      console.error('Payment error:', error);
      alert(`Erro no pagamento: ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
    } finally {
      setLoading(false);
    }
  };

  const getCurrentPackage = () => {
    const packageMap = {
      'download': 'download_only',
      'email': 'email_only',
      'both': 'download_email'
    };
    
    const packageKey = packageMap[deliveryMethod as keyof typeof packageMap] || 'download_only';
    return packages[packageKey];
  };

  const getDeliveryMethodIcon = (method: string) => {
    switch (method) {
      case 'download': return <Download className="h-5 w-5" />;
      case 'email': return <Mail className="h-5 w-5" />;
      case 'both': return <><Download className="h-4 w-4" /><Mail className="h-4 w-4" /></>;
      default: return <Download className="h-5 w-5" />;
    }
  };

  if (!sessionId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center text-red-600">Sessão Não Encontrada</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="mb-4">ID da sessão não fornecido.</p>
            <Button onClick={() => navigate('/owl-agent')}>
              Voltar ao Início
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentPackage = getCurrentPackage();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🦉</div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Finalização do Processo
          </h1>
          <p className="text-gray-600">
            Seu formulário USCIS está pronto! Escolha como receber.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Payment Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Delivery Method Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="mr-2 h-5 w-5" />
                  Como você quer receber seu formulário?
                </CardTitle>
              </CardHeader>
              <CardContent>
                <RadioGroup value={deliveryMethod} onValueChange={setDeliveryMethod}>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-gray-50">
                      <RadioGroupItem value="download" id="download" />
                      <Label htmlFor="download" className="flex-1 cursor-pointer">
                        <div className="flex items-center">
                          <Download className="mr-2 h-4 w-4 text-blue-600" />
                          <div>
                            <div className="font-medium">Download Imediato</div>
                            <div className="text-sm text-gray-500">Baixe seu formulário agora mesmo</div>
                          </div>
                          <div className="ml-auto font-bold text-blue-600">$29.99</div>
                        </div>
                      </Label>
                    </div>

                    <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-gray-50">
                      <RadioGroupItem value="email" id="email" />
                      <Label htmlFor="email" className="flex-1 cursor-pointer">
                        <div className="flex items-center">
                          <Mail className="mr-2 h-4 w-4 text-green-600" />
                          <div>
                            <div className="font-medium">Envio por Email</div>
                            <div className="text-sm text-gray-500">Receba por email em até 24h</div>
                          </div>
                          <div className="ml-auto font-bold text-green-600">$24.99</div>
                        </div>
                      </Label>
                    </div>

                    <div className="flex items-center space-x-2 p-3 border-2 border-blue-200 bg-blue-50 rounded-lg hover:bg-blue-100">
                      <RadioGroupItem value="both" id="both" />
                      <Label htmlFor="both" className="flex-1 cursor-pointer">
                        <div className="flex items-center">
                          <div className="flex items-center mr-2">
                            <Download className="h-4 w-4 text-blue-600" />
                            <span className="mx-1">+</span>
                            <Mail className="h-4 w-4 text-green-600" />
                          </div>
                          <div>
                            <div className="font-medium">Download + Email</div>
                            <div className="text-sm text-gray-500">
                              <Badge className="mr-1 text-xs bg-orange-100 text-orange-800">RECOMENDADO</Badge>
                              Máxima segurança - ambas as opções
                            </div>
                          </div>
                          <div className="ml-auto font-bold text-blue-600">$34.99</div>
                        </div>
                      </Label>
                    </div>
                  </div>
                </RadioGroup>
              </CardContent>
            </Card>

            {/* Payment Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <DollarSign className="mr-2 h-5 w-5" />
                  Resumo do Pagamento
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center">
                      {getDeliveryMethodIcon(deliveryMethod)}
                      <span className="ml-2">{currentPackage.name}</span>
                    </div>
                    <span className="font-semibold">${currentPackage.amount}</span>
                  </div>
                  
                  <div className="border-t pt-3">
                    <div className="flex justify-between items-center font-bold text-lg">
                      <span>Total</span>
                      <span className="text-blue-600">${currentPackage.amount}</span>
                    </div>
                  </div>
                </div>

                <Button 
                  onClick={handlePayment}
                  disabled={loading}
                  className="w-full mt-6 h-12 text-lg bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Processando...
                    </>
                  ) : (
                    <>
                      <CreditCard className="mr-2 h-5 w-5" />
                      Pagar ${currentPackage.amount}
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Session Info */}
            {sessionData && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Informações da Aplicação</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Visto:</span>
                    <Badge variant="outline">{sessionData.visa_type}</Badge>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Idioma:</span>
                    <span>{sessionData.language === 'pt' ? '🇧🇷 Português' : '🇺🇸 English'}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Status:</span>
                    <Badge className="bg-green-100 text-green-800">Completo</Badge>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Privacy Notice */}
            <Card className="border-orange-200 bg-orange-50">
              <CardHeader>
                <CardTitle className="text-sm text-orange-800 flex items-center">
                  <Shield className="mr-2 h-4 w-4" />
                  Aviso Importante - Osprey
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-orange-700 space-y-2">
                <div className="flex items-start">
                  <AlertTriangle className="mr-2 h-3 w-3 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-semibold mb-1">OSPREY NÃO GUARDA seus dados:</p>
                    <ul className="space-y-1 text-xs">
                      <li>• Após download/email, todos os dados são DELETADOS</li>
                      <li>• Este é seu único acesso ao formulário</li>
                      <li>• Não mantemos cópias nem backup</li>
                      <li>• Responsabilidade é transferida para você</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Security Features */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm text-green-800 flex items-center">
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Segurança Garantida
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-gray-600 space-y-1">
                <div className="flex items-center">
                  <Shield className="mr-2 h-3 w-3 text-green-600" />
                  <span>Pagamento seguro via Stripe</span>
                </div>
                <div className="flex items-center">
                  <Clock className="mr-2 h-3 w-3 text-blue-600" />
                  <span>Download válido por 24h</span>
                </div>
                <div className="flex items-center">
                  <Eye className="mr-2 h-3 w-3 text-purple-600" />
                  <span>Máximo 3 downloads</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};