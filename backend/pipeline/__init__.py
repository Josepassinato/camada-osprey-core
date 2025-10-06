"""
Document Analysis Pipeline - Modular Architecture
Sistema modular para análise de documentos com alta precisão
"""

from .mrz_parser import MRZParser, PassportValidator
from .pipeline_framework import DocumentAnalysisPipeline, PipelineStage
from .passport_ocr import PassportOCREngine
from .passport_stages import passport_pipeline, create_passport_pipeline
from .integration import pipeline_integrator

__version__ = "2.0.0"
__all__ = [
    "MRZParser",
    "PassportValidator", 
    "DocumentAnalysisPipeline",
    "PipelineStage",
    "PassportOCREngine",
    "passport_pipeline",
    "create_passport_pipeline",
    "pipeline_integrator"
]