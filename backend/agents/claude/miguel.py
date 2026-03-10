"""
Dr. Miguel — Document Reviewer (Claude-powered)

Reviews document completeness, identifies gaps, and validates document status.
Second agent in the comprehensive-analysis pipeline.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from backend.llm.claude_client import ClaudeClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é o Dr. Miguel, especialista em revisão documental para casos de imigração no escritório {office_name}.

PAPEL: Segundo especialista na cadeia de análise. Você recebe os dados do caso (incluindo lista de documentos recebidos e pendentes) e entrega um parecer sobre a completude e conformidade documental.

EXPERTISE:
- Verificação de completude documental por tipo de visto
- Identificação de documentos faltantes críticos
- Validação de prazos de validade (passaporte 6+ meses, I-94, etc.)
- Conformidade com requisitos USCIS
- Priorização de documentos por urgência

DOCUMENTOS OBRIGATÓRIOS POR TIPO DE VISTO:
- H-1B: Passport, I-94, Diploma, Transcripts, LCA Approved, Offer Letter, Support Letter, Pay Stubs
- EB-1A: Passport, I-94, Diploma, Publications List, Citation Evidence, Awards, Expert Opinion Letters, Reference Letters
- EB-2 NIW: Passport, I-94, Diploma, Transcripts, Publications, Citations, National Interest Statement, Expert Letters
- O-1A: Passport, I-94, Extraordinary Ability Evidence, Awards, Press Coverage, Expert Letters, Contracts
- I-485: Passport, I-94, I-693 Medical, Birth Certificate, Photos, Tax Returns, Employment Records
- I-130: Passport, Marriage Certificate, Joint Evidence (bank/tax/lease), Photos, Affidavits
- L-1A: Passport, I-94, Employment Verification, Org Chart, Business Plan, Financial Statements

REGRAS:
1. Cruze documentos recebidos com documentos obrigatórios
2. Identifique documentos faltantes com nível de urgência
3. Verifique se há inconsistências entre documentos (nomes, datas)
4. Calcule percentual de completude
5. Priorize os próximos documentos que devem ser solicitados

RESPONDA SEMPRE EM JSON válido:
{{
    "agent": "Dr. Miguel - Documentos",
    "visa_type": "tipo",
    "completeness_score": 0-100,
    "documents_received": ["doc1", "doc2"],
    "documents_missing": [
        {{"document": "nome", "urgency": "critical|high|medium|low", "reason": "por que é necessário"}}
    ],
    "documents_expiring_soon": [
        {{"document": "nome", "expiry": "data", "days_remaining": 0}}
    ],
    "inconsistencies": ["inconsistência detectada"],
    "ready_to_file": true/false,
    "next_actions": ["ação prioritária 1", "ação 2"],
    "summary": "Resumo executivo em 2-3 frases para o advogado"
}}"""


class MiguelDocumentAgent:
    """Dr. Miguel — Document review and completeness analysis powered by Claude."""

    def __init__(self, claude_client: Optional[ClaudeClient] = None, db=None):
        self.client = claude_client or ClaudeClient()
        self.db = db
        self.agent_name = "Dr. Miguel - Documentos"

    async def review(
        self,
        case_data: Dict[str, Any],
        visa_type: str,
        office_name: str = "este escritório",
        carlos_analysis: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Review document completeness for a case.

        Args:
            case_data: Full case data including documents_required and documents_received
            visa_type: Target visa type
            office_name: Name of the law firm
            carlos_analysis: Optional output from Carlos (eligibility) for context

        Returns:
            Dict with document review results
        """
        system = SYSTEM_PROMPT.format(office_name=office_name)

        user_msg = f"""REVISÃO DOCUMENTAL

Tipo de Visto: {visa_type}
Dados do Caso: {json.dumps(case_data, ensure_ascii=False, default=str)}"""

        if carlos_analysis:
            user_msg += f"""

CONTEXTO — Análise de Elegibilidade do Dr. Carlos:
{json.dumps(carlos_analysis, ensure_ascii=False, default=str)}"""

        user_msg += "\n\nAnalise a completude documental e retorne o JSON estruturado."

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
                    "ready_to_file": False,
                }

        except Exception as e:
            logger.error(f"Miguel document review failed: {e}")
            return {
                "agent": self.agent_name,
                "error": str(e),
                "ready_to_file": False,
            }
