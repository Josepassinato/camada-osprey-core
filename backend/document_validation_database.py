"""
Document Validation Database - Comprehensive Immigration Document Requirements
Base de dados completa para validação de documentos de imigração americana
"""

DOCUMENT_VALIDATION_DATABASE = {
    # ====================================
    # DOCUMENTOS PESSOAIS FUNDAMENTAIS
    # ====================================
    "passport": {
        "name_pt": "Passaporte",
        "name_en": "Passport",
        "description": "Documento de viagem internacional obrigatório",
        "critical_validations": {
            "document_type": "Deve ser PASSAPORTE, não RG, CNH ou outros",
            "name_match": "Nome deve corresponder exatamente ao nome do aplicante",
            "validity": "Deve ter validade mínima de 6 meses a partir da data de entrada",
            "pages": "Deve ter páginas em branco suficientes para carimbos",
            "condition": "Não pode estar danificado, rasgado ou com páginas soltas"
        },
        "required_fields": [
            "Nome completo (exatamente como no aplicante)",
            "Data de nascimento",
            "Nacionalidade",
            "Número do passaporte",
            "Data de emissão",
            "Data de validade",
            "Autoridade emissora"
        ],
        "security_elements": [
            "Capa oficial com brasão do país",
            "Papel de segurança com marca d'água",
            "Laminação ou proteção oficial",
            "Numeração sequencial",
            "Assinatura do titular"
        ],
        "common_issues": [
            "Passaporte vencido ou próximo do vencimento",
            "Nome diferente do aplicante",
            "Páginas insuficientes",
            "Danos físicos que impedem leitura"
        ],
        "required_for_visas": ["H-1B", "B-1/B-2", "F-1", "O-1", "L-1", "ALL"]
    },

    "birth_certificate": {
        "name_pt": "Certidão de Nascimento",
        "name_en": "Birth Certificate",
        "description": "Documento oficial que comprova nascimento e filiação",
        "critical_validations": {
            "authenticity": "Deve ser emitida por cartório oficial",
            "recent_issuance": "Deve ser recente (emitida nos últimos 12 meses para alguns processos)",
            "complete_info": "Deve conter informações completas dos pais",
            "name_match": "Nome deve corresponder ao do aplicante",
            "legibility": "Deve estar legível e sem rasuras"
        },
        "required_fields": [
            "Nome completo da pessoa",
            "Data de nascimento",
            "Local de nascimento (cidade, estado)",
            "Nome completo do pai",
            "Nome completo da mãe",
            "Data de emissão",
            "Cartório emissor",
            "Assinatura e carimbo oficial"
        ],
        "security_elements": [
            "Papel timbrado oficial",
            "Carimbo em relevo do cartório",
            "Assinatura do oficial",
            "Numeração oficial",
            "Código de verificação (se aplicável)"
        ],
        "common_issues": [
            "Certidão muito antiga",
            "Informações incompletas dos pais",
            "Rasuras ou correções não oficiais",
            "Cartório não reconhecido"
        ],
        "required_for_visas": ["I-485", "I-130", "N-400", "K-1"]
    },

    "marriage_certificate": {
        "name_pt": "Certidão de Casamento",
        "name_en": "Marriage Certificate", 
        "description": "Documento que comprova estado civil de casado",
        "critical_validations": {
            "authenticity": "Deve ser emitida por cartório oficial",
            "recent_issuance": "Preferivelmente recente",
            "both_names": "Deve conter nomes completos de ambos os cônjuges",
            "date_consistency": "Data do casamento deve ser consistente com outras informações",
            "legality": "Casamento deve ter sido legal no país de origem"
        },
        "required_fields": [
            "Nome completo do cônjuge masculino",
            "Nome completo do cônjuge feminino",
            "Data do casamento",
            "Local do casamento",
            "Nome das testemunhas",
            "Cartório/autoridade que celebrou",
            "Data de emissão da certidão"
        ],
        "security_elements": [
            "Papel oficial do cartório",
            "Carimbo oficial em relevo",
            "Assinaturas dos cônjuges",
            "Assinatura do oficial",
            "Numeração do registro"
        ],
        "common_issues": [
            "Casamento não reconhecido nos EUA",
            "Certidão de outro casamento anterior não dissolvido",
            "Informações inconsistentes com outros documentos"
        ],
        "required_for_visas": ["I-485", "I-130", "K-1", "K-3"]
    },

    "diploma": {
        "name_pt": "Diploma de Ensino Superior",
        "name_en": "University Diploma/Degree",
        "description": "Certificado de conclusão de curso superior",
        "critical_validations": {
            "accredited_institution": "Instituição deve ser reconhecida",
            "name_match": "Nome deve corresponder ao aplicante",
            "degree_level": "Nível de graduação deve estar claro",
            "completion_date": "Data de conclusão deve ser lógica",
            "authenticity": "Deve ser original ou cópia autenticada"
        },
        "required_fields": [
            "Nome completo do graduado",
            "Nome da instituição",
            "Título do curso/grau obtido",
            "Data de conclusão/formatura",
            "Assinatura do reitor/diretor",
            "Selo oficial da instituição"
        ],
        "security_elements": [
            "Papel oficial da instituição",
            "Selo em relevo da universidade",
            "Assinatura do reitor",
            "Numeração oficial",
            "Código de verificação (se aplicável)"
        ],
        "common_issues": [
            "Instituição não reconhecida",
            "Diploma de instituição fraudulenta",
            "Informações inconsistentes com histórico",
            "Tradução não certificada"
        ],
        "required_for_visas": ["H-1B", "F-1", "O-1", "EB-1", "EB-2"]
    },

    "transcript": {
        "name_pt": "Histórico Escolar",
        "name_en": "Academic Transcript",
        "description": "Registro detalhado das disciplinas e notas do curso",
        "critical_validations": {
            "completeness": "Deve mostrar todas as disciplinas cursadas",
            "grading_scale": "Sistema de notas deve estar claro",
            "institution_match": "Deve corresponder à mesma instituição do diploma",
            "name_consistency": "Nome deve ser consistente com diploma",
            "official_seal": "Deve ter selo oficial da instituição"
        },
        "required_fields": [
            "Nome completo do estudante",
            "Nome da instituição",
            "Período de estudos",
            "Lista de disciplinas cursadas",
            "Notas obtidas",
            "Sistema de avaliação utilizado",
            "Carga horária total",
            "Data de emissão"
        ],
        "security_elements": [
            "Papel timbrado da instituição",
            "Selo oficial em relevo",
            "Assinatura do registrar",
            "Numeração oficial"
        ],
        "common_issues": [
            "Histórico incompleto",
            "Sistema de notas não explicado",
            "Falta de informações sobre carga horária"
        ],
        "required_for_visas": ["H-1B", "F-1", "O-1", "EB-2"]
    },

    "employment_letter": {
        "name_pt": "Carta do Empregador",
        "name_en": "Employment Letter",
        "description": "Carta oficial do empregador detalhando oferta de trabalho",
        "critical_validations": {
            "official_letterhead": "Deve estar em papel timbrado oficial",
            "complete_job_details": "Deve conter detalhes completos da posição",
            "salary_information": "Deve especificar salário e benefícios",
            "authorized_signature": "Deve ser assinada por pessoa autorizada",
            "recent_date": "Deve ser datada recentemente"
        },
        "required_fields": [
            "Nome completo do funcionário",
            "Título do cargo oferecido",
            "Descrição detalhada das funções",
            "Salário anual",
            "Data de início proposta",
            "Local de trabalho",
            "Nome e título de quem assina",
            "Informações da empresa"
        ],
        "security_elements": [
            "Papel timbrado oficial",
            "Logo da empresa",
            "Assinatura manuscrita",
            "Carimbo da empresa (se aplicável)",
            "Informações de contato verificáveis"
        ],
        "common_issues": [
            "Carta genérica sem detalhes específicos",
            "Assinatura não autorizada",
            "Informações inconsistentes com outros documentos",
            "Empresa não verificável"
        ],
        "required_for_visas": ["H-1B", "L-1", "O-1", "EB-1", "EB-2"]
    },

    "financial_documents": {
        "name_pt": "Comprovantes Financeiros",
        "name_en": "Financial Documents",
        "description": "Documentos que comprovam capacidade financeira",
        "critical_validations": {
            "recent_statements": "Extratos devem ser recentes (últimos 3-6 meses)",
            "sufficient_funds": "Deve mostrar fundos suficientes para o propósito",
            "account_ownership": "Conta deve estar em nome do aplicante",
            "bank_authenticity": "Banco deve ser legítimo e verificável",
            "consistency": "Informações devem ser consistentes"
        },
        "required_fields": [
            "Nome do titular da conta",
            "Número da conta",
            "Nome do banco",
            "Saldo atual",
            "Histórico de movimentações",
            "Data dos extratos",
            "Carimbo/assinatura do banco"
        ],
        "security_elements": [
            "Papel timbrado do banco",
            "Carimbo oficial do banco",
            "Assinatura do gerente",
            "Numeração oficial",
            "Código de verificação"
        ],
        "common_issues": [
            "Saldo insuficiente",
            "Movimentações suspeitas",
            "Extratos muito antigos",
            "Banco não reconhecido"
        ],
        "required_for_visas": ["B-1/B-2", "F-1", "I-130", "I-485"]
    },

    "medical_exam": {
        "name_pt": "Exame Médico",
        "name_en": "Medical Examination",
        "description": "Exame médico realizado por médico credenciado pelo USCIS",
        "critical_validations": {
            "authorized_doctor": "Deve ser realizado por médico credenciado pelo USCIS",
            "complete_forms": "Todos os formulários devem estar preenchidos",
            "vaccination_records": "Histórico de vacinação deve estar completo",
            "recent_exam": "Exame deve ser recente (validade específica)",
            "sealed_envelope": "Deve estar em envelope lacrado (se aplicável)"
        },
        "required_fields": [
            "Nome completo do paciente",
            "Data de nascimento",
            "Resultados dos exames",
            "Histórico de vacinação",
            "Assinatura do médico",
            "Número de licença do médico",
            "Data do exame"
        ],
        "security_elements": [
            "Formulários oficiais do USCIS",
            "Assinatura do médico credenciado",
            "Carimbo profissional",
            "Envelope lacrado oficial"
        ],
        "common_issues": [
            "Médico não credenciado",
            "Exame vencido",
            "Vacinação incompleta",
            "Envelope violado"
        ],
        "required_for_visas": ["I-485", "K-1", "Immigrant Visas"]
    },

    "police_certificate": {
        "name_pt": "Certidão de Antecedentes Criminais",
        "name_en": "Police Certificate",
        "description": "Certidão que comprova ausência de antecedentes criminais",
        "critical_validations": {
            "official_authority": "Deve ser emitida por autoridade policial oficial",
            "coverage_period": "Deve cobrir período adequado de residência",
            "recent_issuance": "Deve ser recente (normalmente 6 meses)",
            "complete_coverage": "Deve cobrir todos os locais de residência",
            "authenticity": "Deve ser original ou cópia autenticada"
        },
        "required_fields": [
            "Nome completo da pessoa",
            "Data de nascimento",
            "Período coberto",
            "Resultado (sem antecedentes/com antecedentes)",
            "Autoridade emissora",
            "Data de emissão",
            "Assinatura oficial"
        ],
        "security_elements": [
            "Papel oficial da polícia",
            "Carimbo oficial",
            "Assinatura do oficial",
            "Numeração oficial",
            "Código de verificação"
        ],
        "common_issues": [
            "Certidão vencida",
            "Período de cobertura insuficiente",
            "Autoridade não reconhecida",
            "Tradução não certificada"
        ],
        "required_for_visas": ["I-485", "K-1", "Immigrant Visas"]
    },

    "i20_form": {
        "name_pt": "Formulário I-20",
        "name_en": "Form I-20",
        "description": "Certificado de Elegibilidade para Status de Estudante",
        "critical_validations": {
            "authorized_school": "Deve ser de escola autorizada pelo SEVP",
            "student_signature": "Deve estar assinado pelo estudante",
            "dso_signature": "Deve estar assinado pelo DSO da escola",
            "sevis_number": "Deve conter número SEVIS válido",
            "program_details": "Detalhes do programa devem estar corretos"
        },
        "required_fields": [
            "Informações pessoais do estudante",
            "Programa de estudos",
            "Duração do programa",
            "Custo estimado",
            "Informações da escola",
            "Número SEVIS",
            "Assinatura do estudante",
            "Assinatura do DSO"
        ],
        "security_elements": [
            "Papel oficial do USCIS",
            "Numeração SEVIS",
            "Assinatura do DSO",
            "Selo da escola"
        ],
        "common_issues": [
            "I-20 vencido",
            "Escola não autorizada",
            "Informações incorretas",
            "Falta de assinaturas"
        ],
        "required_for_visas": ["F-1"]
    }
}

