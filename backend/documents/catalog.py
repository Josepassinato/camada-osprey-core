"""
Document Catalog - Catálogo oficial de tipos de documentos
Conforme especificação técnica completa para validação de documentos imigratórios
"""
from enum import Enum
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """
    Catálogo oficial de tipos de documentos (usar estas chaves exatas)
    """
    # Identidade/Viagem
    PASSPORT_ID_PAGE = "PASSPORT_ID_PAGE"
    VISA_STAMP = "VISA_STAMP"
    I94_RECORD = "I94_RECORD"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"
    SSN_CARD = "SSN_CARD"
    EAD_CARD = "EAD_CARD"
    I797_NOTICE = "I797_NOTICE"
    
    # Estado civil
    BIRTH_CERTIFICATE = "BIRTH_CERTIFICATE"
    MARRIAGE_CERT = "MARRIAGE_CERT"
    DIVORCE_DECREE = "DIVORCE_DECREE"
    DEATH_CERTIFICATE = "DEATH_CERTIFICATE"
    
    # Acadêmicos/Profissionais
    DEGREE_CERTIFICATE = "DEGREE_CERTIFICATE"
    TRANSCRIPT = "TRANSCRIPT"
    CREDENTIAL_EVALUATION = "CREDENTIAL_EVALUATION"
    EMPLOYMENT_OFFER_LETTER = "EMPLOYMENT_OFFER_LETTER"
    EMPLOYMENT_VERIFICATION_LETTER = "EMPLOYMENT_VERIFICATION_LETTER"
    CLIENT_LETTER_END_CLIENT = "CLIENT_LETTER_END_CLIENT"
    LCA_CERTIFIED = "LCA_CERTIFIED"
    PERM_ETA9089 = "PERM_ETA9089"
    
    # Financeiros/Residência
    PAY_STUB = "PAY_STUB"
    TAX_RETURN_1040 = "TAX_RETURN_1040"
    IRS_TAX_TRANSCRIPT = "IRS_TAX_TRANSCRIPT"
    BANK_STATEMENT = "BANK_STATEMENT"
    LEASE_AGREEMENT = "LEASE_AGREEMENT"
    UTILITY_BILL = "UTILITY_BILL"
    
    # Médicos/Fotos/Polícia
    I693_MEDICAL = "I693_MEDICAL"
    PHOTOGRAPHS = "PHOTOGRAPHS"
    POLICE_CERTIFICATE = "POLICE_CERTIFICATE"
    
    # Tradução
    TRANSLATION_CERTIFICATE = "TRANSLATION_CERTIFICATE"
    
    # Evidências relacionais genéricas
    RELATIONSHIP_EVIDENCE_GENERAL = "RELATIONSHIP_EVIDENCE_GENERAL"

