"""
Passport-specific Pipeline Stages
Estágios especializados para processamento de passaportes
"""

import logging
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from .pipeline_framework import PipelineStage, PipelineContext, DocumentAnalysisPipeline
from .mrz_parser import passport_validator, MRZValidationError
from .passport_ocr import passport_ocr_engine

logger = logging.getLogger(__name__)

class PassportOCRStage(PipelineStage):
    """
    Estágio de OCR especializado para passaportes
    """
    
    def __init__(self):
        super().__init__("PassportOCR")
        self.ocr_engine = passport_ocr_engine
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Executa OCR especializado para passaporte"""
        try:
            logger.info(f"Processing passport OCR for document {context.document_id}")
            
            # Execute specialized passport OCR
            ocr_results = self.ocr_engine.extract_text_from_passport(
                context.content_base64, 
                context.document_type
            )
            
            # Store results in context
            context.ocr_results = ocr_results
            
            # Extract printed data for cross-validation
            context.printed_data = ocr_results.get('printed_data', {})
            
            logger.info(f"OCR completed. Confidence: {ocr_results.get('ocr_confidence', 0):.2f}")
            
            return context
            
        except Exception as e:
            error_msg = f"Passport OCR failed: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            
            # Provide fallback OCR results
            context.ocr_results = {
                'mrz_text': '',
                'full_text': 'OCR failed',
                'printed_data': {},
                'ocr_confidence': 0.0,
                'processing_method': 'failed'
            }
            
            return context

class MRZParsingStage(PipelineStage):
    """
    Estágio de parsing e validação de MRZ
    """
    
    def __init__(self):
        super().__init__("MRZParsing")
        self.validator = passport_validator
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Executa parsing e validação de MRZ"""
        try:
            logger.info(f"Processing MRZ for document {context.document_id}")
            
            # Get MRZ text from OCR results
            mrz_text = context.ocr_results.get('mrz_text', '')
            ocr_confidence = context.ocr_results.get('ocr_confidence', 0.8)
            
            if not mrz_text:
                raise MRZValidationError("No MRZ text found in OCR results")
            
            # Perform complete passport validation
            validation_result = self.validator.validate_passport(
                mrz_text=mrz_text,
                printed_data=context.printed_data,
                ocr_confidence=ocr_confidence
            )
            
            # Store results in context
            context.mrz_data = validation_result.mrz_data
            context.validation_results = {
                'validation_status': validation_result.validation_status,
                'confidence_score': validation_result.confidence_score,
                'consistency_check': validation_result.consistency_check,
                'issues': validation_result.issues,
                'recommendations': validation_result.recommendations
            }
            
            # Set final confidence and verdict
            context.final_confidence = validation_result.confidence_score * 100
            context.final_verdict = self._map_validation_status(validation_result.validation_status)
            
            # Add any issues as warnings
            if validation_result.issues:
                context.warnings.extend(validation_result.issues)
            
            logger.info(f"MRZ validation completed. Status: {validation_result.validation_status}, "
                       f"Confidence: {validation_result.confidence_score:.2f}")
            
            return context
            
        except MRZValidationError as e:
            error_msg = f"MRZ validation failed: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            context.final_verdict = "REJEITADO"
            return context
            
        except Exception as e:
            error_msg = f"MRZ processing error: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            context.final_verdict = "NECESSITA_REVISÃO"
            return context
    
    def _map_validation_status(self, status: str) -> str:
        """Maps validation status to system verdict"""
        mapping = {
            'VALID': 'APROVADO',
            'INVALID': 'REJEITADO', 
            'SUSPICIOUS': 'NECESSITA_REVISÃO'
        }
        return mapping.get(status, 'NECESSITA_REVISÃO')

class PassportClassificationStage(PipelineStage):
    """
    Estágio de classificação específico para passaportes
    """
    
    def __init__(self):
        super().__init__("PassportClassification")
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Executa classificação de passaporte"""
        try:
            logger.info(f"Classifying passport document {context.document_id}")
            
            # Basic classification based on MRZ presence and structure
            full_text = context.ocr_results.get('full_text', '')
            mrz_text = context.ocr_results.get('mrz_text', '')
            
            # Determine confidence based on passport characteristics
            confidence = 0.5  # Base confidence
            
            # Check for passport indicators
            passport_indicators = ['PASSPORT', 'PASAPORTE', 'PASSAPORTE', 'P<']
            for indicator in passport_indicators:
                if indicator in full_text.upper() or indicator in mrz_text.upper():
                    confidence += 0.15
            
            # Check MRZ structure
            if mrz_text and mrz_text.startswith('P<'):
                confidence += 0.2
                
            mrz_lines = mrz_text.split('\n') if mrz_text else []
            if len(mrz_lines) == 2 and all(len(line) == 44 for line in mrz_lines):
                confidence += 0.15
            
            # Store classification results
            context.classification_results = {
                'document_type': 'passport',
                'confidence': min(confidence, 1.0),
                'sub_type': 'passport_id_page',
                'indicators_found': [ind for ind in passport_indicators 
                                   if ind in full_text.upper() or ind in mrz_text.upper()],
                'mrz_structure_valid': len(mrz_lines) == 2 and all(len(line) == 44 for line in mrz_lines)
            }
            
            logger.info(f"Classification completed. Type: passport, Confidence: {confidence:.2f}")
            
            return context
            
        except Exception as e:
            error_msg = f"Classification error: {str(e)}"
            logger.error(error_msg)
            context.warnings.append(error_msg)
            
            # Provide default classification
            context.classification_results = {
                'document_type': 'passport',
                'confidence': 0.5,
                'sub_type': 'unknown',
                'error': error_msg
            }
            
            return context

def create_passport_pipeline() -> DocumentAnalysisPipeline:
    """
    Cria pipeline especializado para análise de passaportes
    """
    pipeline = DocumentAnalysisPipeline("PassportAnalysis")
    
    # Add stages in order
    pipeline.add_stages([
        PassportOCRStage(),
        PassportClassificationStage(), 
        MRZParsingStage(),
    ])
    
    return pipeline

# Global passport pipeline instance  
passport_pipeline = create_passport_pipeline()