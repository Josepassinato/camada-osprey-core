import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  FileText, 
  Clock, 
  DollarSign, 
  AlertTriangle, 
  CheckCircle,
  Info,
  Star,
  Users,
  Calendar,
  Building,
  GraduationCap,
  Passport
} from "lucide-react";

interface VisaRequirement {
  id: string;
  name: string;
  description: string;
  required: boolean;
  needsTranslation?: boolean;
  examples: string[];
}

interface VisaRequirementsProps {
  visaType: string;
  onClose: () => void;
}

const VisaRequirements = ({ visaType, onClose }: VisaRequirementsProps) => {
  const getVisaDetails = (type: string) => {
    const requirements: Record<string, any> = {
      'H-1B': {
        title: 'H-1B: Trabalhador Especializado',
        description: 'Para profissionais com ensino superior em ocupação especializada',
        processingTime: '2-4 meses (regular) ou 15 dias (premium)',
        uscisfee: '$555 + $1,500 (anti-fraud) + $4,000 (empregador)',
        eligibility: [
          'Diploma de ensino superior ou equivalente',
          'Oferta de trabalho em ocupação especializada',
          'Empregador americano patrocinador',
          'Qualificações específicas para a função'
        ],
        documents: [
          {
            id: 'passport',
            name: 'Passaporte Válido',
            description: 'Passaporte com pelo menos 6 meses de validade',
            required: true,
            needsTranslation: false,
            examples: ['Passaporte brasileiro válido', 'Páginas com informações pessoais']
          },
          {
            id: 'diploma',
            name: 'Diploma e Histórico Escolar',
            description: 'Comprovação de ensino superior',
            required: true,
            needsTranslation: true,
            examples: ['Diploma universitário', 'Histórico escolar completo', 'Certificados de pós-graduação']
          },
          {
            id: 'job_offer',
            name: 'Carta de Oferta de Emprego',
            description: 'Oferta formal do empregador americano',
            required: true,
            needsTranslation: false,
            examples: ['Labor Condition Application (LCA)', 'Carta detalhada da função', 'Contrato de trabalho']
          },
          {
            id: 'resume',
            name: 'Currículo Profissional',
            description: 'Experiência profissional detalhada',
            required: true,
            needsTranslation: false,
            examples: ['CV em inglês', 'LinkedIn atualizado', 'Portfólio profissional']
          },
          {
            id: 'work_experience',
            name: 'Cartas de Experiência Profissional',
            description: 'Comprovação de experiência na área',
            required: true,
            needsTranslation: true,
            examples: ['Cartas de recomendação', 'Certificados de trabalho', 'Contratos anteriores']
          }
        ],
        tips: [
          'Processo deve ser iniciado pelo empregador americano',
          'Período de aplicação (cap season): Abril de cada ano',
          'Visto válido por até 3 anos, renovável',
          'Permite dependentes (H-4) para cônjuge e filhos'
        ]
      },
      'L-1': {
        title: 'L-1: Transferência Intracompanhia',
        description: 'Para executivos, gerentes ou especialistas transferidos',
        processingTime: '2-4 meses',
        uscisfee: '$555 + $4,500 (L-1A) ou $1,440 (L-1B)',
        eligibility: [
          '1 ano trabalhando na empresa no exterior',
          'Função executiva, gerencial ou especializada',
          'Empresa americana relacionada à estrangeira',
          'Transferência para posição similar ou superior'
        ],
        documents: [
          {
            id: 'passport',
            name: 'Passaporte Válido',
            description: 'Passaporte com pelo menos 6 meses de validade',
            required: true,
            needsTranslation: false,
            examples: ['Passaporte brasileiro válido']
          },
          {
            id: 'employment_letter',
            name: 'Carta de Emprego Atual',
            description: 'Comprovação de trabalho na empresa no exterior',
            required: true,
            needsTranslation: true,
            examples: ['Carta da empresa brasileira', 'Contrato de trabalho', 'Declaração de funções']
          },
          {
            id: 'company_relationship',
            name: 'Documentos da Relação entre Empresas',
            description: 'Comprovação da relação corporativa',
            required: true,
            needsTranslation: true,
            examples: ['Contrato social', 'Documentos de incorporação', 'Organograma corporativo']
          },
          {
            id: 'job_description',
            name: 'Descrição Detalhada da Função',
            description: 'Função atual e futura nos EUA',
            required: true,
            needsTranslation: false,
            examples: ['Job description detalhada', 'Organograma', 'Responsabilidades específicas']
          }
        ],
        tips: [
          'L-1A (executivos/gerentes): até 7 anos',
          'L-1B (conhecimento especializado): até 5 anos',
          'Permite green card durante o visto',
          'Cônjuge pode trabalhar (L-2 EAD)'
        ]
      },
      'O-1': {
        title: 'O-1: Habilidade Extraordinária',
        description: 'Para indivíduos com habilidades extraordinárias',
        processingTime: '2-4 meses',
        uscisfee: '$555 + $1,440',
        eligibility: [
          'Habilidade extraordinária em ciências, artes, educação, negócios ou atletismo',
          'Reconhecimento nacional ou internacional',
          'Evidências substanciais de conquistas',
          'Continuação do trabalho na área de expertise'
        ],
        documents: [
          {
            id: 'passport',
            name: 'Passaporte Válido',
            description: 'Passaporte com validade mínima de 6 meses',
            required: true,
            needsTranslation: false,
            examples: ['Passaporte brasileiro válido']
          },
          {
            id: 'awards',
            name: 'Prêmios e Reconhecimentos',
            description: 'Evidências de excelência na área',
            required: true,
            needsTranslation: true,
            examples: ['Certificados de prêmios', 'Medalhas', 'Reconhecimentos oficiais']
          },
          {
            id: 'media_coverage',
            name: 'Cobertura da Mídia',
            description: 'Publicações sobre seu trabalho',
            required: true,
            needsTranslation: true,
            examples: ['Artigos de jornal', 'Entrevistas', 'Reportagens']
          },
          {
            id: 'peer_review',
            name: 'Participação como Avaliador',
            description: 'Evidências de julgar trabalhos de outros',
            required: false,
            needsTranslation: true,
            examples: ['Convites para revisar artigos', 'Participação em júris', 'Comitês de avaliação']
          }
        ],
        tips: [
          'Exige evidências substanciais de reconhecimento',
          'Válido por até 3 anos',
          'Renovável indefinidamente',
          'Pode levar ao green card EB-1A'
        ]
      },
      'B-1/B-2': {
        title: 'B-1/B-2: Visto de Negócios e Turismo',
        description: 'Para negócios, turismo, visitas familiares, tratamento médico ou eventos sociais',
        processingTime: '2-4 semanas (consulado) ou alguns dias (ESTA)',
        uscisfee: '$120 (consulado) ou $21 (ESTA)',
        eligibility: [
          'B-1: Reuniões de negócios, conferências, consultas, treinamentos',
          'B-2: Turismo, visitas familiares, tratamento médico, eventos sociais',
          'Propósito temporário (máximo 6 meses por entrada)',
          'Intenção clara de retornar ao Brasil',
          'Vínculos fortes com país de origem (emprego, família, propriedades)',
          'Recursos financeiros suficientes para custear toda a viagem'
        ],
        documents: [
          {
            id: 'passport',
            name: 'Passaporte Válido',
            description: 'Passaporte com pelo menos 6 meses de validade',
            required: true,
            needsTranslation: false,
            examples: ['Passaporte brasileiro válido', 'Páginas com informações pessoais']
          },
          {
            id: 'financial_proof',
            name: 'Comprovantes Financeiros',
            description: 'Evidência de recursos para custear a viagem',
            required: true,
            needsTranslation: true,
            examples: ['Extratos bancários (3 meses)', 'Declaração de Imposto de Renda', 'Carta do empregador com salário']
          },
          {
            id: 'employment_letter',
            name: 'Carta do Empregador',
            description: 'Comprovação de vínculo empregatício no Brasil',
            required: true,
            needsTranslation: true,
            examples: ['Carta em papel timbrado', 'Contrato de trabalho', 'Declaração de férias aprovadas']
          },
          {
            id: 'travel_itinerary',
            name: 'Itinerário da Viagem',
            description: 'Planos detalhados da viagem nos EUA',
            required: true,
            needsTranslation: false,
            examples: ['Reservas de hotel', 'Passagens aéreas', 'Roteiro turístico detalhado']
          },
          {
            id: 'business_documents',
            name: 'Documentos de Negócios (B-1)',
            description: 'Para viagens de negócios - se aplicável',
            required: false,
            needsTranslation: true,
            examples: ['Carta da empresa americana convidando', 'Agenda de reuniões/conferências', 'Contrato ou acordo comercial']
          },
          {
            id: 'invitation_letter',
            name: 'Carta Convite (se aplicável)',
            description: 'Se visitando familiares ou amigos nos EUA',
            required: false,
            needsTranslation: false,
            examples: ['Carta de familiar americano', 'Cópia do green card do anfitrião', 'Comprovante de residência do anfitrião']
          },
          {
            id: 'property_docs',
            name: 'Documentos de Propriedades',
            description: 'Comprovação de vínculos com o Brasil',
            required: false,
            needsTranslation: true,
            examples: ['Escritura de imóvel', 'IPTU', 'Financiamento imobiliário']
          },
          {
            id: 'family_ties',
            name: 'Vínculos Familiares no Brasil',
            description: 'Evidência de família e responsabilidades no Brasil',
            required: true,
            needsTranslation: true,
            examples: ['Certidão de casamento', 'Certidão de nascimento dos filhos', 'Atestado escolar dos filhos']
          }
        ],
        tips: [
          'B-1: Para negócios (reuniões, conferências) - NÃO permite trabalho remunerado',
          'B-2: Para turismo, visitas familiares, tratamento médico',
          'Demonstre vínculos fortes com o Brasil (emprego, família, propriedades)',
          'Tenha recursos financeiros comprovados para toda a viagem',
          'Seja honesto sobre o propósito da viagem na entrevista',
          'ESTA disponível para brasileiros (válido por 2 anos) - mais rápido',
          'Visto B-1/B-2 pode ser válido por até 10 anos (múltiplas entradas)',
          'Permanência máxima: 6 meses por entrada (decisão do oficial na imigração)',
          'Taxa de $120 aplicável para brasileiros (acordo de reciprocidade)'
        ]
      },
      'F-1': {
        title: 'F-1: Visto de Estudante',
        description: 'Para estudos acadêmicos em instituições americanas',
        processingTime: '2-6 semanas',
        uscisfee: '$185 + $350 (SEVIS)',
        eligibility: [
          'Aceito em instituição educacional aprovada pelo SEVP',
          'Cursando programa acadêmico ou de idiomas',
          'Recursos financeiros para custear estudos',
          'Intenção de retornar ao país de origem após estudos'
        ],
        documents: [
          {
            id: 'passport',
            name: 'Passaporte Válido',
            description: 'Passaporte com validade além do período de estudos',
            required: true,
            needsTranslation: false,
            examples: ['Passaporte brasileiro válido']
          },
          {
            id: 'i20_form',
            name: 'Formulário I-20',
            description: 'Emitido pela instituição de ensino americana',
            required: true,
            needsTranslation: false,
            examples: ['I-20 original assinado', 'Cópia para records']
          },
          {
            id: 'financial_support',
            name: 'Comprovante de Recursos Financeiros',
            description: 'Evidência de capacidade para custear estudos',
            required: true,
            needsTranslation: true,
            examples: ['Extratos bancários', 'Carta de patrocínio', 'Bolsa de estudos']
          },
          {
            id: 'academic_records',
            name: 'Histórico Acadêmico',
            description: 'Comprovação de estudos anteriores',
            required: true,
            needsTranslation: true,
            examples: ['Histórico escolar', 'Diploma universitário', 'Certificados de cursos']
          },
          {
            id: 'english_proficiency',
            name: 'Comprovação de Inglês',
            description: 'Teste de proficiência em inglês (se exigido)',
            required: false,
            needsTranslation: false,
            examples: ['TOEFL', 'IELTS', 'Duolingo English Test']
          }
        ],
        tips: [
          'Pague a taxa SEVIS antes da entrevista',
          'Demonstre vínculos com o Brasil para retorno',
          'Tenha recursos financeiros para todo o período de estudos',
          'Pode trabalhar no campus após 9 meses de estudos',
          'Válido durante todo o programa + 60 dias de grace period'
        ]
      }
    };

    return requirements[type] || null;
  };

  const visaDetails = getVisaDetails(visaType);

  if (!visaDetails) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-black">{visaDetails.title}</h2>
          <p className="text-gray-600 mt-1">{visaDetails.description}</p>
        </div>
      </div>

      {/* Key Info Cards */}
      <div className="grid md:grid-cols-3 gap-4">
        <Card className="border-black">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-black" />
              <div>
                <p className="font-medium text-black">Tempo de Processamento</p>
                <p className="text-sm text-gray-600">{visaDetails.processingTime}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-black">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <DollarSign className="h-5 w-5 text-black" />
              <div>
                <p className="font-medium text-black">Taxas USCIS</p>
                <p className="text-sm text-gray-600">{visaDetails.uscisfee}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-black">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-black" />
              <div>
                <p className="font-medium text-black">Dependentes</p>
                <p className="text-sm text-gray-600">Cônjuge e filhos permitidos</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Eligibility Requirements */}
      <Card className="border-black">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CheckCircle className="h-5 w-5" />
            <span>Critérios de Elegibilidade</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {visaDetails.eligibility.map((criterion: string, index: number) => (
              <div key={index} className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-gray-700">{criterion}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Required Documents */}
      <Card className="border-black">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5" />
            <span>Documentos Necessários</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {visaDetails.documents.map((doc: VisaRequirement) => (
              <div key={doc.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium text-black">{doc.name}</h4>
                      {doc.required && <Badge variant="destructive" className="text-xs">Obrigatório</Badge>}
                      {doc.needsTranslation && (
                        <Badge variant="outline" className="text-xs border-orange-400 text-orange-700">
                          <Passport className="h-3 w-3 mr-1" />
                          Tradução Juramentada
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{doc.description}</p>
                    
                    <div className="mt-2">
                      <p className="text-xs font-medium text-gray-800 mb-1">Exemplos aceitos:</p>
                      <ul className="text-xs text-gray-600 space-y-1">
                        {doc.examples.map((example, idx) => (
                          <li key={idx} className="flex items-center space-x-1">
                            <span>•</span>
                            <span>{example}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Important Tips */}
      <Alert className="border-blue-200 bg-blue-50">
        <Info className="h-4 w-4" />
        <AlertDescription>
          <div>
            <p className="font-medium text-blue-800 mb-2">Dicas Importantes:</p>
            <ul className="text-sm text-blue-700 space-y-1">
              {visaDetails.tips.map((tip: string, index: number) => (
                <li key={index} className="flex items-start space-x-2">
                  <Star className="h-3 w-3 mt-0.5 flex-shrink-0" />
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        </AlertDescription>
      </Alert>

      {/* Translation Alert */}
      <Alert className="border-orange-200 bg-orange-50">
        <AlertTriangle className="h-4 w-4 text-orange-600" />
        <AlertDescription>
          <div>
            <p className="font-medium text-orange-800 mb-2">⚠️ Tradução Juramentada Necessária</p>
            <p className="text-sm text-orange-700">
              Documentos marcados com <Badge variant="outline" className="mx-1 text-xs border-orange-400 text-orange-700">Tradução Juramentada</Badge> 
              devem ser traduzidos por tradutor certificado. Nossa IA identificará automaticamente quando seus documentos 
              precisarem de tradução e oferecerá parceiros qualificados.
            </p>
          </div>
        </AlertDescription>
      </Alert>

      {/* Action Button */}
      <div className="flex justify-end space-x-4 pt-4">
        <Button variant="outline" onClick={onClose} className="border-black text-black">
          Escolher Outro Visto
        </Button>
        <Button className="bg-black text-white hover:bg-gray-800">
          Começar H1-B
        </Button>
      </div>
    </div>
  );
};

export default VisaRequirements;