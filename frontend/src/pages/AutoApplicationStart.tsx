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
      title: "Organize suas Informações",
      description: "Ferramenta inteligente que ajuda a organizar e estruturar suas informações para preenchimento preciso."
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Validação Automática",
      description: "Sistema verifica consistência e formatos antes da finalização, reduzindo erros comuns."
    },
    {
      icon: <FileText className="h-6 w-6" />,
      title: "Checklist Personalizada",
      description: "Gera lista de documentos e instruções específicas para seu tipo de aplicação."
    },
    {
      icon: <Users className="h-6 w-6" />,
      title: "Você Mantém o Controle",
      description: "Ferramenta de apoio - você revisa tudo e faz sua própria auto-aplicação."
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
                Ferramenta Tecnológica para Auto-Aplicação USCIS
              </h2>
              <p className="text-lg text-muted-foreground mb-6 max-w-3xl mx-auto">
                Somos uma ferramenta de ajuda tecnológica que simplifica o processo de auto-aplicação 
                para quem deseja preencher seus próprios formulários USCIS com precisão e organização.
              </p>
              <Badge className="bg-gray-100 text-black border-gray-300 mb-4">
                🤖 Ferramenta Tecnológica + Você faz sua própria aplicação
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
                    <h4 className="font-semibold text-foreground mb-2">Somos uma ferramenta tecnológica de apoio</h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li>• NÃO somos um escritório de advocacia nem oferecemos consultoria jurídica</li>
                      <li>• NÃO assinamos formulários G-28 (Notice of Entry of Appearance)</li>
                      <li>• Oferecemos apenas uma ferramenta tecnológica para organizar sua auto-aplicação</li>
                      <li>• VOCÊ é responsável por revisar e enviar sua própria aplicação</li>
                      <li>• Para questões legais complexas, consulte um advogado licenciado</li>
                    </ul>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-black flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-foreground mb-2">O que nossa ferramenta oferece:</h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li>• Ferramenta tecnológica para organizar informações de formulários USCIS</li>
                      <li>• Sistema de validação de dados e formatos</li>
                      <li>• Checklist personalizada e instruções passo a passo</li>
                      <li>• Organização automática de documentos e informações</li>
                      <li>• Você revisa, aprova e envia sua própria aplicação</li>
                    </ul>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-4">
                  <p className="text-xs text-muted-foreground">
                    <strong>Responsabilidade:</strong> Somos apenas uma ferramenta de apoio tecnológico. 
                    É SUA responsabilidade revisar todas as informações organizadas, verificar a precisão dos dados 
                    e fazer sua própria auto-aplicação. Consulte um advogado quando necessário. 
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
                  Li e aceito os termos acima. Entendo que esta é apenas uma ferramenta tecnológica de apoio 
                  e que eu sou responsável por fazer minha própria auto-aplicação.
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
                  <h4 className="font-semibold text-foreground mb-2">Organizar Informações</h4>
                  <p className="text-sm text-muted-foreground">
                    Nossa ferramenta ajuda a organizar suas informações de forma estruturada
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-black text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold">
                    2
                  </div>
                  <h4 className="font-semibold text-foreground mb-2">Validar e Revisar</h4>
                  <p className="text-sm text-muted-foreground">
                    Ferramenta verifica formatos e você revisa todas as informações organizadas
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-black text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold">
                    3
                  </div>
                  <h4 className="font-semibold text-foreground mb-2">Sua Auto-Aplicação</h4>
                  <p className="text-sm text-muted-foreground">
                    Você recebe o pacote organizado com instruções para fazer sua própria aplicação
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