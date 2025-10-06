"""
Specialized Document Validators
Validadores específicos por tipo de documento baseados no plano de alta precisão
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    field_name: str
    is_valid: bool
    confidence: float
    extracted_value: str
    normalized_value: str
    issues: List[str]
    recommendations: List[str]

class PassportValidator:
    """
    Validador especializado para passaportes com análise de MRZ
    """
    
    def __init__(self):
        self.country_codes = {
            'BR': {'pattern': r'^[A-Z]{2}\d{6}$', 'name': 'Brazil'},
            'US': {'pattern': r'^[0-9]{9}$', 'name': 'United States'},
            'IN': {'pattern': r'^[A-Z]\d{7}$', 'name': 'India'},
            # Add more countries as needed
        }
    
    def validate_passport_comprehensive(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validação completa de passaporte incluindo MRZ cross-validation
        """
        results = {}
        issues = []
        
        # Validate individual fields
        results['full_name'] = self._validate_name(extracted_data.get('full_name', ''))
        results['passport_number'] = self._validate_passport_number(
            extracted_data.get('passport_number', ''),
            extracted_data.get('nationality', '')
        )
        results['date_of_birth'] = self._validate_date(extracted_data.get('date_of_birth', ''))
        results['expiry_date'] = self._validate_expiry_date(extracted_data.get('expiry_date', ''))
        results['nationality'] = self._validate_nationality(extracted_data.get('nationality', ''))
        
        # MRZ validation if available
        if 'mrz_line1' in extracted_data and 'mrz_line2' in extracted_data:
            mrz_result = self._validate_mrz(
                extracted_data['mrz_line1'],
                extracted_data['mrz_line2']
            )
            results['mrz_validation'] = mrz_result
            
            # Cross-validate MRZ with visual zone
            cross_validation = self._cross_validate_mrz_visual(extracted_data, mrz_result)
            if cross_validation['has_discrepancies']:
                issues.extend(cross_validation['discrepancies'])
        
        # Check expiry status
        if results['expiry_date']['is_valid']:
            expiry_check = self._check_expiry_status(results['expiry_date']['normalized_value'])
            if expiry_check['is_expired']:
                issues.append(f"CRITICAL: Passport expired on {expiry_check['expiry_date']}")
            elif expiry_check['expires_soon']:
                issues.append(f"WARNING: Passport expires soon on {expiry_check['expiry_date']}")
        
        # Calculate overall confidence
        valid_fields = sum(1 for r in results.values() if (isinstance(r, dict) and r.get('is_valid', False)) or (hasattr(r, 'is_valid') and r.is_valid))
        total_fields = len([r for r in results.values() if isinstance(r, (dict, ValidationResult))])
        overall_confidence = (valid_fields / total_fields) * 100 if total_fields > 0 else 0
        
        return {
            'document_type': 'passport',
            'validation_results': results,
            'overall_confidence': overall_confidence,
            'is_valid': overall_confidence >= 80 and len(issues) == 0,
            'issues': issues,
            'uscis_acceptable': overall_confidence >= 90 and all(
                field in results and ((isinstance(results[field], dict) and results[field].get('is_valid', False)) or (hasattr(results[field], 'is_valid') and results[field].is_valid))
                for field in ['full_name', 'passport_number', 'date_of_birth', 'expiry_date']
            )
        }
    
    def _validate_name(self, name: str) -> ValidationResult:
        """Valida nome no passaporte"""
        if not name or len(name.strip()) < 2:
            return ValidationResult(
                field_name='full_name',
                is_valid=False,
                confidence=0.0,
                extracted_value=name,
                normalized_value='',
                issues=['Name is missing or too short'],
                recommendations=['Ensure full name is clearly visible']
            )
        
        # Check for common OCR errors
        issues = []
        if re.search(r'\d', name):
            issues.append('Name contains numbers - possible OCR error')
        
        if len(name.strip()) > 50:
            issues.append('Name is unusually long - verify correctness')
        
        # Normalize name (Title Case, remove extra spaces)
        normalized = ' '.join(word.capitalize() for word in name.strip().split())
        
        confidence = 0.9 if not issues else 0.7
        
        return ValidationResult(
            field_name='full_name',
            is_valid=len(issues) == 0,
            confidence=confidence,
            extracted_value=name,
            normalized_value=normalized,
            issues=issues,
            recommendations=['Verify name spelling matches exactly'] if issues else []
        )
    
    def _validate_passport_number(self, number: str, nationality: str) -> ValidationResult:
        """Valida número do passaporte baseado na nacionalidade"""
        if not number:
            return ValidationResult(
                field_name='passport_number',
                is_valid=False,
                confidence=0.0,
                extracted_value=number,
                normalized_value='',
                issues=['Passport number is missing'],
                recommendations=['Ensure passport number is clearly visible']
            )
        
        # Normalize number (remove spaces, uppercase)
        normalized = re.sub(r'[^\w]', '', number.upper())
        
        # Get country-specific pattern
        country_code = self._get_country_code(nationality)
        if country_code and country_code in self.country_codes:
            pattern = self.country_codes[country_code]['pattern']
            is_valid = bool(re.match(pattern, normalized))
            confidence = 0.95 if is_valid else 0.3
        else:
            # Generic validation for unknown countries
            is_valid = 6 <= len(normalized) <= 12 and normalized.isalnum()
            confidence = 0.8 if is_valid else 0.3
        
        issues = []
        if not is_valid:
            issues.append(f'Passport number format invalid for {nationality or "unknown nationality"}')
        
        return ValidationResult(
            field_name='passport_number',
            is_valid=is_valid,
            confidence=confidence,
            extracted_value=number,
            normalized_value=normalized,
            issues=issues,
            recommendations=['Verify passport number format'] if issues else []
        )
    
    def _validate_date(self, date_str: str) -> ValidationResult:
        """Valida formato de data"""
        if not date_str:
            return ValidationResult(
                field_name='date_of_birth',
                is_valid=False,
                confidence=0.0,
                extracted_value=date_str,
                normalized_value='',
                issues=['Date is missing'],
                recommendations=['Ensure date is clearly visible']
            )
        
        # Try to parse different date formats
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d %b %Y', '%b %d, %Y']
        parsed_date = None
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                break
            except ValueError:
                continue
        
        if not parsed_date:
            return ValidationResult(
                field_name='date_of_birth',
                is_valid=False,
                confidence=0.0,
                extracted_value=date_str,
                normalized_value='',
                issues=['Invalid date format'],
                recommendations=['Check date format and readability']
            )
        
        # Normalize to ISO format
        normalized = parsed_date.strftime('%Y-%m-%d')
        
        # Validate logical constraints
        issues = []
        current_year = datetime.now().year
        
        if parsed_date.year < 1900 or parsed_date.year > current_year:
            issues.append(f'Birth year {parsed_date.year} is not realistic')
        
        if parsed_date > datetime.now():
            issues.append('Birth date is in the future')
        
        return ValidationResult(
            field_name='date_of_birth',
            is_valid=len(issues) == 0,
            confidence=0.95 if len(issues) == 0 else 0.5,
            extracted_value=date_str,
            normalized_value=normalized,
            issues=issues,
            recommendations=[]
        )
    
    def _validate_expiry_date(self, date_str: str) -> ValidationResult:
        """Valida data de expiração"""
        date_result = self._validate_date(date_str)
        date_result.field_name = 'expiry_date'
        
        if date_result.is_valid:
            # Additional validation for expiry dates
            expiry_date = datetime.strptime(date_result.normalized_value, '%Y-%m-%d')
            
            if expiry_date < datetime.now():
                date_result.issues.append('CRITICAL: Passport has expired')
                date_result.is_valid = False
                date_result.confidence = 0.0
        
        return date_result
    
    def _validate_nationality(self, nationality: str) -> ValidationResult:
        """Valida nacionalidade"""
        if not nationality:
            return ValidationResult(
                field_name='nationality',
                is_valid=False,
                confidence=0.0,
                extracted_value=nationality,
                normalized_value='',
                issues=['Nationality is missing'],
                recommendations=['Ensure nationality field is visible']
            )
        
        # Normalize nationality
        normalized = nationality.strip().title()
        
        # Basic validation (could be expanded with country list)
        is_valid = len(normalized) >= 3 and normalized.isalpha()
        confidence = 0.8 if is_valid else 0.3
        
        return ValidationResult(
            field_name='nationality',
            is_valid=is_valid,
            confidence=confidence,
            extracted_value=nationality,
            normalized_value=normalized,
            issues=[] if is_valid else ['Invalid nationality format'],
            recommendations=[]
        )
    
    def _validate_mrz(self, line1: str, line2: str) -> Dict[str, Any]:
        """Valida Machine Readable Zone"""
        # Simplified MRZ validation (full implementation would be more complex)
        try:
            # Basic format check
            if len(line1) != 44 or len(line2) != 44:
                return {'is_valid': False, 'error': 'MRZ lines must be 44 characters each'}
            
            # Extract data from MRZ
            doc_type = line1[:2]
            country_code = line1[2:5]
            name_section = line1[5:44]
            
            passport_number = line2[:9].replace('<', '')
            nationality = line2[10:13]
            birth_date = line2[13:19]
            sex = line2[20]
            expiry_date = line2[21:27]
            
            return {
                'is_valid': True,
                'extracted_data': {
                    'document_type': doc_type,
                    'country_code': country_code,
                    'passport_number': passport_number,
                    'nationality': nationality,
                    'birth_date': self._parse_mrz_date(birth_date),
                    'expiry_date': self._parse_mrz_date(expiry_date),
                    'sex': sex
                }
            }
        except Exception as e:
            return {'is_valid': False, 'error': f'MRZ parsing error: {str(e)}'}
    
    def _cross_validate_mrz_visual(self, visual_data: Dict[str, Any], mrz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-valida dados visuais com MRZ"""
        discrepancies = []
        
        if not mrz_data.get('is_valid'):
            return {'has_discrepancies': False, 'discrepancies': []}
        
        mrz_extracted = mrz_data['extracted_data']
        
        # Compare passport numbers
        visual_passport = visual_data.get('passport_number', '').replace(' ', '').upper()
        mrz_passport = mrz_extracted.get('passport_number', '').upper()
        
        if visual_passport and mrz_passport and visual_passport != mrz_passport:
            discrepancies.append(f'Passport number mismatch: Visual={visual_passport}, MRZ={mrz_passport}')
        
        # Compare dates
        visual_birth = visual_data.get('date_of_birth')
        mrz_birth = mrz_extracted.get('birth_date')
        
        if visual_birth and mrz_birth and visual_birth != mrz_birth:
            discrepancies.append(f'Birth date mismatch: Visual={visual_birth}, MRZ={mrz_birth}')
        
        return {
            'has_discrepancies': len(discrepancies) > 0,
            'discrepancies': discrepancies
        }
    
    def _parse_mrz_date(self, mrz_date: str) -> str:
        """Converte data MRZ (YYMMDD) para ISO format"""
        if len(mrz_date) != 6:
            return ''
        
        try:
            year = int(mrz_date[:2])
            # Assume year > 50 is 19xx, otherwise 20xx
            year = 1900 + year if year > 50 else 2000 + year
            month = int(mrz_date[2:4])
            day = int(mrz_date[4:6])
            
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            return ''
    
    def _get_country_code(self, nationality: str) -> Optional[str]:
        """Obtém código do país baseado na nacionalidade"""
        if not nationality:
            return None
        
        nationality_lower = nationality.lower()
        
        mapping = {
            'brazil': 'BR', 'brazilian': 'BR', 'brasil': 'BR', 'brasileira': 'BR',
            'united states': 'US', 'american': 'US', 'usa': 'US',
            'india': 'IN', 'indian': 'IN'
        }
        
        return mapping.get(nationality_lower)
    
    def _check_expiry_status(self, expiry_date: str) -> Dict[str, Any]:
        """Verifica status de expiração"""
        try:
            expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
            now = datetime.now()
            
            is_expired = expiry < now
            days_until_expiry = (expiry - now).days
            expires_soon = 0 < days_until_expiry <= 180  # 6 months
            
            return {
                'is_expired': is_expired,
                'expires_soon': expires_soon,
                'days_until_expiry': days_until_expiry,
                'expiry_date': expiry_date
            }
        except ValueError:
            return {'is_expired': True, 'expires_soon': False, 'days_until_expiry': -1}

class I797Validator:
    """
    Validador especializado para I-797 Notices
    """
    
    def validate_i797_comprehensive(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validação completa de I-797
        """
        results = {}
        
        # Validate receipt number (critical field)
        results['receipt_number'] = self._validate_receipt_number(
            extracted_data.get('receipt_number', '')
        )
        
        # Validate notice type
        results['notice_type'] = self._validate_notice_type(
            extracted_data.get('notice_type', '')
        )
        
        # Validate petitioner and beneficiary
        results['petitioner'] = self._validate_entity_name(
            extracted_data.get('petitioner', ''), 'petitioner'
        )
        results['beneficiary'] = self._validate_entity_name(
            extracted_data.get('beneficiary', ''), 'beneficiary'
        )
        
        # Validate dates
        results['notice_date'] = self._validate_date_field(
            extracted_data.get('notice_date', ''), 'notice_date'
        )
        results['valid_from'] = self._validate_date_field(
            extracted_data.get('valid_from', ''), 'valid_from'
        )
        results['valid_to'] = self._validate_date_field(
            extracted_data.get('valid_to', ''), 'valid_to'
        )
        
        # Calculate overall confidence
        valid_fields = sum(1 for r in results.values() if (isinstance(r, dict) and r.get('is_valid', False)) or (hasattr(r, 'is_valid') and r.is_valid))
        total_fields = len(results)
        overall_confidence = (valid_fields / total_fields) * 100
        
        # Critical requirements check
        critical_fields = ['receipt_number', 'notice_type', 'beneficiary']
        critical_valid = all(
            field in results and ((isinstance(results[field], dict) and results[field].get('is_valid', False)) or (hasattr(results[field], 'is_valid') and results[field].is_valid))
            for field in critical_fields
        )
        
        return {
            'document_type': 'i797',
            'validation_results': results,
            'overall_confidence': overall_confidence,
            'is_valid': critical_valid and overall_confidence >= 70,
            'critical_fields_valid': critical_valid,
            'uscis_acceptable': critical_valid and overall_confidence >= 85
        }
    
    def _validate_receipt_number(self, receipt_number: str) -> ValidationResult:
        """Valida número de recibo I-797: 3 letras + 10 dígitos"""
        if not receipt_number:
            return ValidationResult(
                field_name='receipt_number',
                is_valid=False,
                confidence=0.0,
                extracted_value=receipt_number,
                normalized_value='',
                issues=['Receipt number is missing'],
                recommendations=['Ensure receipt number is clearly visible in top section']
            )
        
        # Normalize (remove spaces, uppercase)
        normalized = re.sub(r'[^A-Z0-9]', '', receipt_number.upper())
        
        # Validate pattern: 3 letters + 10 digits
        pattern = r'^[A-Z]{3}\d{10}$'
        is_valid = bool(re.match(pattern, normalized))
        
        # Calculate confidence based on format match
        if is_valid:
            confidence = 0.99
        elif len(normalized) == 13 and normalized[:3].isalpha() and normalized[3:].isdigit():
            confidence = 0.8  # Correct length and type distribution
        else:
            confidence = 0.1
        
        issues = []
        recommendations = []
        
        if not is_valid:
            if len(normalized) != 13:
                issues.append(f'Receipt number should be 13 characters, found {len(normalized)}')
            if not normalized[:3].isalpha():
                issues.append('First 3 characters should be letters')
            if not normalized[3:].isdigit():
                issues.append('Last 10 characters should be digits')
            
            recommendations.append('Verify receipt number format: XXX1234567890')
        
        return ValidationResult(
            field_name='receipt_number',
            is_valid=is_valid,
            confidence=confidence,
            extracted_value=receipt_number,
            normalized_value=normalized,
            issues=issues,
            recommendations=recommendations
        )
    
    def _validate_notice_type(self, notice_type: str) -> ValidationResult:
        """Valida tipo de aviso I-797"""
        valid_types = [
            'I-797A', 'I-797B', 'I-797C', 'I-797D', 'I-797E',
            'Approval Notice', 'Receipt Notice', 'Denial Notice',
            'Request for Evidence', 'Notice of Action'
        ]
        
        if not notice_type:
            return ValidationResult(
                field_name='notice_type',
                is_valid=False,
                confidence=0.0,
                extracted_value=notice_type,
                normalized_value='',
                issues=['Notice type is missing'],
                recommendations=['Look for notice type in header section']
            )
        
        normalized = notice_type.strip()
        
        # Check if it matches any valid type
        is_valid = any(valid_type.lower() in normalized.lower() for valid_type in valid_types)
        confidence = 0.9 if is_valid else 0.3
        
        return ValidationResult(
            field_name='notice_type',
            is_valid=is_valid,
            confidence=confidence,
            extracted_value=notice_type,
            normalized_value=normalized,
            issues=[] if is_valid else ['Unknown notice type'],
            recommendations=[] if is_valid else ['Verify notice type in document header']
        )
    
    def _validate_entity_name(self, name: str, entity_type: str) -> ValidationResult:
        """Valida nome de peticionário ou beneficiário"""
        if not name:
            return ValidationResult(
                field_name=entity_type,
                is_valid=False,
                confidence=0.0,
                extracted_value=name,
                normalized_value='',
                issues=[f'{entity_type.title()} name is missing'],
                recommendations=[f'Locate {entity_type} name in document']
            )
        
        # Basic validation
        normalized = ' '.join(name.strip().split())
        is_valid = len(normalized) >= 3 and not re.search(r'^\d+$', normalized)
        confidence = 0.8 if is_valid else 0.3
        
        return ValidationResult(
            field_name=entity_type,
            is_valid=is_valid,
            confidence=confidence,
            extracted_value=name,
            normalized_value=normalized,
            issues=[] if is_valid else [f'Invalid {entity_type} name format'],
            recommendations=[]
        )
    
    def _validate_date_field(self, date_str: str, field_name: str) -> ValidationResult:
        """Valida campo de data"""
        if not date_str:
            return ValidationResult(
                field_name=field_name,
                is_valid=False,
                confidence=0.0,
                extracted_value=date_str,
                normalized_value='',
                issues=[f'{field_name.replace("_", " ").title()} is missing'],
                recommendations=[f'Look for {field_name.replace("_", " ")} in document']
            )
        
        # Try to parse date
        formats = ['%B %d, %Y', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d']
        parsed_date = None
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                break
            except ValueError:
                continue
        
        if not parsed_date:
            return ValidationResult(
                field_name=field_name,
                is_valid=False,
                confidence=0.0,
                extracted_value=date_str,
                normalized_value='',
                issues=['Invalid date format'],
                recommendations=['Check date format and readability']
            )
        
        normalized = parsed_date.strftime('%Y-%m-%d')
        
        # Validate logical constraints
        issues = []
        current_date = datetime.now()
        
        if field_name == 'notice_date':
            if parsed_date > current_date:
                issues.append('Notice date is in the future')
        elif field_name == 'valid_to':
            if parsed_date < current_date:
                issues.append('Authorization has expired')
        
        return ValidationResult(
            field_name=field_name,
            is_valid=len(issues) == 0,
            confidence=0.95 if len(issues) == 0 else 0.6,
            extracted_value=date_str,
            normalized_value=normalized,
            issues=issues,
            recommendations=[]
        )

class TranslationCertificateValidator:
    """
    Validador para certificados de tradução
    """
    
    REQUIRED_PHRASES = [
        'complete and accurate',
        'competent to translate'
    ]
    
    def validate_translation_certificate(self, document_text: str) -> Dict[str, Any]:
        """
        Valida certificado de tradução conforme requisitos USCIS
        """
        issues = []
        found_phrases = []
        
        text_lower = document_text.lower()
        
        # Check for required phrases
        for phrase in self.REQUIRED_PHRASES:
            if phrase in text_lower:
                found_phrases.append(phrase)
            else:
                issues.append(f'Missing required phrase: "{phrase}"')
        
        # Check for translator information
        has_translator_name = bool(re.search(r'translator[^:]*:\s*([A-Za-z\s]+)', text_lower))
        has_signature = 'signature' in text_lower or 'signed' in text_lower
        has_date = bool(re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+\s+\d{1,2},\s+\d{4}', document_text))
        
        if not has_translator_name:
            issues.append('Translator name not clearly identified')
        if not has_signature:
            issues.append('Signature reference missing')
        if not has_date:
            issues.append('Translation date missing')
        
        # Calculate compliance score
        required_elements = 5  # 2 phrases + name + signature + date
        found_elements = len(found_phrases) + sum([has_translator_name, has_signature, has_date])
        compliance_score = (found_elements / required_elements) * 100
        
        is_valid = len(issues) == 0
        
        return {
            'document_type': 'translation_certificate',
            'is_valid': is_valid,
            'compliance_score': compliance_score,
            'found_phrases': found_phrases,
            'missing_phrases': [p for p in self.REQUIRED_PHRASES if p not in found_phrases],
            'has_translator_info': has_translator_name,
            'has_signature': has_signature,
            'has_date': has_date,
            'issues': issues,
            'uscis_compliant': is_valid and compliance_score >= 90
        }

def create_specialized_validators():
    """Factory function para criar instâncias dos validadores"""
    return {
        'passport': PassportValidator(),
        'i797': I797Validator(),
        'translation_certificate': TranslationCertificateValidator()
    }