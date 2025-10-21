import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Languages, 
  DollarSign, 
  Clock, 
  Star, 
  MapPin,
  Phone,
  Mail,
  CheckCircle,
  ExternalLink,
  Award,
  Shield
} from "lucide-react";

interface TranslationPartner {
  id: string;
  name: string;
  description: string;
  rating: number;
  reviews: number;
  priceRange: string;
  estimatedDays: string;
  specialties: string[];
  location: string;
  contact: {
    phone?: string;
    email?: string;
    website?: string;
  };
  certified: boolean;
  uscisAccepted: boolean;
  features: string[];
}

interface TranslationPartnersProps {
  documentType: string;
  documentName: string;
  onSelectPartner: (partner: TranslationPartner) => void;
  onSkip: () => void;
}

const TranslationPartners = ({
  documentType,
  documentName,
  onSelectPartner,
  onSkip
}: TranslationPartnersProps) => {
  const [selectedPartner, setSelectedPartner] = useState<string>("");

  // Lista de parceiros para tradução juramentada
  const partners: TranslationPartner[] = [
    {
      id: "tradutec_sp",
      name: "TradutTec São Paulo",
      description: "Especializada em documentos de imigração para EUA com mais de 15 anos de experiência",
      rating: 4.9,
      reviews: 847,
      priceRange: "R$ 45-80 por página",
      estimatedDays: "2-3 dias úteis",
      specialties: ["Documentos Acadêmicos", "Certidões", "Contratos de Trabalho", "Diplomas"],
      location: "São Paulo, SP",
      contact: {
        phone: "(11) 3255-8900",
        email: "uscis@tradutec.com.br",
        website: "www.tradutec.com.br"
      },
      certified: true,
      uscisAccepted: true,
      features: [
        "Certificação USCIS garantida",
        "Entrega expressa disponível", 
        "Revisão gratuita em 30 dias",
        "Apostilamento incluído"
      ]
    },
    {
      id: "juramentada_rj",
      name: "Tradução Juramentada RJ",
      description: "Tradutora pública certificada especialista em vistos americanos",
      rating: 4.8,
      reviews: 523,
      priceRange: "R$ 55-90 por página",
      estimatedDays: "1-2 dias úteis",
      specialties: ["Vistos H1-B", "Vistos L1", "Documentos Corporativos", "Históricos Escolares"],
      location: "Rio de Janeiro, RJ",
      contact: {
        phone: "(21) 2547-3300",
        email: "contato@juramendarj.com",
        website: "www.traducaojuramendarj.com"
      },
      certified: true,
      uscisAccepted: true,
      features: [
        "Especialista em H1-B e L1",
        "Atendimento 24/7",
        "Entrega digital incluída",
        "Consultoria gratuita"
      ]
    },
    {
      id: "translate_pro",
      name: "TranslatePro Nacional",
      description: "Rede nacional de tradutores juramentados com atendimento online",
      rating: 4.7,
      reviews: 1205,
      priceRange: "R$ 40-75 por página",
      estimatedDays: "3-5 dias úteis",
      specialties: ["Documentos Pessoais", "Acadêmicos", "Profissionais", "Médicos"],
      location: "Atendimento Nacional",
      contact: {
        phone: "0800-555-7890",
        email: "uscis@translatepro.com.br",
        website: "www.translatepro.com.br"
      },
      certified: true,
      uscisAccepted: true,
      features: [
        "Atendimento nacional",
        "Preços competitivos",
        "Plataforma digital completa",
        "Garantia de qualidade"
      ]
    }
  ];

  const handleSelectPartner = (partner: TranslationPartner) => {
    setSelectedPartner(partner.id);
    onSelectPartner(partner);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <Languages className="h-8 w-8 text-orange-600" />
          <div>
            <h2 className="text-2xl font-bold text-black">Tradução Juramentada Necessária</h2>
            <p className="text-gray-600">Parceiros certificados para traduzir seu documento</p>
          </div>
        </div>
        
        <Alert className="border-orange-400 bg-orange-50">
          <Shield className="h-4 w-4 text-orange-600" />
          <AlertDescription>
            <p className="font-medium text-orange-800 mb-2">📄 Documento identificado: {documentName}</p>
            <p className="text-orange-700 text-sm">
              Nosso sistema detectou que este documento precisa de tradução juramentada para ser aceito pelo USCIS. 
              Selecione um de nossos parceiros certificados para realizar a tradução oficial.
            </p>
          </AlertDescription>
        </Alert>
      </div>

      {/* Partners Grid */}
      <div className="grid md:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
        {partners.map((partner) => (
          <Card 
            key={partner.id}
            className={`border-2 cursor-pointer transition-all hover:shadow-lg ${
              selectedPartner === partner.id 
                ? 'border-orange-500 bg-orange-50' 
                : 'border-gray-200 hover:border-orange-300'
            }`}
            onClick={() => setSelectedPartner(partner.id)}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg">{partner.name}</CardTitle>
                  <p className="text-sm text-gray-600 mt-1">{partner.description}</p>
                </div>
                <div className="flex flex-col items-end space-y-1">
                  {partner.certified && (
                    <Badge className="bg-green-100 text-green-800 border-green-300">
                      <Award className="h-3 w-3 mr-1" />
                      Certificado
                    </Badge>
                  )}
                  {partner.uscisAccepted && (
                    <Badge className="bg-blue-100 text-blue-800 border-blue-300">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      USCIS
                    </Badge>
                  )}
                </div>
              </div>
            </CardHeader>

            <CardContent>
              {/* Rating */}
              <div className="flex items-center space-x-2 mb-4">
                <div className="flex items-center space-x-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      className={`h-4 w-4 ${
                        star <= partner.rating 
                          ? 'text-orange-400 fill-current' 
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-sm font-medium">{partner.rating}</span>
                <span className="text-sm text-gray-600">({partner.reviews} avaliações)</span>
              </div>

              {/* Pricing and Time */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="flex items-center space-x-2">
                  <DollarSign className="h-4 w-4 text-green-600" />
                  <div>
                    <p className="text-xs text-gray-600">Preço</p>
                    <p className="font-medium text-sm">{partner.priceRange}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-blue-600" />
                  <div>
                    <p className="text-xs text-gray-600">Prazo</p>
                    <p className="font-medium text-sm">{partner.estimatedDays}</p>
                  </div>
                </div>
              </div>

              {/* Location */}
              <div className="flex items-center space-x-2 mb-4">
                <MapPin className="h-4 w-4 text-gray-600" />
                <span className="text-sm text-gray-700">{partner.location}</span>
              </div>

              {/* Specialties */}
              <div className="mb-4">
                <p className="text-xs text-gray-600 mb-2">Especialidades:</p>
                <div className="flex flex-wrap gap-1">
                  {partner.specialties.slice(0, 2).map((specialty) => (
                    <Badge key={specialty} variant="outline" className="text-xs">
                      {specialty}
                    </Badge>
                  ))}
                  {partner.specialties.length > 2 && (
                    <Badge variant="outline" className="text-xs">
                      +{partner.specialties.length - 2} mais
                    </Badge>
                  )}
                </div>
              </div>

              {/* Features */}
              <div className="mb-4">
                <p className="text-xs text-gray-600 mb-2">Diferenciais:</p>
                <ul className="text-xs text-gray-700 space-y-1">
                  {partner.features.slice(0, 2).map((feature, index) => (
                    <li key={index} className="flex items-center space-x-1">
                      <CheckCircle className="h-3 w-3 text-green-600 flex-shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Contact */}
              <div className="border-t border-gray-200 pt-3">
                <div className="flex items-center space-x-4 text-xs">
                  {partner.contact.phone && (
                    <div className="flex items-center space-x-1">
                      <Phone className="h-3 w-3 text-gray-600" />
                      <span>{partner.contact.phone}</span>
                    </div>
                  )}
                  {partner.contact.website && (
                    <div className="flex items-center space-x-1">
                      <ExternalLink className="h-3 w-3 text-gray-600" />
                      <span>Website</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Select Button */}
              <Button
                onClick={(e) => {
                  e.stopPropagation();
                  handleSelectPartner(partner);
                }}
                className={`w-full mt-4 ${
                  selectedPartner === partner.id
                    ? 'bg-orange-600 text-white hover:bg-orange-700'
                    : 'bg-white text-black border border-black hover:bg-gray-50'
                }`}
              >
                {selectedPartner === partner.id ? 'Selecionado' : 'Selecionar Parceiro'}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between items-center">
        <Button 
          variant="outline" 
          onClick={onSkip}
          className="border-gray-400 text-gray-700"
        >
          Pular por Agora
        </Button>

        <div className="flex space-x-4">
          <Button
            onClick={() => {
              // Open contact with selected partner
              if (selectedPartner) {
                const partner = partners.find(p => p.id === selectedPartner);
                if (partner?.contact.website) {
                  window.open(`https://${partner.contact.website}`, '_blank');
                }
              }
            }}
            disabled={!selectedPartner}
            variant="outline"
            className="border-black text-black"
          >
            Contatar Parceiro
          </Button>

          <Button
            onClick={() => {
              if (selectedPartner) {
                const partner = partners.find(p => p.id === selectedPartner);
                if (partner) {
                  handleSelectPartner(partner);
                }
              }
            }}
            disabled={!selectedPartner}
            className="bg-orange-600 text-white hover:bg-orange-700"
          >
            Continuar com Tradução
          </Button>
        </div>
      </div>

      {/* Additional Info */}
      <Alert className="mt-6 border-blue-200 bg-blue-50">
        <CheckCircle className="h-4 w-4 text-blue-600" />
        <AlertDescription>
          <p className="font-medium text-blue-800 mb-2">ℹ️ Como funciona:</p>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>1. Selecione um parceiro certificado</li>
            <li>2. Entre em contato e envie seu documento</li>
            <li>3. Receba a tradução juramentada certificada</li>
            <li>4. Faça upload do documento traduzido na plataforma</li>
            <li>5. Nosso sistema validará e integrará à sua aplicação</li>
          </ul>
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default TranslationPartners;