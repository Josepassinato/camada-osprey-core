"""
Maria Agent Package

Maria is Osprey's virtual assistant providing:
- Customer support (chat and voice)
- Emotional support with positive psychology
- USCIS information (no legal advice)
- Osprey platform promotion and sales
- Proactive follow-up via WhatsApp

This package contains all Maria-related functionality organized into modules:
- agent.py: Core Maria agent with personality and chat logic
- api.py: FastAPI endpoints for Maria interactions
- voice.py: Text-to-speech and speech-to-text using Google services
- whatsapp.py: WhatsApp integration via Baileys
- gemini_chat.py: Gemini-based chat implementation
"""

from .agent import MariaAgent, maria

__all__ = [
    "MariaAgent",
    "maria",
]
