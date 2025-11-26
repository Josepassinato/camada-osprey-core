import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  PaymentElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Loader2, CheckCircle, CreditCard, Shield, Lock, AlertCircle, Tag, Check } from 'lucide-react';
import { makeApiCall } from '@/utils/api';

// Configurar Stripe (usar chave pública)
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || 'pk_live_51PByv6AfnK9GyzVJSxZwdgq3VrYksnja0kN0eSjBq5s4hTVLQQJhgEOhGMKZrfPR7BwPskZhIv6FbUBb4OJ2UjxZXfHxjC00nL6OqN2X');

interface CheckoutFormProps {
  visaCode: string;
  caseId: string;
  clientSecret: string;
  amount: number;
  packageInfo: any;
}

const CheckoutForm: React.FC<CheckoutFormProps> = ({ visaCode, caseId, clientSecret, amount, packageInfo }) => {
  const stripe = useStripe();
  const elements = useElements();
  const navigate = useNavigate();

  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsProcessing(true);
    setErrorMessage('');

    try {
      const { error, paymentIntent } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/payment/success?case_id=${caseId}`,
        },
        redirect: 'if_required'
      });

      if (error) {
        setErrorMessage(error.message || 'Erro ao processar pagamento');
        setIsProcessing(false);
      } else if (paymentIntent && paymentIntent.status === 'succeeded') {
        setPaymentSuccess(true);
        
        // Aguardar 2 segundos e redirecionar para a aplicação
        setTimeout(() => {
          navigate(`/auto-application/case/${caseId}/basic-data`);
        }, 2000);
      }
    } catch (error: any) {
      setErrorMessage(error.message || 'Erro ao processar pagamento');
      setIsProcessing(false);
    }
  };

  if (paymentSuccess) {
    return (
      <div className="text-center py-12">
        <div className="bg-green-50 border border-green-200 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6">
          <CheckCircle className="h-12 w-12 text-green-600" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-3">
          Pagamento Confirmado!
        </h2>
        <p className="text-lg text-gray-600 mb-2">
          Seu pagamento foi processado com sucesso
        </p>
        <div className="flex items-center justify-center gap-2 text-sm text-gray-500 mb-6">
          <Shield className="h-4 w-4 text-green-600" />
          <span>Processado por</span>
          <svg className="h-4" viewBox="0 0 60 25" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M59.64 14.28h-8.06c.19 1.93 1.6 2.55 3.2 2.55 1.64 0 2.96-.37 4.05-.95v3.32a8.33 8.33 0 0 1-4.56 1.1c-4.01 0-6.83-2.5-6.83-7.48 0-4.19 2.39-7.52 6.3-7.52 3.92 0 5.96 3.28 5.96 7.5 0 .4-.04 1.26-.06 1.48zm-5.92-5.62c-1.03 0-2.17.73-2.17 2.58h4.25c0-1.85-1.07-2.58-2.08-2.58zM40.95 20.3c-1.44 0-2.32-.6-2.9-1.04l-.02 4.63-4.12.87V5.57h3.76l.08 1.02a4.7 4.7 0 0 1 3.23-1.29c2.9 0 5.62 2.6 5.62 7.4 0 5.23-2.7 7.6-5.65 7.6zM40 8.95c-.95 0-1.54.34-1.97.81l.02 6.12c.4.44.98.78 1.95.78 1.52 0 2.54-1.65 2.54-3.87 0-2.15-1.04-3.84-2.54-3.84zM28.24 5.57h4.13v14.44h-4.13V5.57zm0-4.7L32.37 0v3.36l-4.13.88V.88zm-4.32 9.35v9.79H19.8V5.57h3.7l.12 1.22c1-1.77 3.07-1.41 3.62-1.22v3.79c-.52-.17-2.29-.43-3.32.86zm-8.55 4.72c0 2.43 2.6 1.68 3.12 1.46v3.36c-.55.3-1.54.54-2.89.54a4.15 4.15 0 0 1-4.27-4.24l.01-13.17 4.02-.86v3.54h3.14V9.1h-3.13v5.85zm-4.91.7c0 2.97-2.31 4.66-5.73 4.66a11.2 11.2 0 0 1-4.46-.93v-3.93c1.38.75 3.1 1.31 4.46 1.31.92 0 1.53-.24 1.53-1C6.26 13.77 0 14.51 0 9.95 0 7.04 2.28 5.3 5.62 5.3c1.36 0 2.72.2 4.09.75v3.88a9.23 9.23 0 0 0-4.1-1.06c-.86 0-1.44.25-1.44.9 0 1.85 6.29.97 6.29 5.88z" fill="#635BFF"/>
          </svg>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 inline-flex items-center gap-2 mb-6">
          <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
          <span className="text-blue-900 font-medium">
            Redirecionando para sua aplicação...
          </span>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Trust Badges */}
      <div className="flex items-center justify-center gap-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
        <Shield className="h-5 w-5 text-blue-600" />
        <span className="text-sm font-medium text-blue-900">
          Processamento seguro via Stripe
        </span>
      </div>

      {/* Payment Element */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <PaymentElement />
      </div>

      {errorMessage && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-red-800">{errorMessage}</p>
        </div>
      )}

      {/* Pay Button - Stripe Style */}
      <Button
        type="submit"
        disabled={!stripe || isProcessing}
        className="w-full h-12 text-base font-semibold shadow-lg"
        style={{
          background: 'linear-gradient(180deg, #635BFF 0%, #5649E0 100%)',
          border: '1px solid #4840C4'
        }}
      >
        {isProcessing ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin mr-2" />
            Processando pagamento...
          </>
        ) : (
          <>
            <Lock className="h-5 w-5 mr-2" />
            Pagar ${amount.toFixed(2)}
          </>
        )}
      </Button>

      {/* Security Badges */}
      <div className="space-y-3 pt-4 border-t">
        <div className="flex items-center justify-center gap-6 text-xs text-gray-600">
          <div className="flex items-center gap-1.5">
            <Shield className="h-4 w-4 text-green-600" />
            <span>PCI DSS Compliant</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Lock className="h-4 w-4 text-green-600" />
            <span>256-bit SSL</span>
          </div>
        </div>
        
        {/* Stripe Badge */}
        <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
          <span>Powered by</span>
          <svg className="h-5 opacity-70" viewBox="0 0 60 25" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M59.64 14.28h-8.06c.19 1.93 1.6 2.55 3.2 2.55 1.64 0 2.96-.37 4.05-.95v3.32a8.33 8.33 0 0 1-4.56 1.1c-4.01 0-6.83-2.5-6.83-7.48 0-4.19 2.39-7.52 6.3-7.52 3.92 0 5.96 3.28 5.96 7.5 0 .4-.04 1.26-.06 1.48zm-5.92-5.62c-1.03 0-2.17.73-2.17 2.58h4.25c0-1.85-1.07-2.58-2.08-2.58zM40.95 20.3c-1.44 0-2.32-.6-2.9-1.04l-.02 4.63-4.12.87V5.57h3.76l.08 1.02a4.7 4.7 0 0 1 3.23-1.29c2.9 0 5.62 2.6 5.62 7.4 0 5.23-2.7 7.6-5.65 7.6zM40 8.95c-.95 0-1.54.34-1.97.81l.02 6.12c.4.44.98.78 1.95.78 1.52 0 2.54-1.65 2.54-3.87 0-2.15-1.04-3.84-2.54-3.84zM28.24 5.57h4.13v14.44h-4.13V5.57zm0-4.7L32.37 0v3.36l-4.13.88V.88zm-4.32 9.35v9.79H19.8V5.57h3.7l.12 1.22c1-1.77 3.07-1.41 3.62-1.22v3.79c-.52-.17-2.29-.43-3.32.86zm-8.55 4.72c0 2.43 2.6 1.68 3.12 1.46v3.36c-.55.3-1.54.54-2.89.54a4.15 4.15 0 0 1-4.27-4.24l.01-13.17 4.02-.86v3.54h3.14V9.1h-3.13v5.85zm-4.91.7c0 2.97-2.31 4.66-5.73 4.66a11.2 11.2 0 0 1-4.46-.93v-3.93c1.38.75 3.1 1.31 4.46 1.31.92 0 1.53-.24 1.53-1C6.26 13.77 0 14.51 0 9.95 0 7.04 2.28 5.3 5.62 5.3c1.36 0 2.72.2 4.09.75v3.88a9.23 9.23 0 0 0-4.1-1.06c-.86 0-1.44.25-1.44.9 0 1.85 6.29.97 6.29 5.88z" fill="#9CA3AF"/>
          </svg>
          <span className="text-gray-400">•</span>
          <span>Seus dados nunca são armazenados</span>
        </div>

        {/* Card Brands */}
        <div className="flex items-center justify-center gap-3 pt-2">
          <div className="text-xs text-gray-500">Aceitamos:</div>
          <div className="flex gap-2 items-center">
            {/* Visa */}
            <div className="w-10 h-6 bg-white border border-gray-200 rounded flex items-center justify-center">
              <span className="text-xs font-bold text-blue-700">VISA</span>
            </div>
            {/* Mastercard */}
            <div className="w-10 h-6 bg-white border border-gray-200 rounded flex items-center justify-center">
              <div className="flex gap-0.5">
                <div className="w-2 h-2 rounded-full bg-red-500"></div>
                <div className="w-2 h-2 rounded-full bg-orange-500"></div>
              </div>
            </div>
            {/* Amex */}
            <div className="w-10 h-6 bg-blue-500 rounded flex items-center justify-center">
              <span className="text-[8px] font-bold text-white">AMEX</span>
            </div>
          </div>
        </div>
      </div>
    </form>
  );
};

const EmbeddedCheckout = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const visaCode = searchParams.get('visa_code');
  const caseId = searchParams.get('case_id');

  const [loading, setLoading] = useState(true);
  const [clientSecret, setClientSecret] = useState('');
  const [packageInfo, setPackageInfo] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!visaCode || !caseId) {
      setError('Parâmetros inválidos');
      setLoading(false);
      return;
    }

    createPaymentIntent();
  }, [visaCode, caseId]);

  const createPaymentIntent = async () => {
    try {
      setLoading(true);
      
      const data = await makeApiCall('/payment/create-payment-intent', 'POST', {
        visa_code: visaCode,
        case_id: caseId
      });

      if (data.success) {
        setClientSecret(data.client_secret);
        setPackageInfo(data.package);
      } else {
        setError(data.error || 'Erro ao criar pagamento');
      }
    } catch (error: any) {
      setError(error.message || 'Erro ao carregar checkout');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-purple-600 mx-auto mb-4" />
          <p className="text-gray-600">Carregando checkout...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="max-w-md w-full mx-4">
          <CardHeader>
            <CardTitle className="text-red-600">Erro</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">{error}</p>
            <Button onClick={() => navigate('/auto-application/select-form')} variant="outline" className="w-full">
              Voltar
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Stripe Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 bg-white px-6 py-3 rounded-full shadow-sm border border-gray-200 mb-4">
            <Shield className="h-5 w-5 text-green-600" />
            <span className="text-sm font-medium text-gray-700">
              Pagamento seguro processado por
            </span>
            <svg className="h-6" viewBox="0 0 60 25" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M59.64 14.28h-8.06c.19 1.93 1.6 2.55 3.2 2.55 1.64 0 2.96-.37 4.05-.95v3.32a8.33 8.33 0 0 1-4.56 1.1c-4.01 0-6.83-2.5-6.83-7.48 0-4.19 2.39-7.52 6.3-7.52 3.92 0 5.96 3.28 5.96 7.5 0 .4-.04 1.26-.06 1.48zm-5.92-5.62c-1.03 0-2.17.73-2.17 2.58h4.25c0-1.85-1.07-2.58-2.08-2.58zM40.95 20.3c-1.44 0-2.32-.6-2.9-1.04l-.02 4.63-4.12.87V5.57h3.76l.08 1.02a4.7 4.7 0 0 1 3.23-1.29c2.9 0 5.62 2.6 5.62 7.4 0 5.23-2.7 7.6-5.65 7.6zM40 8.95c-.95 0-1.54.34-1.97.81l.02 6.12c.4.44.98.78 1.95.78 1.52 0 2.54-1.65 2.54-3.87 0-2.15-1.04-3.84-2.54-3.84zM28.24 5.57h4.13v14.44h-4.13V5.57zm0-4.7L32.37 0v3.36l-4.13.88V.88zm-4.32 9.35v9.79H19.8V5.57h3.7l.12 1.22c1-1.77 3.07-1.41 3.62-1.22v3.79c-.52-.17-2.29-.43-3.32.86zm-8.55 4.72c0 2.43 2.6 1.68 3.12 1.46v3.36c-.55.3-1.54.54-2.89.54a4.15 4.15 0 0 1-4.27-4.24l.01-13.17 4.02-.86v3.54h3.14V9.1h-3.13v5.85zm-4.91.7c0 2.97-2.31 4.66-5.73 4.66a11.2 11.2 0 0 1-4.46-.93v-3.93c1.38.75 3.1 1.31 4.46 1.31.92 0 1.53-.24 1.53-1C6.26 13.77 0 14.51 0 9.95 0 7.04 2.28 5.3 5.62 5.3c1.36 0 2.72.2 4.09.75v3.88a9.23 9.23 0 0 0-4.1-1.06c-.86 0-1.44.25-1.44.9 0 1.85 6.29.97 6.29 5.88z" fill="#635BFF"/>
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Checkout Seguro
          </h1>
          <p className="text-gray-600">
            Seus dados são criptografados e protegidos
          </p>
        </div>

        <div className="grid md:grid-cols-5 gap-6">
          {/* Order Summary - 2 cols */}
          <div className="md:col-span-2">
            <Card className="shadow-lg border-gray-200">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <CreditCard className="h-5 w-5 text-blue-600" />
                  Resumo do Pedido
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 pt-6">
              <div>
                <p className="text-sm text-gray-600 mb-1">Produto</p>
                <p className="font-semibold text-gray-900">
                  {packageInfo?.name || visaCode}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  {packageInfo?.description}
                </p>
              </div>

              <div className="border-t pt-4">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="text-gray-900">${packageInfo?.price?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between font-bold text-lg">
                  <span>Total</span>
                  <span className="text-purple-600">${packageInfo?.price?.toFixed(2)}</span>
                </div>
              </div>

              {packageInfo?.includes && (
                <div className="border-t pt-4">
                  <p className="text-sm font-semibold text-gray-900 mb-2">
                    O que está incluído:
                  </p>
                  <ul className="space-y-1">
                    {packageInfo.includes.map((item: string, index: number) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                        <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
          </div>

          {/* Payment Form - 3 cols */}
          <div className="md:col-span-3">
            <Card className="shadow-lg border-gray-200">
              <CardHeader className="border-b bg-white">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Informações de Pagamento</CardTitle>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Lock className="h-3 w-3" />
                    <span>Powered by</span>
                    <svg className="h-4" viewBox="0 0 60 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M59.64 14.28h-8.06c.19 1.93 1.6 2.55 3.2 2.55 1.64 0 2.96-.37 4.05-.95v3.32a8.33 8.33 0 0 1-4.56 1.1c-4.01 0-6.83-2.5-6.83-7.48 0-4.19 2.39-7.52 6.3-7.52 3.92 0 5.96 3.28 5.96 7.5 0 .4-.04 1.26-.06 1.48zm-5.92-5.62c-1.03 0-2.17.73-2.17 2.58h4.25c0-1.85-1.07-2.58-2.08-2.58zM40.95 20.3c-1.44 0-2.32-.6-2.9-1.04l-.02 4.63-4.12.87V5.57h3.76l.08 1.02a4.7 4.7 0 0 1 3.23-1.29c2.9 0 5.62 2.6 5.62 7.4 0 5.23-2.7 7.6-5.65 7.6zM40 8.95c-.95 0-1.54.34-1.97.81l.02 6.12c.4.44.98.78 1.95.78 1.52 0 2.54-1.65 2.54-3.87 0-2.15-1.04-3.84-2.54-3.84zM28.24 5.57h4.13v14.44h-4.13V5.57zm0-4.7L32.37 0v3.36l-4.13.88V.88zm-4.32 9.35v9.79H19.8V5.57h3.7l.12 1.22c1-1.77 3.07-1.41 3.62-1.22v3.79c-.52-.17-2.29-.43-3.32.86zm-8.55 4.72c0 2.43 2.6 1.68 3.12 1.46v3.36c-.55.3-1.54.54-2.89.54a4.15 4.15 0 0 1-4.27-4.24l.01-13.17 4.02-.86v3.54h3.14V9.1h-3.13v5.85zm-4.91.7c0 2.97-2.31 4.66-5.73 4.66a11.2 11.2 0 0 1-4.46-.93v-3.93c1.38.75 3.1 1.31 4.46 1.31.92 0 1.53-.24 1.53-1C6.26 13.77 0 14.51 0 9.95 0 7.04 2.28 5.3 5.62 5.3c1.36 0 2.72.2 4.09.75v3.88a9.23 9.23 0 0 0-4.1-1.06c-.86 0-1.44.25-1.44.9 0 1.85 6.29.97 6.29 5.88z" fill="#635BFF"/>
                    </svg>
                  </div>
                </div>
                <CardDescription className="flex items-center gap-1 text-xs mt-2">
                  <Shield className="h-3 w-3 text-green-600" />
                  <span>Seus dados de pagamento são criptografados e seguros</span>
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
              {clientSecret && (
                <Elements 
                  stripe={stripePromise} 
                  options={{
                    clientSecret,
                    appearance: {
                      theme: 'stripe',
                      variables: {
                        colorPrimary: '#9333ea',
                      }
                    }
                  }}
                >
                  <CheckoutForm
                    visaCode={visaCode || ''}
                    caseId={caseId || ''}
                    clientSecret={clientSecret}
                    amount={packageInfo?.price || 0}
                    packageInfo={packageInfo}
                  />
                </Elements>
              )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmbeddedCheckout;
