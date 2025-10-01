import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Clock, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Play,
  ArrowLeft,
  Calendar,
  User,
  Loader2
} from 'lucide-react';

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

interface OwlSavedSessionsProps {
  user: {
    user_id: string;
    email: string;
    name: string;
  };
  sessions: SavedSession[];
  onResumeSession: (sessionId: string) => void;
  onBack: () => void;
  onLogout: () => void;
}

export const OwlSavedSessions: React.FC<OwlSavedSessionsProps> = ({
  user,
  sessions,
  onResumeSession,
  onBack,
  onLogout
}) => {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleResumeSession = async (sessionId: string) => {
    setLoading(sessionId);
    setError(null);
    
    try {
      await onResumeSession(sessionId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao retomar sessão');
    } finally {
      setLoading(null);
    }
  };

  const getVisaTypeDisplay = (visaType: string) => {
    const visaMap: { [key: string]: string } = {
      'H-1B': 'H-1B - Trabalhador Especializado',
      'F-1': 'F-1 - Estudante',
      'I-485': 'I-485 - Ajuste de Status',
      'O-1': 'O-1 - Pessoa de Habilidade Extraordinária',
      'L-1': 'L-1 - Transferência Interna',
      'B-1/B-2': 'B-1/B-2 - Turista/Negócios'
    };
    return visaMap[visaType] || visaType;
  };

  const getStatusBadge = (status: string, progress: number) => {
    if (status === 'completed') {
      return <Badge className="bg-green-100 text-green-800 border-green-200">Completo</Badge>;
    }
    if (progress > 80) {
      return <Badge className="bg-blue-100 text-blue-800 border-blue-200">Quase Pronto</Badge>;
    }
    if (progress > 50) {
      return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">Em Andamento</Badge>;
    }
    return <Badge className="bg-gray-100 text-gray-800 border-gray-200">Iniciado</Badge>;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <Button
            variant="ghost"
            onClick={onBack}
            className="text-blue-600 hover:text-blue-800"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Nova Aplicação
          </Button>
          
          <Button
            variant="outline"
            onClick={onLogout}
            className="text-gray-600"
          >
            Sair
          </Button>
        </div>

        {/* User Welcome */}
        <Card className="mb-6 border-0 shadow-lg">
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="text-4xl">🦉</div>
              <div>
                <CardTitle className="text-xl text-gray-800">
                  Bem-vindo(a), {user.name}!
                </CardTitle>
                <CardDescription className="flex items-center text-gray-600">
                  <User className="mr-1 h-4 w-4" />
                  {user.email}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
        </Card>

        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-700">{error}</AlertDescription>
          </Alert>
        )}

        {/* Saved Sessions */}
        <Card className="border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl text-gray-800 flex items-center">
              <FileText className="mr-2 h-5 w-5" />
              Suas Aplicações Salvas ({sessions.length})
            </CardTitle>
            <CardDescription>
              Continue de onde parou ou inicie uma nova aplicação
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            {sessions.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-6xl mb-4">📝</div>
                <h3 className="text-lg font-semibold text-gray-700 mb-2">
                  Nenhuma aplicação salva
                </h3>
                <p className="text-gray-500 mb-4">
                  Você ainda não possui aplicações salvas. Comece uma nova aplicação!
                </p>
                <Button onClick={onBack}>
                  Iniciar Nova Aplicação
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {sessions.map((session) => (
                  <Card key={session.session_id} className="border border-gray-200 hover:shadow-md transition-shadow">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="font-semibold text-gray-800">
                              {getVisaTypeDisplay(session.visa_type)}
                            </h3>
                            {getStatusBadge(session.status, session.progress_percentage)}
                          </div>
                          
                          <div className="text-sm text-gray-600 space-y-1">
                            <div className="flex items-center">
                              <Calendar className="mr-1 h-3 w-3" />
                              Criado em: {formatDate(session.created_at)}
                            </div>
                            {session.saved_at && (
                              <div className="flex items-center">
                                <Clock className="mr-1 h-3 w-3" />
                                Salvo em: {formatDate(session.saved_at)}
                              </div>
                            )}
                            <div className="flex items-center">
                              <CheckCircle className="mr-1 h-3 w-3" />
                              Progresso: {session.responses_count}/{session.total_fields} campos ({Math.round(session.progress_percentage)}%)
                            </div>
                          </div>

                          {/* Progress Bar */}
                          <div className="mt-3">
                            <div className="flex justify-between text-xs text-gray-500 mb-1">
                              <span>Progresso</span>
                              <span>{Math.round(session.progress_percentage)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full transition-all"
                                style={{ width: `${session.progress_percentage}%` }}
                              />
                            </div>
                          </div>
                        </div>

                        <div className="ml-4">
                          <Button
                            onClick={() => handleResumeSession(session.session_id)}
                            disabled={loading === session.session_id}
                            className="bg-blue-600 hover:bg-blue-700"
                          >
                            {loading === session.session_id ? (
                              <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Carregando...
                              </>
                            ) : (
                              <>
                                <Play className="mr-2 h-4 w-4" />
                                Continuar
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};