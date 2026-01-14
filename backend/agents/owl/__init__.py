"""
Owl Agent Package

The Owl agent is an intelligent questionnaire conductor that guides users
through immigration form completion with contextual help and validation.

Key Features:
- Guided questionnaire sessions
- Field-specific guidance and validation
- Multi-language support (PT/EN)
- Real-time validation with Google Document AI
- AI-powered contextual assistance
- Visa-specific field filtering

Main Components:
- IntelligentOwlAgent: Core agent for questionnaire guidance
"""

from .agent import IntelligentOwlAgent

__all__ = [
    "IntelligentOwlAgent",
]
