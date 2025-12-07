import { Sparkles, Shield, Phone, Mail, MapPin } from "lucide-react";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const footerSections = [
    {
      title: "Vistos Disponíveis",
      links: [
        { name: "F-1 (Estudante)", href: "/visa-selection" },
        { name: "H-1B (Trabalho)", href: "/visa-selection" },
        { name: "I-539 (Extensão)", href: "/visa-selection" },
        { name: "I-589 (Asilo)", href: "/visa-selection" },
        { name: "EB-1A (Green Card)", href: "/visa-selection" },
        { name: "Ver Todos", href: "/visa-selection" }
      ]
    },
    {
      title: "Empresa",
      links: [
        { name: "Sobre Nós", href: "/about" },
        { name: "Contato", href: "/contact" },
        { name: "FAQ", href: "/faq" },
        { name: "Como Funciona", href: "/about#como-funciona" }
      ]
    },
    {
      title: "Legal",
      links: [
        { name: "Política de Privacidade", href: "/privacy-policy" },
        { name: "Termos de Uso", href: "/terms-of-use" },
        { name: "Disclaimer Legal", href: "/legal-disclaimer" },
        { name: "Aviso de Limitações", href: "/legal-disclaimer" }
      ]
    },
    {
      title: "Suporte",
      links: [
        { name: "Central de Ajuda", href: "/faq" },
        { name: "Fale Conosco", href: "/contact" },
        { name: "Encontrar Advogado", href: "https://www.aila.org/find-a-lawyer", external: true }
      ]
    }
  ];

  const socialLinks = [
    { name: "LinkedIn", href: "#", icon: "💼" },
    { name: "Twitter", href: "#", icon: "🐦" },
    { name: "Facebook", href: "#", icon: "📘" },
    { name: "YouTube", href: "#", icon: "📺" },
    { name: "Instagram", href: "#", icon: "📸" }
  ];

  return (
    <footer className="bg-gradient-subtle border-t border-border">
      <div className="container-responsive">
        
        {/* Main footer content */}
        <div className="py-16 grid grid-cols-1 lg:grid-cols-6 gap-12">
          
          {/* Brand section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-black rounded-xl flex items-center justify-center shadow-glow">
                <Sparkles className="h-7 w-7 text-white" />
              </div>
              <div>
                <div className="text-2xl font-bold text-foreground">OSPREY</div>
                <div className="text-sm text-muted-foreground -mt-1">Immigration Platform</div>
              </div>
            </div>
            
            {/* Description */}
            <p className="text-muted-foreground leading-relaxed max-w-md">
              A plataforma líder em auto aplicação imigratória com tecnologia de sistema avançada. 
              Transformando sonhos em realidade desde 2020.
            </p>

            {/* Contact info */}
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-muted-foreground">
                <span className="text-lg">📧</span>
                <a 
                  href="mailto:contact@goosprey.com"
                  className="hover:text-foreground transition-colors"
                >
                  contact@goosprey.com
                </a>
              </div>
              
              <div className="flex items-center gap-4 mt-4">
                <div className="px-3 py-1 bg-success/10 text-success text-xs font-medium rounded-full">
                  SOC 2 Certified
                </div>
                <div className="px-3 py-1 bg-black/10 text-black text-xs font-medium rounded-full">
                  USCIS Approved
                </div>
              </div>
            </div>

            {/* Social links */}
            <div className="flex items-center gap-3">
              {socialLinks.map((social) => (
                <a
                  key={social.name}
                  href={social.href}
                  className="w-10 h-10 bg-white/50 hover:bg-white/80 rounded-lg flex items-center justify-center transition-colors text-lg"
                  aria-label={social.name}
                >
                  {social.icon}
                </a>
              ))}
            </div>
          </div>

          {/* Links sections */}
          {footerSections.map((section) => (
            <div key={section.title} className="space-y-6">
              <h3 className="text-lg font-semibold text-foreground">
                {section.title}
              </h3>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.name}>
                    <a
                      href={link.href}
                      className="text-muted-foreground hover:text-foreground transition-colors text-sm"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Newsletter section */}
        <div className="py-8 border-t border-border">
          <div className="glass rounded-2xl p-8 text-center">
            <h3 className="text-xl font-semibold text-foreground mb-3">
              Fique por dentro das novidades
            </h3>
            <p className="text-muted-foreground mb-6 max-w-lg mx-auto">
              Receba dicas exclusivas sobre imigração, atualizações das leis e 
              histórias de sucesso direto no seu email.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
              <input
                type="email"
                placeholder="Seu melhor email"
                className="flex-1 px-4 py-3 bg-white/80 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent text-sm"
              />
              <button className="px-6 py-3 bg-black text-black-foreground rounded-lg font-medium hover:shadow-glow transition-all duration-300 text-sm">
                Inscrever
              </button>
            </div>
          </div>
        </div>

        {/* Bottom section */}
        <div className="py-8 border-t border-border">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="text-sm text-muted-foreground">
              © {currentYear} OSPREY Immigration Platform. Todos os direitos reservados.
            </div>
            
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <span>🇺🇸 Baseado nos EUA</span>
              <span>🔒 Dados Seguros</span>
              <span>⚡ Powered by sistema</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;