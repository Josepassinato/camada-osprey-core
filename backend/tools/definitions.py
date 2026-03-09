"""
Tool definitions for Osprey Chief of Staff — Gemini Function Calling.
14 tools: 7 read + 7 write operations against MongoDB.
"""


TOOL_DECLARATIONS = [
    # =========================================================================
    # READ TOOLS (7)
    # =========================================================================
    {
        "name": "get_firm_overview",
        "description": (
            "Get a complete overview of the firm: total cases, breakdown by visa type, "
            "breakdown by status, upcoming deadlines in the next 7 days, cases at risk "
            "(idle 14+ days or missing documents). Use when the attorney asks for a "
            "summary, 'what's happening today', 'overview', or 'status geral'."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "list_cases",
        "description": (
            "List cases for the firm, optionally filtered by status or visa type. "
            "Returns case_id, client_name, visa_type, status, and next deadline. "
            "Use when attorney asks 'quantos casos', 'list cases', 'casos ativos'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Filter by status: intake, docs_pending, docs_review, forms_gen, attorney_review, ready_to_file, filed, rfe_received, rfe_response, approved, denied, withdrawn",
                },
                "visa_type": {
                    "type": "string",
                    "description": "Filter by visa type, e.g. H-1B, EB-2 NIW, O-1A, I-485, I-130, F-1",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results to return (default 20, max 50)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_case",
        "description": (
            "Get full details of a specific case by case_id or client name. "
            "Returns all fields including documents list, deadlines, notes, and history. "
            "Use when attorney mentions a specific client or case."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "string",
                    "description": "The case ID (e.g. CASE-A1B2C3D4)",
                },
                "client_name": {
                    "type": "string",
                    "description": "Client name to search for (partial match, case-insensitive)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "search_cases",
        "description": (
            "Search cases by keyword across client name, notes, and visa type. "
            "Use for broad searches when client name is ambiguous or partial."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword to match against client_name, notes, visa_type",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_deadlines",
        "description": (
            "Get all upcoming deadlines across all cases, sorted by urgency. "
            "Use when attorney asks about deadlines, 'prazos', 'what's due', etc."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "days_ahead": {
                    "type": "integer",
                    "description": "How many days ahead to look (default 14, max 90)",
                },
                "include_overdue": {
                    "type": "boolean",
                    "description": "Include past-due deadlines (default true)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_case_documents",
        "description": (
            "List all documents attached to a case, including which ones are received "
            "and which are still missing based on visa type requirements. "
            "Use when attorney asks about document status for a case."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "string",
                    "description": "The case ID",
                },
                "client_name": {
                    "type": "string",
                    "description": "Client name (if case_id unknown)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_case_stats",
        "description": (
            "Get aggregate statistics: total cases, active, by visa type, by status, "
            "critical deadlines, pending review count. "
            "Use for quick numbers: 'how many', 'quantos', dashboard stats."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    # =========================================================================
    # WRITE TOOLS (7)
    # =========================================================================
    {
        "name": "create_case",
        "description": (
            "Create a new immigration case. Use when attorney says 'novo caso', "
            "'open case', 'abrir caso', or provides new client details."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "client_name": {
                    "type": "string",
                    "description": "Full name of the client/beneficiary",
                },
                "visa_type": {
                    "type": "string",
                    "description": "Visa category: H-1B, EB-1A, EB-2 NIW, O-1A, I-130, I-485, F-1, B-2, etc.",
                },
                "notes": {
                    "type": "string",
                    "description": "Initial case notes or context",
                },
            },
            "required": ["client_name", "visa_type"],
        },
    },
    {
        "name": "update_case",
        "description": (
            "Update a case's status, notes, client name, or visa type. "
            "Use when attorney says 'aprovado', 'denied', 'update status', "
            "'muda para', 'teve RFE', etc. ALWAYS confirm before executing."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "string",
                    "description": "The case ID to update",
                },
                "client_name_search": {
                    "type": "string",
                    "description": "Client name to find the case (if case_id unknown)",
                },
                "status": {
                    "type": "string",
                    "description": "New status: intake, docs_pending, docs_review, forms_gen, attorney_review, ready_to_file, filed, rfe_received, rfe_response, approved, denied, withdrawn",
                },
                "notes": {
                    "type": "string",
                    "description": "Updated notes (appended to existing)",
                },
                "visa_type": {
                    "type": "string",
                    "description": "Updated visa type",
                },
            },
            "required": [],
        },
    },
    {
        "name": "add_deadline",
        "description": (
            "Add a deadline to a case. Use when attorney says 'prazo', 'deadline', "
            "'filing date', 'empurra o prazo para', 'set deadline'. "
            "ALWAYS confirm the date before executing."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "string",
                    "description": "The case ID",
                },
                "client_name_search": {
                    "type": "string",
                    "description": "Client name to find the case",
                },
                "title": {
                    "type": "string",
                    "description": "Deadline title (e.g. 'Filing deadline', 'RFE response due', 'Premium Processing deadline')",
                },
                "due_date": {
                    "type": "string",
                    "description": "Due date in ISO format YYYY-MM-DD",
                },
                "notes": {
                    "type": "string",
                    "description": "Additional notes about this deadline",
                },
            },
            "required": ["title", "due_date"],
        },
    },
    {
        "name": "add_case_note",
        "description": (
            "Append a timestamped note to a case's history. "
            "Use when attorney gives instructions, updates, or observations about a case. "
            "Examples: 'anota que', 'add note', 'registra', 'ligar para cliente'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "string",
                    "description": "The case ID",
                },
                "client_name_search": {
                    "type": "string",
                    "description": "Client name to find the case",
                },
                "note": {
                    "type": "string",
                    "description": "The note content to add",
                },
            },
            "required": ["note"],
        },
    },
    {
        "name": "attach_document",
        "description": (
            "Record that a document has been received for a case. "
            "Use after a document is identified (via WhatsApp image, upload, etc.). "
            "Updates the case's document list and shows progress."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "string",
                    "description": "The case ID",
                },
                "client_name_search": {
                    "type": "string",
                    "description": "Client name to find the case",
                },
                "document_type": {
                    "type": "string",
                    "description": "Type: passport, i94, diploma, transcript, pay_stub, lca, org_chart, recommendation_letter, tax_return, birth_certificate, marriage_certificate, photos, ev_letter, resume_cv, job_offer, apostille, translation, other",
                },
                "filename": {
                    "type": "string",
                    "description": "Original filename if available",
                },
                "notes": {
                    "type": "string",
                    "description": "Notes about the document (e.g. 'valid until 03/2029', 'needs apostille')",
                },
            },
            "required": ["document_type"],
        },
    },
    {
        "name": "create_reminder",
        "description": (
            "Create a reminder that will send a WhatsApp alert to the attorney. "
            "Use when attorney says 'lembra-me', 'remind me', 'alerta', 'avisa em'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The reminder message",
                },
                "remind_at": {
                    "type": "string",
                    "description": "When to send the reminder, ISO format YYYY-MM-DDTHH:MM",
                },
                "case_id": {
                    "type": "string",
                    "description": "Optional case ID to link the reminder to",
                },
            },
            "required": ["message", "remind_at"],
        },
    },
    {
        "name": "generate_letter",
        "description": (
            "Generate a legal document: cover letter, RFE response, NIW statement, "
            "support letter, or status inquiry. "
            "Use when attorney says 'gera', 'generate', 'draft', 'criar carta', "
            "'NIW statement', 'cover letter', 'RFE response'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "string",
                    "description": "The case ID",
                },
                "client_name_search": {
                    "type": "string",
                    "description": "Client name to find the case",
                },
                "letter_type": {
                    "type": "string",
                    "description": "Type: initial_filing, rfe_response, appeal, withdrawal, status_inquiry, niw_statement, support_letter",
                },
                "special_instructions": {
                    "type": "string",
                    "description": "Any special instructions for the letter content",
                },
            },
            "required": ["letter_type"],
        },
    },
]


