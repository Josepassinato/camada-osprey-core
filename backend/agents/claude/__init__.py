"""
Claude-powered specialized agents for Imigrai.

Agents:
- Carlos: Eligibility Analyst
- Miguel: Document Reviewer
- Patricia: Strategy & Compliance Advisor
- Dr. Ricardo: Letter Writer (on-demand only)
"""

from .carlos import CarlosEligibilityAgent
from .miguel import MiguelDocumentAgent
from .patricia import PatriciaStrategyAgent
from .ricardo import RicardoLetterAgent

__all__ = [
    "CarlosEligibilityAgent",
    "MiguelDocumentAgent",
    "PatriciaStrategyAgent",
    "RicardoLetterAgent",
]
