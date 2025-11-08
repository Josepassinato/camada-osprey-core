import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  FileEdit, 
  Send,
  AlertTriangle,
  Info,
  Lock,
  Unlock
} from 'lucide-react';

interface DraftSubmissionModeProps {
  caseId: string;
  currentMode?: 'draft' | 'submission';
  completenessScore?: number;
  onModeChange?: (mode: 'draft' | 'submission') => void;
  disabled?: boolean;
}

export const DraftSubmissionMode: React.FC<DraftSubmissionModeProps> = ({
  caseId,
  currentMode = 'draft',
  completenessScore = 0,
  onModeChange,
  disabled = false
}) => {
  const [mode, setMode] = useState<'draft' | 'submission'>(currentMode);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://owlagent.preview.emergentagent.com';

  const canActivateSubmissionMode = completenessScore >= 70;

  const updateMode = async (newMode: 'draft' | 'submission') => {
    if (disabled) return;

    // Verificar se pode ativar modo submission
    if (newMode === 'submission' && !canActivateSubmissionMode) {
      setError('Não é possível ativar modo de submissão. Complete pelo menos 70% das informações.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${backendUrl}/api/auto-application/case/${caseId}/mode?mode=${newMode}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Falha ao atualizar modo');
      }

      const data = await response.json();
      setMode(newMode);
      
      if (onModeChange) {
        onModeChange(newMode);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <Card className={`border-2 ${
        mode === 'draft' 
          ? 'border-gray-200 bg-gray-50' 
          : 'border-green-200 bg-green-50'
      }`}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                {mode === 'draft' ? (
                  <>
                    <FileEdit className="w-5 h-5" />
                    <span>Modo: RASCUNHO</span>
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    <span>Modo: SUBMISSÃO</span>
                  </>
                )}
              </CardTitle>
              <CardDescription className="mt-2">
                {mode === 'draft' ? (
                  'Este documento é um rascunho educativo e NÃO deve ser enviado ao USCIS no estado atual.'
                ) : (
                  'Documento preparado para revisão final e submissão ao USCIS.'
                )}
              </CardDescription>
            </div>
            <Badge className={mode === 'draft' ? 'bg-gray-600' : 'bg-green-600'}>
              {mode === 'draft' ? 'RASCUNHO' : 'SUBMISSÃO'}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Completude:</span>
              <span className={`font-bold ${
                completenessScore >= 90 ? 'text-green-600' :
                completenessScore >= 70 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {completenessScore}%
              </span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all ${
                  completenessScore >= 90 ? 'bg-green-600' :
                  completenessScore >= 70 ? 'bg-yellow-600' :
                  'bg-red-600'
                }`}
                style={{ width: `${completenessScore}%` }}
              />
            </div>
          </div>

          {/* Mode Toggle Buttons */}
          {mode === 'draft' && (
            <div className="space-y-3">
              <Alert className="border-blue-200 bg-blue-50">
                <Info className="h-4 w-4" />
                <AlertTitle>Para Converter em Submissão:</AlertTitle>
                <AlertDescription className="text-sm space-y-1 mt-2">
                  <p>✓ Complete todos os campos obrigatórios (70% mínimo)</p>
                  <p>✓ Revise com nossa ferramenta de verificação</p>
                  <p>✓ Consulte com advogado (recomendado)</p>
                  <p>✓ Ative "Modo Submissão"</p>
                </AlertDescription>
              </Alert>

              <Button
                onClick={() => updateMode('submission')}
                disabled={!canActivateSubmissionMode || loading || disabled}
                className="w-full"
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Ativando...</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <Unlock className="w-4 h-4" />
                    <span>Ativar Modo Submissão</span>
                  </div>
                )}
              </Button>

              {!canActivateSubmissionMode && (
                <p className="text-sm text-red-600 text-center">
                  Complete pelo menos 70% das informações para ativar modo submissão
                </p>
              )}
            </div>
          )}

          {mode === 'submission' && (
            <div className="space-y-3">
              <Alert className="border-green-200 bg-green-50">
                <Info className="h-4 w-4" />
                <AlertTitle>Modo Submissão Ativo</AlertTitle>
                <AlertDescription className="text-sm mt-2">
                  <p>✓ Todas as informações essenciais foram fornecidas</p>
                  <p>✓ Documento pronto para revisão final</p>
                  <p>⚠️ Recomendamos revisar com advogado antes do envio ao USCIS</p>
                </AlertDescription>
              </Alert>

              <Button
                variant="outline"
                onClick={() => updateMode('draft')}
                disabled={loading || disabled}
                className="w-full"
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                    <span>Revertendo...</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <Lock className="w-4 h-4" />
                    <span>Voltar para Modo Rascunho</span>
                  </div>
                )}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Warning about incomplete applications */}
      {mode === 'draft' && completenessScore < 70 && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>⚠️ Importante</AlertTitle>
          <AlertDescription className="text-sm">
            Enviar aplicações incompletas ao USCIS pode resultar em:
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li>Rejeição imediata da aplicação</li>
              <li>Perda das taxas de processamento ($535-$1,760)</li>
              <li>Atraso de 3-12 meses no processo</li>
              <li>Necessidade de refazer toda a aplicação</li>
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Error Display */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Erro</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default DraftSubmissionMode;
