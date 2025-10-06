"""
Driver License Validator - Specific Document Validator
Validador especializado para carteiras de motorista (Driver's License)
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
class DriverLicenseData:
    """Structured data from driver license"""
    # Personal Information
    full_name: str = ""
    license_number: str = ""
    date_of_birth: Optional[date] = None
    address: str = ""
    
    # License Information
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    license_class: str = ""
    state_issued: str = ""
    country_issued: str = ""
    
    # Physical Description
    height: str = ""
    weight: str = ""
    eye_color: str = ""
    hair_color: str = ""
    sex: str = ""
    
    # Validation
    confidence_score: float = 0.0
    validation_status: str = "PENDING"
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []

class DriverLicenseValidator:
    """
    Specialized validator for driver licenses from multiple states/countries
    """
    
    def __init__(self):
        # Driver license patterns for different states/countries
        self.patterns = {
            'license_number': [
                r'(?:license|dl|lic)[:\s#]*([a-z0-9\-]{6,15})',
                r'(?:número|numero)[:\s#]*([a-z0-9\-]{6,15})',
                r'(?:id|identification)[:\s#]*([a-z0-9\-]{6,15})',
                r'([a-z]\d{7,12})',  # Common format: Letter + numbers
            ],
            'full_name': [
                r'(?:name|nome|ln)[:\s]+([A-Z][A-Za-z\s,\-\']{2,40})',
                r'(?:last\s+name|surname)[:\s]+([A-Z][A-Za-z\s,\-\']{2,25})',
                r'(?:first\s+name|given\s+name)[:\s]+([A-Z][A-Za-z\s,\-\']{2,25})',
            ],
            'date_of_birth': [
                r'(?:dob|date\s+of\s+birth|born|nascimento)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:birth)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',  # Generic date pattern
            ],
            'address': [
                r'(?:address|addr|endereço)[:\s]+([A-Z0-9][A-Za-z0-9\s,\-\#\.]{10,80})',
                r'(?:street|rua|avenida)[:\s]+([A-Z0-9][A-Za-z0-9\s,\-\#\.]{10,60})',
            ],
            'expiration': [
                r'(?:exp|expires|expiration|vencimento)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:valid\s+until|válido\s+até)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
            ],
            'issue_date': [
                r'(?:issued|iss|emissão)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:date\s+issued)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
            ],
            'license_class': [
                r'(?:class|classe|type)[:\s]*([A-Z]{1,3})',
                r'(?:category|categoria)[:\s]*([A-Z]{1,3})',
            ],
            'state': [
                r'(?:state|estado)[:\s]*([A-Z]{2,20})',
                r'(?:issued\s+by)[:\s]*([A-Z]{2,20})',
            ],
            'physical_attributes': [
                r'(?:height|altura)[:\s]*(\d+[\'\"]?\-?\d*[\'\"]?)',
                r'(?:weight|peso)[:\s]*(\d+\s*lbs?|\d+\s*kg)',
                r'(?:eyes|olhos)[:\s]*([A-Z]{3,6})',
                r'(?:hair|cabelo)[:\s]*([A-Z]{3,6})',
                r'(?:sex|sexo|gender)[:\s]*([MF])',
            ]
        }
        
        # US State abbreviations
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
        
        # Valid license classes
        self.license_classes = {
            'A': 'Commercial - Combination vehicles',
            'B': 'Commercial - Large trucks',
            'C': 'Commercial - Small hazmat/passenger vehicles',
            'D': 'Regular operator license',
            'M': 'Motorcycle',
            'CDL': 'Commercial Driver License'
        }
    
    async def validate_driver_license(self, 
                                    document_content: str,
                                    document_type: str = "driver_license") -> DriverLicenseData:
        """
        Validate and extract data from driver license
        
        Args:
            document_content: Base64 image or text content
            document_type: Document type identifier
        
        Returns:
            DriverLicenseData with extracted and validated information
        """
        try:
            result = DriverLicenseData()
            
            # 1. Extract text if image provided
            if self._is_base64_image(document_content):
                ocr_result = await real_ocr_engine.extract_text_from_image(
                    document_content, 
                    mode="document",
                    language="eng"  # Driver licenses typically in English
                )
                text_content = ocr_result.text
                base_confidence = ocr_result.confidence
            else:
                text_content = document_content
                base_confidence = 0.9
            
            # 2. Verify this is actually a driver license
            if not self._verify_driver_license(text_content):
                result.validation_status = "INVALID"
                result.issues.append("Document does not appear to be a driver license")
                return result
            
            # 3. Extract structured data
            result = await self._extract_license_data(text_content, result)
            
            # 4. Validate extracted data
            validation_result = self._validate_license_data(result)
            result.validation_status = validation_result['status']
            result.issues.extend(validation_result['issues'])
            
            # 5. Calculate confidence score
            result.confidence_score = self._calculate_confidence(result, base_confidence)
            
            logger.info(f"Driver license validation completed: status={result.validation_status}, confidence={result.confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Driver license validation failed: {e}")
            result = DriverLicenseData()
            result.validation_status = "INVALID"
            result.issues.append(f"Validation error: {str(e)}")
            return result
    
    def _is_base64_image(self, content: str) -> bool:
        """Check if content is base64 encoded image"""
        return (content.startswith('data:image/') or 
                (len(content) > 100 and content.replace('+', '').replace('/', '').replace('=', '').isalnum()))
    
    def _verify_driver_license(self, text: str) -> bool:
        """Verify this is a driver license document"""
        text_lower = text.lower()
        
        # Driver license indicators
        dl_indicators = [
            'driver license', "driver's license", 'driving license',
            'department of motor vehicles', 'dmv',
            'operator license', 'chauffeur license',
            'commercial driver license', 'cdl',
            'license number', 'dl#', 'lic#'
        ]
        
        found_indicators = sum(1 for indicator in dl_indicators if indicator in text_lower)
        return found_indicators >= 2
    
    async def _extract_license_data(self, text: str, result: DriverLicenseData) -> DriverLicenseData:
        """Extract structured data from driver license text"""
        
        # Extract license number
        for pattern in self.patterns['license_number']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.license_number = match.group(1).upper().replace('-', '')
                break
        
        # Extract full name (try to get complete name)
        names_found = []
        for pattern in self.patterns['full_name']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            names_found.extend(matches)
        
        if names_found:
            # Use the longest name found (likely the most complete)
            result.full_name = max(names_found, key=len).strip()
        
        # Extract date of birth
        for pattern in self.patterns['date_of_birth']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result.date_of_birth = self._parse_date(match.group(1))
                    break
                except:
                    continue
        
        # Extract address
        for pattern in self.patterns['address']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.address = match.group(1).strip()
                break
        
        # Extract expiration date
        for pattern in self.patterns['expiration']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result.expiration_date = self._parse_date(match.group(1))
                    break
                except:
                    continue
        
        # Extract issue date
        for pattern in self.patterns['issue_date']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result.issue_date = self._parse_date(match.group(1))
                    break
                except:
                    continue
        
        # Extract license class
        for pattern in self.patterns['license_class']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                class_found = match.group(1).upper()
                if class_found in self.license_classes:
                    result.license_class = class_found
                break
        
        # Extract state
        for pattern in self.patterns['state']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                state_found = match.group(1).upper()
                if state_found in self.us_states:
                    result.state_issued = state_found
                    result.country_issued = "USA"
                break
        
        # Extract physical attributes
        for pattern in self.patterns['physical_attributes']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                match_lower = match.lower()
                if any(height_indicator in match_lower for height_indicator in ['ft', 'in', '"', "'"]):
                    result.height = match
                elif any(weight_indicator in match_lower for weight_indicator in ['lb', 'kg']):
                    result.weight = match
                elif len(match) <= 6 and match.isalpha():
                    if not result.eye_color and any(eye in match_lower for eye in ['blu', 'brn', 'grn', 'haz', 'gry']):
                        result.eye_color = match.upper()
                    elif not result.hair_color and any(hair in match_lower for hair in ['blk', 'brn', 'bln', 'red', 'gry']):
                        result.hair_color = match.upper()
                elif match.upper() in ['M', 'F']:
                    result.sex = match.upper()
        
        return result
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string in various formats"""
        date_str = date_str.strip()
        
        # Try MM/DD/YYYY first (US format)
        formats = ['%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _validate_license_data(self, result: DriverLicenseData) -> Dict[str, Any]:
        """Validate extracted driver license data"""
        issues = []
        
        # Check required fields
        if not result.license_number:
            issues.append("License number not found")
        elif len(result.license_number) < 6:
            issues.append("License number appears too short")
        
        if not result.full_name:
            issues.append("Full name not found")
        elif len(result.full_name) < 3:
            issues.append("Full name appears incomplete")
        
        if not result.date_of_birth:
            issues.append("Date of birth not found")
        else:
            # Check if DOB is reasonable
            today = date.today()
            age = (today - result.date_of_birth).days // 365
            if age < 16:
                issues.append("Date of birth indicates age below minimum driving age")
            elif age > 100:
                issues.append("Date of birth indicates unreasonable age")
        
        # Check expiration date
        if result.expiration_date:
            if result.expiration_date < date.today():
                issues.append("Driver license has expired")
            elif result.expiration_date < date.today().replace(year=date.today().year + 1):
                issues.append("Driver license expires within 1 year")
        else:
            issues.append("Expiration date not found")
        
        # Check date consistency
        if result.issue_date and result.expiration_date:
            if result.issue_date > result.expiration_date:
                issues.append("Issue date is after expiration date")
        
        if result.issue_date and result.date_of_birth:
            issue_age = (result.issue_date - result.date_of_birth).days // 365
            if issue_age < 16:
                issues.append("License issued before minimum driving age")
        
        # Check state information
        if not result.state_issued:
            issues.append("Issuing state not found")
        
        # Determine status
        critical_issues = len([i for i in issues if any(word in i.lower() for word in ['not found', 'expired', 'invalid'])])
        
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
    
    def _calculate_confidence(self, result: DriverLicenseData, base_confidence: float) -> float:
        """Calculate overall confidence score"""
        confidence = base_confidence * 0.3  # Base OCR confidence (30%)
        
        # Required fields (50%)
        field_score = 0.0
        if result.license_number and len(result.license_number) >= 6:
            field_score += 0.15
        if result.full_name and len(result.full_name) >= 3:
            field_score += 0.15
        if result.date_of_birth:
            field_score += 0.10
        if result.expiration_date:
            field_score += 0.05
        if result.state_issued:
            field_score += 0.05
        
        confidence += field_score
        
        # Validation status (20%)
        status_scores = {'VALID': 0.2, 'SUSPICIOUS': 0.1, 'INVALID': 0.0}
        confidence += status_scores.get(result.validation_status, 0.0)
        
        return min(confidence, 1.0)

class DriverLicenseValidationStage(PipelineStage):
    """
    Pipeline stage for driver license validation
    """
    
    def __init__(self):
        super().__init__("driver_license_validation", enabled=True)
        self.validator = DriverLicenseValidator()
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process driver license validation"""
        try:
            # Only process if document is classified as driver license
            if context.document_type.lower() not in ['driver_license', 'drivers_license', 'driving_license', 'dl']:
                logger.info(f"Skipping driver license validation for document type: {context.document_type}")
                return context
            
            # Validate driver license
            result = await self.validator.validate_driver_license(
                context.content_base64,
                context.document_type
            )
            
            # Add results to context
            context.validation_results['driver_license'] = {
                'full_name': result.full_name,
                'license_number': result.license_number,
                'date_of_birth': result.date_of_birth.isoformat() if result.date_of_birth else None,
                'address': result.address,
                'issue_date': result.issue_date.isoformat() if result.issue_date else None,
                'expiration_date': result.expiration_date.isoformat() if result.expiration_date else None,
                'license_class': result.license_class,
                'state_issued': result.state_issued,
                'country_issued': result.country_issued,
                'height': result.height,
                'weight': result.weight,
                'eye_color': result.eye_color,
                'hair_color': result.hair_color,
                'sex': result.sex,
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
            
            logger.info(f"Driver license validation completed: {result.validation_status}, confidence: {result.confidence_score:.2f}")
            
            return context
            
        except Exception as e:
            error_msg = f"Driver license validation stage failed: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            return context

# Global instances
driver_license_validator = DriverLicenseValidator()
driver_license_validation_stage = DriverLicenseValidationStage()