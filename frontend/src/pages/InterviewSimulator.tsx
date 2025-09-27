import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  MessageSquare, 
  Clock, 
  CheckCircle, 
  ArrowLeft,
  ArrowRight,
  Target,
  AlertTriangle,
  Play,
  Star
} from "lucide-react";
import { useNavigate } from "react-router-dom";

interface InterviewQuestion {
  question_en: string;
  question_pt: string;
  tips: string[];
  key_points: string[];
}

interface InterviewSession {
  session_id: string;
  interview_type: string;
  visa_type: string;
  difficulty: string;
  questions: InterviewQuestion[];
  current_question: number;
  created_at: string;
}

interface InterviewFeedback {
  score: number;
  confidence_level: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  improved_answer: string;
}

const InterviewSimulator = () => {
  const navigate = useNavigate();
  const [showSetup, setShowSetup] = useState(true);
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [feedback, setFeedback] = useState<InterviewFeedback | null>(null);
  const [sessionCompleted, setSessionCompleted] = useState(false);
  
  // Setup form state
  const [interviewType, setInterviewType] = useState("consular");
  const [visaType, setVisaType] = useState("h1b");
  const [difficulty, setDifficulty] = useState("beginner");

  const startSession = async () => {
    setIsLoading(true);
    setError("");

    try {
      const token = localStorage.getItem('osprey_token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/education/interview/start`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            interview_type: interviewType,
            visa_type: visaType,
            difficulty: difficulty,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSession(data.session);
        setShowSetup(false);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erro ao iniciar simulação');
      }
    } catch (error) {
      console.error('Start session error:', error);
      setError('Erro de conexão. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!session || !currentAnswer.trim()) return;

    setIsLoading(true);
    try {
      const token = localStorage.getItem('osprey_token');
      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/education/interview/${session.session_id}/answer`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            answer: currentAnswer,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setFeedback(data.feedback);
      } else {
        setError('Erro ao enviar resposta');
      }
    } catch (error) {
      console.error('Submit answer error:', error);
      setError('Erro de conexão');
    } finally {
      setIsLoading(false);
    }
  };

  const nextQuestion = async () => {
    if (!session) return;

    if (session.current_question < session.questions.length - 1) {
      // Move to next question
      setSession({
        ...session,
        current_question: session.current_question + 1
      });
      setCurrentAnswer("");
      setFeedback(null);
    } else {
      // Complete interview
      try {
        const token = localStorage.getItem('osprey_token');
        const response = await fetch(
          `${import.meta.env.VITE_BACKEND_URL}/api/education/interview/${session.session_id}/complete`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (response.ok) {
          setSessionCompleted(true);
        }
      } catch (error) {
        console.error('Complete interview error:', error);
      }
    }
  };

  if (showSetup) {
    return (
      <div className="min-h-screen bg-gradient-subtle">
        {/* Header */}
        <div className="glass border-b border-white/20">
          <div className="container-responsive py-6">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/education')}
                className="p-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Voltar
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                  <MessageSquare className="h-8 w-8 text-gray-700" />
                  Simulador de Entrevista
                </h1>
                <p className="text-muted-foreground">
                  Configure sua simulação de entrevista personalizada
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="container-responsive section-padding">
          <div className="max-w-2xl mx-auto">
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle>Configurar Simulação</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Interview Type */}
                <div>
                  <label className="text-sm font-medium text-foreground mb-3 block">
                    Tipo de Entrevista
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <button
                      onClick={() => setInterviewType("consular")}
                      className={`p-4 border rounded-lg text-left transition-colors ${
                        interviewType === "consular"
                          ? 'bg-gray-100 border-gray-300 text-gray-900'
                          : 'hover:bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className="font-medium">Entrevista Consular</div>
                      <div className="text-sm text-muted-foreground">
                        Simulação de entrevista no consulado
                      </div>
                    </button>
                    <button
                      onClick={() => setInterviewType("uscis")}
                      className={`p-4 border rounded-lg text-left transition-colors ${
                        interviewType === "uscis"
                          ? 'bg-gray-100 border-gray-300 text-gray-900'
                          : 'hover:bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className="font-medium">Entrevista USCIS</div>
                      <div className="text-sm text-muted-foreground">
                        Simulação de entrevista no USCIS
                      </div>
                    </button>
                  </div>
                </div>

                {/* Visa Type */}
                <div>
                  <label className="text-sm font-medium text-foreground mb-3 block">
                    Tipo de Visto
                  </label>
                  <select
                    value={visaType}
                    onChange={(e) => setVisaType(e.target.value)}
                    className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                  >
                    <option value="h1b">H1-B (Trabalho)</option>
                    <option value="f1">F1 (Estudante)</option>
                    <option value="b1b2">B1/B2 (Turismo/Negócios)</option>
                    <option value="l1">L1 (Transferência)</option>
                    <option value="o1">O1 (Habilidade Extraordinária)</option>
                  </select>
                </div>

                {/* Difficulty */}
                <div>
                  <label className="text-sm font-medium text-foreground mb-3 block">
                    Nível de Dificuldade
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <button
                      onClick={() => setDifficulty("beginner")}
                      className={`p-3 border rounded-lg text-center transition-colors ${
                        difficulty === "beginner"
                          ? 'bg-gray-100 border-gray-300 text-gray-900'
                          : 'hover:bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className="font-medium">Iniciante</div>
                      <div className="text-xs text-muted-foreground">Perguntas básicas</div>
                    </button>
                    <button
                      onClick={() => setDifficulty("intermediate")}
                      className={`p-3 border rounded-lg text-center transition-colors ${
                        difficulty === "intermediate"
                          ? 'bg-gray-100 border-gray-300 text-gray-900'
                          : 'hover:bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className="font-medium">Intermediário</div>
                      <div className="text-xs text-muted-foreground">Perguntas moderadas</div>
                    </button>
                    <button
                      onClick={() => setDifficulty("advanced")}
                      className={`p-3 border rounded-lg text-center transition-colors ${
                        difficulty === "advanced"
                          ? 'bg-gray-100 border-gray-300 text-gray-900'
                          : 'hover:bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className="font-medium">Avançado</div>
                      <div className="text-xs text-muted-foreground">Perguntas complexas</div>
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="bg-gray-100 border border-gray-300 rounded-lg p-3">
                    <p className="text-gray-700 text-sm flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      {error}
                    </p>
                  </div>
                )}

                <Button 
                  onClick={startSession}
                  disabled={isLoading}
                  className="w-full bg-gray-700 text-white hover:bg-gray-800"
                >
                  {isLoading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <Play className="h-4 w-4" />
                      Iniciar Simulação
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  if (sessionCompleted) {
    return (
      <div className="min-h-screen bg-gradient-subtle">
        <div className="container-responsive section-padding">
          <div className="max-w-2xl mx-auto text-center">
            <Card className="glass border-0">
              <CardContent className="p-8">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="h-8 w-8 text-gray-700" />
                </div>
                <h2 className="text-2xl font-bold text-foreground mb-2">
                  Entrevista Concluída!
                </h2>
                <p className="text-muted-foreground mb-6">
                  Parabéns! Você completou a simulação de entrevista.
                </p>
                <div className="flex gap-4 justify-center">
                  <Button 
                    onClick={() => {
                      setShowSetup(true);
                      setSession(null);
                      setSessionCompleted(false);
                      setFeedback(null);
                    }}
                    variant="outline"
                  >
                    Nova Simulação
                  </Button>
                  <Button onClick={() => navigate('/education')}>
                    Voltar ao Centro Educacional
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Carregando simulação...</p>
        </div>
      </div>
    );
  }

  const currentQuestion = session.questions[session.current_question];

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="glass border-b border-white/20">
        <div className="container-responsive py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/education')}
                className="p-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Sair
              </Button>
              <div>
                <h1 className="text-xl font-bold text-foreground">
                  Simulação de Entrevista - {session.visa_type.toUpperCase()}
                </h1>
                <p className="text-sm text-muted-foreground">
                  Pergunta {session.current_question + 1} de {session.questions.length}
                </p>
              </div>
            </div>
            <Badge className="bg-gray-100 text-gray-800 border-gray-200">
              {session.difficulty}
            </Badge>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        <div className="max-w-4xl mx-auto grid lg:grid-cols-3 gap-8">
          {/* Question and Answer */}
          <div className="lg:col-span-2 space-y-6">
            {/* Question */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-gray-700" />
                  Pergunta da Entrevista
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-foreground mb-2">English:</h3>
                  <p className="text-foreground">{currentQuestion.question_en}</p>
                </div>
                <div className="p-4 bg-gray-100 rounded-lg">
                  <h3 className="font-medium text-foreground mb-2">Português:</h3>
                  <p className="text-foreground">{currentQuestion.question_pt}</p>
                </div>
              </CardContent>
            </Card>

            {/* Answer Input */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle>Sua Resposta</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <textarea
                  value={currentAnswer}
                  onChange={(e) => setCurrentAnswer(e.target.value)}
                  placeholder="Digite sua resposta aqui... (pode ser em português ou inglês)"
                  className="w-full h-32 px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent resize-none"
                  disabled={feedback !== null}
                />
                
                {!feedback ? (
                  <Button 
                    onClick={submitAnswer}
                    disabled={isLoading || !currentAnswer.trim()}
                    className="bg-gray-700 text-white hover:bg-gray-800"
                  >
                    {isLoading ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      'Enviar Resposta'
                    )}
                  </Button>
                ) : (
                  <Button 
                    onClick={nextQuestion}
                    className="bg-gray-700 text-white hover:bg-gray-800"
                  >
                    {session.current_question < session.questions.length - 1 ? (
                      <>
                        Próxima Pergunta
                        <ArrowRight className="h-4 w-4" />
                      </>
                    ) : (
                      'Finalizar Entrevista'
                    )}
                  </Button>
                )}
              </CardContent>
            </Card>

            {/* Feedback */}
            {feedback && (
              <Card className="glass border-0">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Star className="h-5 w-5 text-gray-700" />
                    Feedback da IA
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-foreground">{feedback.score}/100</div>
                      <div className="text-sm text-muted-foreground">Pontuação</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-medium text-foreground">{feedback.confidence_level}</div>
                      <div className="text-sm text-muted-foreground">Confiança</div>
                    </div>
                  </div>

                  {feedback.strengths.length > 0 && (
                    <div>
                      <h4 className="font-medium text-foreground mb-2">✅ Pontos Fortes:</h4>
                      <ul className="space-y-1">
                        {feedback.strengths.map((strength, index) => (
                          <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                            {strength}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {feedback.suggestions.length > 0 && (
                    <div>
                      <h4 className="font-medium text-foreground mb-2">💡 Sugestões:</h4>
                      <ul className="space-y-1">
                        {feedback.suggestions.map((suggestion, index) => (
                          <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                            <div className="w-1.5 h-1.5 bg-gray-600 rounded-full mt-2 flex-shrink-0"></div>
                            {suggestion}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Question Tips */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">Dicas para Esta Pergunta</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {currentQuestion.tips.map((tip, index) => (
                    <li key={index} className="text-sm text-foreground flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-gray-700 rounded-full mt-2 flex-shrink-0"></div>
                      {tip}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Key Points */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold flex items-center gap-2">
                  <Target className="h-5 w-5 text-gray-700" />
                  Pontos-Chave
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {currentQuestion.key_points.map((point, index) => (
                    <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                      {point}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Session Info */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">Informações da Sessão</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-gray-700" />
                  <span className="text-sm">{session.interview_type}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-gray-700" />
                  <span className="text-sm">{new Date(session.created_at).toLocaleString()}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterviewSimulator;