import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { 
  ArrowRight,
  CheckCircle,
  FileText,
  Clock,
  Shield,
  Zap,
  User,
  CreditCard,
  Download
} from "lucide-react";

const AutoApplicationStart = () => {
  const navigate = useNavigate();
  const [agreed, setAgreed] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  const startApplication = async () => {
    if (!agreed) {
      alert('Por favor, aceite os termos para continuar.');
      return;
    }

    setIsCreating(true);
    
    try {
      // Generate session token for anonymous tracking
      const sessionToken = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('osprey_session_token', sessionToken);
      
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auto-application/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_token: sessionToken
        }),
      });

      if (response.ok) {
        const data = await response.json();
        // Navigate to form selection with case ID
        navigate('/auto-application/select-form', { 
          state: { caseId: data.case.case_id, sessionToken } 
        });
      } else {
        throw new Error('Falha ao criar aplicação');
      }
    } catch (error) {
      console.error('Error starting application:', error);
      alert('Erro ao iniciar aplicação. Tente novamente.');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-black">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="text-2xl font-bold text-black">Osprey</div>
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#como-funciona" className="text-black hover:text-gray-600 transition-colors">Como funciona</a>
            <a href="#depoimentos" className="text-black hover:text-gray-600 transition-colors">Depoimentos</a>
            <Button variant="outline" className="border-black text-black hover:bg-gray-50">
              Entrar
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-24">
        <div className="text-center max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center px-4 py-2 bg-gray-100 rounded-full text-sm text-black mb-8">
            <Zap className="h-4 w-4 mr-2" />
            IA Avançada para Imigração
          </div>
          
          {/* Main Headline */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-black mb-6 tracking-tight leading-tight">
            Clique. Clique. Clique.
            <br />
            <span className="text-gray-600">E seu visto está pronto.</span>
          </h1>
          
          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-black mb-12 font-light max-w-3xl mx-auto leading-relaxed">
            Osprey torna a aplicação de visto americano surpreendentemente rápida para brasileiros - 
            em apenas <strong>3 passos</strong> - com uma experiência simples e completa.
          </p>
          
          {/* CTA */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <Button 
              onClick={startApplication}
              disabled={!agreed || isCreating}
              className="bg-black text-white hover:bg-gray-800 px-8 py-4 text-lg font-medium rounded-full"
            >
              {isCreating ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Iniciando...
                </>
              ) : (
                <>
                  Começar Aplicação
                  <ArrowRight className="h-5 w-5 ml-2" />
                </>
              )}
            </Button>
            <div className="flex items-center text-sm text-gray-600">
              <Clock className="h-4 w-4 mr-2" />
              Leva apenas 15 minutos
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="flex items-center justify-center space-x-8 text-sm text-gray-600">
            <div className="flex items-center">
              <Shield className="h-4 w-4 mr-2" />
              100% Seguro
            </div>
            <div className="flex items-center">
              <Zap className="h-4 w-4 mr-2" />
              IA Avançada
            </div>
            <div className="flex items-center">
              <FileText className="h-4 w-4 mr-2" />
              9 Formulários USCIS
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="como-funciona" className="bg-gray-50 py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-black mb-4">
              Aplicação de visto deveria ser simples.
              <br />
              Agora é.
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Investir em qualquer coisa hoje em dia leva apenas alguns cliques. 
              A menos que você esteja aplicando para um visto americano. Então vira uma bagunça infinita de documentos.
            </p>
          </div>

          {/* Process Steps */}
          <div className="grid md:grid-cols-3 gap-12 mb-20">
            {[
              {
                step: "01",
                icon: <User className="h-8 w-8" />,
                title: "Conte sua história",
                description: "Nossa IA analisa sua situação pessoal e extrai informações importantes automaticamente em português."
              },
              {
                step: "02", 
                icon: <FileText className="h-8 w-8" />,
                title: "Formulários automáticos",
                description: "Preenchemos automaticamente os formulários oficiais do USCIS com suas informações, traduzindo tudo para inglês."
              },
              {
                step: "03",
                icon: <Download className="h-8 w-8" />,
                title: "Baixe e envie",
                description: "Receba todos os documentos organizados com instruções detalhadas para submissão ao USCIS."
              }
            ].map((item, index) => (
              <div key={index} className="text-center">
                <div className="text-6xl font-bold text-gray-200 mb-4">{item.step}</div>
                <div className="w-16 h-16 bg-black text-white rounded-full flex items-center justify-center mx-auto mb-6">
                  {item.icon}
                </div>
                <h3 className="text-xl font-bold text-black mb-4">{item.title}</h3>
                <p className="text-gray-600 leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-black mb-4">
              Não poderia ser mais fácil.
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: <Zap className="h-8 w-8" />,
                title: "Sem papel e caneta",
                description: "Todo o processo é completamente digitalizado e organizado em passos simples e clicáveis."
              },
              {
                icon: <Shield className="h-8 w-8" />,
                title: "Brasileiro? Sem problema",
                description: "Osprey oferece a assistência que você não consegue sozinho para aplicar nos EUA."
              },
              {
                icon: <User className="h-8 w-8" />,
                title: "Time especialista",
                description: "Nós te guiamos através das questões legais e burocráticas. Não precisa virar especialista da noite pro dia."
              },
              {
                icon: <FileText className="h-8 w-8" />,
                title: "Mantenha-se informado",
                description: "Com um processo simplificado, será tão fácil quanto rastrear um pacote. Sem surpresas."
              }
            ].map((feature, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 bg-black text-white rounded-full flex items-center justify-center mx-auto mb-6">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-bold text-black mb-3">{feature.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="depoimentos" className="bg-gray-50 py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-black mb-4">
              Veja o que nossos usuários dizem
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                quote: "A seriedade deles me deu confiança. Todas as perguntas foram sempre prontamente respondidas. Eu recomendo.",
                author: "Carlos M. - Empresário"
              },
              {
                quote: "Apesar dos avisos sobre a dificuldade de aplicar nos EUA, foi surpreendentemente fácil com a Osprey. Eles cuidaram de tudo remotamente.",
                author: "Ana S. - Desenvolvedora"
              },
              {
                quote: "Fiquei tão satisfeito com o serviço que voltei para fazer uma segunda aplicação com eles.",
                author: "João P. - Advogado"
              }
            ].map((testimonial, index) => (
              <div key={index} className="bg-white p-8 rounded-lg">
                <p className="text-gray-800 mb-6 italic">"{testimonial.quote}"</p>
                <div className="text-black font-medium">{testimonial.author}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Legal Disclaimer */}
      <section className="py-12 border-t border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="font-bold text-black mb-3">Importante - Ferramenta Tecnológica de Apoio</h3>
            <p className="text-sm text-gray-600 mb-4">
              Esta é uma ferramenta de apoio tecnológico, não consultoria jurídica. 
              Organizamos e preenchemos formulários baseados nas suas informações e fornecemos orientações gerais sobre o processo.
            </p>
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="terms-footer"
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
                className="h-4 w-4 mt-1 accent-black"
              />
              <label htmlFor="terms-footer" className="text-sm text-gray-600">
                Entendo que esta é uma ferramenta de apoio e não constitui consultoria jurídica. 
                Aceito os termos e condições de uso.
              </label>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 bg-black text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Você está a alguns cliques de aplicar para seu visto americano. Pronto?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Preencha um formulário rápido e entraremos em contato em breve.
          </p>
          <Button 
            onClick={startApplication}
            disabled={!agreed || isCreating}
            className="bg-white text-black hover:bg-gray-100 px-8 py-4 text-lg font-medium rounded-full"
          >
            {isCreating ? 'Iniciando...' : 'Começar Agora'}
            <ArrowRight className="h-5 w-5 ml-2" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="text-2xl font-bold text-black mb-4 md:mb-0">Osprey</div>
            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <a href="#" className="hover:text-black transition-colors">Privacidade</a>
              <a href="#" className="hover:text-black transition-colors">Termos</a>
              <a href="#" className="hover:text-black transition-colors">Suporte</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default AutoApplicationStart;