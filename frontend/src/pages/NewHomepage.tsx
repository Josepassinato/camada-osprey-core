import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/clerk-react";
import { Button } from "@/components/ui/button";
import { makeApiCall } from "@/utils/api";
import MariaChatWidget from "@/components/MariaChatWidget";
import BetaBanner from "@/components/BetaBanner";
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

    // Check if user is logged in
    const token = localStorage.getItem('osprey_token');
    const user = localStorage.getItem('osprey_user');
    
    if (!token || !user) {
      // User not logged in, redirect to signup
      localStorage.setItem('osprey_redirect_after_login', '/auto-application/select-form');
      navigate('/signup');
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
    } catch (error) {
      alert(`Erro ao iniciar aplicação: ${error.message}\n\nTente novamente ou recarregue a página.`);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Beta Banner - Only on homepage */}
      <BetaBanner />
      
      {/* Header */}
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
            Osprey
          </div>
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#como-funciona" className="text-gray-700 hover:text-purple-600 transition-colors font-medium">Como Funciona</a>
            <a href="#precos" className="text-gray-700 hover:text-purple-600 transition-colors font-medium">Preços</a>
            
            <SignedOut>
              <SignInButton mode="modal">
                <button
                  className="border-2 border-purple-600 bg-white text-purple-600 font-semibold px-4 py-2 rounded-lg transition-all hover:bg-purple-600 hover:text-white"
                >
                  Entrar
                </button>
              </SignInButton>
            </SignedOut>
            
            <SignedIn>
              <button
                onClick={() => navigate('/dashboard')}
                className="border-2 border-purple-600 bg-white text-purple-600 font-semibold px-4 py-2 rounded-lg transition-all hover:bg-purple-600 hover:text-white"
              >
                Dashboard
              </button>
              <UserButton 
                afterSignOutUrl="/"
                appearance={{
                  elements: {
                    avatarBox: "w-10 h-10"
                  }
                }}
              />
            </SignedIn>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-purple-50 via-white to-indigo-50 pt-20 pb-32">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center max-w-5xl mx-auto">
            {/* Main Headline */}
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Aplique para seu <span className="text-purple-600">visto americano</span>
              <span className="block bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                10x mais rápido
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
                  Concordo com os termos de uso e política de privacidade. Entendo que esta é uma ferramenta de auxílio tecnológico, não consultoria jurídica. Se não tenho clareza sobre meu caminho imigratório, consultarei um advogado especializado.
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

      {/* Important Notice */}
      <section className="py-12 bg-gradient-to-r from-amber-50 to-orange-50 border-y-4 border-amber-400">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-2xl p-8 shadow-xl border-2 border-amber-400">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <div className="w-16 h-16 bg-gradient-to-br from-amber-500 to-orange-500 rounded-full flex items-center justify-center">
                  <Shield className="h-8 w-8 text-white" />
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-gray-900 mb-3 flex items-center gap-2">
                  ⚖️ Aviso Importante sobre Orientação Jurídica
                </h3>
                <p className="text-lg text-gray-800 leading-relaxed mb-4">
                  <strong className="text-amber-700">Caso você ainda não tenha clareza do seu melhor caminho imigratório,</strong> recomendamos <strong className="text-amber-700">fortemente a consulta de um advogado de imigração</strong> especializado antes de iniciar qualquer processo.
                </p>
                <div className="bg-amber-50 rounded-lg p-4 border-l-4 border-amber-500">
                  <p className="text-sm text-gray-700">
                    ℹ️ <strong>Nossa plataforma é uma ferramenta tecnológica</strong> que auxilia no preenchimento de formulários. Não substituímos aconselhamento jurídico personalizado. Para casos complexos ou dúvidas sobre elegibilidade, sempre consulte um profissional qualificado.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Target Audience - "Is This For You?" */}
      <section className="py-20 bg-gradient-to-br from-purple-50 via-white to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="inline-block px-4 py-2 bg-purple-100 rounded-full mb-4">
              <span className="text-purple-700 font-semibold text-sm">Qualificação</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Esta Ferramenta É Para Você Se...
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Identifique-se com pelo menos uma das situações abaixo:
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
            {[
              {
                icon: <Target className="h-8 w-8" />,
                title: "Você já sabe qual visto precisa",
                description: "Já pesquisou, já sabe exatamente qual tipo de visto ou mudança de status você quer aplicar, só precisa de ajuda para preencher corretamente os formulários oficiais.",
                color: "from-green-500 to-emerald-600",
                highlight: "✓ Caminho definido"
              },
              {
                icon: <FileText className="h-8 w-8" />,
                title: "A burocracia te assusta",
                description: "Você conhece seu caminho imigratório, tem direito ao visto, mas se perde na complexidade dos formulários oficiais de 20+ páginas do USCIS e na organização de documentos.",
                color: "from-blue-500 to-cyan-600",
                highlight: "✓ Precisa de orientação"
              },
              {
                icon: <DollarSign className="h-8 w-8" />,
                title: "Não tem recursos para profissional",
                description: "Você tem status e direito de aplicar para um visto, mas não tem os $5.000-$15.000 necessários para contratar serviços tradicionais. Prefere investir em si mesmo.",
                color: "from-purple-500 to-violet-600",
                highlight: "✓ Orçamento limitado"
              },
              {
                icon: <Shield className="h-8 w-8" />,
                title: "Medo de errar sozinho",
                description: "Você sabe que pode fazer self-petition ou auto aplicação, mas tem medo de cometer um erro banal que possa atrasar seu processo ou até prejudicá-lo. Precisa de validação.",
                color: "from-orange-500 to-red-600",
                highlight: "✓ Busca segurança"
              },
              {
                icon: <Clock className="h-8 w-8" />,
                title: "Quer agilidade e autonomia",
                description: "Você não quer esperar semanas para agendar consultas ou depender da disponibilidade de terceiros. Quer começar hoje e ter controle total do seu processo no seu tempo.",
                color: "from-indigo-500 to-blue-600",
                highlight: "✓ Independência"
              },
              {
                icon: <CheckCircle className="h-8 w-8" />,
                title: "Já tem documentação organizada",
                description: "Você é organizado, tem seus documentos em ordem (passaporte, I-94, comprovantes), só precisa de uma ferramenta inteligente que te guie no preenchimento correto dos formulários.",
                color: "from-teal-500 to-green-600",
                highlight: "✓ Está preparado"
              }
            ].map((item, idx) => (
              <div 
                key={idx}
                className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all border-2 border-gray-100 hover:border-purple-300 group"
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className={`w-14 h-14 bg-gradient-to-br ${item.color} rounded-xl flex items-center justify-center text-white flex-shrink-0 shadow-lg group-hover:scale-110 transition-transform`}>
                    {item.icon}
                  </div>
                  <div className="flex-1">
                    <div className="inline-block px-3 py-1 bg-green-100 rounded-full mb-2">
                      <span className="text-green-700 text-xs font-bold">{item.highlight}</span>
                    </div>
                  </div>
                </div>
                
                <h3 className="text-xl font-bold text-gray-900 mb-3 leading-tight">
                  {item.title}
                </h3>
                
                <p className="text-gray-600 leading-relaxed text-sm">
                  {item.description}
                </p>
              </div>
            ))}
          </div>

          {/* Call-out box */}
          <div className="mt-12 max-w-4xl mx-auto">
            <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl p-8 text-white text-center shadow-2xl">
              <h3 className="text-2xl md:text-3xl font-bold mb-4">
                ✓ Se identificou com pelo menos uma situação acima?
              </h3>
              <p className="text-lg opacity-90 mb-6">
                Então nossa ferramenta foi feita para você! Simplifique seu processo de imigração com tecnologia de ponta.
              </p>
              <Button 
                onClick={startApplication}
                disabled={!agreed || isCreating}
                className="bg-white text-purple-600 hover:bg-gray-100 px-8 py-4 text-lg font-semibold rounded-full shadow-xl transform hover:scale-105 transition-all"
              >
                Começar Minha Aplicação Agora
                <ArrowRight className="h-5 w-5 ml-2" />
              </Button>
              <p className="text-sm opacity-75 mt-4">
                Sem cartão de crédito para começar • 100% Seguro
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Not For You Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-xl p-8 border-2 border-gray-200 shadow-md">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
              ⚠️ Esta ferramenta <span className="text-red-600">NÃO é para você</span> se:
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              {[
                {
                  icon: "❓",
                  text: "Você não sabe qual tipo de visto ou processo precisa aplicar"
                },
                {
                  icon: "🤔",
                  text: "Tem dúvidas sobre sua elegibilidade ou direito ao visto"
                },
                {
                  icon: "⚖️",
                  text: "Seu caso envolve questões criminais ou violações de status"
                },
                {
                  icon: "🔍",
                  text: "Precisa de análise estratégica personalizada do seu caso"
                }
              ].map((item, idx) => (
                <div key={idx} className="flex items-start gap-3 p-4 bg-red-50 rounded-lg border border-red-200">
                  <span className="text-2xl flex-shrink-0">{item.icon}</span>
                  <p className="text-gray-700">{item.text}</p>
                </div>
              ))}
            </div>
            <div className="mt-6 p-4 bg-amber-50 rounded-lg border-l-4 border-amber-500">
              <p className="text-sm text-gray-800">
                <strong>💡 Nestes casos:</strong> Recomendamos fortemente que você consulte primeiro um advogado de imigração especializado para avaliar seu caso, definir a melhor estratégia e depois, se apropriado, utilize nossa ferramenta para executar o preenchimento dos formulários.
              </p>
            </div>
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
                  { icon: <FileText className="h-6 w-6" />, text: "Sistema preenche formulários automaticamente" },
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
              Nosso sistema guia você do início ao fim. Sem burocracia, sem complicação.
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
                title: "Sistema Preenche Tudo",
                description: "Responda perguntas simples em português. Nosso sistema traduz e preenche automaticamente os formulários oficiais do USCIS.",
                color: "from-indigo-500 to-indigo-600"
              },
              {
                step: "03",
                icon: <Award className="h-8 w-8" />,
                title: "Baixe e Envie",
                description: "Receba todos os documentos organizados, revisados e prontos para submissão ao USCIS. Com instruções passo a passo. Após 24 horas o link de download expira.",
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
                title: "Sistema Inteligente",
                description: "Sistema treinado em milhares de casos aprovados pelo USCIS."
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

      {/* USCIS Self-Representation Notice */}
      <section className="py-12 bg-gradient-to-r from-green-50 to-emerald-50 border-y border-green-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-2xl shadow-lg p-8 border-2 border-green-500">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-3xl">✅</span>
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-gray-900 mb-3">
                  Você Pode Se Representar Legalmente
                </h3>
                <div className="mb-4">
                  <p className="text-gray-800 font-semibold mb-2 leading-relaxed italic text-lg">
                    "You can always represent yourself before USCIS."
                  </p>
                  <p className="text-sm text-gray-600 mb-3">
                    <strong>— U.S. Citizenship and Immigration Services (USCIS)</strong>
                  </p>
                  <p className="text-gray-700 text-sm italic mb-2">
                    "Você sempre pode se representar perante o USCIS."
                  </p>
                  <a 
                    href="https://www.uscis.gov/sites/default/files/document/brochures/UPIL%20Brochure_English.pdf" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-green-700 hover:text-green-800 text-xs font-semibold inline-block"
                  >
                    📄 Ver documento oficial →
                  </a>
                </div>
                <div className="bg-green-50 border-l-4 border-green-600 p-4 rounded">
                  <p className="text-sm text-gray-700">
                    <strong>Nossa missão</strong> é facilitar esse direito através de tecnologia, 
                    tornando o processo mais simples, rápido e acessível para todos.
                  </p>
                </div>
                <a 
                  href="/about" 
                  className="inline-block mt-4 text-green-700 font-semibold hover:text-green-800 transition-colors"
                >
                  Saiba mais sobre auto-representação →
                </a>
              </div>
            </div>
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

                <button
                  className={`w-full py-6 text-lg font-semibold transition-all rounded-lg flex items-center justify-center gap-2 ${
                    plan.popular
                      ? 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white shadow-lg'
                      : 'bg-white border-2 border-purple-600 text-purple-600 hover:bg-purple-600 hover:text-white'
                  }`}
                  onClick={startApplication}
                >
                  Começar Agora
                  <ArrowRight className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>

          <p className="text-center text-gray-600 mt-12">
            💳 Pagamento seguro via Stripe • 🔒 Garantia de satisfação • 🎟️ Use o cupom <strong>LANCAMENTO50</strong> no checkout
          </p>
          <p className="text-center text-sm text-amber-600 mt-4 font-medium">
            ⏱️ <strong>Importante:</strong> Após a conclusão, o link de download do seu pacote expira em 24 horas
          </p>
        </div>
      </section>

      {/* Testimonials Section - Social Proof */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center justify-center gap-2 bg-purple-100 text-purple-700 px-4 py-2 rounded-full text-sm font-semibold mb-4">
              <Award className="w-4 h-4" />
              Histórias de Sucesso
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Milhares de Aplicações Bem-Sucedidas
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Veja o que nossos usuários dizem sobre como transformamos o processo de aplicação de visto
            </p>
          </div>

          {/* Testimonials Grid */}
          <div className="grid md:grid-cols-3 gap-8">
            {/* Testimonial 1 */}
            <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl p-8 border border-purple-200 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                  MC
                </div>
                <div>
                  <h4 className="font-bold text-gray-900">Maria Costa</h4>
                  <p className="text-sm text-gray-600">F-1 Estudante • Brasil</p>
                </div>
              </div>
              <div className="mb-4">
                <div className="flex gap-1 text-yellow-400 mb-3">
                  ⭐⭐⭐⭐⭐
                </div>
                <p className="text-gray-700 leading-relaxed">
                  &ldquo;Incrível! Preenchi meu formulário I-20 em menos de 20 minutos. O processo que parecia impossível ficou super simples. A validação por IA me ajudou a evitar erros que eu nem sabia que estava cometendo.&rdquo;
                </p>
              </div>
              <div className="text-sm text-purple-600 font-semibold">
                ✅ Visto aprovado em 3 semanas
              </div>
            </div>

            {/* Testimonial 2 */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 border border-blue-200 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                  RS
                </div>
                <div>
                  <h4 className="font-bold text-gray-900">Rafael Silva</h4>
                  <p className="text-sm text-gray-600">H-1B Trabalho • Portugal</p>
                </div>
              </div>
              <div className="mb-4">
                <div className="flex gap-1 text-yellow-400 mb-3">
                  ⭐⭐⭐⭐⭐
                </div>
                <p className="text-gray-700 leading-relaxed">
                  &ldquo;Economizei mais de $2000 que gastaria com um serviço de preenchimento. A plataforma é intuitiva e me guiou passo a passo. Senti confiança total nos documentos gerados.&rdquo;
                </p>
              </div>
              <div className="text-sm text-blue-600 font-semibold">
                ✅ Processo concluído em 1 dia
              </div>
            </div>

            {/* Testimonial 3 */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-8 border border-green-200 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-green-600 to-emerald-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                  AP
                </div>
                <div>
                  <h4 className="font-bold text-gray-900">Ana Pereira</h4>
                  <p className="text-sm text-gray-600">EB-1A Green Card • Brasil</p>
                </div>
              </div>
              <div className="mb-4">
                <div className="flex gap-1 text-yellow-400 mb-3">
                  ⭐⭐⭐⭐⭐
                </div>
                <p className="text-gray-700 leading-relaxed">
                  &ldquo;Achei que teria que contratar um advogado caríssimo. Com a Osprey, organizei tudo sozinha e depois levei para um advogado revisar. Economizei tempo e dinheiro!&rdquo;
                </p>
              </div>
              <div className="text-sm text-green-600 font-semibold">
                ✅ Documentos aprovados pelo advogado
              </div>
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                10,000+
              </div>
              <p className="text-gray-600 text-sm">Aplicações Processadas</p>
            </div>
            <div>
              <div className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                98%
              </div>
              <p className="text-gray-600 text-sm">Taxa de Satisfação</p>
            </div>
            <div>
              <div className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                15 min
              </div>
              <p className="text-gray-600 text-sm">Tempo Médio</p>
            </div>
            <div>
              <div className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                $2,500
              </div>
              <p className="text-gray-600 text-sm">Economia Média</p>
            </div>
          </div>

          {/* Legal Disclaimer */}
          <div className="mt-12 bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
            <p className="text-sm text-gray-700">
              <strong>Importante:</strong> Os depoimentos representam experiências individuais. Resultados podem variar. 
              Nossa plataforma é uma ferramenta tecnológica e não garante aprovação de vistos. 
              Recomendamos consultar um advogado de imigração para avaliação legal do seu caso.
            </p>
          </div>
        </div>
      </section>

      {/* Legal Disclaimer Before CTA */}
      <section className="py-12 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-xl p-6 shadow-md border-2 border-gray-200">
            <div className="flex items-start gap-3">
              <Shield className="h-6 w-6 text-amber-600 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-bold text-gray-900 mb-2">Disclaimer Importante:</h4>
                <p className="text-sm text-gray-700 leading-relaxed">
                  Esta plataforma é uma <strong>ferramenta de auxílio tecnológico</strong> e não constitui consultoria jurídica. 
                  <strong className="text-amber-700"> Se você ainda não tem clareza sobre qual é o melhor caminho imigratório para seu caso, recomendamos fortemente consultar um advogado de imigração</strong> antes de prosseguir. 
                  Nosso sistema auxilia no preenchimento de formulários, mas não avalia elegibilidade ou estratégias migratórias individuais.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* Testimonials Section - Social Proof */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center justify-center gap-2 bg-purple-100 text-purple-700 px-4 py-2 rounded-full text-sm font-semibold mb-4">
              <Award className="w-4 h-4" />
              Histórias de Sucesso
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Milhares de Aplicações Bem-Sucedidas
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Veja o que nossos usuários dizem sobre como transformamos o processo de aplicação de visto
            </p>
          </div>

          {/* Testimonials Grid */}
          <div className="grid md:grid-cols-3 gap-8">
            {/* Testimonial 1 */}
            <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl p-8 border border-purple-200 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                  MC
                </div>
                <div>
                  <h4 className="font-bold text-gray-900">Maria Costa</h4>
                  <p className="text-sm text-gray-600">F-1 Estudante • Brasil</p>
                </div>
              </div>
              <div className="mb-4">
                <div className="flex gap-1 text-yellow-400 mb-3">
                  ⭐⭐⭐⭐⭐
                </div>
                <p className="text-gray-700 leading-relaxed">
                  "Incrível! Preenchi meu formulário I-20 em menos de 20 minutos. O processo que parecia impossível ficou super simples. A validação por IA me ajudou a evitar erros que eu nem sabia que estava cometendo."
                </p>
              </div>
              <div className="text-sm text-purple-600 font-semibold">
                ✅ Visto aprovado em 3 semanas
              </div>
            </div>

            {/* Testimonial 2 */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 border border-blue-200 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                  RS
                </div>
                <div>
                  <h4 className="font-bold text-gray-900">Rafael Silva</h4>
                  <p className="text-sm text-gray-600">H-1B Trabalho • Portugal</p>
                </div>
              </div>
              <div className="mb-4">
                <div className="flex gap-1 text-yellow-400 mb-3">
                  ⭐⭐⭐⭐⭐
                </div>
                <p className="text-gray-700 leading-relaxed">
                  "Economizei mais de $2000 que gastaria com um serviço de preenchimento. A plataforma é intuitiva e me guiou passo a passo. Senti confiança total nos documentos gerados."
                </p>
              </div>
              <div className="text-sm text-blue-600 font-semibold">
                ✅ Processo concluído em 1 dia
              </div>
            </div>

            {/* Testimonial 3 */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-8 border border-green-200 hover:shadow-xl transition-shadow">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-green-600 to-emerald-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                  AP
                </div>
                <div>
                  <h4 className="font-bold text-gray-900">Ana Pereira</h4>
                  <p className="text-sm text-gray-600">EB-1A Green Card • Brasil</p>
                </div>
              </div>
              <div className="mb-4">
                <div className="flex gap-1 text-yellow-400 mb-3">
                  ⭐⭐⭐⭐⭐
                </div>
                <p className="text-gray-700 leading-relaxed">
                  "Achei que teria que contratar um advogado caríssimo. Com a Osprey, organizei tudo sozinha e depois levei para um advogado revisar. Economizei tempo e dinheiro!"
                </p>
              </div>
              <div className="text-sm text-green-600 font-semibold">
                ✅ Documentos aprovados pelo advogado
              </div>
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                10,000+
              </div>
              <p className="text-gray-600 text-sm">Aplicações Processadas</p>
            </div>
            <div>
              <div className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                98%
              </div>
              <p className="text-gray-600 text-sm">Taxa de Satisfação</p>
            </div>
            <div>
              <div className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                15 min
              </div>
              <p className="text-gray-600 text-sm">Tempo Médio</p>
            </div>
            <div>
              <div className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                $2,500
              </div>
              <p className="text-gray-600 text-sm">Economia Média</p>
            </div>
          </div>

          {/* Legal Disclaimer */}
          <div className="mt-12 bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
            <p className="text-sm text-gray-700">
              <strong>Importante:</strong> Os depoimentos representam experiências individuais. Resultados podem variar. 
              Nossa plataforma é uma ferramenta tecnológica e não garante aprovação de vistos. 
              Recomendamos consultar um advogado de imigração para avaliação legal do seu caso.
            </p>
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
            Simplifique seu processo de imigração com nossa plataforma inteligente
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
                Concordo com os termos. Entendo que esta é uma ferramenta tecnológica, não consultoria jurídica. Se necessário, consultarei um advogado de imigração.
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
                <li><a href="#como-funciona" className="hover:text-purple-600">Como Funciona</a></li>
                <li><a href="#precos" className="hover:text-purple-600">Preços</a></li>
                <li><a href="/auto-application/select-form" className="hover:text-purple-600">Vistos Disponíveis</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-4">Empresa</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="/about" className="hover:text-purple-600">Sobre Nós</a></li>
                <li><a href="/contact" className="hover:text-purple-600">Contato</a></li>
                <li><a href="/faq" className="hover:text-purple-600">FAQ</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="/privacy-policy" className="hover:text-purple-600">Política de Privacidade</a></li>
                <li><a href="/terms-of-use" className="hover:text-purple-600">Termos de Uso</a></li>
                <li><a href="/legal-disclaimer" className="hover:text-purple-600">Aviso Legal</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-200 pt-8 text-center text-sm text-gray-600">
            <p>© 2024 Osprey. Todos os direitos reservados. Esta é uma plataforma de auxílio tecnológico, não consultoria jurídica.</p>
          </div>
        </div>
      </footer>

      {/* Maria Chat Widget */}
      <MariaChatWidget />
    </div>
  );
};

export default NewHomepage;
