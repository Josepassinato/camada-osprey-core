"""
Dra. Paula Agent - Gemini Edition
Agent using Gemini via Portkey LLM Client

This implementation uses the unified LLM client for Gemini access,
providing observability, cost tracking, and multi-provider routing.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

from backend.agents.base import BaseAgent
from backend.agents.dra_paula.knowledge_base import dra_paula_knowledge
from backend.llm.types import ChatMessage, MessageRole

logger = logging.getLogger(__name__)


class DraPaulaGeminiAgent(BaseAgent):
    """
    Dra. Paula powered by Gemini via Portkey
    
    Features:
    - Uses local knowledge base (knowledge_base.py)
    - Powered by Gemini via Portkey LLM Client
    - Inherits from BaseAgent for unified interface
    - Educational focus with legal disclaimers
    """
    
    def __init__(self, llm_client=None):
        super().__init__(
            llm_client=llm_client,
            agent_name="dra_paula_gemini",
            default_model="gemini-1.5-pro",
            default_temperature=0.7
        )
        
        self.knowledge_base = dra_paula_knowledge
        
        logger.info(f"✅ DraPaulaGeminiAgent initialized with model={self.default_model}")
    
    def _get_legal_disclaimer(self) -> str:
        """Get standard legal disclaimer"""
        return """

⚖️ AVISO LEGAL IMPORTANTE:
Esta informação é EXCLUSIVAMENTE educativa e orientativa. NÃO constitui aconselhamento jurídico, consultoria legal ou serviços advocatícios.

Para decisões legais específicas sobre seu caso:
✅ Consulte um advogado de imigração licenciado
✅ Verifique informações oficiais no site do USCIS (uscis.gov)
✅ Busque orientação profissional qualificada

Uso deste sistema é por sua conta e risco."""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process method required by BaseAgent
        
        Args:
            input_data: Dict with 'question', optional 'visa_type', 'context', 'agent_type'
        
        Returns:
            Dict with response and metadata
        """
        question = input_data.get("question", "")
        visa_type = input_data.get("visa_type")
        context = input_data.get("context")
        agent_type = input_data.get("agent_type", "general")
        
        return await self.consult(
            question=question,
            visa_type=visa_type,
            context=context,
            agent_type=agent_type
        )
    
    async def consult(
        self, 
        question: str, 
        visa_type: str = None, 
        context: str = None,
        agent_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Main consultation method with Dra. Paula's knowledge
        
        Args:
            question: User's question
            visa_type: Optional visa type (H-1B, L1, etc)
            context: Optional additional context
            agent_type: Type of specialized agent (document_validation, form_generation, etc)
        
        Returns:
            Dict with response, visa_knowledge, and metadata
        """
        try:
            # Get relevant knowledge from local base
            visa_knowledge = ""
            if visa_type:
                visa_info = self.knowledge_base.get_visa_specific_knowledge(visa_type)
                if visa_info:
                    visa_knowledge = f"""
                    
[CONHECIMENTO ESPECÍFICO DO VISTO {visa_type}]
Descrição: {visa_info.get('description', 'N/A')}
Requisitos: {json.dumps(visa_info.get('requirements', []), indent=2, ensure_ascii=False)}
Problemas Comuns: {json.dumps(visa_info.get('common_issues', []), indent=2, ensure_ascii=False)}
Dicas da Dra. Paula: {json.dumps(visa_info.get('dra_paula_tips', []), indent=2, ensure_ascii=False)}
"""
            
            # Get enhanced prompt for specific agent type
            enhanced_system_knowledge = self.knowledge_base.get_enhanced_prompt_for_agent(
                agent_type, 
                context or ""
            )
            
            # Build comprehensive system prompt
            system_prompt = f"""
Você é a Dra. Paula, especialista brasileira em imigração americana com foco em auto-aplicação para brasileiros.

DIRETRIZES CRÍTICAS:
- Forneça APENAS informações educativas e orientações gerais
- NUNCA dê conselhos jurídicos específicos ou tome decisões pelo usuário
- SEMPRE enfatize que o usuário deve consultar advogado de imigração licenciado para decisões legais
- Seja precisa, prática e empática
- Use linguagem acessível para brasileiros

{enhanced_system_knowledge}

{visa_knowledge}

CONTEXTO ADICIONAL:
{context or "Nenhum contexto adicional fornecido"}

INSTRUÇÕES DE RESPOSTA:
1. Responda de forma clara e estruturada
2. Use bullets ou numbered lists quando apropriado
3. Destaque informações importantes com **negrito**
4. Se for caso complexo, recomende consultar advogado
5. Finalize com o disclaimer legal

{self._get_legal_disclaimer()}
"""
            
            # Build messages
            messages = self._build_messages(
                system_prompt=system_prompt,
                user_message=question
            )
            
            # Call LLM via BaseAgent's _call_llm method
            logger.info(f"🤖 Calling Gemini for question: {question[:50]}...")
            
            response_content = await self._call_llm(
                messages=messages,
                model=self.default_model,
                temperature=self.default_temperature,
                max_tokens=2000
            )
            
            result = {
                "success": True,
                "response": response_content,
                "visa_type": visa_type,
                "agent_type": agent_type,
                "model": self.default_model,
                "has_visa_knowledge": bool(visa_knowledge),
                "disclaimer_included": True
            }
            
            logger.info(f"✅ Gemini response generated successfully ({len(response_content)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in DraPaulaGeminiAgent.consult: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "Desculpe, ocorreu um erro ao processar sua consulta. Por favor, tente novamente.",
                "model": self.default_model
            }
    
    async def validate_document(
        self, 
        document_type: str, 
        document_data: Dict[str, Any],
        visa_type: str = None
    ) -> Dict[str, Any]:
        """Specialized method for document validation"""
        
        question = f"""
        Preciso validar um documento do tipo: {document_type}
        
        Dados do documento:
        {json.dumps(document_data, indent=2, ensure_ascii=False)}
        
        Por favor, forneça:
        1. Verificações necessárias para este tipo de documento
        2. Problemas comuns encontrados em documentos brasileiros deste tipo
        3. Requisitos específicos do USCIS para este documento
        4. Dicas para garantir que o documento seja aceito
        """
        
        return await self.consult(
            question=question,
            visa_type=visa_type,
            agent_type="document_validation"
        )
    
    async def check_eligibility(
        self,
        visa_type: str,
        applicant_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check eligibility for a specific visa type"""
        
        question = f"""
        Análise de elegibilidade para visto {visa_type}:
        
        Perfil do aplicante:
        {json.dumps(applicant_profile, indent=2, ensure_ascii=False)}
        
        Por favor, analise:
        1. Se o perfil atende os requisitos básicos do visto {visa_type}
        2. Quais documentos serão necessários
        3. Possíveis desafios ou pontos de atenção
        4. Próximos passos recomendados
        5. Estimativa de custos e prazos
        
        IMPORTANTE: Esta é apenas uma análise educativa inicial. Para decisão final, 
        o aplicante DEVE consultar um advogado de imigração licenciado.
        """
        
        return await self.consult(
            question=question,
            visa_type=visa_type,
            agent_type="general"
        )


# Global instance (optional, for easy access)
_gemini_agent_instance = None


def get_gemini_dra_paula_agent() -> DraPaulaGeminiAgent:
    """Get singleton instance of Gemini Dra. Paula Agent"""
    global _gemini_agent_instance
    if _gemini_agent_instance is None:
        _gemini_agent_instance = DraPaulaGeminiAgent()
    return _gemini_agent_instance
