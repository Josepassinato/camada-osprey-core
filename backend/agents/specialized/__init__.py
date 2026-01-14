"""
Specialized Immigration Agents Package

This package contains specialized AI agents for specific immigration tasks:
- Document validation and authenticity checking
- Form validation and data consistency
- Eligibility analysis for visa types
- USCIS compliance checking
- Immigration letter writing
- USCIS form translation
- Urgency triage and routing

Each agent is a domain expert that uses the LLM abstraction layer
and integrates with Dra. Paula's knowledge base.
"""

from .document_validator import DocumentValidationAgent, create_document_validator
from .form_validator import FormValidationAgent, create_form_validator
from .eligibility_analyst import EligibilityAnalysisAgent, create_eligibility_analyst
from .compliance_checker import ComplianceCheckAgent, create_compliance_checker
from .letter_writer import ImmigrationLetterWriterAgent, create_immigration_letter_writer
from .translator import USCISFormTranslatorAgent, create_uscis_form_translator
from .triage import UrgencyTriageAgent, create_urgency_triage
from .coordinator import SpecializedAgentCoordinator, create_specialized_agent_coordinator

__all__ = [
    # Agent classes
    "DocumentValidationAgent",
    "FormValidationAgent",
    "EligibilityAnalysisAgent",
    "ComplianceCheckAgent",
    "ImmigrationLetterWriterAgent",
    "USCISFormTranslatorAgent",
    "UrgencyTriageAgent",
    "SpecializedAgentCoordinator",
    # Factory functions
    "create_document_validator",
    "create_form_validator",
    "create_eligibility_analyst",
    "create_compliance_checker",
    "create_immigration_letter_writer",
    "create_uscis_form_translator",
    "create_urgency_triage",
    "create_specialized_agent_coordinator",
]
