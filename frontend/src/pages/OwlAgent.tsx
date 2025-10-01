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
    if (selectedVisa) {
      navigate(`/owl-agent/questionnaire?visa=${selectedVisa}&lang=${selectedLanguage}`);
    }
  };

  return (
    <OwlSessionProvider>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-12">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-4 mb-6">
              <div className="w-20 h-20 bg-white rounded-full shadow-lg flex items-center justify-center">
                <span className="text-5xl">🦉</span>
              </div>
              <div className="text-left">
                <h1 className="text-4xl font-bold text-gray-900 mb-2">
                  Agente Coruja
                </h1>
                <p className="text-xl text-blue-600 font-medium">
                  Sistema Inteligente de Questionários
                </p>
              </div>
            </div>
            
            <p className="text-lg text-gray-700 max-w-3xl mx-auto leading-relaxed">
              Nosso assistente inteligente conduz você através de questionários personalizados,
              valida suas respostas em tempo real e gera formulários USCIS oficiais automaticamente.
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <Sparkles className="w-6 h-6 text-blue-600" />
                </div>
                <CardTitle className="text-lg">Orientação Inteligente</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Receba dicas contextuais e orientações em tempo real baseadas no seu tipo de visto
                </p>
              </CardContent>
            </Card>

            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <FileText className="w-6 h-6 text-green-600" />
                </div>
                <CardTitle className="text-lg">Validação Automática</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Validação progressiva com pontuação visual e feedback instantâneo para cada campo
                </p>
              </CardContent>
            </Card>

            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <Languages className="w-6 h-6 text-purple-600" />
                </div>
                <CardTitle className="text-lg">Multi-idioma</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Suporte completo em Português e Inglês com alternância durante a sessão
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Start Questionnaire Section */}
          <Card className="max-w-2xl mx-auto">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl flex items-center justify-center gap-2">
                <span className="text-2xl">🚀</span>
                Iniciar Questionário Inteligente
              </CardTitle>
              <p className="text-gray-600">
                Selecione seu tipo de visto e idioma preferido para começar
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Visa Type Selection */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Tipo de Visto *
                </label>
                <Select value={selectedVisa} onValueChange={setSelectedVisa}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Selecione o tipo de visto" />
                  </SelectTrigger>
                  <SelectContent>
                    {visaTypes.map((visa) => (
                      <SelectItem key={visa.value} value={visa.value}>
                        {visa.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Language Selection */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">
                  Idioma Preferido
                </label>
                <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {languages.map((lang) => (
                      <SelectItem key={lang.value} value={lang.value}>
                        {lang.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Start Button */}
              <Button
                onClick={handleStartQuestionnaire}
                disabled={!selectedVisa}
                className="w-full bg-blue-600 hover:bg-blue-700 text-lg py-6"
              >
                Iniciar Questionário Inteligente
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>

              {!selectedVisa && (
                <p className="text-sm text-gray-500 text-center">
                  Selecione um tipo de visto para continuar
                </p>
              )}
            </CardContent>
          </Card>

          {/* Benefits Section */}
          <div className="mt-16 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-8">
              Por que usar o Agente Coruja?
            </h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="text-3xl mb-3">⚡</div>
                <h3 className="font-semibold mb-2">Rápido e Eficiente</h3>
                <p className="text-sm text-gray-600">
                  Complete questionários em minutos, não horas
                </p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="text-3xl mb-3">🎯</div>
                <h3 className="font-semibold mb-2">Precisão Garantida</h3>
                <p className="text-sm text-gray-600">
                  Validação com IA e APIs do Google
                </p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="text-3xl mb-3">📋</div>
                <h3 className="font-semibold mb-2">Formulários USCIS</h3>
                <p className="text-sm text-gray-600">
                  Geração automática de PDFs oficiais
                </p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="text-3xl mb-3">💾</div>
                <h3 className="font-semibold mb-2">Progresso Salvo</h3>
                <p className="text-sm text-gray-600">
                  Continue de onde parou a qualquer momento
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </OwlSessionProvider>
  );
};