"""
Hybrid Dra. Paula Agent - Safe Migration Layer
Uses Gemini by default, falls back to OpenAI if needed

This module provides a safe transition from OpenAI to Gemini
without breaking existing functionality.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from gemini_dra_paula_agent import DraPaulaGeminiAgent
from dra_paula_knowledge_base import dra_paula_knowledge

logger = logging.getLogger(__name__)


class HybridDraPaulaAgent:
    """
    Hybrid agent that tries Gemini first, falls back to OpenAI if needed
    
    This provides a safe migration path:
    1. Try Gemini (new implementation)
    2. If Gemini fails, use OpenAI (existing implementation)
    3. Log all switches for monitoring
    
    Features:
    - Zero downtime migration
    - Automatic fallback
    - Performance monitoring
    - Easy rollback via feature flag
    """
    
    def __init__(self, prefer_gemini: bool = True):
        """
        Initialize hybrid agent
        
        Args:
            prefer_gemini: If True, try Gemini first. If False, use OpenAI directly.
        """
        self.prefer_gemini = prefer_gemini
        self.emergent_key = os.environ.get('EMERGENT_LLM_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        
        # Initialize Gemini agent
        self.gemini_agent = None
        if self.emergent_key and self.prefer_gemini:
            try:
                self.gemini_agent = DraPaulaGeminiAgent()
                logger.info("✅ Gemini agent initialized (primary)")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Gemini agent: {str(e)}")
        
        # OpenAI fallback
        self.has_openai = bool(self.openai_key)
        
        logger.info(f"🔧 HybridDraPaulaAgent initialized - Gemini: {self.gemini_agent is not None}, OpenAI fallback: {self.has_openai}")
    
    async def consult(
        self, 
        question: str, 
        visa_type: str = None, 
        context: str = None,
        agent_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Consult with automatic fallback logic
        
        Flow:
        1. If Gemini available and prefer_gemini=True -> Try Gemini
        2. If Gemini fails or not available -> Use OpenAI fallback
        3. Return result with metadata about which provider was used
        """
        
        # Try Gemini first (if available and preferred)
        if self.gemini_agent and self.prefer_gemini:
            try:
                logger.info("🚀 Trying Gemini (primary provider)...")
                result = await self.gemini_agent.consult(
                    question=question,
                    visa_type=visa_type,
                    context=context,
                    agent_type=agent_type
                )
                
                if result.get("success"):
                    logger.info("✅ Gemini response successful")
                    result["provider_used"] = "gemini"
                    result["fallback_used"] = False
                    return result
                else:
                    logger.warning(f"⚠️ Gemini returned error: {result.get('error')}")
                    # Fall through to OpenAI fallback
            
            except Exception as e:
                logger.error(f"❌ Gemini error: {str(e)}")
                # Fall through to OpenAI fallback
        
        # OpenAI fallback
        if self.has_openai:
            try:
                logger.info("🔄 Using OpenAI fallback...")
                result = await self._consult_with_openai(
                    question=question,
                    visa_type=visa_type,
                    context=context,
                    agent_type=agent_type
                )
                result["provider_used"] = "openai"
                result["fallback_used"] = True
                logger.info("✅ OpenAI fallback successful")
                return result
            
            except Exception as e:
                logger.error(f"❌ OpenAI fallback also failed: {str(e)}")
                return {
                    "success": False,
                    "error": f"Both Gemini and OpenAI failed: {str(e)}",
                    "response": "Desculpe, ocorreu um erro ao processar sua consulta. Por favor, tente novamente.",
                    "provider_used": "none",
                    "fallback_used": True
                }
        
        # No providers available
        return {
            "success": False,
            "error": "No LLM providers available",
            "response": "Sistema temporariamente indisponível. Por favor, tente novamente mais tarde.",
            "provider_used": "none",
            "fallback_used": False
        }
    
    async def _consult_with_openai(
        self,
        question: str,
        visa_type: str = None,
        context: str = None,
        agent_type: str = "general"
    ) -> Dict[str, Any]:
        """
        OpenAI fallback implementation
        Uses local knowledge base + OpenAI (similar to Gemini implementation)
        """
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.openai_key)
        
        # Get knowledge from local base (same as Gemini)
        visa_knowledge = ""
        if visa_type:
            visa_info = dra_paula_knowledge.get_visa_knowledge(visa_type)
            if visa_info:
                import json
                visa_knowledge = f"""
                
[CONHECIMENTO ESPECÍFICO DO VISTO {visa_type}]
{json.dumps(visa_info, indent=2, ensure_ascii=False)}
"""
        
        enhanced_system_knowledge = dra_paula_knowledge.get_enhanced_prompt_for_agent(
            agent_type, 
            context or ""
        )
        
        # Build prompt (same structure as Gemini)
        full_prompt = f"""
Você é a Dra. Paula, especialista brasileira em imigração americana.

DIRETRIZES CRÍTICAS:
- Forneça APENAS informações educativas e orientações gerais
- NUNCA dê conselhos jurídicos específicos
- SEMPRE recomende consultar advogado de imigração licenciado

{enhanced_system_knowledge}

{visa_knowledge}

CONTEXTO: {context or "Nenhum"}

PERGUNTA: {question}

⚖️ AVISO LEGAL: Esta informação é educativa. NÃO constitui consultoria jurídica.
Consulte um advogado de imigração licenciado para decisões legais.
"""
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é a Dra. Paula, especialista em imigração americana."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        return {
            "success": True,
            "response": response.choices[0].message.content,
            "visa_type": visa_type,
            "agent_type": agent_type,
            "model": "gpt-4o",
            "has_visa_knowledge": bool(visa_knowledge),
            "disclaimer_included": True
        }
    
    async def validate_document(
        self, 
        document_type: str, 
        document_data: Dict[str, Any],
        visa_type: str = None
    ) -> Dict[str, Any]:
        """Document validation with automatic fallback"""
        if self.gemini_agent:
            try:
                return await self.gemini_agent.validate_document(
                    document_type=document_type,
                    document_data=document_data,
                    visa_type=visa_type
                )
            except:
                pass
        
        # Fallback to consult method
        import json
        question = f"Validar documento {document_type}: {json.dumps(document_data, ensure_ascii=False)}"
        return await self.consult(question=question, visa_type=visa_type, agent_type="document_validation")
    
    async def check_eligibility(
        self,
        visa_type: str,
        applicant_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Eligibility check with automatic fallback"""
        if self.gemini_agent:
            try:
                return await self.gemini_agent.check_eligibility(
                    visa_type=visa_type,
                    applicant_profile=applicant_profile
                )
            except:
                pass
        
        # Fallback to consult method
        import json
        question = f"Analisar elegibilidade para {visa_type}: {json.dumps(applicant_profile, ensure_ascii=False)}"
        return await self.consult(question=question, visa_type=visa_type)


# Global instance with feature flag
# Set PREFER_GEMINI_AGENT=false in .env to use OpenAI directly
_hybrid_agent_instance = None

def get_dra_paula_agent(prefer_gemini: bool = None) -> HybridDraPaulaAgent:
    """
    Get singleton instance of Hybrid Dra. Paula Agent
    
    Args:
        prefer_gemini: Override default preference. If None, reads from env or defaults to True
    
    Returns:
        HybridDraPaulaAgent instance
    """
    global _hybrid_agent_instance
    
    if prefer_gemini is None:
        # Read from environment (feature flag)
        prefer_gemini = os.environ.get('PREFER_GEMINI_AGENT', 'true').lower() != 'false'
    
    if _hybrid_agent_instance is None:
        _hybrid_agent_instance = HybridDraPaulaAgent(prefer_gemini=prefer_gemini)
    
    return _hybrid_agent_instance


# Backward compatibility: provide same interface as before
async def consult_dra_paula(
    question: str,
    visa_type: str = None,
    context: str = None
) -> str:
    """
    Backward compatible function
    Returns just the response text (not the full dict)
    """
    agent = get_dra_paula_agent()
    result = await agent.consult(question=question, visa_type=visa_type, context=context)
    return result.get("response", "")
