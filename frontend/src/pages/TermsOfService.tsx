import { ArrowLeft, Scale, AlertTriangle, Globe } from "lucide-react";
import { useNavigate } from "react-router-dom";

const TermsOfService = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container-responsive">
          <div className="flex items-center justify-between py-4">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Voltar</span>
            </button>
            
            <div className="flex items-center gap-2">
              <Scale className="h-5 w-5 text-muted-foreground" />
              <h1 className="text-xl font-semibold text-foreground">Termos de Uso</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="container-responsive py-12">
        <div className="max-w-4xl mx-auto">
          
          {/* Hero Section */}
          <div className="text-center mb-12 space-y-4">
            <div className="w-20 h-20 bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl flex items-center justify-center mx-auto">
              <Scale className="h-10 w-10 text-white" />
            </div>
            
            <h1 className="text-4xl font-bold text-foreground">
              Termos de Uso
            </h1>
            
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Entenda seus direitos e responsabilidades ao utilizar a OSPREY Immigration AI.
            </p>
            
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <Globe className="h-4 w-4" />
              <span>Versão simplificada - Inglês e Português</span>
            </div>
          </div>

          {/* Important Notice */}
          <div className="bg-orange-50 border border-orange-200 rounded-2xl p-6 mb-8">
            <div className="flex items-start gap-4">
              <AlertTriangle className="h-6 w-6 text-orange-600 mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-orange-900 mb-2">Aviso Importante</h3>
                <p className="text-orange-800 text-sm leading-relaxed">
                  A OSPREY é uma ferramenta tecnológica de auxílio. <strong>Não somos um escritório de advocacia</strong> e não fornecemos aconselhamento jurídico. Para casos complexos, recomendamos consultar um advogado especializado em imigração.
                </p>
              </div>
            </div>
          </div>

          {/* Content Sections */}
          <div className="prose prose-lg max-w-none space-y-12">
            
            {/* 1. Natureza da Plataforma */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-blue-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">1</span>
                Natureza da Plataforma
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <div className="space-y-3 text-muted-foreground">
                    <p>OSPREY is a technology platform designed to help individuals organize, validate, and manage their own immigration applications.</p>
                    <p className="font-semibold text-red-600">OSPREY is not a law firm, not a preparer, and not a legal representative.</p>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <div className="space-y-3 text-muted-foreground">
                    <p>A OSPREY é uma plataforma tecnológica desenvolvida para auxiliar indivíduos a organizar, validar e gerenciar suas próprias aplicações de imigração.</p>
                    <p className="font-semibold text-red-600">A OSPREY não é um escritório de advocacia, não é um preparador e não é um representante legal.</p>
                  </div>
                </div>
              </div>
            </section>

            {/* 2. Limitação de Responsabilidade */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-red-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">2</span>
                Limitação de Responsabilidade
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li className="font-semibold">OSPREY does not provide legal advice.</li>
                    <li className="font-semibold">OSPREY does not decide which visa type you should apply for.</li>
                    <li className="font-semibold">OSPREY does not represent you before USCIS or any other government agency.</li>
                    <li>All requirements and supporting evidence displayed in OSPREY are based on publicly available USCIS instructions.</li>
                    <li className="font-semibold">Users remain solely responsible for reviewing, completing, and submitting their own applications.</li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li className="font-semibold">A OSPREY não fornece aconselhamento jurídico.</li>
                    <li className="font-semibold">A OSPREY não decide qual tipo de visto você deve solicitar.</li>
                    <li className="font-semibold">A OSPREY não o representa perante o USCIS ou qualquer outro órgão governamental.</li>
                    <li>Todas as exigências e documentos de apoio exibidos na OSPREY são baseados em instruções públicas disponíveis no site do USCIS.</li>
                    <li className="font-semibold">Os usuários permanecem totalmente responsáveis por revisar, completar e enviar suas próprias aplicações.</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 3. Casos Complexos */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-yellow-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">3</span>
                Casos Complexos
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <div className="space-y-3 text-muted-foreground">
                    <p className="font-semibold">For complex or exceptional cases, we strongly recommend that you consult with a licensed immigration attorney.</p>
                    <p>OSPREY may provide information about partner attorneys, but this is optional and separate from our services.</p>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <div className="space-y-3 text-muted-foreground">
                    <p className="font-semibold">Para casos complexos ou excepcionais, recomendamos fortemente que você consulte um advogado de imigração licenciado.</p>
                    <p>A OSPREY pode fornecer informações sobre advogados parceiros, mas isso é opcional e separado dos nossos serviços.</p>
                  </div>
                </div>
              </div>
            </section>

            {/* 4. Uso Aceitável */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-green-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">4</span>
                Uso Aceitável
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <p className="text-muted-foreground mb-4">By using OSPREY, you agree to:</p>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li>Use the platform only for lawful purposes.</li>
                    <li>Provide accurate and truthful information in your application.</li>
                    <li>Accept that OSPREY is a tool for assistance, not a substitute for professional legal advice.</li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <p className="text-muted-foreground mb-4">Ao utilizar a OSPREY, você concorda em:</p>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li>Usar a plataforma apenas para fins legais.</li>
                    <li>Fornecer informações precisas e verdadeiras em sua aplicação.</li>
                    <li>Reconhecer que a OSPREY é uma ferramenta de auxílio, e não um substituto de aconselhamento jurídico profissional.</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 5. Privacidade e Dados */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-purple-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">5</span>
                Privacidade e Dados
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    We value your privacy. All data you provide is stored securely and is only used to generate and organize your immigration package. Please review our Privacy Policy for details.
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Nós valorizamos sua privacidade. Todos os dados fornecidos são armazenados de forma segura e utilizados apenas para gerar e organizar o seu pacote de imigração. Consulte nossa Política de Privacidade para mais detalhes.
                  </p>
                </div>
              </div>
            </section>

            {/* 6. Aceitação dos Termos */}
            <section className="glass rounded-2xl p-8 bg-gradient-to-r from-orange-50 to-red-50">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-orange-600 text-white rounded-lg flex items-center justify-center text-sm font-bold">6</span>
                Aceitação dos Termos
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <p className="text-muted-foreground leading-relaxed font-semibold">
                    By creating an account and using OSPREY, you acknowledge that you have read, understood, and agree to these Terms of Use.
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <p className="text-muted-foreground leading-relaxed font-semibold">
                    Ao criar uma conta e utilizar a OSPREY, você reconhece que leu, entendeu e concorda com estes Termos de Uso.
                  </p>
                </div>
              </div>
            </section>
            
            {/* Footer info */}
            <div className="text-center pt-8">
              <p className="text-sm text-muted-foreground">
                Última atualização: Setembro 2025 • Last updated: September 2025
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TermsOfService;