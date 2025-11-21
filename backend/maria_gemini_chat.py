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
        Chat com Gemini via Emergent LLM Key
        
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
                "error": "Emergent LLM Key not configured"
            }
        
        try:
            # Criar nova instância de LlmChat para cada conversa
            import uuid
            session_id = f"maria_chat_{uuid.uuid4().hex[:8]}"
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=system_prompt
            ).with_model("gemini", "gemini-2.0-flash")
            
            # Se houver histórico, adicionar ao contexto
            # (A biblioteca gerencia o histórico internamente)
            
            # Criar mensagem do usuário
            user_msg = UserMessage(text=user_message)
            
            # Enviar mensagem e obter resposta
            response_text = await chat.send_message(user_msg)
            
            return {
                "success": True,
                "response": response_text,
                "model": "gemini-2.0-flash",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erro no chat Gemini (Emergent): {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "fallback": True
            }


# Singleton instance
maria_gemini = MariaGeminiChat()
