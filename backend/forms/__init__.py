"""
Forms Package

This package handles USCIS form processing, including form filling,
field extraction, and form structure management.

Modules:
- filler: USCIS form filling functionality
- structures: Friendly form structure definitions
- field_extraction: Field extraction engine for forms
- i129_overlay: I-129 form overlay filling
- debug: Debug utilities for form field inspection
"""

from backend.forms.filler import USCISFormFiller, FormFillerAgent, form_filler, form_filler_agent, fill_form_automatically
from backend.forms.field_extraction import FieldExtractionEngine, field_extraction_engine
from backend.forms.i129_overlay import I129OverlayFiller, i129_filler, fill_i129_form

__all__ = [
    'USCISFormFiller',
    'FormFillerAgent',
    'form_filler',
    'form_filler_agent',
    'fill_form_automatically',
    'FieldExtractionEngine',
    'field_extraction_engine',
    'I129OverlayFiller',
    'i129_filler',
    'fill_i129_form',
]
