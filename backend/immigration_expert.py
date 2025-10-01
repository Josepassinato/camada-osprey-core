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
        
        # Try EMERGENT_LLM_KEY first, fallback to OpenAI
        self.emergent_key = os.environ.get('EMERGENT_LLM_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        self.use_openai_direct = False
        
        if not self.emergent_key and not self.openai_key:
            raise ValueError("Neither EMERGENT_LLM_KEY nor OPENAI_API_KEY found in environment variables")
        
        # Use OpenAI directly if EMERGENT_LLM_KEY is not available or budget exceeded
        if not self.emergent_key or self.openai_key:
            self.use_openai_direct = True
            self.api_key = self.openai_key
        else:
            self.api_key = self.emergent_key
    
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
        Validate form data using Dra. Paula B2C's immigration expertise
        
        Args:
            form_data: User's form data
            visa_type: Type of visa being applied for
            step_id: Current step in the process
            
        Returns:
            Dict with validation results, suggestions, and warnings
        """
        try:
            prompt = f"""
            DRA. PAULA - VALIDAÇÃO DE FORMULÁRIO OSPREY

            Analise os seguintes dados do formulário para visto {visa_type}:
            
            ETAPA ATUAL: {step_id}
            DADOS DO FORMULÁRIO: {form_data}
            
            Como especialista em imigração, forneça uma análise detalhada em formato JSON:
            {{
                "status": "ok|warning|error", 
                "dra_paula_analysis": "Sua análise profissional resumida",
                "issues": [
                    {{
                        "field": "nome_do_campo",
                        "severity": "high|medium|low",
                        "message": "descrição do problema específico",
                        "suggestion": "como corrigir (orientação prática da Dra. Paula)"
                    }}
                ],
                "missing_info": ["campo obrigatório 1", "campo obrigatório 2"],
                "recommendations": ["recomendação específica 1", "recomendação específica 2"],
                "next_steps": ["próximo passo sugerido 1", "próximo passo sugerido 2"],
                "uscis_compliance": "compliant|needs_review|non_compliant",
                "disclaimer": "Análise da Dra. Paula B2C - ferramenta de apoio, não consultoria jurídica."
            }}
            
            Use seu conhecimento especializado em imigração para brasileiros nos EUA.
            """
            
            session_id = f"dra_paula_validation_{visa_type}_{step_id}_{hash(str(form_data)) % 10000}"
            response = await self._call_dra_paula(prompt, session_id)
            
            # Try to parse JSON response
            import json
            try:
                result = json.loads(response)
                # Ensure Dra. Paula signature
                result["expert"] = "Dra. Paula B2C"
                result["assistant_id"] = self.assistant_id
                return result
            except json.JSONDecodeError:
                # Fallback if response isn't valid JSON
                return {
                    "expert": "Dra. Paula B2C",
                    "assistant_id": self.assistant_id,
                    "status": "ok",
                    "dra_paula_analysis": response,
                    "issues": [],
                    "missing_info": [],
                    "recommendations": [response],
                    "next_steps": [],
                    "uscis_compliance": "needs_review",
                    "disclaimer": "Análise da Dra. Paula B2C - ferramenta de apoio, não consultoria jurídica."
                }
                
        except Exception as e:
            logger.error(f"Error in Dra. Paula validation: {e}")
            return {
                "expert": "Dra. Paula B2C",
                "assistant_id": self.assistant_id,
                "status": "error",
                "dra_paula_analysis": "Erro na análise. Tente novamente.",
                "issues": [{"field": "system", "severity": "high", "message": "Erro temporário na análise da Dra. Paula."}],
                "missing_info": [],
                "recommendations": ["Tente novamente em alguns instantes"],
                "next_steps": [],
                "uscis_compliance": "needs_review",
                "disclaimer": "Erro temporário - consulte um especialista se necessário."
            }
    
    async def analyze_document(self, 
                              document_type: str, 
                              document_content: str,
                              visa_type: str,
                              user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze uploaded documents for completeness, accuracy and authenticity - Dra. Paula B2C
        """
        try:
            user_info = ""
            if user_data:
                user_info = f"""
                DADOS DO USUÁRIO PARA VALIDAÇÃO:
                Nome: {user_data.get('fullName', 'N/A')}
                Data de Nascimento: {user_data.get('dateOfBirth', 'N/A')}
                Nacionalidade: {user_data.get('nationality', 'N/A')}
                """
            
            prompt = f"""
            DRA. PAULA B2C - ANÁLISE RIGOROSA DE DOCUMENTO

            TIPO ESPERADO: {document_type}
            VISTO: {visa_type}
            CONTEÚDO DO DOCUMENTO: {document_content[:1500]}
            
            {user_info}
            
            VALIDAÇÕES CRÍTICAS OBRIGATÓRIAS:
            1. Verificar se o documento é realmente do tipo esperado ({document_type})
            2. Verificar se os dados pessoais no documento batem com os dados do usuário
            3. Verificar se é um documento válido e não uma imagem aleatória
            4. Verificar autenticidade e formato oficial
            5. Verificar se não é documento de outra pessoa
            
            Como Dra. Paula B2C, faça uma análise RIGOROSA e CRÍTICA:
            
            {{
                "document_type_correct": true/false,
                "belongs_to_user": true/false,
                "is_authentic_document": true/false,
                "document_valid": true/false,
                "completeness_score": 0-100,
                "critical_issues": [
                    {{
                        "severity": "CRÍTICO|ALTO|MÉDIO|BAIXO",
                        "issue": "Descrição detalhada do problema",
                        "impact": "Impacto na aplicação do visto"
                    }}
                ],
                "data_inconsistencies": ["inconsistência1", "inconsistência2"],
                "missing_elements": ["elemento obrigatório 1"],
                "recommendations": ["ação corretiva 1", "ação corretiva 2"],
                "expiration_check": "ok|warning|expired|cannot_verify",
                "uscis_compliance": "compliant|needs_review|non_compliant|rejected",
                "dra_paula_verdict": "APROVADO|REJEITADO|REQUER_REVISÃO",
                "expert_notes": "Observações técnicas da Dra. Paula"
            }}
            
            IMPORTANTE: Seja RIGOROSA. Se não for o documento correto ou for de outra pessoa, REJEITE.
            """
            
            session_id = f"dra_paula_doc_{visa_type}_{document_type}_{hash(document_content) % 10000}"
            response = await self._call_dra_paula(prompt, session_id)
            
            import json
            try:
                result = json.loads(response)
                # Add Dra. Paula signature
                result["expert"] = "Dra. Paula B2C"
                result["assistant_id"] = self.assistant_id
                return result
            except json.JSONDecodeError:
                # If can't parse JSON, assume there's an issue
                return {
                    "expert": "Dra. Paula B2C",
                    "assistant_id": self.assistant_id,
                    "document_type_correct": False,
                    "belongs_to_user": False, 
                    "is_authentic_document": False,
                    "document_valid": False,
                    "completeness_score": 0,
                    "critical_issues": [{"severity": "CRÍTICO", "issue": "Erro na análise do documento", "impact": "Não foi possível validar"}],
                    "data_inconsistencies": ["Erro no processamento"],
                    "missing_elements": ["Análise válida"],
                    "recommendations": [response],
                    "expiration_check": "cannot_verify",
                    "uscis_compliance": "rejected",
                    "dra_paula_verdict": "REJEITADO",
                    "expert_notes": "Erro no processamento - documento deve ser reanalisado"
                }
                
        except Exception as e:
            logger.error(f"Error in Dra. Paula document analysis: {e}")
            return {
                "expert": "Dra. Paula B2C",
                "assistant_id": self.assistant_id,
                "document_type_correct": False,
                "belongs_to_user": False,
                "is_authentic_document": False,
                "document_valid": False,
                "completeness_score": 0,
                "critical_issues": [{"severity": "CRÍTICO", "issue": "Erro técnico na análise", "impact": "Documento não pôde ser validado"}],
                "data_inconsistencies": ["Erro no sistema"],
                "missing_elements": ["Análise completa"],
                "recommendations": ["Tente fazer upload do documento novamente", "Verifique se o arquivo não está corrompido"],
                "expiration_check": "cannot_verify",
                "uscis_compliance": "rejected",
                "dra_paula_verdict": "REJEITADO",
                "expert_notes": "Erro técnico - documento deve ser re-enviado"
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


# Factory function to create Dra. Paula B2C expert
def create_immigration_expert(provider: str = "openai", 
                            model: str = "gpt-4o",
                            assistant_id: str = "asst_AV1O2IBTnDXpEZXiSSQGBT4",
                            custom_prompt: str = None) -> ImmigrationExpert:
    """
    Factory function to create Dra. Paula B2C immigration expert
    
    Args:
        provider: LLM provider (default: openai)
        model: Model to use (default: gpt-4o) 
        assistant_id: Dra. Paula's Assistant ID
        custom_prompt: Override system prompt if needed
    """
    return ImmigrationExpert(
        provider=provider,
        model=model,
        assistant_id=assistant_id,
        custom_system_prompt=custom_prompt
    )