class DocumentCatalog:
    """
    Catálogo de documentos com metadados e mapeamentos
    """
    
    def __init__(self):
        self.document_metadata = self._initialize_metadata()
        self.visa_document_mapping = self._initialize_visa_mapping()
    
    def _initialize_metadata(self) -> Dict[str, Dict]:
        """
        Metadados dos tipos de documentos
        """
        return {
            # Identidade/Viagem
            DocumentType.PASSPORT_ID_PAGE.value: {
                "category": "identity_travel",
                "description": "Página de identificação do passaporte",
                "priority": "critical",
                "typical_pages": 1,
                "requires_translation": True
            },
            DocumentType.I94_RECORD.value: {
                "category": "identity_travel", 
                "description": "Registro I-94 de entrada nos EUA",
                "priority": "high",
                "typical_pages": 1,
                "requires_translation": False
            },
            DocumentType.I797_NOTICE.value: {
                "category": "identity_travel",
                "description": "Notificação I-797 do USCIS",
                "priority": "critical",
                "typical_pages": 1,
                "requires_translation": False
            },
            
            # Estado civil
            DocumentType.BIRTH_CERTIFICATE.value: {
                "category": "civil_status",
                "description": "Certidão de nascimento",
                "priority": "critical",
                "typical_pages": 1,
                "requires_translation": True
            },
            DocumentType.MARRIAGE_CERT.value: {
                "category": "civil_status",
                "description": "Certidão de casamento",
                "priority": "critical", 
                "typical_pages": 1,
                "requires_translation": True
            },
            
            # Acadêmicos/Profissionais
            DocumentType.DEGREE_CERTIFICATE.value: {
                "category": "academic_professional",
                "description": "Diploma/Certificado de graduação",
                "priority": "high",
                "typical_pages": 1,
                "requires_translation": True
            },
            DocumentType.TRANSCRIPT.value: {
                "category": "academic_professional",
                "description": "Histórico escolar",
                "priority": "high",
                "typical_pages": 2,
                "requires_translation": True
            },
            DocumentType.CREDENTIAL_EVALUATION.value: {
                "category": "academic_professional",
                "description": "Avaliação de credenciais acadêmicas",
                "priority": "high",
                "typical_pages": 3,
                "requires_translation": False
            },
            DocumentType.EMPLOYMENT_OFFER_LETTER.value: {
                "category": "academic_professional",
                "description": "Carta de oferta de emprego",
                "priority": "critical",
                "typical_pages": 2,
                "requires_translation": False
            },
            DocumentType.EMPLOYMENT_VERIFICATION_LETTER.value: {
                "category": "academic_professional",
                "description": "Carta de verificação de emprego",
                "priority": "medium",
                "typical_pages": 1,
                "requires_translation": False
            },
            
            # Financeiros
            DocumentType.PAY_STUB.value: {
                "category": "financial",
                "description": "Contracheque",
                "priority": "medium",
                "typical_pages": 1,
                "requires_translation": False
            },
            DocumentType.TAX_RETURN_1040.value: {
                "category": "financial",
                "description": "Declaração de imposto de renda 1040",
                "priority": "high",
                "typical_pages": 5,
                "requires_translation": False
            },
            
            # Médicos
            DocumentType.I693_MEDICAL.value: {
                "category": "medical",
                "description": "Exame médico I-693",
                "priority": "critical",
                "typical_pages": 4,
                "requires_translation": False
            },
            
            # Tradução
            DocumentType.TRANSLATION_CERTIFICATE.value: {
                "category": "translation",
                "description": "Certificado de tradução",
                "priority": "critical",
                "typical_pages": 1,
                "requires_translation": False
            }
        }
    
    def _initialize_visa_mapping(self) -> Dict[str, List[str]]:
        """
        Mapeamento de documentos por tipo de visto
        """
        return {
            "H-1B": [
                DocumentType.PASSPORT_ID_PAGE.value,
                DocumentType.I94_RECORD.value,
                DocumentType.DEGREE_CERTIFICATE.value,
                DocumentType.TRANSCRIPT.value,
                DocumentType.CREDENTIAL_EVALUATION.value,
                DocumentType.EMPLOYMENT_OFFER_LETTER.value,
                DocumentType.LCA_CERTIFIED.value,
                DocumentType.I797_NOTICE.value
            ],
            "F-1": [
                DocumentType.PASSPORT_ID_PAGE.value,
                DocumentType.I94_RECORD.value,
                DocumentType.DEGREE_CERTIFICATE.value,
                DocumentType.TRANSCRIPT.value,
                DocumentType.CREDENTIAL_EVALUATION.value,
                "I20_FORM",
                "SEVIS_FEE_RECEIPT"
            ],
            "B-1/B-2": [
                DocumentType.PASSPORT_ID_PAGE.value,
                DocumentType.I94_RECORD.value,
                "FINANCIAL_DOCUMENTS",
                "INVITATION_LETTER"
            ],
            "I-485": [
                DocumentType.PASSPORT_ID_PAGE.value,
                DocumentType.BIRTH_CERTIFICATE.value,
                DocumentType.MARRIAGE_CERT.value,
                DocumentType.I693_MEDICAL.value,
                DocumentType.TAX_RETURN_1040.value,
                DocumentType.EMPLOYMENT_OFFER_LETTER.value
            ],
            "I-589": [
                DocumentType.PASSPORT_ID_PAGE.value,
                DocumentType.BIRTH_CERTIFICATE.value,
                DocumentType.MARRIAGE_CERT.value,
                "PERSECUTION_EVIDENCE",
                "COUNTRY_CONDITION_EVIDENCE"
            ]
        }
    
    def get_document_info(self, doc_type: str) -> Optional[Dict]:
        """
        Retorna informações sobre um tipo de documento
        """
        return self.document_metadata.get(doc_type)
    
    def get_documents_for_visa(self, visa_type: str) -> List[str]:
        """
        Retorna lista de documentos típicos para um tipo de visto
        """
        return self.visa_document_mapping.get(visa_type, [])
    
    def get_document_category(self, doc_type: str) -> Optional[str]:
        """
        Retorna categoria do documento
        """
        info = self.get_document_info(doc_type)
        return info.get("category") if info else None
    
    def requires_translation(self, doc_type: str) -> bool:
        """
        Verifica se documento tipicamente requer tradução
        """
        info = self.get_document_info(doc_type)
        return info.get("requires_translation", False) if info else False
    
    def get_priority(self, doc_type: str) -> str:
        """
        Retorna prioridade do documento (critical, high, medium, low)
        """
        info = self.get_document_info(doc_type)
        return info.get("priority", "medium") if info else "medium"
    
    def is_valid_document_type(self, doc_type: str) -> bool:
        """
        Verifica se é um tipo de documento válido
        """
        try:
            DocumentType(doc_type)
            return True
        except ValueError:
            return False
    
    def get_all_document_types(self) -> List[str]:
        """
        Retorna lista de todos os tipos de documentos válidos
        """
        return [doc_type.value for doc_type in DocumentType]
    
    def get_documents_by_category(self, category: str) -> List[str]:
        """
        Retorna documentos por categoria
        """
        result = []
        for doc_type, metadata in self.document_metadata.items():
            if metadata.get("category") == category:
                result.append(doc_type)
        return result
    
    def suggest_document_type(self, filename: str, content_hints: List[str] = None) -> List[str]:
        """
        Sugere possíveis tipos de documento baseado no nome do arquivo e dicas de conteúdo
        """
        filename_lower = filename.lower()
        suggestions = []
        
        # Heurísticas básicas baseadas no nome do arquivo
        if any(word in filename_lower for word in ["passport", "passaporte"]):
            suggestions.append(DocumentType.PASSPORT_ID_PAGE.value)
        
        if any(word in filename_lower for word in ["diploma", "degree", "certificate"]):
            suggestions.append(DocumentType.DEGREE_CERTIFICATE.value)
            
        if any(word in filename_lower for word in ["transcript", "historico"]):
            suggestions.append(DocumentType.TRANSCRIPT.value)
            
        if any(word in filename_lower for word in ["birth", "nascimento"]):
            suggestions.append(DocumentType.BIRTH_CERTIFICATE.value)
            
        if any(word in filename_lower for word in ["marriage", "casamento"]):
            suggestions.append(DocumentType.MARRIAGE_CERT.value)
            
        if any(word in filename_lower for word in ["employment", "job", "offer"]):
            suggestions.append(DocumentType.EMPLOYMENT_OFFER_LETTER.value)
            
        if any(word in filename_lower for word in ["pay", "payroll", "salary"]):
            suggestions.append(DocumentType.PAY_STUB.value)
            
        if any(word in filename_lower for word in ["tax", "1040"]):
            suggestions.append(DocumentType.TAX_RETURN_1040.value)
            
        if any(word in filename_lower for word in ["i94"]):
            suggestions.append(DocumentType.I94_RECORD.value)
            
        if any(word in filename_lower for word in ["i797"]):
            suggestions.append(DocumentType.I797_NOTICE.value)
            
        if any(word in filename_lower for word in ["i693", "medical"]):
            suggestions.append(DocumentType.I693_MEDICAL.value)
            
        if any(word in filename_lower for word in ["translation", "traducao"]):
            suggestions.append(DocumentType.TRANSLATION_CERTIFICATE.value)
        
        return suggestions[:3]  # Retorna top 3 sugestões

# Instância global do catálogo
document_catalog = DocumentCatalog()