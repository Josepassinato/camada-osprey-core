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
import { Loader2, CheckCircle, CreditCard, Shield, Lock } from 'lucide-react';
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
      <div className="text-center py-8">
        <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Pagamento Confirmado!
        </h2>
        <p className="text-gray-600 mb-4">
          Redirecionando para sua aplicação...
        </p>
        <Loader2 className="h-6 w-6 animate-spin text-purple-600 mx-auto" />
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Informações de Pagamento
        </h3>
        <p className="text-sm text-gray-600">
          Preencha os dados do seu cartão de forma segura
        </p>
      </div>

      <PaymentElement />

      {errorMessage && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{errorMessage}</p>
        </div>
      )}

      <Button
        type="submit"
        disabled={!stripe || isProcessing}
        className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 h-12 text-lg"
      >
        {isProcessing ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin mr-2" />
            Processando...
          </>
        ) : (
          <>
            <Lock className="h-5 w-5 mr-2" />
            Pagar ${amount.toFixed(2)}
          </>
        )}
      </Button>

      <div className="flex items-center justify-center gap-4 text-xs text-gray-500">
        <div className="flex items-center gap-1">
          <Shield className="h-4 w-4" />
          <span>Pagamento 100% seguro</span>
        </div>
        <div className="flex items-center gap-1">
          <Lock className="h-4 w-4" />
          <span>Criptografia SSL</span>
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
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="grid md:grid-cols-2 gap-6">
          {/* Order Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5" />
                Resumo do Pedido
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
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

          {/* Payment Form */}
          <Card>
            <CardHeader>
              <CardTitle>Finalizar Pagamento</CardTitle>
              <CardDescription>
                Pagamento seguro processado pelo Stripe
              </CardDescription>
            </CardHeader>
            <CardContent>
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
  );
};

export default EmbeddedCheckout;
