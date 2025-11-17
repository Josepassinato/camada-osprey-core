import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, CheckCircle, XCircle, CreditCard, Tag, ArrowLeft } from 'lucide-react';
import { makeApiCall } from '@/utils/api';
import ProcessTypeBadge from '@/components/ProcessTypeBadge';
import { useProcessType } from '@/contexts/ProcessTypeContext';

interface PackageInfo {
  name: string;
  description: string;
  price: number;
  category: string;
  category_name: string;
  includes: string[];
}

interface PriceInfo {
  original_price: number;
  discount_percentage: number;
  discount_amount: number;
  final_price: number;
  savings: number;
}

const PaymentPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { processType } = useProcessType();
  
  const visaCode = searchParams.get('visa_code');
  const caseId = searchParams.get('case_id');
  
  const [packageInfo, setPackageInfo] = useState<PackageInfo | null>(null);
  const [priceInfo, setPriceInfo] = useState<PriceInfo | null>(null);
  const [voucherCode, setVoucherCode] = useState('');
  const [voucherApplied, setVoucherApplied] = useState(false);
  const [voucherMessage, setVoucherMessage] = useState('');
  const [isValidatingVoucher, setIsValidatingVoucher] = useState(false);
  const [isProcessingPayment, setIsProcessingPayment] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!visaCode || !caseId) {
      setError('Informações de visto ou caso ausentes');
      setLoading(false);
      return;
    }
    
    loadPackageInfo();
  }, [visaCode, caseId]);

  const loadPackageInfo = async () => {
    try {
      setLoading(true);
      const response = await makeApiCall(`/packages/${visaCode}`, 'GET');
      
      if (response.success) {
        setPackageInfo(response.package);
        setPriceInfo(response.price_info);
      } else {
        setError('Erro ao carregar informações do pacote');
      }
    } catch (err: any) {
      console.error('Erro ao carregar pacote:', err);
      setError(err.message || 'Erro ao carregar informações');
    } finally {
      setLoading(false);
    }
  };

  const handleApplyVoucher = async () => {
    if (!voucherCode.trim()) {
      setVoucherMessage('Por favor, insira um código de voucher');
      return;
    }

    setIsValidatingVoucher(true);
    setVoucherMessage('');
    setError('');

    try {
      const response = await makeApiCall(
        `/vouchers/validate/${voucherCode}?visa_code=${visaCode}`,
        'GET'
      );

      if (response.valid) {
        setVoucherApplied(true);
        setVoucherMessage(response.message);
        
        // Recarregar preço com voucher
        const priceResponse = await makeApiCall(
          `/packages/${visaCode}?voucher_code=${voucherCode}`,
          'GET'
        );
        
        if (priceResponse.success) {
          setPriceInfo(priceResponse.price_info);
        }
      } else {
        setVoucherApplied(false);
        setVoucherMessage(response.message || 'Voucher inválido');
      }
    } catch (err: any) {
      setVoucherMessage(err.message || 'Erro ao validar voucher');
    } finally {
      setIsValidatingVoucher(false);
    }
  };

  const handleRemoveVoucher = async () => {
    setVoucherCode('');
    setVoucherApplied(false);
    setVoucherMessage('');
    
    // Recarregar preço sem voucher
    await loadPackageInfo();
  };

  const handlePayment = async () => {
    if (!caseId || !visaCode) return;

    setIsProcessingPayment(true);
    setError('');

    try {
      const response = await makeApiCall('/payment/create-checkout', 'POST', {
        visa_code: visaCode,
        case_id: caseId,
        voucher_code: voucherApplied ? voucherCode : ''
      });

      if (response.success && response.checkout_url) {
        // Redirecionar para Stripe Checkout
        window.location.href = response.checkout_url;
      } else {
        setError(response.error || 'Erro ao criar sessão de pagamento');
        setIsProcessingPayment(false);
      }
    } catch (err: any) {
      console.error('Erro ao processar pagamento:', err);
      setError(err.message || 'Erro ao processar pagamento');
      setIsProcessingPayment(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error && !packageInfo) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <XCircle className="h-5 w-5" />
              Erro
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={() => navigate('/auto-application/select-form')} className="w-full">
              Voltar
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 sm:py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                onClick={() => navigate('/auto-application/select-form')}
                className="p-2"
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <div>
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
                  Pagamento Seguro
                </h1>
                <p className="text-sm text-gray-600">Processado por Stripe</p>
              </div>
            </div>
            <ProcessTypeBadge processType={processType} size="sm" />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-6 sm:py-8">
        <div className="grid md:grid-cols-2 gap-6">
          {/* Package Info */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Pacote Selecionado</CardTitle>
                  <Badge variant="outline">{packageInfo?.category_name}</Badge>
                </div>
                <CardDescription>
                  <span className="font-semibold text-lg text-gray-900">
                    {visaCode}: {packageInfo?.name}
                  </span>
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">{packageInfo?.description}</p>
                
                <div className="space-y-2">
                  <h4 className="font-semibold text-sm text-gray-900">O que está incluído:</h4>
                  <ul className="space-y-2">
                    {packageInfo?.includes.map((item, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Active Vouchers Info */}
            <Card className="bg-blue-50 border-blue-200">
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <Tag className="h-4 w-4" />
                  Voucher Disponível
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="bg-white rounded-lg p-3 border border-blue-300">
                    <p className="font-mono font-bold text-blue-700 text-lg">LANCAMENTO50</p>
                    <p className="text-sm text-gray-600 mt-1">50% de desconto - Bônus de Lançamento</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Payment Info */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Resumo do Pagamento</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Price Breakdown */}
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Preço do Pacote</span>
                    <span className="font-semibold text-gray-900">
                      ${priceInfo?.original_price.toFixed(2)}
                    </span>
                  </div>
                  
                  {voucherApplied && priceInfo && priceInfo.discount_percentage > 0 && (
                    <div className="flex justify-between items-center text-green-600">
                      <span>Desconto ({priceInfo.discount_percentage}%)</span>
                      <span className="font-semibold">
                        -${priceInfo.discount_amount.toFixed(2)}
                      </span>
                    </div>
                  )}
                  
                  <div className="border-t pt-3 mt-3">
                    <div className="flex justify-between items-center">
                      <span className="text-lg font-bold text-gray-900">Total</span>
                      <span className="text-2xl font-bold text-blue-600">
                        ${priceInfo?.final_price.toFixed(2)}
                      </span>
                    </div>
                    {voucherApplied && priceInfo && priceInfo.savings > 0 && (
                      <p className="text-sm text-green-600 text-right mt-1">
                        Você economiza ${priceInfo.savings.toFixed(2)}!
                      </p>
                    )}
                  </div>
                </div>

                {/* Voucher Input */}
                <div className="border-t pt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Código de Voucher
                  </label>
                  
                  {!voucherApplied ? (
                    <div className="flex gap-2">
                      <Input
                        type="text"
                        placeholder="Ex: LANCAMENTO50"
                        value={voucherCode}
                        onChange={(e) => setVoucherCode(e.target.value.toUpperCase())}
                        disabled={isValidatingVoucher}
                        className="flex-1"
                      />
                      <Button
                        onClick={handleApplyVoucher}
                        disabled={isValidatingVoucher || !voucherCode.trim()}
                        variant="outline"
                      >
                        {isValidatingVoucher ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          'Aplicar'
                        )}
                      </Button>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg p-3">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <span className="font-mono font-semibold text-green-700">
                          {voucherCode}
                        </span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleRemoveVoucher}
                        className="text-red-600 hover:text-red-700"
                      >
                        Remover
                      </Button>
                    </div>
                  )}
                  
                  {voucherMessage && (
                    <Alert className={`mt-2 ${voucherApplied ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                      <AlertDescription className={voucherApplied ? 'text-green-700' : 'text-red-700'}>
                        {voucherMessage}
                      </AlertDescription>
                    </Alert>
                  )}
                </div>

                {/* Error Message */}
                {error && (
                  <Alert className="bg-red-50 border-red-200">
                    <XCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-700">
                      {error}
                    </AlertDescription>
                  </Alert>
                )}

                {/* Payment Button */}
                <Button
                  onClick={handlePayment}
                  disabled={isProcessingPayment}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6 text-lg"
                >
                  {isProcessingPayment ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Processando...
                    </>
                  ) : (
                    <>
                      <CreditCard className="mr-2 h-5 w-5" />
                      Pagar ${priceInfo?.final_price.toFixed(2)} com Stripe
                    </>
                  )}
                </Button>

                <p className="text-xs text-gray-500 text-center">
                  Pagamento seguro processado por Stripe. Seus dados estão protegidos.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaymentPage;
