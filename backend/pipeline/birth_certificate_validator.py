"""
Birth Certificate Validator - Specific Document Validator
Validador especializado para Certidões de Nascimento
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date
import asyncio

from .pipeline_framework import PipelineStage, PipelineContext
from .real_ocr_engine import real_ocr_engine

logger = logging.getLogger(__name__)

@dataclass
class BirthCertificateData:
    """Structured data from birth certificate"""
    full_name: str = ""
    date_of_birth: Optional[date] = None
    place_of_birth: str = ""
    parents_names: List[str] = None
    registration_number: str = ""
    registration_date: Optional[date] = None
    registry_office: str = ""
    country_issued: str = ""
    language: str = ""
    
    # Validation results
    confidence_score: float = 0.0
    validation_status: str = "PENDING"  # VALID, INVALID, SUSPICIOUS
    issues: List[str] = None
    
    def __post_init__(self):
        if self.parents_names is None:
            self.parents_names = []
        if self.issues is None:
            self.issues = []

class BirthCertificateValidator:
    """
    Specialized validator for birth certificates
    Supports multiple languages and formats
    """
    
    def __init__(self):
        self.name_patterns = {
            'full_name': [
                r'(?:nome|name|nom|nombre)[:\s]+([A-Z][A-Za-z\s]+)',
                r'(?:full\s+name|nome\s+completo)[:\s]+([A-Z][A-Za-z\s]+)',
                r'(?:nasceu|born|né|nació)[:\s]+([A-Z][A-Za-z\s]+)',
            ],
            'mother_name': [
                r'(?:mãe|mother|mère|madre|mae)[:\s]+([A-Z][A-Za-z\s]+)',
                r'(?:nome\s+da\s+mãe|mother\'?s?\s+name)[:\s]+([A-Z][A-Za-z\s]+)',
            ],
            'father_name': [
                r'(?:pai|father|père|padre)[:\s]+([A-Z][A-Za-z\s]+)',
                r'(?:nome\s+do\s+pai|father\'?s?\s+name)[:\s]+([A-Z][A-Za-z\s]+)',
            ]
        }
        
        self.date_patterns = [
            r'(?:nascimento|birth|naissance|nacimiento)[:\s]+(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4})',
            r'(?:born\s+on|nasceu\s+em)[:\s]+(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4})',
            r'(?:date\s+of\s+birth|data\s+de\s+nascimento)[:\s]+([A-Z]{3}\s+\d{1,2},?\s+\d{4})',
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[A-Za-z]*\s+\d{4})',
        ]
        
        self.place_patterns = [
            r'(?:local|place|lieu|lugar)[:\s]+(?:de\s+)?(?:nascimento|birth|naissance|nacimiento)[:\s]+([A-Z][A-Za-z\s,-]+)',
            r'(?:born\s+in|nasceu\s+em)[:\s]+([A-Z][A-Za-z\s,-]+)',
            r'(?:place\s+of\s+birth|local\s+de\s+nascimento)[:\s]+([A-Z][A-Za-z\s,-]+)',
        ]
        
        self.registry_patterns = [
            r'(?:registro|registration|registre|registro)[:\s]+(?:n[oº°]?\.?\s*)?([A-Z0-9\-\/]+)',
            r'(?:certificate\s+number|número\s+da\s+certidão)[:\s]+([A-Z0-9\-\/]+)',
            r'(?:livro|book|livre|libro)[:\s]+([A-Z0-9\-\/]+)',
        ]
    
    async def validate_birth_certificate(self, 
                                       document_content: str,
                                       document_type: str = "birth_certificate",
                                       language_hint: str = None) -> BirthCertificateData:
        """
        Validate and extract data from birth certificate
        
        Args:
            document_content: Base64 image or text content
            document_type: Type of document for processing hints
            language_hint: Language hint (pt, en, es, fr)
        
        Returns:
            BirthCertificateData with extracted and validated information
        """
        try:
            result = BirthCertificateData()
            
            # 1. Extract text if image provided
            if self._is_base64_image(document_content):
                ocr_result = await real_ocr_engine.extract_text_from_image(
                    document_content, 
                    mode="document",
                    language=language_hint or "auto"
                )
                text_content = ocr_result.text
                result.language = ocr_result.language
                base_confidence = ocr_result.confidence
            else:
                text_content = document_content
                result.language = language_hint or "unknown"
                base_confidence = 0.9  # High confidence for direct text
            
            # 2. Extract structured data
            result = await self._extract_birth_certificate_data(text_content, result)
            
            # 3. Validate extracted data
            validation_result = self._validate_extracted_data(result)
            result.validation_status = validation_result['status']
            result.issues.extend(validation_result['issues'])
            
            # 4. Calculate final confidence
            result.confidence_score = self._calculate_confidence(result, base_confidence)
            
            logger.info(f"Birth certificate validation completed: status={result.validation_status}, confidence={result.confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Birth certificate validation failed: {e}")
            result = BirthCertificateData()
            result.validation_status = "INVALID"
            result.issues.append(f"Validation error: {str(e)}")
            return result
    
    def _is_base64_image(self, content: str) -> bool:
        """Check if content is base64 encoded image"""
        return (content.startswith('data:image/') or 
                (len(content) > 100 and content.replace('+', '').replace('/', '').replace('=', '').isalnum()))
    
    async def _extract_birth_certificate_data(self, text: str, result: BirthCertificateData) -> BirthCertificateData:
        """Extract structured data from birth certificate text"""
        
        # Extract full name
        for pattern in self.name_patterns['full_name']:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                result.full_name = match.group(1).strip()
                break
        
        # Extract date of birth
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    date_str = match.group(1)
                    result.date_of_birth = self._parse_date(date_str)
                    break
                except:
                    continue
        
        # Extract place of birth
        for pattern in self.place_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                result.place_of_birth = match.group(1).strip()
                break
        
        # Extract parents' names
        for pattern in self.name_patterns['mother_name']:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                result.parents_names.append(f"Mother: {match.group(1).strip()}")
                break
        
        for pattern in self.name_patterns['father_name']:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                result.parents_names.append(f"Father: {match.group(1).strip()}")
                break
        
        # Extract registration information
        for pattern in self.registry_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                result.registration_number = match.group(1).strip()
                break
        
        # Detect country/registry office
        result.registry_office = self._detect_registry_office(text)
        result.country_issued = self._detect_country(text)
        
        return result
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string in various formats"""
        date_str = date_str.strip()
        
        # Common date formats
        formats = [
            '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y',
            '%d.%m.%Y', '%m.%d.%Y', '%Y-%m-%d',
            '%B %d, %Y', '%d %B %Y', '%b %d, %Y', '%d %b %Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        # Try month name parsing for Portuguese/Spanish/French
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
            'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
            'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        
        # Try parsing with month names
        for month_name, month_num in month_map.items():
            if month_name.lower() in date_str.lower():
                try:
                    # Extract day and year
                    numbers = re.findall(r'\d+', date_str)
                    if len(numbers) >= 2:
                        day = int(numbers[0])
                        year = int(numbers[-1])
                        return date(year, month_num, day)
                except:
                    continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _detect_registry_office(self, text: str) -> str:
        """Detect registry office from text"""
        office_patterns = [
            r'(?:cartório|notary|registry|registre|registro\s+civil)[:\s]+([A-Z][A-Za-z\s,\-]+)',
            r'(?:civil\s+registry|registro\s+civil\s+das\s+pessoas\s+naturais)[:\s]+([A-Z][A-Za-z\s,\-]+)',
            r'(?:issued\s+by|emitido\s+por)[:\s]+([A-Z][A-Za-z\s,\-]+)',
        ]
        
        for pattern in office_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _detect_country(self, text: str) -> str:
        """Detect issuing country from text"""
        # Common country indicators
        country_indicators = {
            'brazil': ['brasil', 'brazil', 'república federativa do brasil', 'rfd'],
            'usa': ['united states', 'usa', 'us', 'america'],
            'portugal': ['portugal', 'república portuguesa'],
            'spain': ['españa', 'spain', 'reino de españa'],
            'france': ['france', 'république française'],
            'italy': ['italia', 'italy', 'repubblica italiana'],
            'argentina': ['argentina', 'república argentina'],
            'colombia': ['colombia', 'república de colombia'],
            'mexico': ['méxico', 'mexico', 'estados unidos mexicanos']
        }
        
        text_lower = text.lower()
        
        for country, indicators in country_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    return country.upper()
        
        return ""
    
    def _validate_extracted_data(self, result: BirthCertificateData) -> Dict[str, Any]:
        """Validate extracted birth certificate data"""
        issues = []
        
        # Check required fields
        if not result.full_name:
            issues.append("Full name not found")
        elif len(result.full_name) < 3:
            issues.append("Full name appears incomplete")
        
        if not result.date_of_birth:
            issues.append("Date of birth not found")
        else:
            # Validate date of birth is reasonable
            today = date.today()
            if result.date_of_birth > today:
                issues.append("Date of birth is in the future")
            elif result.date_of_birth < date(1900, 1, 1):
                issues.append("Date of birth is unreasonably old")
        
        if not result.place_of_birth:
            issues.append("Place of birth not found")
        
        if not result.parents_names:
            issues.append("Parents' names not found")
        
        if not result.registration_number:
            issues.append("Registration number not found")
        
        # Determine status
        critical_issues = len([i for i in issues if 'not found' in i])
        
        if critical_issues == 0:
            status = "VALID"
        elif critical_issues <= 2:
            status = "SUSPICIOUS"
        else:
            status = "INVALID"
        
        return {
            'status': status,
            'issues': issues,
            'critical_issues_count': critical_issues
        }
    
    def _calculate_confidence(self, result: BirthCertificateData, base_confidence: float) -> float:
        """Calculate overall confidence score"""
        confidence = base_confidence * 0.4  # Base OCR confidence (40%)
        
        # Data completeness (40%)
        completeness_score = 0.0
        if result.full_name:
            completeness_score += 0.15
        if result.date_of_birth:
            completeness_score += 0.10
        if result.place_of_birth:
            completeness_score += 0.05
        if result.parents_names:
            completeness_score += 0.05
        if result.registration_number:
            completeness_score += 0.05
        
        confidence += completeness_score
        
        # Validation status (20%)
        status_scores = {'VALID': 0.2, 'SUSPICIOUS': 0.1, 'INVALID': 0.0}
        confidence += status_scores.get(result.validation_status, 0.0)
        
        return min(confidence, 1.0)

class BirthCertificateValidationStage(PipelineStage):
    """
    Pipeline stage for birth certificate validation
    """
    
    def __init__(self):
        super().__init__("birth_certificate_validation", enabled=True)
        self.validator = BirthCertificateValidator()
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process birth certificate validation"""
        try:
            # Only process if document is classified as birth certificate
            if context.document_type.lower() not in ['birth_certificate', 'birth_cert', 'certidao_nascimento']:
                logger.info(f"Skipping birth certificate validation for document type: {context.document_type}")
                return context
            
            # Validate birth certificate
            result = await self.validator.validate_birth_certificate(
                context.content_base64,
                context.document_type,
                language_hint="auto"
            )
            
            # Add results to context
            context.validation_results['birth_certificate'] = {
                'full_name': result.full_name,
                'date_of_birth': result.date_of_birth.isoformat() if result.date_of_birth else None,
                'place_of_birth': result.place_of_birth,
                'parents_names': result.parents_names,
                'registration_number': result.registration_number,
                'registry_office': result.registry_office,
                'country_issued': result.country_issued,
                'language': result.language,
                'confidence_score': result.confidence_score,
                'validation_status': result.validation_status,
                'issues': result.issues
            }
            
            # Update overall confidence
            if result.confidence_score > context.final_confidence:
                context.final_confidence = result.confidence_score
            
            # Update verdict based on validation
            if result.validation_status == "VALID":
                context.final_verdict = "APROVADO"
            elif result.validation_status == "SUSPICIOUS":
                context.final_verdict = "NECESSITA_REVISÃO"
            else:
                context.final_verdict = "REJEITADO"
                context.errors.extend(result.issues)
            
            logger.info(f"Birth certificate validation completed: {result.validation_status}, confidence: {result.confidence_score:.2f}")
            
            return context
            
        except Exception as e:
            error_msg = f"Birth certificate validation stage failed: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            return context

# Global instances
birth_certificate_validator = BirthCertificateValidator()
birth_certificate_validation_stage = BirthCertificateValidationStage()