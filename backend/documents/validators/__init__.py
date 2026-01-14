"""
Document Validators Sub-package

This package contains specialized document validators for different document types.
"""

try:
    from .specialized import (
        I797Validator,
        PassportValidator,
        TranslationCertificateValidator,
        ValidationResult,
    )
except ImportError:
    # Graceful degradation if imports fail
    ValidationResult = None
    PassportValidator = None
    I797Validator = None
    TranslationCertificateValidator = None

__all__ = [
    "ValidationResult",
    "PassportValidator",
    "I797Validator",
    "TranslationCertificateValidator",
]
