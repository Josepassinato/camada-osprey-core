"""
Document Processing Package

This package contains all document-related functionality including:
- Document analysis and classification
- Document data extraction
- Document quality checking
- Document validation
- Cross-document consistency checking
"""

# Note: Some imports may fail until all modules are fully migrated
# Import what's available
try:
    from .analyzer import DocumentAnalyzer
except ImportError:
    DocumentAnalyzer = None

try:
    from .classifier import DocumentClassifier
except ImportError:
    DocumentClassifier = None

try:
    from .data_extractor import DocumentDataExtractor
except ImportError:
    DocumentDataExtractor = None

try:
    from .quality_checker import DocumentQualityChecker
except ImportError:
    DocumentQualityChecker = None

try:
    from .catalog import DocumentCatalog, DocumentType
except ImportError:
    DocumentCatalog = None
    DocumentType = None

try:
    from .recognition import EnhancedDocumentRecognitionAgent
except ImportError:
    EnhancedDocumentRecognitionAgent = None

try:
    from .consistency import CrossDocumentConsistencyEngine
except ImportError:
    CrossDocumentConsistencyEngine = None

try:
    from .metrics import DocumentAnalysisMetrics
except ImportError:
    DocumentAnalysisMetrics = None

__all__ = [
    "DocumentAnalyzer",
    "DocumentClassifier",
    "DocumentDataExtractor",
    "DocumentQualityChecker",
    "DocumentCatalog",
    "DocumentType",
    "EnhancedDocumentRecognitionAgent",
    "CrossDocumentConsistencyEngine",
    "DocumentAnalysisMetrics",
]
