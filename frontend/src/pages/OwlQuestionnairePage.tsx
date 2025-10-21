import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Home } from 'lucide-react';
import { OwlSessionProvider, useOwlSession } from '@/components/owl/OwlSessionManager';
import { OwlQuestionnaire } from '@/components/owl/OwlQuestionnaire';
import { OwlFormGenerator } from '@/components/owl/OwlFormGenerator';

const OwlQuestionnaireContent: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { state, startSession } = useOwlSession();
  const [showFormGenerator, setShowFormGenerator] = useState(false);

  const visaType = searchParams.get('visa') || 'H-1B';
  const language = searchParams.get('lang') || 'pt';

  useEffect(() => {
    if (!state.session) {
      startSession(visaType, language);
    }
  }, [visaType, language, state.session]);

  // Show form generator when questionnaire is complete (progress >= 90%)
  useEffect(() => {
    if (state.session && state.session.progress >= 90) {
      setShowFormGenerator(true);
    }
  }, [state.session?.progress]);

  const handleBackToHome = () => {
    navigate('/owl-agent');
  };

  const handleBackToQuestionnaire = () => {
    setShowFormGenerator(false);
  };

  if (state.loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-4xl">🦉</span>
          </div>
          <p className="text-lg text-gray-600">Iniciando sessão do Agente Coruja...</p>
        </div>
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-4xl">❌</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Erro na Sessão</h2>
          <p className="text-gray-600 mb-4">{state.error}</p>
          <Button onClick={handleBackToHome} variant="outline">
            <Home className="w-4 h-4 mr-2" />
            Voltar ao Início
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                onClick={showFormGenerator ? handleBackToQuestionnaire : handleBackToHome}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                {showFormGenerator ? 'Voltar ao Questionário' : 'Voltar ao Início'}
              </Button>
              
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-xl">🦉</span>
                </div>
                <div>
                  <h1 className="font-semibold text-gray-900">
                    {showFormGenerator ? 'Gerador de Formulários' : 'Questionário Inteligente'}
                  </h1>
                  <p className="text-sm text-gray-600">
                    {state.session?.visa_type} • {language === 'pt' ? 'Português' : 'English'}
                  </p>
                </div>
              </div>
            </div>

            {state.session && (
              <div className="text-right">
                <p className="text-sm text-gray-600">
                  Progresso: {Math.round(state.session.progress)}%
                </p>
                <p className="text-xs text-gray-500">
                  Sessão: {state.session.session_id.slice(0, 8)}...
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="py-8">
        {showFormGenerator ? (
          <div className="max-w-4xl mx-auto px-4">
            <OwlFormGenerator />
            
            {/* Option to go back to questionnaire */}
            <div className="mt-8 text-center">
              <Button
                variant="outline"
                onClick={handleBackToQuestionnaire}
                className="mr-4"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Voltar ao Questionário
              </Button>
              
              <Button
                onClick={() => setShowFormGenerator(true)}
                className="bg-green-600 hover:bg-green-700"
              >
                Continuar com Formulários
              </Button>
            </div>
          </div>
        ) : (
          <OwlQuestionnaire />
        )}
      </div>

      {/* Footer */}
      <div className="bg-white border-t mt-16">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <span className="text-lg">🦉</span>
              <span>Agente Coruja - Sistema Inteligente de Questionários</span>
            </div>
            <div className="flex items-center gap-4">
              <span>Powered by sistema</span>
              <span>•</span>
              <span>USCIS Compliant</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export const OwlQuestionnairePage: React.FC = () => {
  return (
    <OwlSessionProvider>
      <OwlQuestionnaireContent />
    </OwlSessionProvider>
  );
};