"""
Consistency Stage - Pipeline Stage for Cross-Document Validation
Estágio do pipeline para validação de consistência entre documentos
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import asyncio

from .pipeline_framework import PipelineStage, PipelineContext
from .consistency_engine import consistency_engine, DocumentInfo, ConsistencyReport

logger = logging.getLogger(__name__)

class ConsistencyValidationStage(PipelineStage):
    """
    Pipeline stage for cross-document consistency validation
    """
    
    def __init__(self):
        super().__init__("consistency_validation", enabled=True)
        self.engine = consistency_engine
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """
        Process consistency validation across multiple documents
        """
        try:
            # Check if we have multiple documents to compare
            if not hasattr(context, 'all_documents') or len(context.all_documents) < 2:
                logger.info("Skipping consistency validation - insufficient documents for comparison")
                return context
            
            # Extract document information for consistency checking
            documents = []
            for doc_data in context.all_documents:
                doc_info = self._extract_document_info(doc_data)
                if doc_info:
                    documents.append(doc_info)
            
            if len(documents) < 2:
                logger.info("Skipping consistency validation - unable to extract info from multiple documents")
                return context
            
            # Perform consistency validation
            logger.info(f"Performing consistency validation across {len(documents)} documents")
            consistency_report = await self.engine.validate_consistency(documents)
            
            # Add results to context
            context.validation_results['consistency_validation'] = {
                'overall_status': consistency_report.overall_status,
                'confidence_score': consistency_report.confidence_score,
                'documents_analyzed': consistency_report.documents_analyzed,
                'critical_issues': consistency_report.critical_issues,
                'warning_issues': consistency_report.warning_issues,
                'info_issues': consistency_report.info_issues,
                'total_issues': len(consistency_report.issues),
                'issues': [self._serialize_issue(issue) for issue in consistency_report.issues],
                'recommendations': consistency_report.recommendations,
                'processing_time': consistency_report.processing_time
            }
            
            # Update overall context based on consistency results
            if consistency_report.overall_status == "INCONSISTENT":
                context.final_verdict = "REJEITADO"
                context.errors.append("Critical consistency issues found between documents")
            elif consistency_report.overall_status == "SUSPICIOUS":
                if context.final_verdict != "REJEITADO":
                    context.final_verdict = "NECESSITA_REVISÃO"
                context.warnings.append("Suspicious inconsistencies found - manual review recommended")
            
            # Update confidence score (take minimum of current and consistency)
            context.final_confidence = min(context.final_confidence, consistency_report.confidence_score)
            
            logger.info(f"Consistency validation completed: {consistency_report.overall_status}, "
                       f"confidence: {consistency_report.confidence_score:.2f}")
            
            return context
            
        except Exception as e:
            error_msg = f"Consistency validation stage failed: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            return context
    
    def _extract_document_info(self, doc_data: Dict[str, Any]) -> Optional[DocumentInfo]:
        """
        Extract DocumentInfo from document validation results
        """
        try:
            doc_info = DocumentInfo(
                document_type=doc_data.get('document_type', 'unknown'),
                document_id=doc_data.get('document_id', f"doc_{id(doc_data)}")
            )
            
            # Extract personal information from various document types
            validation_results = doc_data.get('validation_results', {})
            
            # From passport data
            if 'passport' in validation_results or 'mrz_data' in validation_results:
                passport_data = validation_results.get('passport', validation_results.get('mrz_data', {}))
                doc_info.full_name = passport_data.get('full_name', '')
                doc_info.passport_number = passport_data.get('passport_number', '')
                doc_info.nationality = passport_data.get('nationality', '')
                doc_info.country_issued = passport_data.get('issuing_country', '')
                
                # Parse date of birth
                dob_str = passport_data.get('date_of_birth', '')
                if dob_str:
                    doc_info.date_of_birth = self._parse_date(dob_str)
                
                # Parse expiration date
                exp_str = passport_data.get('expiration_date', '')
                if exp_str:
                    doc_info.expiration_date = self._parse_date(exp_str)
            
            # From birth certificate data
            if 'birth_certificate' in validation_results:
                birth_data = validation_results['birth_certificate']
                doc_info.full_name = doc_info.full_name or birth_data.get('full_name', '')
                doc_info.place_of_birth = birth_data.get('place_of_birth', '')
                doc_info.parents_names = birth_data.get('parents_names', [])
                
                # Parse date of birth
                dob_str = birth_data.get('date_of_birth', '')
                if dob_str and not doc_info.date_of_birth:
                    doc_info.date_of_birth = self._parse_date(dob_str)
            
            # From I-765 data
            if 'i765_ead' in validation_results:
                i765_data = validation_results['i765_ead']
                doc_info.full_name = doc_info.full_name or i765_data.get('full_name', '')
                doc_info.alien_number = i765_data.get('alien_number', '')
                doc_info.country_of_birth = i765_data.get('country_of_birth', '')
                doc_info.document_number = i765_data.get('document_number', '')
                
                # Parse dates
                dob_str = i765_data.get('date_of_birth', '')
                if dob_str and not doc_info.date_of_birth:
                    doc_info.date_of_birth = self._parse_date(dob_str)
                
                valid_from_str = i765_data.get('valid_from', '')
                if valid_from_str:
                    doc_info.issue_date = self._parse_date(valid_from_str)
                
                valid_until_str = i765_data.get('valid_until', '')
                if valid_until_str:
                    doc_info.expiration_date = self._parse_date(valid_until_str)
            
            # From I-797 data
            if 'i797' in validation_results:
                i797_data = validation_results['i797']
                doc_info.full_name = doc_info.full_name or i797_data.get('beneficiary_name', '')
                doc_info.alien_number = doc_info.alien_number or i797_data.get('alien_number', '')
                doc_info.document_number = doc_info.document_number or i797_data.get('receipt_number', '')
            
            # Extract names for better matching
            if doc_info.full_name:
                name_parts = doc_info.full_name.strip().split()
                if len(name_parts) >= 2:
                    doc_info.first_name = name_parts[0]
                    doc_info.last_name = name_parts[-1]
            
            # Set confidence and extraction method
            doc_info.confidence_score = doc_data.get('confidence_score', 0.8)
            doc_info.extraction_method = "pipeline_extraction"
            
            # Only return if we have enough information for consistency checking
            if doc_info.full_name or doc_info.passport_number or doc_info.alien_number:
                return doc_info
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract document info: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string in various formats"""
        if not date_str:
            return None
        
        try:
            # Try ISO format first
            if isinstance(date_str, str) and 'T' in date_str:
                return datetime.fromisoformat(date_str.split('T')[0]).date()
            elif isinstance(date_str, str):
                return datetime.fromisoformat(date_str).date()
            
            # If it's already a date object
            if hasattr(date_str, 'date'):
                return date_str.date()
            elif isinstance(date_str, date):
                return date_str
            
            return None
            
        except Exception:
            # Try other common formats
            formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%d-%m-%Y']
            
            for fmt in formats:
                try:
                    return datetime.strptime(str(date_str), fmt).date()
                except ValueError:
                    continue
            
            return None
    
    def _serialize_issue(self, issue) -> Dict[str, Any]:
        """Serialize ConsistencyIssue for JSON response"""
        return {
            'issue_type': issue.issue_type,
            'severity': issue.severity,
            'field_name': issue.field_name,
            'document1_id': issue.document1_id,
            'document2_id': issue.document2_id,
            'value1': str(issue.value1) if issue.value1 else None,
            'value2': str(issue.value2) if issue.value2 else None,
            'similarity_score': issue.similarity_score,
            'description': issue.description,
            'recommendation': issue.recommendation
        }

class MultiDocumentConsistencyPipeline:
    """
    Specialized pipeline for multi-document consistency validation
    """
    
    def __init__(self):
        self.consistency_stage = ConsistencyValidationStage()
    
    async def validate_documents(self, documents_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate consistency across multiple documents
        
        Args:
            documents_data: List of document data with validation results
        
        Returns:
            Consistency validation results
        """
        try:
            # Create a mock context with multiple documents
            context = PipelineContext(
                content_base64="",
                document_type="multi_document",
                user_id="consistency_check"
            )
            
            # Add all documents to context
            context.all_documents = documents_data
            
            # Process consistency validation
            result_context = await self.consistency_stage.process(context)
            
            # Return consistency results
            return result_context.validation_results.get('consistency_validation', {})
            
        except Exception as e:
            logger.error(f"Multi-document consistency validation failed: {e}")
            return {
                'overall_status': 'ERROR',
                'confidence_score': 0.0,
                'error': str(e)
            }

# Global instances
consistency_validation_stage = ConsistencyValidationStage()
multi_document_consistency_pipeline = MultiDocumentConsistencyPipeline()