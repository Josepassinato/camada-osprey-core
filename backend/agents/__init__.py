"""
AI Agents Package

This package contains all AI agent implementations for the Osprey platform,
including conversational assistants, document processors, and specialized
immigration consultants.

Sub-packages:
    - maria/: Maria conversational assistant (voice, chat, WhatsApp)
    - dra_paula/: Dra. Paula immigration specialist agents
    - owl/: Owl intelligent agent for complex reasoning
    - specialized/: Specialized agents (validators, analysts, writers)
    - qa/: Quality assurance and feedback agents
    - oracle/: Oracle consultant agent

Modules:
    - base.py: Base agent class with common LLM interaction patterns
    - immigration_expert.py: Immigration expert agent (Dra. Paula B2C)
"""

# Don't import BaseAgent at package level to avoid circular imports
# Import it explicitly when needed: from agents.base import BaseAgent

__all__ = [
    "BaseAgent",
    "ImmigrationExpert",
    "create_immigration_expert",
]
