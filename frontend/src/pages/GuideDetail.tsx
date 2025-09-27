import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  BookOpen, 
  Clock, 
  CheckCircle, 
  ArrowLeft,
  ArrowRight,
  Target,
  AlertTriangle
} from "lucide-react";

interface GuideDetail {
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

const GuideDetail = () => {
  const { visaType } = useParams();
  const navigate = useNavigate();
  const [guide, setGuide] = useState<GuideDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentSection, setCurrentSection] = useState(0);
  const [completedSections, setCompletedSections] = useState<number[]>([]);

  useEffect(() => {
    fetchGuideDetail();
  }, [visaType]);

  const fetchGuideDetail = async () => {
    try {
      const token = localStorage.getItem('osprey_token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/api/education/guides/${visaType}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setGuide(data.guide);
      } else {
        setError('Erro ao carregar guia');
      }
    } catch (error) {
      console.error('Guide detail error:', error);
      setError('Erro de conexão');
    } finally {
      setIsLoading(false);
    }
  };

  const markSectionComplete = (sectionIndex: number) => {
    if (!completedSections.includes(sectionIndex)) {
      setCompletedSections([...completedSections, sectionIndex]);
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

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto"></div>
          <p className="text-muted-foreground">Carregando guia...</p>
        </div>
      </div>
    );
  }

  if (error || !guide) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center space-y-4">
          <AlertTriangle className="h-12 w-12 text-gray-700 mx-auto" />
          <p className="text-foreground">Guia não encontrado</p>
          <Button onClick={() => navigate('/education')}>
            Voltar para Educação
          </Button>
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
              onClick={() => navigate('/education')}
              className="p-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Voltar
            </Button>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-bold text-foreground">{guide.title}</h1>
                <Badge className={`${getDifficultyColor(guide.difficulty_level)} border`}>
                  {guide.difficulty_level}
                </Badge>
              </div>
              <p className="text-muted-foreground">{guide.description}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Guide Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Progress */}
            <Card className="glass border-0">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-medium">Progresso do Guia</span>
                  <span className="text-sm text-muted-foreground">
                    {completedSections.length}/{guide.sections.length} seções
                  </span>
                </div>
                <Progress 
                  value={(completedSections.length / guide.sections.length) * 100} 
                  className="h-2" 
                />
              </CardContent>
            </Card>

            {/* Current Section */}
            {guide.sections.length > 0 && (
              <Card className="glass border-0">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <BookOpen className="h-5 w-5 text-gray-700" />
                      Seção {currentSection + 1}: {guide.sections[currentSection].title}
                    </CardTitle>
                    {completedSections.includes(currentSection) && (
                      <CheckCircle className="h-6 w-6 text-gray-700" />
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="prose prose-sm max-w-none">
                    <p className="text-foreground leading-relaxed">
                      {guide.sections[currentSection].content}
                    </p>
                  </div>

                  <div className="flex items-center justify-between pt-4">
                    <Button
                      variant="outline"
                      onClick={() => setCurrentSection(Math.max(0, currentSection - 1))}
                      disabled={currentSection === 0}
                    >
                      <ArrowLeft className="h-4 w-4" />
                      Anterior
                    </Button>

                    <Button
                      onClick={() => markSectionComplete(currentSection)}
                      disabled={completedSections.includes(currentSection)}
                      className="bg-gray-700 text-white hover:bg-gray-800"
                    >
                      {completedSections.includes(currentSection) ? (
                        <>
                          <CheckCircle className="h-4 w-4" />
                          Concluída
                        </>
                      ) : (
                        'Marcar como Concluída'
                      )}
                    </Button>

                    <Button
                      variant="outline"
                      onClick={() => setCurrentSection(Math.min(guide.sections.length - 1, currentSection + 1))}
                      disabled={currentSection === guide.sections.length - 1}
                    >
                      Próxima
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Guide Info */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">Informações</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-gray-700" />
                  <span className="text-sm">{guide.estimated_time_minutes} minutos</span>
                </div>
                <div className="flex items-center gap-2">
                  <BookOpen className="h-4 w-4 text-gray-700" />
                  <span className="text-sm">{guide.sections.length} seções</span>
                </div>
                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-gray-700" />
                  <span className="text-sm">{guide.requirements.length} requisitos</span>
                </div>
              </CardContent>
            </Card>

            {/* Sections Navigation */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">Navegação por Seções</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {guide.sections.map((section, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentSection(index)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      currentSection === index
                        ? 'bg-gray-100 text-gray-900 border border-gray-300'
                        : 'hover:bg-gray-50 text-muted-foreground'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        {index + 1}. {section.title}
                      </span>
                      {completedSections.includes(index) && (
                        <CheckCircle className="h-4 w-4 text-gray-700" />
                      )}
                    </div>
                  </button>
                ))}
              </CardContent>
            </Card>

            {/* Requirements */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">Requisitos</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {guide.requirements.map((req, index) => (
                    <li key={index} className="text-sm text-foreground flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-gray-700 rounded-full mt-2 flex-shrink-0"></div>
                      {req}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Success Tips */}
            <Card className="glass border-0">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">Dicas de Sucesso</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {guide.success_tips.map((tip, index) => (
                    <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                      {tip}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GuideDetail;