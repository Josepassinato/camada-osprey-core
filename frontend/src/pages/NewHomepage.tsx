import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { makeApiCall } from "@/utils/api";
import { 
  ArrowRight,
  CheckCircle,
  Clock,
  Shield,
  Zap,
  DollarSign,
  Users,
  FileText,
  TrendingUp,
  Award,
  Target,
  Sparkles,
  ChevronDown
} from "lucide-react";

const NewHomepage = () => {
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
      const sessionToken = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('osprey_session_token', sessionToken);
      
      const data = await makeApiCall('/auto-application/start', 'POST', {
        session_token: sessionToken
      });

      if (data && data.case && data.case.case_id) {
        localStorage.setItem('osprey_current_case_id', data.case.case_id);
        navigate('/auto-application/select-form', { 
          state: { caseId: data.case.case_id, sessionToken } 
        });
      } else {
        throw new Error('Resposta inválida do servidor');
      }
    } catch (error: any) {
      alert(`Erro ao iniciar aplicação: ${error.message}\n\nTente novamente ou recarregue a página.`);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
            Osprey
          </div>
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#como-funciona" className="text-gray-700 hover:text-purple-600 transition-colors font-medium">Como Funciona</a>
            <a href="#precos" className="text-gray-700 hover:text-purple-600 transition-colors font-medium">Preços</a>
            <a href="#depoimentos" className="text-gray-700 hover:text-purple-600 transition-colors font-medium">Depoimentos</a>
            <Button variant="outline" className="border-purple-600 text-purple-600 hover:bg-purple-50">
              Entrar
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-purple-50 via-white to-indigo-50 pt-20 pb-32">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center max-w-5xl mx-auto">
            {/* Social Proof Badge */}
            <div className="inline-flex items-center px-4 py-2 bg-white rounded-full shadow-lg mb-8 border border-purple-100">
              <Sparkles className="h-4 w-4 text-purple-600 mr-2" />
              <span className="text-sm font-semibold text-gray-900">Já ajudamos +1.000 pessoas</span>
            </div>
            
            {/* Main Headline */}
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Faça Seu Visto Americano
              <span className="block bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                10x Mais Rápido
              </span>
            </h1>
            
            {/* Subheadline */}
            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed">
              Plataforma inteligente que <strong>preenche automaticamente</strong> os formulários do USCIS. 
              Economize <strong className="text-purple-600">milhares de dólares</strong> e meses de espera.
            </p>
            
            {/* Value Props */}
            <div className="flex flex-wrap justify-center gap-6 mb-10">
              <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm border border-gray-200">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="font-medium text-gray-900">100% Self-Service</span>
              </div>
              <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm border border-gray-200">
                <Clock className="h-5 w-5 text-blue-600" />
                <span className="font-medium text-gray-900">15 minutos para começar</span>
              </div>
              <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm border border-gray-200">
                <DollarSign className="h-5 w-5 text-purple-600" />
                <span className="font-medium text-gray-900">A partir de $149</span>
              </div>
            </div>
            
            {/* CTA */}
            <div className="flex flex-col items-center gap-4">
              <Button 
                onClick={(e) => {
                  e.preventDefault();
                  if (!agreed) {
                    alert('Por favor, aceite os termos primeiro.');
                    return;
                  }
                  startApplication();
                }}
                disabled={!agreed || isCreating}
                className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white px-10 py-6 text-lg font-semibold rounded-full shadow-2xl shadow-purple-300 transform hover:scale-105 transition-all"
                size="lg"
              >
                {isCreating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Iniciando...
                  </>
                ) : (
                  <>
                    Começar Agora - É Grátis
                    <ArrowRight className="h-5 w-5 ml-2" />
                  </>
                )}
              </Button>
              
              {/* Terms */}
              <div className="flex items-start gap-3 max-w-md">
                <input
                  type="checkbox"
                  id="terms-hero"
                  checked={agreed}
                  onChange={(e) => setAgreed(e.target.checked)}
                  className="h-4 w-4 mt-1 accent-purple-600 cursor-pointer"
                />
                <label htmlFor="terms-hero" className="text-sm text-gray-600 cursor-pointer">
                  Concordo com os termos de uso e política de privacidade. Esta é uma ferramenta de auxílio, não consultoria jurídica.
                </label>
              </div>
              
              <p className="text-sm text-gray-500 mt-2">
                💳 Sem cartão de crédito • 🔒 100% Seguro • ⚡ Resultado em minutos
              </p>
            </div>
          </div>
          
          {/* Scroll Indicator */}
          <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
            <ChevronDown className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </section>

      {/* Problem/Solution Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            {/* Problem */}
            <div className="space-y-6">
              <div className="inline-block px-4 py-2 bg-red-100 rounded-full">
                <span className="text-red-700 font-semibold text-sm">O Problema Tradicional</span>
              </div>
              <h2 className="text-4xl font-bold text-gray-900">
                Processos de imigração são <span className="text-red-600">caros e complexos</span>
              </h2>
              <ul className="space-y-4">
                {[
                  { icon: "💰", text: "Serviços tradicionais cobram $5.000 - $15.000 por caso" },
                  { icon: "⏰", text: "Meses de espera para agendar consultas" },
                  { icon: "📄", text: "Formulários confusos de 20+ páginas" },
                  { icon: "❌", text: "Erros custam tempo e dinheiro" }
                ].map((item, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <span className="text-2xl">{item.icon}</span>
                    <span className="text-lg text-gray-700 pt-1">{item.text}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            {/* Solution */}
            <div className="space-y-6 bg-gradient-to-br from-purple-50 to-indigo-50 p-8 rounded-2xl border-2 border-purple-200">
              <div className="inline-block px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-full">
                <span className="text-white font-semibold text-sm">Nossa Solução</span>
              </div>
              <h2 className="text-4xl font-bold text-gray-900">
                Tecnologia que <span className="text-purple-600">simplifica tudo</span>
              </h2>
              <ul className="space-y-4">
                {[
                  { icon: <DollarSign className="h-6 w-6" />, text: "De $149 a $3.000 (até 95% mais barato)" },
                  { icon: <Zap className="h-6 w-6" />, text: "Comece hoje mesmo, em 15 minutos" },
                  { icon: <FileText className="h-6 w-6" />, text: "IA preenche formulários automaticamente" },
                  { icon: <CheckCircle className="h-6 w-6" />, text: "Sistema verifica erros antes de enviar" }
                ].map((item, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-purple-600 flex-shrink-0">
                      {item.icon}
                    </div>
                    <span className="text-lg text-gray-900 font-medium pt-2">{item.text}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="como-funciona" className="py-20 bg-gradient-to-br from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-2 bg-purple-100 rounded-full mb-4">
              <span className="text-purple-700 font-semibold text-sm">Processo Simplificado</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              3 Passos Simples Para Seu Visto
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Nossa IA guia você do início ao fim. Sem burocracia, sem complicação.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                icon: <Target className="h-8 w-8" />,
                title: "Escolha Seu Visto",
                description: "Selecione o tipo de visto que precisa. Oferecemos 7 categorias diferentes, de turismo a Green Card.",
                color: "from-purple-500 to-purple-600"
              },
              {
                step: "02",
                icon: <Sparkles className="h-8 w-8" />,
                title: "IA Preenche Tudo",
                description: "Responda perguntas simples em português. Nossa IA traduz e preenche automaticamente os formulários oficiais do USCIS.",
                color: "from-indigo-500 to-indigo-600"
              },
              {
                step: "03",
                icon: <Award className="h-8 w-8" />,
                title: "Baixe e Envie",
                description: "Receba todos os documentos organizados, revisados e prontos para submissão ao USCIS. Com instruções passo a passo.",
                color: "from-blue-500 to-blue-600"
              }
            ].map((item, idx) => (
              <div key={idx} className="relative">
                <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all border border-gray-100 h-full">
                  <div className="text-8xl font-bold text-gray-100 absolute -top-4 -left-2 select-none">
                    {item.step}
                  </div>
                  <div className={`w-16 h-16 bg-gradient-to-br ${item.color} rounded-2xl flex items-center justify-center text-white mb-6 relative z-10 shadow-lg`}>
                    {item.icon}
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">{item.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{item.description}</p>
                </div>
                {idx < 2 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-20">
                    <ArrowRight className="h-8 w-8 text-purple-300" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits/Features */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Por Que Escolher a Osprey?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Tecnologia de ponta para simplificar seu processo de imigração
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: <Shield className="h-8 w-8" />,
                title: "100% Seguro",
                description: "Dados criptografados e protegidos. Compliance total com USCIS."
              },
              {
                icon: <Zap className="h-8 w-8" />,
                title: "Inteligência Artificial",
                description: "IA treinada em milhares de casos aprovados pelo USCIS."
              },
              {
                icon: <Users className="h-8 w-8" />,
                title: "Suporte Dedicado",
                description: "Equipe disponível para tirar dúvidas durante todo o processo."
              },
              {
                icon: <TrendingUp className="h-8 w-8" />,
                title: "Taxa de Aprovação",
                description: "Nossa plataforma otimiza suas chances de aprovação."
              },
              {
                icon: <FileText className="h-8 w-8" />,
                title: "Formulários Oficiais",
                description: "Usamos apenas formulários oficiais e atualizados do USCIS."
              },
              {
                icon: <Clock className="h-8 w-8" />,
                title: "Acesso Vitalício",
                description: "Acesse e edite seus formulários quando precisar, para sempre."
              },
              {
                icon: <CheckCircle className="h-8 w-8" />,
                title: "Revisão Automática",
                description: "Sistema detecta erros e inconsistências antes do envio."
              },
              {
                icon: <DollarSign className="h-8 w-8" />,
                title: "Preço Justo",
                description: "Até 95% mais barato que serviços tradicionais."
              }
            ].map((feature, idx) => (
              <div key={idx} className="text-center group">
                <div className="w-20 h-20 bg-gradient-to-br from-purple-100 to-indigo-100 rounded-2xl flex items-center justify-center text-purple-600 mx-auto mb-4 group-hover:scale-110 transition-transform shadow-lg">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="precos" className="py-20 bg-gradient-to-br from-purple-50 via-white to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-2 bg-purple-100 rounded-full mb-4">
              <span className="text-purple-700 font-semibold text-sm">Preços Transparentes</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Preços Honestos. Sem Surpresas.
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Compare: Serviços tradicionais cobram $5.000-$15.000. Nossa tecnologia torna acessível.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                name: "Básico",
                price: "$149",
                original: "$299",
                description: "Perfeito para extensões e mudanças simples",
                features: [
                  "I-539 (Extensão Turista)",
                  "I-765 (Autorização Trabalho)",
                  "I-90 (Renovação Green Card)",
                  "Formulários preenchidos",
                  "Checklist de documentos",
                  "Acesso vitalício"
                ],
                popular: false
              },
              {
                name: "Intermediário",
                price: "$490",
                original: "$980",
                description: "Para estudantes e petições familiares",
                features: [
                  "Tudo do Básico +",
                  "F-1 (Visto Estudante)",
                  "I-130 (Petição Familiar)",
                  "Suporte prioritário",
                  "Revisão de documentos",
                  "Orientação passo-a-passo"
                ],
                popular: true
              },
              {
                name: "Premium",
                price: "$1.250",
                original: "$2.500-$3.000",
                description: "Green Card por habilidade extraordinária",
                features: [
                  "Tudo do Intermediário +",
                  "EB-2 NIW (Interesse Nacional)",
                  "EB-1A (Habilidade Extraordinária)",
                  "Análise de elegibilidade",
                  "Estratégia personalizada",
                  "Consultoria especializada"
                ],
                popular: false
              }
            ].map((plan, idx) => (
              <div 
                key={idx} 
                className={`bg-white rounded-2xl p-8 border-2 hover:shadow-2xl transition-all relative ${
                  plan.popular 
                    ? 'border-purple-600 shadow-xl scale-105' 
                    : 'border-gray-200'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-1 rounded-full text-sm font-bold shadow-lg">
                      MAIS POPULAR
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600 text-sm mb-4">{plan.description}</p>
                  <div className="flex items-center justify-center gap-2">
                    <span className="text-gray-400 line-through text-lg">{plan.original}</span>
                    <span className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                      {plan.price}
                    </span>
                  </div>
                  <p className="text-green-600 text-sm font-semibold mt-2">
                    🎉 50% OFF Lançamento
                  </p>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, fidx) => (
                    <li key={fidx} className="flex items-start gap-3">
                      <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button 
                  className={`w-full py-6 text-lg font-semibold ${
                    plan.popular
                      ? 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white shadow-lg'
                      : 'bg-white border-2 border-purple-600 text-purple-600 hover:bg-purple-50'
                  }`}
                  onClick={startApplication}
                >
                  Começar Agora
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
              </div>
            ))}
          </div>

          <p className="text-center text-gray-600 mt-12">
            💳 Pagamento seguro via Stripe • 🔒 Garantia de satisfação • 🎟️ Use o cupom <strong>LANCAMENTO50</strong> no checkout
          </p>
        </div>
      </section>

      {/* Testimonials */}
      <section id="depoimentos" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              O Que Nossos Clientes Dizem
            </h2>
            <p className="text-xl text-gray-600">
              Milhares de pessoas já realizaram o sonho americano com a Osprey
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: "Maria Silva",
                role: "Visto F-1 Aprovado",
                avatar: "👩🏻‍💼",
                text: "Economizei mais de $8.000 comparado aos serviços tradicionais. O processo foi tão simples que consegui fazer sozinha em um fim de semana. Recomendo demais!",
                rating: 5
              },
              {
                name: "Carlos Santos",
                role: "Green Card EB-2 NIW",
                avatar: "👨🏽‍💻",
                text: "A plataforma me guiou em cada passo do caminho. A IA preencheu tudo perfeitamente e o suporte foi excepcional. Meu Green Card foi aprovado!",
                rating: 5
              },
              {
                name: "Ana Rodrigues",
                role: "Extensão B-1/B-2",
                avatar: "👩🏻‍🎓",
                text: "Estava preocupada com a complexidade, mas a Osprey tornou tudo tão fácil. Em 15 minutos tinha tudo pronto. Valeu cada centavo!",
                rating: 5
              }
            ].map((testimonial, idx) => (
              <div key={idx} className="bg-gradient-to-br from-purple-50 to-white rounded-2xl p-8 border border-purple-100 hover:shadow-xl transition-all">
                <div className="flex items-center gap-2 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <span key={i} className="text-yellow-400 text-xl">⭐</span>
                  ))}
                </div>
                <p className="text-gray-700 mb-6 italic leading-relaxed">
                  "{testimonial.text}"
                </p>
                <div className="flex items-center gap-3">
                  <span className="text-4xl">{testimonial.avatar}</span>
                  <div>
                    <p className="font-bold text-gray-900">{testimonial.name}</p>
                    <p className="text-sm text-gray-600">{testimonial.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 bg-gradient-to-r from-purple-600 to-indigo-600 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-pattern opacity-10"></div>
        
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Pronto Para Realizar Seu Sonho Americano?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Junte-se a milhares de pessoas que já simplificaram seu processo de imigração
          </p>
          
          <div className="flex flex-col items-center gap-4">
            <Button 
              onClick={startApplication}
              disabled={!agreed || isCreating}
              className="bg-white text-purple-600 hover:bg-gray-100 px-10 py-6 text-lg font-semibold rounded-full shadow-2xl transform hover:scale-105 transition-all"
              size="lg"
            >
              {isCreating ? 'Iniciando...' : 'Começar Agora - Grátis'}
              <ArrowRight className="h-5 w-5 ml-2" />
            </Button>
            
            <div className="flex items-start gap-3 max-w-md">
              <input
                type="checkbox"
                id="terms-final"
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
                className="h-4 w-4 mt-1 accent-white cursor-pointer"
              />
              <label htmlFor="terms-final" className="text-sm opacity-90 cursor-pointer">
                Concordo com os termos de uso. Esta é uma ferramenta tecnológica, não consultoria jurídica.
              </label>
            </div>
            
            <p className="text-sm opacity-75 mt-4">
              🚀 Comece em minutos • 💰 Economize milhares • ✅ Aprovação garantida ou seu dinheiro de volta
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent mb-4">
                Osprey
              </div>
              <p className="text-gray-600 text-sm">
                Simplificando processos de imigração através de tecnologia.
              </p>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-4">Produto</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-purple-600">Como Funciona</a></li>
                <li><a href="#" className="hover:text-purple-600">Preços</a></li>
                <li><a href="#" className="hover:text-purple-600">Vistos Disponíveis</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-4">Empresa</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-purple-600">Sobre Nós</a></li>
                <li><a href="#" className="hover:text-purple-600">Blog</a></li>
                <li><a href="#" className="hover:text-purple-600">Carreiras</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-4">Suporte</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-purple-600">Central de Ajuda</a></li>
                <li><a href="#" className="hover:text-purple-600">Contato</a></li>
                <li><a href="#" className="hover:text-purple-600">Termos de Uso</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-200 pt-8 text-center text-sm text-gray-600">
            <p>© 2024 Osprey. Todos os direitos reservados. Esta é uma plataforma de auxílio tecnológico, não consultoria jurídica.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default NewHomepage;
