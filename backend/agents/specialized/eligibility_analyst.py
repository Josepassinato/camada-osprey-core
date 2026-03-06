"""
Eligibility Analysis Agent

Specialized agent for visa eligibility analysis.
Dr. Carlos - Expert in visa eligibility requirements.
"""

import logging
from typing import Any, Dict, Optional

from agents.base import BaseAgent
from llm.portkey_client import LLMClient

logger = logging.getLogger(__name__)


class EligibilityAnalysisAgent(BaseAgent):
    """
    Specialized agent for visa eligibility analysis

    Dr. Carlos - Visa eligibility expert

    Capabilities:
    - Visa-specific requirement verification
    - Educational and professional qualification analysis
    - Eligibility criteria checking
    - Risk factor identification
    - Application strength assessment
    """

    def __init__(
        self, llm_client: Optional[LLMClient] = None, db=None, use_dra_paula_knowledge: bool = True
    ):
        super().__init__(
            llm_client=llm_client,
            agent_name="Dr. Carlos - Analista de Elegibilidade",
            default_model="gpt-4o",
            default_temperature=0.5,
        )

        self.db = db
        self.use_dra_paula_knowledge = use_dra_paula_knowledge
        self.dra_paula_assistant_id = "asst_kkyn65SQFfkloH4SalOZfwwh"
        self.specialization = "Visa Eligibility Analysis"

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process eligibility analysis request"""
        candidate_data = input_data.get("candidate_data")
        visa_type = input_data.get("visa_type")

        if not candidate_data or not visa_type:
            return {
                "agent": self.agent_name,
                "error": "Missing required fields: candidate_data and visa_type",
                "eligible": False,
            }

        return await self.analyze_eligibility(candidate_data=candidate_data, visa_type=visa_type)

    def get_system_prompt(self) -> str:
        return f"""
        Você é o Dr. Carlos, especialista EXCLUSIVO em análise de elegibilidade para vistos americanos.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({self.dra_paula_assistant_id}).

        EXPERTISE ESPECÍFICA:
        - Requisitos específicos por tipo de visto (H1-B, L1, O1, F1, etc.)
        - Análise de qualificações educacionais e profissionais
        - Verificação de critérios de elegibilidade
        - Identificação de potenciais problemas de aprovação
        - Recomendações para fortalecer a aplicação

        RESPOSTA SEMPRE EM JSON:
        {{
            "agent": "Dr. Carlos - Elegibilidade",
            "eligible": true/false,
            "eligibility_score": 0-100,
            "met_requirements": ["req1", "req2"],
            "missing_requirements": ["req1", "req2"],
            "risk_factors": [{{"risk": "descrição", "severity": "high|medium|low"}}],
            "strengths": ["ponto forte 1"],
            "recommendations": ["melhoria 1"],
            "approval_probability": "high|medium|low",
            "additional_evidence_needed": ["evidência 1"]
        }}
        """

    async def analyze_eligibility(
        self, candidate_data: Dict[str, Any], visa_type: str
    ) -> Dict[str, Any]:
        """Analyze candidate eligibility for visa type"""
        prompt = f"""
        ANÁLISE DE ELEGIBILIDADE

        Tipo de Visto: {visa_type}
        Dados do Candidato: {candidate_data}

        Analise a elegibilidade do candidato para o visto {visa_type}.
        """

        messages = self._build_messages(system_prompt=self.get_system_prompt(), user_message=prompt)

        response = await self._call_llm(messages)

        try:
            import json

            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "agent": self.agent_name,
                "raw_response": response,
                "parse_error": True,
                "eligible": False,
            }


def create_eligibility_analyst(
    llm_client: Optional[LLMClient] = None, db=None
) -> EligibilityAnalysisAgent:
    """Create an EligibilityAnalysisAgent instance"""
    return EligibilityAnalysisAgent(llm_client=llm_client, db=db)
