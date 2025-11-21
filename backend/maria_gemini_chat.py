"""
Maria Chat usando Google Gemini em vez de OpenAI
Gemini oferece conversação mais natural
"""

import os
import google.generativeai as genai
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configurar Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class MariaGeminiChat:
    """
    Chat da Maria usando Gemini Pro
    Mais natural e humanizado que GPT
    """
    
    def __init__(self):
        # Use gemini-2.5-flash (latest and fastest) para chat
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.available = GEMINI_API_KEY is not None
        
        if not self.available:
            print("⚠️ GEMINI_API_KEY não configurada")
        
        # Configurações de geração
        self.generation_config = {
            "temperature": 0.9,  # Mais criativa e variada
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        # Safety settings (permitir conteúdo sobre imigração)
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"  # Permitir discussões sobre processos legais
            },
        ]
    
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
