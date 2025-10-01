import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, FileText, Languages, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { OwlAuth } from '../components/owl/OwlAuth';
import { OwlSavedSessions } from '../components/owl/OwlSavedSessions';

interface User {
  user_id: string;
  email: string;
  name: string;
}

interface SavedSession {
  session_id: string;
  case_id: string;
  visa_type: string;
  language: string;
  status: string;
  created_at: string;
  saved_at?: string;
  progress_percentage: number;
  responses_count: number;
  total_fields: number;
}

export const OwlAgent: React.FC = () => {
  const navigate = useNavigate();
  const [selectedVisa, setSelectedVisa] = useState<string>('');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('pt');
  const [currentView, setCurrentView] = useState<'main' | 'auth' | 'saved-sessions'>('main');
  const [authMode, setAuthMode] = useState<'login' | 'save-progress'>('login');
  const [user, setUser] = useState<User | null>(null);
  const [savedSessions, setSavedSessions] = useState<SavedSession[]>([]);

  const visaTypes = [
    { value: 'H-1B', label: 'H-1B - Trabalhador Especializado', description: 'Para profissionais em ocupações especializadas' },
    { value: 'F-1', label: 'F-1 - Estudante', description: 'Para estudos acadêmicos nos EUA' },
    { value: 'I-485', label: 'I-485 - Ajuste de Status', description: 'Para residência permanente' },
    { value: 'O-1', label: 'O-1 - Habilidade Extraordinária', description: 'Para pessoas com habilidades excepcionais' },
    { value: 'L-1', label: 'L-1 - Transferência Interna', description: 'Para funcionários de empresas multinacionais' },
    { value: 'B-1/B-2', label: 'B-1/B-2 - Turista/Negócios', description: 'Para visitas temporárias' }
  ];

  const languages = [
    { value: 'pt', label: 'Português' },
    { value: 'en', label: 'English' },
  ];

  const handleStartQuestionnaire = () => {
    if (!selectedVisa) return;
    
    navigate(`/owl-agent/questionnaire?visa=${selectedVisa}&lang=${selectedLanguage}`);
  };

  const handleSaveProgressLogin = () => {
    setAuthMode('save-progress');
    setCurrentView('auth');
  };

  const handleAccessSavedApplications = () => {
    setAuthMode('login');
    setCurrentView('auth');
  };

  const handleLogin = (userData: User, sessions: SavedSession[] = []) => {
    setUser(userData);
    setSavedSessions(sessions);
    setCurrentView('saved-sessions');
  };

  const handleResumeSession = async (sessionId: string) => {
    const getBackendUrl = () => {
      return import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL || '';
    };

    try {
      const response = await fetch(`${getBackendUrl()}/api/owl-agent/resume-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_email: user?.email,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to resume session');
      }

      const data = await response.json();
      
      // Navigate to questionnaire with session data
      navigate(`/owl-agent/questionnaire?session=${sessionId}&visa=${data.session.visa_type}&lang=${data.session.language}`);
      
    } catch (error) {
      console.error('Error resuming session:', error);
      throw error;
    }
  };

  const handleLogout = () => {
    setUser(null);
    setSavedSessions([]);
    setCurrentView('main');
  };

  const handleBackToMain = () => {
    setCurrentView('main');
  };

  // Render different views based on current state
  if (currentView === 'auth') {
    return (
      <OwlAuth
        mode={authMode}
        onLogin={handleLogin}
        onBack={handleBackToMain}
      />
    );
  }

  if (currentView === 'saved-sessions' && user) {
    return (
      <OwlSavedSessions
        user={user}
        sessions={savedSessions}
        onResumeSession={handleResumeSession}
        onBack={handleBackToMain}
        onLogout={handleLogout}
      />
    );
  }

  // Main view
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <Card className="shadow-2xl border-0">
          <CardHeader className="text-center space-y-4">
            <div className="text-8xl animate-bounce">🦉</div>
            <CardTitle className="text-3xl font-bold text-gray-800">
              Agente Coruja
            </CardTitle>
            <CardDescription className="text-lg text-gray-600">
              Sistema Inteligente de Questionários para Imigração
            </CardDescription>
            <div className="flex flex-wrap gap-2 justify-center">
              <Badge variant="secondary" className="text-xs">🤖 IA Inteligente</Badge>
              <Badge variant="secondary" className="text-xs">🌐 Multi-idioma</Badge>
              <Badge variant="secondary" className="text-xs">📋 USCIS Forms</Badge>
              <Badge variant="secondary" className="text-xs">💾 Salvamento Automático</Badge>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Quick Access Buttons */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <Button
                variant="outline"
                onClick={handleAccessSavedApplications}
                className="h-20 flex flex-col items-center justify-center space-y-2 border-blue-200 hover:border-blue-400 hover:bg-blue-50"
              >
                <div className="text-2xl">📂</div>
                <div className="text-sm font-medium">Minhas Aplicações Salvas</div>
              </Button>
              
              <Button
                variant="outline"
                onClick={handleSaveProgressLogin}
                className="h-20 flex flex-col items-center justify-center space-y-2 border-green-200 hover:border-green-400 hover:bg-green-50"
              >
                <div className="text-2xl">💾</div>
                <div className="text-sm font-medium">Salvar Progresso</div>
              </Button>
            </div>

            {/* New Application Section */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">
                Iniciar Nova Aplicação
              </h3>

              
              <div className="space-y-4">
                {/* Visa Type Selection */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Tipo de Visto *</label>
                  <Select value={selectedVisa} onValueChange={setSelectedVisa}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Selecione o tipo de visto" />
                    </SelectTrigger>
                    <SelectContent>
                      {visaTypes.map((visa) => (
                        <SelectItem key={visa.value} value={visa.value}>
                          <div className="py-1">
                            <div className="font-medium">{visa.label}</div>
                            <div className="text-xs text-gray-500">{visa.description}</div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Language Selection */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Idioma</label>
                  <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pt">🇧🇷 Português</SelectItem>
                      <SelectItem value="en">🇺🇸 English</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Start Button */}
                <Button
                  onClick={handleStartQuestionnaire}
                  disabled={!selectedVisa}
                  className="w-full h-12 text-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                >
                  {selectedVisa 
                    ? `Iniciar Questionário Inteligente - ${selectedVisa}`
                    : 'Selecione um tipo de visto'
                  }
                </Button>
              </div>
            </div>

            {/* Features Info */}
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <h4 className="font-semibold text-gray-800 text-sm">✨ Funcionalidades:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Orientação inteligente em tempo real</li>
                <li>• Validação automática com Google APIs</li>
                <li>• Geração automática de formulários USCIS</li>
                <li>• Salvamento automático do progresso</li>
                <li>• Suporte completo em português e inglês</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};