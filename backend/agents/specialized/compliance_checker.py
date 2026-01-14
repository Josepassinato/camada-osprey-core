"""
Compliance Check Agent

Specialized agent for USCIS compliance and final review.
Dra. Patricia - Expert in USCIS compliance.
"""

import logging
from typing import Any, Dict, Optional

from agents.base import BaseAgent
from llm.portkey_client import LLMClient

logger = logging.getLogger(__name__)


class ComplianceCheckAgent(BaseAgent):
    """
    Specialized agent for USCIS compliance and final review
    
    Dra. Patricia - USCIS compliance expert
    
    Capabilities:
    - USCIS regulation compliance checking
    - Final submission readiness review
    - Red flag identification
    - Consistency verification
    - Submission recommendation
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        db=None,
        use_dra_paula_knowledge: bool = True
    ):
        super().__init__(
            llm_client=llm_client,
            agent_name="Dra. Patricia - Compliance USCIS",
            default_model="gpt-4o",
            default_temperature=0.2,  # Very low for compliance
        )
        
        self.db = db
        self.use_dra_paula_knowledge = use_dra_paula_knowledge
        self.dra_paula_assistant_id = "asst_kkyn65SQFfkloH4SalOZfwwh"
        self.specialization = "USCIS Compliance & Final Review"
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process compliance check request"""
        application_data = input_data.get("application_data")
        visa_type = input_data.get("visa_type")
        
        if not application_data:
            return {
                "agent": self.agent_name,
                "error": "Missing required field: application_data",
                "uscis_compliant": False
            }
        
        return await self.check_compliance(
            application_data=application_data,
            visa_type=visa_type
        )
    
    def get_system_prompt(self) -> str:
        return f"""
        Você é a Dra. Patricia, especialista EXCLUSIVA em compliance USCIS e revisão final.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({self.dra_paula_assistant_id}).
        
        EXPERTISE ESPECÍFICA:
        - Regulamentações atuais do USCIS
        - Checklist final de compliance
        - Identificação de red flags
        - Verificação de consistência geral
        - Preparação para submissão
        
        CHECKLIST FINAL OBRIGATÓRIO:
        1. Todos os documentos necessários incluídos
        2. Formulários preenchidos corretamente
        3. Taxas corretas calculadas
        4. Nenhuma inconsistência entre documentos
        5. Conformidade com regulamentações atuais
        
        RESPOSTA SEMPRE EM JSON:
        {{
            "agent": "Dra. Patricia - Compliance",
            "uscis_compliant": true/false,
            "ready_for_submission": true/false,
            "compliance_score": 0-100,
            "red_flags": ["flag1"],
            "missing_elements": ["elemento1"],
            "final_checklist": [{{"item": "descrição", "status": "ok|missing|issue"}}],
            "submission_recommendation": "ENVIAR|NÃO_ENVIAR|REVISAR_PRIMEIRO",
            "final_notes": "Observações finais"
        }}
        
        SEJA A ÚLTIMA LINHA DE DEFESA. Só aprove aplicações 100% prontas.
        """
    
    async def check_compliance(
        self,
        application_data: Dict[str, Any],
        visa_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check application compliance with USCIS requirements"""
        prompt = f"""
        VERIFICAÇÃO DE COMPLIANCE USCIS
        
        Tipo de Visto: {visa_type or 'Não especificado'}
        Dados da Aplicação: {application_data}
        
        Realize verificação final de compliance e determine se está pronto para submissão.
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
                "uscis_compliant": False
            }


def create_compliance_checker(llm_client: Optional[LLMClient] = None, db=None) -> ComplianceCheckAgent:
    """Create a ComplianceCheckAgent instance"""
    return ComplianceCheckAgent(llm_client=llm_client, db=db)
