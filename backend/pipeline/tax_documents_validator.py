"""
Tax Documents Validator - Specific Document Validator  
Validador especializado para documentos fiscais (W-2, 1040, 1099, etc)
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
class TaxDocumentData:
    """Structured data from tax documents"""
    # Document Information
    document_type: str = ""  # W-2, 1040, 1099-MISC, etc.
    tax_year: Optional[int] = None
    
    # Personal Information
    taxpayer_name: str = ""
    spouse_name: str = ""
    social_security_number: str = ""
    spouse_ssn: str = ""
    address: str = ""
    
    # Financial Information
    total_income: Optional[float] = None
    wages: Optional[float] = None
    federal_withholding: Optional[float] = None
    state_withholding: Optional[float] = None
    taxable_income: Optional[float] = None
    
    # Employer Information (for W-2)
    employer_name: str = ""
    employer_ein: str = ""
    employer_address: str = ""
    
    # Form-specific fields
    form_fields: Dict[str, Any] = None
    
    # Validation
    confidence_score: float = 0.0
    validation_status: str = "PENDING"  # VALID, INVALID, SUSPICIOUS
    issues: List[str] = None
    
    def __post_init__(self):
        if self.form_fields is None:
            self.form_fields = {}
        if self.issues is None:
            self.issues = []

class TaxDocumentsValidator:
    """
    Specialized validator for tax documents (W-2, 1040, 1099 series, etc.)
    Handles multiple tax form types and validates financial data
    """
    
    def __init__(self):
        # Tax document type patterns
        self.document_type_patterns = {
            'w2': [
                r'form\s+w-?2',
                r'wage\s+and\s+tax\s+statement',
                r'declaração\s+de\s+salários\s+e\s+impostos'
            ],
            '1040': [
                r'form\s+10-?40',
                r'u\.?s\.?\s+individual\s+income\s+tax\s+return',
                r'declaração\s+de\s+imposto\s+de\s+renda\s+individual'
            ],
            '1099': [
                r'form\s+10-?99',
                r'miscellaneous\s+income',
                r'renda\s+diversa'
            ],
            'schedule_c': [
                r'schedule\s+c',
                r'profit\s+or\s+loss\s+from\s+business'
            ],
            'state_tax': [
                r'state\s+tax\s+return',
                r'resident\s+income\s+tax\s+return'
            ]
        }
        
        # Common tax document patterns
        self.patterns = {
            'tax_year': [
                r'(?:tax\s+year|ano\s+fiscal)[:\s]*(\d{4})',
                r'(?:for\s+calendar\s+year|para\s+o\s+ano\s+civil)[:\s]*(\d{4})',
                r'(\d{4})\s*(?:tax\s+return|declaração)',
                r'form\s+\w+.*?(\d{4})',  # Extract year from form header
            ],
            'taxpayer_name': [
                r'(?:name|nome)[:\s]*([A-Z][A-Za-z\s\-\']{3,50})',
                r'(?:taxpayer|contribuinte)[:\s]*([A-Z][A-Za-z\s\-\']{3,50})',
                r'(?:first\s+name|nome)[:\s]*([A-Z][A-Za-z\s\-\']{3,50})',
                r'(?:last\s+name|sobrenome)[:\s]*([A-Z][A-Za-z\s\-\']{3,50})',
            ],
            'ssn': [
                r'(?:social\s+security\s+number|ssn|número\s+ssn)[:\s]*(\d{3}[-\s]?\d{2}[-\s]?\d{4})',
                r'(?:your\s+social\s+security\s+number)[:\s]*(\d{3}[-\s]?\d{2}[-\s]?\d{4})',
                r'(\d{3}[-\s]\d{2}[-\s]\d{4})',
            ],
            'address': [
                r'(?:home\s+address|endereço)[:\s]*([A-Za-z0-9\s,\-\.#]{10,80})',
                r'(?:mailing\s+address)[:\s]*([A-Za-z0-9\s,\-\.#]{10,80})',
            ],
            'wages': [
                r'(?:wages|salários|federal\s+wages)[:\s]*\$?([0-9,]+\.?\d{0,2})',
                r'(?:box\s+1|caixa\s+1)[:\s]*\$?([0-9,]+\.?\d{0,2})',
                r'(?:total\s+wages)[:\s]*\$?([0-9,]+\.?\d{0,2})',
            ],
            'federal_withholding': [
                r'(?:federal\s+income\s+tax\s+withheld|imposto\s+federal\s+retido)[:\s]*\$?([0-9,]+\.?\d{0,2})',
                r'(?:box\s+2|caixa\s+2)[:\s]*\$?([0-9,]+\.?\d{0,2})',
            ],
            'state_withholding': [
                r'(?:state\s+income\s+tax|imposto\s+estadual)[:\s]*\$?([0-9,]+\.?\d{0,2})',
                r'(?:state\s+tax\s+withheld)[:\s]*\$?([0-9,]+\.?\d{0,2})',
            ],
            'employer_name': [
                r'(?:employer|empregador)[:\s]*([A-Z][A-Za-z0-9\s,\-\.&]{3,60})',
                r'(?:company\s+name|nome\s+da\s+empresa)[:\s]*([A-Z][A-Za-z0-9\s,\-\.&]{3,60})',
                r'(?:payer|pagador)[:\s]*([A-Z][A-Za-z0-9\s,\-\.&]{3,60})',
            ],
            'employer_ein': [
                r'(?:employer\s+identification\s+number|ein)[:\s]*(\d{2}[-\s]?\d{7})',
                r'(?:federal\s+id)[:\s]*(\d{2}[-\s]?\d{7})',
                r'(\d{2}[-\s]\d{7})',  # EIN format
            ],
            'total_income': [
                r'(?:total\s+income|renda\s+total)[:\s]*\$?([0-9,]+\.?\d{0,2})',
                r'(?:adjusted\s+gross\s+income|agi)[:\s]*\$?([0-9,]+\.?\d{0,2})',
            ],
            'taxable_income': [
                r'(?:taxable\s+income|renda\s+tributável)[:\s]*\$?([0-9,]+\.?\d{0,2})',
                r'(?:line\s+\d+.*taxable)[:\s]*\$?([0-9,]+\.?\d{0,2})',
            ]
        }
        
        # Valid tax years (reasonable range)
        self.valid_tax_years = list(range(2010, datetime.now().year + 2))
        
        # Common tax document indicators
        self.tax_indicators = [
            'internal revenue service', 'irs', 'tax return', 'w-2', 'form 1040',
            'income tax', 'tax year', 'adjusted gross income', 'federal withholding',
            'social security', 'medicare', 'employer identification number'
        ]
    
    async def validate_tax_document(self, 
                                   document_content: str,
                                   document_type: str = "tax_document") -> TaxDocumentData:
        """
        Validate and extract data from tax document
        
        Args:
            document_content: Base64 image or text content
            document_type: Document type identifier
        
        Returns:
            TaxDocumentData with extracted and validated information
        """
        try:
            result = TaxDocumentData()
            
            # 1. Extract text if image provided
            if self._is_base64_image(document_content):
                ocr_result = await real_ocr_engine.extract_text_from_image(
                    document_content, 
                    mode="document",
                    language="eng"  # Tax documents typically in English
                )
                text_content = ocr_result.text
                base_confidence = ocr_result.confidence
            else:
                text_content = document_content
                base_confidence = 0.9
            
            # 2. Verify this is actually a tax document
            if not self._verify_tax_document(text_content):
                result.validation_status = "INVALID"
                result.issues.append("Document does not appear to be a tax document")
                return result
            
            # 3. Identify specific tax document type
            result.document_type = self._identify_tax_document_type(text_content)
            
            # 4. Extract structured data
            result = await self._extract_tax_data(text_content, result)
            
            # 5. Validate extracted data
            validation_result = self._validate_tax_data(result)
            result.validation_status = validation_result['status']
            result.issues.extend(validation_result['issues'])
            
            # 6. Calculate confidence score
            result.confidence_score = self._calculate_confidence(result, base_confidence)
            
            logger.info(f"Tax document validation completed: type={result.document_type}, status={result.validation_status}, confidence={result.confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Tax document validation failed: {e}")
            result = TaxDocumentData()
            result.validation_status = "INVALID"
            result.issues.append(f"Validation error: {str(e)}")
            return result
    
    def _is_base64_image(self, content: str) -> bool:
        """Check if content is base64 encoded image"""
        return (content.startswith('data:image/') or 
                (len(content) > 100 and content.replace('+', '').replace('/', '').replace('=', '').isalnum()))
    
    def _verify_tax_document(self, text: str) -> bool:
        """Verify this is a tax document"""
        text_lower = text.lower()
        
        found_indicators = sum(1 for indicator in self.tax_indicators 
                             if indicator in text_lower)
        
        # Also check for specific form patterns
        form_pattern_found = any(
            any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
            for patterns in self.document_type_patterns.values()
        )
        
        return found_indicators >= 2 or form_pattern_found
    
    def _identify_tax_document_type(self, text: str) -> str:
        """Identify specific type of tax document"""
        text_lower = text.lower()
        
        for doc_type, patterns in self.document_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return doc_type.upper()
        
        # Default classification based on content
        if 'wage' in text_lower and ('w-2' in text_lower or 'w2' in text_lower):
            return "W-2"
        elif '1040' in text_lower or 'individual income tax' in text_lower:
            return "1040"
        elif '1099' in text_lower:
            return "1099"
        else:
            return "UNKNOWN_TAX_FORM"
    
    async def _extract_tax_data(self, text: str, result: TaxDocumentData) -> TaxDocumentData:
        """Extract structured data from tax document text"""
        
        # Extract tax year
        for pattern in self.patterns['tax_year']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    year = int(match.group(1))
                    if year in self.valid_tax_years:
                        result.tax_year = year
                        break
                except ValueError:
                    continue
        
        # Extract taxpayer name
        names_found = []
        for pattern in self.patterns['taxpayer_name']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            names_found.extend(matches)
        
        # Filter valid names
        valid_names = [name.strip() for name in names_found 
                      if len(name.strip()) > 2 and not any(char.isdigit() for char in name)]
        
        if valid_names:
            # Use the longest name found
            result.taxpayer_name = max(valid_names, key=len)
        
        # Extract SSN
        for pattern in self.patterns['ssn']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ssn_raw = match.group(1)
                ssn_clean = re.sub(r'[-\s]', '', ssn_raw)
                if len(ssn_clean) == 9 and ssn_clean.isdigit():
                    result.social_security_number = f"{ssn_clean[:3]}-{ssn_clean[3:5]}-{ssn_clean[5:9]}"
                    break
        
        # Extract address
        for pattern in self.patterns['address']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.address = match.group(1).strip()
                break
        
        # Extract financial information
        financial_fields = {
            'wages': 'wages',
            'federal_withholding': 'federal_withholding', 
            'state_withholding': 'state_withholding',
            'total_income': 'total_income',
            'taxable_income': 'taxable_income'
        }
        
        for field_name, result_attr in financial_fields.items():
            for pattern in self.patterns[field_name]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        amount_str = match.group(1).replace(',', '')
                        amount = float(amount_str)
                        setattr(result, result_attr, amount)
                        break
                    except ValueError:
                        continue
        
        # Extract employer information (for W-2 and similar forms)
        if result.document_type in ['W-2', 'W2']:
            # Employer name
            for pattern in self.patterns['employer_name']:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    result.employer_name = match.group(1).strip()
                    break
            
            # Employer EIN
            for pattern in self.patterns['employer_ein']:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    ein_raw = match.group(1)
                    ein_clean = re.sub(r'[-\s]', '', ein_raw)
                    if len(ein_clean) == 9 and ein_clean.isdigit():
                        result.employer_ein = f"{ein_clean[:2]}-{ein_clean[2:]}"
                    break
        
        return result
    
    def _validate_tax_data(self, result: TaxDocumentData) -> Dict[str, Any]:
        """Validate extracted tax document data"""
        issues = []
        
        # Check required fields
        if not result.document_type or result.document_type == "UNKNOWN_TAX_FORM":
            issues.append("Could not identify tax document type")
        
        if not result.tax_year:
            issues.append("Tax year not found")
        elif result.tax_year not in self.valid_tax_years:
            issues.append(f"Invalid tax year: {result.tax_year}")
        
        if not result.taxpayer_name:
            issues.append("Taxpayer name not found")
        elif len(result.taxpayer_name) < 3:
            issues.append("Taxpayer name appears incomplete")
        
        if not result.social_security_number:
            issues.append("Social Security Number not found")
        else:
            # Validate SSN format
            ssn_clean = result.social_security_number.replace('-', '')
            if len(ssn_clean) != 9 or not ssn_clean.isdigit():
                issues.append("Invalid SSN format")
        
        # Validate financial amounts
        financial_fields = [result.wages, result.total_income, result.taxable_income, 
                          result.federal_withholding, result.state_withholding]
        
        valid_amounts = [amount for amount in financial_fields if amount is not None]
        
        if not valid_amounts:
            issues.append("No financial information found")
        else:
            # Check for negative amounts (except withholding which could be refunds)
            for amount in valid_amounts:
                if amount < 0 and amount not in [result.federal_withholding, result.state_withholding]:
                    issues.append(f"Negative income amount found: ${amount}")
        
        # Document type specific validation
        if result.document_type == "W-2":
            if not result.employer_name:
                issues.append("Employer name not found in W-2")
            if not result.employer_ein:
                issues.append("Employer EIN not found in W-2")
            if result.wages is None:
                issues.append("Wage information not found in W-2")
        
        # Check year consistency
        current_year = datetime.now().year
        if result.tax_year and result.tax_year > current_year:
            issues.append("Tax year is in the future")
        
        # Determine status
        critical_issues = len([i for i in issues if any(word in i.lower() 
                              for word in ['not found', 'invalid', 'negative'])])
        
        if critical_issues == 0:
            status = "VALID"
        elif critical_issues <= 3:
            status = "SUSPICIOUS" 
        else:
            status = "INVALID"
        
        return {
            'status': status,
            'issues': issues,
            'critical_issues_count': critical_issues
        }
    
    def _calculate_confidence(self, result: TaxDocumentData, base_confidence: float) -> float:
        """Calculate overall confidence score"""
        confidence = base_confidence * 0.25  # Base OCR confidence (25%)
        
        # Document identification (20%)
        if result.document_type and result.document_type != "UNKNOWN_TAX_FORM":
            confidence += 0.20
        elif result.document_type:
            confidence += 0.10
        
        # Required fields (35%)
        field_score = 0.0
        if result.taxpayer_name:
            field_score += 0.10
        if result.social_security_number:
            field_score += 0.10
        if result.tax_year:
            field_score += 0.08
        if any([result.wages, result.total_income, result.taxable_income]):
            field_score += 0.07
        
        confidence += field_score
        
        # Document type specific fields (10%)
        if result.document_type == "W-2":
            if result.employer_name and result.employer_ein:
                confidence += 0.10
            elif result.employer_name or result.employer_ein:
                confidence += 0.05
        
        # Validation status (10%)
        status_scores = {'VALID': 0.10, 'SUSPICIOUS': 0.05, 'INVALID': 0.0}
        confidence += status_scores.get(result.validation_status, 0.0)
        
        return min(confidence, 1.0)

class TaxDocumentsValidationStage(PipelineStage):
    """
    Pipeline stage for tax documents validation
    """
    
    def __init__(self):
        super().__init__("tax_documents_validation", enabled=True)
        self.validator = TaxDocumentsValidator()
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process tax document validation"""
        try:
            # Only process if document is classified as tax document
            if context.document_type.lower() not in ['tax_document', 'w2', 'w-2', '1040', '1099', 'tax_return', 'documento_fiscal']:
                logger.info(f"Skipping tax document validation for document type: {context.document_type}")
                return context
            
            # Validate tax document
            result = await self.validator.validate_tax_document(
                context.content_base64,
                context.document_type
            )
            
            # Add results to context
            context.validation_results['tax_document'] = {
                'document_type': result.document_type,
                'tax_year': result.tax_year,
                'taxpayer_name': result.taxpayer_name,
                'spouse_name': result.spouse_name,
                'social_security_number': result.social_security_number,
                'spouse_ssn': result.spouse_ssn,
                'address': result.address,
                'total_income': result.total_income,
                'wages': result.wages,
                'federal_withholding': result.federal_withholding,
                'state_withholding': result.state_withholding,
                'taxable_income': result.taxable_income,
                'employer_name': result.employer_name,
                'employer_ein': result.employer_ein,
                'employer_address': result.employer_address,
                'form_fields': result.form_fields,
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
            
            logger.info(f"Tax document validation completed: {result.validation_status}, confidence: {result.confidence_score:.2f}")
            
            return context
            
        except Exception as e:
            error_msg = f"Tax document validation stage failed: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            return context

# Global instances
tax_documents_validator = TaxDocumentsValidator()
tax_documents_validation_stage = TaxDocumentsValidationStage()