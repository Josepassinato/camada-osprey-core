import { useEffect, useState } from 'react';

interface LoadingModalProps {
  isOpen: boolean;
  message?: string;
}

export function LoadingModal({ isOpen, message = "Processando..." }: LoadingModalProps) {
  const [dots, setDots] = useState('');

  useEffect(() => {
    if (!isOpen) return;

    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.');
    }, 500);

    return () => clearInterval(interval);
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="bg-white rounded-lg shadow-2xl p-8 max-w-sm w-full mx-4 animate-in fade-in duration-200">
        <div className="flex flex-col items-center space-y-4">
          {/* Animated spinner - same as "Carregando simulação..." */}
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black"></div>

          {/* Message */}
          <div className="text-center">
            <p className="text-lg font-medium text-gray-900">
              {message}
              <span className="inline-block w-8 text-left">{dots}</span>
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Isso pode levar alguns segundos
            </p>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
            <div className="h-full bg-black rounded-full animate-pulse" style={{ width: '60%' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}
