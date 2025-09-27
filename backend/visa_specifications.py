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