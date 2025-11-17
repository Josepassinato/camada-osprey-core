import React from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { XCircle, ArrowLeft, RotateCcw } from 'lucide-react';

const PaymentCancel: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const caseId = searchParams.get('case_id');

  const handleTryAgain = () => {
    navigate(`/payment?case_id=${caseId}&visa_code=${searchParams.get('visa_code') || ''}`);
  };

  const handleBack = () => {
    navigate('/auto-application/select-form');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-gray-50 flex items-center justify-center p-4">
      <Card className="max-w-md w-full">
        <CardHeader className="text-center pb-4">
          <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <XCircle className="h-10 w-10 text-red-600" />
          </div>
          <CardTitle className="text-2xl text-red-700">
            Pagamento Cancelado
          </CardTitle>
          <CardDescription className="text-base">
            Seu pagamento não foi processado
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <div className="bg-white rounded-lg border p-4">
            <p className="text-gray-600 text-sm">
              Não se preocupe! Nenhuma cobrança foi realizada. Você pode tentar novamente quando estiver pronto.
            </p>
          </div>

          <div className="space-y-3">
            <Button
              onClick={handleTryAgain}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            >
              <RotateCcw className="mr-2 h-4 w-4" />
              Tentar Novamente
            </Button>
            
            <Button
              onClick={handleBack}
              variant="outline"
              className="w-full"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Voltar para Seleção de Vistos
            </Button>
          </div>

          <p className="text-xs text-gray-500 text-center">
            Precisa de ajuda? Entre em contato com nosso suporte
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentCancel;
