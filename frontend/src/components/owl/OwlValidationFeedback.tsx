import React from 'react';
import { CheckCircle, AlertCircle, XCircle, Info, Loader2 } from 'lucide-react';

interface ValidationResult {
  score: number;
  status: 'valid' | 'warning' | 'invalid' | 'pending';
  message: string;
  suggestions?: string[];
}

interface OwlValidationFeedbackProps {
  validation: ValidationResult | null;
  loading?: boolean;
  fieldName: string;
}

export const OwlValidationFeedback: React.FC<OwlValidationFeedbackProps> = ({
  validation,
  loading = false,
  fieldName,
}) => {
  if (loading) {
    return (
      <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
        <span className="text-sm text-blue-700">Validando {fieldName}...</span>
      </div>
    );
  }

  if (!validation) {
    return null;
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'valid':
        return 'green';
      case 'warning':
        return 'blue';
      case 'invalid':
        return 'red';
      default:
        return 'blue';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'valid':
        return <CheckCircle className="w-4 h-4" />;
      case 'warning':
        return <AlertCircle className="w-4 h-4" />;
      case 'invalid':
        return <XCircle className="w-4 h-4" />;
      default:
        return <Info className="w-4 h-4" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const color = getStatusColor(validation.status);

  return (
    <div className={`p-4 border rounded-lg bg-${color}-50 border-${color}-200`}>
      {/* Header with icon and score */}
      <div className="flex items-center justify-between mb-2">
        <div className={`flex items-center gap-2 text-${color}-700`}>
          {getStatusIcon(validation.status)}
          <span className="font-medium text-sm">
            {validation.status === 'valid' && 'Válido'}
            {validation.status === 'warning' && 'Atenção'}
            {validation.status === 'invalid' && 'Inválido'}
            {validation.status === 'pending' && 'Pendente'}
          </span>
        </div>
        <div className={`text-sm font-bold ${getScoreColor(validation.score)}`}>
          {validation.score}%
        </div>
      </div>

      {/* Validation message */}
      <p className={`text-sm text-${color}-800 mb-3`}>
        {validation.message}
      </p>

      {/* Score bar */}
      <div className="mb-3">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
              validation.score >= 80
                ? 'bg-green-500'
                : validation.score >= 60
                ? 'bg-yellow-500'
                : 'bg-red-500'
            }`}
            style={{ width: `${validation.score}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>0%</span>
          <span>Confiança: {validation.score}%</span>
          <span>100%</span>
        </div>
      </div>

      {/* Suggestions */}
      {validation.suggestions && validation.suggestions.length > 0 && (
        <div className={`bg-${color}-100 rounded-lg p-3`}>
          <h4 className={`text-sm font-medium text-${color}-800 mb-2`}>
            💡 Sugestões para melhorar:
          </h4>
          <ul className={`text-sm text-${color}-700 space-y-1`}>
            {validation.suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-xs mt-1">•</span>
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};