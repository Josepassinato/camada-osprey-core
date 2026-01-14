"""
Visa Processing Package

This package contains all visa-related functionality including:
- Visa specifications and requirements
- Document mapping for different visa types
- Detailed visa information
- Auto-updater for visa information
- API endpoints for visa processing

Modules:
    specifications: Detailed specifications for each visa type
    document_mapping: Maps documents to visa requirements
    information: Comprehensive visa information
    auto_updater: Automated visa information updates
    api: API endpoints for visa operations
"""

from .document_mapping import (
    VisaDocumentMapper,
    get_smart_extraction_prompt,
    get_visa_document_requirements,
    visa_document_mapper,
)
from .information import VISA_DETAILED_INFO, get_visa_processing_info
from .specifications import (
    VISA_SPECIFICATIONS,
    get_common_issues,
    get_key_questions,
    get_required_documents,
    get_visa_specifications,
)

__all__ = [
    # Specifications
    'VISA_SPECIFICATIONS',
    'get_visa_specifications',
    'get_required_documents',
    'get_key_questions',
    'get_common_issues',
    
    # Document Mapping
    'VisaDocumentMapper',
    'visa_document_mapper',
    'get_visa_document_requirements',
    'get_smart_extraction_prompt',
    
    # Information
    'VISA_DETAILED_INFO',
    'get_visa_processing_info',
]