# Required documents by visa type (used by get_case_documents)
REQUIRED_DOCUMENTS = {
    "H-1B": [
        "passport", "i94", "diploma", "transcript", "resume_cv",
        "lca", "org_chart", "job_offer", "pay_stub", "ev_letter",
    ],
    "EB-1A": [
        "passport", "i94", "diploma", "resume_cv", "ev_letter",
        "recommendation_letter", "photos", "tax_return",
    ],
    "EB-2 NIW": [
        "passport", "i94", "diploma", "transcript", "resume_cv",
        "ev_letter", "recommendation_letter", "tax_return",
    ],
    "O-1A": [
        "passport", "i94", "diploma", "resume_cv", "ev_letter",
        "recommendation_letter", "photos",
    ],
    "O-1B": [
        "passport", "i94", "resume_cv", "ev_letter",
        "recommendation_letter", "photos",
    ],
    "I-130": [
        "passport", "birth_certificate", "marriage_certificate",
        "photos", "ev_letter", "tax_return",
    ],
    "I-485": [
        "passport", "i94", "birth_certificate", "photos",
        "tax_return", "pay_stub", "translation",
    ],
    "F-1": [
        "passport", "diploma", "transcript", "photos",
    ],
    "B-2": [
        "passport", "photos",
    ],
    "L-1A": [
        "passport", "i94", "resume_cv", "org_chart", "ev_letter",
    ],
    "L-1B": [
        "passport", "i94", "resume_cv", "ev_letter",
    ],
}

# Human-readable document type names
DOC_TYPE_LABELS = {
    "passport": "Passaporte",
    "i94": "I-94",
    "diploma": "Diploma",
    "transcript": "Histórico Escolar",
    "resume_cv": "Currículo / CV",
    "lca": "LCA Aprovada",
    "org_chart": "Organograma da Empresa",
    "job_offer": "Oferta de Emprego",
    "pay_stub": "Contracheque / Pay Stub",
    "ev_letter": "Carta de Evidência",
    "recommendation_letter": "Carta de Recomendação",
    "photos": "Fotos (passaporte/visto)",
    "tax_return": "Declaração de Impostos",
    "birth_certificate": "Certidão de Nascimento",
    "marriage_certificate": "Certidão de Casamento",
    "apostille": "Apostila",
    "translation": "Tradução Juramentada",
    "other": "Outro Documento",
}
