"""
Marriage Certificate Validator - Specific Document Validator
Validador especializado para certidões de casamento
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
class MarriageCertificateData:
    """Structured data from marriage certificate"""
    # Spouse Information
    spouse1_name: str = ""
    spouse2_name: str = ""
    spouse1_maiden_name: str = ""
    spouse2_maiden_name: str = ""
    
    # Marriage Details
    marriage_date: Optional[date] = None
    marriage_location: str = ""
    officiant_name: str = ""
    officiant_title: str = ""
    
    # Document Information
    certificate_number: str = ""
    registration_date: Optional[date] = None
    issuing_authority: str = ""
    state_issued: str = ""
    country_issued: str = ""
    
    # Witness Information
    witnesses: List[str] = None
    
    # Validation
    confidence_score: float = 0.0
    validation_status: str = "PENDING"
    issues: List[str] = None
    
    def __post_init__(self):
        if self.witnesses is None:
            self.witnesses = []
        if self.issues is None:
            self.issues = []

class MarriageCertificateValidator:
    """
    Specialized validator for marriage certificates
    Supports multiple languages and formats
    """
    
    def __init__(self):
        # Marriage certificate patterns
        self.patterns = {
            'spouse_names': [
                r'(?:bride|esposa|noiva)[:\s]+([A-Z][A-Za-z\s\-\']{2,40})',
                r'(?:groom|esposo|noivo)[:\s]+([A-Z][A-Za-z\s\-\']{2,40})',
                r'(?:spouse|cônjuge)[:\s]+([A-Z][A-Za-z\s\-\']{2,40})',
                r'(?:husband|marido)[:\s]+([A-Z][A-Za-z\s\-\']{2,40})',
                r'(?:wife|esposa)[:\s]+([A-Z][A-Za-z\s\-\']{2,40})',
            ],
            'maiden_names': [
                r'(?:maiden\s+name|nome\s+de\s+solteira)[:\s]+([A-Z][A-Za-z\s\-\']{2,30})',
                r'(?:formerly|anteriormente)[:\s]+([A-Z][A-Za-z\s\-\']{2,30})',
                r'(?:née|nascida)[:\s]+([A-Z][A-Za-z\s\-\']{2,30})',
            ],
            'marriage_date': [
                r'(?:married\s+on|casado\s+em|data\s+do\s+casamento)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:date\s+of\s+marriage|ceremony\s+date)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:on\s+the)[:\s]*(\d{1,2}(?:st|nd|rd|th)?\s+(?:day\s+of\s+)?[A-Za-z]+\s+\d{4})',
            ],
            'marriage_location': [
                r'(?:married\s+at|casado\s+em|local\s+do\s+casamento)[:\s]+([A-Z][A-Za-z0-9\s,\-\.]{5,80})',
                r'(?:ceremony\s+held\s+at|cerimônia\s+realizada\s+em)[:\s]+([A-Z][A-Za-z0-9\s,\-\.]{5,80})',
                r'(?:place\s+of\s+marriage|local)[:\s]+([A-Z][A-Za-z0-9\s,\-\.]{5,80})',
            ],
            'officiant': [
                r'(?:officiant|celebrante|oficiante)[:\s]+([A-Z][A-Za-z\s\-\'\.]{5,50})',
                r'(?:performed\s+by|celebrado\s+por)[:\s]+([A-Z][A-Za-z\s\-\'\.]{5,50})',
                r'(?:minister|pastor|judge|juiz)[:\s]+([A-Z][A-Za-z\s\-\'\.]{5,50})',
            ],
            'certificate_number': [
                r'(?:certificate\s+number|número\s+da\s+certidão)[:\s#]*([A-Z0-9\-]{4,20})',
                r'(?:registration\s+number|número\s+de\s+registro)[:\s#]*([A-Z0-9\-]{4,20})',
                r'(?:license\s+number)[:\s#]*([A-Z0-9\-]{4,20})',
            ],
            'registration_date': [
                r'(?:registered\s+on|registrado\s+em)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:filed\s+on|arquivado\s+em)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
            ],
            'witnesses': [
                r'(?:witness|testemunha)[:\s]+([A-Z][A-Za-z\s\-\']{3,40})',
                r'(?:witnessed\s+by|testemunhado\s+por)[:\s]+([A-Z][A-Za-z\s\-\']{3,40})',
            ],
            'issuing_authority': [
                r'(?:issued\s+by|emitido\s+por)[:\s]+([A-Z][A-Za-z\s\-,\.]{5,60})',
                r'(?:registrar|oficial\s+de\s+registro)[:\s]+([A-Z][A-Za-z\s\-,\.]{5,60})',
                r'(?:clerk|escrivão)[:\s]+([A-Z][A-Za-z\s\-,\.]{5,60})',
            ]
        }
        
        # Common marriage certificate indicators
        self.certificate_indicators = [
            'marriage certificate', 'certificate of marriage', 'certidão de casamento',
            'matrimony', 'matrimônio', 'wedding certificate', 'union certificate',
            'civil marriage', 'casamento civil', 'religious marriage'
        ]
        
        # US States and countries
        self.us_states = {
            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
            'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
            'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
            'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
            'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
            'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
            'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
            'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
            'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
            'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
            'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
            'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
        }
    
    async def validate_marriage_certificate(self, 
                                          document_content: str,
                                          document_type: str = "marriage_certificate") -> MarriageCertificateData:
        """
        Validate and extract data from marriage certificate
        
        Args:
            document_content: Base64 image or text content
            document_type: Document type identifier
        
        Returns:
            MarriageCertificateData with extracted and validated information
        """
        try:
            result = MarriageCertificateData()
            
            # 1. Extract text if image provided
            if self._is_base64_image(document_content):
                ocr_result = await real_ocr_engine.extract_text_from_image(
                    document_content, 
                    mode="document",
                    language="auto"
                )
                text_content = ocr_result.text
                base_confidence = ocr_result.confidence
            else:
                text_content = document_content
                base_confidence = 0.9
            
            # 2. Verify this is actually a marriage certificate
            if not self._verify_marriage_certificate(text_content):
                result.validation_status = "INVALID"
                result.issues.append("Document does not appear to be a marriage certificate")
                return result
            
            # 3. Extract structured data
            result = await self._extract_marriage_data(text_content, result)
            
            # 4. Validate extracted data
            validation_result = self._validate_marriage_data(result)
            result.validation_status = validation_result['status']
            result.issues.extend(validation_result['issues'])
            
            # 5. Calculate confidence score
            result.confidence_score = self._calculate_confidence(result, base_confidence)
            
            logger.info(f"Marriage certificate validation completed: status={result.validation_status}, confidence={result.confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Marriage certificate validation failed: {e}")
            result = MarriageCertificateData()
            result.validation_status = "INVALID"
            result.issues.append(f"Validation error: {str(e)}")
            return result
    
    def _is_base64_image(self, content: str) -> bool:
        """Check if content is base64 encoded image"""
        return (content.startswith('data:image/') or 
                (len(content) > 100 and content.replace('+', '').replace('/', '').replace('=', '').isalnum()))
    
    def _verify_marriage_certificate(self, text: str) -> bool:
        """Verify this is a marriage certificate document"""
        text_lower = text.lower()
        
        found_indicators = sum(1 for indicator in self.certificate_indicators 
                             if indicator in text_lower)
        
        # Also check for key marriage-related terms
        marriage_terms = ['bride', 'groom', 'spouse', 'married', 'matrimony', 'wedding', 'union']
        marriage_term_count = sum(1 for term in marriage_terms if term in text_lower)
        
        return found_indicators >= 1 or marriage_term_count >= 2
    
    async def _extract_marriage_data(self, text: str, result: MarriageCertificateData) -> MarriageCertificateData:
        """Extract structured data from marriage certificate text"""
        
        # Extract spouse names
        spouse_names = []
        for pattern in self.patterns['spouse_names']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            spouse_names.extend(matches)
        
        # Clean and assign spouse names
        unique_names = list(set([name.strip() for name in spouse_names if len(name.strip()) > 2]))
        if len(unique_names) >= 2:
            result.spouse1_name = unique_names[0]
            result.spouse2_name = unique_names[1]
        elif len(unique_names) == 1:
            result.spouse1_name = unique_names[0]
        
        # Extract maiden names
        for pattern in self.patterns['maiden_names']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if not result.spouse1_maiden_name:
                    result.spouse1_maiden_name = match.strip()
                elif not result.spouse2_maiden_name:
                    result.spouse2_maiden_name = match.strip()
                    break
        
        # Extract marriage date
        for pattern in self.patterns['marriage_date']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result.marriage_date = self._parse_date(match.group(1))
                    break
                except:
                    continue
        
        # Extract marriage location
        for pattern in self.patterns['marriage_location']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.marriage_location = match.group(1).strip()
                break
        
        # Extract officiant information
        for pattern in self.patterns['officiant']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                officiant_full = match.group(1).strip()
                result.officiant_name = officiant_full
                
                # Try to extract title
                title_patterns = [r'(Rev\.?|Dr\.?|Judge|Pastor|Minister)', r'(Reverend|Doctor)']
                for title_pattern in title_patterns:
                    title_match = re.search(title_pattern, officiant_full, re.IGNORECASE)
                    if title_match:
                        result.officiant_title = title_match.group(1)
                        result.officiant_name = re.sub(title_pattern, '', officiant_full, flags=re.IGNORECASE).strip()
                        break
                break
        
        # Extract certificate number
        for pattern in self.patterns['certificate_number']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.certificate_number = match.group(1).upper()
                break
        
        # Extract registration date
        for pattern in self.patterns['registration_date']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result.registration_date = self._parse_date(match.group(1))
                    break
                except:
                    continue
        
        # Extract witnesses
        for pattern in self.patterns['witnesses']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                witness_name = match.strip()
                if witness_name and witness_name not in result.witnesses:
                    result.witnesses.append(witness_name)
        
        # Extract issuing authority
        for pattern in self.patterns['issuing_authority']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.issuing_authority = match.group(1).strip()
                break
        
        # Detect state and country from location or authority
        result = self._detect_jurisdiction(text, result)
        
        return result
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string in various formats"""
        date_str = date_str.strip()
        
        # Handle ordinal dates like "15th day of March 2020"
        ordinal_pattern = r'(\d{1,2})(?:st|nd|rd|th)?\s+(?:day\s+of\s+)?([A-Za-z]+)\s+(\d{4})'
        ordinal_match = re.match(ordinal_pattern, date_str)
        if ordinal_match:
            day, month_name, year = ordinal_match.groups()
            month_names = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                'september': 9, 'october': 10, 'november': 11, 'december': 12,
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            month_num = month_names.get(month_name.lower())
            if month_num:
                return date(int(year), month_num, int(day))
        
        # Standard formats
        formats = ['%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _detect_jurisdiction(self, text: str, result: MarriageCertificateData) -> MarriageCertificateData:
        """Detect issuing state and country from text"""
        text_upper = text.upper()
        
        # Check for US states
        for state_code, state_name in self.us_states.items():
            if (state_code in text_upper or state_name.upper() in text_upper):
                result.state_issued = state_code
                result.country_issued = "USA"
                break
        
        # Check for other countries
        country_indicators = {
            'CANADA': ['CANADA', 'CANADIAN'],
            'MEXICO': ['MEXICO', 'MEXICAN', 'MÉXICO'],
            'BRAZIL': ['BRAZIL', 'BRASIL', 'BRAZILIAN'],
            'UK': ['UNITED KINGDOM', 'ENGLAND', 'SCOTLAND', 'WALES', 'BRITISH']
        }
        
        for country, indicators in country_indicators.items():
            if any(indicator in text_upper for indicator in indicators):
                result.country_issued = country
                break
        
        return result
    
    def _validate_marriage_data(self, result: MarriageCertificateData) -> Dict[str, Any]:
        """Validate extracted marriage certificate data"""
        issues = []
        
        # Check required fields
        if not result.spouse1_name and not result.spouse2_name:
            issues.append("Spouse names not found")
        elif not result.spouse1_name or not result.spouse2_name:
            issues.append("Only one spouse name found - both required")
        
        if not result.marriage_date:
            issues.append("Marriage date not found")
        else:
            # Validate date is reasonable
            today = date.today()
            if result.marriage_date > today:
                issues.append("Marriage date is in the future")
            elif result.marriage_date < date(1800, 1, 1):
                issues.append("Marriage date is unreasonably old")
        
        if not result.marriage_location:
            issues.append("Marriage location not found")
        
        if not result.certificate_number:
            issues.append("Certificate number not found")
        
        # Check date consistency
        if result.marriage_date and result.registration_date:
            if result.registration_date < result.marriage_date:
                issues.append("Registration date is before marriage date")
        
        # Check for completeness
        if not result.officiant_name:
            issues.append("Officiant information not found")
        
        if not result.issuing_authority:
            issues.append("Issuing authority not found")
        
        # Determine status
        critical_issues = len([i for i in issues if any(word in i.lower() for word in ['not found', 'required', 'future'])])
        
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
    
    def _calculate_confidence(self, result: MarriageCertificateData, base_confidence: float) -> float:
        """Calculate overall confidence score"""
        confidence = base_confidence * 0.3  # Base OCR confidence (30%)
        
        # Required fields (50%)
        field_score = 0.0
        if result.spouse1_name and result.spouse2_name:
            field_score += 0.20  # Both spouse names
        elif result.spouse1_name or result.spouse2_name:
            field_score += 0.10  # At least one spouse name
        
        if result.marriage_date:
            field_score += 0.10
        if result.marriage_location:
            field_score += 0.08
        if result.certificate_number:
            field_score += 0.07
        if result.officiant_name:
            field_score += 0.05
        
        confidence += field_score
        
        # Validation status (20%)
        status_scores = {'VALID': 0.2, 'SUSPICIOUS': 0.1, 'INVALID': 0.0}
        confidence += status_scores.get(result.validation_status, 0.0)
        
        return min(confidence, 1.0)

class MarriageCertificateValidationStage(PipelineStage):
    """
    Pipeline stage for marriage certificate validation
    """
    
    def __init__(self):
        super().__init__("marriage_certificate_validation", enabled=True)
        self.validator = MarriageCertificateValidator()
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process marriage certificate validation"""
        try:
            # Only process if document is classified as marriage certificate
            if context.document_type.lower() not in ['marriage_certificate', 'marriage_cert', 'certidao_casamento']:
                logger.info(f"Skipping marriage certificate validation for document type: {context.document_type}")
                return context
            
            # Validate marriage certificate
            result = await self.validator.validate_marriage_certificate(
                context.content_base64,
                context.document_type
            )
            
            # Add results to context
            context.validation_results['marriage_certificate'] = {
                'spouse1_name': result.spouse1_name,
                'spouse2_name': result.spouse2_name,
                'spouse1_maiden_name': result.spouse1_maiden_name,
                'spouse2_maiden_name': result.spouse2_maiden_name,
                'marriage_date': result.marriage_date.isoformat() if result.marriage_date else None,
                'marriage_location': result.marriage_location,
                'officiant_name': result.officiant_name,
                'officiant_title': result.officiant_title,
                'certificate_number': result.certificate_number,
                'registration_date': result.registration_date.isoformat() if result.registration_date else None,
                'issuing_authority': result.issuing_authority,
                'state_issued': result.state_issued,
                'country_issued': result.country_issued,
                'witnesses': result.witnesses,
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
            
            logger.info(f"Marriage certificate validation completed: {result.validation_status}, confidence: {result.confidence_score:.2f}")
            
            return context
            
        except Exception as e:
            error_msg = f"Marriage certificate validation stage failed: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            return context

# Global instances
marriage_certificate_validator = MarriageCertificateValidator()
marriage_certificate_validation_stage = MarriageCertificateValidationStage()