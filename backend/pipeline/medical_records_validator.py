"""
Medical Records Validator - Specific Document Validator
Validador especializado para registros médicos
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
class MedicalRecordData:
    """Structured data from medical records"""
    # Patient Information
    patient_name: str = ""
    patient_id: str = ""
    date_of_birth: Optional[date] = None
    gender: str = ""
    address: str = ""
    
    # Medical Information
    record_type: str = ""  # Lab Report, Prescription, Medical Report, etc.
    record_date: Optional[date] = None
    provider_name: str = ""
    provider_address: str = ""
    medical_license: str = ""
    
    # Clinical Information
    diagnosis: List[str] = None
    medications: List[str] = None
    procedures: List[str] = None
    vital_signs: Dict[str, str] = None
    lab_results: Dict[str, str] = None
    
    # Document Metadata
    institution_name: str = ""
    document_id: str = ""
    page_number: Optional[int] = None
    
    # Privacy and Security
    contains_phi: bool = False  # Protected Health Information
    hipaa_compliant: bool = False
    
    # Validation
    confidence_score: float = 0.0
    validation_status: str = "PENDING"  # VALID, INVALID, SUSPICIOUS
    issues: List[str] = None
    
    def __post_init__(self):
        if self.diagnosis is None:
            self.diagnosis = []
        if self.medications is None:
            self.medications = []
        if self.procedures is None:
            self.procedures = []
        if self.vital_signs is None:
            self.vital_signs = {}
        if self.lab_results is None:
            self.lab_results = {}
        if self.issues is None:
            self.issues = []

class MedicalRecordsValidator:
    """
    Specialized validator for medical records
    Handles various types of medical documents while respecting privacy
    """
    
    def __init__(self):
        # Medical record type patterns
        self.record_type_patterns = {
            'lab_report': [
                r'laboratory\s+report',
                r'lab\s+results',
                r'pathology\s+report',
                r'blood\s+test',
                r'urine\s+analysis',
                r'relatório\s+laboratorial'
            ],
            'prescription': [
                r'prescription',
                r'rx',
                r'medication\s+list',
                r'receita\s+médica',
                r'prescrição'
            ],
            'medical_report': [
                r'medical\s+report',
                r'clinical\s+summary',
                r'discharge\s+summary',
                r'consultation\s+report',
                r'relatório\s+médico'
            ],
            'vaccination_record': [
                r'vaccination\s+record',
                r'immunization\s+record',
                r'vaccine\s+card',
                r'cartão\s+de\s+vacinação'
            ],
            'imaging_report': [
                r'radiology\s+report',
                r'x-ray\s+report',
                r'mri\s+report',
                r'ct\s+scan',
                r'ultrasound',
                r'relatório\s+de\s+imagem'
            ]
        }
        
        # General medical document patterns
        self.patterns = {
            'patient_name': [
                r'(?:patient\s+name|nome\s+do\s+paciente)[:\s]*([A-Z][A-Za-z\s\-\']{3,50})',
                r'(?:name|nome)[:\s]*([A-Z][A-Za-z\s\-\']{3,50})',
                r'(?:patient|paciente)[:\s]*([A-Z][A-Za-z\s\-\']{3,50})',
            ],
            'patient_id': [
                r'(?:patient\s+id|id\s+do\s+paciente|medical\s+record\s+number|mrn)[:\s#]*([A-Z0-9\-]{4,20})',
                r'(?:chart\s+number|número\s+do\s+prontuário)[:\s#]*([A-Z0-9\-]{4,20})',
                r'(?:account\s+number)[:\s#]*([A-Z0-9\-]{4,20})',
            ],
            'date_of_birth': [
                r'(?:date\s+of\s+birth|dob|data\s+de\s+nascimento)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:born|nascido)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
            ],
            'gender': [
                r'(?:gender|sex|sexo|gênero)[:\s]*(male|female|m|f|masculino|feminino)',
            ],
            'record_date': [
                r'(?:date|data)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:report\s+date|data\s+do\s+relatório)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:service\s+date|data\s+do\s+serviço)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
            ],
            'provider_name': [
                r'(?:physician|doctor|dr\.?\s+|médico|doutor)[:\s]*([A-Z][A-Za-z\s\-\'\.]{3,50})',
                r'(?:attending|provider|provedor)[:\s]*([A-Z][A-Za-z\s\-\'\.]{3,50})',
                r'(?:ordering\s+physician)[:\s]*([A-Z][A-Za-z\s\-\'\.]{3,50})',
            ],
            'medical_license': [
                r'(?:license|licença|crmn)[:\s#]*([A-Z0-9\-]{4,15})',
                r'(?:medical\s+license\s+number)[:\s#]*([A-Z0-9\-]{4,15})',
            ],
            'institution': [
                r'(?:hospital|clinic|laboratory|laboratório|clínica)[:\s]*([A-Z][A-Za-z0-9\s,\-\.&]{5,60})',
                r'(?:medical\s+center|centro\s+médico)[:\s]*([A-Z][A-Za-z0-9\s,\-\.&]{5,60})',
            ],
            'diagnosis': [
                r'(?:diagnosis|diagnóstico|impression|impressão)[:\s]*([A-Za-z0-9\s,\-\.;]{5,100})',
                r'(?:primary\s+diagnosis)[:\s]*([A-Za-z0-9\s,\-\.;]{5,100})',
                r'(?:icd.*?code)[:\s]*([A-Z]\d{2}\.?\d?)',
            ],
            'medications': [
                r'(?:medication|medicamento|drug|droga)[:\s]*([A-Za-z0-9\s,\-\.]{3,50})',
                r'(?:prescription|prescrição|rx)[:\s]*([A-Za-z0-9\s,\-\.]{3,50})',
                r'(?:take|tomar|use)[:\s]*([A-Za-z0-9\s,\-\.]{3,50})',
            ],
            'procedures': [
                r'(?:procedure|procedimento|surgery|cirurgia)[:\s]*([A-Za-z0-9\s,\-\.]{5,80})',
                r'(?:operation|operação|treatment|tratamento)[:\s]*([A-Za-z0-9\s,\-\.]{5,80})',
            ],
            'vital_signs': [
                r'(?:blood\s+pressure|pressão\s+arterial|bp)[:\s]*(\d{2,3}/\d{2,3})',
                r'(?:temperature|temperatura)[:\s]*(\d{2,3}\.?\d?\s*°?[CF]?)',
                r'(?:heart\s+rate|pulse|frequência\s+cardíaca)[:\s]*(\d{2,3})',
                r'(?:weight|peso)[:\s]*(\d{2,3}\.?\d?\s*(?:kg|lb|lbs)?)',
                r'(?:height|altura)[:\s]*(\d{1,2}\'?\s*\d{0,2}\"?|\d{2,3}\s*cm)',
            ]
        }
        
        # Medical document indicators
        self.medical_indicators = [
            'patient', 'doctor', 'physician', 'hospital', 'clinic', 'medical',
            'diagnosis', 'prescription', 'medication', 'laboratory', 'pathology',
            'radiology', 'blood', 'urine', 'vital signs', 'medical record',
            'health', 'treatment', 'therapy', 'surgery', 'procedure'
        ]
        
        # Protected Health Information (PHI) indicators
        self.phi_indicators = [
            'social security number', 'ssn', 'date of birth', 'address',
            'phone number', 'email', 'medical record number', 'account number',
            'patient id', 'insurance id'
        ]
    
    async def validate_medical_record(self, 
                                    document_content: str,
                                    document_type: str = "medical_record") -> MedicalRecordData:
        """
        Validate and extract data from medical record
        
        Args:
            document_content: Base64 image or text content
            document_type: Document type identifier
        
        Returns:
            MedicalRecordData with extracted and validated information
        """
        try:
            result = MedicalRecordData()
            
            # 1. Extract text if image provided
            if self._is_base64_image(document_content):
                ocr_result = await real_ocr_engine.extract_text_from_image(
                    document_content, 
                    mode="document",
                    language="auto"  # Medical records can be in multiple languages
                )
                text_content = ocr_result.text
                base_confidence = ocr_result.confidence
            else:
                text_content = document_content
                base_confidence = 0.9
            
            # 2. Verify this is actually a medical record
            if not self._verify_medical_record(text_content):
                result.validation_status = "INVALID"
                result.issues.append("Document does not appear to be a medical record")
                return result
            
            # 3. Identify specific medical record type
            result.record_type = self._identify_medical_record_type(text_content)
            
            # 4. Check for PHI content
            result.contains_phi = self._check_phi_content(text_content)
            
            # 5. Extract structured data
            result = await self._extract_medical_data(text_content, result)
            
            # 6. Validate extracted data
            validation_result = self._validate_medical_data(result)
            result.validation_status = validation_result['status']
            result.issues.extend(validation_result['issues'])
            
            # 7. Calculate confidence score
            result.confidence_score = self._calculate_confidence(result, base_confidence)
            
            logger.info(f"Medical record validation completed: type={result.record_type}, status={result.validation_status}, confidence={result.confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Medical record validation failed: {e}")
            result = MedicalRecordData()
            result.validation_status = "INVALID"
            result.issues.append(f"Validation error: {str(e)}")
            return result
    
    def _is_base64_image(self, content: str) -> bool:
        """Check if content is base64 encoded image"""
        return (content.startswith('data:image/') or 
                (len(content) > 100 and content.replace('+', '').replace('/', '').replace('=', '').isalnum()))
    
    def _verify_medical_record(self, text: str) -> bool:
        """Verify this is a medical record document"""
        text_lower = text.lower()
        
        found_indicators = sum(1 for indicator in self.medical_indicators 
                             if indicator in text_lower)
        
        # Also check for specific record type patterns
        record_pattern_found = any(
            any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
            for patterns in self.record_type_patterns.values()
        )
        
        return found_indicators >= 3 or record_pattern_found
    
    def _identify_medical_record_type(self, text: str) -> str:
        """Identify specific type of medical record"""
        for record_type, patterns in self.record_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return record_type.upper().replace('_', ' ')
        
        return "GENERAL_MEDICAL_RECORD"
    
    def _check_phi_content(self, text: str) -> bool:
        """Check if document contains Protected Health Information"""
        text_lower = text.lower()
        
        phi_found = sum(1 for indicator in self.phi_indicators 
                       if indicator in text_lower)
        
        # Also check for specific PHI patterns (SSN, phone numbers, etc.)
        phi_patterns = [
            r'\d{3}[-\s]?\d{2}[-\s]?\d{4}',  # SSN
            r'\(\d{3}\)\s*\d{3}[-\s]?\d{4}',  # Phone number
            r'\d{1,5}\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd)',  # Address
        ]
        
        pattern_found = any(re.search(pattern, text) for pattern in phi_patterns)
        
        return phi_found >= 2 or pattern_found
    
    async def _extract_medical_data(self, text: str, result: MedicalRecordData) -> MedicalRecordData:
        """Extract structured data from medical record text"""
        
        # Extract patient name
        for pattern in self.patterns['patient_name']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name_candidate = match.group(1).strip()
                # Filter out obvious non-names
                if not any(word in name_candidate.lower() for word in ['hospital', 'clinic', 'report', 'record']):
                    result.patient_name = name_candidate
                    break
        
        # Extract patient ID
        for pattern in self.patterns['patient_id']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.patient_id = match.group(1).strip()
                break
        
        # Extract date of birth
        for pattern in self.patterns['date_of_birth']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result.date_of_birth = self._parse_date(match.group(1))
                    break
                except:
                    continue
        
        # Extract gender
        for pattern in self.patterns['gender']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                gender_raw = match.group(1).upper()
                if gender_raw in ['M', 'MALE', 'MASCULINO']:
                    result.gender = "MALE"
                elif gender_raw in ['F', 'FEMALE', 'FEMININO']:
                    result.gender = "FEMALE"
                break
        
        # Extract record date
        for pattern in self.patterns['record_date']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result.record_date = self._parse_date(match.group(1))
                    break
                except:
                    continue
        
        # Extract provider name
        for pattern in self.patterns['provider_name']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.provider_name = match.group(1).strip()
                break
        
        # Extract medical license
        for pattern in self.patterns['medical_license']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.medical_license = match.group(1).strip()
                break
        
        # Extract institution name
        for pattern in self.patterns['institution']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.institution_name = match.group(1).strip()
                break
        
        # Extract diagnosis information
        for pattern in self.patterns['diagnosis']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                diagnosis = match.strip()
                if len(diagnosis) > 3 and diagnosis not in result.diagnosis:
                    result.diagnosis.append(diagnosis)
        
        # Extract medications
        for pattern in self.patterns['medications']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                medication = match.strip()
                if len(medication) > 2 and medication not in result.medications:
                    result.medications.append(medication)
        
        # Extract procedures
        for pattern in self.patterns['procedures']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                procedure = match.strip()
                if len(procedure) > 4 and procedure not in result.procedures:
                    result.procedures.append(procedure)
        
        # Extract vital signs
        for pattern in self.patterns['vital_signs']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if 'pressure' in pattern or 'bp' in pattern:
                    result.vital_signs['blood_pressure'] = match
                elif 'temperature' in pattern:
                    result.vital_signs['temperature'] = match
                elif 'heart' in pattern or 'pulse' in pattern:
                    result.vital_signs['heart_rate'] = match
                elif 'weight' in pattern:
                    result.vital_signs['weight'] = match
                elif 'height' in pattern:
                    result.vital_signs['height'] = match
        
        return result
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string in various formats"""
        date_str = date_str.strip()
        formats = ['%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _validate_medical_data(self, result: MedicalRecordData) -> Dict[str, Any]:
        """Validate extracted medical record data"""
        issues = []
        
        # Check required fields
        if not result.patient_name:
            issues.append("Patient name not found")
        elif len(result.patient_name) < 3:
            issues.append("Patient name appears incomplete")
        
        if not result.record_type or result.record_type == "GENERAL_MEDICAL_RECORD":
            issues.append("Could not identify specific medical record type")
        
        if not result.record_date:
            issues.append("Record date not found")
        else:
            # Check if date is reasonable
            today = date.today()
            if result.record_date > today:
                issues.append("Record date is in the future")
            elif result.record_date < date(1900, 1, 1):
                issues.append("Record date is unreasonably old")
        
        # Validate date of birth if present
        if result.date_of_birth:
            today = date.today()
            if result.date_of_birth > today:
                issues.append("Date of birth is in the future")
            elif result.date_of_birth < date(1900, 1, 1):
                issues.append("Date of birth is unreasonably old")
        
        # Check for medical content
        if not result.diagnosis and not result.medications and not result.procedures and not result.vital_signs:
            issues.append("No medical content found (diagnosis, medications, procedures, or vital signs)")
        
        # Privacy check
        if result.contains_phi and not result.hipaa_compliant:
            issues.append("Document contains PHI but HIPAA compliance not verified")
        
        # Provider information
        if not result.provider_name and not result.institution_name:
            issues.append("No healthcare provider information found")
        
        # Determine status
        critical_issues = len([i for i in issues if any(word in i.lower() 
                              for word in ['not found', 'future', 'unreasonably'])])
        
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
    
    def _calculate_confidence(self, result: MedicalRecordData, base_confidence: float) -> float:
        """Calculate overall confidence score"""
        confidence = base_confidence * 0.25  # Base OCR confidence (25%)
        
        # Patient identification (25%)
        patient_score = 0.0
        if result.patient_name:
            patient_score += 0.15
        if result.patient_id:
            patient_score += 0.05
        if result.date_of_birth:
            patient_score += 0.05
        
        confidence += patient_score
        
        # Medical content (30%)
        content_score = 0.0
        if result.diagnosis:
            content_score += 0.10
        if result.medications:
            content_score += 0.08
        if result.procedures:
            content_score += 0.06
        if result.vital_signs:
            content_score += 0.06
        
        confidence += content_score
        
        # Provider and institutional info (10%)
        if result.provider_name or result.institution_name:
            confidence += 0.10
        
        # Validation status (10%)
        status_scores = {'VALID': 0.10, 'SUSPICIOUS': 0.05, 'INVALID': 0.0}
        confidence += status_scores.get(result.validation_status, 0.0)
        
        return min(confidence, 1.0)

class MedicalRecordsValidationStage(PipelineStage):
    """
    Pipeline stage for medical records validation
    """
    
    def __init__(self):
        super().__init__("medical_records_validation", enabled=True)
        self.validator = MedicalRecordsValidator()
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process medical record validation"""
        try:
            # Only process if document is classified as medical record
            if context.document_type.lower() not in ['medical_record', 'medical_report', 'lab_report', 'prescription', 'registro_medico']:
                logger.info(f"Skipping medical record validation for document type: {context.document_type}")
                return context
            
            # Validate medical record
            result = await self.validator.validate_medical_record(
                context.content_base64,
                context.document_type
            )
            
            # Add results to context
            context.validation_results['medical_record'] = {
                'patient_name': result.patient_name,
                'patient_id': result.patient_id,
                'date_of_birth': result.date_of_birth.isoformat() if result.date_of_birth else None,
                'gender': result.gender,
                'address': result.address,
                'record_type': result.record_type,
                'record_date': result.record_date.isoformat() if result.record_date else None,
                'provider_name': result.provider_name,
                'provider_address': result.provider_address,
                'medical_license': result.medical_license,
                'diagnosis': result.diagnosis,
                'medications': result.medications,
                'procedures': result.procedures,
                'vital_signs': result.vital_signs,
                'lab_results': result.lab_results,
                'institution_name': result.institution_name,
                'document_id': result.document_id,
                'page_number': result.page_number,
                'contains_phi': result.contains_phi,
                'hipaa_compliant': result.hipaa_compliant,
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
            
            logger.info(f"Medical record validation completed: {result.validation_status}, confidence: {result.confidence_score:.2f}")
            
            return context
            
        except Exception as e:
            error_msg = f"Medical record validation stage failed: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            return context

# Global instances
medical_records_validator = MedicalRecordsValidator()
medical_records_validation_stage = MedicalRecordsValidationStage()