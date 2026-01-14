"""
USCIS Form Translator Agent

Specialized agent for validating friendly forms and translating to official USCIS forms.
Dr. Fernando - Expert in USCIS form translation and validation.
"""

import logging
from typing import Dict, Any, Optional

from agents.base import BaseAgent
from llm.portkey_client import LLMClient

logger = logging.getLogger(__name__)


class USCISFormTranslatorAgent(BaseAgent):
    """
    Specialized agent for USCIS form translation and validation
    
    Dr. Fernando - USCIS form translation expert
    
    Capabilities:
    - Friendly form to official USCIS form mapping
    - Field validation and format checking
    - Technical terminology translation
    - USCIS compliance verification
    - Ambiguity detection and clarification
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        db=None,
        use_dra_paula_knowledge: bool = True
    ):
        super().__init__(
            llm_client=llm_client,
            agent_name="Dr. Fernando - Tradutor e Validador USCIS",
            default_model="gpt-4o",
            default_temperature=0.2,  # Very low for accurate translation
        )
        
        self.db = db
        self.use_dra_paula_knowledge = use_dra_paula_knowledge
        self.dra_paula_assistant_id = "asst_kkyn65SQFfkloH4SalOZfwwh"
        self.specialization = "USCIS Form Translation & Validation"
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process form translation request"""
        friendly_form_data = input_data.get("friendly_form_data")
        target_uscis_form = input_data.get("target_uscis_form")
        
        if not friendly_form_data or not target_uscis_form:
            return {
                "agent": self.agent_name,
                "error": "Missing required fields: friendly_form_data and target_uscis_form",
                "translation_status": "FAILED"
            }
        
        return await self.translate_form(
            friendly_form_data=friendly_form_data,
            target_uscis_form=target_uscis_form
        )
    
    def get_system_prompt(self) -> str:
        return f"""
        Você é o Dr. Fernando, especialista EXCLUSIVO em validação e tradução de formulários USCIS.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({self.dra_paula_assistant_id}).
        
        FUNÇÃO CRÍTICA:
        1. Analisar respostas do formulário amigável (português)
        2. Validar completude e correção das informações
        3. Traduzir de forma precisa para formulários oficiais USCIS (inglês)
        
        EXPERTISE ESPECÍFICA:
        - Mapeamento de campos formulário amigável → formulário oficial USCIS
        - Terminologia técnica oficial do USCIS
        - Formatos específicos por tipo de formulário
        - Validação de dados conforme regulamentações
        - Tradução juramentada e técnica
        
        VALIDAÇÕES OBRIGATÓRIAS:
        1. Verificar se todas as perguntas obrigatórias foram respondidas
        2. Validar formato de datas (MM/DD/YYYY para USCIS)
        3. Confirmar consistência entre seções
        4. Verificar se respostas atendem critérios específicos
        5. Detectar respostas ambíguas ou incompletas
        
        REGRAS DE TRADUÇÃO RÍGIDAS:
        - Use terminologia técnica oficial do USCIS
        - Mantenha fidelidade absoluta ao significado
        - Não interprete ou presuma informações
        - Se resposta for ambígua, solicite esclarecimento
        - Use formatos de data/endereço americanos
        
        RESPOSTA SEMPRE EM JSON:
        {{
            "agent": "Dr. Fernando - Tradutor e Validador USCIS",
            "source_form_type": "formulário amigável",
            "target_uscis_form": "formulário USCIS",
            "validation_results": {{
                "form_complete": true/false,
                "completion_percentage": 0-100,
                "missing_required_fields": ["campo1"],
                "invalid_formats": [{{
                    "field": "campo",
                    "current_value": "valor",
                    "required_format": "formato",
                    "example": "exemplo"
                }}],
                "consistency_issues": [{{
                    "fields": ["campo1", "campo2"],
                    "issue": "descrição",
                    "resolution_needed": "ação"
                }}],
                "ambiguous_responses": [{{
                    "field": "campo",
                    "response": "resposta",
                    "clarification_needed": "esclarecimento"
                }}]
            }},
            "translation_status": "APROVADO_PARA_TRADUCAO|NECESSITA_CORRECOES|INFORMACOES_INSUFICIENTES",
            "uscis_form_translation": "formulário traduzido ou [TRADUCAO PENDENTE]",
            "field_mapping": [{{
                "friendly_field": "campo amigável",
                "uscis_field": "campo oficial",
                "translated_value": "valor traduzido",
                "notes": "observações"
            }}],
            "quality_assurance": {{
                "translation_accuracy": "high|medium|low",
                "uscis_compliance": true/false,
                "ready_for_submission": true/false,
                "confidence_level": 0-100
            }},
            "recommendations": ["ação1"]
        }}
        
        SEJA RIGOROSO: Prefira solicitar esclarecimentos do que fazer traduções imprecisas.
        """
    
    async def translate_form(
        self,
        friendly_form_data: Dict[str, Any],
        target_uscis_form: str
    ) -> Dict[str, Any]:
        """Translate friendly form to official USCIS form"""
        prompt = f"""
        TRADUÇÃO E VALIDAÇÃO DE FORMULÁRIO USCIS
        
        Formulário Amigável: {friendly_form_data}
        Formulário USCIS Destino: {target_uscis_form}
        
        Valide e traduza o formulário amigável para o formato oficial USCIS.
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
                "translation_status": "FAILED"
            }


def create_uscis_form_translator(llm_client: Optional[LLMClient] = None, db=None) -> USCISFormTranslatorAgent:
    """Create a USCISFormTranslatorAgent instance"""
    return USCISFormTranslatorAgent(llm_client=llm_client, db=db)
