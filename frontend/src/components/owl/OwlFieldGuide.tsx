import React, { useState, useEffect } from 'react';
import { Info, Lightbulb, AlertTriangle, ExternalLink } from 'lucide-react';
import { useOwlSession } from './OwlSessionManager';

interface FieldGuide {
  field_id: string;
  title: string;
  description: string;
  tips: string[];
  examples: string[];
  importance_level: number;
  visa_specific_notes?: string;
  common_mistakes?: string[];
  uscis_requirements?: string;
}

interface OwlFieldGuideProps {
  fieldId: string;
  className?: string;
}

export const OwlFieldGuide: React.FC<OwlFieldGuideProps> = ({ fieldId, className = '' }) => {
  const { state } = useOwlSession();
  const [guide, setGuide] = useState<FieldGuide | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getBackendUrl = () => {
    return import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  };

  useEffect(() => {
    const fetchFieldGuide = async () => {
      if (!state.session || !fieldId) return;

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `${getBackendUrl()}/api/owl-agent/field-guidance/${state.session.session_id}/${fieldId}`
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch field guide: ${response.statusText}`);
        }

        const data = await response.json();
        setGuide(data.guide);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchFieldGuide();
  }, [fieldId, state.session]);

  if (loading) {
    return (
      <div className={`bg-blue-50 border border-blue-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm text-blue-700">Carregando orientações...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-600" />
          <span className="text-sm text-red-700">Erro ao carregar orientações: {error}</span>
        </div>
      </div>
    );
  }

  if (!guide) {
    return null;
  }

  const getImportanceColor = (level: number) => {
    if (level >= 4) return 'red';
    if (level >= 3) return 'yellow';
    return 'blue';
  };

  const importanceColor = getImportanceColor(guide.importance_level);

  return (
    <div className={`bg-white border rounded-lg shadow-sm ${className}`}>
      {/* Header with owl mascot */}
      <div className={`bg-${importanceColor}-50 border-b border-${importanceColor}-200 p-4`}>
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-lg">🦉</span>
          </div>
          <div className="flex-1">
            <h3 className={`font-semibold text-${importanceColor}-900`}>{guide.title}</h3>
            <p className={`text-sm text-${importanceColor}-700 mt-1`}>{guide.description}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className={`text-xs px-2 py-1 bg-${importanceColor}-100 text-${importanceColor}-800 rounded-full`}>
                Importância: {guide.importance_level}/5
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Tips section */}
        {guide.tips && guide.tips.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Lightbulb className="w-4 h-4 text-yellow-600" />
              <h4 className="font-medium text-gray-900">Dicas importantes:</h4>
            </div>
            <ul className="space-y-1">
              {guide.tips.map((tip, index) => (
                <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                  <span className="text-yellow-600 mt-1">💡</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Examples section */}
        {guide.examples && guide.examples.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Info className="w-4 h-4 text-blue-600" />
              <h4 className="font-medium text-gray-900">Exemplos:</h4>
            </div>
            <ul className="space-y-1">
              {guide.examples.map((example, index) => (
                <li key={index} className="text-sm text-gray-700 bg-gray-50 p-2 rounded">
                  <span className="font-mono">{example}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Common mistakes */}
        {guide.common_mistakes && guide.common_mistakes.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-4 h-4 text-red-600" />
              <h4 className="font-medium text-gray-900">Erros comuns a evitar:</h4>
            </div>
            <ul className="space-y-1">
              {guide.common_mistakes.map((mistake, index) => (
                <li key={index} className="text-sm text-red-700 flex items-start gap-2">
                  <span className="text-red-600 mt-1">⚠️</span>
                  <span>{mistake}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Visa-specific notes */}
        {guide.visa_specific_notes && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <h4 className="font-medium text-blue-900 mb-1">Nota específica para seu visto:</h4>
            <p className="text-sm text-blue-800">{guide.visa_specific_notes}</p>
          </div>
        )}

        {/* USCIS requirements */}
        {guide.uscis_requirements && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <ExternalLink className="w-4 h-4 text-green-600" />
              <h4 className="font-medium text-green-900">Requisitos USCIS:</h4>
            </div>
            <p className="text-sm text-green-800">{guide.uscis_requirements}</p>
          </div>
        )}
      </div>
    </div>
  );
};