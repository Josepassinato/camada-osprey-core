"""
Maria Chat using LLMClient with Gemini
Gemini offers more natural conversation
"""

import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from backend.llm.portkey_client import LLMClient
from backend.llm.types import ChatMessage, MessageRole

logger = logging.getLogger(__name__)


class MariaGeminiChat:
    """
    Chat da Maria usando Gemini via LLMClient
    Mais natural e humanizado que GPT
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.available = True
        logger.info("✅ Maria Gemini Chat configured with LLMClient")
    
    async def chat(
        self,
        user_message: str,
        system_prompt: str,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Chat with Gemini via LLMClient
        
        Args:
            user_message: User message
            system_prompt: System prompt (Maria's personality)
            conversation_history: Conversation history
        
        Returns:
            Dict with response
        """
        try:
            # Prepare messages
            messages = [
                ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)
            ]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    role = MessageRole.USER if msg.get("role") == "user" else MessageRole.ASSISTANT
                    messages.append(ChatMessage(role=role, content=msg.get("content", "")))
            
            # Add current user message
            messages.append(ChatMessage(role=MessageRole.USER, content=user_message))
            
            # Call LLM
            response = await self.llm_client.chat_completion(
                messages=[msg.model_dump() for msg in messages],
                model="gemini-2.0-flash-exp",
                temperature=0.8,
                max_tokens=1000
            )
            
            response_text = response["choices"][0]["message"]["content"]
            
            return {
                "success": True,
                "response": response_text,
                "model": "gemini-2.0-flash-exp",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error in Gemini chat: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "fallback": True
            }


# Singleton instance
maria_gemini = MariaGeminiChat()
