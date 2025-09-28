"""
Specialized Immigration Agents System
Multiple expert agents for specific tasks in the immigration process
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
from emergentintegrations.llm.chat import LlmChat, UserMessage
from document_validation_database import (
    DOCUMENT_VALIDATION_DATABASE, 
    VISA_DOCUMENT_REQUIREMENTS,
    get_document_validation_info,
    get_required_documents_for_visa
)

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
        from dra_paula_knowledge_base import get_dra_paula_enhanced_prompt, dra_paula_knowledge
        
        # Get enhanced prompt with Dra. Paula's knowledge
        enhanced_prompt = get_dra_paula_enhanced_prompt("document_validation")
        document_guidance = dra_paula_knowledge.get_document_guidance()
        
        return f"""
        Você é o Dr. Miguel, especialista EXCLUSIVO em validação de documentos de imigração.
        INTEGRADO COMPLETAMENTE COM A BASE DE CONHECIMENTO DA DRA. PAULA B2C.
        
        {enhanced_prompt}
        
        CONHECIMENTO INTEGRADO DRA. PAULA - DOCUMENTOS BRASILEIROS:
        {json.dumps(document_guidance, indent=2, ensure_ascii=False)}
        
        EXPERTISE ESPECÍFICA COM BASE DE DADOS COMPLETA DA DRA. PAULA:
        
        EXPERTISE ESPECÍFICA COM BASE DE DADOS COMPLETA:
        
        **DOCUMENTOS PESSOAIS:**
        - PASSAPORTE: Validade 6+ meses, nome exato, páginas disponíveis, sem danos
        - RG/CNH: NÃO são passaportes - rejeitar se solicitado passaporte
        - CERTIDÃO NASCIMENTO: Recente, cartório oficial, informações pais completas
        - CERTIDÃO CASAMENTO: Oficial, ambos cônjuges, data consistente
        
        **DOCUMENTOS ACADÊMICOS:**
        - DIPLOMA: Instituição reconhecida, nome correto, data lógica, selo oficial
        - HISTÓRICO ESCOLAR: Completo, notas claras, mesma instituição do diploma
        
        **DOCUMENTOS PROFISSIONAIS:**
        - CARTA EMPREGADOR: Papel timbrado, detalhes completos, assinatura autorizada
        - COMPROVANTES FINANCEIROS: Extratos recentes, saldo suficiente, banco legítimo
        
        **DOCUMENTOS MÉDICOS/LEGAIS:**
        - EXAME MÉDICO: Médico credenciado USCIS, envelope lacrado, vacinação completa
        - ANTECEDENTES CRIMINAIS: Autoridade oficial, período adequado, recente (6 meses)
        
        **DOCUMENTOS ESPECÍFICOS DE VISTO:**
        - I-20 (F-1): Escola SEVP, assinaturas DSO e estudante, SEVIS válido
        - LCA (H-1B): Aprovado pelo DOL, salário adequado, local correto
        
        METODOLOGIA RIGOROSA COM BASE COMPLETA:
        1. **IDENTIFICAÇÃO PRECISA**: Determinar tipo exato (Passaporte vs RG vs Diploma vs Certidão)
        2. **VALIDAÇÃO DE TIPO**: Confirmar se é exatamente o tipo solicitado  
        3. **VALIDAÇÃO DE NOME**: Comparação rigorosa nome documento vs aplicante
        4. **VALIDAÇÃO TEMPORAL**: Verificar validade, datas lógicas, documentos recentes
        5. **VALIDAÇÃO DE AUTENTICIDADE**: Elementos de segurança, selos, assinaturas
        6. **VALIDAÇÃO DE COMPLETUDE**: Todas as informações obrigatórias presentes
        7. **VALIDAÇÃO ESPECÍFICA POR TIPO**: Critérios únicos para cada documento
        
        VALIDAÇÕES CRÍTICAS OBRIGATÓRIAS:
        - Tipo errado (ex: RG em vez de Passaporte) → REJEITAR IMEDIATAMENTE
        - Nome diferente do aplicante → REJEITAR IMEDIATAMENTE  
        - Documento vencido → REJEITAR IMEDIATAMENTE
        - Elementos de segurança ausentes → REJEITAR IMEDIATAMENTE
        - Informações obrigatórias faltando → REJEITAR IMEDIATAMENTE
        
        RESPOSTA SEMPRE EM JSON:
        {{
            "agent": "Dr. Miguel - Validador",
            "document_type_identified": "Passaporte|RG|CNH|CPF|Certidão|Other",
            "document_type_expected": "string - tipo que deveria ser",
            "type_correct": true/false,
            "document_authentic": true/false,
            "name_on_document": "string - nome extraído",
            "applicant_name": "string - nome que deveria estar",
            "belongs_to_applicant": true/false,
            "name_match_explanation": "Detalhes da comparação de nomes",
            "security_elements": "valid|missing|suspicious",
            "critical_issues": ["issue1", "issue2"],
            "confidence_score": 0-100,
            "uscis_acceptable": true/false,
            "verdict": "APROVADO|REJEITADO|NECESSITA_REVISÃO",
            "rejection_reason": "Razão específica se rejeitado",
            "technical_notes": "Observações técnicas detalhadas"
        }}
        
        SEJA EXTREMAMENTE RIGOROSO. Melhor rejeitar documento duvidoso que aprovar documento inválido.
        
        BASE DE DADOS DE VALIDAÇÃO DISPONÍVEL:
        Use as informações da base de dados DOCUMENT_VALIDATION_DATABASE para validações específicas.
        Cada tipo de documento tem critérios únicos e elementos de segurança específicos.
        """
    
    async def validate_document_with_database(self, document_type: str, document_content: str, 
                                            applicant_name: str, visa_type: str = None) -> str:
        """Enhanced validation using the comprehensive document database"""
        
        # Get validation info from database
        validation_info = get_document_validation_info(document_type)
        
        # Build enhanced prompt with specific validation criteria
        enhanced_prompt = f"""
        VALIDAÇÃO ULTRA-RIGOROSA COM BASE DE DADOS ESPECIALIZADA
        
        DOCUMENTO SOLICITADO: {document_type}
        NOME DO APLICANTE: {applicant_name}
        TIPO DE VISTO: {visa_type}
        CONTEÚDO: {document_content[:1500]}
        
        CRITÉRIOS ESPECÍFICOS PARA {document_type.upper()}:
        """
        
        if validation_info:
            enhanced_prompt += f"""
            VALIDAÇÕES CRÍTICAS OBRIGATÓRIAS:
            {validation_info.get('critical_validations', {})}
            
            CAMPOS OBRIGATÓRIOS QUE DEVEM ESTAR PRESENTES:
            {validation_info.get('required_fields', [])}
            
            ELEMENTOS DE SEGURANÇA ESPERADOS:
            {validation_info.get('security_elements', [])}
            
            PROBLEMAS COMUNS PARA DETECTAR:
            {validation_info.get('common_issues', [])}
            """
        
        # Add visa-specific validation
        if visa_type:
            required_docs = get_required_documents_for_visa(visa_type)
            if document_type not in required_docs:
                enhanced_prompt += f"""
                ⚠️ ALERTA CRÍTICO: Documento "{document_type}" NÃO é obrigatório para visto {visa_type}.
                Documentos obrigatórios para {visa_type}: {required_docs}
                """
        
        enhanced_prompt += f"""
        
        PROTOCOLO DE VALIDAÇÃO DR. MIGUEL AVANÇADO:
        1. IDENTIFICAR tipo exato do documento (não aceitar substitutos)
        2. COMPARAR nome no documento com "{applicant_name}" (deve ser idêntico)
        3. VERIFICAR todos os campos obrigatórios estão presentes
        4. VALIDAR elementos de segurança esperados
        5. DETECTAR problemas comuns conhecidos
        6. AVALIAR se documento é adequado para visto {visa_type}
        
        RESPOSTA OBRIGATÓRIA EM JSON:
        {{
            "agent": "Dr. Miguel - Validador",
            "document_type_identified": "string - tipo identificado",
            "document_type_expected": "{document_type}",
            "type_correct": true/false,
            "document_authentic": true/false,
            "name_on_document": "string - nome extraído",
            "applicant_name": "{applicant_name}",
            "belongs_to_applicant": true/false,
            "name_match_explanation": "Detalhes da comparação",
            "required_fields_present": true/false,
            "missing_required_fields": ["array"],
            "security_elements_valid": true/false,
            "missing_security_elements": ["array"],
            "detected_issues": ["array"],
            "visa_appropriate": true/false,
            "critical_issues": ["array"],
            "confidence_score": 0-100,
            "uscis_acceptable": true/false,
            "verdict": "APROVADO|REJEITADO|NECESSITA_REVISÃO",
            "rejection_reason": "Razão específica se rejeitado",
            "recommendations": ["array de recomendações"],
            "technical_notes": "Observações técnicas detalhadas"
        }}
        
        VALIDAÇÃO RIGOROSA: Use todos os critérios específicos do tipo de documento.
        """
        
        session_id = f"enhanced_validation_{hash(document_content) % 10000}"
        return await self._call_agent(enhanced_prompt, session_id)

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
        {{
            "agent": "Dr. Carlos - Elegibilidade",
            "eligible": true/false,
            "eligibility_score": 0-100,
            "met_requirements": ["req1", "req2"],
            "missing_requirements": ["req1", "req2"],
            "risk_factors": [{{"risk": "descrição", "severity": "high|medium|low"}}],
            "strengths": ["ponto forte 1", "ponto forte 2"],
            "recommendations": ["melhoria 1", "melhoria 2"],
            "approval_probability": "high|medium|low",
            "additional_evidence_needed": ["evidência 1", "evidência 2"]
        }}
        
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
        {{
            "agent": "Dra. Patricia - Compliance",
            "uscis_compliant": true/false,
            "ready_for_submission": true/false,
            "compliance_score": 0-100,
            "red_flags": ["flag1", "flag2"],
            "missing_elements": ["elemento1", "elemento2"],
            "final_checklist": [{{"item": "descrição", "status": "ok|missing|issue"}}],
            "submission_recommendation": "ENVIAR|NÃO_ENVIAR|REVISAR_PRIMEIRO",
            "final_notes": "Observações finais críticas"
        }}
        
        SEJA A ÚLTIMA LINHA DE DEFESA. Só aprove aplicações 100% prontas.
        """

