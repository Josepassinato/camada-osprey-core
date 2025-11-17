import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle, Loader2, Download, ArrowRight } from 'lucide-react';
import { makeApiCall } from '@/utils/api';

const PaymentSuccess: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const sessionId = searchParams.get('session_id');
  const caseId = searchParams.get('case_id');
  
  const [paymentStatus, setPaymentStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (sessionId) {
      verifyPayment();
    } else {
      setError('ID de sessão ausente');
      setLoading(false);
    }
  }, [sessionId]);

  const verifyPayment = async () => {
    try {
      setLoading(true);
      const response = await makeApiCall(`/payment/status/${sessionId}`, 'GET');
      
      if (response.success && response.payment_status === 'paid') {
        setPaymentStatus(response);
      } else {
        setError('Pagamento ainda não confirmado. Aguarde alguns instantes.');
        // Tentar novamente após 2 segundos
        setTimeout(verifyPayment, 2000);
      }
    } catch (err: any) {
      console.error('Erro ao verificar pagamento:', err);
      setError(err.message || 'Erro ao verificar pagamento');
    } finally {
      setLoading(false);
    }
  };

  const handleContinue = () => {
    if (caseId) {
      navigate(`/auto-application/case/${caseId}/basic-data`);
    } else {
      navigate('/auto-application/start');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto" />
              <p className="text-gray-600">Verificando seu pagamento...</p>
              <p className="text-sm text-gray-500">Por favor, aguarde</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardHeader>
            <CardTitle className="text-yellow-600">Aguarde...</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600">{error}</p>
            <Button onClick={verifyPayment} className="w-full">
              Verificar Novamente
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
      <Card className="max-w-2xl w-full">
        <CardHeader className="text-center pb-4">
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <CheckCircle className="h-10 w-10 text-green-600" />
          </div>
          <CardTitle className="text-2xl sm:text-3xl text-green-700">
            Pagamento Confirmado!
          </CardTitle>
          <CardDescription className="text-lg">
            Seu pagamento foi processado com sucesso
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Payment Details */}
          <div className="bg-white rounded-lg border p-4 space-y-3">
            <h3 className="font-semibold text-gray-900">Detalhes do Pagamento</h3>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Valor Pago</p>
                <p className="font-semibold text-gray-900">
                  ${paymentStatus?.amount_total?.toFixed(2)}
                </p>
              </div>
              
              <div>
                <p className="text-gray-600">ID da Transação</p>
                <p className="font-mono text-xs text-gray-900">
                  {sessionId?.slice(0, 20)}...
                </p>
              </div>
              
              {paymentStatus?.customer_email && (
                <div className="col-span-2">
                  <p className="text-gray-600">Email</p>
                  <p className="font-semibold text-gray-900">
                    {paymentStatus.customer_email}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Next Steps */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">Próximos Passos</h3>
            <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800">
              <li>Continue preenchendo seu formulário</li>
              <li>Revise todas as informações cuidadosamente</li>
              <li>Faça download do PDF completo ao finalizar</li>
              <li>Envie para o USCIS seguindo as instruções</li>
            </ol>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <Button
              onClick={handleContinue}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6 text-lg"
            >
              Continuar para o Formulário
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            
            <p className="text-xs text-gray-500 text-center">
              Um email de confirmação será enviado em breve
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentSuccess;
