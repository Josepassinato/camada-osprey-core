import { useState, useEffect } from 'react';

interface UseOnboardingProps {
  onboardingKey: string;  // Chave única para identificar qual onboarding (ex: 'dashboard', 'form')
  autoStart?: boolean;    // Iniciar automaticamente se não completado
}

interface UseOnboardingReturn {
  showOnboarding: boolean;
  startOnboarding: () => void;
  completeOnboarding: () => void;
  skipOnboarding: () => void;
  resetOnboarding: () => void;
  isCompleted: boolean;
}

export const useOnboarding = ({
  onboardingKey,
  autoStart = true
}: UseOnboardingProps): UseOnboardingReturn => {
  const storageKey = `onboarding_${onboardingKey}`;
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    // Verificar se já completou ou pulou o onboarding
    const completed = localStorage.getItem(`${storageKey}_completed`) === 'true';
    const skipped = localStorage.getItem(`${storageKey}_skipped`) === 'true';
    
    setIsCompleted(completed);

    // Se não completou nem pulou, e autoStart está ativo, iniciar automaticamente
    if (!completed && !skipped && autoStart) {
      // Delay pequeno para garantir que a página carregou
      const timer = setTimeout(() => {
        setShowOnboarding(true);
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [onboardingKey, autoStart, storageKey]);

  const startOnboarding = () => {
    setShowOnboarding(true);
  };

  const completeOnboarding = () => {
    localStorage.setItem(`${storageKey}_completed`, 'true');
    localStorage.removeItem(`${storageKey}_skipped`);
    setShowOnboarding(false);
    setIsCompleted(true);
    
    // Enviar analytics (opcional)
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'onboarding_completed', {
        onboarding_type: onboardingKey
      });
    }
  };

  const skipOnboarding = () => {
    localStorage.setItem(`${storageKey}_skipped`, 'true');
    setShowOnboarding(false);
    
    // Enviar analytics (opcional)
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'onboarding_skipped', {
        onboarding_type: onboardingKey
      });
    }
  };

  const resetOnboarding = () => {
    localStorage.removeItem(`${storageKey}_completed`);
    localStorage.removeItem(`${storageKey}_skipped`);
    setIsCompleted(false);
    setShowOnboarding(false);
  };

  return {
    showOnboarding,
    startOnboarding,
    completeOnboarding,
    skipOnboarding,
    resetOnboarding,
    isCompleted
  };
};

export default useOnboarding;
