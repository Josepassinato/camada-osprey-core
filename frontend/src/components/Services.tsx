import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Plane, 
  GraduationCap, 
  Heart, 
  Briefcase, 
  Users, 
  ArrowRight, 
  TrendingUp,
  Star
} from "lucide-react";

const services = [
  {
    icon: Briefcase,
    title: "Visto de Trabalho",
    description: "Processo completo para obtenção de visto de trabalho nos EUA com suporte especializado.",
    types: ["H1-B", "L1", "O1", "EB-5"],
    popular: true,
    color: "blue",
    features: ["Análise de Elegibilidade", "Preparação de Documentos", "Acompanhamento USCIS"]
  },
  {
    icon: GraduationCap,
    title: "Visto de Estudante",
    description: "Suporte completo para aplicações acadêmicas e programas de intercâmbio.",
    types: ["F1", "M1", "J1", "F2"],
    popular: false,
    color: "purple",
    features: ["Escolha de Instituição", "I-20 Processing", "Entrevista Consular"]
  },
  {
    icon: Heart,
    title: "Reunificação Familiar",
    description: "Processos especializados em imigração baseada em laços familiares.",
    types: ["CR1", "IR1", "K1", "F2A"],
    popular: false,
    color: "pink",
    features: ["Petição Familiar", "Documentos Comprobatórios", "Timeline Otimizado"]
  },
  {
    icon: Users,
    title: "Residência Permanente",
    description: "Caminhos estratégicos para obtenção de Green Card e cidadania americana.",
    types: ["Green Card", "EB-1", "EB-2", "EB-3"],
    popular: true,
    color: "green",
    features: ["Estratégia Personalizada", "Priority Date", "Adjustment of Status"]
  },
  {
    icon: Plane,
    title: "Visto de Turismo",
    description: "Aplicações rápidas para turismo, negócios e visitas de curta duração.",
    types: ["B1/B2", "ESTA", "VWP"],
    popular: false,
    color: "orange",
    features: ["DS-160 Otimizado", "Prep. Entrevista", "Aprovação Expressa"]
  },
  {
    icon: TrendingUp,
    title: "Visto de Investidor",
    description: "Soluções completas para empreendedores e investidores qualificados.",
    types: ["E2", "EB-5", "L1A"],
    popular: false,
    color: "emerald",
    features: ["Business Plan", "Documentação Financeira", "Due Diligence"]
  }
];

const colorSchemes = {
  blue: "from-blue-500/20 to-cyan-500/20 border-blue-200/30",
  purple: "from-purple-500/20 to-pink-500/20 border-purple-200/30",
  pink: "from-pink-500/20 to-rose-500/20 border-pink-200/30",
  green: "from-green-500/20 to-emerald-500/20 border-green-200/30",
  orange: "from-orange-500/20 to-yellow-500/20 border-orange-200/30",
  emerald: "from-emerald-500/20 to-teal-500/20 border-emerald-200/30",
};

const Services = () => {
  return (
    <section id="services" className="section-padding bg-gradient-subtle">
      <div className="container-responsive">
        
        {/* Header */}
        <div className="text-center space-y-4 mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border border-primary/20 mb-4">
            <Star className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">Nossos Serviços</span>
          </div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground max-w-4xl mx-auto">
            <span className="text-gradient">Soluções Completas</span> para Cada Jornada
          </h2>
          
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Oferecemos suporte especializado para todos os tipos de processos imigratórios,
            com tecnologia avançada e expertise jurídica.
          </p>
        </div>

        {/* Services Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((service, index) => {
            const IconComponent = service.icon;
            const colorClass = colorSchemes[service.color as keyof typeof colorSchemes];
            
            return (
              <Card 
                key={index} 
                className={`relative card-hover glass border-0 bg-gradient-to-br ${colorClass} overflow-hidden group`}
              >
                {/* Popular badge */}
                {service.popular && (
                  <div className="absolute -top-2 -right-2 z-10">
                    <Badge className="bg-gradient-primary text-primary-foreground font-medium border-0 shadow-glow">
                      ⭐ Popular
                    </Badge>
                  </div>
                )}

                <CardHeader className="pb-4 relative">
                  {/* Icon */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="relative">
                      <div className="w-14 h-14 bg-white/80 rounded-2xl flex items-center justify-center shadow-soft group-hover:shadow-glow transition-all duration-300">
                        <IconComponent className="h-7 w-7 text-primary" />
                      </div>
                    </div>
                  </div>
                  
                  <CardTitle className="text-xl font-bold text-foreground">
                    {service.title}
                  </CardTitle>
                </CardHeader>

                <CardContent className="space-y-6">
                  <p className="text-muted-foreground leading-relaxed">
                    {service.description}
                  </p>
                  
                  {/* Visa types */}
                  <div className="flex flex-wrap gap-2">
                    {service.types.map((type, typeIndex) => (
                      <Badge 
                        key={typeIndex} 
                        variant="secondary" 
                        className="bg-white/50 text-foreground border-0 font-medium"
                      >
                        {type}
                      </Badge>
                    ))}
                  </div>

                  {/* Features */}
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-foreground">Incluído:</div>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      {service.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-center gap-2">
                          <div className="w-1.5 h-1.5 bg-primary rounded-full flex-shrink-0"></div>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* CTA Button */}
                  <Button 
                    variant="ghost" 
                    className="w-full justify-between group bg-white/50 hover:bg-white/80 border-0 font-medium"
                  >
                    Saiba Mais
                    <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <Button size="lg" className="btn-gradient text-lg font-medium">
            Ver Todos os Serviços
            <ArrowRight className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </section>
  );
};

export default Services;