import React from 'react';
import { Progress } from '@/components/ui/progress';
import { CheckCircle, Circle, Clock } from 'lucide-react';

interface OwlProgressTrackerProps {
  progress: number;
  currentStep: number;
  totalSteps: number;
  steps: Array<{
    id: string;
    title: string;
    completed: boolean;
    current: boolean;
  }>;
}

export const OwlProgressTracker: React.FC<OwlProgressTrackerProps> = ({
  progress,
  currentStep,
  totalSteps,
  steps,
}) => {
  return (
    <div className="w-full bg-white rounded-lg shadow-sm border p-6">
      {/* Owl mascot header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
          <span className="text-2xl">🦉</span>
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">Progresso do Questionário</h3>
          <p className="text-sm text-gray-600">
            Passo {currentStep} de {totalSteps} • {Math.round(progress)}% concluído
          </p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="mb-6">
        <Progress value={progress} className="h-3" />
        <div className="flex justify-between text-xs text-gray-500 mt-2">
          <span>0%</span>
          <span className="font-medium">{Math.round(progress)}%</span>
          <span>100%</span>
        </div>
      </div>

      {/* Steps list */}
      <div className="space-y-3">
        {steps.map((step, index) => (
          <div
            key={step.id}
            className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
              step.current
                ? 'bg-blue-50 border border-blue-200'
                : step.completed
                ? 'bg-green-50'
                : 'bg-gray-50'
            }`}
          >
            <div className="flex-shrink-0">
              {step.completed ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : step.current ? (
                <Clock className="w-5 h-5 text-blue-600" />
              ) : (
                <Circle className="w-5 h-5 text-gray-400" />
              )}
            </div>
            <div className="flex-1">
              <p
                className={`text-sm font-medium ${
                  step.current
                    ? 'text-blue-900'
                    : step.completed
                    ? 'text-green-900'
                    : 'text-gray-600'
                }`}
              >
                {step.title}
              </p>
            </div>
            <div className="text-xs text-gray-500">
              {step.completed ? '✓' : step.current ? '→' : ''}
            </div>
          </div>
        ))}
      </div>

      {/* Completion message */}
      {progress === 100 && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <p className="text-sm font-medium text-green-900">
              Questionário concluído com sucesso!
            </p>
          </div>
          <p className="text-xs text-green-700 mt-1">
            Agora você pode gerar seu formulário USCIS.
          </p>
        </div>
      )}
    </div>
  );
};