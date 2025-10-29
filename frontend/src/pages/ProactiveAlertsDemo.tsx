import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import ProactiveAlertsDisplay, { AlertsBadge } from '../components/ProactiveAlertsDisplay';
import { Bell, RefreshCw } from 'lucide-react';

export const ProactiveAlertsDemo: React.FC = () => {
  const [caseId, setCaseId] = useState('demo_case_123');
  const [activeCaseId, setActiveCaseId] = useState('demo_case_123');

  const handleLoadAlerts = () => {
    setActiveCaseId(caseId);
  };

  return (
    <div className="container mx-auto p-6 space-y-6 max-w-6xl">
      {/* Header */}
      <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-white">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Bell className="w-8 h-8 text-blue-600" />
              <div>
                <CardTitle className="text-2xl">Sistema de Alertas Proativos Inteligentes</CardTitle>
                <CardDescription className="mt-2 text-base">
                  Guia automático baseado em requisitos do USCIS - Substitui chat de ajuda
                </CardDescription>
              </div>
            </div>
            <AlertsBadge caseId={activeCaseId} />
          </div>
        </CardHeader>
      </Card>

      {/* Demo Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Demonstração</CardTitle>
          <CardDescription>
            Digite um ID de caso para ver seus alertas proativos
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-end space-x-4">
            <div className="flex-1">
              <Label htmlFor="caseId">Case ID</Label>
              <Input
                id="caseId"
                value={caseId}
                onChange={(e) => setCaseId(e.target.value)}
                placeholder="Ex: demo_case_123"
              />
            </div>
            <Button onClick={handleLoadAlerts} className="gap-2">
              <RefreshCw className="w-4 h-4" />
              Carregar Alertas
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
            <Card className="bg-red-50 border-red-200">
              <CardContent className="pt-4">
                <div className="text-2xl font-bold text-red-600">🔔</div>
                <p className="font-medium text-red-900 mt-2">Documentos Expirando</p>
                <p className="text-sm text-red-700">Passaporte, vistos, etc.</p>
              </CardContent>
            </Card>

            <Card className="bg-yellow-50 border-yellow-200">
              <CardContent className="pt-4">
                <div className="text-2xl font-bold text-yellow-600">⚠️</div>
                <p className="font-medium text-yellow-900 mt-2">Campos Incompletos</p>
                <p className="text-sm text-yellow-700">Retomar onde parou</p>
              </CardContent>
            </Card>

            <Card className="bg-green-50 border-green-200">
              <CardContent className="pt-4">
                <div className="text-2xl font-bold text-green-600">🎉</div>
                <p className="font-medium text-green-900 mt-2">Boas Notícias</p>
                <p className="text-sm text-green-700">Updates do USCIS</p>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>

      {/* Alerts Display */}
      <ProactiveAlertsDisplay 
        caseId={activeCaseId}
        autoRefresh={true}
        refreshInterval={300}
        showDismissed={false}
      />

      {/* Features Info */}
      <Card>
        <CardHeader>
          <CardTitle>Tipos de Alertas Inteligentes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h3 className="font-semibold flex items-center space-x-2">
                <span className="text-2xl">🔔</span>
                <span>Documentos Expirando</span>
              </h3>
              <p className="text-sm text-gray-600 ml-8">
                "Seu passaporte expira em 3 meses. USCIS requer 6+ meses de validade"
              </p>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold flex items-center space-x-2">
                <span className="text-2xl">⚠️</span>
                <span>Campos Incompletos</span>
              </h3>
              <p className="text-sm text-gray-600 ml-8">
                "Você parou na etapa 3. 5 minutos para completar!"
              </p>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold flex items-center space-x-2">
                <span className="text-2xl">💡</span>
                <span>Oportunidades</span>
              </h3>
              <p className="text-sm text-gray-600 ml-8">
                "Conforme diretrizes do USCIS: Adicionar carta do empregador aumenta chance em +12%"
              </p>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold flex items-center space-x-2">
                <span className="text-2xl">🎉</span>
                <span>Boas Notícias</span>
              </h3>
              <p className="text-sm text-gray-600 ml-8">
                "Segundo últimas informações do USCIS: Casos como o seu estão sendo aprovados 18% mais rápido!"
              </p>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold flex items-center space-x-2">
                <span className="text-2xl">⏰</span>
                <span>Deadlines</span>
              </h3>
              <p className="text-sm text-gray-600 ml-8">
                "Seu status atual expira em 45 dias. Finalize urgentemente!"
              </p>
            </div>

            <div className="space-y-2">
              <h3 className="font-semibold flex items-center space-x-2">
                <span className="text-2xl">📎</span>
                <span>Sugestões de Docs</span>
              </h3>
              <p className="text-sm text-gray-600 ml-8">
                "Adicionar declaração de impostos conjunta fortalece sua aplicação"
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* System Info */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="pt-6">
          <div className="space-y-2 text-sm">
            <p className="font-medium text-blue-900">✨ Sistema Inteligente:</p>
            <ul className="list-disc list-inside text-blue-800 space-y-1 ml-4">
              <li>Verificações diárias automáticas</li>
              <li>Contextual ao estágio do usuário</li>
              <li>Baseado em requisitos reais do USCIS</li>
              <li>Substitui chat - mais proativo e menos reativo</li>
              <li>Email/SMS/Push notifications (em breve)</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProactiveAlertsDemo;
