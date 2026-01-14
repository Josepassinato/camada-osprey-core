"""
Urgency Triage Agent

Agent to triage issues by urgency and route to appropriate specialist.
Dr. Roberto - Expert in issue triage and routing.
"""

import logging
from typing import Any, Dict, Optional

from agents.base import BaseAgent
from llm.portkey_client import LLMClient

logger = logging.getLogger(__name__)


class UrgencyTriageAgent(BaseAgent):
    """
    Agent to triage issues by urgency and route to appropriate specialist
    
    Dr. Roberto - Triage and routing expert
    
    Capabilities:
    - Urgency classification
    - Issue type identification
    - Specialist routing
    - Priority ordering
    - Complexity assessment
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        db=None
    ):
        super().__init__(
            llm_client=llm_client,
            agent_name="Dr. Roberto - Triagem",
            default_model="gpt-4o",
            default_temperature=0.4,
        )
        
        self.db = db
        self.specialization = "Issue Triage & Routing"
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process triage request"""
        issue_description = input_data.get("issue_description")
        context = input_data.get("context", {})
        
        if not issue_description:
            return {
                "agent": self.agent_name,
                "error": "Missing required field: issue_description",
                "urgency": "UNKNOWN"
            }
        
        return await self.triage_issue(
            issue_description=issue_description,
            context=context
        )
    
    def get_system_prompt(self) -> str:
        return """
        Você é o Dr. Roberto, especialista em triagem e roteamento de questões de imigração.
        
        FUNÇÃO PRINCIPAL:
        - Classificar urgência e tipo de problema
        - Rotear para o especialista correto
        - Priorizar questões críticas
        - Coordenar múltiplos agentes quando necessário
        
        ESPECIALISTAS DISPONÍVEIS:
        1. Dr. Miguel - Validação de Documentos
        2. Dra. Ana - Validação de Formulários
        3. Dr. Carlos - Análise de Elegibilidade
        4. Dra. Patricia - Compliance USCIS
        5. Dr. Ricardo - Redação de Cartas
        6. Dr. Fernando - Tradução de Formulários
        
        RESPOSTA SEMPRE EM JSON:
        {
            "agent": "Dr. Roberto - Triagem",
            "urgency": "CRÍTICO|ALTO|MÉDIO|BAIXO",
            "issue_type": "documento|formulário|elegibilidade|compliance|carta|tradução|geral",
            "recommended_specialist": "nome do especialista",
            "requires_multiple_agents": true/false,
            "priority_order": ["agent1", "agent2"],
            "estimated_complexity": "simples|moderado|complexo",
            "immediate_action_needed": true/false,
            "routing_rationale": "explicação da decisão"
        }
        """
    
    async def triage_issue(
        self,
        issue_description: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Triage issue and determine routing"""
        prompt = f"""
        TRIAGEM DE QUESTÃO DE IMIGRAÇÃO
        
        Descrição do Problema: {issue_description}
        Contexto: {context}
        
        Classifique a urgência, identifique o tipo de problema e recomende o especialista apropriado.
        """
        
        messages = self._build_messages(
            system_prompt=self.get_system_prompt(),
            user_message=prompt
        )
        
        response = await self._call_llm(messages)
        
        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "agent": self.agent_name,
                "raw_response": response,
                "parse_error": True,
                "urgency": "UNKNOWN"
            }


def create_urgency_triage(llm_client: Optional[LLMClient] = None, db=None) -> UrgencyTriageAgent:
    """Create an UrgencyTriageAgent instance"""
    return UrgencyTriageAgent(llm_client=llm_client, db=db)
