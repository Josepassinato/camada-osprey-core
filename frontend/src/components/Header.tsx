import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Menu, X, Sparkles, ChevronDown, User, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Header = () => {
  const navigate = useNavigate();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    // Check for logged in user
    const userData = localStorage.getItem('osprey_user');
    if (userData) {
      setUser(JSON.parse(userData));
    }

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('osprey_token');
    localStorage.removeItem('osprey_user');
    setUser(null);
    navigate('/');
  };

  const navigation = [
    { name: "Serviços", href: "#services", hasDropdown: true },
    { name: "Como Funciona", href: "#process" },
    { name: "Preços", href: "#pricing" },
    { name: "Sobre", href: "#about" },
  ];

  return (
    <header 
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        isScrolled 
          ? "glass border-b border-white/20 shadow-soft" 
          : "bg-transparent"
      }`}
    >
      <div className="container-responsive">
        <div className="flex items-center justify-between h-16 lg:h-20">
          
          {/* Logo */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            <div className="relative">
              <div className="w-10 h-10 bg-black rounded-xl flex items-center justify-center shadow-glow">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
            </div>
            <div>
              <div className="text-xl font-bold text-foreground">OSPREY</div>
              <div className="text-xs text-muted-foreground -mt-1">Immigration Platform</div>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center space-x-8">
            {navigation.map((item) => (
              <div key={item.name} className="relative group">
                <a
                  href={item.href}
                  className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors group-hover:bg-white/50 rounded-lg"
                >
                  {item.name}
                  {item.hasDropdown && (
                    <ChevronDown className="h-4 w-4 transition-transform group-hover:rotate-180" />
                  )}
                </a>
                
                {/* Dropdown menu simulation */}
                {item.hasDropdown && (
                  <div className="absolute top-full left-0 w-64 glass border border-white/20 rounded-xl shadow-elegant opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 mt-2 p-4 space-y-3">
                    <div className="text-xs font-medium text-black mb-3">Tipos de Visto</div>
                    {["Visto H1-B", "Visto L1", "Green Card", "Visto de Estudante"].map((service) => (
                      <a key={service} href="#" className="block text-sm text-muted-foreground hover:text-foreground transition-colors py-1">
                        {service}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </nav>

          {/* Desktop CTA */}
          <div className="hidden lg:flex items-center gap-4">
            {user ? (
              <>
                <Button 
                  variant="ghost" 
                  className="font-medium"
                  onClick={() => navigate('/dashboard')}
                >
                  <User className="h-4 w-4" />
                  Dashboard
                </Button>
                <Button 
                  variant="outline" 
                  onClick={handleLogout}
                >
                  <LogOut className="h-4 w-4" />
                  Sair
                </Button>
              </>
            ) : (
              <>
                <Button 
                  variant="ghost" 
                  className="font-medium"
                  onClick={() => navigate('/login')}
                >
                  Entrar
                </Button>
                <Button 
                  className="bg-black text-white hover:bg-gray-800 font-medium"
                  onClick={() => navigate('/signup')}
                >
                  Começar Agora
                </Button>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden p-2 rounded-lg glass hover:bg-white/90 transition-colors"
          >
            {isMobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMobileMenuOpen && (
        <div className="lg:hidden glass border-t border-white/20">
          <div className="container-responsive">
            <nav className="py-6 space-y-4">
              {navigation.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="block px-4 py-3 text-base font-medium text-muted-foreground hover:text-foreground hover:bg-white/50 rounded-lg transition-colors"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item.name}
                </a>
              ))}
              
              <div className="pt-4 border-t border-white/20 space-y-3">
                {user ? (
                  <>
                    <Button 
                      variant="ghost" 
                      className="w-full justify-start font-medium"
                      onClick={() => {
                        navigate('/dashboard');
                        setIsMobileMenuOpen(false);
                      }}
                    >
                      <User className="h-4 w-4" />
                      Dashboard
                    </Button>
                    <Button 
                      variant="outline" 
                      className="w-full justify-start"
                      onClick={() => {
                        handleLogout();
                        setIsMobileMenuOpen(false);
                      }}
                    >
                      <LogOut className="h-4 w-4" />
                      Sair
                    </Button>
                  </>
                ) : (
                  <>
                    <Button 
                      variant="ghost" 
                      className="w-full justify-start font-medium"
                      onClick={() => {
                        navigate('/login');
                        setIsMobileMenuOpen(false);
                      }}
                    >
                      Entrar
                    </Button>
                    <Button 
                      className="w-full bg-black text-white hover:bg-gray-800 font-medium"
                      onClick={() => {
                        navigate('/signup');
                        setIsMobileMenuOpen(false);
                      }}
                    >
                      Começar Agora
                    </Button>
                  </>
                )}
              </div>
            </nav>
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;