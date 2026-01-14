import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from models.documents import DocumentPriority, DocumentType, UserDocument
from agents.specialized import create_document_validator

logger = logging.getLogger(__name__)


def extract_text_from_base64_image(base64_content: str) -> str:
    """Extract text from base64 image using OCR simulation."""
    return "Extracted text from document using OCR"


def validate_file_type(mime_type: str) -> bool:
    """Validate if file type is supported."""
    supported_types = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/tiff",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    return mime_type in supported_types


async def analyze_document_with_ai(document: UserDocument) -> Dict[str, Any]:
    """Analyze document with Dr. Miguel's improved validation."""
    try:
        validator = create_document_validator()

        if document.mime_type.startswith("image/"):
            content = extract_text_from_base64_image(document.content_base64)
        else:
            content = f"Document type: {document.document_type}, Filename: {document.original_filename}"

        user_data = getattr(document, "user_data", {})

        validation_prompt = f"""
        VALIDAÇÃO RIGOROSA DE DOCUMENTO - DR. MIGUEL MELHORADO
        
        DADOS CRÍTICOS PARA VALIDAÇÃO:
        - Tipo de Documento Esperado: {document.document_type}
        - Conteúdo do Documento: {content[:1500]}
        - Dados do Usuário: {user_data}
        - Nome do Arquivo: {document.original_filename}
        
        VALIDAÇÕES OBRIGATÓRIAS:
        1. TIPO CORRETO: Verificar se é exatamente do tipo "{document.document_type}"
        2. NOME CORRETO: Verificar se nome no documento corresponde ao aplicante
        3. AUTENTICIDADE: Verificar se é documento genuíno
        4. VALIDADE: Verificar se não está vencido
        5. ACEITABILIDADE USCIS: Confirmar se atende padrões USCIS
        
        INSTRUÇÕES CRÍTICAS:
        - Se tipo de documento não for o esperado → REJEITAR
        - Se nome não corresponder ao aplicante → REJEITAR  
        - Se documento vencido → REJEITAR
        - Explicar claramente qualquer problema encontrado
        
        RESPOSTA OBRIGATÓRIA EM JSON:
        {{
            "document_type_identified": "string",
            "type_correct": true/false,
            "name_validation": "approved|rejected|cannot_verify",
            "belongs_to_applicant": true/false,
            "validity_status": "valid|invalid|expired|unclear",
            "uscis_acceptable": true/false,
            "critical_issues": ["array of issues"],
            "verdict": "APROVADO|REJEITADO|NECESSITA_REVISÃO",
            "completeness_score": 0-100,
            "key_information": ["extracted info"],
            "suggestions": ["improvement suggestions"],
            "rejection_reason": "specific reason if rejected"
        }}
        
        Faça validação técnica rigorosa conforme protocolo Dr. Miguel.
        """

        session_id = f"doc_analysis_{document.id}"
        dr_miguel_analysis = await validator._call_agent(validation_prompt, session_id)

        analysis_text = dr_miguel_analysis.strip()
        analysis_text = analysis_text.replace("```json", "").replace("```", "").strip()

        try:
            miguel_result = json.loads(analysis_text)
            analysis = {
                "completeness_score": miguel_result.get("completeness_score", 50),
                "validity_status": miguel_result.get("validity_status", "unclear"),
                "key_information": miguel_result.get("key_information", []),
                "missing_information": [],
                "suggestions": miguel_result.get("suggestions", []),
                "expiration_warnings": [],
                "quality_issues": miguel_result.get("critical_issues", []),
                "next_steps": [],
                "dr_miguel_validation": {
                    "document_type_identified": miguel_result.get("document_type_identified"),
                    "type_correct": miguel_result.get("type_correct"),
                    "belongs_to_applicant": miguel_result.get("belongs_to_applicant"),
                    "verdict": miguel_result.get("verdict"),
                    "rejection_reason": miguel_result.get("rejection_reason"),
                    "uscis_acceptable": miguel_result.get("uscis_acceptable"),
                },
            }
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse Dr. Miguel analysis: {analysis_text}")
            analysis = {
                "completeness_score": 25,
                "validity_status": "unclear",
                "key_information": ["Análise pendente - erro na validação"],
                "missing_information": ["Validação completa necessária"],
                "suggestions": ["Documento precisa ser revalidado pelo Dr. Miguel"],
                "expiration_warnings": [],
                "quality_issues": ["Erro na análise automática"],
                "next_steps": ["Reenviar documento ou contactar suporte"],
                "dr_miguel_validation": {
                    "verdict": "NECESSITA_REVISÃO",
                    "rejection_reason": "Erro na análise automática",
                },
            }

        return analysis

    except Exception as e:
        logger.error(f"Error analyzing document with sistema: {str(e)}")
        return {
            "completeness_score": 50,
            "validity_status": "unclear",
            "key_information": ["Documento carregado"],
            "missing_information": ["Análise automática não disponível"],
            "suggestions": ["Revise o documento manualmente"],
            "expiration_warnings": [],
            "quality_issues": ["Análise automática falhou"],
            "next_steps": ["Upload realizado, aguarde revisão manual"],
        }


def determine_document_priority(
    document_type: DocumentType, expiration_date: Optional[datetime]
) -> DocumentPriority:
    """Determine document priority based on type and expiration."""
    high_priority_docs = [DocumentType.passport, DocumentType.medical_exam, DocumentType.police_clearance]

    if document_type in high_priority_docs:
        return DocumentPriority.high

    if expiration_date:
        days_to_expire = (expiration_date - datetime.now(timezone.utc)).days
        if days_to_expire <= 30:
            return DocumentPriority.high
        if days_to_expire <= 90:
            return DocumentPriority.medium

    return DocumentPriority.low
