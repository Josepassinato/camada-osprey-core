"""
Voice processing package for Osprey platform.

This package handles voice-based interactions for form filling assistance,
including voice input processing, WebSocket management, and real-time guidance.
"""

from backend.voice.agent import VoiceAgent, voice_agent
from backend.voice.websocket import VoiceWebSocketManager, voice_manager

__all__ = [
    "VoiceAgent",
    "voice_agent",
    "VoiceWebSocketManager",
    "voice_manager",
]
