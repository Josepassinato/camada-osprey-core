import { Button } from "@/components/ui/button";
import { ArrowRight, CheckCircle, Sparkles, MessageSquare } from "lucide-react";
import { useNavigate } from "react-router-dom";

const CTA = () => {
  const navigate = useNavigate();

  return (
    <section className="section-padding bg-gradient-subtle relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-black/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-accent/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="container-responsive relative">
        <div className="max-w-5xl mx-auto">
          
          {/* Main CTA Card */}
          <div className="glass border border-black/20 rounded-3xl p-8 md:p-12 lg:p-16 text-center space-y-8 card-hover relative overflow-hidden">
            
            {/* Background pattern */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5 rounded-3xl"></div>
            
            {/* Content */}
            <div className="relative space-y-6">
              
              {/* Badge */}
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-black/30">
                <Sparkles className="h-4 w-4 text-black animate-pulse" />
                <span className="text-sm font-medium text-black">Comece sua Jornada Agora</span>
              </div>

              {/* Main heading */}
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground max-w-4xl mx-auto">
                Pronto para 
                <span className="text-gradient"> Transformar</span> 
                <br className="hidden sm:block" />
                seu Futuro?
              </h2>

              {/* Description */}
              <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto">
                Junte-se a milhares de pessoas que já realizaram o sonho americano 
                através da nossa plataforma. <span className="text-foreground font-medium">Começar é gratuito!</span>
              </p>

              {/* Key benefits */}
              <div className="grid sm:grid-cols-3 gap-6 max-w-2xl mx-auto">
                <div className="flex items-center gap-3 text-left sm:justify-center">
                  <CheckCircle className="h-5 w-5 text-success flex-shrink-0" />
                  <span className="text-sm font-medium text-foreground">Análise gratuita</span>
                </div>
                <div className="flex items-center gap-3 text-left sm:justify-center">
                  <CheckCircle className="h-5 w-5 text-success flex-shrink-0" />
                  <span className="text-sm font-medium text-foreground">Sem compromisso</span>
                </div>
                <div className="flex items-center gap-3 text-left sm:justify-center">
                  <CheckCircle className="h-5 w-5 text-success flex-shrink-0" />
                  <span className="text-sm font-medium text-foreground">Resultados em 24h</span>
                </div>
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center max-w-lg mx-auto">
                <Button 
                  size="xl" 
                  className="bg-black text-white hover:bg-gray-800 text-lg font-medium group flex-1"
                  onClick={() => navigate('/signup')}
                >
                  Iniciar Processo Gratuito
                  <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
                
                <Button 
                  variant="outline" 
                  size="xl" 
                  className="text-lg font-medium btn-glass hover:border-black/30 flex-1"
                  onClick={() => navigate('/chat')}
                >
                  <MessageSquare className="h-5 w-5" />
                  Falar com Especialista IA
                </Button>
              </div>

              {/* Trust indicators */}
              <div className="flex items-center justify-center gap-8 text-sm text-muted-foreground pt-6">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                  <span>Sem taxas ocultas</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-black rounded-full animate-pulse delay-300"></div>
                  <span>Suporte premium incluído</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-accent rounded-full animate-pulse delay-700"></div>
                  <span>Garantia de satisfação</span>
                </div>
              </div>
            </div>

            {/* Floating elements */}
            <div className="absolute -top-6 -left-6 glass border border-success/20 rounded-2xl p-4 rotate-12">
              <CheckCircle className="h-8 w-8 text-success" />
            </div>
            
            <div className="absolute -bottom-6 -right-6 glass border border-black/20 rounded-2xl p-4 -rotate-12">
              <Sparkles className="h-8 w-8 text-black animate-pulse" />
            </div>
          </div>

          {/* Bottom testimonial */}
          <div className="mt-16 text-center">
            <div className="inline-flex items-center gap-4 p-6 glass rounded-2xl border border-black/10 max-w-2xl">
              <div className="flex -space-x-2">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="w-10 h-10 bg-gradient-primary rounded-full border-2 border-white flex items-center justify-center text-white text-sm font-medium">
                    {i === 1 ? "M" : i === 2 ? "A" : i === 3 ? "J" : "S"}
                  </div>
                ))}
              </div>
              
              <div className="text-left">
                <div className="flex items-center gap-1 mb-1">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="w-4 h-4 text-black">⭐</div>
                  ))}
                </div>
                <p className="text-sm text-muted-foreground">
                  <span className="font-medium text-foreground">"Processo incrível!"</span> - 
                  Mais de 5.000 clientes aprovados
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTA;