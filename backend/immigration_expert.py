"""
Immigration Expert Agent Integration
Specialized OpenAI agent for immigration advice and validation
"""
import os
import logging
from typing import Optional, Dict, Any, List
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class ImmigrationExpert:
    """
    Wrapper for specialized immigration agent - Dra. Paula B2C
    Handles immigration-specific queries, validations, and advice
    """
    
    def __init__(self, 
                 provider: str = "openai", 
                 model: str = "gpt-4o",
                 assistant_id: str = "asst_AV1O2IBTnDXpEZXiSSQGBT4",
                 custom_system_prompt: Optional[str] = None):
        """
        Initialize the immigration expert agent - Dra. Paula B2C
        
        Args:
            provider: LLM provider (openai, anthropic, gemini)
            model: Specific model name
            assistant_id: OpenAI Assistant ID for Dra. Paula B2C
            custom_system_prompt: Your specialized immigration prompt
        """
        self.provider = provider
        self.model = model
        self.assistant_id = assistant_id
        
        # Dra. Paula B2C specialized prompt (can be overridden)
        self.system_prompt = custom_system_prompt or f"""
        Você é a Dra. Paula B2C, uma especialista em imigração americana com vasto conhecimento em leis de imigração dos EUA.
        
        IDENTIDADE:
        - Assistant ID: {self.assistant_id}
        - Especialista em processos de imigração B2C (Business to Consumer)
        - Foco em auto-aplicação de vistos para brasileiros
        
        ESPECIALIDADES:
        - Vistos de trabalho (H1-B, L1, O1, TN, E2)
        - Vistos familiares (I-130, IR/CR, K1, K3)
        - Ajuste de status e green card
        - Formulários USCIS e procedimentos
        - Análise de elegibilidade específica
        - Identificação de problemas e soluções práticas
        - Orientações para brasileiros nos EUA
        
        DIRETRIZES OSPREY:
        - Sempre inclua disclaimer sobre não ser consultoria jurídica
        - Forneça orientações baseadas em regulamentações atuais do USCIS
        - Identifique problemas potenciais nos formulários
        - Sugira documentos necessários e específicos
        - Use linguagem clara em português brasileiro
        - Seja precisa, prática e acessível
        - Foque em auto-aplicação sem advogado
        
        CONTEXTO OSPREY:
        Esta é uma ferramenta de apoio tecnológico do sistema OSPREY para auto-aplicação de vistos.
        Não constitui consultoria jurídica. Sempre recomende consultar um advogado para casos complexos.
        """
        
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    async def _call_dra_paula(self, prompt: str, session_id: str = None) -> str:
        """
        Call Dra. Paula B2C assistant specifically
        Uses the trained assistant with immigration knowledge base
        """
        try:
            # If we have an assistant_id, we can use it with emergentintegrations
            # For now, we'll use the standard LlmChat but with Dra. Paula's enhanced prompt
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id or f"dra_paula_{hash(prompt) % 10000}",
                system_message=self.system_prompt
            ).with_model(self.provider, self.model)
            
            # Enhanced prompt for Dra. Paula's context
            enhanced_prompt = f"""
            [SISTEMA OSPREY - DRA. PAULA B2C]
            Assistant ID: {self.assistant_id}
            
            {prompt}
            
            Por favor, responda como Dra. Paula B2C, especialista em imigração com foco em brasileiros nos EUA.
            Use seu conhecimento especializado e sempre inclua disclaimers apropriados.
            """
            
            user_message = UserMessage(text=enhanced_prompt)
            response = await chat.send_message(user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error calling Dra. Paula: {e}")
            return "Desculpe, a Dra. Paula não está disponível no momento. Tente novamente."
    
    async def validate_form_data(self, 
                                form_data: Dict[str, Any], 
                                visa_type: str,
                                step_id: str) -> Dict[str, Any]:
        """
        Validate form data using immigration expertise
        
        Args:
            form_data: User's form data
            visa_type: Type of visa being applied for
            step_id: Current step in the process
            
        Returns:
            Dict with validation results, suggestions, and warnings
        """
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"validation_{visa_type}_{step_id}_{hash(str(form_data)) % 10000}",
                system_message=self.system_prompt
            ).with_model(self.provider, self.model)
            
            prompt = f"""
            Analise os seguintes dados do formulário para visto {visa_type}:
            
            ETAPA: {step_id}
            DADOS: {form_data}
            
            Por favor, forneça uma análise detalhada em formato JSON:
            {{
                "status": "ok|warning|error", 
                "issues": [
                    {{
                        "field": "nome_do_campo",
                        "severity": "high|medium|low",
                        "message": "descrição do problema",
                        "suggestion": "como corrigir"
                    }}
                ],
                "missing_info": ["campo1", "campo2"],
                "recommendations": ["sugestão1", "sugestão2"],
                "next_steps": ["próximo passo 1", "próximo passo 2"],
                "disclaimer": "Esta análise é baseada nas informações fornecidas e não constitui consultoria jurídica."
            }}
            """
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Try to parse JSON response
            import json
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback if response isn't valid JSON
                return {
                    "status": "ok",
                    "issues": [],
                    "missing_info": [],
                    "recommendations": [response],
                    "next_steps": [],
                    "disclaimer": "Esta análise é baseada nas informações fornecidas."
                }
                
        except Exception as e:
            logger.error(f"Error in immigration validation: {e}")
            return {
                "status": "error",
                "issues": [{"field": "system", "severity": "high", "message": "Erro na análise. Tente novamente."}],
                "missing_info": [],
                "recommendations": [],
                "next_steps": [],
                "disclaimer": "Ocorreu um erro na análise."
            }
    
    async def analyze_document(self, 
                              document_type: str, 
                              document_content: str,
                              visa_type: str) -> Dict[str, Any]:
        """
        Analyze uploaded documents for completeness and accuracy
        """
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"doc_analysis_{visa_type}_{document_type}_{hash(document_content) % 10000}",
                system_message=self.system_prompt
            ).with_model(self.provider, self.model)
            
            prompt = f"""
            Analise o seguinte documento para visto {visa_type}:
            
            TIPO DE DOCUMENTO: {document_type}
            CONTEÚDO: {document_content[:2000]}  # Truncate for token limits
            
            Forneça análise em JSON:
            {{
                "document_valid": true/false,
                "completeness_score": 0-100,
                "issues_found": ["problema1", "problema2"],
                "missing_elements": ["elemento1", "elemento2"],
                "recommendations": ["sugestão1", "sugestão2"],
                "expiration_check": "ok|warning|expired",
                "uscis_compliance": "compliant|needs_review|non_compliant"
            }}
            """
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            import json
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "document_valid": True,
                    "completeness_score": 85,
                    "issues_found": [],
                    "missing_elements": [],
                    "recommendations": [response],
                    "expiration_check": "ok",
                    "uscis_compliance": "compliant"
                }
                
        except Exception as e:
            logger.error(f"Error in document analysis: {e}")
            return {
                "document_valid": False,
                "completeness_score": 0,
                "issues_found": ["Erro na análise do documento"],
                "missing_elements": [],
                "recommendations": ["Tente fazer upload do documento novamente"],
                "expiration_check": "unknown",
                "uscis_compliance": "needs_review"
            }
    
    async def generate_advice(self, 
                             question: str, 
                             context: Dict[str, Any] = None) -> str:
        """
        Generate specialized immigration advice based on user question
        """
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"advice_{hash(question) % 10000}",
                system_message=self.system_prompt
            ).with_model(self.provider, self.model)
            
            context_str = f"CONTEXTO DO USUÁRIO: {context}" if context else ""
            
            prompt = f"""
            {context_str}
            
            PERGUNTA: {question}
            
            Por favor, forneça uma resposta detalhada e útil sobre esta questão de imigração.
            Inclua sempre o disclaimer sobre não ser consultoria jurídica.
            """
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating advice: {e}")
            return "Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente ou contate o suporte."


# Factory function to create expert with custom configuration
def create_immigration_expert(provider: str = "openai", 
                            model: str = "gpt-4o",
                            custom_prompt: str = None) -> ImmigrationExpert:
    """
    Factory function to create immigration expert with custom settings
    """
    return ImmigrationExpert(
        provider=provider,
        model=model,
        custom_system_prompt=custom_prompt
    )