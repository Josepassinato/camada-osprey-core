"""
Social Security Card Validator
Validador especializado para cartões de Social Security
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
import logging
import re
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class SSNValidationResult(BaseModel):
    """Resultado da validação de SSN"""
    is_valid: bool
    ssn_number: Optional[str] = None
    card_type: Optional[str] = None  # "Unrestricted", "Valid for work only with DHS authorization", etc.
    issues: List[str] = []
    confidence_score: float = 0.0
    recommendations: List[str] = []
    
    # Campos específicos extraídos
    name_on_card: Optional[str] = None
    signature_present: bool = False
    card_condition: str = "unknown"  # "good", "fair", "poor", "damaged"
    
    # Validações específicas
    ssn_format_valid: bool = False
    name_matches_applicant: bool = False
    card_readable: bool = False
    
class SocialSecurityValidator:
    """Validador para cartões de Social Security"""
    
    def __init__(self):
        # Padrões de SSN válidos
        self.ssn_pattern = re.compile(r'^\d{3}-?\d{2}-?\d{4}$')
        
        # Áreas SSN inválidas (não mais atribuídas ou reservadas)
        self.invalid_areas = {
            '000', '666', '900', '901', '902', '903', '904', '905', '906', '907', '908', '909'
        }
        
        # Tipos de cartão conhecidos
        self.card_types = {
            'unrestricted': 'Unrestricted - Valid for employment',
            'work_authorization': 'Valid for work only with DHS authorization',
            'not_valid_employment': 'Not valid for employment'
        }

    def validate_ssn_format(self, ssn: str) -> Tuple[bool, List[str]]:
        """Valida formato do SSN"""
        issues = []
        
        if not ssn:
            issues.append("SSN não fornecido")
            return False, issues
            
        # Remove formatação
        clean_ssn = re.sub(r'[^\d]', '', ssn)
        
        if len(clean_ssn) != 9:
            issues.append("SSN deve ter exatamente 9 dígitos")
            return False, issues
            
        # Verificar área (primeiros 3 dígitos)
        area = clean_ssn[:3]
        if area in self.invalid_areas:
            issues.append(f"Área SSN inválida: {area}")
            return False, issues
            
        # Verificar grupo (dígitos 4-5)
        group = clean_ssn[3:5]
        if group == '00':
            issues.append("Grupo SSN não pode ser 00")
            return False, issues
            
        # Verificar número serial (últimos 4 dígitos)
        serial = clean_ssn[5:9]
        if serial == '0000':
            issues.append("Número serial SSN não pode ser 0000")
            return False, issues
            
        return True, issues

    def extract_ssn_from_text(self, text: str) -> Optional[str]:
        """Extrai SSN do texto OCR"""
        # Padrões comuns de SSN em documentos
        patterns = [
            r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',  # 123-45-6789 ou 123456789
            r'SSN:?\s*(\d{3}[-\s]?\d{2}[-\s]?\d{4})',
            r'Social Security Number:?\s*(\d{3}[-\s]?\d{2}[-\s]?\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Se o padrão tem grupo de captura, use-o; caso contrário, use o match completo
                return match.group(1) if match.groups() else match.group(0)
        
        return None

    def analyze_card_condition(self, text: str, confidence_scores: Dict[str, float]) -> str:
        """Analisa condição física do cartão baseado na qualidade OCR"""
        # Baseado na qualidade do OCR e palavras-chave
        avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0
        
        # Palavras que indicam problemas
        damage_indicators = ['damaged', 'torn', 'faded', 'illegible', 'worn']
        
        text_lower = text.lower()
        damage_count = sum(1 for indicator in damage_indicators if indicator in text_lower)
        
        if avg_confidence >= 0.9 and damage_count == 0:
            return "good"
        elif avg_confidence >= 0.7 and damage_count <= 1:
            return "fair"
        elif avg_confidence >= 0.5 and damage_count <= 2:
            return "poor"
        else:
            return "damaged"

    def validate_social_security_card(
        self,
        document_text: str,
        applicant_name: str,
        confidence_scores: Optional[Dict[str, float]] = None
    ) -> SSNValidationResult:
        """
        Valida cartão de Social Security
        
        Args:
            document_text: Texto extraído do documento via OCR
            applicant_name: Nome do aplicante para comparação
            confidence_scores: Scores de confiança do OCR por palavra
            
        Returns:
            SSNValidationResult com validação completa
        """
        try:
            result = SSNValidationResult(is_valid=False)
            
            if not document_text:
                result.issues.append("Documento não contém texto legível")
                return result
                
            # 1. Extrair SSN do texto
            extracted_ssn = self.extract_ssn_from_text(document_text)
            if extracted_ssn:
                result.ssn_number = extracted_ssn
                
                # Validar formato do SSN
                ssn_valid, ssn_issues = self.validate_ssn_format(extracted_ssn)
                result.ssn_format_valid = ssn_valid
                result.issues.extend(ssn_issues)
            else:
                result.issues.append("SSN não encontrado no documento")
                
            # 2. Verificar se é um cartão de Social Security válido
            ss_keywords = ['social security', 'social security administration', 'ssa']
            text_lower = document_text.lower()
            
            is_ss_card = any(keyword in text_lower for keyword in ss_keywords)
            if not is_ss_card:
                result.issues.append("Documento não parece ser um cartão de Social Security")
            
            # 3. Detectar tipo de cartão
            if 'not valid for employment' in text_lower:
                result.card_type = self.card_types['not_valid_employment']
            elif 'valid for work only with dhs authorization' in text_lower:
                result.card_type = self.card_types['work_authorization'] 
            else:
                result.card_type = self.card_types['unrestricted']
                
            # 4. Extrair nome do cartão
            name_patterns = [
                r'(?:NAME|Name)[:]\s*([A-Z\s]+)',
                r'^([A-Z\s]{2,50})$',  # Linha com apenas nome em maiúsculas
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, document_text, re.MULTILINE)
                if match:
                    result.name_on_card = match.group(1).strip()
                    break
                    
            # 5. Comparar nome com aplicante
            if result.name_on_card and applicant_name:
                # Normalizar nomes para comparação
                card_name = re.sub(r'[^\w\s]', '', result.name_on_card.upper())
                applicant_normalized = re.sub(r'[^\w\s]', '', applicant_name.upper())
                
                # Verificar se há correspondência parcial (pelo menos 70% das palavras)
                card_words = set(card_name.split())
                applicant_words = set(applicant_normalized.split())
                
                if card_words and applicant_words:
                    match_ratio = len(card_words.intersection(applicant_words)) / max(len(card_words), len(applicant_words))
                    result.name_matches_applicant = match_ratio >= 0.7
                    
                    if not result.name_matches_applicant:
                        result.issues.append(f"Nome no cartão ({result.name_on_card}) não corresponde ao aplicante ({applicant_name})")
            else:
                result.issues.append("Não foi possível extrair o nome do cartão ou comparar com o aplicante")
                
            # 6. Verificar assinatura (busca por indicadores)
            signature_indicators = ['signature', 'signed', 'sign']
            result.signature_present = any(indicator in text_lower for indicator in signature_indicators)
            
            # 7. Analisar condição do cartão
            result.card_condition = self.analyze_card_condition(document_text, confidence_scores or {})
            
            # 8. Verificar legibilidade
            result.card_readable = len(document_text.strip()) > 10  # Texto mínimo legível
            
            # 9. Calcular score de confiança
            confidence_factors = []
            
            if result.ssn_format_valid:
                confidence_factors.append(0.3)
            if result.name_matches_applicant:
                confidence_factors.append(0.25)
            if is_ss_card:
                confidence_factors.append(0.2)
            if result.card_readable:
                confidence_factors.append(0.15)
            if result.card_condition in ['good', 'fair']:
                confidence_factors.append(0.1)
                
            result.confidence_score = sum(confidence_factors)
            
            # 10. Determinar se é válido
            result.is_valid = (
                result.ssn_format_valid and
                result.name_matches_applicant and
                result.card_readable and
                is_ss_card and
                result.card_condition != 'damaged'
            )
            
            # 11. Gerar recomendações
            if not result.is_valid:
                if not result.ssn_format_valid:
                    result.recommendations.append("Verifique se o SSN está claramente visível e correto")
                if not result.name_matches_applicant:
                    result.recommendations.append("Confirme que o nome no cartão corresponde ao nome do aplicante")
                if not result.card_readable:
                    result.recommendations.append("Documento precisa estar mais legível - considere nova foto")
                if result.card_condition == 'damaged':
                    result.recommendations.append("Cartão danificado - considere solicitar substituição ao SSA")
            else:
                result.recommendations.append("Cartão de Social Security válido e aceito")
                
            logger.info(f"Social Security validation completed - Valid: {result.is_valid}, Confidence: {result.confidence_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error validating Social Security card: {e}")
            result = SSNValidationResult(
                is_valid=False,
                issues=[f"Erro na validação: {str(e)}"],
                recommendations=["Tente fazer upload novamente ou contacte o suporte"]
            )
            return result

    def get_ssn_requirements(self) -> Dict[str, Any]:
        """Retorna requisitos para cartão de Social Security válido"""
        return {
            "document_type": "Social Security Card",
            "required_elements": [
                "Social Security Number (9 digits)",
                "Full name matching applicant",
                "Card in good condition",
                "Clear and readable text"
            ],
            "format_requirements": [
                "SSN format: XXX-XX-XXXX",
                "Area (first 3 digits) cannot be 000, 666, or 900-999",
                "Group (middle 2 digits) cannot be 00", 
                "Serial (last 4 digits) cannot be 0000"
            ],
            "card_types_accepted": [
                "Unrestricted (no work restrictions)",
                "Valid for work only with DHS authorization (for certain visa holders)",
                "Not valid for employment (generally not accepted for work authorization)"
            ],
            "common_issues": [
                "Damaged or illegible card",
                "Name mismatch with other documents",
                "Invalid SSN format",
                "Poor photo quality"
            ],
            "tips": [
                "Take photo in good lighting",
                "Ensure all text is clearly visible",
                "Card should be flat without shadows",
                "If card is damaged, consider requesting replacement from SSA"
            ]
        }
        
    def validate_for_uscis_purposes(self, validation_result: SSNValidationResult, visa_type: str) -> Dict[str, Any]:
        """Valida SSN card especificamente para propósitos USCIS"""
        
        # Requisitos específicos por tipo de visto/aplicação
        visa_requirements = {
            'H-1B': {
                'ssn_required': False,  # SSN não é obrigatório para H-1B inicial
                'acceptable_types': ['unrestricted', 'work_authorization']
            },
            'I-485': {
                'ssn_required': True,   # SSN geralmente necessário para AOS
                'acceptable_types': ['unrestricted', 'work_authorization']
            },
            'I-765': {
                'ssn_required': False,  # Para EAD application
                'acceptable_types': ['unrestricted', 'work_authorization', 'not_valid_employment']
            }
        }
        
        requirements = visa_requirements.get(visa_type, {
            'ssn_required': False,
            'acceptable_types': ['unrestricted', 'work_authorization']
        })
        
        uscis_validation = {
            "uscis_acceptable": False,
            "visa_type": visa_type,
            "ssn_required": requirements['ssn_required'],
            "validation_summary": validation_result.dict(),
            "uscis_specific_issues": [],
            "uscis_recommendations": []
        }
        
        # Verificar se é aceitável para USCIS
        if validation_result.is_valid:
            card_type_key = None
            if 'unrestricted' in validation_result.card_type.lower():
                card_type_key = 'unrestricted'
            elif 'dhs authorization' in validation_result.card_type.lower():
                card_type_key = 'work_authorization'
            elif 'not valid for employment' in validation_result.card_type.lower():
                card_type_key = 'not_valid_employment'
                
            if card_type_key and card_type_key in requirements['acceptable_types']:
                uscis_validation["uscis_acceptable"] = True
                uscis_validation["uscis_recommendations"].append("Social Security Card aceito para este tipo de aplicação USCIS")
            else:
                uscis_validation["uscis_specific_issues"].append(f"Tipo de cartão não aceito para {visa_type}")
        else:
            uscis_validation["uscis_specific_issues"].extend(validation_result.issues)
            
        if not uscis_validation["uscis_acceptable"]:
            uscis_validation["uscis_recommendations"].extend([
                "Verifique se você possui o tipo correto de Social Security Card",
                f"Para {visa_type}, os tipos aceitos são: {', '.join(requirements['acceptable_types'])}",
                "Se necessário, consulte o Social Security Administration para esclarecimentos"
            ])
            
        return uscis_validation