# Mapeamento de documentos por tipo de visto
VISA_DOCUMENT_REQUIREMENTS = {
    "H-1B": [
        "passport", "diploma", "transcript", "employment_letter", 
        "labor_condition_application"
        # NOTE: petition_i129 is generated by AI, not uploaded by user
    ],
    "B-1/B-2": [
        "passport", "financial_documents", "invitation_letter", 
        "employment_verification", "property_documents"
    ],
    "F-1": [
        "passport", "i20_form", "financial_documents", "transcript",
        "sevis_fee_receipt", "language_proficiency"
    ],
    "O-1": [
        "passport", "diploma", "employment_letter", "recommendation_letters",
        "awards_recognition", "media_coverage"
        # NOTE: petition_i129 is generated by AI, not uploaded by user
    ],
    "L-1": [
        "passport", "employment_letter", "company_relationship_proof",
        "previous_employment_proof"
        # NOTE: petition_i129 is generated by AI, not uploaded by user
    ],
    "I-485": [
        "birth_certificate", "marriage_certificate", "passport",
        "medical_exam", "police_certificate", "financial_documents",
        "employment_letter", "tax_returns"
    ],
    "I-130": [
        "birth_certificate", "marriage_certificate", "passport",
        "petitioner_citizenship_proof", "relationship_evidence"
    ],
    "I-589": [
        "passport", "birth_certificate", "marriage_certificate", 
        "identity_documents", "persecution_evidence", "country_condition_evidence",
        "psychological_evaluation", "medical_records", "supporting_documents"
    ],
    "N-400": [
        "green_card", "tax_returns", "travel_records", 
        "marriage_certificate", "divorce_decree"
    ]
}

def get_document_validation_info(document_type: str) -> dict:
    """Get validation information for a specific document type"""
    return DOCUMENT_VALIDATION_DATABASE.get(document_type, {})

def get_required_documents_for_visa(visa_type: str) -> list:
    """Get list of required documents for a specific visa type"""
    return VISA_DOCUMENT_REQUIREMENTS.get(visa_type, [])

def validate_document_for_visa(document_type: str, visa_type: str) -> bool:
    """Check if a document is required for a specific visa"""
    required_docs = get_required_documents_for_visa(visa_type)
    return document_type in required_docs