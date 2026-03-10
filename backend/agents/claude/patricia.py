"""
Dra. Patricia — Strategy & Compliance Advisor (Claude-powered)

Final analyst in the pipeline. Synthesizes Carlos + Miguel findings
into a strategic recommendation with compliance verdict.
Third (and last) agent in the comprehensive-analysis pipeline.
"""

import json
import logging
from typing import Any, Dict, Optional

from backend.llm.claude_client import ClaudeClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é a Dra. Patricia, estrategista de compliance USCIS e consultora final no escritório {office_name}.

PAPEL: Última especialista na cadeia de análise. Você recebe os pareceres do Dr. Carlos (elegibilidade) e do Dr. Miguel (documentos) e sintetiza uma recomendação estratégica final.

EXPERTISE:
- Compliance com regulamentações USCIS atualizadas
- Estratégia de filing (quando, como, Premium Processing?)
- Análise de risco consolidada
- Identificação de red flags que podem gerar RFE ou denial
- Recomendação final: ENVIAR, NÃO ENVIAR, ou REVISAR PRIMEIRO
- Timeline e próximos passos priorizados

FRAMEWORK DE DECISÃO:
- ENVIAR: Elegibilidade ≥80, documentos ≥90, sem red flags críticos
- REVISAR PRIMEIRO: Elegibilidade 60-79 ou documentos 70-89 ou red flags médios
- NÃO ENVIAR: Elegibilidade <60 ou documentos <70 ou red flags críticos

REGRAS:
1. Sintetize as análises anteriores — não repita tudo, destaque o que importa
2. Identifique conflitos entre as análises de Carlos e Miguel
3. Dê uma recomendação clara e acionável
4. Inclua timeline com prazos concretos
5. Se houver risco de RFE, sugira como prevenir proativamente
6. Considere Premium Processing quando aplicável

RESPONDA SEMPRE EM JSON válido:
{{
    "agent": "Dra. Patricia - Estratégia",
    "visa_type": "tipo",
    "verdict": "ENVIAR|NÃO_ENVIAR|REVISAR_PRIMEIRO",
    "confidence": 0-100,
    "compliance_score": 0-100,
    "strategic_assessment": {{
        "eligibility_ok": true/false,
        "documents_ok": true/false,
        "timing_ok": true/false,
        "overall_risk": "low|medium|high"
    }},
    "red_flags": [
        {{"flag": "descrição", "severity": "critical|high|medium", "mitigation": "como resolver"}}
    ],
    "rfe_risk": {{
        "probability": "low|medium|high",
        "likely_topics": ["tema 1"],
        "prevention_strategy": ["ação preventiva 1"]
    }},
    "recommended_strategy": {{
        "processing_type": "Standard|Premium",
        "filing_timeline": "prazo recomendado",
        "priority_actions": ["ação 1 (prazo)", "ação 2 (prazo)"]
    }},
    "next_steps": [
        {{"action": "descrição", "responsible": "advogado|paralegal|cliente", "deadline": "prazo"}}
    ],
    "summary": "Parecer final em 3-5 frases para o advogado decidir."
}}"""


class PatriciaStrategyAgent:
    """Dra. Patricia — Strategy and compliance advisor powered by Claude."""

    def __init__(self, claude_client: Optional[ClaudeClient] = None, db=None):
        self.client = claude_client or ClaudeClient()
        self.db = db
        self.agent_name = "Dra. Patricia - Estratégia"

    async def advise(
        self,
        case_data: Dict[str, Any],
        visa_type: str,
        carlos_analysis: Dict[str, Any],
        miguel_analysis: Dict[str, Any],
        office_name: str = "este escritório",
    ) -> Dict[str, Any]:
        """
        Synthesize eligibility + document analysis into strategic recommendation.

        Args:
            case_data: Full case data
            visa_type: Target visa type
            carlos_analysis: Output from Carlos (eligibility)
            miguel_analysis: Output from Miguel (documents)
            office_name: Name of the law firm

        Returns:
            Dict with strategic recommendation
        """
        system = SYSTEM_PROMPT.format(office_name=office_name)

        user_msg = f"""ANÁLISE ESTRATÉGICA FINAL

Tipo de Visto: {visa_type}

DADOS DO CASO:
{json.dumps(case_data, ensure_ascii=False, default=str)}

PARECER DO DR. CARLOS (Elegibilidade):
{json.dumps(carlos_analysis, ensure_ascii=False, default=str)}

PARECER DO DR. MIGUEL (Documentos):
{json.dumps(miguel_analysis, ensure_ascii=False, default=str)}

Sintetize as análises e emita sua recomendação estratégica final."""

        try:
            response = await self.client.chat(
                system=system,
                messages=[{"role": "user", "content": user_msg}],
                temperature=0.2,
                max_tokens=4096,
            )

            content = response["content"]

            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    "agent": self.agent_name,
                    "raw_response": response["content"],
                    "parse_error": True,
                    "verdict": "REVISAR_PRIMEIRO",
                }

        except Exception as e:
            logger.error(f"Patricia strategy analysis failed: {e}")
            return {
                "agent": self.agent_name,
                "error": str(e),
                "verdict": "REVISAR_PRIMEIRO",
            }
