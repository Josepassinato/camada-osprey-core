"""
Translation utilities for the Osprey backend
Provides translation services, language detection, and translation gate enforcement
"""

from .agent import (
    TranslationAgent,
    translate_text,
    translator,
)
from .gate import (
    TranslationGate,
    translation_gate,
)
from .service import (
    TranslationService,
    translate_form,
)
from .service import translate_text as translate_text_service
from .service import (
    translation_service,
)

__all__ = [
    # Translation Agent
    "TranslationAgent",
    "translator",
    "translate_text",
    # Translation Gate
    "TranslationGate",
    "translation_gate",
    # Translation Service
    "TranslationService",
    "translation_service",
    "translate_text_service",
    "translate_form",
]
