"""
Assistente Conversacional de Imigração com IA
Responde dúvidas em linguagem simples e contextual
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

# Initialize emergent integrations client
emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')

def create_llm_client(system_message: str, session_id: str) -> LlmChat:
    """Create LlmChat instance with required parameters"""
    return LlmChat(
        api_key=emergent_llm_key,
        session_id=session_id,
        system_message=system_message
    )

class ConversationalAssistant:
    """Assistente conversacional que ajuda usuários com dúvidas sobre imigração"""
    
    def __init__(self):
        self.conversation_history = {}  # Armazena histórico por session_id
    
    def _get_system_prompt(self, language_mode: str = "simple", visa_type: str = None) -> str:
        """Gera prompt do sistema baseado no modo de linguagem"""
        
        if language_mode == "simple":
            base_prompt = """
Você é um assistente amigável e paciente que ajuda pessoas com processos de imigração americana.

IMPORTANTE - Seu Estilo:
- Use linguagem MUITO SIMPLES, como se estivesse explicando para um amigo
- Evite jargão técnico. Se usar, explique imediatamente
- Use analogias do dia-a-dia
- Seja encorajador e empático
- Responda em português brasileiro

NUNCA:
- Dê conselhos legais diretos ("você deve fazer X")
- Garanta resultados ("sua aplicação será aprovada")
- Assuste o usuário desnecessariamente

SEMPRE:
- Use frases como "Geralmente o USCIS pede...", "Normalmente é necessário..."
- Ofereça consultar um advogado para casos complexos
- Explique o "por quê" das coisas
- Seja paciente com perguntas repetidas

Exemplos de como responder:

Pergunta técnica: "O que é peticionário?"
Sua resposta: "Peticionário é um nome complicado, né? 😊 É simplesmente a pessoa que está pedindo o visto para você. Por exemplo, se seu marido americano está pedindo para você vir morar nos EUA, ELE é o peticionário. Você é a pessoa que vai receber o visto (beneficiário). Pensando assim fica mais fácil!"

Pergunta sobre documentos: "Que documentos preciso?"
Sua resposta: "Vou te explicar de um jeito simples! Os documentos principais são:
• Seu passaporte (tem que estar valendo ainda)
• Certidões (nascimento, casamento se tiver)
• Fotos suas (tipo foto 3x4)
• Comprovante de onde você mora
Mas o tipo de visto que você quer muda um pouco isso. Me conta, qual visto você está buscando?"
"""
        else:  # technical mode
            base_prompt = """
You are a knowledgeable immigration assistant providing accurate information about U.S. immigration processes.

GUIDELINES:
- Use official USCIS terminology
- Provide precise, technical information
- Reference specific forms and requirements
- Respond in Portuguese or English based on user's language

NEVER:
- Provide legal advice
- Guarantee outcomes
- Make unauthorized interpretations of law

