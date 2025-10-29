import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { 
  FileText, 
  CheckSquare, 
  Settings,
  AlertTriangle,
  Info
} from 'lucide-react';
import CompletenessAnalyzer from './CompletenessAnalyzer';
import VisaChecklist from './VisaChecklist';
import DraftSubmissionMode from './DraftSubmissionMode';

interface ValidationSuite Props {
  caseId: string;
  visaType: string;
  userData: Record<string, any>;
  currentMode?: 'draft' | 'submission';
  onValidationComplete?: (canSubmit: boolean, analysis: any) => void;
  showAllTabs?: boolean;
}

export const ValidationSuite: React.FC<ValidationSuiteProps> = ({
  caseId,
  visaType,
  userData,
  currentMode = 'draft',
  onValidationComplete,
  showAllTabs = true
}) => {
  const [analysis, setAnalysis] = useState<any>(null);
  const [checklistComplete, setChecklistComplete] = useState(false);
  const [mode, setMode] = useState<'draft' | 'submission'>(currentMode);
  const [activeTab, setActiveTab] = useState('analysis');

  const completenessScore = analysis?.overall_score || 0;
  const canSubmit = completenessScore >= 70 && (mode === 'submission' || completenessScore >= 90);

  useEffect(() => {
    if (onValidationComplete && analysis) {
      onValidationComplete(canSubmit, analysis);
    }
  }, [canSubmit, analysis]);

  const handleAnalysisComplete = (analysisData: any) => {
    setAnalysis(analysisData);
  };

  const handleModeChange = (newMode: 'draft' | 'submission') => {
    setMode(newMode);
  };

  return (
    <div className="space-y-6">
      {/* Quick Status Summary */}
      <Card className={`border-2 ${
        canSubmit 
          ? 'border-green-200 bg-green-50' 
          : completenessScore >= 70 
          ? 'border-yellow-200 bg-yellow-50'
          : 'border-red-200 bg-red-50'
      }`}>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className={`text-3xl font-bold ${
                completenessScore >= 90 ? 'text-green-600' :
                completenessScore >= 70 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {completenessScore}%
              </div>
              <div className="text-sm text-gray-600">Completude</div>
            </div>
            <div className="text-center">
              <div className={`text-3xl font-bold ${
                mode === 'submission' ? 'text-green-600' : 'text-gray-600'
              }`}>
                {mode === 'draft' ? 'RASCUNHO' : 'SUBMISSÃO'}
              </div>
              <div className="text-sm text-gray-600">Modo Atual</div>
            </div>
            <div className="text-center">
              <div className={`text-3xl font-bold ${
                canSubmit ? 'text-green-600' : 'text-red-600'
              }`}>
                {canSubmit ? '✓' : '✗'}
              </div>
              <div className="text-sm text-gray-600">
                {canSubmit ? 'Pode Finalizar' : 'Não Pode Finalizar'}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content Tabs */}
      {showAllTabs ? (
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="analysis">
              <FileText className="w-4 h-4 mr-2" />
              Análise
            </TabsTrigger>
            <TabsTrigger value="checklist">
              <CheckSquare className="w-4 h-4 mr-2" />
              Checklist
            </TabsTrigger>
            <TabsTrigger value="mode">
              <Settings className="w-4 h-4 mr-2" />
              Modo
            </TabsTrigger>
          </TabsList>

          <TabsContent value="analysis" className="space-y-4">
            <CompletenessAnalyzer
              visaType={visaType}
              userData={userData}
              onAnalysisComplete={handleAnalysisComplete}
              autoAnalyze={true}
            />
          </TabsContent>

          <TabsContent value="checklist" className="space-y-4">
            <VisaChecklist
              visaType={visaType}
              userData={userData}
              onChecklistComplete={setChecklistComplete}
              showProgress={true}
            />
          </TabsContent>

          <TabsContent value="mode" className="space-y-4">
            <DraftSubmissionMode
              caseId={caseId}
              currentMode={mode}
              completenessScore={completenessScore}
              onModeChange={handleModeChange}
            />
          </TabsContent>
        </Tabs>
      ) : (
        <div className="space-y-4">
          <CompletenessAnalyzer
            visaType={visaType}
            userData={userData}
            onAnalysisComplete={handleAnalysisComplete}
            autoAnalyze={true}
          />
          
          <DraftSubmissionMode
            caseId={caseId}
            currentMode={mode}
            completenessScore={completenessScore}
            onModeChange={handleModeChange}
          />
        </div>
      )}

      {/* Action Buttons */}
      {!canSubmit && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Não Pode Finalizar Aplicação</AlertTitle>
          <AlertDescription>
            {completenessScore < 70 ? (
              <>
                <p className="mb-2">Complete pelo menos 70% das informações obrigatórias antes de prosseguir.</p>
                <Button
                  variant="default"
                  onClick={() => setActiveTab('analysis')}
                  className="mt-2"
                >
                  Ver Campos Faltando
                </Button>
              </>
            ) : (
              <>
                <p className="mb-2">Ative o "Modo Submissão" para finalizar a aplicação.</p>
                <Button
                  variant="default"
                  onClick={() => setActiveTab('mode')}
                  className="mt-2"
                >
                  Ativar Modo Submissão
                </Button>
              </>
            )}
          </AlertDescription>
        </Alert>
      )}

      {canSubmit && mode === 'draft' && (
        <Alert className="border-yellow-200 bg-yellow-50">
          <Info className="h-4 w-4" />
          <AlertTitle>Pronto para Conversão</AlertTitle>
          <AlertDescription>
            <p className="mb-2">Sua aplicação atingiu {completenessScore}% de completude. Você pode ativar o modo submissão quando estiver pronto.</p>
            <Button
              variant="default"
              onClick={() => setActiveTab('mode')}
              className="mt-2"
            >
              Ativar Modo Submissão
            </Button>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default ValidationSuite;
