"""
Specialized Immigration Agents System
Multiple expert agents for specific tasks in the immigration process
"""
import os
import logging
from typing import Optional, Dict, Any, List
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class BaseSpecializedAgent:
    """Base class for all specialized agents with Dra. Paula's knowledge base"""
    
    def __init__(self, 
                 agent_name: str,
                 specialization: str,
                 provider: str = "openai", 
                 model: str = "gpt-4o",
                 use_dra_paula_knowledge: bool = True):
        self.agent_name = agent_name
        self.specialization = specialization
        self.provider = provider
        self.model = model
        self.use_dra_paula_knowledge = use_dra_paula_knowledge
        self.dra_paula_assistant_id = "asst_AV1O2IBTnDXpEZXiSSQGBT4"  # Banco de dados da Dra. Paula
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    async def _call_agent(self, prompt: str, session_id: str) -> str:
        """Base method to call the specialized agent with Dra. Paula's knowledge"""
        try:
            # Use system prompt and enhanced user prompt
            system_message = f"""
            {self.get_system_prompt()}
            
            BANCO DE CONHECIMENTO DRA. PAULA B2C:
            Assistant ID: {self.dra_paula_assistant_id}
            
            Use o conhecimento especializado da Dra. Paula B2C sobre:
            - Leis de imigração americana atualizadas
            - Processos USCIS específicos 
            - Regulamentações e mudanças recentes
            - Precedentes e casos práticos
            - Documentação obrigatória por tipo de visto
            
            Combine sua especialização com o conhecimento da Dra. Paula para dar a resposta mais precisa possível.
            """
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=system_message
            ).with_model(self.provider, self.model)
            
            # Send the actual task as user message
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            return response
            
        except Exception as e:
            logger.error(f"Error calling {self.agent_name} with Dra. Paula's knowledge: {e}")
            return f"Erro ao processar com {self.agent_name}. Tente novamente."
    
    def get_system_prompt(self) -> str:
        """Override in subclasses for specific prompts"""
        raise NotImplementedError

class DocumentValidationAgent(BaseSpecializedAgent):
    """Specialized agent for document validation and authenticity checking"""
    
    def __init__(self):
        super().__init__(
            agent_name="Dr. Miguel - Validador de Documentos",
            specialization="Document Validation & Authenticity"
        )
    
    def get_system_prompt(self) -> str:
        return f"""
        Você é o Dr. Miguel, especialista EXCLUSIVO em validação de documentos de imigração.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({self.dra_paula_assistant_id}).
        
        EXPERTISE ESPECÍFICA COM CONHECIMENTO DA DRA. PAULA:
        - Validação de passaportes (formato, segurança, autenticidade) conforme padrões USCIS atuais
        - Análise de diplomas e certificados acadêmicos usando critérios específicos por país
        - Verificação de documentos de trabalho e cartas de emprego conforme regulamentações
        - Detecção de inconsistências e falsificações baseada em casos práticos
        - Conformidade com padrões USCIS usando conhecimento atualizado da Dra. Paula
        
        METODOLOGIA RIGOROSA COM CONHECIMENTO DRA. PAULA:
        1. Verificar se o documento é do tipo correto conforme lista USCIS atualizada
        2. Validar formato oficial e elementos de segurança usando padrões internacionais
        3. Confirmar dados pessoais consistentes com perfil do aplicante
        4. Detectar adulterações ou irregularidades usando técnicas especializadas
        5. Verificar validade e expiração conforme regulamentações atuais
        6. Aplicar conhecimento específico da Dra. Paula sobre documentos brasileiros nos EUA
        
        RESPOSTA SEMPRE EM JSON:
        {
            "agent": "Dr. Miguel - Validador",
            "document_authentic": true/false,
            "type_correct": true/false,
            "belongs_to_applicant": true/false,
            "security_elements": "valid|missing|suspicious",
            "critical_issues": ["issue1", "issue2"],
            "confidence_score": 0-100,
            "uscis_acceptable": true/false,
            "verdict": "APROVADO|REJEITADO|NECESSITA_REVISÃO",
            "technical_notes": "Observações técnicas detalhadas"
        }
        
        SEJA EXTREMAMENTE RIGOROSO. Melhor rejeitar documento duvidoso que aprovar documento inválido.
        """

