import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  ArrowLeft,
  ArrowRight,
  CreditCard,
  CheckCircle,
  AlertTriangle,
  Save,
  RefreshCw,
  Info,
  Download,
  FileText,
  Package,
  DollarSign,
  Lock,
  Shield,
  Calendar,
  Clock,
  Zap,
  Mail,
  Phone,
  ExternalLink,
  Send
} from "lucide-react";
import USCISSubmissionGuide from "@/components/USCISSubmissionGuide";

interface PricingPackage {
  id: string;
  name: string;
  price: number;
  originalPrice?: number;
  description: string;
  features: string[];
  recommended?: boolean;
  uscis_fee_included: boolean;
}

interface PaymentMethod {
  id: string;
  type: 'credit_card' | 'pix' | 'bank_transfer';
  name: string;
  icon: any;
  processing_time: string;
  fees?: string;
}

const PaymentAndDownload = () => {
  const { caseId } = useParams();
  const navigate = useNavigate();
  
  const [case_, setCase] = useState<any>(null);
  const [visaSpecs, setVisaSpecs] = useState<any>(null);
  const [packages, setPackages] = useState<PricingPackage[]>([]);
  const [selectedPackage, setSelectedPackage] = useState<string>('');
  const [selectedPayment, setSelectedPayment] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState("");
  const [paymentComplete, setPaymentComplete] = useState(false);
  const [downloadReady, setDownloadReady] = useState(false);
  const [showSubmissionGuide, setShowSubmissionGuide] = useState(false);

  const paymentMethods: PaymentMethod[] = [
    {
      id: 'credit_card',
      type: 'credit_card',
      name: 'Cartão de Crédito',
      icon: CreditCard,
      processing_time: 'Imediato',
      fees: 'Taxa de 2.9%'
    },
    {
      id: 'pix',
      type: 'pix',
      name: 'PIX',
      icon: Zap,
      processing_time: '1-2 minutos',
      fees: 'Sem taxas'
    },
    {
      id: 'bank_transfer',
      type: 'bank_transfer',
      name: 'Transferência Bancária',
      icon: DollarSign,
      processing_time: '1-2 dias úteis',
      fees: 'Sem taxas'
    }
  ];

  useEffect(() => {
    if (caseId) {
      fetchCase();
    }
  }, [caseId]);

  const fetchCase = async () => {
    try {
      const sessionToken = localStorage.getItem('osprey_session_token');
      
      let url = `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}`;
      if (sessionToken && sessionToken !== 'null') {
        url += `?session_token=${sessionToken}`;
      }
      
      const response = await fetch(url);

      if (response.ok) {
        const data = await response.json();
        setCase(data.case);
        
        // Check if payment is already complete
        if (data.case.payment_status === 'completed') {
          setPaymentComplete(true);
        }
        
        // Check if download is ready
        if (data.case.final_package_generated) {
          setDownloadReady(true);
        }
        
        if (data.case.form_code) {
          await fetchVisaSpecs(data.case.form_code);
          generatePackages(data.case.form_code);
        }
      } else {
        setError('Caso não encontrado');
      }
    } catch (error) {
      console.error('Fetch case error:', error);
      setError('Erro de conexão');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchVisaSpecs = async (formCode: string) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/auto-application/visa-specs/${formCode}`
      );

      if (response.ok) {
        const data = await response.json();
        setVisaSpecs(data);
      }
    } catch (error) {
      console.error('Fetch visa specs error:', error);
    }
  };

  const generatePackages = (formCode: string) => {
    const basePrice = 299;
    const uscis_fee = parseInt(visaSpecs?.specifications.uscis_fee?.replace('$', '').replace(',', '') || '500');
    
    const packageOptions: PricingPackage[] = [
      {
        id: 'basic',
        name: 'Pacote Básico',
        price: basePrice,
        description: 'Formulários preenchidos e organizados para submissão',
        uscis_fee_included: false,
        features: [
          'Formulários oficiais preenchidos em inglês',
          'Checklist personalizado de documentos',
          'Instruções passo-a-passo para submissão',
          'Suporte via email por 30 dias',
          'Templates de cartas de apoio'
        ]
      },
      {
        id: 'complete',
        name: 'Pacote Completo',
        price: basePrice + 200,
        originalPrice: basePrice + 300,
        description: 'Tudo do básico + revisão profissional e suporte prioritário',
        recommended: true,
        uscis_fee_included: false,
        features: [
          'Tudo do Pacote Básico',
          'Revisão profissional dos formulários',
          'Consulta de 1 hora via video chamada',
          'Suporte prioritário via WhatsApp',
          'Acompanhamento do status da aplicação',
          'Templates de respostas para RFE',
          'Guia de preparação para entrevista'
        ]
      },
      {
        id: 'premium',
        name: 'Pacote Premium + Taxa USCIS',
        price: basePrice + 200 + uscis_fee,
        description: 'Pacote completo + pagamento da taxa USCIS incluído',
        uscis_fee_included: true,
        features: [
          'Tudo do Pacote Completo',
          `Taxa USCIS de ${visaSpecs?.specifications.uscis_fee || '$500'} incluída`,
          'Submissão automática ao USCIS',
          'Monitoramento em tempo real do caso',
          'Notificações automáticas de atualizações',
          'Garantia de reembolso se rejeitado por erro nosso'
        ]
      }
    ];

    setPackages(packageOptions);
    setSelectedPackage('complete'); // Pre-select recommended
  };

  const processPayment = async () => {
    if (!selectedPackage || !selectedPayment) {
      setError('Selecione um pacote e método de pagamento');
      return;
    }

    setIsProcessing(true);
    
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/process-payment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_id: caseId,
          package_id: selectedPackage,
          payment_method: selectedPayment,
          amount: packages.find(p => p.id === selectedPackage)?.price
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Simulate payment processing
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        setPaymentComplete(true);
        
        // Start generating final package
        generateFinalPackage();
        
      } else {
        setError('Erro ao processar pagamento');
      }
      
    } catch (error) {
      console.error('Payment error:', error);
      setError('Erro de conexão no pagamento');
    } finally {
      setIsProcessing(false);
    }
  };

  const generateFinalPackage = async () => {
    setIsGenerating(true);
    
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/generate-package`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_id: caseId,
          package_type: selectedPackage
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Simulate package generation
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        setDownloadReady(true);
        
        // Update case status
        await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/case/${caseId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            status: 'completed',
            final_package_generated: true,
            final_package_url: data.download_url
          }),
        });
        
      } else {
        setError('Erro ao gerar pacote final');
      }
      
    } catch (error) {
      console.error('Package generation error:', error);
      setError('Erro ao gerar pacote');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadPackage = () => {
    // Simulate download
    const link = document.createElement('a');
    link.href = '#'; // In real implementation, this would be the actual file URL
    link.download = `OSPREY-${case_?.form_code}-${case_?.case_id}-Package.zip`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Show success message
    alert('Download iniciado! Verifique sua pasta de downloads.');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Preparando opções de pagamento...</p>
        </div>
      </div>
    );
  }

  if (error && !case_) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <Card className="glass border-0 max-w-md">
          <CardContent className="text-center p-8">
            <AlertTriangle className="h-12 w-12 text-gray-700 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-foreground mb-2">
              {error || 'Caso não encontrado'}
            </h2>
            <Button onClick={() => navigate('/auto-application/start')}>
              Voltar ao Início
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="glass border-b border-white/20">
        <div className="container-responsive py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate(`/auto-application/case/${caseId}/review`)}
                className="p-2"
                disabled={paymentComplete}
              >
                <ArrowLeft className="h-4 w-4" />
                Voltar
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                  {downloadReady ? (
                    <Package className="h-8 w-8 text-green-600" />
                  ) : (
                    <CreditCard className="h-8 w-8 text-black" />
                  )}
                  {visaSpecs?.specifications.title || case_.form_code}
                </h1>
                <p className="text-muted-foreground">
                  Etapa 6 de 6: {downloadReady ? 'Download do Pacote' : 'Pagamento & Finalização'} • Caso: {case_.case_id}
                </p>
              </div>
            </div>
            <Badge className={`${paymentComplete ? 'bg-green-100 text-green-800 border-green-200' : 'bg-gray-100 text-gray-800 border-gray-200'}`}>
              {paymentComplete ? 'Pago' : 'Aguardando Pagamento'}
            </Badge>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        <div className="max-w-6xl mx-auto">
          
          {/* Success State - Download Ready */}
          {downloadReady && (
            <div className="space-y-6">
              <Card className="glass border-0 bg-green-50 border-green-200">
                <CardContent className="text-center p-8">
                  <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
                  <h2 className="text-2xl font-bold text-green-800 mb-2">
                    Parabéns! Sua aplicação está pronta!
                  </h2>
                  <p className="text-green-700 mb-6">
                    Seu pacote completo foi gerado com sucesso e está pronto para download.
                  </p>
                  
                  <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                    <Card className="bg-white border-green-200">
                      <CardContent className="p-6">
                        <Package className="h-12 w-12 text-green-600 mx-auto mb-4" />
                        <h3 className="font-bold text-lg mb-2">Pacote Completo</h3>
                        <ul className="text-sm text-gray-600 space-y-1 mb-4">
                          <li>• Formulários oficiais preenchidos</li>
                          <li>• Checklist de documentos</li>
                          <li>• Instruções detalhadas</li>
                          <li>• Cartas de apoio</li>
                          <li>• Guia de submissão</li>
                        </ul>
                        <Button 
                          onClick={downloadPackage}
                          className="w-full bg-green-600 hover:bg-green-700 text-white"
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Download Pacote (ZIP)
                        </Button>
                      </CardContent>
                    </Card>
                    
                    <Card className="bg-white border-green-200">
                      <CardContent className="p-6">
                        <Mail className="h-12 w-12 text-green-600 mx-auto mb-4" />
                        <h3 className="font-bold text-lg mb-2">Suporte Contínuo</h3>
                        <p className="text-sm text-gray-600 mb-4">
                          Nossa equipe está pronta para ajudar você durante todo o processo.
                        </p>
                        <div className="space-y-2">
                          <Button variant="outline" className="w-full">
                            <Mail className="h-4 w-4 mr-2" />
                            support@osprey.com
                          </Button>
                          <Button variant="outline" className="w-full">
                            <Phone className="h-4 w-4 mr-2" />
                            WhatsApp Suporte
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                  
                  <div className="mt-8 p-4 bg-white rounded-lg border border-green-200">
                    <h4 className="font-medium text-gray-800 mb-2">Próximos Passos:</h4>
                    <ol className="text-sm text-gray-600 space-y-1 text-left max-w-2xl mx-auto">
                      <li>1. Faça o download do pacote completo acima</li>
                      <li>2. Revise todos os documentos e formulários</li>
                      <li>3. Reúna os documentos originais conforme checklist</li>
                      <li>4. Agende sua submissão seguindo as instruções</li>
                      <li>5. Entre em contato conosco se tiver dúvidas</li>
                    </ol>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Payment Processing State */}
          {isProcessing && (
            <Card className="glass border-0 max-w-md mx-auto">
              <CardContent className="text-center p-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
                <h3 className="text-lg font-semibold mb-2">Processando Pagamento</h3>
                <p className="text-muted-foreground">
                  Aguarde enquanto processamos seu pagamento...
                </p>
              </CardContent>
            </Card>
          )}

          {/* Package Generation State */}
          {isGenerating && (
            <Card className="glass border-0 max-w-md mx-auto">
              <CardContent className="text-center p-8">
                <Package className="h-12 w-12 text-black mx-auto mb-4 animate-pulse" />
                <h3 className="text-lg font-semibold mb-2">Gerando Seu Pacote</h3>
                <p className="text-muted-foreground">
                  Preparando todos os documentos e formulários...
                </p>
                <Progress value={75} className="mt-4" />
              </CardContent>
            </Card>
          )}

          {/* Payment Selection State */}
          {!paymentComplete && !isProcessing && !isGenerating && (
            <div className="space-y-8">
              
              {/* Package Selection */}
              <div>
                <h2 className="text-2xl font-bold text-center mb-6">Escolha seu Pacote</h2>
                <div className="grid md:grid-cols-3 gap-6">
                  {packages.map((pkg) => (
                    <Card 
                      key={pkg.id}
                      className={`glass border-0 cursor-pointer transition-all ${
                        selectedPackage === pkg.id 
                          ? 'ring-2 ring-black bg-gray-50' 
                          : 'hover:shadow-lg'
                      } ${pkg.recommended ? 'border-black border-2' : ''}`}
                      onClick={() => setSelectedPackage(pkg.id)}
                    >
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-lg">{pkg.name}</CardTitle>
                          {pkg.recommended && (
                            <Badge className="bg-black text-white">Recomendado</Badge>
                          )}
                        </div>
                        <div className="text-2xl font-bold">
                          ${pkg.price}
                          {pkg.originalPrice && (
                            <span className="text-lg text-gray-500 line-through ml-2">
                              ${pkg.originalPrice}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">{pkg.description}</p>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {pkg.features.map((feature, index) => (
                            <li key={index} className="flex items-start gap-2 text-sm">
                              <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                              <span>{feature}</span>
                            </li>
                          ))}
                        </ul>
                        
                        {pkg.uscis_fee_included && (
                          <div className="mt-4 p-3 bg-green-50 rounded-lg">
                            <div className="flex items-center gap-2">
                              <Shield className="h-4 w-4 text-green-600" />
                              <span className="text-sm font-medium text-green-800">
                                Taxa USCIS Incluída
                              </span>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Payment Method Selection */}
              <div>
                <h2 className="text-2xl font-bold text-center mb-6">Método de Pagamento</h2>
                <div className="grid md:grid-cols-3 gap-4 max-w-3xl mx-auto">
                  {paymentMethods.map((method) => {
                    const IconComponent = method.icon;
                    return (
                      <Card
                        key={method.id}
                        className={`glass border-0 cursor-pointer transition-all ${
                          selectedPayment === method.id 
                            ? 'ring-2 ring-black bg-gray-50' 
                            : 'hover:shadow-lg'
                        }`}
                        onClick={() => setSelectedPayment(method.id)}
                      >
                        <CardContent className="p-4 text-center">
                          <IconComponent className="h-8 w-8 mx-auto mb-2" />
                          <h3 className="font-medium">{method.name}</h3>
                          <p className="text-xs text-muted-foreground">{method.processing_time}</p>
                          {method.fees && (
                            <p className="text-xs text-gray-500 mt-1">{method.fees}</p>
                          )}
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </div>

              {/* Security & Trust */}
              <Card className="glass border-0 bg-gray-50 max-w-2xl mx-auto">
                <CardContent className="p-6 text-center">
                  <Lock className="h-8 w-8 text-gray-700 mx-auto mb-3" />
                  <h3 className="font-medium mb-2">Pagamento 100% Seguro</h3>
                  <p className="text-sm text-muted-foreground">
                    Seus dados são protegidos com criptografia de nível bancário. 
                    Processamento via Stripe e PagSeguro.
                  </p>
                </CardContent>
              </Card>

              {/* Final Action */}
              <div className="text-center">
                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                    {error}
                  </div>
                )}
                
                <Button
                  onClick={processPayment}
                  disabled={!selectedPackage || !selectedPayment || isProcessing}
                  className="bg-black text-white hover:bg-gray-800 px-8 py-3 text-lg"
                >
                  {isProcessing ? (
                    <>
                      <RefreshCw className="h-5 w-5 animate-spin mr-2" />
                      Processando...
                    </>
                  ) : (
                    <>
                      <Lock className="h-5 w-5 mr-2" />
                      Finalizar Pagamento
                      {selectedPackage && (
                        <span className="ml-2">
                          - ${packages.find(p => p.id === selectedPackage)?.price}
                        </span>
                      )}
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PaymentAndDownload;