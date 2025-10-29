"""
Sistema de Textos Adaptativos - 2 Níveis de Linguagem
Permite alternar entre linguagem simples e técnica em toda a aplicação
"""

# Dicionário de textos adaptativos por contexto
ADAPTIVE_TEXTS = {
    # ===== INFORMAÇÕES PESSOAIS =====
    "personal_info": {
        "simple": {
            "section_title": "Sobre Você",
            "section_description": "Vamos começar com suas informações básicas",
            "full_name": "Seu nome completo",
            "full_name_help": "Escreva seu nome exatamente como está no seu passaporte",
            "date_of_birth": "Data de nascimento",
            "date_of_birth_help": "Dia, mês e ano que você nasceu",
            "place_of_birth": "Onde você nasceu?",
            "place_of_birth_help": "Cidade e país onde você nasceu",
            "current_address": "Onde você mora agora?",
            "current_address_help": "Rua, número, cidade, estado e CEP",
            "phone": "Seu telefone",
            "phone_help": "Número com código do país (ex: +55 11 98765-4321)",
            "email": "Seu e-mail",
            "email_help": "E-mail que você usa sempre",
            "passport": "Número do passaporte",
            "passport_help": "Aquele número no seu passaporte"
        },
        "technical": {
            "section_title": "Personal Information",
            "section_description": "Provide your basic personal information",
            "full_name": "Full Legal Name",
            "full_name_help": "As it appears on your passport",
            "date_of_birth": "Date of Birth",
            "date_of_birth_help": "MM/DD/YYYY format",
            "place_of_birth": "Place of Birth",
            "place_of_birth_help": "City and country of birth",
            "current_address": "Current Residential Address",
            "current_address_help": "Street, city, state, ZIP code",
            "phone": "Phone Number",
            "phone_help": "Include country code",
            "email": "Email Address",
            "email_help": "Valid email for correspondence",
            "passport": "Passport Number",
            "passport_help": "As shown on valid passport"
        }
    },
    
    # ===== I-130 ESPECÍFICO =====
    "i130": {
        "simple": {
            "petitioner": "Quem está pedindo para você?",
            "petitioner_help": "A pessoa americana (ou residente) que está te trazendo",
            "beneficiary": "Você (quem vai receber o visto)",
            "beneficiary_help": "A pessoa que vai imigrar para os EUA",
            "relationship": "Qual a relação entre vocês?",
            "relationship_help": "Cônjuge (casado/a), filho/a, pai/mãe, irmão/ã",
            "marriage_date": "Quando vocês casaram?",
            "marriage_date_help": "Data do casamento oficial",
            "marriage_place": "Onde foi o casamento?",
            "marriage_place_help": "Cidade e país do casamento",
            "relationship_proof": "Como provar que vocês são família/casados?",
            "relationship_proof_help": "Certidão de casamento, fotos juntos, contas conjuntas",
            "us_entry": "Quando você entrou nos EUA?",
            "us_entry_help": "Se já esteve lá, quando foi?",
            "immigration_status": "Qual sua situação de imigração?",
            "immigration_status_help": "Turista? Estudante? Sem visto? Pediu asilo?"
        },
        "technical": {
            "petitioner": "Petitioner Information",
            "petitioner_help": "U.S. Citizen or LPR filing the petition",
            "beneficiary": "Beneficiary Information",
            "beneficiary_help": "Foreign national being sponsored",
            "relationship": "Relationship to Petitioner",
            "relationship_help": "Spouse, child, parent, sibling",
            "marriage_date": "Date of Marriage",
            "marriage_date_help": "Legal marriage date",
            "marriage_place": "Place of Marriage",
            "marriage_place_help": "City and country where married",
            "relationship_proof": "Evidence of Bona Fide Relationship",
            "relationship_proof_help": "Marriage certificate, joint documents, photos",
            "us_entry": "Date of Entry to U.S.",
            "us_entry_help": "If applicable, date of last entry",
            "immigration_status": "Current Immigration Status",
            "immigration_status_help": "B-2, F-1, H-1B, pending asylum, etc."
        }
    },
    
    # ===== H-1B ESPECÍFICO =====
    "h1b": {
        "simple": {
            "employer": "Nome da empresa que vai te contratar",
            "employer_help": "Nome completo da empresa americana",
            "job_title": "Seu cargo/função",
            "job_title_help": "Ex: Engenheiro, Programador, Designer",
            "job_description": "O que você vai fazer no trabalho?",
            "job_description_help": "Descreva suas tarefas principais",
            "salary": "Quanto você vai ganhar por ano?",
            "salary_help": "Salário anual em dólares (ex: $80,000)",
            "start_date": "Quando você começa?",
            "start_date_help": "Data prevista para começar a trabalhar",
            "education": "Sua formação",
            "education_help": "Faculdade que você fez, diploma que tem",
            "experience": "Experiência de trabalho",
            "experience_help": "Onde trabalhou antes e por quanto tempo"
        },
        "technical": {
            "employer": "Sponsoring Employer",
            "employer_help": "Full legal name of U.S. employer",
            "job_title": "Job Title",
            "job_title_help": "Official position title",
            "job_description": "Job Description",
            "job_description_help": "Detailed description of duties",
            "salary": "Annual Salary",
            "salary_help": "Prevailing wage or higher",
            "start_date": "Employment Start Date",
            "start_date_help": "Anticipated start date",
            "education": "Educational Qualifications",
            "education_help": "Degree, major, institution",
            "experience": "Work Experience",
            "experience_help": "Previous employment and duration"
        }
    },
    
    # ===== I-539 ESPECÍFICO =====
    "i539": {
        "simple": {
            "current_status": "Com qual visto você está agora?",
            "current_status_help": "Ex: Turista (B-2), Estudante (F-1)",
            "expiration_date": "Até quando seu visto é válido?",
            "expiration_date_help": "Data de vencimento do visto atual",
            "extension_reason": "Por que você quer ficar mais tempo?",
            "extension_reason_help": "Razão genuína (tratamento médico, família, etc)",
            "intended_departure": "Quando você planeja sair dos EUA?",
            "intended_departure_help": "Data que você pretende voltar",
            "financial_support": "Como você está se sustentando?",
            "financial_support_help": "De onde vem o dinheiro para suas despesas?",
            "ties_home_country": "O que te prende ao seu país?",
            "ties_home_country_help": "Família, casa, trabalho que te espera"
        },
        "technical": {
            "current_status": "Current Nonimmigrant Status",
            "current_status_help": "B-1, B-2, F-1, etc.",
            "expiration_date": "Current Status Expiration Date",
            "expiration_date_help": "Date shown on I-94",
            "extension_reason": "Reason for Extension",
            "extension_reason_help": "Detailed explanation",
            "intended_departure": "Intended Departure Date",
            "intended_departure_help": "Planned date of leaving U.S.",
            "financial_support": "Financial Support",
            "financial_support_help": "Source of funds during stay",
            "ties_home_country": "Ties to Home Country",
            "ties_home_country_help": "Family, property, employment"
        }
    },
    
    # ===== DOCUMENTOS =====
    "documents": {
        "simple": {
            "section_title": "Seus Documentos",
            "section_description": "Envie os documentos que você tem",
            "passport_upload": "Foto do seu passaporte",
            "passport_upload_help": "Página com sua foto e dados",
            "birth_certificate": "Certidão de nascimento",
            "birth_certificate_help": "Documento oficial de quando você nasceu",
            "marriage_certificate": "Certidão de casamento",
            "marriage_certificate_help": "Se for casado, documento do casamento",
            "photos": "Fotos",
            "photos_help": "Fotos suas, da família, do relacionamento",
            "financial_docs": "Documentos de dinheiro",
            "financial_docs_help": "Extrato do banco, recibo de salário",
            "translation_note": "📝 Documentos não em inglês precisam ser traduzidos",
            "format_note": "📎 Aceita: PDF, JPG, PNG (máx 10MB cada)"
        },
        "technical": {
            "section_title": "Supporting Documents",
            "section_description": "Upload required documentation",
            "passport_upload": "Passport Biographical Page",
            "passport_upload_help": "Valid passport photo page",
            "birth_certificate": "Birth Certificate",
            "birth_certificate_help": "Official birth record",
            "marriage_certificate": "Marriage Certificate",
            "marriage_certificate_help": "If applicable, official certificate",
            "photos": "Photographs",
            "photos_help": "Passport-style and relationship evidence",
            "financial_docs": "Financial Documentation",
            "financial_docs_help": "Bank statements, pay stubs, tax returns",
            "translation_note": "📝 Non-English documents require certified translation",
            "format_note": "📎 Accepted: PDF, JPG, PNG (max 10MB each)"
        }
    },
    
    # ===== AÇÕES/BOTÕES =====
    "actions": {
        "simple": {
            "continue": "Continuar",
            "back": "Voltar",
            "save": "Salvar",
            "save_progress": "Salvar e Continuar Depois",
            "submit": "Enviar",
            "download": "Baixar",
            "upload": "Enviar Arquivo",
            "cancel": "Cancelar",
            "confirm": "Confirmar",
            "edit": "Editar",
            "delete": "Apagar",
            "next_step": "Próximo Passo",
            "previous_step": "Passo Anterior",
            "finish": "Finalizar",
            "start": "Começar"
        },
        "technical": {
            "continue": "Continue",
            "back": "Back",
            "save": "Save",
            "save_progress": "Save Progress",
            "submit": "Submit",
            "download": "Download",
            "upload": "Upload File",
            "cancel": "Cancel",
            "confirm": "Confirm",
            "edit": "Edit",
            "delete": "Delete",
            "next_step": "Next",
            "previous_step": "Previous",
            "finish": "Complete",
            "start": "Begin"
        }
    },
    
    # ===== VALIDAÇÕES E ERROS =====
    "validation": {
        "simple": {
            "required": "Este campo é obrigatório",
            "invalid_email": "E-mail inválido",
            "invalid_phone": "Telefone inválido",
            "invalid_date": "Data inválida",
            "too_short": "Muito curto, precisa ter mais caracteres",
            "too_long": "Muito longo, reduza o tamanho",
            "numbers_only": "Só pode ter números",
            "letters_only": "Só pode ter letras",
            "file_too_large": "Arquivo muito grande (máx 10MB)",
            "invalid_format": "Formato não aceito"
        },
        "technical": {
            "required": "Required field",
            "invalid_email": "Invalid email address",
            "invalid_phone": "Invalid phone number",
            "invalid_date": "Invalid date format",
            "too_short": "Minimum length not met",
            "too_long": "Exceeds maximum length",
            "numbers_only": "Numeric characters only",
            "letters_only": "Alphabetic characters only",
            "file_too_large": "File size exceeds 10MB limit",
            "invalid_format": "Unsupported file format"
        }
    },
    
    # ===== STATUS E PROGRESSO =====
    "status": {
        "simple": {
            "not_started": "Não Começou",
            "in_progress": "Em Andamento",
            "completed": "Completo",
            "pending": "Aguardando",
            "approved": "Aprovado",
            "rejected": "Rejeitado",
            "under_review": "Em Análise",
            "draft": "Rascunho",
            "submitted": "Enviado",
            "processing": "Processando"
        },
        "technical": {
            "not_started": "Not Started",
            "in_progress": "In Progress",
            "completed": "Completed",
            "pending": "Pending",
            "approved": "Approved",
            "rejected": "Rejected",
            "under_review": "Under Review",
            "draft": "Draft",
            "submitted": "Submitted",
            "processing": "Processing"
        }
    },
    
    # ===== AVISOS E INFORMAÇÕES =====
    "alerts": {
        "simple": {
            "legal_disclaimer": "⚖️ Importante: Estas informações são educativas. Para conselhos legais específicos, consulte um advogado de imigração licenciado.",
            "save_reminder": "💾 Lembre de salvar seu progresso regularmente!",
            "required_fields": "📝 Campos com * são obrigatórios",
            "translation_required": "🌐 Documentos em outro idioma precisam ser traduzidos para inglês",
            "processing_time": "⏱️ O tempo de processamento varia. Geralmente leva vários meses.",
            "uscis_source": "📚 Baseado em requisitos públicos do USCIS (uscis.gov)",
            "data_security": "🔒 Seus dados estão seguros e criptografados",
            "progress_saved": "✅ Progresso salvo com sucesso!",
            "incomplete_warning": "⚠️ Algumas informações importantes estão faltando",
            "success": "🎉 Sucesso!"
        },
        "technical": {
            "legal_disclaimer": "⚖️ Disclaimer: This information is educational. For specific legal advice, consult a licensed immigration attorney.",
            "save_reminder": "💾 Remember to save your progress regularly",
            "required_fields": "📝 Fields marked with * are required",
            "translation_required": "🌐 Non-English documents require certified translation",
            "processing_time": "⏱️ Processing times vary. Typically several months.",
            "uscis_source": "📚 Based on public USCIS requirements (uscis.gov)",
            "data_security": "🔒 Your data is encrypted and secure",
            "progress_saved": "✅ Progress saved successfully",
            "incomplete_warning": "⚠️ Required information is incomplete",
            "success": "🎉 Success!"
        }
    }
}

# Função helper para obter texto
def get_text(context: str, key: str, mode: str = "simple") -> str:
    """
    Obtém texto adaptado baseado no contexto e modo de linguagem
    
    Args:
        context: Contexto do texto (ex: "personal_info", "i130", etc)
        key: Chave específica do texto
        mode: "simple" ou "technical"
    
    Returns:
        Texto no modo especificado ou fallback para modo simples
    """
    try:
        return ADAPTIVE_TEXTS[context][mode][key]
    except KeyError:
        # Fallback para modo simples se não encontrar
        try:
            return ADAPTIVE_TEXTS[context]["simple"][key]
        except KeyError:
            return f"[{key}]"  # Retorna a chave se não encontrar nada

# Função para obter todo um contexto
def get_context_texts(context: str, mode: str = "simple") -> dict:
    """
    Obtém todos os textos de um contexto específico
    
    Args:
        context: Contexto desejado
        mode: "simple" ou "technical"
    
    Returns:
        Dicionário com todos os textos do contexto
    """
    try:
        return ADAPTIVE_TEXTS[context][mode]
    except KeyError:
        return {}
