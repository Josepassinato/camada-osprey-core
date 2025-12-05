import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, Clock, FileText, ArrowRight } from 'lucide-react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

interface VisaType {
  code: string;
  name: string;
  category: string;
  description: string;
  estimated_time: string;
}

const VisaSelection: React.FC = () => {
  const navigate = useNavigate();
  const [visaTypes, setVisaTypes] = useState<VisaType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVisa, setSelectedVisa] = useState<string | null>(null);

  useEffect(() => {
    const loadVisaTypes = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${BACKEND_URL}/api/friendly-form/available-visas`);
        
        if (!response.ok) {
          throw new Error('Não foi possível carregar os tipos de visto');
        }
        
        const data = await response.json();
        setVisaTypes(data.visa_types);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    };

    loadVisaTypes();
  }, []);

  const handleStartApplication = async (visaCode: string) => {
    try {
      setSelectedVisa(visaCode);
      
      // Create a new case
      const response = await fetch(`${BACKEND_URL}/api/auto-application/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          form_code: visaCode,
          process_type: 'extension'
        })
      });
      
      if (!response.ok) {
        throw new Error('Erro ao criar aplicação');
      }
      
      const result = await response.json();
      const caseId = result.case.case_id;
      
      // Navigate to the dynamic form
      navigate(`/friendly-form/${visaCode}/${caseId}`);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao iniciar aplicação');
      setSelectedVisa(null);
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'Não-Imigrante': 'bg-blue-100 text-blue-800',
      'Estudante': 'bg-green-100 text-green-800',
      'Trabalho': 'bg-purple-100 text-purple-800',
      'Turismo': 'bg-yellow-100 text-yellow-800',
      'Habilidade Especial': 'bg-orange-100 text-orange-800',
      'Asilo/Proteção': 'bg-red-100 text-red-800',
      'Imigrante': 'bg-indigo-100 text-indigo-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Carregando tipos de visto...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">
          Selecione o Tipo de Visto
        </h1>
        <p className="text-muted-foreground text-lg">
          Escolha o tipo de aplicação que você deseja fazer
        </p>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {visaTypes.map((visa) => (
          <Card 
            key={visa.code}
            className="hover:shadow-lg transition-shadow cursor-pointer relative overflow-hidden group"
          >
            <CardHeader>
              <div className="flex items-start justify-between mb-2">
                <Badge className={getCategoryColor(visa.category)}>
                  {visa.category}
                </Badge>
                <div className="flex items-center text-sm text-muted-foreground">
                  <Clock className="h-3 w-3 mr-1" />
                  {visa.estimated_time}
                </div>
              </div>
              
              <CardTitle className="text-xl">
                {visa.name}
              </CardTitle>
              
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <FileText className="h-4 w-4" />
                <span className="font-mono font-semibold">{visa.code}</span>
              </div>
            </CardHeader>
            
            <CardContent>
              <CardDescription className="mb-4 min-h-[3rem]">
                {visa.description}
              </CardDescription>
              
              <Button
                onClick={() => handleStartApplication(visa.code)}
                disabled={selectedVisa === visa.code}
                className="w-full group-hover:bg-primary group-hover:text-primary-foreground"
                variant="outline"
              >
                {selectedVisa === visa.code ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                    Iniciando...
                  </>
                ) : (
                  <>
                    Iniciar Aplicação
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Info Section */}
      <Card className="mt-12 bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-900">
            📋 Como funciona?
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-blue-800">
          <div className="flex items-start gap-3">
            <div className="bg-blue-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 font-bold">
              1
            </div>
            <div>
              <strong>Selecione o tipo de visto</strong> que você precisa da lista acima
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="bg-blue-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 font-bold">
              2
            </div>
            <div>
              <strong>Preencha o formulário amigável</strong> em português com suas informações
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="bg-blue-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 font-bold">
              3
            </div>
            <div>
              <strong>Validação inteligente</strong> verifica se seus dados estão completos e corretos
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="bg-blue-200 rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 font-bold">
              4
            </div>
            <div>
              <strong>Formulário oficial USCIS</strong> é preenchido automaticamente com seus dados traduzidos para inglês
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VisaSelection;
