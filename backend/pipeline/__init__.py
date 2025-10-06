"""
Document Analysis Pipeline - Modular Architecture
Sistema modular para análise de documentos com alta precisão
"""

from .mrz_parser import MRZParser, PassportValidator
from .pipeline_framework import DocumentAnalysisPipeline, PipelineStage
from .passport_ocr import PassportOCREngine

__version__ = "2.0.0"
__all__ = [
    "MRZParser",
    "PassportValidator", 
    "DocumentAnalysisPipeline",
    "PipelineStage",
    "PassportOCREngine"
]