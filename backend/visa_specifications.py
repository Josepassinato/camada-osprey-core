# Especificações detalhadas para cada visto USCIS
# Dados baseados em regulamentações oficiais do USCIS

VISA_SPECIFICATIONS = {
    "I-130": {
        "title": "Petição de Parente Estrangeiro",
        "category": "Família",
        "description": "Para cidadãos e residentes permanentes peticionarem familiares elegíveis",
        "uscis_fee": "$535",
        "processing_time": "8-33 meses",
        
        "required_documents": [
            "Certidão de nascimento do peticionário",
            "Prova de cidadania americana ou Green Card",
            "Certidão de nascimento do beneficiário",
            "Certidão de casamento (se aplicável)",
            "Certidão de divórcio/óbito (casamentos anteriores)",
            "Fotos tipo passaporte (2 para cada pessoa)",
            "Cópia do passaporte do beneficiário"
        ],
        
        "evidence_required": {
            "spouse": [
                "Certidão de casamento",
                "Evidência de relacionamento genuíno (fotos, correspondências)",
                "Declarações conjuntas de imposto",
                "Contas bancárias conjuntas",
                "Contratos de aluguel/hipoteca conjuntos"
            ],
            "child": [
                "Certidão de nascimento mostrando parentesco",
                "Certidão de adoção (se aplicável)",
                "Prova de custódia legal (se aplicável)"
            ],
            "parent": [
                "Certidão de nascimento do peticionário mostrando parentesco",
                "Prova de que peticionário tem 21+ anos"
            ],
            "sibling": [
                "Certidões de nascimento de ambos mostrando mesmos pais",
                "Prova de que peticionário tem 21+ anos"
            ]
        },
        
        "key_questions": [
            "Qual é sua relação com o beneficiário?",
            "Você é cidadão americano ou residente permanente?",
            "Quando você se tornou cidadão/residente permanente?",
            "O beneficiário já esteve nos EUA?",
            "Você já peticionou outros parentes antes?",
            "Você tem renda suficiente para ser patrocinador?",
            "Há algum impedimento criminal ou de imigração?"
        ],
        
        "common_issues": [
            "Falta de evidência suficiente de relacionamento genuíno",
            "Documentos não traduzidos adequadamente",
            "Renda insuficiente do peticionário",
            "Histórico de imigração complexo do beneficiário"
        ]
    },
    
    "N-400": {
        "title": "Pedido de Naturalização",
        "category": "Cidadania", 
        "description": "Para residentes permanentes elegíveis se tornarem cidadãos americanos",
        "uscis_fee": "$725",
        "processing_time": "8-14 meses",
        
        "required_documents": [
            "Cópia do Green Card (frente e verso)",
            "Fotos tipo passaporte (2 fotos)",
            "Cópia de todas as páginas do passaporte",
            "Declarações de imposto dos últimos 5 anos",
            "Certificados de casamento/divórcio",
            "Registros militares (se aplicável)",
            "Certidões criminais (se aplicável)"
        ],
        
        "evidence_required": {
            "residence": [
                "Histórico completo de endereços dos últimos 5 anos",
                "Contas de utilidades, extratos bancários",
                "Contratos de aluguel ou escrituras",
                "Registros de emprego"
            ],
            "travel": [
                "Lista completa de todas as viagens fora dos EUA",
                "Carimbos de entrada/saída no passaporte",
                "Documentos de viagens prolongadas (6+ meses)"
            ],
            "good_moral_character": [
                "Registros criminais (se houver)",
                "Certidões de antecedentes criminais",
                "Evidência de reabilitação (se aplicável)",
                "Cartas de referência de caráter"
            ]
        },
        
        "key_questions": [
            "Há quanto tempo você é residente permanente?",
            "Você esteve fisicamente presente nos EUA pelo tempo requerido?",
            "Você fez viagens longas fora dos EUA?",
            "Você tem algum registro criminal?",
            "Você pagou todos os impostos exigidos?",
            "Você consegue falar, ler e escrever inglês básico?",
            "Você está disposto a fazer o juramento de lealdade?"
        ],
        
        "common_issues": [
            "Tempo insuficiente de presença física nos EUA",
            "Viagens prolongadas que quebram continuidade de residência",
            "Problemas com histórico de impostos",
            "Registros criminais não divulgados",
            "Falta de proficiência em inglês"
        ]
    },
    
    "I-765": {
        "title": "Autorização de Trabalho",
        "category": "Trabalho",
        "description": "Para solicitar permissão de trabalho nos Estados Unidos",
        "uscis_fee": "$410", 
        "processing_time": "3-5 meses",
        
        "required_documents": [
            "Fotos tipo passaporte (2 fotos)",
            "Cópia da certidão de nascimento",
            "Cópia do passaporte e visto",
            "Evidência de elegibilidade para categoria específica",
            "I-94 (registro de entrada/saída)",
            "Documentos do status imigratório atual"
        ],
        
        "evidence_required": {
            "student_f1": [
                "I-20 válido da escola",
                "Carta da escola confirmando necessidade econômica",
                "Evidência de dificuldades financeiras",
                "Histórico acadêmico satisfatório"
            ],
            "asylum_applicant": [
                "Recibo do pedido de asilo (I-589)",
                "Evidência de que aplicação foi protocolada há 150+ dias",
                "Nenhuma decisão final negativa"
            ],
            "asylee": [
                "Decisão de concessão de asilo",
                "I-94 mostrando status de asilado"
            ],
            "spouse_of_e1_e2": [
                "Evidência do status E-1/E-2 do cônjuge",
                "Certidão de casamento",
                "I-94 do cônjuge principal"
            ]
        },
        
        "key_questions": [
            "Qual é sua categoria de elegibilidade?",
            "Qual é seu status imigratório atual?",
            "Você já trabalhou nos EUA antes?",
            "Você já teve autorização de trabalho anterior?",
            "Há quanto tempo você está no seu status atual?",
            "Sua situação mudou desde a última autorização?"
        ],
        
        "common_issues": [
            "Categoria de elegibilidade incorreta",
            "Status imigratório expirado",
            "Documentos de suporte inadequados",
            "Timing inadequado da aplicação"
        ]
    },
    
    "I-485": {
        "title": "Ajuste de Status",
        "category": "Green Card",
        "description": "Para ajustar status para residente permanente estando nos EUA", 
        "uscis_fee": "$1,225",
        "processing_time": "8-24 meses",
        
        "required_documents": [
            "Certidão de nascimento",
            "Fotos tipo passaporte (2 fotos)",
            "Cópia do passaporte e vistos",
            "I-94 (histórico de entradas/saídas)",
            "Exame médico (I-693)",
            "Declarações de imposto (3-5 anos)",
            "Certidões criminais (se aplicável)"
        ],
        
        "evidence_required": {
            "family_based": [
                "Petição I-130 aprovada",
                "Evidência de relacionamento familiar",
                "Affidavit of Support (I-864)",
                "Evidência de renda do patrocinador"
            ],
            "employment_based": [
                "Petição I-140 aprovada", 
                "Labor Certification aprovada (se aplicável)",
                "Carta do empregador atual",
                "Evidência de qualificações"
            ],
            "asylum_based": [
                "Decisão de concessão de asilo",
                "Evidência de 1+ ano como asilado nos EUA"
            ]
        },
        
        "key_questions": [
            "Qual é a base para seu ajuste de status?",
            "Você entrou legalmente nos EUA?",
            "Você manteve status legal desde a entrada?",
            "Você tem algum registro criminal?",
            "Você já foi deportado ou removido?",
            "Você completou o exame médico?",
            "Há uma petição aprovada para você?"
        ],
        
        "common_issues": [
            "Entrada ilegal nos EUA",
            "Violação de status imigratório",
            "Registros criminais inadmissíveis",
            "Exame médico incompleto ou expirado",
            "Problemas com prioridade de data"
        ]
    },
    
    "I-90": {
        "title": "Renovação de Green Card",
        "category": "Green Card",
        "description": "Para renovar ou substituir cartão de residente permanente",
        "uscis_fee": "$540",
        "processing_time": "6-10 meses",
        
        "required_documents": [
            "Cópia do Green Card atual (frente e verso)",
            "Fotos tipo passaporte (2 fotos)",
            "Cópia de documento de identidade com foto",
            "Evidência de mudança legal de nome (se aplicável)",
            "Relatório policial (se cartão foi roubado)"
        ],
        
        "evidence_required": {
            "renewal": [
                "Green Card expirando em 6 meses",
                "Evidência de residência contínua nos EUA"
            ],
            "replacement": [
                "Evidência de que cartão foi perdido/roubado/danificado",
                "Relatório policial (se roubado)",
                "Declaração juramentada sobre a perda"
            ],
            "name_change": [
                "Ordem judicial de mudança de nome",
                "Certidão de casamento/divórcio",
                "Documentos legais da mudança"
            ]
        },
        
        "key_questions": [
            "Por que você está aplicando para um novo Green Card?",
            "Quando seu cartão atual expira?",
            "Você mudou de nome desde o último cartão?",
            "Você manteve residência contínua nos EUA?",
            "Você fez viagens prolongadas fora dos EUA?",
            "Você tem algum registro criminal recente?"
        ],
        
        "common_issues": [
            "Aplicação muito cedo (mais de 6 meses antes da expiração)",
            "Evidência insuficiente de residência contínua",
            "Viagens prolongadas não explicadas",
            "Mudança de nome não documentada adequadamente"
        ]
    },
    
    "I-751": {
        "title": "Remoção de Condições",
        "category": "Green Card", 
        "description": "Para remover condições do status de residente permanente",
        "uscis_fee": "$595",
        "processing_time": "12-18 meses",
        
        "required_documents": [
            "Cópia do Green Card condicional",
            "Fotos tipo passaporte (2 fotos)",
            "Certidão de casamento",
            "Declarações de imposto conjuntas",
            "Evidência de vida conjugal genuína",
            "Certidões de nascimento dos filhos (se aplicável)"
        ],
        
        "evidence_required": {
            "joint_filing": [
                "Declarações de imposto conjuntas",
                "Contas bancárias conjuntas", 
                "Propriedades em nome conjunto",
                "Seguros com beneficiário mútuo",
                "Fotos e viagens juntos",
                "Declarações de amigos e família",
                "Correspondências dirigidas a ambos"
            ],
            "divorce_waiver": [
                "Decreto final de divórcio",
                "Evidência de que casamento foi genuíno",
                "Evidência de abuso (se aplicável)"
            ],
            "abuse_waiver": [
                "Relatórios policiais",
                "Ordens de proteção",
                "Relatórios médicos",
                "Declarações de testemunhas",
                "Evidência psicológica"
            ]
        },
        
        "key_questions": [
            "Você ainda está casado com o peticionário original?",
            "O casamento foi genuíno desde o início?",
            "Você tem evidência de vida conjugal contínua?",
            "Houve algum período de separação?",
            "Você tem filhos juntos?",
            "Você arquivou impostos conjuntamente?",
            "Há alguma evidência de fraude no casamento?"
        ],
        
        "common_issues": [
            "Evidência insuficiente de casamento genuíno",
            "Períodos de separação não explicados", 
            "Aplicação fora do prazo (90 dias antes da expiração)",
            "Inconsistências em declarações anteriores"
        ]
    },
    
    "I-589": {
        "title": "Pedido de Asilo",
        "category": "Asilo",
        "description": "Para pessoas que buscam proteção nos EUA devido à perseguição",
        "uscis_fee": "$0",
        "processing_time": "2-5 anos",
        
        "required_documents": [
            "Formulário I-589 preenchido",
            "Evidência de identidade (passaporte, certidão de nascimento)",
            "Declaração pessoal detalhada sobre perseguição",
            "Evidências de perseguição ou ameaças",
            "Documentos do país de origem",
            "Relatórios sobre condições do país",
            "Fotos tipo passaporte (2 fotos)"
        ],
        
        "evidence_required": {
            "persecution_evidence": [
                "Relatórios médicos de ferimentos",
                "Relatórios policiais",
                "Ordens de prisão ou mandados",
                "Ameaças escritas ou gravadas",
                "Fotos de ferimentos ou danos à propriedade",
                "Declarações de testemunhas",
                "Artigos de jornal sobre perseguição"
            ],
            "country_conditions": [
                "Relatórios do Departamento de Estado dos EUA",
                "Relatórios de organizações de direitos humanos",
                "Artigos acadêmicos sobre condições do país",
                "Notícias sobre perseguição a grupos similares"
            ],
            "identity_documents": [
                "Passaporte ou documento de identidade nacional",
                "Certidão de nascimento",
                "Documentos de casamento/família",
                "Carteira de trabalho ou documentos profissionais"
            ],
            "expert_testimony": [
                "Relatórios de especialistas em país de origem",
                "Avaliação psicológica de trauma",
                "Relatório médico sobre tortura",
                "Tradução certificada de documentos"
            ]
        },
        
        "key_questions": [
            "Quando você chegou aos Estados Unidos?",
            "Você aplicou para asilo dentro de 1 ano da chegada?",
            "Por que você não pode retornar ao seu país de origem?",
            "Qual foi a natureza da perseguição que você sofreu?",
            "A perseguição foi baseada em raça, religião, nacionalidade, política ou grupo social?",
            "O governo do seu país estava envolvido na perseguição?",
            "Você procurou proteção das autoridades locais?",
            "Você já aplicou para asilo em outro país?",
            "Você cometeu algum crime grave?",
            "Você tem familiares que também precisam de proteção?"
        ],
        
        "protected_grounds": [
            "Raça ou etnia",
            "Religião ou crenças religiosas", 
            "Nacionalidade",
            "Opinião política",
            "Pertencimento a grupo social particular (LGBTI+, mulheres, etc.)"
        ],
        
        "common_issues": [
            "Aplicação após o prazo de 1 ano (sem circunstâncias excepcionais)",
            "Falta de evidência credível de perseguição",
            "Inconsistências no testemunho",
            "Perseguição por motivos criminais (não elegível)",
            "Proteção interna disponível no país de origem",
            "Crimes graves cometidos pelo aplicante"
        ]
    },
    
    "O-1": {
        "title": "Visto de Habilidade Extraordinária",
        "category": "Trabalho Especializado",
        "description": "Para indivíduos com habilidades extraordinárias em ciências, artes, educação, negócios ou atletismo",
        "uscis_fee": "$460",
        "processing_time": "2-4 meses",
        
        "required_documents": [
            "Formulário I-129 (Petição de Trabalhador Não-Imigrante)",
            "Suplemento O (Classificação O)",
            "Contrato ou resumo dos termos do emprego",
            "Itinerário detalhado das atividades nos EUA",
            "Carta de consulta de organização apropriada",
            "Evidência de habilidade extraordinária",
            "Cópia do passaporte",
            "Taxa de petição I-129"
        ],
        
        "evidence_required": {
            "extraordinary_ability_arts": [
                "Liderança ou papel crítico em organizações distinguidas",
                "Reconhecimento nacional ou internacional por conquistas",
                "Registro de sucesso comercial ou crítico maior",
                "Reconhecimento significativo de organizações, críticos, etc.",
                "Salário alto ou remuneração comparado a outros na área",
                "Participação em painéis como juiz do trabalho de outros",
                "Contribuições artísticas originais de significância major"
            ],
            "extraordinary_ability_sciences": [
                "Prêmios nacionais ou internacionais de excelência",
                "Membro de associações que exigem conquistas excepcionais",
                "Material publicado sobre o indivíduo em publicações profissionais",
                "Participação como juiz do trabalho de outros na área",
                "Contribuições científicas originais de significância major",
                "Autoria de artigos acadêmicos em publicações profissionais",
                "Emprego em posição crítica para organizações distinguidas",
                "Salário alto comparado a outros na área"
            ],
            "business_achievements": [
                "Prêmios de excelência nacional ou internacional",
                "Membro de associações profissionais de elite",
                "Publicações sobre conquistas em mídia profissional",
                "Liderança em organizações distinguidas",
                "Salário excepcionalmente alto",
                "Participação como juiz/avaliador de outros profissionais"
            ]
        },
        
        "key_questions": [
            "Em que área você tem habilidade extraordinária?",
            "Quais prêmios ou reconhecimentos você recebeu?",
            "Você é membro de organizações profissionais prestigiosas?",
            "Suas conquistas foram publicadas na mídia?",
            "Você já foi juiz do trabalho de outros profissionais?",
            "Qual é sua contribuição original para sua área?",
            "Seu salário está no topo da sua área?",
            "Você teve papel crítico em organizações distinguidas?",
            "Qual será sua atividade específica nos EUA?",
            "Quem será seu empregador ou peticionário nos EUA?"
        ],
        
        "consultation_organizations": {
            "arts": "Organização sindical apropriada (SAG-AFTRA, etc.)",
            "sciences": "Associação profissional na área específica", 
            "business": "Associação empresarial relevante",
            "athletics": "Organização atlética apropriada",
            "education": "Associação educacional relevante"
        },
        
        "common_issues": [
            "Evidência insuficiente de habilidade extraordinária",
            "Falta de carta de consulta de organização apropriada",
            "Itinerário vago ou incompleto das atividades",
            "Comparação inadequada com pares na área",
            "Documentação de conquistas inadequadamente traduzida",
            "Falta de evidência de reconhecimento nacional/internacional"
        ]
    },
    
    "H-1B": {
        "title": "Visto de Trabalho Especializado",
        "category": "Trabalho",
        "description": "Para profissionais especializados em ocupações que requerem aplicação teórica e prática de conhecimentos especializados",
        "uscis_fee": "$460 + taxas adicionais",
        "processing_time": "3-8 meses",
        
        "required_documents": [
            "Formulário I-129 (Petição de Trabalhador Não-Imigrante)",
            "Suplemento H (Classificação H)",
            "Labor Condition Application (LCA) certificada",
            "Carta de oferta de emprego",
            "Evidência de qualificações educacionais",
            "Evidência de experiência profissional",
            "Cópia do diploma universitário",
            "Histórico acadêmico oficial",
            "Avaliação de credenciais (se necessário)"
        ],
        
        "evidence_required": {
            "specialty_occupation": [
                "Descrição detalhada das funções do cargo",
                "Evidência de que a posição requer diploma de bacharel",
                "Evidência de complexidade e singularidade das funções",
                "Grau de supervisão e julgamento independente requerido"
            ],
            "employer_qualifications": [
                "Prova de que o empregador é uma entidade válida",
                "Evidência de capacidade financeira para pagar salário",
                "Histórico de conformidade com leis trabalhistas",
                "Organograma mostrando onde a posição se encaixa"
            ],
            "educational_requirements": [
                "Diploma de bacharel ou superior em área relacionada",
                "Histórico acadêmico oficial (transcript)",
                "Avaliação de credenciais por organização credenciada",
                "Tradução certificada de documentos estrangeiros"
            ],
            "experience_alternative": [
                "3 anos de experiência = 1 ano de educação universitária",
                "Cartas de empregadores anteriores detalhando experiência",
                "Certificados profissionais relevantes",
                "Evidência de treinamento especializado"
            ]
        },
        
        "key_questions": [
            "Qual é sua área de especialização?",
            "Você tem diploma de bacharel ou superior?",
            "Em que área é seu diploma?",
            "Sua área de estudo está relacionada ao trabalho oferecido?",
            "Quantos anos de experiência profissional você tem?",
            "Qual será seu salário nos EUA?",
            "O salário atende ao salário prevalente da área?",
            "A empresa tem capacidade de pagar o salário proposto?",
            "As funções do cargo requerem conhecimento especializado?",
            "Você já trabalhou nos EUA antes em visto H-1B?"
        ],
        
        "specialty_occupation_criteria": [
            "Diploma de bacharel ou superior é normalmente o requisito mínimo",
            "Grau de complexidade da posição é tão especializado que está associado com diploma",
            "Empregador normalmente requer diploma para a posição",
            "Natureza das funções é tão especializada e complexa que requer conhecimento de bacharel"
        ],
        
        "common_issues": [
            "LCA não certificada ou com problemas",
            "Diploma não relacionado à área da posição",
            "Salário abaixo do salário prevalente",
            "Posição não qualifica como specialty occupation",
            "Avaliação de credenciais inadequada",
            "Experiência insuficiente para compensar falta de educação",
            "Capacidade financeira do empregador questionável",
            "Descrição vaga das funções do trabalho"
        ]
    }
}

def get_visa_specifications(form_code: str):
    """Retorna especificações detalhadas para um formulário específico"""
    return VISA_SPECIFICATIONS.get(form_code, {})

def get_required_documents(form_code: str, subcategory: str = None):
    """Retorna lista de documentos necessários para um formulário específico"""
    specs = get_visa_specifications(form_code)
    if not specs:
        return []
    
    documents = specs.get("required_documents", [])
    
    if subcategory and "evidence_required" in specs:
        evidence = specs["evidence_required"].get(subcategory, [])
        documents.extend(evidence)
    
    return documents

def get_key_questions(form_code: str):
    """Retorna perguntas-chave para um formulário específico"""
    specs = get_visa_specifications(form_code)
    return specs.get("key_questions", [])

def get_common_issues(form_code: str):
    """Retorna problemas comuns para um formulário específico"""
    specs = get_visa_specifications(form_code)
    return specs.get("common_issues", [])