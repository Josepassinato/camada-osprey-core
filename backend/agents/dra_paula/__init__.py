"""
Dra. Paula Agent Package

This package contains the Dra. Paula immigration specialist agent implementations.
Dra. Paula is a specialized agent for immigration document review and analysis.

Modules:
    - gemini_agent: Gemini-based implementation of Dra. Paula
    - hybrid_agent: Hybrid implementation combining multiple LLM providers
    - knowledge_base: Knowledge base management for Dra. Paula
"""

from backend.agents.dra_paula.gemini_agent import DraPaulaGeminiAgent
from backend.agents.dra_paula.hybrid_agent import HybridDraPaulaAgent
from backend.agents.dra_paula.knowledge_base import (
    DraPaulaKnowledgeBase,
    dra_paula_knowledge,
)

__all__ = [
    "DraPaulaGeminiAgent",
    "HybridDraPaulaAgent",
    "DraPaulaKnowledgeBase",
    "dra_paula_knowledge",
]
