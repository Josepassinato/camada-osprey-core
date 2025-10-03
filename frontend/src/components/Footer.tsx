import { Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const footerSections = [
    {
      title: "Serviços",
      links: [
        { name: "Visto H1-B", href: "#" },
        { name: "Green Card", href: "#" },
        { name: "Visto de Estudante", href: "#" },
        { name: "Reunificação Familiar", href: "#" },
        { name: "Visto de Investidor", href: "#" },
        { name: "Visto de Turismo", href: "#" }
      ]
    },
    {
      title: "Empresa",
      links: [
        { name: "Sobre Nós", href: "#" },
        { name: "Nossa Equipe", href: "#" },
        { name: "Carreiras", href: "#" },
        { name: "Imprensa", href: "#" },
        { name: "Blog", href: "#" },
        { name: "Parceiros", href: "#" }
      ]
    },
    {
      title: "Recursos",
      links: [
        { name: "Central de Ajuda", href: "#" },
        { name: "Guias de Imigração", href: "#" },
        { name: "Calculadora de Custos", href: "#" },
        { name: "Status do Sistema", href: "#" },
        { name: "API Documentation", href: "#" },
        { name: "Webinars", href: "#" }
      ]
    },
    {
      title: "Legal",
      links: [
        { name: "Política de Privacidade", href: "/privacy-policy" },
        { name: "Termos de Uso", href: "#" },
        { name: "Cookies", href: "#" },
        { name: "Compliance", href: "#" },
        { name: "Segurança", href: "#" },
        { name: "GDPR", href: "#" }
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
              A plataforma líder em auto aplicação imigratória com tecnologia de IA avançada. 
              Transformando sonhos em realidade desde 2020.
            </p>

            {/* Trust badges */}
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="px-3 py-1 bg-success/10 text-success text-xs font-medium rounded-full">
                  SOC 2 Certified
                </div>
                <div className="px-3 py-1 bg-black/10 text-black text-xs font-medium rounded-full">
                  USCIS Approved
                </div>
              </div>
              
              <div className="flex items-center gap-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                  <span>5.000+ Aprovações</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-black rounded-full animate-pulse delay-300"></div>
                  <span>98% Taxa de Sucesso</span>
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
              <span>⚡ Powered by AI</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;