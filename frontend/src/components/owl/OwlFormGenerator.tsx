import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Download, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { useOwlSession } from './OwlSessionManager';

interface GeneratedForm {
  form_id: string;
  visa_type: string;
  form_type: string;
  completion_percentage: number;
  generated_at: string;
  download_url: string;
}

interface OwlFormGeneratorProps {
  className?: string;
}

export const OwlFormGenerator: React.FC<OwlFormGeneratorProps> = ({ className = '' }) => {
  const { state } = useOwlSession();
  const [generating, setGenerating] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [generatedForm, setGeneratedForm] = useState<GeneratedForm | null>(null);
  const [error, setError] = useState<string | null>(null);

  const getBackendUrl = () => {
    return import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  };

  const generateForm = async () => {
    if (!state.session) {
      setError('Nenhuma sessão ativa encontrada');
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      const response = await fetch(`${getBackendUrl()}/api/owl-agent/generate-uscis-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: state.session.session_id,
        }),
      });

      if (!response.ok) {
        throw new Error(`Falha ao gerar formulário: ${response.statusText}`);
      }

      const data = await response.json();
      setGeneratedForm(data.form);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setGenerating(false);
    }
  };

  const downloadForm = async (formId: string) => {
    setDownloading(true);
    setError(null);

    try {
      const response = await fetch(`${getBackendUrl()}/api/owl-agent/download-form/${formId}`);

      if (!response.ok) {
        throw new Error(`Falha ao baixar formulário: ${response.statusText}`);
      }

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `uscis_${state.session?.visa_type}_${formId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setDownloading(false);
    }
  };

  const getCompletionColor = (percentage: number) => {
    if (percentage >= 90) return 'green';
    if (percentage >= 70) return 'yellow';
    return 'red';
  };

  return (
    <div className={`bg-white border rounded-lg shadow-sm p-6 ${className}`}>
      {/* Header with owl mascot */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
          <span className="text-2xl">🦉</span>
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">Gerador de Formulários USCIS</h3>
          <p className="text-sm text-gray-600">
            Gere automaticamente seus formulários oficiais baseados nas suas respostas
          </p>
        </div>
      </div>

      {/* Session info */}
      {state.session && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-blue-900">
                Tipo de Visto: {state.session.visa_type}
              </p>
              <p className="text-sm text-blue-700">
                Progresso: {Math.round(state.session.progress)}%
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-blue-600">
                Sessão: {state.session.session_id.slice(0, 8)}...
              </p>
              <p className="text-xs text-blue-500">
                {Object.keys(state.session.responses).length} respostas salvas
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-600" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Generate form section */}
      {!generatedForm && (
        <div className="text-center">
          <div className="mb-4">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600 mb-2">
              Pronto para gerar seu formulário USCIS oficial?
            </p>
            <p className="text-sm text-gray-500">
              Baseado nas suas respostas, criaremos um PDF preenchido automaticamente.
            </p>
          </div>

          <Button
            onClick={generateForm}
            disabled={generating || !state.session || state.session.progress < 50}
            className="bg-green-600 hover:bg-green-700"
          >
            {generating ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Gerando formulário...
              </>
            ) : (
              <>
                <FileText className="w-4 h-4 mr-2" />
                Gerar Formulário USCIS
              </>
            )}
          </Button>

          {state.session && state.session.progress < 50 && (
            <p className="text-xs text-gray-500 mt-2">
              Complete pelo menos 50% do questionário para gerar o formulário
            </p>
          )}
        </div>
      )}

      {/* Generated form section */}
      {generatedForm && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <h4 className="font-medium text-green-900">Formulário gerado com sucesso!</h4>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Tipo de Formulário:</p>
                <p className="font-medium text-gray-900">{generatedForm.form_type}</p>
              </div>
              <div>
                <p className="text-gray-600">Tipo de Visto:</p>
                <p className="font-medium text-gray-900">{generatedForm.visa_type}</p>
              </div>
              <div>
                <p className="text-gray-600">Completude:</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full bg-${getCompletionColor(generatedForm.completion_percentage)}-500`}
                      style={{ width: `${generatedForm.completion_percentage}%` }}
                    />
                  </div>
                  <span className={`font-medium text-${getCompletionColor(generatedForm.completion_percentage)}-600`}>
                    {generatedForm.completion_percentage}%
                  </span>
                </div>
              </div>
              <div>
                <p className="text-gray-600">Gerado em:</p>
                <p className="font-medium text-gray-900">
                  {new Date(generatedForm.generated_at).toLocaleString('pt-BR')}
                </p>
              </div>
            </div>
          </div>

          {/* Download button */}
          <div className="text-center">
            <Button
              onClick={() => downloadForm(generatedForm.form_id)}
              disabled={downloading}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {downloading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Baixando...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4 mr-2" />
                  Baixar Formulário PDF
                </>
              )}
            </Button>
          </div>

          {/* Generate new form button */}
          <div className="text-center pt-4 border-t">
            <Button
              variant="outline"
              onClick={() => setGeneratedForm(null)}
              className="text-gray-600"
            >
              Gerar Novo Formulário
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};