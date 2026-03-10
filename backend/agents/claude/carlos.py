"""
Dr. Carlos — Eligibility Analyst (Claude-powered)

Analyzes visa eligibility based on candidate profile and case data.
First agent in the comprehensive-analysis pipeline.
"""

import json
import logging
from typing import Any, Dict, Optional

from backend.llm.claude_client import ClaudeClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é o Dr. Carlos, analista sênior de elegibilidade para vistos americanos no escritório {office_name}.

PAPEL: Primeiro especialista na cadeia de análise. Você recebe os dados brutos do caso e entrega um parecer estruturado de elegibilidade.

EXPERTISE:
- Requisitos específicos por tipo de visto (H-1B, EB-1A, EB-2 NIW, O-1A, L-1A, I-130, I-485, F-1)
- Análise de qualificações educacionais e profissionais
- Verificação de critérios de elegibilidade do USCIS
- Identificação de riscos e pontos fracos
- Recomendações para fortalecer a aplicação

REFERÊNCIAS LEGAIS:
- H-1B: Specialty occupation, LCA, employer-employee relationship, prevailing wage, cap/lottery
- EB-1A: 3 de 10 critérios + final merits determination (Kazarian framework)
- EB-2 NIW: Dhanasar 3 prongs (mérito nacional, bem posicionado, beneficial to waive)
- O-1A: 3 de 8 critérios, extraordinary ability, sustained national/international acclaim
- I-485: Eligible category, priority date current, admissibility, no bars
- I-130: Bona fide relationship, petitioner eligibility, beneficiary relationship proof

REGRAS:
1. Analise APENAS com os dados fornecidos — não invente fatos
2. Se dados críticos estão faltando, indique explicitamente
3. Seja direto e objetivo — o advogado não precisa de explicações básicas
4. Inclua score numérico de elegibilidade (0-100)
5. Liste critérios atendidos e não atendidos separadamente

RESPONDA SEMPRE EM JSON válido com esta estrutura:
{{
    "agent": "Dr. Carlos - Elegibilidade",
    "visa_type": "tipo analisado",
    "eligible": true/false,
    "eligibility_score": 0-100,
    "met_requirements": ["req1", "req2"],
    "missing_requirements": ["req1"],
    "risk_factors": [{{"risk": "descrição", "severity": "high|medium|low"}}],
    "strengths": ["ponto forte 1"],
    "weaknesses": ["ponto fraco 1"],
    "missing_data": ["dado que falta para análise completa"],
    "approval_probability": "high|medium|low",
    "recommendations": ["ação recomendada 1"],
    "summary": "Resumo executivo em 2-3 frases para o advogado"
}}"""


class CarlosEligibilityAgent:
    """Dr. Carlos — Visa eligibility analysis powered by Claude."""

    def __init__(self, claude_client: Optional[ClaudeClient] = None, db=None):
        self.client = claude_client or ClaudeClient()
        self.db = db
        self.agent_name = "Dr. Carlos - Elegibilidade"

    async def analyze(
        self,
        case_data: Dict[str, Any],
        visa_type: str,
        office_name: str = "este escritório",
    ) -> Dict[str, Any]:
        """
        Analyze visa eligibility for a case.

        Args:
            case_data: Full case data (client info, documents, notes)
            visa_type: Target visa type (H-1B, EB-1A, etc.)
            office_name: Name of the law firm

        Returns:
            Dict with eligibility analysis results
        """
        system = SYSTEM_PROMPT.format(office_name=office_name)

        user_msg = f"""ANÁLISE DE ELEGIBILIDADE

Tipo de Visto: {visa_type}
Dados do Caso: {json.dumps(case_data, ensure_ascii=False, default=str)}

Analise a elegibilidade do candidato para o visto {visa_type} e retorne o JSON estruturado."""

        try:
            response = await self.client.chat(
                system=system,
                messages=[{"role": "user", "content": user_msg}],
                temperature=0.3,
                max_tokens=4096,
            )

            content = response["content"]

            # Try to parse JSON from response
            try:
                # Handle markdown code blocks
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
                    "eligible": False,
                }

        except Exception as e:
            logger.error(f"Carlos eligibility analysis failed: {e}")
            return {
                "agent": self.agent_name,
                "error": str(e),
                "eligible": False,
            }
