import { Button } from "@/components/ui/button";
import { ArrowRight, CheckCircle, Sparkles, Shield, Clock } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className="relative min-h-screen flex items-center bg-gradient-subtle overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0">
        <div className="absolute top-20 right-20 w-72 h-72 bg-black/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 left-20 w-96 h-96 bg-gray-600/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="container-responsive relative z-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          
          {/* Content */}
          <div className="space-y-8">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-primary/20">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-primary">Plataforma Líder em Imigração</span>
            </div>

            {/* Main heading */}
            <div className="space-y-6">
              <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold leading-tight">
                <span className="text-foreground">Simplifique sua</span>
                <br />
                <span className="text-gradient">Jornada Imigratória</span>
              </h1>
              
              <p className="text-xl md:text-2xl text-muted-foreground leading-relaxed max-w-2xl">
                Plataforma completa com IA para auto aplicação de processos imigratórios. 
                <span className="text-foreground font-medium"> Rápido, seguro e 100% digital.</span>
              </p>
            </div>

            {/* Trust indicators */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="flex items-center gap-3 p-4 rounded-xl glass-dark hover:bg-white/90 transition-colors">
                <div className="flex-shrink-0 w-12 h-12 bg-success/10 rounded-lg flex items-center justify-center">
                  <CheckCircle className="h-6 w-6 text-success" />
                </div>
                <div>
                  <div className="text-sm font-medium text-foreground">100% Digital</div>
                  <div className="text-xs text-muted-foreground">Processo completo online</div>
                </div>
              </div>

              <div className="flex items-center gap-3 p-4 rounded-xl glass-dark hover:bg-white/90 transition-colors">
                <div className="flex-shrink-0 w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <div className="text-sm font-medium text-foreground">98% Aprovação</div>
                  <div className="text-xs text-muted-foreground">Taxa de sucesso comprovada</div>
                </div>
              </div>

              <div className="flex items-center gap-3 p-4 rounded-xl glass-dark hover:bg-white/90 transition-colors">
                <div className="flex-shrink-0 w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                  <Clock className="h-6 w-6 text-accent" />
                </div>
                <div>
                  <div className="text-sm font-medium text-foreground">30 Dias</div>
                  <div className="text-xs text-muted-foreground">Tempo médio de aprovação</div>
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Button 
                size="xl" 
                className="btn-gradient text-lg font-medium group"
                onClick={() => navigate('/signup')}
              >
                Iniciar Aplicação Agora
                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              
              <Button 
                variant="outline" 
                size="xl" 
                className="text-lg font-medium btn-glass hover:border-primary/30"
              >
                Ver Como Funciona
              </Button>
            </div>

            {/* Social proof */}
            <div className="flex items-center gap-8 pt-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-foreground">5.000+</div>
                <div className="text-sm text-muted-foreground">Aprovações</div>
              </div>
              <div className="w-px h-12 bg-border"></div>
              <div className="text-center">
                <div className="text-2xl font-bold text-foreground">98%</div>
                <div className="text-sm text-muted-foreground">Taxa de Sucesso</div>
              </div>
              <div className="w-px h-12 bg-border"></div>
              <div className="text-center">
                <div className="text-2xl font-bold text-foreground">24/7</div>
                <div className="text-sm text-muted-foreground">Suporte Expert</div>
              </div>
            </div>
          </div>

          {/* Visual */}
          <div className="relative">
            <div className="relative z-10">
              {/* Main visual card */}
              <div className="relative glass border border-white/20 rounded-3xl p-8 card-hover">
                <div className="aspect-[4/3] bg-gradient-primary rounded-2xl relative overflow-hidden">
                  {/* Simulated dashboard/document interface */}
                  <div className="absolute inset-4 bg-white/95 rounded-xl p-6 space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 bg-success rounded-full"></div>
                      <div className="text-sm font-medium text-zinc-700">Status: Em Processamento</div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="h-2 bg-zinc-200 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-primary rounded-full w-3/4"></div>
                      </div>
                      <div className="text-xs text-zinc-500">75% completo - Análise de documentos</div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 bg-zinc-50 rounded-lg">
                        <div className="text-xs text-zinc-500">Prazo Estimado</div>
                        <div className="text-sm font-medium text-zinc-700">30 dias</div>
                      </div>
                      <div className="p-3 bg-zinc-50 rounded-lg">
                        <div className="text-xs text-zinc-500">Próximo Passo</div>
                        <div className="text-sm font-medium text-zinc-700">Entrevista</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Floating indicators */}
                <div className="absolute -top-4 -right-4 glass border border-success/20 rounded-full p-3">
                  <CheckCircle className="h-6 w-6 text-success" />
                </div>
                
                <div className="absolute -bottom-4 -left-4 glass border border-primary/20 rounded-full p-3">
                  <Sparkles className="h-6 w-6 text-primary animate-pulse" />
                </div>
              </div>
            </div>

            {/* Background decoration */}
            <div className="absolute -top-6 -right-6 w-full h-full bg-gradient-primary/20 rounded-3xl -z-10 blur-sm"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;