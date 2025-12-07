import { useState } from "react";
import { ChevronDown, ChevronUp, Search, HelpCircle, MessageCircle, BookOpen, Shield, DollarSign, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const FAQ = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState("all");
  const [expandedQuestion, setExpandedQuestion] = useState<number | null>(null);

  const categories = [
    { id: "all", name: "Todas", icon: BookOpen },
    { id: "platform", name: "Sobre a Plataforma", icon: HelpCircle },
    { id: "process", name: "Processo de Aplicação", icon: FileText },
    { id: "security", name: "Segurança e Privacidade", icon: Shield },
    { id: "pricing", name: "Preços e Pagamentos", icon: DollarSign },
    { id: "support", name: "Suporte", icon: MessageCircle },
  ];

  const faqs = [
    // Sobre a Plataforma
    {
      category: "platform",
      question: "O que é o Osprey (DocSimple)?",
      answer: "Osprey é uma plataforma tecnológica que auxilia na organização e preparação de documentos para processos de imigração nos Estados Unidos. Utilizamos IA avançada para ajudar você a preencher formulários oficiais do USCIS de forma mais rápida e organizada. IMPORTANTE: Não somos um escritório de advocacia e não oferecemos consultoria jurídica."
    },
    {
      category: "platform",
      question: "Vocês são advogados de imigração?",
      answer: "NÃO. Somos uma plataforma tecnológica de organização de documentos. Não oferecemos consultoria jurídica, não analisamos casos individuais e não recomendamos tipos de visto. Recomendamos fortemente que você consulte um advogado de imigração qualificado para avaliar seu caso específico, especialmente se houver qualquer complexidade ou dúvida jurídica."
    },
    {
      category: "platform",
      question: "Posso aplicar para visto sem advogado? É legal fazer isso por conta própria?",
      answer: "SIM! Você tem o DIREITO LEGAL de se auto-representar perante o USCIS.\n\nSegundo documento oficial do USCIS:\n\n\"You can always represent yourself before USCIS.\"\n— U.S. Citizenship and Immigration Services (USCIS)\n\nTradução: \"Você sempre pode se representar perante o USCIS.\"\n\nFonte: USCIS Official Brochure \"Who can help me with my USCIS case?\" (https://www.uscis.gov/sites/default/files/document/brochures/UPIL%20Brochure_English.pdf)\n\nNossa plataforma existe justamente para facilitar esse direito, oferecendo ferramentas que ajudam você a organizar documentos e preencher formulários oficiais corretamente. Para casos simples e diretos, muitas pessoas conseguem aplicar com sucesso por conta própria.\n\nIMPORTANTE: Para casos complexos (ex: histórico criminal, negações anteriores, situações especiais), recomendamos fortemente consultar um advogado de imigração qualificado. O USCIS adverte que apenas advogados licenciados e representantes credenciados pela BIA (Board of Immigration Appeals) podem fornecer aconselhamento jurídico de imigração."
    },
    {
      category: "platform",
      question: "Como a plataforma funciona?",
      answer: "Nossa plataforma funciona em etapas simples: 1) Você escolhe o tipo de visto que deseja aplicar, 2) Responde a perguntas em linguagem simples sobre sua situação, 3) Nossa IA organiza suas respostas e preenche automaticamente os formulários oficiais do USCIS, 4) Você revisa e baixa os documentos prontos para submissão. Todo o processo é guiado e leva cerca de 15-30 minutos."
    },
    {
      category: "platform",
      question: "Quais tipos de visto vocês suportam?",
      answer: "Atualmente suportamos os seguintes vistos: F-1 (Estudante), H-1B (Trabalho Temporário), I-539 (Extensão/Mudança de Status), I-589 (Pedido de Asilo), EB-1A (Green Card para Pessoas com Habilidades Extraordinárias), I-130 (Petição para Parente Estrangeiro), entre outros. Estamos constantemente adicionando novos tipos de visto à plataforma."
    },

    // Processo de Aplicação
    {
      category: "process",
      question: "Quanto tempo leva para completar uma aplicação?",
      answer: "Em média, nossos usuários completam o preenchimento dos formulários em 15-30 minutos, dependendo da complexidade do visto. Isso é muito mais rápido do que preencher manualmente os formulários do USCIS, que pode levar várias horas ou dias. Você pode salvar seu progresso e voltar a qualquer momento."
    },
    {
      category: "process",
      question: "Posso salvar meu progresso e continuar depois?",
      answer: "Sim! Nossa plataforma possui a funcionalidade 'Salvar e Continuar'. Seu progresso é automaticamente salvo conforme você preenche o formulário. Você pode fazer logout e retornar a qualquer momento para continuar de onde parou."
    },
    {
      category: "process",
      question: "O que acontece depois que eu completo o formulário?",
      answer: "Após completar e revisar todas as informações, você poderá baixar: 1) Formulários oficiais do USCIS preenchidos e prontos para impressão/submissão, 2) Checklist de documentos necessários para anexar, 3) Guia de instruções para submissão. Você será responsável por imprimir, assinar e enviar os formulários ao USCIS seguindo as instruções oficiais."
    },
    {
      category: "process",
      question: "Vocês enviam os formulários ao USCIS por mim?",
      answer: "Não. Nós preparamos e organizamos os documentos, mas VOCÊ é responsável por revisar, assinar e enviar os formulários ao USCIS. Fornecemos instruções detalhadas sobre como e para onde enviar, mas o envio é de sua responsabilidade."
    },
    {
      category: "process",
      question: "Como sei se as informações estão corretas?",
      answer: "Nossa IA realiza validação em duas etapas: primeiro, verifica se todos os campos obrigatórios foram preenchidos corretamente; segundo, analisa a coerência e completude das informações fornecidas. No entanto, VOCÊ é o responsável final por revisar e confirmar a veracidade de todas as informações antes da submissão ao USCIS. Recomendamos também que um advogado de imigração revise seus documentos."
    },

    // Segurança e Privacidade
    {
      category: "security",
      question: "Meus dados estão seguros?",
      answer: "Sim. Levamos a segurança dos seus dados muito a sério. Utilizamos criptografia de ponta a ponta, armazenamento seguro em servidores certificados SOC 2, e seguimos as melhores práticas de segurança da indústria. Seus dados pessoais nunca são compartilhados com terceiros sem seu consentimento explícito. Para mais detalhes, consulte nossa Política de Privacidade."
    },
    {
      category: "security",
      question: "Quem tem acesso às minhas informações?",
      answer: "Apenas você e nossa equipe técnica autorizada (para fins de suporte técnico e manutenção da plataforma) têm acesso às suas informações. Não vendemos, alugamos ou compartilhamos seus dados com terceiros para fins de marketing. Todos os acessos são registrados e auditados regularmente."
    },
    {
      category: "security",
      question: "Por quanto tempo vocês mantêm meus dados?",
      answer: "Mantemos seus dados enquanto sua conta estiver ativa e por um período adicional conforme exigido por lei. Você pode solicitar a exclusão completa de seus dados a qualquer momento através da nossa página de contato. Processamos solicitações de exclusão em até 30 dias."
    },
    {
      category: "security",
      question: "Vocês estão em conformidade com LGPD e GDPR?",
      answer: "Sim. Nossa Política de Privacidade está em conformidade com a Lei Geral de Proteção de Dados (LGPD) do Brasil, o General Data Protection Regulation (GDPR) da União Europeia, e leis de privacidade aplicáveis nos Estados Unidos. Você tem direito de acessar, corrigir, exportar e excluir seus dados a qualquer momento."
    },

    // Preços e Pagamentos
    {
      category: "pricing",
      question: "Quanto custa usar a plataforma?",
      answer: "Nossos preços variam de acordo com o tipo de visto e complexidade da aplicação. Os valores começam a partir de $149 por aplicação completa. Isso inclui: preenchimento guiado de formulários, validação por IA, geração de PDFs prontos para submissão, checklist de documentos e suporte básico. Não há taxas ocultas. Você paga apenas uma vez por aplicação."
    },
    {
      category: "pricing",
      question: "Este valor inclui as taxas do USCIS?",
      answer: "NÃO. O valor que você paga à nossa plataforma é apenas pelo serviço de organização e preparação de documentos. As taxas oficiais do USCIS (que variam de $85 a $700+ dependendo do tipo de visto) devem ser pagas diretamente ao governo dos EUA no momento da submissão da sua aplicação. Informamos claramente qual será a taxa do USCIS para seu tipo de visto."
    },
    {
      category: "pricing",
      question: "Vocês oferecem reembolso?",
      answer: "Oferecemos garantia de satisfação. Se você não estiver satisfeito com nossa plataforma antes de completar e baixar seus formulários, entre em contato conosco para um reembolso total. Após o download dos documentos finalizados, reembolsos são avaliados caso a caso. Por favor, consulte nossos Termos de Uso para detalhes completos."
    },
    {
      category: "pricing",
      question: "Quais formas de pagamento vocês aceitam?",
      answer: "Aceitamos todos os principais cartões de crédito e débito (Visa, Mastercard, American Express) através do Stripe, nosso processador de pagamentos seguro. Não armazenamos informações de cartão de crédito em nossos servidores. Todos os pagamentos são processados de forma segura e criptografada."
    },
    {
      category: "pricing",
      question: "Preciso pagar antes de usar a plataforma?",
      answer: "Não necessariamente. Você pode criar uma conta e explorar a plataforma gratuitamente. O pagamento é solicitado apenas quando você deseja baixar os formulários finalizados e prontos para submissão. Isso permite que você experimente nossa plataforma antes de se comprometer financeiramente."
    },

    // Suporte
    {
      category: "support",
      question: "Como posso entrar em contato com o suporte?",
      answer: "Você pode entrar em contato conosco através de: 1) Email: contato@docsimple.com (respondemos em até 24 horas úteis), 2) Formulário de contato na página 'Contato', 3) Chat da Maria (nossa assistente virtual) disponível 24/7 para dúvidas rápidas sobre a plataforma. Para questões legais sobre seu caso específico, recomendamos consultar um advogado."
    },
    {
      category: "support",
      question: "Vocês oferecem suporte em português?",
      answer: "Sim! Nossa plataforma e nosso suporte estão disponíveis em português e inglês. A Maria, nossa assistente virtual, também fala ambos os idiomas e pode ajudá-lo a navegar pela plataforma."
    },
    {
      category: "support",
      question: "Vocês podem revisar meus documentos?",
      answer: "Podemos revisar se os formulários foram preenchidos corretamente do ponto de vista técnico (campos obrigatórios, formatação, etc.). No entanto, NÃO podemos revisar a estratégia legal do seu caso ou avaliar se as informações fornecidas são adequadas para sua situação. Para revisão legal, você deve consultar um advogado de imigração licenciado."
    },
    {
      category: "support",
      question: "E se eu tiver dúvidas sobre qual visto aplicar?",
      answer: "NÃO podemos recomendar qual tipo de visto você deve aplicar, pois isso constitui aconselhamento legal. Nossa plataforma pode fornecer informações gerais sobre cada tipo de visto, mas a decisão final deve ser tomada por você, preferencialmente com orientação de um advogado de imigração qualificado que possa analisar sua situação específica."
    },
    {
      category: "support",
      question: "Vocês oferecem indicação de advogados?",
      answer: "Sim. Podemos indicar recursos para encontrar advogados de imigração qualificados, como o site da American Immigration Lawyers Association (AILA) em www.aila.org/find-a-lawyer. No entanto, não temos afiliação com nenhum advogado específico e não recebemos comissões por indicações."
    },
  ];

  const filteredFaqs = faqs.filter(faq => {
    const matchesCategory = activeCategory === "all" || faq.category === activeCategory;
    const matchesSearch = faq.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          faq.answer.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40 backdrop-blur-sm bg-white/90">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <a href="/" className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
            Osprey
          </a>
          <nav className="flex items-center gap-6">
            <a href="/" className="text-gray-700 hover:text-purple-600 transition-colors">Início</a>
            <a href="/contact" className="text-gray-700 hover:text-purple-600 transition-colors">Contato</a>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-white/20 rounded-full mb-6">
              <HelpCircle className="w-8 h-8" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Perguntas Frequentes (FAQ)
            </h1>
            <p className="text-xl text-blue-100 max-w-2xl mx-auto">
              Encontre respostas para as dúvidas mais comuns sobre nossa plataforma
            </p>
          </div>
        </div>
      </section>

      {/* Search and Filter Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8">
        <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-200">
          {/* Search Bar */}
          <div className="relative mb-6">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              type="text"
              placeholder="Pesquisar perguntas..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-12 pr-4 py-3 w-full text-lg border-gray-300 focus:border-purple-500 focus:ring-purple-500"
            />
          </div>

          {/* Category Filter */}
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => {
              const Icon = category.icon;
              return (
                <button
                  key={category.id}
                  onClick={() => setActiveCategory(category.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                    activeCategory === category.id
                      ? "bg-purple-600 text-white shadow-md"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {category.name}
                </button>
              );
            })}
          </div>
        </div>
      </section>

      {/* FAQ List */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="space-y-4">
          {filteredFaqs.length === 0 ? (
            <div className="text-center py-16">
              <p className="text-gray-500 text-lg">
                Nenhuma pergunta encontrada. Tente outra busca ou categoria.
              </p>
            </div>
          ) : (
            filteredFaqs.map((faq, index) => (
              <div
                key={index}
                className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
              >
                <button
                  onClick={() => setExpandedQuestion(expandedQuestion === index ? null : index)}
                  className="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                >
                  <span className="text-lg font-semibold text-gray-900 pr-4">
                    {faq.question}
                  </span>
                  {expandedQuestion === index ? (
                    <ChevronUp className="w-5 h-5 text-purple-600 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  )}
                </button>
                
                {expandedQuestion === index && (
                  <div className="px-6 pb-5 pt-0">
                    <div className="prose prose-blue max-w-none">
                      <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                        {faq.answer}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Não encontrou sua resposta?
          </h2>
          <p className="text-xl text-purple-100 mb-8">
            Nossa equipe está pronta para ajudar você com qualquer dúvida
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              onClick={() => window.location.href = '/contact'}
              className="bg-white text-purple-600 hover:bg-gray-100 px-8 py-3 text-lg font-semibold rounded-lg shadow-lg"
            >
              Entre em Contato
            </Button>
            <Button
              onClick={() => window.location.href = '/'}
              variant="outline"
              className="border-2 border-white text-white hover:bg-white/10 px-8 py-3 text-lg font-semibold rounded-lg"
            >
              Voltar ao Início
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-8 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-600 text-sm">
            © 2024 Osprey. Todos os direitos reservados. Esta é uma plataforma de auxílio tecnológico, não consultoria jurídica.
          </p>
          <div className="mt-4 flex justify-center gap-6 text-sm">
            <a href="/privacy-policy" className="text-gray-600 hover:text-purple-600">Política de Privacidade</a>
            <a href="/terms-of-use" className="text-gray-600 hover:text-purple-600">Termos de Uso</a>
            <a href="/legal-disclaimer" className="text-gray-600 hover:text-purple-600">Aviso Legal</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default FAQ;
