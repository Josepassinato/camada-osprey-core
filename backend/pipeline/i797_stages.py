"""
I-797 Specific Pipeline Stages
Estágios especializados para processamento de documentos I-797 USCIS
"""

import logging
from typing import Dict, List, Any, Optional
from .pipeline_framework import PipelineStage, PipelineContext, DocumentAnalysisPipeline
from .i797_validator import i797_validator, I797ValidationResult

logger = logging.getLogger(__name__)

class I797OCRStage(PipelineStage):
    """
    Estágio de OCR especializado para documentos I-797
    """
    
    def __init__(self):
        super().__init__("I797OCR")
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Executa OCR especializado para I-797"""
        try:
            logger.info(f"Processing I-797 OCR for document {context.document_id}")
            
            # Simulate I-797 OCR extraction (in production, would use real OCR)
            # Focus on key areas: header, receipt number, dates, case type
            
            sample_i797_text = """
            U.S. DEPARTMENT OF HOMELAND SECURITY
            U.S. Citizenship and Immigration Services
            
            I-797, Notice of Action
            
            Receipt Number: WAC2190012345
            Case Type: I-129 PETITION FOR A NONIMMIGRANT WORKER
            Priority Date: Not Available
            Notice Date: MAR 15, 2024
            Valid Until: SEP 15, 2026
            
            Petitioner: TECH COMPANY INC
            Beneficiary: JOHN SMITH
            
            THE ABOVE PETITION HAS BEEN APPROVED.
            """
            
            # Store OCR results
            context.ocr_results = {
                'full_text': sample_i797_text.strip(),
                'document_type_detected': 'i797',
                'ocr_confidence': 0.92,
                'processing_method': 'specialized_i797_ocr',
                'key_fields_detected': [
                    'receipt_number', 'case_type', 'notice_date', 
                    'petitioner', 'beneficiary'
                ]
            }
            
            logger.info(f"I-797 OCR completed. Confidence: 0.92")
            
            return context
            
        except Exception as e:
            error_msg = f"I-797 OCR failed: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            
            # Provide fallback OCR results
            context.ocr_results = {
                'full_text': 'OCR failed for I-797',
                'document_type_detected': 'unknown',
                'ocr_confidence': 0.0,
                'processing_method': 'failed'
            }
            
            return context

class I797ValidationStage(PipelineStage):
    """
    Estágio de validação específico para I-797
    """
    
    def __init__(self):
        super().__init__("I797Validation")
        self.validator = i797_validator
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Executa validação completa de I-797"""
        try:
            logger.info(f"Processing I-797 validation for document {context.document_id}")
            
            # Get text from OCR results
            document_text = context.ocr_results.get('full_text', '')
            
            if not document_text or document_text == 'OCR failed for I-797':
                raise ValueError("No valid text found for I-797 validation")
            
            # Perform I-797 validation
            validation_result = self.validator.validate_i797(
                document_text=document_text,
                extracted_data=context.ocr_results
            )
            
            # Store validation results
            context.validation_results = {
                'validation_status': validation_result.validation_status,
                'confidence_score': validation_result.confidence_score,
                'issues': validation_result.issues,
                'recommendations': validation_result.recommendations,
                'formatting_analysis': validation_result.formatting_analysis,
                'i797_data': validation_result.i797_data
            }
            
            # Set final confidence and verdict
            context.final_confidence = validation_result.confidence_score * 100
            context.final_verdict = self._map_validation_status(validation_result.validation_status)
            
            # Add any issues as warnings or errors
            if validation_result.issues:
                if validation_result.validation_status == "INVALID":
                    context.errors.extend(validation_result.issues)
                else:
                    context.warnings.extend(validation_result.issues)
            
            logger.info(f"I-797 validation completed. Status: {validation_result.validation_status}, "
                       f"Confidence: {validation_result.confidence_score:.2f}")
            
            return context
            
        except Exception as e:
            error_msg = f"I-797 validation error: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            context.final_verdict = "REJEITADO"
            return context
    
    def _map_validation_status(self, status: str) -> str:
        """Maps validation status to system verdict"""
        mapping = {
            'VALID': 'APROVADO',
            'INVALID': 'REJEITADO',
            'SUSPICIOUS': 'NECESSITA_REVISÃO'
        }
        return mapping.get(status, 'NECESSITA_REVISÃO')