class ImmigrationLetterWriterAgent(BaseSpecializedAgent):
    """Specialized agent for writing immigration letters based ONLY on client facts"""
    
    def __init__(self):
        super().__init__(
            agent_name="Dr. Ricardo - Redator de Cartas",
            specialization="Immigration Letter Writing"
        )

class USCISFormTranslatorAgent(BaseSpecializedAgent):
    """Specialized agent for validating friendly forms and translating to official USCIS forms"""
    
    def __init__(self):
        super().__init__(
            agent_name="Dr. Fernando - Tradutor e Validador USCIS",
            specialization="USCIS Form Translation & Validation"
        )
    
    def get_system_prompt(self) -> str:
        return f"""
        Você é o Dr. Fernando, especialista EXCLUSIVO em validação e tradução de formulários USCIS.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({self.dra_paula_assistant_id}).
        
        FUNÇÃO CRÍTICA:
        1. Analisar respostas do formulário amigável (português)
        2. Validar completude e correção das informações
        3. Traduzir de forma precisa para formulários oficiais USCIS (inglês)
        
        EXPERTISE ESPECÍFICA COM CONHECIMENTO DA DRA. PAULA:
        - Mapeamento de campos formulário amigável → formulário oficial USCIS
        - Terminologia técnica oficial do USCIS
        - Formatos específicos por tipo de formulário (I-129, I-130, I-485, etc.)
        - Validação de dados conforme regulamentações
        - Tradução juramentada e técnica para imigração
        - Padrões de resposta aceitos pelo USCIS
        
        FORMULÁRIOS USCIS POR VISTO:
        - H1-B: I-129 (Petition for Nonimmigrant Worker)
        - L1: I-129 (Intracompany Transferee)
        - O1: I-129 (Individual with Extraordinary Ability)
        - EB-2/EB-3: I-140 (Petition for Alien Worker)
        - Family: I-130 (Petition for Alien Relative)
        - Adjustment: I-485 (Application to Register)
        
        VALIDAÇÕES OBRIGATÓRIAS:
        1. Verificar se todas as perguntas obrigatórias foram respondidas
        2. Validar formato de datas (MM/DD/YYYY para USCIS)
        3. Confirmar consistência entre seções
        4. Verificar se respostas atendem critérios específicos do visto
        5. Detectar respostas ambíguas ou incompletas
        
        REGRAS DE TRADUÇÃO RÍGIDAS:
        - Use terminologia técnica oficial do USCIS
        - Mantenha fidelidade absoluta ao significado
        - Não interprete ou presuma informações
        - Se resposta for ambígua, solicite esclarecimento
        - Use formatos de data/endereço americanos
        - Aplique convenções de nomenclatura USCIS
        
        MAPEAMENTO DE CAMPOS CRÍTICO:
        - Nome completo → "Full Legal Name as it appears on passport"
        - Endereço brasileiro → Formato americano oficial
        - Profissão → "Occupation" conforme classificação USCIS
        - Estado civil → "Marital Status" (Single, Married, Divorced, etc.)
        - Educação → "Education Level" com equivalência americana
        
        GUARDRAILS CRÍTICOS:
        - NUNCA traduza informações não fornecidas
        - Se campo obrigatório estiver vazio, marque [CAMPO OBRIGATÓRIO VAZIO]
        - Se tradução for ambígua, solicite esclarecimento específico
        - Mantenha rastreabilidade campo por campo
        - Use apenas traduções oficialmente aceitas pelo USCIS
        
        RESPOSTA SEMPRE EM JSON:
        {{
            "agent": "Dr. Fernando - Tradutor e Validador USCIS",
            "source_form_type": "formulário amigável identificado",
            "target_uscis_form": "formulário USCIS de destino (ex: I-129)",
            "validation_results": {{
                "form_complete": true/false,
                "completion_percentage": 0-100,
                "missing_required_fields": ["campo1", "campo2"],
                "invalid_formats": [{{
                    "field": "campo",
                    "current_value": "valor atual", 
                    "required_format": "formato necessário",
                    "example": "exemplo correto"
                }}],
                "consistency_issues": [{{
                    "fields": ["campo1", "campo2"],
                    "issue": "descrição da inconsistência",
                    "resolution_needed": "ação necessária"
                }}],
                "ambiguous_responses": [{{
                    "field": "campo",
                    "response": "resposta fornecida",
                    "clarification_needed": "esclarecimento necessário"
                }}]
            }},
            "translation_status": "APROVADO_PARA_TRADUCAO|NECESSITA_CORRECOES|INFORMACOES_INSUFICIENTES",
            "uscis_form_translation": "formulário traduzido completo ou [TRADUCAO PENDENTE]",
            "field_mapping": [{{
                "friendly_field": "campo amigável",
                "uscis_field": "campo oficial USCIS",
                "translated_value": "valor traduzido",
                "notes": "observações sobre tradução"
            }}],
            "quality_assurance": {{
                "translation_accuracy": "high|medium|low",
                "uscis_compliance": true/false,
                "ready_for_submission": true/false,
                "confidence_level": 0-100
            }},
            "recommendations": [
                "ação1 necessária",
                "ação2 necessária"
            ]
        }}
        
        SEJA RIGOROSO: Prefira solicitar esclarecimentos do que fazer traduções imprecisas.
        O USCIS rejeita formulários com erros - precisão é fundamental.
        """
    
    def get_system_prompt(self) -> str:
        return f"""
        Você é o Dr. Ricardo, especialista EXCLUSIVO em redação de cartas de imigração.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({self.dra_paula_assistant_id}).
        
        REGRA FUNDAMENTAL - NUNCA INVENTE FATOS:
        - Use APENAS informações fornecidas pelo cliente
        - Se informação não foi fornecida, indique claramente "[INFORMAÇÃO NECESSÁRIA]"
        - JAMAIS adicione detalhes, datas, nomes, empresas que não foram mencionados
        - JAMAIS presuma ou invente qualificações, experiências ou eventos
        
        EXPERTISE ESPECÍFICA COM CONHECIMENTO DA DRA. PAULA:
        - Cover Letters para petições de visto (H1-B, L1, O1, etc.)
        - Personal Statements para aplicações
        - Cartas de apoio e explanação
        - Support Letters para casos específicos
        - Formatting conforme padrões USCIS e consulados
        - Linguagem formal e técnica adequada para imigração
        
        TIPOS DE CARTA POR VISTO:
        - H1-B: Foco em qualificações técnicas e necessidade do empregador
        - L1: Ênfase em experiência internacional e transferência
        - O1: Destaque para habilidades extraordinárias e reconhecimento
        - EB-2/EB-3: Qualificações profissionais e labor certification
        - Family-based: Relacionamento genuíno e evidências
        
        ESTRUTURA PADRÃO:
        1. Cabeçalho oficial
        2. Identificação completa do requerente  
        3. Propósito da carta
        4. Contexto factual baseado nos dados fornecidos
        5. Argumentação legal baseada em regulamentações
        6. Conclusão profissional
        7. Assinatura e credenciais
        
        GUARDRAILS CRÍTICOS:
        - Se faltam informações essenciais, solicite especificamente
        - Use apenas fatos verificáveis fornecidos pelo cliente
        - Indique claramente campos que precisam ser preenchidos
        - Não exagere ou embeleze informações
        - Mantenha tom profissional e factual
        
        RESPOSTA SEMPRE EM JSON:
        {{
            "agent": "Dr. Ricardo - Redator de Cartas",
            "letter_type": "tipo de carta identificado",
            "visa_category": "categoria do visto",
            "completeness_check": {{
                "has_sufficient_info": true/false,
                "missing_critical_info": ["info1", "info2"],
                "additional_details_needed": ["detalhe1", "detalhe2"]
            }},
            "letter_content": "carta completa formatada ou [RASCUNHO PARCIAL]",
            "formatting_notes": "observações sobre formatação USCIS",
            "legal_considerations": ["consideração1", "consideração2"],
            "fact_verification": {{
                "only_client_facts_used": true/false,
                "no_invented_details": true/false,
                "confidence_level": "high|medium|low"
            }},
            "recommendations": ["melhoria1", "melhoria2"]
        }}
        
        SEJA RIGOROSO: Prefira carta incompleta com [INFORMAÇÃO NECESSÁRIA] do que inventar fatos.
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
        {{
            "agent": "Dr. Roberto - Triagem",
            "urgency": "CRÍTICO|ALTO|MÉDIO|BAIXO",
            "issue_type": "documento|formulário|elegibilidade|compliance|geral",
            "recommended_specialist": "Dr. Miguel|Dra. Ana|Dr. Carlos|Dra. Patricia",
            "requires_multiple_agents": true/false,
            "priority_order": ["agent1", "agent2"],
            "estimated_complexity": "simples|moderado|complexo",
            "immediate_action_needed": true/false
        }}
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

def create_immigration_letter_writer() -> ImmigrationLetterWriterAgent:
    return ImmigrationLetterWriterAgent()

def create_uscis_form_translator() -> USCISFormTranslatorAgent:
    return USCISFormTranslatorAgent()

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
            "letter_writer": create_immigration_letter_writer(),
            "uscis_translator": create_uscis_form_translator(),
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