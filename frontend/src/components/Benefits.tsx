import { Card, CardContent } from "@/components/ui/card";
import { 
  Shield, 
  Clock, 
  Users, 
  Award, 
  Headphones, 
  FileCheck,
  Zap,
  Globe,
  Lock
} from "lucide-react";

const benefits = [
  {
    icon: Shield,
    title: "Segurança Máxima",
    description: "Seus dados protegidos com criptografia bancária e compliance SOC 2",
    color: "from-blue-500/10 to-cyan-500/10",
    iconColor: "text-black"
  },
  {
    icon: Zap,
    title: "Processo Inteligente",
    description: "IA avançada acelera análises e otimiza sua aplicação automaticamente",
    color: "from-purple-500/10 to-pink-500/10", 
    iconColor: "text-black"
  },
  {
    icon: Users,
    title: "Especialistas Dedicados",
    description: "Equipe de advogados experientes acompanha cada etapa do seu caso",
    color: "from-emerald-500/10 to-teal-500/10",
    iconColor: "text-black"
  },
  {
    icon: Award,
    title: "Taxa de Sucesso 98%",
    description: "Histórico comprovado com mais de 5.000 processos aprovados",
    color: "from-amber-500/10 to-orange-500/10",
    iconColor: "text-black"
  },
  {
    icon: Headphones,
    title: "Suporte Premium 24/7",
    description: "Atendimento especializado disponível sempre que você precisar",
    color: "from-rose-500/10 to-pink-500/10",
    iconColor: "text-black"
  },
  {
    icon: FileCheck,
    title: "Garantia de Resultados",
    description: "Aprovação garantida ou reembolso de 100% do investimento",
    color: "from-green-500/10 to-emerald-500/10",
    iconColor: "text-black"
  },
  {
    icon: Clock,
    title: "Rapidez Comprovada",
    description: "Média de 30 dias para aprovação com nosso processo otimizado",
    color: "from-indigo-500/10 to-blue-500/10",
    iconColor: "text-black"
  },
  {
    icon: Globe,
    title: "Alcance Global",
    description: "Cobertura em mais de 50 países com parceiros locais especializados",
    color: "from-violet-500/10 to-purple-500/10",
    iconColor: "text-violet-600"
  },
  {
    icon: Lock,
    title: "Conformidade Total",
    description: "Aderência completa às regulamentações USCIS e práticas éticas",
    color: "from-slate-500/10 to-gray-500/10",
    iconColor: "text-slate-600"
  }
];

const Benefits = () => {
  return (
    <section className="section-padding bg-background">
      <div className="container-responsive">
        
        {/* Header */}
        <div className="text-center space-y-6 mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-primary/20">
            <Award className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">Por que OSPREY?</span>
          </div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground max-w-5xl mx-auto">
            A <span className="text-gradient">Plataforma Mais Confiável</span> para sua Imigração
          </h2>
          
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Combinamos tecnologia de ponta, expertise jurídica e atendimento humanizado 
            para garantir o sucesso da sua jornada imigratória.
          </p>
        </div>

        {/* Benefits Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {benefits.map((benefit, index) => {
            const IconComponent = benefit.icon;
            
            return (
              <Card 
                key={index} 
                className={`group card-hover glass border-0 bg-gradient-to-br ${benefit.color} relative overflow-hidden`}
              >
                <CardContent className="p-8 text-center space-y-6">
                  
                  {/* Icon */}
                  <div className="relative mx-auto">
                    <div className="w-20 h-20 bg-white/80 rounded-2xl flex items-center justify-center shadow-soft group-hover:shadow-glow group-hover:scale-110 transition-all duration-300">
                      <IconComponent className={`h-10 w-10 ${benefit.iconColor}`} />
                    </div>
                    
                    {/* Glow effect */}
                    <div className={`absolute inset-0 w-20 h-20 bg-gradient-to-r ${benefit.color} rounded-2xl blur-xl opacity-0 group-hover:opacity-50 transition-opacity duration-300 -z-10`}></div>
                  </div>
                  
                  {/* Content */}
                  <div className="space-y-3">
                    <h3 className="text-xl font-bold text-foreground group-hover:text-primary transition-colors">
                      {benefit.title}
                    </h3>
                    
                    <p className="text-muted-foreground leading-relaxed">
                      {benefit.description}
                    </p>
                  </div>
                </CardContent>

                {/* Hover border effect */}
                <div className="absolute inset-0 rounded-lg border-2 border-transparent group-hover:border-primary/20 transition-colors duration-300 pointer-events-none"></div>
              </Card>
            );
          })}
        </div>

        {/* Trust indicators */}
        <div className="mt-20 text-center">
          <div className="inline-flex items-center gap-12 p-8 glass rounded-2xl border border-primary/10">
            <div className="text-center">
              <div className="text-3xl font-bold text-gradient mb-1">5.000+</div>
              <div className="text-sm text-muted-foreground">Clientes Aprovados</div>
            </div>
            <div className="w-px h-12 bg-border"></div>
            <div className="text-center">
              <div className="text-3xl font-bold text-gradient mb-1">98%</div>
              <div className="text-sm text-muted-foreground">Taxa de Sucesso</div>
            </div>
            <div className="w-px h-12 bg-border"></div>
            <div className="text-center">
              <div className="text-3xl font-bold text-gradient mb-1">30</div>
              <div className="text-sm text-muted-foreground">Dias Médios</div>
            </div>
            <div className="w-px h-12 bg-border"></div>
            <div className="text-center">
              <div className="text-3xl font-bold text-gradient mb-1">24/7</div>
              <div className="text-sm text-muted-foreground">Suporte Premium</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Benefits;