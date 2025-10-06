"""
I-765 Employment Authorization Document Validator
Validador especializado para documentos I-765 (EAD)
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
class I765Data:
    """Structured data from I-765 Employment Authorization Document"""
    # Personal Information
    full_name: str = ""
    alien_number: str = ""
    uscis_account_number: str = ""
    date_of_birth: Optional[date] = None
    country_of_birth: str = ""
    
    # Document Information
    document_number: str = ""
    category: str = ""
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    
    # Employment Authorization
    work_authorized: bool = False
    restrictions: str = ""
    
    # Validation
    confidence_score: float = 0.0
    validation_status: str = "PENDING"
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []

class I765Validator:
    """
    Specialized validator for I-765 Employment Authorization Documents
    """
    
    def __init__(self):
        # I-765 specific patterns
        self.patterns = {
            'document_title': [
                r'employment\s+authorization\s+document',
                r'documento\s+de\s+autorização\s+de\s+trabalho',
                r'i-765',
                r'ead'
            ],
            'alien_number': [
                r'(?:alien\s+registration\s+number|a\s*#|uscis\s*#)[:\s]*([a-z]?\d{8,9})',
                r'(?:número\s+de\s+registro\s+de\s+estrangeiro)[:\s]*([a-z]?\d{8,9})',
                r'a\s*-?\s*(\d{8,9})',
            ],
            'document_number': [
                r'(?:card\s+number|número\s+do\s+cartão)[:\s]*([a-z]{3}\d{10})',
                r'(?:document\s+number)[:\s]*([a-z0-9\-]+)',
                r'(?:ead\s+number)[:\s]*([a-z0-9\-]+)',
            ],
            'uscis_number': [
                r'(?:uscis\s+account\s+number)[:\s]*([a-z0-9\-]+)',
                r'(?:receipt\s+number)[:\s]*([a-z]{3}\d{10})',
            ],
            'category': [
                r'(?:category|categoria)[:\s]*([a-z0-9\(\)]+)',
                r'(?:class\s+of\s+admission)[:\s]*([a-z0-9\(\)]+)',
                r'(?:based\s+on)[:\s]*([a-z0-9\(\)\s]+)',
            ],
            'validity_dates': [
                r'(?:valid\s+from|válido\s+de)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:card\s+expires|expira\s+em)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:not\s+valid\s+after|não\s+válido\s+após)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
            ],
            'restrictions': [
                r'(?:employment\s+authorized)[:\s]*(.{0,50})',
                r'(?:valid\s+for\s+work\s+only\s+with\s+dhs\s+authorization)',
                r'(?:not\s+valid\s+for\s+reentry\s+to\s+u\.?s\.?)',
            ]
        }
        
        # Common I-765 categories
        self.valid_categories = {
            'A05': 'Asylum applicant',
            'A07': 'N-648 applicant',  
            'A08': 'Asylum grantee',
            'A09': 'Adjustment of status applicant',
            'A10': 'Adjustment of status applicant',
            'C03A': 'F-1 student - Optional Practical Training',
            'C03B': 'F-1 student - STEM Extension',
            'C03C': 'F-1 student - Cap-gap extension',
            'C05': 'M-1 student - Practical training',
            'C08': 'Asylum applicant',
            'C09': 'Adjustment of status applicant (spouse/child)',
            'C10': 'Withholding of removal',
            'C14': 'Deferred Action for Childhood Arrivals (DACA)',
            'C31': 'TPS beneficiary',
            'C33': 'Spouse of E-1/E-2 treaty trader/investor',
        }
    
    async def validate_i765_document(self, 
                                   document_content: str,
                                   document_type: str = "i765_ead") -> I765Data:
        """
        Validate and extract data from I-765 Employment Authorization Document
        
        Args:
            document_content: Base64 image or text content
            document_type: Document type identifier
        
        Returns:
            I765Data with extracted and validated information
        """
        try:
            result = I765Data()
            
            # 1. Extract text if image provided
            if self._is_base64_image(document_content):
                ocr_result = await real_ocr_engine.extract_text_from_image(
                    document_content, 
                    mode="document",
                    language="eng"  # I-765 is always in English
                )
                text_content = ocr_result.text
                base_confidence = ocr_result.confidence
            else:
                text_content = document_content
                base_confidence = 0.9
            
            # 2. Verify this is actually an I-765 document
            if not self._verify_i765_document(text_content):
                result.validation_status = "INVALID"
                result.issues.append("Document does not appear to be an I-765 Employment Authorization Document")
                return result
            
            # 3. Extract structured data
            result = await self._extract_i765_data(text_content, result)
            
            # 4. Validate extracted data
            validation_result = self._validate_i765_data(result)
            result.validation_status = validation_result['status']
            result.issues.extend(validation_result['issues'])
            
            # 5. Calculate confidence score
            result.confidence_score = self._calculate_confidence(result, base_confidence)
            
            logger.info(f"I-765 validation completed: status={result.validation_status}, confidence={result.confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"I-765 validation failed: {e}")
            result = I765Data()
            result.validation_status = "INVALID"
            result.issues.append(f"Validation error: {str(e)}")
            return result
    
    def _is_base64_image(self, content: str) -> bool:
        """Check if content is base64 encoded image"""
        return (content.startswith('data:image/') or 
                (len(content) > 100 and content.replace('+', '').replace('/', '').replace('=', '').isalnum()))
    
    def _verify_i765_document(self, text: str) -> bool:
        """Verify this is an I-765 document"""
        text_lower = text.lower()
        
        # Check for I-765 indicators
        i765_indicators = [
            'employment authorization document',
            'i-765',
            'ead',
            'work authorization',
            'department of homeland security',
            'u.s. citizenship and immigration services',
            'uscis'
        ]
        
        found_indicators = sum(1 for indicator in i765_indicators if indicator in text_lower)
        return found_indicators >= 2
    
    async def _extract_i765_data(self, text: str, result: I765Data) -> I765Data:
        """Extract structured data from I-765 text"""
        
        # Extract alien registration number
        for pattern in self.patterns['alien_number']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                alien_num = match.group(1).upper().replace('-', '')
                if alien_num.startswith('A'):
                    result.alien_number = alien_num
                else:
                    result.alien_number = f"A{alien_num}"
                break
        
        # Extract document number
        for pattern in self.patterns['document_number']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.document_number = match.group(1).upper()
                break
        
        # Extract USCIS number
        for pattern in self.patterns['uscis_number']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.uscis_account_number = match.group(1).upper()
                break
        
        # Extract category
        for pattern in self.patterns['category']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                category = match.group(1).upper().replace('(', '').replace(')', '')
                if category in self.valid_categories:
                    result.category = category
                break
        
        # Extract validity dates
        date_matches = []
        for pattern in self.patterns['validity_dates']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            date_matches.extend(matches)
        
        # Parse dates
        parsed_dates = []
        for date_str in date_matches:
            try:
                parsed_date = self._parse_date(date_str)
                parsed_dates.append(parsed_date)
            except:
                continue
        
        # Assign dates (earliest is valid_from, latest is valid_until)
        if len(parsed_dates) >= 2:
            parsed_dates.sort()
            result.valid_from = parsed_dates[0]
            result.valid_until = parsed_dates[-1]
        elif len(parsed_dates) == 1:
            # Assume it's the expiration date
            result.valid_until = parsed_dates[0]
        
        # Extract restrictions/employment authorization
        for pattern in self.patterns['restrictions']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'authorized' in match.group(0).lower():
                    result.work_authorized = True
                if match.groups():
                    result.restrictions = match.group(1).strip()
                break
        
        # Extract personal information (name, DOB, country)
        result = self._extract_personal_info(text, result)
        
        return result
    
    def _extract_personal_info(self, text: str, result: I765Data) -> I765Data:
        """Extract personal information from I-765"""
        
        # Name patterns (usually appears near the top)
        name_patterns = [
            r'(?:name|nome)[:\s]+([A-Z][A-Za-z\s,]+)',
            r'(?:surname|last\s+name)[:\s]+([A-Z][A-Za-z\s]+)',
            r'(?:given\s+name|first\s+name)[:\s]+([A-Z][A-Za-z\s]+)',
        ]
        
        names_found = []
        for pattern in name_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            names_found.extend(matches)
        
        if names_found:
            # Combine names or use longest one
            result.full_name = max(names_found, key=len).strip()
        
        # Date of birth patterns
        dob_patterns = [
            r'(?:date\s+of\s+birth|born|dob)[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
            r'(?:birth\s+date|data\s+de\s+nascimento)[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
        ]
        
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result.date_of_birth = self._parse_date(match.group(1))
                    break
                except:
                    continue
        
        # Country of birth
        country_patterns = [
            r'(?:country\s+of\s+birth|lugar\s+de\s+nascimento)[:\s]+([A-Z][A-Za-z\s]+)',
            r'(?:born\s+in)[:\s]+([A-Z][A-Za-z\s]+)',
        ]
        
        for pattern in country_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.country_of_birth = match.group(1).strip()
                break
        
        return result
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string in MM/DD/YYYY or DD/MM/YYYY format"""
        date_str = date_str.strip()
        
        # Try MM/DD/YYYY first (US format)
        formats = ['%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _validate_i765_data(self, result: I765Data) -> Dict[str, Any]:
        """Validate extracted I-765 data"""
        issues = []
        
        # Check required fields
        if not result.alien_number:
            issues.append("Alien registration number (A-Number) not found")
        elif not re.match(r'^A\d{8,9}$', result.alien_number):
            issues.append("Alien registration number format is invalid")
        
        if not result.document_number:
            issues.append("Document number not found")
        
        if not result.category:
            issues.append("Category not found or invalid")
        elif result.category not in self.valid_categories:
            issues.append(f"Unknown category: {result.category}")
        
        # Check validity dates
        if result.valid_until:
            today = date.today()
            if result.valid_until < today:
                issues.append("Document has expired")
            elif result.valid_until < today.replace(year=today.year + 1):
                issues.append("Document expires within 1 year")
        else:
            issues.append("Expiration date not found")
        
        if result.valid_from and result.valid_until:
            if result.valid_from > result.valid_until:
                issues.append("Valid from date is after expiration date")
        
        # Check personal information
        if not result.full_name:
            issues.append("Full name not found")
        
        if not result.date_of_birth:
            issues.append("Date of birth not found")
        elif result.date_of_birth > date.today():
            issues.append("Date of birth is in the future")
        
        # Determine status
        critical_issues = len([i for i in issues if any(word in i.lower() for word in ['not found', 'invalid', 'expired'])])
        
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
    
    def _calculate_confidence(self, result: I765Data, base_confidence: float) -> float:
        """Calculate overall confidence score"""
        confidence = base_confidence * 0.3  # Base OCR confidence (30%)
        
        # Required fields (50%)
        field_score = 0.0
        if result.alien_number and re.match(r'^A\d{8,9}$', result.alien_number):
            field_score += 0.15
        if result.document_number:
            field_score += 0.10
        if result.category and result.category in self.valid_categories:
            field_score += 0.10
        if result.valid_until:
            field_score += 0.10
        if result.full_name:
            field_score += 0.05
        
        confidence += field_score
        
        # Validation status (20%)
        status_scores = {'VALID': 0.2, 'SUSPICIOUS': 0.1, 'INVALID': 0.0}
        confidence += status_scores.get(result.validation_status, 0.0)
        
        return min(confidence, 1.0)

class I765ValidationStage(PipelineStage):
    """
    Pipeline stage for I-765 Employment Authorization Document validation
    """
    
    def __init__(self):
        super().__init__("i765_validation", enabled=True)
        self.validator = I765Validator()
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process I-765 document validation"""
        try:
            # Only process if document is classified as I-765
            if context.document_type.lower() not in ['i765', 'i-765', 'ead', 'employment_authorization']:
                logger.info(f"Skipping I-765 validation for document type: {context.document_type}")
                return context
            
            # Validate I-765 document
            result = await self.validator.validate_i765_document(
                context.content_base64,
                context.document_type
            )
            
            # Add results to context
            context.validation_results['i765_ead'] = {
                'full_name': result.full_name,
                'alien_number': result.alien_number,
                'uscis_account_number': result.uscis_account_number,
                'date_of_birth': result.date_of_birth.isoformat() if result.date_of_birth else None,
                'country_of_birth': result.country_of_birth,
                'document_number': result.document_number,
                'category': result.category,
                'category_description': self.validator.valid_categories.get(result.category, ''),
                'valid_from': result.valid_from.isoformat() if result.valid_from else None,
                'valid_until': result.valid_until.isoformat() if result.valid_until else None,
                'work_authorized': result.work_authorized,
                'restrictions': result.restrictions,
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
            
            logger.info(f"I-765 validation completed: {result.validation_status}, confidence: {result.confidence_score:.2f}")
            
            return context
            
        except Exception as e:
            error_msg = f"I-765 validation stage failed: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            return context

# Global instances
i765_validator = I765Validator()
i765_validation_stage = I765ValidationStage()