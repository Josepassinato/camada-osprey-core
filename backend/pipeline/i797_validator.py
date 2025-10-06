"""
I-797 Notice of Action Validator - High Precision USCIS Document Validation
Validador especializado para documentos I-797 do USCIS com padrões específicos
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum

logger = logging.getLogger(__name__)

class I797Type(Enum):
    """Tipos de I-797 Notice"""
    APPROVAL = "approval"
    RECEIPT = "receipt" 
    RFE = "rfe"  # Request for Evidence
    DENIAL = "denial"
    REVOCATION = "revocation"
    UNKNOWN = "unknown"

class ServiceCenter(Enum):
    """USCIS Service Centers"""
    EAC = "EAC"  # Vermont Service Center (Eastern Adjudication Center)
    WAC = "WAC"  # California Service Center (Western Adjudication Center) 
    MSC = "MSC"  # National Benefits Center (Missouri Service Center)
    NBC = "NBC"  # National Benefits Center
    SRC = "SRC"  # Texas Service Center (Southern Regional Center)
    LIN = "LIN"  # Nebraska Service Center (Lincoln)
    IOE = "IOE"  # ELIS system receipts
    FLN = "FLN"  # Federal Law Enforcement Training Center

@dataclass
class I797Data:
    """Dados estruturados extraídos do I-797"""
    receipt_number: str
    service_center: str
    case_type: str
    priority_date: Optional[date]
    notice_date: Optional[date]
    valid_until_date: Optional[date]
    i797_type: I797Type
    petitioner_name: str
    beneficiary_name: str
    
    # Validation results
    receipt_number_valid: bool
    format_valid: bool
    dates_consistent: bool
    confidence_score: float
    
    # Raw extracted data
    raw_text: str
    extracted_fields: Dict[str, Any]

@dataclass
class I797ValidationResult:
    """Resultado completo da validação I-797"""
    i797_data: Optional[I797Data]
    validation_status: str  # VALID, INVALID, SUSPICIOUS
    confidence_score: float
    issues: List[str]
    recommendations: List[str]
    formatting_analysis: Dict[str, Any]

class I797Validator:
    """
    Validador especializado para documentos I-797 do USCIS
    Implementa validação de Receipt Number, formatação e consistência de dados
    """
    
    def __init__(self):
        # Receipt Number patterns por Service Center
        self.receipt_patterns = {
            ServiceCenter.EAC: r'^EAC\d{10}$',
            ServiceCenter.WAC: r'^WAC\d{10}$', 
            ServiceCenter.MSC: r'^MSC\d{10}$',
            ServiceCenter.NBC: r'^NBC\d{10}$',
            ServiceCenter.SRC: r'^SRC\d{10}$',
            ServiceCenter.LIN: r'^LIN\d{10}$',
            ServiceCenter.IOE: r'^IOE\d{10}$',
            ServiceCenter.FLN: r'^FLN\d{10}$'
        }
        
        # I-797 formatting patterns
        self.formatting_patterns = {
            'header': r'U\.S\.\s+DEPARTMENT\s+OF\s+HOMELAND\s+SECURITY',
            'uscis_logo': r'U\.S\.\s+Citizenship\s+and\s+Immigration\s+Services',
            'form_title': r'I-797[A-C]?,?\s+Notice\s+of\s+Action',
            'receipt_number_line': r'Receipt\s+Number\s*:?\s*([A-Z]{3}\d{10})',
            'case_type_line': r'Case\s+Type\s*:?\s*([A-Z0-9\-\s]+)',
            'priority_date': r'Priority\s+Date\s*:?\s*([A-Z]{3}\s+\d{1,2},\s+\d{4})',
            'notice_date': r'Notice\s+Date\s*:?\s*([A-Z]{3}\s+\d{1,2},\s+\d{4})',
            'valid_until': r'Valid\s+(?:From|Until|Through)\s*:?\s*([A-Z]{3}\s+\d{1,2},\s+\d{4})'
        }
        
        # Common I-797 case types
        self.valid_case_types = {
            'I-129', 'I-130', 'I-140', 'I-485', 'I-765', 'I-131',
            'I-90', 'I-751', 'N-400', 'I-526', 'I-829', 'I-924'
        }
    
    def validate_i797(self, 
                     document_text: str,
                     extracted_data: Dict[str, Any] = None) -> I797ValidationResult:
        """
        Validação completa de documento I-797
        
        Args:
            document_text: Texto extraído do documento via OCR
            extracted_data: Dados adicionais extraídos (opcional)
            
        Returns:
            I797ValidationResult com análise completa
        """
        try:
            logger.info("Starting I-797 validation")
            
            # 1. Verificar se é realmente um I-797
            is_i797 = self._verify_i797_document(document_text)
            if not is_i797:
                return self._create_invalid_result("Document does not appear to be an I-797")
            
            # 2. Extrair dados estruturados
            i797_data = self._extract_i797_data(document_text, extracted_data)
            
            # 3. Validar Receipt Number
            receipt_valid = self._validate_receipt_number(i797_data.receipt_number)
            i797_data.receipt_number_valid = receipt_valid
            
            # 4. Validar formatação USCIS
            format_analysis = self._validate_uscis_formatting(document_text)
            i797_data.format_valid = format_analysis['overall_valid']
            
            # 5. Validar consistência de datas
            dates_consistent = self._validate_date_consistency(i797_data)
            i797_data.dates_consistent = dates_consistent
            
            # 6. Calcular confidence score
            confidence = self._calculate_i797_confidence(i797_data, format_analysis)
            i797_data.confidence_score = confidence
            
            # 7. Determinar status de validação
            validation_status, issues, recommendations = self._determine_i797_status(
                i797_data, format_analysis
            )
            
            return I797ValidationResult(
                i797_data=i797_data,
                validation_status=validation_status,
                confidence_score=confidence,
                issues=issues,
                recommendations=recommendations,
                formatting_analysis=format_analysis
            )
            
        except Exception as e:
            logger.error(f"I-797 validation error: {e}")
            return self._create_invalid_result(f"Validation failed: {str(e)}")
    
    def _verify_i797_document(self, text: str) -> bool:
        """Verifica se o documento é realmente um I-797"""
        indicators = [
            'I-797',
            'Notice of Action',
            'U.S. Department of Homeland Security',
            'U.S. Citizenship and Immigration Services',
            'USCIS',
            'Receipt Number'
        ]
        
        text_upper = text.upper()
        matches = sum(1 for indicator in indicators if indicator.upper() in text_upper)
        
        # Precisa de pelo menos 3 indicadores
        return matches >= 3
    
    def _extract_i797_data(self, 
                          text: str, 
                          additional_data: Dict[str, Any] = None) -> I797Data:
        """Extrai dados estruturados do I-797"""
        
        # Extract Receipt Number
        receipt_match = re.search(self.formatting_patterns['receipt_number_line'], text, re.IGNORECASE)
        receipt_number = receipt_match.group(1) if receipt_match else ""
        
        # Extract Case Type  
        case_type_match = re.search(self.formatting_patterns['case_type_line'], text, re.IGNORECASE)
        case_type = case_type_match.group(1).strip() if case_type_match else ""
        
        # Extract dates
        priority_date = self._extract_date(text, self.formatting_patterns['priority_date'])
        notice_date = self._extract_date(text, self.formatting_patterns['notice_date'])
        valid_until = self._extract_date(text, self.formatting_patterns['valid_until'])
        
        # Determine I-797 type
        i797_type = self._determine_i797_type(text)
        
        # Extract names (simplified patterns)
        petitioner_name = self._extract_petitioner_name(text)
        beneficiary_name = self._extract_beneficiary_name(text)
        
        # Determine service center from receipt number
        service_center = self._get_service_center(receipt_number)
        
        return I797Data(
            receipt_number=receipt_number,
            service_center=service_center,
            case_type=case_type,
            priority_date=priority_date,
            notice_date=notice_date,
            valid_until_date=valid_until,
            i797_type=i797_type,
            petitioner_name=petitioner_name,
            beneficiary_name=beneficiary_name,
            receipt_number_valid=False,  # Will be set later
            format_valid=False,  # Will be set later
            dates_consistent=False,  # Will be set later
            confidence_score=0.0,  # Will be calculated later
            raw_text=text[:1000],  # First 1000 chars for reference
            extracted_fields=additional_data or {}
        )
    
    def _validate_receipt_number(self, receipt_number: str) -> bool:
        """Valida Receipt Number do USCIS"""
        if not receipt_number:
            return False
        
        receipt_clean = receipt_number.replace(' ', '').replace('-', '').upper()
        
        # Check against all known patterns
        for service_center, pattern in self.receipt_patterns.items():
            if re.match(pattern, receipt_clean):
                return True
        
        return False
    
    def _validate_uscis_formatting(self, text: str) -> Dict[str, Any]:
        """Valida formatação oficial USCIS"""
        analysis = {
            'header_present': False,
            'uscis_logo_present': False,
            'form_title_present': False,
            'receipt_format_valid': False,
            'overall_valid': False,
            'formatting_score': 0.0
        }
        
        # Check each formatting element
        if re.search(self.formatting_patterns['header'], text, re.IGNORECASE):
            analysis['header_present'] = True
            analysis['formatting_score'] += 0.25
        
        if re.search(self.formatting_patterns['uscis_logo'], text, re.IGNORECASE):
            analysis['uscis_logo_present'] = True
            analysis['formatting_score'] += 0.25
        
        if re.search(self.formatting_patterns['form_title'], text, re.IGNORECASE):
            analysis['form_title_present'] = True
            analysis['formatting_score'] += 0.25
        
        if re.search(self.formatting_patterns['receipt_number_line'], text, re.IGNORECASE):
            analysis['receipt_format_valid'] = True
            analysis['formatting_score'] += 0.25
        
        # Overall validity (need at least 3/4 elements)
        analysis['overall_valid'] = analysis['formatting_score'] >= 0.75
        
        return analysis
    
    def _validate_date_consistency(self, i797_data: I797Data) -> bool:
        """Valida consistência entre datas"""
        try:
            # Notice date should be present
            if not i797_data.notice_date:
                return False
            
            today = date.today()
            
            # Notice date should not be in the future
            if i797_data.notice_date > today:
                return False
            
            # If priority date exists, should be before or equal to notice date
            if i797_data.priority_date and i797_data.priority_date > i797_data.notice_date:
                return False
            
            # If valid until date exists, should be after notice date
            if (i797_data.valid_until_date and 
                i797_data.valid_until_date <= i797_data.notice_date):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Date consistency validation error: {e}")
            return False
    
    def _extract_date(self, text: str, pattern: str) -> Optional[date]:
        """Extrai data usando padrão específico"""
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if not match:
                return None
            
            date_str = match.group(1)
            # Parse format like "JAN 15, 2024"
            parsed_date = datetime.strptime(date_str, "%b %d, %Y").date()
            return parsed_date
            
        except Exception as e:
            logger.debug(f"Date extraction error for pattern {pattern}: {e}")
            return None
    
    def _determine_i797_type(self, text: str) -> I797Type:
        """Determina tipo de I-797 baseado no conteúdo"""
        text_upper = text.upper()
        
        if 'APPROVAL' in text_upper or 'APPROVED' in text_upper:
            return I797Type.APPROVAL
        elif 'REQUEST FOR EVIDENCE' in text_upper or 'RFE' in text_upper:
            return I797Type.RFE
        elif 'DENIAL' in text_upper or 'DENIED' in text_upper:
            return I797Type.DENIAL
        elif 'RECEIPT' in text_upper:
            return I797Type.RECEIPT
        elif 'REVOCATION' in text_upper or 'REVOKED' in text_upper:
            return I797Type.REVOCATION
        else:
            return I797Type.UNKNOWN
    
    def _extract_petitioner_name(self, text: str) -> str:
        """Extrai nome do petitioner (simplificado)"""
        patterns = [
            r'Petitioner:?\s*([A-Z][A-Za-z\s,\.]+)',
            r'From:?\s*([A-Z][A-Za-z\s,\.]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # Clean up name (remove trailing punctuation)
                return re.sub(r'[,\.]$', '', name).strip()
        
        return ""
    
    def _extract_beneficiary_name(self, text: str) -> str:
        """Extrai nome do beneficiary (simplificado)"""
        patterns = [
            r'Beneficiary:?\s*([A-Z][A-Za-z\s,\.]+)',
            r'For:?\s*([A-Z][A-Za-z\s,\.]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                return re.sub(r'[,\.]$', '', name).strip()
        
        return ""
    
    def _get_service_center(self, receipt_number: str) -> str:
        """Determina service center pelo Receipt Number"""
        if not receipt_number:
            return ""
        
        prefix = receipt_number[:3].upper()
        service_centers = {
            'EAC': 'Vermont Service Center',
            'WAC': 'California Service Center', 
            'MSC': 'Missouri Service Center',
            'NBC': 'National Benefits Center',
            'SRC': 'Texas Service Center',
            'LIN': 'Nebraska Service Center',
            'IOE': 'ELIS System',
            'FLN': 'Federal Law Enforcement Training Center'
        }
        
        return service_centers.get(prefix, f"Unknown ({prefix})")
    
    def _calculate_i797_confidence(self, 
                                  i797_data: I797Data,
                                  format_analysis: Dict[str, Any]) -> float:
        """Calcula confidence score do I-797"""
        score = 0.0
        
        # Receipt number validation (30%)
        if i797_data.receipt_number_valid:
            score += 0.30
        
        # Formatting validation (25%)
        score += format_analysis['formatting_score'] * 0.25
        
        # Date consistency (20%)
        if i797_data.dates_consistent:
            score += 0.20
        
        # Case type validation (15%)
        if any(case_type in i797_data.case_type for case_type in self.valid_case_types):
            score += 0.15
        
        # Name extraction (10%)
        if i797_data.petitioner_name or i797_data.beneficiary_name:
            score += 0.10
        
        return min(score, 1.0)
    
    def _determine_i797_status(self, 
                              i797_data: I797Data,
                              format_analysis: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
        """Determina status de validação final"""
        issues = []
        recommendations = []
        
        # Check critical validations
        if not i797_data.receipt_number_valid:
            issues.append("Invalid Receipt Number format")
        
        if not format_analysis['overall_valid']:
            issues.append("Document does not match USCIS formatting standards")
        
        if not i797_data.dates_consistent:
            issues.append("Date inconsistencies detected")
        
        # Determine status
        if not issues:
            status = "VALID"
            recommendations.append("I-797 validation successful")
        elif len(issues) >= 2:
            status = "INVALID"
            recommendations.extend([
                "Document appears to be invalid or corrupted",
                "Verify document authenticity",
                "Consider rescanning with better quality"
            ])
        else:
            status = "SUSPICIOUS"
            recommendations.extend([
                "Manual review recommended",
                "Verify specific issues identified",
                "Check document quality and completeness"
            ])
        
        return status, issues, recommendations
    
    def _create_invalid_result(self, error_message: str) -> I797ValidationResult:
        """Cria resultado para documento inválido"""
        return I797ValidationResult(
            i797_data=None,
            validation_status="INVALID",
            confidence_score=0.0,
            issues=[error_message],
            recommendations=["Verify document is a valid I-797", "Check document quality"],
            formatting_analysis={}
        )

# Global validator instance
i797_validator = I797Validator()