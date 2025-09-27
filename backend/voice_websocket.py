import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from voice_agent import voice_agent

logger = logging.getLogger(__name__)

class VoiceWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, Dict] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.sessions[session_id] = {
            "connected_at": asyncio.get_event_loop().time(),
            "last_activity": asyncio.get_event_loop().time()
        }
        
        logger.info(f"Voice WebSocket connected: {session_id}")
        
        # Send welcome message
        await self.send_personal_message(session_id, {
            "type": "connection_established",
            "session_id": session_id,
            "capabilities": ["voice_guidance", "form_validation", "step_assistance"],
            "message": "Assistente de voz conectado. Posso ajudá-lo com sua aplicação de imigração."
        })
    
    def disconnect(self, session_id: str):
        """Disconnect a WebSocket client"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.sessions:
            del self.sessions[session_id]
        logger.info(f"Voice WebSocket disconnected: {session_id}")
    
    async def send_personal_message(self, session_id: str, message: dict):
        """Send message to specific session"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
                self.sessions[session_id]["last_activity"] = asyncio.get_event_loop().time()
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def handle_message(self, session_id: str, message: dict) -> dict:
        """Handle incoming message from client"""
        try:
            # Update last activity
            if session_id in self.sessions:
                self.sessions[session_id]["last_activity"] = asyncio.get_event_loop().time()
            
            # Process message through voice agent
            response = await voice_agent.process_voice_message(session_id, message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling message from {session_id}: {e}")
            return {
                "type": "error", 
                "message": "Erro ao processar mensagem",
                "error": str(e)
            }
    
    def get_session_count(self) -> int:
        """Get number of active sessions"""
        return len(self.active_connections)
    
    def get_session_info(self, session_id: str) -> dict:
        """Get session information"""
        return self.sessions.get(session_id, {})

# Global manager instance
voice_manager = VoiceWebSocketManager()