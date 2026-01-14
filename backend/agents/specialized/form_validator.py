"""
Form Validation Agent

Specialized agent for form completion and data consistency validation.
Dra. Ana - Expert in USCIS form validation.
"""

import logging
from typing import Any, Dict, Optional

from agents.base import BaseAgent
from llm.portkey_client import LLMClient

logger = logging.getLogger(__name__)


class FormValidationAgent(BaseAgent):
    """
    Specialized agent for form completion and data consistency
    
    Dra. Ana - USCIS form validation expert
    
    Capabilities:
    - Required field validation
    - Data format verification
    - Cross-section consistency checking
    - USCIS compliance verification
    - Conflict detection
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        db=None,
        use_dra_paula_knowledge: bool = True
    ):
        """
        Initialize Form Validation Agent
        
        Args:
            llm_client: LLM client instance
            db: MongoDB connection for knowledge base access
            use_dra_paula_knowledge: Whether to use Dra. Paula's knowledge base
        """
        super().__init__(
            llm_client=llm_client,
            agent_name="Dra. Ana - Validadora de Formulários",
            default_model="gpt-4o",
            default_temperature=0.3,
        )
        
        self.db = db
        self.use_dra_paula_knowledge = use_dra_paula_knowledge
        self.dra_paula_assistant_id = "asst_kkyn65SQFfkloH4SalOZfwwh"
        self.specialization = "Form Validation & Data Consistency"
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process form validation request
        
        Args:
            input_data: Dict containing:
                - form_data: Form data to validate
                - form_type: Type of form (I-129, I-130, etc.)
                - visa_type: Optional visa type for context
        
        Returns:
            Dict containing validation results
        """
        form_data = input_data.get("form_data")
        form_type = input_data.get("form_type")
        visa_type = input_data.get("visa_type")
        
        if not form_data or not form_type:
            return {
                "agent": self.agent_name,
                "error": "Missing required fields: form_data and form_type",
                "form_complete": False
            }
        
        return await self.validate_form(
            form_data=form_data,
            form_type=form_type,
            visa_type=visa_type
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Dra. Ana"""
        return f"""
        Você é a Dra. Ana, especialista EXCLUSIVA em validação de formulários USCIS.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({self.dra_paula_assistant_id}).
        
        EXPERTISE ESPECÍFICA COM CONHECIMENTO DA DRA. PAULA:
        - Validação de campos obrigatórios por tipo de visto usando critérios atualizados
        - Consistência de dados entre seções conforme regulamentações USCIS
        - Formatação correta de datas, endereços, nomes seguindo padrões americanos
        - Regras específicas por formulário (I-129, I-130, etc.) com atualizações recentes
        - Detecção de campos conflitantes baseada em casos práticos da Dra. Paula
        
        VALIDAÇÕES OBRIGATÓRIAS COM CONHECIMENTO DRA. PAULA:
        1. Todos os campos obrigatórios preenchidos conforme lista USCIS atualizada
        2. Formatos corretos (datas MM/DD/YYYY, telefones, etc.) seguindo padrões americanos
        3. Consistência entre seções diferentes usando lógica de validação cruzada
        4. Conformidade com regras específicas do visto baseada em regulamentações atuais
        5. Detecção de informações conflitantes usando conhecimento prático da Dra. Paula
        6. Aplicação de regras específicas para brasileiros aplicando nos EUA
        
        RESPOSTA SEMPRE EM JSON:
        {{
            "agent": "Dra. Ana - Formulários",
            "form_complete": true/false,
            "completion_percentage": 0-100,
            "missing_required": ["campo1", "campo2"],
            "format_errors": [{{"field": "campo", "error": "descrição"}}],
            "consistency_issues": [{{"fields": ["campo1", "campo2"], "issue": "conflito"}}],
            "uscis_compliance": true/false,
            "blocking_issues": ["issue1", "issue2"],
            "recommendations": ["ação1", "ação2"],
            "next_required_step": "próxima ação obrigatória"
        }}
        
        SEJA PRECISA E DETALHISTA. Identifique TODOS os problemas antes de aprovar.
        """
    
    async def _get_knowledge_base_context(
        self,
        form_type: str,
        agent_role: str = "form_validation"
    ) -> str:
        """Get relevant context from knowledge base"""
        try:
            if not self.db:
                return ""
            
            from backend.knowledge.helper import get_knowledge_helper
            helper = get_knowledge_helper(self.db)
            
            context = await helper.get_context_for_agent(form_type, agent_role)
            return context
            
        except Exception as e:
            logger.warning(f"Could not fetch knowledge base context: {e}")
            return ""
    
    async def validate_form(
        self,
        form_data: Dict[str, Any],
        form_type: str,
        visa_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate form data for completeness and consistency
        
        Args:
            form_data: Form data to validate
            form_type: Type of form (I-129, I-130, etc.)
            visa_type: Optional visa type for context
        
        Returns:
            Dict containing validation results
        """
        # Get knowledge base context
        kb_context = await self._get_knowledge_base_context(form_type)
        
        # Build validation prompt
        prompt = f"""
        VALIDAÇÃO DE FORMULÁRIO USCIS
        
        Tipo de Formulário: {form_type}
        Tipo de Visto: {visa_type or 'Não especificado'}
        
        Dados do Formulário:
        {form_data}
        
        Por favor, valide:
        1. Todos os campos obrigatórios estão preenchidos?
        2. Os formatos estão corretos (datas, telefones, etc.)?
        3. Há consistência entre as seções?
        4. O formulário está em conformidade com USCIS?
        5. Há algum conflito ou inconsistência nos dados?
        
        Forneça análise detalhada no formato JSON especificado.
        """
        
        # Build messages
        messages = self._build_messages(
            system_prompt=self.get_system_prompt() + f"\n\n{kb_context}",
            user_message=prompt
        )
        
        # Call LLM
        response = await self._call_llm(messages)
        
        # Try to parse JSON response
        try:
            import json
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "agent": self.agent_name,
                "raw_response": response,
                "parse_error": True,
                "form_complete": False
            }


# Factory function
def create_form_validator(llm_client: Optional[LLMClient] = None, db=None) -> FormValidationAgent:
    """Create a FormValidationAgent instance"""
    return FormValidationAgent(llm_client=llm_client, db=db)