class I797ClassificationStage(PipelineStage):
    """
    Estágio de classificação específico para I-797
    """
    
    def __init__(self):
        super().__init__("I797Classification")
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Executa classificação de documento I-797"""
        try:
            logger.info(f"Classifying I-797 document {context.document_id}")
            
            full_text = context.ocr_results.get('full_text', '')
            confidence = 0.5  # Base confidence
            
            # Check for I-797 indicators
            i797_indicators = [
                'I-797', 'Notice of Action', 'U.S. Department of Homeland Security',
                'U.S. Citizenship and Immigration Services', 'Receipt Number',
                'Case Type', 'USCIS'
            ]
            
            indicators_found = []
            for indicator in i797_indicators:
                if indicator.upper() in full_text.upper():
                    indicators_found.append(indicator)
                    confidence += 0.08
            
            # Determine sub-type based on content
            sub_type = "unknown"
            if "APPROVAL" in full_text.upper() or "APPROVED" in full_text.upper():
                sub_type = "approval_notice"
                confidence += 0.05
            elif "RECEIPT" in full_text.upper():
                sub_type = "receipt_notice"
                confidence += 0.05
            elif "REQUEST FOR EVIDENCE" in full_text.upper():
                sub_type = "rfe_notice"
                confidence += 0.05
            elif "DENIAL" in full_text.upper():
                sub_type = "denial_notice"
                confidence += 0.05
            
            # Store classification results
            context.classification_results = {
                'document_type': 'i797',
                'confidence': min(confidence, 1.0),
                'sub_type': sub_type,
                'indicators_found': indicators_found,
                'uscis_document': True
            }
            
            logger.info(f"I-797 classification completed. Type: {sub_type}, Confidence: {confidence:.2f}")
            
            return context
            
        except Exception as e:
            error_msg = f"I-797 classification error: {str(e)}"
            logger.error(error_msg)
            context.warnings.append(error_msg)
            
            # Provide default classification
            context.classification_results = {
                'document_type': 'i797',
                'confidence': 0.5,
                'sub_type': 'unknown',
                'error': error_msg
            }
            
            return context

class I797SecurityCheckStage(PipelineStage):
    """
    Estágio de verificações de segurança para I-797
    """
    
    def __init__(self):
        super().__init__("I797SecurityCheck")
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Executa verificações de segurança específicas do I-797"""
        try:
            logger.info(f"Running I-797 security checks for document {context.document_id}")
            
            security_issues = []
            security_score = 1.0
            
            validation_results = context.validation_results or {}
            i797_data = validation_results.get('i797_data')
            
            if i797_data:
                # Check Receipt Number validity
                if hasattr(i797_data, 'receipt_number_valid') and not i797_data.receipt_number_valid:
                    security_issues.append("CRITICAL: Invalid Receipt Number format")
                    security_score = 0.0
                
                # Check document authenticity via formatting
                formatting_analysis = validation_results.get('formatting_analysis', {})
                if not formatting_analysis.get('overall_valid', False):
                    security_issues.append("WARNING: Document formatting inconsistent with USCIS standards")
                    security_score -= 0.3
                
                # Check date validity
                if hasattr(i797_data, 'dates_consistent') and not i797_data.dates_consistent:
                    security_issues.append("WARNING: Date inconsistencies detected")
                    security_score -= 0.2
                
                # Check for expired documents (if has valid until date)
                if hasattr(i797_data, 'valid_until_date') and i797_data.valid_until_date:
                    from datetime import date
                    if i797_data.valid_until_date < date.today():
                        security_issues.append("WARNING: Document has expired")
                        security_score -= 0.1
            
            # Store security check results
            context.stage_results[self.stage_name] = {
                'security_score': max(security_score, 0.0),
                'security_issues': security_issues,
                'checks_performed': [
                    'receipt_number_validation',
                    'uscis_formatting_validation',
                    'date_consistency_validation',
                    'expiration_check'
                ]
            }
            
            # Add issues to context
            for issue in security_issues:
                if issue.startswith('CRITICAL'):
                    context.errors.append(issue)
                else:
                    context.warnings.append(issue)
            
            # Stop pipeline if critical security issues found
            if security_score == 0.0:
                context.should_stop = True
                context.final_verdict = "REJEITADO"
            
            logger.info(f"I-797 security checks completed. Score: {security_score:.2f}, "
                       f"Issues: {len(security_issues)}")
            
            return context
            
        except Exception as e:
            error_msg = f"I-797 security check error: {str(e)}"
            logger.error(error_msg)
            context.warnings.append(error_msg)
            return context

def create_i797_pipeline() -> DocumentAnalysisPipeline:
    """
    Cria pipeline especializado para análise de documentos I-797
    """
    pipeline = DocumentAnalysisPipeline("I797Analysis")
    
    # Add I-797 specific stages
    pipeline.add_stages([
        I797OCRStage(),
        I797ClassificationStage(),
        I797ValidationStage(),
        I797SecurityCheckStage()
    ])
    
    return pipeline

# Global I-797 pipeline instance
i797_pipeline = create_i797_pipeline()