import { ArrowLeft, Shield, FileText, Globe } from "lucide-react";
import { useNavigate } from "react-router-dom";

const PrivacyPolicy = () => {
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
              <Shield className="h-5 w-5 text-muted-foreground" />
              <h1 className="text-xl font-semibold text-foreground">Política de Privacidade</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="container-responsive py-12">
        <div className="max-w-4xl mx-auto">
          
          {/* Hero Section */}
          <div className="text-center mb-12 space-y-4">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto">
              <FileText className="h-10 w-10 text-white" />
            </div>
            
            <h1 className="text-4xl font-bold text-foreground">
              Política de Privacidade
            </h1>
            
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Na OSPREY Immigration AI, sua privacidade e proteção de dados são nossas maiores prioridades.
            </p>
            
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <Globe className="h-4 w-4" />
              <span>Versão bilíngue - Inglês e Português</span>
            </div>
          </div>

          {/* Content Sections */}
          <div className="prose prose-lg max-w-none space-y-12">
            
            {/* 1. Introdução */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-blue-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">1</span>
                Introdução
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    At OSPREY Immigration AI ("OSPREY"), your privacy and the protection of your personal information are our top priorities. This Privacy Policy explains how we collect, use, store, and delete the information you provide while using our platform.
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Na OSPREY Immigration AI ("OSPREY"), sua privacidade e a proteção das suas informações pessoais são nossas maiores prioridades. Esta Política de Privacidade explica como coletamos, utilizamos, armazenamos e descartamos as informações que você fornece ao utilizar nossa plataforma.
                  </p>
                </div>
              </div>
            </section>

            {/* 2. Natureza da Plataforma */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-green-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">2</span>
                Natureza da Plataforma
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <div className="space-y-2">
                    <p className="text-muted-foreground leading-relaxed">
                      OSPREY is a technology platform that facilitates the self-preparation of immigration applications.
                    </p>
                    <p className="text-muted-foreground leading-relaxed font-semibold">
                      We are not a law firm, not a preparer, and not a legal representative.
                    </p>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <div className="space-y-2">
                    <p className="text-muted-foreground leading-relaxed">
                      A OSPREY é uma plataforma tecnológica que facilita a auto-preparação de aplicações de imigração.
                    </p>
                    <p className="text-muted-foreground leading-relaxed font-semibold">
                      Nós não somos um escritório de advocacia, não atuamos como preparador e não representamos legalmente o usuário.
                    </p>
                  </div>
                </div>
              </div>
            </section>

            {/* 3. Coleta de Informações */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-purple-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">3</span>
                Coleta de Informações
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <p className="text-muted-foreground leading-relaxed mb-4">
                    We collect only the information that you voluntarily provide while preparing your immigration application. This may include:
                  </p>
                  <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
                    <li>Personal identification details (name, date of birth, address).</li>
                    <li>Supporting documents required by USCIS forms.</li>
                    <li>Information entered in our forms to generate your application package.</li>
                  </ul>
                  <p className="text-muted-foreground leading-relaxed mt-4 font-semibold">
                    We do not collect unnecessary or unrelated information.
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <p className="text-muted-foreground leading-relaxed mb-4">
                    Coletamos apenas as informações que você fornece voluntariamente durante a preparação da sua aplicação de imigração. Isso pode incluir:
                  </p>
                  <ul className="list-disc list-inside text-muted-foreground space-y-1 ml-4">
                    <li>Dados pessoais de identificação (nome, data de nascimento, endereço).</li>
                    <li>Documentos de apoio exigidos pelos formulários do USCIS.</li>
                    <li>Informações inseridas em nossos formulários para gerar seu pacote de aplicação.</li>
                  </ul>
                  <p className="text-muted-foreground leading-relaxed mt-4 font-semibold">
                    Não coletamos informações desnecessárias ou não relacionadas.
                  </p>
                </div>
              </div>
            </section>

            {/* 4. Uso das Informações */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-orange-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">4</span>
                Uso das Informações
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li>Your data is used only temporarily while you prepare your application.</li>
                    <li>The purpose is exclusively to facilitate the preparation and organization of your application.</li>
                    <li className="font-semibold">We do not provide legal advice based on your information.</li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li>Seus dados são usados apenas temporariamente enquanto você prepara a sua aplicação.</li>
                    <li>A finalidade é exclusivamente facilitar a preparação e organização da sua aplicação.</li>
                    <li className="font-semibold">Não fornecemos aconselhamento jurídico com base em suas informações.</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 5. Descarte de Informações */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-red-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">5</span>
                Descarte de Informações
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li>After you complete your process, all personal data and documents are automatically discarded and securely deleted from our systems.</li>
                    <li className="font-semibold">No permanent retention occurs.</li>
                    <li className="font-semibold">We do not build historical databases of user cases.</li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li>Após a conclusão do processo, todos os dados pessoais e documentos são automaticamente descartados e excluídos de forma segura de nossos sistemas.</li>
                    <li className="font-semibold">Não ocorre retenção permanente.</li>
                    <li className="font-semibold">Não construímos bancos de dados históricos com casos de usuários.</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 6. Compartilhamento de Informações */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-indigo-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">6</span>
                Compartilhamento de Informações
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li className="font-semibold">We do not sell, rent, or trade your information.</li>
                    <li>We do not share your information with third parties, except when legally required (e.g., by court order).</li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li className="font-semibold">Não vendemos, alugamos ou comercializamos suas informações.</li>
                    <li>Não compartilhamos suas informações com terceiros, exceto quando exigido por lei (ex.: ordem judicial).</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 7. Segurança dos Dados */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-teal-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">7</span>
                Segurança dos Dados
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li>All communications are encrypted (HTTPS/SSL).</li>
                    <li>Files are processed in secure environments with restricted access.</li>
                    <li>Temporary data storage uses modern encryption standards.</li>
                    <li>Logs are kept for operational monitoring, without storing your personal documents.</li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li>Todas as comunicações são criptografadas (HTTPS/SSL).</li>
                    <li>Os arquivos são processados em ambientes seguros e com acesso restrito.</li>
                    <li>O armazenamento temporário de dados utiliza padrões modernos de criptografia.</li>
                    <li>Logs são mantidos apenas para monitoramento operacional, sem armazenar seus documentos pessoais.</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 8. Direitos do Usuário */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-pink-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">8</span>
                Direitos do Usuário
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <p className="text-muted-foreground leading-relaxed mb-4">You have the right to:</p>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li>Access the data you temporarily provide.</li>
                    <li>Request correction of inaccurate information.</li>
                    <li>Request deletion of your data before completing the process.</li>
                    <li>Withdraw your consent at any time.</li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <p className="text-muted-foreground leading-relaxed mb-4">Você tem o direito de:</p>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li>Acessar os dados que fornece temporariamente.</li>
                    <li>Solicitar a correção de informações incorretas.</li>
                    <li>Solicitar a exclusão de seus dados antes da conclusão do processo.</li>
                    <li>Retirar seu consentimento a qualquer momento.</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 9. Conformidade Legal */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-yellow-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">9</span>
                Conformidade Legal
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <p className="text-muted-foreground leading-relaxed mb-4">
                    OSPREY complies with applicable data protection laws, including:
                  </p>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li>GDPR (General Data Protection Regulation – European Union).</li>
                    <li>CCPA (California Consumer Privacy Act – USA).</li>
                    <li>LGPD (Lei Geral de Proteção de Dados – Brazil).</li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <p className="text-muted-foreground leading-relaxed mb-4">
                    A OSPREY está em conformidade com as leis de proteção de dados aplicáveis, incluindo:
                  </p>
                  <ul className="list-disc list-inside text-muted-foreground space-y-2 ml-4">
                    <li>GDPR (Regulamento Geral de Proteção de Dados – União Europeia).</li>
                    <li>CCPA (Lei de Privacidade do Consumidor da Califórnia – EUA).</li>
                    <li>LGPD (Lei Geral de Proteção de Dados – Brasil).</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 10. Alterações desta Política */}
            <section className="glass rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-gray-500 text-white rounded-lg flex items-center justify-center text-sm font-bold">10</span>
                Alterações desta Política
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    We may update this Privacy Policy to reflect changes in technology, laws, or our practices. Any changes will be communicated on this page with a new "last updated" date.
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Podemos atualizar esta Política de Privacidade para refletir mudanças em tecnologia, leis ou em nossas práticas. Quaisquer alterações serão comunicadas nesta página com uma nova data de "última atualização".
                  </p>
                </div>
              </div>
            </section>

            {/* 11. Contato */}
            <section className="glass rounded-2xl p-8 bg-gradient-to-r from-blue-50 to-purple-50">
              <h2 className="text-2xl font-bold text-foreground mb-6 flex items-center gap-3">
                <span className="w-8 h-8 bg-blue-600 text-white rounded-lg flex items-center justify-center text-sm font-bold">11</span>
                Contato
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">English</h3>
                  <p className="text-muted-foreground leading-relaxed mb-3">
                    If you have any questions about this Privacy Policy, please contact us at:
                  </p>
                  <div className="flex items-center gap-2 text-blue-600 font-medium">
                    <span>📧</span>
                    <a href="mailto:privacy@osprey.ai" className="hover:underline">privacy@osprey.ai</a>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">Português</h3>
                  <p className="text-muted-foreground leading-relaxed mb-3">
                    Se tiver dúvidas sobre esta Política de Privacidade, entre em contato conosco em:
                  </p>
                  <div className="flex items-center gap-2 text-blue-600 font-medium">
                    <span>📧</span>
                    <a href="mailto:privacy@osprey.ai" className="hover:underline">privacy@osprey.ai</a>
                  </div>
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

export default PrivacyPolicy;