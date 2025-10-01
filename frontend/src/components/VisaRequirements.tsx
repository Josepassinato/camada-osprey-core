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
  Globe
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
      },
      'I-130': {
        title: 'I-130: Petição para Familiar',
        description: 'Petição para parente imediato de cidadão americano ou residente permanente',
        processingTime: '8-16 meses (dependendo da categoria)',
        uscisfee: '$535',
        eligibility: [
          'Cidadão americano ou residente permanente legal',
          'Relacionamento familiar qualificado',
          'Capacidade de patrocinar financeiramente'
        ],
        documents: [
          {
            id: 'form_i130',
            name: 'Formulário I-130',
            description: 'Petição devidamente preenchida',
            required: true,
            needsTranslation: false,
            examples: ['Formulário I-130 assinado', 'Taxa de processamento paga']
          },
          {
            id: 'citizenship_proof',
            name: 'Comprovação de Cidadania/Residência',
            description: 'Documento que comprove status legal nos EUA',
            required: true,
            needsTranslation: false,
            examples: ['Certidão de nascimento americana', 'Green Card', 'Passaporte americano']
          }
        ],
        tips: [
          'Categoria de parente determina tempo de espera',
          'Parentes imediatos não têm cota numérica',
          'Outros parentes entram em fila de espera'
        ]
      },
      'I-485': {
        title: 'I-485: Ajuste de Status',
        description: 'Solicitação para se tornar residente permanente sem sair dos EUA',
        processingTime: '8-14 meses',
        uscisfee: '$1,140 + $85 (biometria)',
        eligibility: [
          'Status legal atual nos EUA',
          'Petição I-130 ou I-140 aprovada',
          'Priority date atual (se aplicável)'
        ],
        documents: [
          {
            id: 'form_i485',
            name: 'Formulário I-485',
            description: 'Aplicação para ajuste de status',
            required: true,
            needsTranslation: false,
            examples: ['Formulário I-485 completo', 'Taxa de processamento']
          },
          {
            id: 'medical_exam',
            name: 'Exame Médico',
            description: 'Exame médico por médico autorizado pelo USCIS',
            required: true,
            needsTranslation: false,
            examples: ['Form I-693', 'Vacinas atualizadas', 'Exames laboratoriais']
          }
        ],
        tips: [
          'Permite trabalhar com EAD durante processamento',
          'Pode viajar com Advance Parole',
          'Entrevista pode ser necessária'
        ]
      },
      'I-589': {
        title: 'I-589: Solicitação de Asilo',
        description: 'Pedido de proteção por perseguição ou medo fundamentado',
        processingTime: '6 meses - 2 anos',
        uscisfee: 'Sem taxa',
        eligibility: [
          'Estar fisicamente nos EUA',
          'Aplicar dentro de 1 ano da chegada (com exceções)',
          'Demonstrar perseguição ou medo fundamentado'
        ],
        documents: [
          {
            id: 'form_i589',
            name: 'Formulário I-589',
            description: 'Solicitação de asilo e proteção contra remoção',
            required: true,
            needsTranslation: false,
            examples: ['Formulário I-589 detalhado', 'Declaração pessoal']
          },
          {
            id: 'country_evidence',
            name: 'Evidências do País',
            description: 'Documentos que comprovem condições no país de origem',
            required: true,
            needsTranslation: true,
            examples: ['Relatórios de direitos humanos', 'Artigos de jornal', 'Relatórios governamentais']
          }
        ],
        tips: [
          'Prazo de 1 ano é crucial',
          'Consistência na história é essencial',
          'Advogado especializado é recomendado'
        ]
      },
      'I-751': {
        title: 'I-751: Remoção de Condições',
        description: 'Remoção das condições do green card baseado em casamento',
        processingTime: '12-20 meses',
        uscisfee: '$595 + $85 (biometria)',
        eligibility: [
          'Green card condicional de 2 anos',
          'Ainda casado com cidadão/residente americano',
          'Casamento de boa fé (não para imigração)'
        ],
        documents: [
          {
            id: 'form_i751',
            name: 'Formulário I-751',
            description: 'Petição para remover condições da residência',
            required: true,
            needsTranslation: false,
            examples: ['Formulário I-751 conjunto', 'Taxa de processamento']
          },
          {
            id: 'marriage_evidence',
            name: 'Evidências do Casamento',
            description: 'Provas de casamento genuíno e vida conjunta',
            required: true,
            needsTranslation: false,
            examples: ['Contas conjuntas', 'Declaração de imposto conjunta', 'Fotos familiares']
          }
        ],
        tips: [
          'Aplicar 90 dias antes do vencimento do green card',
          'Casamento deve ser genuíno',
          'Entrevista pode ser necessária'
        ]
      },
      'I-765': {
        title: 'I-765: Autorização de Trabalho',
        description: 'Solicitação de documento de autorização de emprego (EAD)',
        processingTime: '3-5 meses',
        uscisfee: '$410',
        eligibility: [
          'Categoria elegível para EAD',
          'Status legal nos EUA',
          'Necessidade econômica demonstrada (alguns casos)'
        ],
        documents: [
          {
            id: 'form_i765',
            name: 'Formulário I-765',
            description: 'Aplicação para autorização de emprego',
            required: true,
            needsTranslation: false,
            examples: ['Formulário I-765 completo', 'Categoria específica marcada']
          },
          {
            id: 'supporting_docs',
            name: 'Documentos de Apoio',
            description: 'Evidências da categoria de elegibilidade',
            required: true,
            needsTranslation: false,
            examples: ['I-94', 'Aprovação I-485', 'Status de estudante F-1']
          }
        ],
        tips: [
          'Categoria determina elegibilidade',
          'EAD é específico para categoria',
          'Renovar antes do vencimento'
        ]
      },
      'I-90': {
        title: 'I-90: Renovação de Green Card',
        description: 'Substituição ou renovação do cartão de residente permanente',
        processingTime: '6-10 meses',
        uscisfee: '$455 + $85 (biometria)',
        eligibility: [
          'Residente permanente legal',
          'Green card vencido, perdido ou danificado',
          'Informações desatualizadas no cartão'
        ],
        documents: [
          {
            id: 'form_i90',
            name: 'Formulário I-90',
            description: 'Aplicação para substituir cartão de residente permanente',
            required: true,
            needsTranslation: false,
            examples: ['Formulário I-90 completo', 'Taxa de processamento']
          },
          {
            id: 'current_green_card',
            name: 'Green Card Atual',
            description: 'Cópia do cartão atual (se disponível)',
            required: false,
            needsTranslation: false,
            examples: ['Frente e verso do green card', 'Boletim de ocorrência se roubado']
          }
        ],
        tips: [
          'Renovar 6 meses antes do vencimento',
          'Receipt notice serve como extensão temporária',
          'Não afeta status de residente'
        ]
      },
      'N-400': {
        title: 'N-400: Naturalização',
        description: 'Solicitação para se tornar cidadão americano',
        processingTime: '8-14 meses',
        uscisfee: '$640 + $85 (biometria)',
        eligibility: [
          'Residente permanente por 3-5 anos',
          'Residência contínua nos EUA',
          'Conhecimento de inglês e educação cívica'
        ],
        documents: [
          {
            id: 'form_n400',
            name: 'Formulário N-400',
            description: 'Aplicação para naturalização',
            required: true,
            needsTranslation: false,
            examples: ['Formulário N-400 detalhado', 'Taxa de processamento']
          },
          {
            id: 'tax_returns',
            name: 'Declarações de Imposto',
            description: 'Últimas 3-5 declarações de imposto',
            required: true,
            needsTranslation: false,
            examples: ['Tax returns completas', 'Transcripts do IRS']
          }
        ],
        tips: [
          'Teste de inglês e educação cívica obrigatório',
          'Residência contínua é crucial',
          'Entrevista individual necessária'
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
                          <Globe className="h-3 w-3 mr-1" />
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
          Voltar à Seleção
        </Button>
        <Button 
          className="bg-black text-white hover:bg-gray-800"
          onClick={() => {
            onClose();
            // Trigger form creation through parent component
            const event = new CustomEvent('startApplication', { detail: { visaType } });
            window.dispatchEvent(event);
          }}
        >
          Começar {visaType}
        </Button>
      </div>
    </div>
  );
};

export default VisaRequirements;