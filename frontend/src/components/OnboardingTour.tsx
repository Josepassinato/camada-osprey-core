import React, { useState, useEffect } from 'react';
import { X, ChevronLeft, ChevronRight, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  targetSelector?: string;  // CSS selector do elemento alvo
  position?: 'top' | 'bottom' | 'left' | 'right';
  action?: () => void;  // Ação ao avançar
}

interface OnboardingTourProps {
  steps: OnboardingStep[];
  onComplete: () => void;
  onSkip: () => void;
  show: boolean;
}

const OnboardingTour: React.FC<OnboardingTourProps> = ({
  steps,
  onComplete,
  onSkip,
  show
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [targetPosition, setTargetPosition] = useState<{ top: number; left: number } | null>(null);

  useEffect(() => {
    if (!show) return;

    const updatePosition = () => {
      const step = steps[currentStep];
      if (step.targetSelector) {
        const element = document.querySelector(step.targetSelector);
        if (element) {
          const rect = element.getBoundingClientRect();
          setTargetPosition({
            top: rect.top + rect.height + 10,
            left: rect.left
          });
          
          // Scroll para o elemento
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
          
          // Highlight do elemento
          element.classList.add('onboarding-highlight');
          return () => element.classList.remove('onboarding-highlight');
        }
      } else {
        setTargetPosition(null);
      }
    };

    updatePosition();
    window.addEventListener('resize', updatePosition);
    
    return () => {
      window.removeEventListener('resize', updatePosition);
    };
  }, [currentStep, show, steps]);

  const handleNext = () => {
    // Executar ação se existir
    if (steps[currentStep].action) {
      steps[currentStep].action!();
    }

    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    // Salvar que pulou onboarding
    localStorage.setItem('onboarding_skipped', 'true');
    onSkip();
  };

  if (!show) return null;

  const step = steps[currentStep];
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity" />

      {/* Tooltip Card */}
      <div
        className="fixed z-50 bg-white rounded-lg shadow-2xl p-6 max-w-md w-full transition-all"
        style={
          targetPosition
            ? {
                top: `${targetPosition.top}px`,
                left: `${targetPosition.left}px`,
                transform: 'translateX(-50%)'
              }
            : {
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)'
              }
        }
      >
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-blue-100 text-blue-700 text-xs font-semibold px-2 py-1 rounded">
                {currentStep + 1} de {steps.length}
              </span>
              <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-600 transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
            <h3 className="text-xl font-bold text-gray-900">{step.title}</h3>
          </div>
          <button
            onClick={handleSkip}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            title="Pular tour"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <p className="text-gray-700 mb-6 leading-relaxed">
          {step.description}
        </p>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <div className="flex gap-2">
            {currentStep > 0 && (
              <Button
                variant="outline"
                onClick={handlePrevious}
                className="gap-2"
              >
                <ChevronLeft className="w-4 h-4" />
                Anterior
              </Button>
            )}
          </div>

          <div className="flex gap-2">
            <Button
              variant="ghost"
              onClick={handleSkip}
              className="text-gray-600"
            >
              Pular
            </Button>
            <Button
              onClick={handleNext}
              className="gap-2"
            >
              {currentStep === steps.length - 1 ? (
                <>
                  <Check className="w-4 h-4" />
                  Concluir
                </>
              ) : (
                <>
                  Próximo
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Global styles for highlight */}
      <style>{`
        .onboarding-highlight {
          position: relative;
          z-index: 45;
          box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.5),
                      0 0 0 9999px rgba(0, 0, 0, 0.5);
          border-radius: 8px;
          transition: all 0.3s ease;
        }
      `}</style>
    </>
  );
};

// Predefined onboarding flows
export const dashboardOnboarding: OnboardingStep[] = [
  {
    id: 'welcome',
    title: '👋 Bem-vindo ao OSPREY Immigration!',
    description: 'Vamos fazer um tour rápido pela plataforma para você começar. Leva apenas 2 minutos!',
  },
  {
    id: 'new-application',
    title: '📝 Iniciar Nova Aplicação',
    description: 'Clique aqui para começar uma nova aplicação de visto. Nós guiaremos você passo a passo.',
    targetSelector: '[data-tour="new-application"]',
  },
  {
    id: 'application-list',
    title: '📋 Suas Aplicações',
    description: 'Aqui você pode ver todas as suas aplicações em andamento. Você pode pausar e retomar a qualquer momento.',
    targetSelector: '[data-tour="application-list"]',
  },
  {
    id: 'maria-chat',
    title: '💬 Converse com Maria',
    description: 'Maria é nossa assistente virtual. Ela pode responder perguntas sobre processos de imigração a qualquer momento!',
    targetSelector: '[data-tour="maria-chat"]',
  },
  {
    id: 'documents',
    title: '📄 Upload de Documentos',
    description: 'Nossa IA verifica automaticamente seus documentos e até corrige dados do cadastro se necessário.',
    targetSelector: '[data-tour="documents"]',
  },
  {
    id: 'complete',
    title: '🎉 Tudo Pronto!',
    description: 'Você está pronto para começar. Se precisar de ajuda, basta clicar no ícone de chat para falar com Maria.',
  }
];

export const formOnboarding: OnboardingStep[] = [
  {
    id: 'friendly-form',
    title: '📝 Formulário Amigável',
    description: 'Este é nosso formulário simplificado. Respondemos em português e convertemos automaticamente para o formato oficial do USCIS.',
  },
  {
    id: 'validation',
    title: '✅ Validação em Tempo Real',
    description: 'Validamos suas respostas em tempo real e alertamos sobre requisitos legais importantes.',
  },
  {
    id: 'save-progress',
    title: '💾 Salvar Progresso',
    description: 'Seu progresso é salvo automaticamente. Você pode sair e voltar a qualquer momento.',
  },
  {
    id: 'pdf-generation',
    title: '📄 Geração de PDF',
    description: 'Quando terminar, geramos automaticamente o PDF oficial pronto para envio ao USCIS.',
  }
];

export default OnboardingTour;
