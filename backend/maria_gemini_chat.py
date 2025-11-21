"""
Maria Chat usando Google Gemini via Emergent LLM Key
Gemini oferece conversação mais natural
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Configurar Emergent LLM Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')


class MariaGeminiChat:
    """
    Chat da Maria usando Gemini via Emergent LLM Key
    Mais natural e humanizado que GPT
    """
    
    def __init__(self):
        self.api_key = EMERGENT_LLM_KEY
        self.available = EMERGENT_LLM_KEY is not None
        
        if not self.available:
            print("⚠️ EMERGENT_LLM_KEY não configurada")
        else:
            print("✅ Maria Gemini Chat configurado com Emergent LLM Key")
    
    async def chat(
        self,
        user_message: str,
        system_prompt: str,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Chat com Gemini
        
        Args:
            user_message: Mensagem do usuário
            system_prompt: Prompt de sistema (personalidade da Maria)
            conversation_history: Histórico da conversa
        
        Returns:
            Dict com resposta
        """
        if not self.available:
            return {
                "success": False,
                "error": "Gemini API not configured"
            }
        
        try:
            # Gemini não tem "system" message separado
            # Vamos incluir o system prompt no início do contexto
            
            # Construir histórico para Gemini
            chat_history = []
            
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg["role"] == "user" else "model"
                    chat_history.append({
                        "role": role,
                        "parts": [msg["content"]]
                    })
            
            # Iniciar chat com histórico
            chat = self.model.start_chat(history=chat_history)
            
            # Adicionar system prompt ao primeiro user message se não houver histórico
            if not conversation_history:
                full_message = f"{system_prompt}\n\n---\n\nUsuário: {user_message}"
            else:
                full_message = user_message
            
            # Enviar mensagem
            response = chat.send_message(
                full_message,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            return {
                "success": True,
                "response": response.text,
                "model": "gemini-pro",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erro no chat Gemini: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": True
            }


# Singleton instance
maria_gemini = MariaGeminiChat()