ALWAYS:
- Cite USCIS sources when relevant
- Recommend legal consultation for complex cases
- Provide disclaimers about information being educational
"""
        
        if visa_type:
            base_prompt += f"\n\nCONTEXTO: O usuário está trabalhando em uma aplicação {visa_type}. Adapte suas respostas para esse contexto específico."
        
        return base_prompt
    
    async def chat(
        self,
        session_id: str,
        user_message: str,
        language_mode: str = "simple",
        visa_type: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Processa mensagem do usuário e retorna resposta conversacional"""
        
        try:
            # Inicializar histórico se não existir
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            # Adicionar contexto do usuário se disponível
            context_info = ""
            if user_context:
                context_info = f"\nContexto do usuário: {json.dumps(user_context, ensure_ascii=False)}"
            
            # Chamar OpenAI
            llm = create_llm_client(
                system_message=self._get_system_prompt(language_mode, visa_type) + context_info,
                session_id=session_id
            )
            
            # Build conversation history
            conversation = ""
            for msg in self.conversation_history[session_id][-10:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation += f"{role}: {msg['content']}\n"
            
            conversation += f"User: {user_message}\n"
            
            response = llm.send_message(
                conversation,
                model="gpt-4o",
                max_tokens=800,
                temperature=0.7
            )
            
            assistant_message = response.strip()
            
            # Atualizar histórico
            self.conversation_history[session_id].append({
                "role": "user",
                "content": user_message
            })
            self.conversation_history[session_id].append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Detectar se é uma pergunta sobre termos específicos
            suggestions = self._generate_suggestions(user_message, visa_type)
            
            return {
                "success": True,
                "response": assistant_message,
                "suggestions": suggestions,
                "conversation_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in conversational chat: {e}")
            
            # Fallback response
            fallback_response = self._get_fallback_response(user_message)
            
            return {
                "success": False,
                "response": fallback_response,
                "error": str(e),
                "suggestions": [],
                "conversation_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _generate_suggestions(self, user_message: str, visa_type: Optional[str]) -> List[str]:
        """Gera sugestões de perguntas relacionadas"""
        
        # Sugestões baseadas em palavras-chave
        message_lower = user_message.lower()
        
        suggestions = []
        
        if "documento" in message_lower or "preciso" in message_lower:
            suggestions = [
                "Quais documentos são obrigatórios?",
                "Como organizar meus documentos?",
                "Preciso traduzir documentos?"
            ]
        elif "tempo" in message_lower or "demora" in message_lower:
            suggestions = [
                "Quanto tempo demora o processo?",
                "Como acompanhar meu caso?",
                "O que fazer se demorar muito?"
            ]
        elif "entrevista" in message_lower:
            suggestions = [
                "Como me preparar para entrevista?",
                "Que perguntas fazem na entrevista?",
                "Posso levar tradutor?"
            ]
        elif "dinheiro" in message_lower or "taxa" in message_lower or "custo" in message_lower:
            suggestions = [
                "Quanto custa o processo?",
                "Quais são as taxas do USCIS?",
                "Preciso comprovar renda?"
            ]
        else:
            # Sugestões gerais baseadas em visa_type
            if visa_type == "I-130":
                suggestions = [
                    "Como provar meu relacionamento?",
                    "Quanto tempo demora I-130?",
                    "Que documentos de casamento preciso?"
                ]
            elif visa_type == "H-1B":
                suggestions = [
                    "Meu empregador faz o pedido?",
                    "Quanto tempo demora H-1B?",
                    "Preciso de diploma específico?"
                ]
            else:
                suggestions = [
                    "Como começar minha aplicação?",
                    "Quanto custa todo o processo?",
                    "Preciso de advogado?"
                ]
        
        return suggestions[:3]  # Retornar apenas 3 sugestões
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Resposta de fallback se IA falhar"""
        
        message_lower = user_message.lower()
        
        if "documento" in message_lower:
            return """
Entendo que você tem dúvida sobre documentos! 📄

Os documentos principais geralmente incluem:
• Passaporte válido
• Certidões (nascimento, casamento)
• Fotos
• Comprovante de endereço

Mas isso varia pelo tipo de visto. Você pode me contar mais sobre seu caso? Ou consulte nossa lista completa de requisitos na seção "Checklist".

💡 Para orientação personalizada, recomendo consultar um advogado de imigração.
"""
        elif "tempo" in message_lower or "demora" in message_lower:
            return """
Sobre o tempo de processamento ⏱️

Geralmente varia muito:
• I-130: 12-18 meses
• H-1B: 3-6 meses
• I-539: 6-12 meses

Mas atenção: esses são tempos aproximados. O USCIS pode demorar mais ou menos dependendo do caso.

Você pode acompanhar seu caso no site do USCIS com o número de recibo.
"""
        else:
            return """
Obrigado pela sua pergunta! 😊

Desculpe, estou com dificuldade para processar sua mensagem no momento. 

Você pode:
• Reformular sua pergunta de outra forma
• Consultar nossos guias na seção "Educação"
• Falar com nosso suporte

💡 Lembre-se: para orientação legal específica, sempre consulte um advogado de imigração licenciado.
"""
    
    def clear_history(self, session_id: str):
        """Limpa histórico de conversa"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
    
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Retorna histórico de conversa"""
        return self.conversation_history.get(session_id, [])
    
    async def get_quick_answer(self, question: str, visa_type: Optional[str] = None) -> str:
        """Resposta rápida para perguntas comuns (sem histórico)"""
        
        try:
            system_prompt = f"""
Responda esta pergunta sobre imigração de forma BREVE e SIMPLES (máximo 3 parágrafos).
Use linguagem simples e emojis quando apropriado.
{f"Contexto: Visto {visa_type}" if visa_type else ""}

IMPORTANTE: Esta é informação educativa. Sempre mencione que não substitui consultoria jurídica.
"""
            
            llm = create_llm_client(
                system_message=system_prompt,
                session_id=f"quick_{datetime.now(timezone.utc).timestamp()}"
            )
            
            response = llm.send_message(
                question,
                model="gpt-4o",
                max_tokens=400,
                temperature=0.7
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error getting quick answer: {e}")
            return "Desculpe, não consegui processar sua pergunta no momento. Tente novamente."


# FAQ pré-definidas para respostas instantâneas
COMMON_QUESTIONS = {
    "o que é peticionário": {
        "simple": """
**Peticionário** é um nome técnico que confunde todo mundo! 😅

De forma simples: é a pessoa que está PEDINDO o visto para você.

**Exemplos:**
• Se seu marido americano está te trazendo → ELE é o peticionário
• Se sua empresa americana está te contratando → A EMPRESA é o peticionário
• Se seu pai cidadão está te peticionando → SEU PAI é o peticionário

Você (quem vai receber o visto) é chamado de **beneficiário**.

Pensando assim fica mais fácil, né? 😊
""",
        "technical": """
**Petitioner** refers to the U.S. citizen or Lawful Permanent Resident filing the immigration petition on behalf of another person (the beneficiary).

For family-based petitions (Form I-130), the petitioner must establish a qualifying relationship. For employment-based petitions, the petitioning employer must demonstrate the need for the foreign worker's services.
"""
    },
    "quanto custa": {
        "simple": """
**Custos de imigração** 💰

Depende do tipo de visto, mas aqui vai uma ideia:

**Taxas do USCIS:**
• I-130 (família): $535
• H-1B (trabalho): $460 + taxas extras
• I-539 (extensão): $370

**Outros custos possíveis:**
• Exame médico: $200-500
• Traduções: $20-50 por documento
• Fotos: $10-20
• Envio de documentos: $30-100

**TOTAL típico: $1,000 - $3,000** (sem advogado)

Com advogado: adicione $2,000-$5,000

💡 Nosso sistema ajuda você a fazer sozinho e economizar!
""",
        "technical": """
**Immigration Filing Fees:**

- Form I-130: $535
- Form I-485: $1,140 (includes biometrics)
- Form I-765: $410
- Form N-400: $640

Additional costs may include medical examination, translations, photographs, and legal representation if desired.

Refer to USCIS website for most current fee schedule: uscis.gov/fees
"""
    }
}
