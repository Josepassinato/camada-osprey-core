import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  BookOpen, 
  MessageSquare, 
  Lightbulb, 
  Search, 
  Clock, 
  Trophy, 
  Target,
  ArrowRight,
  GraduationCap,
  Sparkles,
  Play,
  CheckCircle,
  User,
  Star
} from "lucide-react";
import { useNavigate } from "react-router-dom";

interface Guide {
  id: string;
  visa_type: string;
  title: string;
  description: string;
  difficulty_level: string;
  estimated_time_minutes: number;
  sections: Array<{title: string; content: string}>;
  requirements: string[];
  common_mistakes: string[];
  success_tips: string[];
}

interface UserProgress {
  guides_completed: string[];
  interviews_completed: string[];
  knowledge_queries: number;
  total_study_time_minutes: number;
  achievement_badges: string[];
}

interface PersonalizedTip {
  id: string;
  tip_category: string;
  title: string;
  content: string;
  priority: string;
  is_read: boolean;
  created_at: string;
}

const Education = () => {
  const navigate = useNavigate();
  const [guides, setGuides] = useState<Guide[]>([]);
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [tips, setTips] = useState<PersonalizedTip[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResult, setSearchResult] = useState<any>(null);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    fetchEducationData();
  }, []);

  const fetchEducationData = async () => {
    try {
      const token = localStorage.getItem('osprey_token');
      if (!token) {
        navigate('/login');
        return;
      }

      // Fetch guides, progress, and tips in parallel
      const [guidesRes, progressRes, tipsRes] = await Promise.all([
        fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/education/guides`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/education/progress`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/education/tips`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (guidesRes.ok) {
        const guidesData = await guidesRes.json();
        setGuides(guidesData.guides || []);
      }

      if (progressRes.ok) {
        const progressData = await progressRes.json();
        setProgress(progressData.progress || null);
      }

      if (tipsRes.ok) {
        const tipsData = await tipsRes.json();
        setTips(tipsData.tips || []);
      }

    } catch (error) {
      console.error('Education data error:', error);
      setError('Erro ao carregar dados educacionais');
    } finally {
      setIsLoading(false);
    }
  };

  const getDifficultyColor = (level: string) => {
    const colors = {
      'beginner': 'bg-gray-100 text-gray-800 border-gray-200',
      'intermediate': 'bg-gray-200 text-gray-900 border-gray-300',
      'advanced': 'bg-gray-300 text-black border-gray-400',
    };
    return colors[level as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      'high': 'border-l-black bg-gray-50',
      'medium': 'border-l-gray-600 bg-gray-50',
      'low': 'border-l-gray-400 bg-gray-50',
    };
    return colors[priority as keyof typeof colors] || 'border-l-gray-500 bg-gray-50';
  };

  const getVisaTypeLabel = (type: string) => {
    const labels = {
      'h1b': 'H1-B (Trabalho)',
      'l1': 'L1 (Transferência)',
      'o1': 'O1 (Habilidade Extraordinária)',
      'eb5': 'EB-5 (Investidor)',
      'f1': 'F1 (Estudante)',
      'b1b2': 'B1/B2 (Turismo/Negócios)',
      'green_card': 'Green Card',
      'family': 'Reunificação Familiar',
    };
    return labels[type as keyof typeof labels] || type.toUpperCase();
  };

  const formatStudyTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const isGuideCompleted = (guideType: string) => {
    return progress?.guides_completed.includes(guideType) || false;
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const token = localStorage.getItem('osprey_token');
      const response = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/education/knowledge-base/search`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (response.ok) {
        const result = await response.json();
        setSearchResult(result);
      } else {
        setError('Erro na busca. Tente novamente.');
      }
    } catch (error) {
      console.error('Search error:', error);
      setError('Erro de conexão na busca.');
    } finally {
      setIsSearching(false);
    }
  };

  const markTipAsRead = async (tipId: string) => {
    try {
      const token = localStorage.getItem('osprey_token');
      await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/education/tips/${tipId}/read`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      setTips(prev => prev.map(tip => 
        tip.id === tipId ? { ...tip, is_read: true } : tip
      ));
    } catch (error) {
      console.error('Mark tip as read error:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Carregando centro educacional...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="glass border-b border-white/20">
        <div className="container-responsive py-6">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/dashboard')}
              className="p-2"
            >
              ← Dashboard
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                <GraduationCap className="h-8 w-8 text-primary" />
                Centro Educacional
              </h1>
              <p className="text-muted-foreground">
                Aprenda tudo sobre imigração com guias interativos e IA
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        
        {/* Progress Overview */}
        {progress && (
          <Card className="glass border-0 mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-5 w-5 text-primary" />
                Seu Progresso de Aprendizado
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-2">
                    <BookOpen className="h-8 w-8 text-primary" />
                  </div>
                  <div className="text-2xl font-bold text-foreground">{progress.guides_completed.length}</div>
                  <div className="text-sm text-muted-foreground">Guias Concluídos</div>
                </div>
                
                <div className="text-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <MessageSquare className="h-8 w-8 text-gray-700" />
                  </div>
                  <div className="text-2xl font-bold text-foreground">{progress.interviews_completed.length}</div>
                  <div className="text-sm text-muted-foreground">Entrevistas Simuladas</div>
                </div>
                
                <div className="text-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <Clock className="h-8 w-8 text-gray-700" />
                  </div>
                  <div className="text-2xl font-bold text-foreground">{formatStudyTime(progress.total_study_time_minutes)}</div>
                  <div className="text-sm text-muted-foreground">Tempo de Estudo</div>
                </div>
                
                <div className="text-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <Search className="h-8 w-8 text-gray-700" />
                  </div>
                  <div className="text-2xl font-bold text-foreground">{progress.knowledge_queries}</div>
                  <div className="text-sm text-muted-foreground">Consultas Realizadas</div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* Interactive Guides */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-primary" />
                  Guias Interativos por Tipo de Visto
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {guides.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                      <BookOpen className="h-8 w-8 text-primary" />
                    </div>
                    <p className="text-muted-foreground">Carregando guias interativos...</p>
                  </div>
                ) : (
                  guides.map((guide) => (
                    <div 
                      key={guide.id}
                      className="p-6 border border-white/20 rounded-lg hover:bg-white/50 transition-colors cursor-pointer relative"
                      onClick={() => navigate(`/education/guides/${guide.visa_type}`)}
                    >
                      {isGuideCompleted(guide.visa_type) && (
                        <div className="absolute top-4 right-4">
                          <CheckCircle className="h-6 w-6 text-success" />
                        </div>
                      )}
                      
                      <div className="flex items-start gap-4">
                        <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                          <BookOpen className="h-6 w-6 text-gray-700" />
                        </div>
                        
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-semibold text-foreground">{guide.title}</h3>
                            <Badge className={`${getDifficultyColor(guide.difficulty_level)} border`}>
                              {guide.difficulty_level}
                            </Badge>
                          </div>
                          
                          <p className="text-muted-foreground mb-3">{guide.description}</p>
                          
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                            <div>
                              <div className="text-muted-foreground">Tempo estimado</div>
                              <div className="font-medium flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {guide.estimated_time_minutes} min
                              </div>
                            </div>
                            <div>
                              <div className="text-muted-foreground">Seções</div>
                              <div className="font-medium">{guide.sections.length} capítulos</div>
                            </div>
                            <div>
                              <div className="text-muted-foreground">Requisitos</div>
                              <div className="font-medium">{guide.requirements.length} itens</div>
                            </div>
                            <div>
                              <div className="text-muted-foreground">Dicas</div>
                              <div className="font-medium">{guide.success_tips.length} dicas</div>
                            </div>
                          </div>
                          
                          <Button 
                            className="mt-4 btn-gradient group"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/education/guides/${guide.visa_type}`);
                            }}
                          >
                            {isGuideCompleted(guide.visa_type) ? 'Revisar Guia' : 'Iniciar Guia'}
                            <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>

            {/* Interview Simulator */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-accent" />
                  Simulador de Entrevista com IA
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-6">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                      <MessageSquare className="h-6 w-6 text-gray-700" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-foreground mb-2">
                        Pratique Entrevistas Consulares
                      </h3>
                      <p className="text-muted-foreground mb-4">
                        Simule entrevistas reais com perguntas geradas por IA. Receba feedback 
                        personalizado para melhorar suas respostas e aumentar suas chances de aprovação.
                      </p>
                      
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4 text-sm">
                        <div className="flex items-center gap-2">
                          <Sparkles className="h-4 w-4 text-primary" />
                          <span>Perguntas com IA</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Target className="h-4 w-4 text-success" />
                          <span>Feedback detalhado</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4 text-accent" />
                          <span>Múltiplos cenários</span>
                        </div>
                      </div>
                      
                      <Button 
                        className="btn-gradient group"
                        onClick={() => navigate('/education/interview')}
                      >
                        <Play className="h-4 w-4" />
                        Iniciar Simulação
                        <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Knowledge Base Search */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="h-5 w-5 text-orange-500" />
                  Base de Conhecimento Inteligente
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-4">
                  <div className="flex-1">
                    <input
                      type="text"
                      placeholder="Digite sua pergunta sobre imigração..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                      className="w-full px-4 py-3 bg-white/50 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                      disabled={isSearching}
                    />
                  </div>
                  <Button 
                    onClick={handleSearch}
                    disabled={isSearching || !searchQuery.trim()}
                    className="btn-gradient"
                  >
                    {isSearching ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <Search className="h-4 w-4" />
                    )}
                  </Button>
                </div>

                {searchResult && (
                  <div className="bg-white/30 rounded-lg p-6 space-y-4">
                    <div className="prose prose-sm max-w-none">
                      <h4 className="text-foreground font-semibold mb-3">Resposta:</h4>
                      <p className="text-foreground leading-relaxed">{searchResult.answer}</p>
                    </div>

                    {searchResult.related_topics && searchResult.related_topics.length > 0 && (
                      <div>
                        <h5 className="font-medium text-foreground mb-2">Tópicos relacionados:</h5>
                        <div className="flex flex-wrap gap-2">
                          {searchResult.related_topics.map((topic: string, index: number) => (
                            <Badge key={index} variant="secondary">{topic}</Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {searchResult.next_steps && searchResult.next_steps.length > 0 && (
                      <div>
                        <h5 className="font-medium text-foreground mb-2">Próximos passos:</h5>
                        <ul className="text-sm text-muted-foreground space-y-1">
                          {searchResult.next_steps.map((step: string, index: number) => (
                            <li key={index} className="flex items-start gap-2">
                              <ArrowRight className="h-3 w-3 mt-1 flex-shrink-0" />
                              {step}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {searchResult.warnings && searchResult.warnings.length > 0 && (
                      <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                        <h5 className="font-medium text-orange-800 mb-1">⚠️ Importante:</h5>
                        {searchResult.warnings.map((warning: string, index: number) => (
                          <p key={index} className="text-orange-700 text-sm">{warning}</p>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Personalized Tips */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5 text-yellow-500" />
                  Dicas Personalizadas
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {tips.length === 0 ? (
                  <div className="text-center py-4">
                    <Lightbulb className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">Gerando dicas personalizadas...</p>
                  </div>
                ) : (
                  tips.slice(0, 5).map((tip) => (
                    <div 
                      key={tip.id}
                      className={`p-4 rounded-lg border-l-4 ${getPriorityColor(tip.priority)} ${
                        tip.is_read ? 'opacity-75' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-foreground text-sm">{tip.title}</h4>
                        {!tip.is_read && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => markTipAsRead(tip.id)}
                            className="text-xs h-6 px-2"
                          >
                            Marcar como lida
                          </Button>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground">{tip.content}</p>
                      <div className="mt-2">
                        <Badge className="text-xs" variant="secondary">
                          {tip.tip_category}
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">Ações Rápidas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => navigate('/education/interview')}
                >
                  <MessageSquare className="h-4 w-4" />
                  Nova Simulação de Entrevista
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => navigate('/chat')}
                >
                  <Sparkles className="h-4 w-4" />
                  Chat com IA
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => navigate('/documents')}
                >
                  <BookOpen className="h-4 w-4" />
                  Meus Documentos
                </Button>
              </CardContent>
            </Card>

            {/* Achievement Progress */}
            {progress && (
              <Card className="glass border-0">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold flex items-center gap-2">
                    <Star className="h-5 w-5 text-yellow-500" />
                    Conquistas
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">Progresso Geral</span>
                      <span className="text-sm text-muted-foreground">
                        {Math.round((progress.guides_completed.length / Math.max(guides.length, 1)) * 100)}%
                      </span>
                    </div>
                    <Progress 
                      value={(progress.guides_completed.length / Math.max(guides.length, 1)) * 100} 
                      className="h-2" 
                    />
                  </div>

                  <div className="text-xs text-muted-foreground space-y-1">
                    <div>• {progress.guides_completed.length} guias concluídos</div>
                    <div>• {progress.interviews_completed.length} entrevistas simuladas</div>
                    <div>• {formatStudyTime(progress.total_study_time_minutes)} de estudo</div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Education;