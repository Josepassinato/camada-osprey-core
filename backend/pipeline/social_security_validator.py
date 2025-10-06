"""
Social Security Card Validator - Specific Document Validator
Validador especializado para cartões de Social Security
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
class SocialSecurityCardData:
    """Structured data from Social Security Card"""
    # Personal Information
    full_name: str = ""
    social_security_number: str = ""
    
    # Card Information
    card_type: str = ""  # Original, Replacement, Corrected
    signature: str = ""
    
    # Security Features
    has_security_features: bool = False
    security_features_detected: List[str] = None
    
    # Employment Authorization
    employment_authorized: bool = True  # Default for US citizens
    work_restrictions: List[str] = None
    
    # Validation
    ssn_area_valid: bool = False
    ssn_group_valid: bool = False
    ssn_serial_valid: bool = False
    
    confidence_score: float = 0.0
    validation_status: str = "PENDING"  # VALID, INVALID, SUSPICIOUS
    issues: List[str] = None
    
    def __post_init__(self):
        if self.security_features_detected is None:
            self.security_features_detected = []
        if self.work_restrictions is None:
            self.work_restrictions = []
        if self.issues is None:
            self.issues = []

class SocialSecurityValidator:
    """
    Specialized validator for Social Security Cards
    Validates SSN format, security features, and employment authorization
    """
    
    def __init__(self):
        # Social Security Card patterns
        self.patterns = {
            'full_name': [
                r'(?:name|nome)[:\s]*([A-Z][A-Za-z\s\-\']{3,50})',
                r'([A-Z][A-Z\s\-\']{5,50})',  # All caps name format
                r'(?:this\s+certifies\s+that)[:\s]*([A-Z][A-Za-z\s\-\']{3,50})',
            ],
            'ssn': [
                r'(\d{3}[-\s]?\d{2}[-\s]?\d{4})',
                r'(?:social\s+security\s+number)[:\s]*(\d{3}[-\s]?\d{2}[-\s]?\d{4})',
                r'(?:ssn)[:\s]*(\d{3}[-\s]?\d{2}[-\s]?\d{4})',
            ],
            'signature': [
                r'(?:signature|assinatura)[:\s]*([A-Za-z\s\-\']{3,50})',
                r'(?:authorized\s+signature)[:\s]*([A-Za-z\s\-\']{3,50})',
            ]
        }
        
        # Invalid SSN ranges (these should not be issued)
        self.invalid_ssn_ranges = {
            'area': [
                '000',  # Never assigned
                '666',  # Never assigned
                '900', '901', '902', '903', '904', '905', '906', '907', '908', '909',  # Never assigned
                '910', '911', '912', '913', '914', '915', '916', '917', '918', '919',
                '920', '921', '922', '923', '924', '925', '926', '927', '928', '929',
                '930', '931', '932', '933', '934', '935', '936', '937', '938', '939',
                '940', '941', '942', '943', '944', '945', '946', '947', '948', '949',
                '950', '951', '952', '953', '954', '955', '956', '957', '958', '959',
                '960', '961', '962', '963', '964', '965', '966', '967', '968', '969',
                '970', '971', '972', '973', '974', '975', '976', '977', '978', '979',
                '980', '981', '982', '983', '984', '985', '986', '987', '988', '989',
                '990', '991', '992', '993', '994', '995', '996', '997', '998', '999'
            ]
        }
        
        # Security features to look for
        self.security_features = [
            'social security administration',
            'department of health and human services',
            'this number has been established for',
            'not valid for employment',
            'valid for work only with ins authorization',
            'valid for work only with dhs authorization',
            'watermark',
            'security paper',
            'microprinting'
        ]
        
        # Employment restriction indicators
        self.employment_restrictions = [
            'not valid for employment',
            'valid for work only with ins authorization',
            'valid for work only with dhs authorization',
            'not authorized for employment'
        ]
        
        # Social Security Card indicators
        self.card_indicators = [
            'social security', 'social security administration', 'ssa',
            'this number has been established for', 'signature',
            'department of health and human services'
        ]
    
    async def validate_social_security_card(self, 
                                          document_content: str,
                                          document_type: str = "social_security_card") -> SocialSecurityCardData:
        """
        Validate and extract data from Social Security Card
        
        Args:
            document_content: Base64 image or text content
            document_type: Document type identifier
        
        Returns:
            SocialSecurityCardData with extracted and validated information
        """
        try:
            result = SocialSecurityCardData()
            
            # 1. Extract text if image provided
            if self._is_base64_image(document_content):
                ocr_result = await real_ocr_engine.extract_text_from_image(
                    document_content, 
                    mode="document",
                    language="eng"  # SSN cards are in English
                )
                text_content = ocr_result.text
                base_confidence = ocr_result.confidence
            else:
                text_content = document_content
                base_confidence = 0.9
            
            # 2. Verify this is actually a Social Security Card
            if not self._verify_social_security_card(text_content):
                result.validation_status = "INVALID"
                result.issues.append("Document does not appear to be a Social Security Card")
                return result
            
            # 3. Extract structured data
            result = await self._extract_ssn_data(text_content, result)
            
            # 4. Validate SSN format and ranges
            if result.social_security_number:
                ssn_validation = self._validate_ssn_format(result.social_security_number)
                result.ssn_area_valid = ssn_validation['area_valid']
                result.ssn_group_valid = ssn_validation['group_valid']
                result.ssn_serial_valid = ssn_validation['serial_valid']
                result.issues.extend(ssn_validation['issues'])
            
            # 5. Check security features
            result.security_features_detected = self._detect_security_features(text_content)
            result.has_security_features = len(result.security_features_detected) > 0
            
            # 6. Check employment restrictions
            result.work_restrictions = self._check_employment_restrictions(text_content)
            result.employment_authorized = len(result.work_restrictions) == 0
            
            # 7. Validate extracted data
            validation_result = self._validate_ssn_card_data(result)
            result.validation_status = validation_result['status']
            result.issues.extend(validation_result['issues'])
            
            # 8. Calculate confidence score
            result.confidence_score = self._calculate_confidence(result, base_confidence)
            
            logger.info(f"Social Security Card validation completed: status={result.validation_status}, confidence={result.confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Social Security Card validation failed: {e}")
            result = SocialSecurityCardData()
            result.validation_status = "INVALID"
            result.issues.append(f"Validation error: {str(e)}")
            return result
    
    def _is_base64_image(self, content: str) -> bool:
        """Check if content is base64 encoded image"""
        return (content.startswith('data:image/') or 
                (len(content) > 100 and content.replace('+', '').replace('/', '').replace('=', '').isalnum()))
    
    def _verify_social_security_card(self, text: str) -> bool:
        """Verify this is a Social Security Card document"""
        text_lower = text.lower()
        
        found_indicators = sum(1 for indicator in self.card_indicators 
                             if indicator in text_lower)
        
        # Must have at least 2 indicators to be considered a SSN card
        return found_indicators >= 2
    
    async def _extract_ssn_data(self, text: str, result: SocialSecurityCardData) -> SocialSecurityCardData:
        """Extract structured data from Social Security Card text"""
        
        # Extract full name
        for pattern in self.patterns['full_name']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name_candidate = match.group(1).strip()
                # Filter out obvious non-names
                if not any(word in name_candidate.lower() for word in ['social', 'security', 'administration', 'department']):
                    result.full_name = name_candidate
                    break
        
        # Extract SSN
        for pattern in self.patterns['ssn']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ssn_raw = match.group(1)
                # Normalize SSN format
                ssn_clean = re.sub(r'[-\s]', '', ssn_raw)
                if len(ssn_clean) == 9 and ssn_clean.isdigit():
                    result.social_security_number = f"{ssn_clean[:3]}-{ssn_clean[3:5]}-{ssn_clean[5:9]}"
                    break
        
        # Extract signature (if visible)
        for pattern in self.patterns['signature']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.signature = match.group(1).strip()
                break
        
        return result
    
    def _validate_ssn_format(self, ssn: str) -> Dict[str, Any]:
        """Validate SSN format and check against invalid ranges"""
        issues = []
        
        # Remove dashes for validation
        ssn_clean = ssn.replace('-', '')
        
        if len(ssn_clean) != 9 or not ssn_clean.isdigit():
            issues.append("Invalid SSN format")
            return {
                'area_valid': False,
                'group_valid': False,
                'serial_valid': False,
                'issues': issues
            }
        
        area = ssn_clean[:3]
        group = ssn_clean[3:5]
        serial = ssn_clean[5:9]
        
        # Validate area (first 3 digits)
        area_valid = area not in self.invalid_ssn_ranges['area']
        if not area_valid:
            issues.append(f"Invalid SSN area: {area}")
        
        # Validate group (middle 2 digits) - cannot be 00
        group_valid = group != '00'
        if not group_valid:
            issues.append("Invalid SSN group: cannot be 00")
        
        # Validate serial (last 4 digits) - cannot be 0000
        serial_valid = serial != '0000'
        if not serial_valid:
            issues.append("Invalid SSN serial: cannot be 0000")
        
        return {
            'area_valid': area_valid,
            'group_valid': group_valid,
            'serial_valid': serial_valid,
            'issues': issues
        }
    
    def _detect_security_features(self, text: str) -> List[str]:
        """Detect security features in the document"""
        text_lower = text.lower()
        detected_features = []
        
        for feature in self.security_features:
            if feature in text_lower:
                detected_features.append(feature)
        
        return detected_features
    
    def _check_employment_restrictions(self, text: str) -> List[str]:
        """Check for employment authorization restrictions"""
        text_lower = text.lower()
        restrictions = []
        
        for restriction in self.employment_restrictions:
            if restriction in text_lower:
                restrictions.append(restriction)
        
        return restrictions
    
    def _validate_ssn_card_data(self, result: SocialSecurityCardData) -> Dict[str, Any]:
        """Validate extracted Social Security Card data"""
        issues = []
        
        # Check required fields
        if not result.full_name:
            issues.append("Name not found on card")
        elif len(result.full_name) < 3:
            issues.append("Name appears incomplete")
        
        if not result.social_security_number:
            issues.append("Social Security Number not found")
        
        # Check SSN validity
        if not (result.ssn_area_valid and result.ssn_group_valid and result.ssn_serial_valid):
            issues.append("SSN format or range validation failed")
        
        # Check security features
        if not result.has_security_features:
            issues.append("No security features detected - may be fraudulent")
        
        # Determine status
        critical_issues = len([i for i in issues if any(word in i.lower() 
                              for word in ['not found', 'invalid', 'fraudulent', 'failed'])])
        
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
    
    def _calculate_confidence(self, result: SocialSecurityCardData, base_confidence: float) -> float:
        """Calculate overall confidence score"""
        confidence = base_confidence * 0.25  # Base OCR confidence (25%)
        
        # Name extraction (20%)
        if result.full_name:
            confidence += 0.20
        elif result.full_name and len(result.full_name) > 5:
            confidence += 0.15
        
        # SSN extraction and validation (35%)
        if result.social_security_number:
            confidence += 0.15
            if result.ssn_area_valid:
                confidence += 0.07
            if result.ssn_group_valid:
                confidence += 0.07
            if result.ssn_serial_valid:
                confidence += 0.06
        
        # Security features (15%)
        if result.has_security_features:
            feature_score = min(len(result.security_features_detected) * 0.03, 0.15)
            confidence += feature_score
        
        # Employment authorization (5%)
        if result.employment_authorized:
            confidence += 0.05
        elif result.work_restrictions:
            confidence += 0.02  # Partial credit for detecting restrictions
        
        # Validation status (10%)
        status_scores = {'VALID': 0.10, 'SUSPICIOUS': 0.05, 'INVALID': 0.0}
        confidence += status_scores.get(result.validation_status, 0.0)
        
        return min(confidence, 1.0)

class SocialSecurityCardValidationStage(PipelineStage):
    """
    Pipeline stage for Social Security Card validation
    """
    
    def __init__(self):
        super().__init__("social_security_card_validation", enabled=True)
        self.validator = SocialSecurityValidator()
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process Social Security Card validation"""
        try:
            # Only process if document is classified as Social Security Card
            if context.document_type.lower() not in ['social_security_card', 'ssn_card', 'social_security', 'cartao_ssn']:
                logger.info(f"Skipping Social Security Card validation for document type: {context.document_type}")
                return context
            
            # Validate Social Security Card
            result = await self.validator.validate_social_security_card(
                context.content_base64,
                context.document_type
            )
            
            # Add results to context
            context.validation_results['social_security_card'] = {
                'full_name': result.full_name,
                'social_security_number': result.social_security_number,
                'card_type': result.card_type,
                'signature': result.signature,
                'has_security_features': result.has_security_features,
                'security_features_detected': result.security_features_detected,
                'employment_authorized': result.employment_authorized,
                'work_restrictions': result.work_restrictions,
                'ssn_area_valid': result.ssn_area_valid,
                'ssn_group_valid': result.ssn_group_valid,
                'ssn_serial_valid': result.ssn_serial_valid,
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
            
            logger.info(f"Social Security Card validation completed: {result.validation_status}, confidence: {result.confidence_score:.2f}")
            
            return context
            
        except Exception as e:
            error_msg = f"Social Security Card validation stage failed: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            return context

# Global instances
social_security_validator = SocialSecurityValidator()
social_security_card_validation_stage = SocialSecurityCardValidationStage()