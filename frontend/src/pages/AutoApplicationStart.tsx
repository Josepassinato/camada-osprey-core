import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  ArrowLeft,
  ArrowRight,
  Shield,
  AlertTriangle,
  CheckCircle,
  FileText,
  Scale,
  Clock,
  Users
} from "lucide-react";

const AutoApplicationStart = () => {
  const navigate = useNavigate();
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const acceptDisclaimer = async () => {
    if (!disclaimerAccepted) return;
    
    // Generate session token for anonymous user
    const sessionToken = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('osprey_session_token', sessionToken);
    
    // Proceed to form selection without requiring login
    navigate('/auto-application/select-form');
  };

  const benefits = [
    {
      icon: <Clock className="h-6 w-6" />,
      title: "Economize Tempo",
      description: "Sistema inteligente que preenche automaticamente os formulários oficiais com base nas suas informações."
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Reduz Erros",
      description: "IA verifica consistência e valida dados antes da submissão final."
    },
    {
      icon: <FileText className="h-6 w-6" />,
      title: "Documentos Organizados",
      description: "Checklist personalizada e análise automática de documentos."
    },
    {
      icon: <Users className="h-6 w-6" />,
      title: "Suporte Especializado",
      description: "Orientação educacional durante todo o processo de aplicação."
    }
  ];

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
              <ArrowLeft className="h-4 w-4" />
              Dashboard
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-foreground flex items-center gap-3">
                <FileText className="h-8 w-8 text-black" />
                Auto-Aplicação AI
              </h1>
              <p className="text-muted-foreground">
                Sistema inteligente para preparação de formulários USCIS
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="container-responsive section-padding">
        <div className="max-w-6xl mx-auto">
          
          {/* Hero Section */}
          <Card className="glass border-0 mb-8">
            <CardContent className="p-8 text-center">
              <div className="w-20 h-20 bg-black text-white rounded-full flex items-center justify-center mx-auto mb-6">
                <FileText className="h-10 w-10" />
              </div>
              <h2 className="text-3xl font-bold text-foreground mb-4">
                Prepare sua Aplicação USCIS com IA
              </h2>
              <p className="text-lg text-muted-foreground mb-6 max-w-3xl mx-auto">
                Nossa plataforma utiliza inteligência artificial para simplificar o processo de aplicação 
                aos serviços de imigração americanos, garantindo precisão e conformidade.
              </p>
              <Badge className="bg-gray-100 text-black border-gray-300 mb-4">
                🤖 Tecnologia de Ponta + Orientação Educacional
              </Badge>
            </CardContent>
          </Card>

          {/* Benefits */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {benefits.map((benefit, index) => (
              <Card key={index} className="glass border-0 text-center">
                <CardContent className="p-6">
                  <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-4 text-gray-700">
                    {benefit.icon}
                  </div>
                  <h3 className="font-semibold text-foreground mb-2">{benefit.title}</h3>
                  <p className="text-sm text-muted-foreground">{benefit.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Legal Disclaimer */}
          <Card className="glass border-0 border-l-4 border-l-black">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-xl">
                <Scale className="h-6 w-6 text-black" />
                Aviso Legal Importante
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-6 space-y-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-black flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-foreground mb-2">Esta plataforma NÃO é um escritório de advocacia</h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li>• Não oferecemos consultoria jurídica nem representação legal</li>
                      <li>• Não assinamos formulários G-28 (Notice of Entry of Appearance)</li>
                      <li>• Fornecemos apenas orientação educacional para auto-aplicação</li>
                      <li>• Para questões legais complexas, consulte um advogado licenciado</li>
                    </ul>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-black flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-foreground mb-2">O que oferecemos:</h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li>• Ferramenta educacional para preparação de formulários USCIS</li>
                      <li>• Análise automática de documentos para verificação de completude</li>
                      <li>• Orientação passo a passo baseada em regulamentações públicas</li>
                      <li>• Sistema inteligente para organização e validação de dados</li>
                    </ul>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-4">
                  <p className="text-xs text-muted-foreground">
                    <strong>Responsabilidade:</strong> É sua responsabilidade revisar todos os formulários preenchidos, 
                    verificar a precisão das informações e consultar um advogado quando necessário. 
                    A OSPREY não se responsabiliza por resultados de aplicações ou decisões do USCIS.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4 p-4 bg-gray-100 rounded-lg">
                <input
                  type="checkbox"
                  id="disclaimer-accept"
                  checked={disclaimerAccepted}
                  onChange={(e) => setDisclaimerAccepted(e.target.checked)}
                  className="w-4 h-4"
                />
                <label htmlFor="disclaimer-accept" className="text-sm font-medium text-foreground">
                  Li e aceito os termos acima. Entendo que esta plataforma oferece apenas orientação educacional 
                  e não constitui consultoria jurídica.
                </label>
              </div>

              {error && (
                <div className="bg-gray-100 border border-gray-300 rounded-lg p-3">
                  <p className="text-gray-700 text-sm flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    {error}
                  </p>
                </div>
              )}

              <div className="flex justify-center">
                <Button 
                  onClick={acceptDisclaimer}
                  disabled={!disclaimerAccepted || isLoading}
                  className="bg-black text-white hover:bg-gray-800 text-lg font-medium px-8 py-3"
                >
                  {isLoading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <>
                      Aceitar e Continuar
                      <ArrowRight className="h-5 w-5" />
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Process Overview */}
          <Card className="glass border-0 mt-8">
            <CardHeader>
              <CardTitle>Como Funciona o Processo</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="w-12 h-12 bg-black text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold">
                    1
                  </div>
                  <h4 className="font-semibold text-foreground mb-2">Escolha o Formulário</h4>
                  <p className="text-sm text-muted-foreground">
                    Selecione o tipo de formulário USCIS apropriado para sua situação
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-black text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold">
                    2
                  </div>
                  <h4 className="font-semibold text-foreground mb-2">Preencha e Valide</h4>
                  <p className="text-sm text-muted-foreground">
                    Nossa IA ajuda a preencher corretamente e valida suas informações
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-black text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold">
                    3
                  </div>
                  <h4 className="font-semibold text-foreground mb-2">Download e Envio</h4>
                  <p className="text-sm text-muted-foreground">
                    Receba o pacote completo com instruções para envio ao USCIS
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AutoApplicationStart;