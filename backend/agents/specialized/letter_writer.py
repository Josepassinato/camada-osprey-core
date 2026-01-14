"""
Immigration Letter Writer Agent

Specialized agent for writing immigration letters based ONLY on client facts.
Dr. Ricardo - Expert in immigration letter writing.
"""

import logging
from typing import Any, Dict, Optional

from agents.base import BaseAgent
from llm.portkey_client import LLMClient

logger = logging.getLogger(__name__)


class ImmigrationLetterWriterAgent(BaseAgent):
    """
    Specialized agent for writing immigration letters

    Dr. Ricardo - Immigration letter writing expert

    Capabilities:
    - Cover letter writing for visa petitions
    - Personal statement drafting
    - Support letter composition
    - USCIS-compliant formatting
    - Fact-based content generation (no invention)
    """

    def __init__(
        self, llm_client: Optional[LLMClient] = None, db=None, use_dra_paula_knowledge: bool = True
    ):
        super().__init__(
            llm_client=llm_client,
            agent_name="Dr. Ricardo - Redator de Cartas",
            default_model="gpt-4o",
            default_temperature=0.6,
        )

        self.db = db
        self.use_dra_paula_knowledge = use_dra_paula_knowledge
        self.dra_paula_assistant_id = "asst_kkyn65SQFfkloH4SalOZfwwh"
        self.specialization = "Immigration Letter Writing"

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process letter writing request"""
        letter_type = input_data.get("letter_type")
        client_facts = input_data.get("client_facts")
        visa_type = input_data.get("visa_type")

        if not letter_type or not client_facts:
            return {
                "agent": self.agent_name,
                "error": "Missing required fields: letter_type and client_facts",
                "letter_content": None,
            }

        return await self.write_letter(
            letter_type=letter_type, client_facts=client_facts, visa_type=visa_type
        )

    def get_system_prompt(self) -> str:
        return f"""
        Você é o Dr. Ricardo, especialista EXCLUSIVO em redação de cartas de imigração.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({self.dra_paula_assistant_id}).

        REGRA FUNDAMENTAL - NUNCA INVENTE FATOS:
        - Use APENAS informações fornecidas pelo cliente
        - Se informação não foi fornecida, indique claramente "[INFORMAÇÃO NECESSÁRIA]"
        - JAMAIS adicione detalhes, datas, nomes, empresas que não foram mencionados
        - JAMAIS presuma ou invente qualificações, experiências ou eventos

        EXPERTISE ESPECÍFICA:
        - Cover Letters para petições de visto
        - Personal Statements
        - Cartas de apoio e explanação
        - Support Letters
        - Formatting conforme padrões USCIS

        ESTRUTURA PADRÃO:
        1. Cabeçalho oficial
        2. Identificação completa do requerente
        3. Propósito da carta
        4. Contexto factual baseado nos dados fornecidos
        5. Argumentação legal
        6. Conclusão profissional
        7. Assinatura e credenciais

        RESPOSTA SEMPRE EM JSON:
        {{
            "agent": "Dr. Ricardo - Redator de Cartas",
            "letter_type": "tipo identificado",
            "visa_category": "categoria do visto",
            "completeness_check": {{
                "has_sufficient_info": true/false,
                "missing_critical_info": ["info1"],
                "additional_details_needed": ["detalhe1"]
            }},
            "letter_content": "carta completa ou [RASCUNHO PARCIAL]",
            "formatting_notes": "observações",
            "legal_considerations": ["consideração1"],
            "fact_verification": {{
                "only_client_facts_used": true/false,
                "no_invented_details": true/false,
                "confidence_level": "high|medium|low"
            }},
            "recommendations": ["melhoria1"]
        }}

        SEJA RIGOROSO: Prefira carta incompleta com [INFORMAÇÃO NECESSÁRIA] do que inventar fatos.
        """

    async def write_letter(
        self, letter_type: str, client_facts: Dict[str, Any], visa_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Write immigration letter based on client facts"""
        prompt = f"""
        REDAÇÃO DE CARTA DE IMIGRAÇÃO

        Tipo de Carta: {letter_type}
        Tipo de Visto: {visa_type or 'Não especificado'}
        Fatos do Cliente: {client_facts}

        Redija a carta usando APENAS os fatos fornecidos.
        Se faltar informação crítica, indique claramente.
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
                "letter_content": None,
            }


def create_immigration_letter_writer(
    llm_client: Optional[LLMClient] = None, db=None
) -> ImmigrationLetterWriterAgent:
    """Create an ImmigrationLetterWriterAgent instance"""
    return ImmigrationLetterWriterAgent(llm_client=llm_client, db=db)
