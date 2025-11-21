import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowRight, 
  ArrowLeft,
  CheckCircle, 
  FileText, 
  Clock, 
  DollarSign,
  AlertTriangle,
  Shield,
  Loader2
} from 'lucide-react';

const VisaPreview = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const visaCode = searchParams.get('visa_code');
  const caseId = searchParams.get('case_id');
  
  const [loading, setLoading] = useState(true);
  const [visaDetails, setVisaDetails] = useState<any>(null);

  useEffect(() => {
    loadVisaDetails();
  }, [visaCode]);

  const loadVisaDetails = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/visa-requirements/${visaCode}`);
      if (response.ok) {
        const data = await response.json();
        setVisaDetails(data);
      }
    } catch (error) {
      console.error('Error loading visa details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = () => {
    // Redirect to payment
    navigate(`/payment?visa_code=${visaCode}&case_id=${caseId}`);
  };

  const handleBack = () => {
    navigate('/auto-application/select-form');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
      </div>
    );
  }

  // Default details if API call fails
  const details = visaDetails || getDefaultVisaDetails(visaCode);

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            {details.title}
          </h1>
          <p className="text-lg text-gray-600">
            Veja os passos da jornada e documentos necessários
          </p>
        </div>

        {/* Visa Overview */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-6 w-6 text-purple-600" />
              Visão Geral
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 mb-4">{details.description}</p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                <Clock className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-600">Tempo de Processamento</p>
                  <p className="font-semibold text-gray-900">{details.processingTime}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                <DollarSign className="h-5 w-5 text-green-600" />
                <div>
                  <p className="text-sm text-gray-600">Taxa USCIS</p>
                  <p className="font-semibold text-gray-900">{details.uscisfee}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
                <Shield className="h-5 w-5 text-purple-600" />
                <div>
                  <p className="text-sm text-gray-600">Complexidade</p>
                  <Badge variant="outline">{details.complexity}</Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Journey Steps */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-6 w-6 text-purple-600" />
              Passos da Jornada
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {details.steps.map((step: any, index: number) => (
                <div key={index} className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">{step.title}</h3>
                    <p className="text-sm text-gray-600">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Required Documents */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-6 w-6 text-purple-600" />
              Documentos Necessários
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {details.documents.map((doc: string, index: number) => (
                <li key={index} className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{doc}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Important Notes */}
        <Card className="mb-8 border-amber-200 bg-amber-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-900">
              <AlertTriangle className="h-6 w-6 text-amber-600" />
              Importante Saber
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-amber-900">
              <li>• Você terá acesso vitalício ao seu formulário preenchido</li>
              <li>• Poderá salvar seu progresso a qualquer momento</li>
              <li>• Nosso sistema te guiará em português passo a passo</li>
              <li>• Após finalizar, o link de download expira em 24 horas</li>
              <li>• Não guardamos suas informações após o download</li>
            </ul>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-between">
          <Button
            variant="outline"
            onClick={handleBack}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Voltar para Seleção
          </Button>
          
          <Button
            onClick={handleConfirm}
            className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 flex items-center gap-2"
          >
            Confirmar e Ir para Pagamento
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

// Default visa details
const getDefaultVisaDetails = (visaCode: string | null) => {
  const defaults: Record<string, any> = {
    'I-539': {
      title: 'I-539 - Extensão de Visto de Turista',
      description: 'Estenda sua estadia nos EUA mantendo seu status legal de visitante.',
      processingTime: '4-8 meses',
      uscisfee: '$370',
      complexity: 'Básico',
      steps: [
        { title: 'Dados Básicos', description: 'Preencha suas informações pessoais e de passaporte' },
        { title: 'Upload de Documentos', description: 'Envie cópias de documentos necessários' },
        { title: 'Revisão do Sistema', description: 'Nosso sistema revisa e traduz automaticamente' },
        { title: 'Formulário USCIS', description: 'Formulário oficial preenchido e pronto' },
        { title: 'Download Final', description: 'Baixe seu pacote completo para submissão' }
      ],
      documents: [
        'Passaporte válido',
        'I-94 (registro de entrada/saída)',
        'Comprovante financeiro',
        'Carta explicando motivo da extensão',
        'Cópia do visto anterior'
      ]
    },
    'F-1': {
      title: 'F-1 - Visto de Estudante',
      description: 'Obtenha autorização para estudar em instituição acadêmica nos EUA.',
      processingTime: 'Varia',
      uscisfee: '$350',
      complexity: 'Intermediário',
      steps: [
        { title: 'Dados Básicos', description: 'Informações pessoais e educacionais' },
        { title: 'Detalhes da Escola', description: 'Informações sobre a instituição e programa' },
        { title: 'Documentação Financeira', description: 'Comprovação de recursos' },
        { title: 'Revisão e Tradução', description: 'Sistema prepara documentos' },
        { title: 'Pacote Final', description: 'Download de todos os documentos' }
      ],
      documents: [
        'Passaporte válido',
        'Formulário I-20 da escola',
        'Comprovante financeiro',
        'Histórico escolar',
        'Carta de aceitação da instituição',
        'Comprovante de pagamento SEVIS'
      ]
    }
  };

  return defaults[visaCode || 'I-539'] || defaults['I-539'];
};

export default VisaPreview;