class FormValidationAgent(BaseSpecializedAgent):
    """Specialized agent for form completion and data consistency"""
    
    def __init__(self):
        super().__init__(
            agent_name="Dra. Ana - Validadora de Formulários",
            specialization="Form Validation & Data Consistency"
        )
    
    def get_system_prompt(self) -> str:
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
        {
            "agent": "Dra. Ana - Formulários",
            "form_complete": true/false,
            "completion_percentage": 0-100,
            "missing_required": ["campo1", "campo2"],
            "format_errors": [{"field": "campo", "error": "descrição"}],
            "consistency_issues": [{"fields": ["campo1", "campo2"], "issue": "conflito"}],
            "uscis_compliance": true/false,
            "blocking_issues": ["issue1", "issue2"],
            "recommendations": ["ação1", "ação2"],
            "next_required_step": "próxima ação obrigatória"
        }
        
        SEJA PRECISA E DETALHISTA. Identifique TODOS os problemas antes de aprovar.
        """

class EligibilityAnalysisAgent(BaseSpecializedAgent):
    """Specialized agent for visa eligibility analysis"""
    
    def __init__(self):
        super().__init__(
            agent_name="Dr. Carlos - Analista de Elegibilidade", 
            specialization="Visa Eligibility Analysis"
        )
    
    def get_system_prompt(self) -> str:
        return f"""
        Você é o Dr. Carlos, especialista EXCLUSIVO em análise de elegibilidade para vistos americanos.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({self.dra_paula_assistant_id}).
        
        EXPERTISE ESPECÍFICA COM CONHECIMENTO DA DRA. PAULA:
        - Requisitos específicos por tipo de visto (H1-B, L1, O1, F1, etc.) com atualizações regulatórias
        - Análise de qualificações educacionais e profissionais usando equivalências brasileiras
        - Verificação de critérios de elegibilidade baseada em casos reais de brasileiros
        - Identificação de potenciais problemas de aprovação usando experiência prática
        - Recomendações para fortalecer a aplicação com estratégias comprovadas
        - Conhecimento específico sobre perfis brasileiros que obtiveram sucesso nos EUA
        
        ANÁLISE SISTEMÁTICA:
        1. Verificar se candidato atende critérios básicos
        2. Analisar força da aplicação
        3. Identificar pontos fracos ou riscos
        4. Sugerir melhorias ou documentação adicional
        5. Prever probabilidade de aprovação
        
        RESPOSTA SEMPRE EM JSON:
        {
            "agent": "Dr. Carlos - Elegibilidade",
            "eligible": true/false,
            "eligibility_score": 0-100,
            "met_requirements": ["req1", "req2"],
            "missing_requirements": ["req1", "req2"],
            "risk_factors": [{"risk": "descrição", "severity": "high|medium|low"}],
            "strengths": ["ponto forte 1", "ponto forte 2"],
            "recommendations": ["melhoria 1", "melhoria 2"],
            "approval_probability": "high|medium|low",
            "additional_evidence_needed": ["evidência 1", "evidência 2"]
        }
        
        SEJA REALISTA E HONESTO sobre as chances de aprovação.
        """

class ComplianceCheckAgent(BaseSpecializedAgent):
    """Specialized agent for USCIS compliance and final review"""
    
    def __init__(self):
        super().__init__(
            agent_name="Dra. Patricia - Compliance USCIS",
            specialization="USCIS Compliance & Final Review"
        )
    
    def get_system_prompt(self) -> str:
        return f"""
        Você é a Dra. Patricia, especialista EXCLUSIVA em compliance USCIS e revisão final.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({self.dra_paula_assistant_id}).
        
        EXPERTISE ESPECÍFICA COM CONHECIMENTO DA DRA. PAULA:
        - Regulamentações atuais do USCIS com atualizações mais recentes
        - Checklist final de compliance baseado em casos aprovados e rejeitados
        - Identificação de red flags usando experiência prática em casos brasileiros
        - Verificação de consistência geral aplicando padrões rigorosos do USCIS
        - Preparação para submissão com estratégias de sucesso comprovadas
        - Conhecimento específico sobre armadilhas comuns em aplicações brasileiras
        
        CHECKLIST FINAL OBRIGATÓRIO:
        1. Todos os documentos necessários incluídos
        2. Formulários preenchidos corretamente
        3. Taxas corretas calculadas
        4. Nenhuma inconsistência entre documentos
        5. Conformidade com regulamentações atuais
        
        RESPOSTA SEMPRE EM JSON:
        {
            "agent": "Dra. Patricia - Compliance",
            "uscis_compliant": true/false,
            "ready_for_submission": true/false,
            "compliance_score": 0-100,
            "red_flags": ["flag1", "flag2"],
            "missing_elements": ["elemento1", "elemento2"],
            "final_checklist": [{"item": "descrição", "status": "ok|missing|issue"}],
            "submission_recommendation": "ENVIAR|NÃO_ENVIAR|REVISAR_PRIMEIRO",
            "final_notes": "Observações finais críticas"
        }
        
        SEJA A ÚLTIMA LINHA DE DEFESA. Só aprove aplicações 100% prontas.
        """

class UrgencyTriageAgent(BaseSpecializedAgent):
    """Agent to triage issues by urgency and route to appropriate specialist"""
    
    def __init__(self):
        super().__init__(
            agent_name="Dr. Roberto - Triagem",
            specialization="Issue Triage & Routing"
        )
    
    def get_system_prompt(self) -> str:
        return """
        Você é o Dr. Roberto, especialista em triagem e roteamento de questões de imigração.
        
        FUNÇÃO PRINCIPAL:
        - Classificar urgência e tipo de problema
        - Rotear para o especialista correto
        - Priorizar questões críticas
        - Coordenar múltiplos agentes quando necessário
        
        ESPECIALISTAS DISPONÍVEIS:
        1. Dr. Miguel - Validação de Documentos
        2. Dra. Ana - Validação de Formulários  
        3. Dr. Carlos - Análise de Elegibilidade
        4. Dra. Patricia - Compliance USCIS
        
        RESPOSTA SEMPRE EM JSON:
        {
            "agent": "Dr. Roberto - Triagem",
            "urgency": "CRÍTICO|ALTO|MÉDIO|BAIXO",
            "issue_type": "documento|formulário|elegibilidade|compliance|geral",
            "recommended_specialist": "Dr. Miguel|Dra. Ana|Dr. Carlos|Dra. Patricia",
            "requires_multiple_agents": true/false,
            "priority_order": ["agent1", "agent2"],
            "estimated_complexity": "simples|moderado|complexo",
            "immediate_action_needed": true/false
        }
        """

# Factory functions for each specialized agent
def create_document_validator() -> DocumentValidationAgent:
    return DocumentValidationAgent()

def create_form_validator() -> FormValidationAgent:
    return FormValidationAgent()

def create_eligibility_analyst() -> EligibilityAnalysisAgent:
    return EligibilityAnalysisAgent()

def create_compliance_checker() -> ComplianceCheckAgent:
    return ComplianceCheckAgent()

def create_urgency_triage() -> UrgencyTriageAgent:
    return UrgencyTriageAgent()

# Multi-Agent Coordinator
class SpecializedAgentCoordinator:
    """Coordinates multiple specialized agents for comprehensive analysis"""
    
    def __init__(self):
        self.agents = {
            "document_validator": create_document_validator(),
            "form_validator": create_form_validator(), 
            "eligibility_analyst": create_eligibility_analyst(),
            "compliance_checker": create_compliance_checker(),
            "triage": create_urgency_triage()
        }
    
    async def analyze_comprehensive(self, 
                                  task_type: str,
                                  data: Dict[str, Any],
                                  user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis using appropriate specialized agents
        """
        results = {
            "coordinator": "Specialized Agent System",
            "task_type": task_type,
            "analyses": {},
            "summary": {},
            "recommendations": []
        }
        
        try:
            # First, use triage to determine which agents to use
            triage_prompt = f"""
            Analise esta tarefa e determine quais especialistas devem ser consultados:
            
            TIPO DE TAREFA: {task_type}
            DADOS: {data}
            CONTEXTO: {user_context}
            """
            
            triage_response = await self.agents["triage"]._call_agent(
                triage_prompt, 
                f"triage_{hash(str(data)) % 10000}"
            )
            
            results["triage"] = triage_response
            
            # Based on task type, call appropriate agents
            if task_type == "document_validation":
                doc_analysis = await self.agents["document_validator"]._call_agent(
                    self._build_document_prompt(data, user_context),
                    f"doc_val_{hash(str(data)) % 10000}"
                )
                results["analyses"]["document_validation"] = doc_analysis
                
            elif task_type == "form_validation":
                form_analysis = await self.agents["form_validator"]._call_agent(
                    self._build_form_prompt(data, user_context),
                    f"form_val_{hash(str(data)) % 10000}"
                )
                results["analyses"]["form_validation"] = form_analysis
                
            elif task_type == "eligibility_check":
                eligibility_analysis = await self.agents["eligibility_analyst"]._call_agent(
                    self._build_eligibility_prompt(data, user_context),
                    f"elig_check_{hash(str(data)) % 10000}"
                )
                results["analyses"]["eligibility"] = eligibility_analysis
                
            elif task_type == "compliance_review":
                compliance_analysis = await self.agents["compliance_checker"]._call_agent(
                    self._build_compliance_prompt(data, user_context),
                    f"compliance_{hash(str(data)) % 10000}"
                )
                results["analyses"]["compliance"] = compliance_analysis
            
            # Always do final summary
            results["summary"] = self._generate_summary(results["analyses"])
            
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {
                "coordinator": "Specialized Agent System",
                "error": str(e),
                "analyses": {},
                "summary": {"status": "error"},
                "recommendations": ["Erro no sistema - tente novamente"]
            }
    
    def _build_document_prompt(self, data: Dict, context: Dict) -> str:
        return f"""
        VALIDAÇÃO DE DOCUMENTO - DR. MIGUEL
        
        Documento Esperado: {data.get('document_type', 'N/A')}
        Conteúdo: {data.get('document_content', 'N/A')[:1000]}
        Dados do Usuário: {context.get('user_data', {})}
        
        Faça validação rigorosa de autenticidade e conformidade.
        """
    
    def _build_form_prompt(self, data: Dict, context: Dict) -> str:
        return f"""
        VALIDAÇÃO DE FORMULÁRIO - DRA. ANA
        
        Formulário: {data.get('form_data', {})}
        Tipo de Visto: {data.get('visa_type', 'N/A')}
        Etapa: {data.get('step_id', 'N/A')}
        
        Verifique completude, formatação e consistência.
        """
    
    def _build_eligibility_prompt(self, data: Dict, context: Dict) -> str:
        return f"""
        ANÁLISE DE ELEGIBILIDADE - DR. CARLOS
        
        Perfil do Candidato: {data.get('applicant_profile', {})}
        Visto Desejado: {data.get('visa_type', 'N/A')}
        Qualificações: {data.get('qualifications', {})}
        
        Avalie elegibilidade e chances de aprovação.
        """
    
    def _build_compliance_prompt(self, data: Dict, context: Dict) -> str:
        return f"""
        REVISÃO FINAL DE COMPLIANCE - DRA. PATRICIA
        
        Aplicação Completa: {data.get('complete_application', {})}
        Documentos: {data.get('documents', [])}
        Formulários: {data.get('forms', {})}
        
        Verifique se está pronto para submissão ao USCIS.
        """
    
    def _generate_summary(self, analyses: Dict) -> Dict:
        """Generate overall summary from all agent analyses"""
        summary = {
            "overall_status": "needs_review",
            "critical_issues": 0,
            "agents_consulted": list(analyses.keys()),
            "ready_to_proceed": False
        }
        
        # Count critical issues across all analyses
        # This would need more sophisticated logic based on actual response formats
        
        return summary