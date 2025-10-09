"""
Sistema de Tutor Inteligente para Imigração
Fornece orientação personalizada e contextual aos usuários durante todo o processo de imigração
"""

import logging
from typing import Dict, List, Any, Optional
from enum import Enum
import openai
import os
from datetime import datetime, timezone
import uuid
import json

logger = logging.getLogger(__name__)

class TutorPersonality(str, Enum):
    """Personalidades disponíveis para o tutor"""
    FRIENDLY = "friendly"  # Amigável e encorajador
    PROFESSIONAL = "professional"  # Profissional e direto
    DETAILED = "detailed"  # Detalhista e explicativo
    SIMPLIFIED = "simplified"  # Simplificado para iniciantes

class TutorAction(str, Enum):
    """Ações que o tutor pode realizar"""
    DOCUMENT_GUIDANCE = "document_guidance"
    FORM_ASSISTANCE = "form_assistance"
    TIMELINE_ESTIMATION = "timeline_estimation"
    REQUIREMENT_CHECK = "requirement_check"
    NEXT_STEPS = "next_steps"
    TROUBLESHOOTING = "troubleshooting"
    DOCUMENT_CHECKLIST = "document_checklist"
    PROGRESS_ANALYSIS = "progress_analysis"
    COMMON_MISTAKES = "common_mistakes"
    INTERVIEW_PREP = "interview_prep"

class TutorMessage(BaseModel):
    """Mensagem do tutor personalizada"""
    id: str
    title: str
    message: str
    action_type: TutorAction
    personality: TutorPersonality
    
    # Contexto
    visa_type: str
    current_step: str
    user_level: str  # "beginner", "intermediate", "advanced"
    
    # Interatividade
    quick_actions: List[Dict[str, str]] = []  # Botões de ação rápida
    related_help: List[str] = []              # Tópicos relacionados
    next_steps: List[str] = []                # Próximos passos sugeridos
    
    # Metadata
    priority: int = 5                         # 1-10, 10 = mais importante
    show_duration: int = 10                   # Segundos para mostrar
    can_dismiss: bool = True
    requires_action: bool = False
    
    timestamp: datetime = datetime.now(timezone.utc)

class UserProgress(BaseModel):
    """Progresso do usuário no sistema"""
    user_id: str
    visa_type: str
    
    # Níveis de conhecimento (0-100)
    immigration_knowledge: int = 0
    documents_knowledge: int = 0
    forms_knowledge: int = 0
    process_knowledge: int = 0
    
    # Histórico
    completed_steps: List[str] = []
    common_mistakes: List[str] = []
    successful_actions: List[str] = []
    
    # Preferências de aprendizado
    preferred_personality: TutorPersonality = TutorPersonality.FRIENDLY
    detail_level: str = "medium"  # "low", "medium", "high"
    language_preference: str = "pt"
    
    # Estatísticas
    total_interactions: int = 0
    help_requests: int = 0
    errors_corrected: int = 0
    achievements_earned: int = 0
    
    last_active: datetime = datetime.now(timezone.utc)

class IntelligentTutorSystem:
    """Sistema de Tutor Inteligente com IA melhorado para usuários leigos"""
    
    def __init__(self, db):
        self.db = db
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        
    async def get_contextual_guidance(
        self, 
        user_id: str, 
        current_step: str, 
        visa_type: str,
        personality: TutorPersonality = TutorPersonality.FRIENDLY,
        action: TutorAction = TutorAction.NEXT_STEPS
    ) -> Dict[str, Any]:
        """
        Fornece orientação contextual baseada no estado atual do usuário
        """
        try:
            # Obter contexto do usuário
            user_context = await self._get_user_context(user_id, visa_type)
            
            # Criar prompt personalizado
            guidance_prompt = self._create_guidance_prompt(
                user_context, current_step, visa_type, personality, action
            )
            
            # Chamar OpenAI para gerar orientação
            response = await self._generate_ai_response(guidance_prompt)
            
            # Salvar interação para aprendizado
            await self._save_interaction(user_id, current_step, response, action)
            
            return {
                "guidance": response,
                "personality": personality,
                "action": action,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar orientação contextual: {str(e)}")
            return await self._get_fallback_guidance(current_step, visa_type)

    async def get_document_checklist(self, user_id: str, visa_type: str) -> Dict[str, Any]:
        """Gera checklist personalizado de documentos com base no progresso do usuário"""
        try:
            user_context = await self._get_user_context(user_id, visa_type)
            
            # Documentos já carregados pelo usuário
            uploaded_docs = [doc.get('document_type') for doc in user_context.get('documents', [])]
            
            prompt = f"""
            Crie um checklist de documentos personalizado para um brasileiro aplicando para visto {visa_type}.
            
            DOCUMENTOS JÁ CARREGADOS: {uploaded_docs}
            
            Responda em JSON com esta estrutura:
            {{
                "required_documents": [
                    {{
                        "document": "nome_do_documento",
                        "status": "uploaded|pending|optional",
                        "description": "descrição clara do documento",
                        "tips": ["dica prática 1", "dica prática 2"],
                        "where_to_get": "onde obter este documento",
                        "validity_period": "período de validade",
                        "priority": "high|medium|low"
                    }}
                ],
                "next_priority": "próximo documento mais importante a carregar",
                "completion_percentage": 85
            }}
            
            Seja específico sobre onde obter cada documento no Brasil e inclua dicas práticas.
            """
            
            response = await self._generate_ai_response(prompt)
            parsed_response = json.loads(response.strip().replace('```json', '').replace('```', ''))
            
            return {
                "checklist": parsed_response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar checklist de documentos: {str(e)}")
            return await self._get_fallback_checklist(visa_type)

    async def analyze_progress(self, user_id: str, visa_type: str) -> Dict[str, Any]:
        """Analisa o progresso do usuário e oferece insights personalizados"""
        try:
            user_context = await self._get_user_context(user_id, visa_type)
            
            # Calcular estatísticas de progresso
            docs_uploaded = len(user_context.get('documents', []))
            cases_active = len([case for case in user_context.get('cases', []) 
                             if case.get('status') in ['created', 'form_selected', 'basic_data', 'documents_uploaded']])
            
            prompt = f"""
            Analise o progresso deste usuário brasileiro no processo de visto {visa_type}:
            
            DADOS DO USUÁRIO:
            - Documentos carregados: {docs_uploaded}
            - Casos ativos: {cases_active}
            - País atual: {user_context.get('user_profile', {}).get('current_country', 'Brasil')}
            
            Forneça uma análise em JSON:
            {{
                "progress_percentage": 45,
                "current_phase": "Preparação de Documentos",
                "strengths": ["o que está indo bem"],
                "areas_for_improvement": ["o que precisa de atenção"],
                "estimated_time_to_completion": "2-3 semanas",
                "next_milestones": ["próximo marco importante"],
                "personalized_advice": "conselho específico para este usuário",
                "risk_factors": ["possíveis problemas a evitar"],
                "encouragement": "mensagem encorajadora personalizada"
            }}
            
            Seja realista mas encorajador, e específico para a situação atual.
            """
            
            response = await self._generate_ai_response(prompt)
            parsed_response = json.loads(response.strip().replace('```json', '').replace('```', ''))
            
            return {
                "analysis": parsed_response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar progresso: {str(e)}")
            return await self._get_fallback_progress_analysis(visa_type)

    async def get_common_mistakes_for_step(self, current_step: str, visa_type: str) -> Dict[str, Any]:
        """Identifica erros comuns específicos da etapa atual"""
        try:
            prompt = f"""
            Liste os erros mais comuns que brasileiros cometem na etapa "{current_step}" 
            do processo de visto {visa_type}.
            
            Responda em JSON:
            {{
                "step": "{current_step}",
                "common_mistakes": [
                    {{
                        "mistake": "descrição do erro",
                        "why_it_happens": "por que as pessoas cometem esse erro",
                        "how_to_avoid": "como evitar",
                        "consequence": "o que pode acontecer se cometer esse erro",
                        "severity": "high|medium|low"
                    }}
                ],
                "prevention_tips": ["dica geral de prevenção"],
                "success_strategies": ["estratégia para ter sucesso nesta etapa"]
            }}
            
            Foque em erros práticos e específicos que afetam brasileiros.
            """
            
            response = await self._generate_ai_response(prompt)
            parsed_response = json.loads(response.strip().replace('```json', '').replace('```', ''))
            
            return {
                "mistakes_analysis": parsed_response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar erros comuns: {str(e)}")
            return await self._get_fallback_mistakes_analysis(current_step, visa_type)

    async def get_interview_preparation(self, user_id: str, visa_type: str) -> Dict[str, Any]:
        """Preparação personalizada para entrevista consular"""
        try:
            user_context = await self._get_user_context(user_id, visa_type)
            
            prompt = f"""
            Crie um plano de preparação para entrevista consular de visto {visa_type} 
            para este brasileiro:
            
            PERFIL: {user_context.get('user_profile', {})}
            
            Responda em JSON:
            {{
                "preparation_plan": {{
                    "weeks_before": [
                        {{
                            "week": 4,
                            "tasks": ["tarefa específica"],
                            "focus": "área de foco principal"
                        }}
                    ],
                    "day_of_interview": {{
                        "what_to_bring": ["documento obrigatório"],
                        "what_to_wear": "orientação sobre vestimenta",
                        "arrival_time": "quando chegar",
                        "mindset_tips": ["dica psicológica"]
                    }}
                }},
                "practice_questions": [
                    {{
                        "question": "pergunta em inglês",
                        "portuguese_translation": "tradução em português",
                        "good_answer_example": "exemplo de boa resposta",
                        "what_not_to_say": ["o que evitar dizer"],
                        "difficulty": "easy|medium|hard"
                    }}
                ],
                "red_flags_to_avoid": ["comportamento que pode prejudicar"],
                "confidence_boosters": ["forma de aumentar confiança"]
            }}
            
            Seja específico para a realidade de brasileiros aplicando nos consulados americanos.
            """
            
            response = await self._generate_ai_response(prompt)
            parsed_response = json.loads(response.strip().replace('```json', '').replace('```', ''))
            
            return {
                "interview_prep": parsed_response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar preparação de entrevista: {str(e)}")
            return await self._get_fallback_interview_prep(visa_type)
    
    async def _get_user_context(self, user_id: str, visa_type: str) -> Dict[str, Any]:
        """Coleta contexto completo do usuário"""
        try:
            # Buscar dados do usuário
            user = await self.db.users.find_one({"id": user_id}) or {}
            
            # Buscar documentos do usuário
            documents = await self.db.documents.find(
                {"user_id": user_id}, 
                {"_id": 0, "content_base64": 0}
            ).to_list(100)
            
            # Buscar casos do usuário
            cases = await self.db.auto_cases.find(
                {"user_id": user_id}, 
                {"_id": 0}
            ).to_list(100)
            
            # Buscar interações anteriores
            previous_interactions = await self.db.tutor_interactions.find(
                {"user_id": user_id}, 
                {"_id": 0}
            ).sort("created_at", -1).limit(5).to_list(5)
            
            return {
                "user_profile": {
                    "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                    "country_of_birth": user.get('country_of_birth'),
                    "current_country": user.get('current_country')
                },
                "documents": documents,
                "cases": cases,
                "previous_interactions": previous_interactions,
                "visa_type": visa_type
            }
            
        except Exception as e:
            logger.error(f"Erro ao coletar contexto do usuário: {str(e)}")
            return {}
    
    def _create_guidance_prompt(
        self, 
        context: Dict[str, Any], 
        current_step: str, 
        visa_type: str, 
        personality: TutorPersonality,
        action: TutorAction
    ) -> str:
        """Cria prompt personalizado baseado no contexto"""
        
        personality_traits = {
            TutorPersonality.FRIENDLY: "Seja amigável, encorajador e use linguagem calorosa. Use emojis quando apropriado.",
            TutorPersonality.PROFESSIONAL: "Seja profissional, direto e conciso. Use linguagem formal.",
            TutorPersonality.DETAILED: "Forneça explicações detalhadas e passo-a-passo. Seja minucioso.",
            TutorPersonality.SIMPLIFIED: "Use linguagem simples e fácil de entender. Evite jargões técnicos."
        }
        
        action_instructions = {
            TutorAction.DOCUMENT_GUIDANCE: "Foque em orientações sobre documentos necessários, como prepará-los e organizá-los.",
            TutorAction.FORM_ASSISTANCE: "Ajude com preenchimento de formulários e campos específicos.",
            TutorAction.TIMELINE_ESTIMATION: "Forneça estimativas realistas de tempo para cada etapa do processo.",
            TutorAction.REQUIREMENT_CHECK: "Verifique se o usuário atende aos requisitos necessários.",
            TutorAction.NEXT_STEPS: "Indique claramente quais são os próximos passos a seguir.",
            TutorAction.TROUBLESHOOTING: "Ajude a resolver problemas ou dificuldades específicas.",
            TutorAction.DOCUMENT_CHECKLIST: "Forneça uma lista organizada de documentos com status.",
            TutorAction.PROGRESS_ANALYSIS: "Analise o progresso e forneça insights sobre melhorias.",
            TutorAction.COMMON_MISTAKES: "Identifique e previna erros comuns nesta etapa.",
            TutorAction.INTERVIEW_PREP: "Prepare o usuário para a entrevista consular."
        }
        
        return f"""
        Você é um tutor especialista em imigração americana, especialmente experiente em ajudar brasileiros.
        Você entende as dificuldades específicas, documentos brasileiros, e os consulados americanos no Brasil.
        
        PERSONALIDADE: {personality_traits[personality]}
        FOCO DA ORIENTAÇÃO: {action_instructions[action]}
        
        CONTEXTO DO USUÁRIO:
        - Nome: {context.get('user_profile', {}).get('name', 'Usuário')}
        - Tipo de visto: {visa_type}
        - Etapa atual: {current_step}
        - Documentos carregados: {len(context.get('documents', []))}
        - Casos ativos: {len(context.get('cases', []))}
        
        INSTRUÇÕES ESPECÍFICAS:
        1. Forneça orientação específica para a etapa atual ({current_step})
        2. Seja extremamente prático e acionável
        3. Mencione documentos brasileiros específicos e onde obtê-los
        4. Inclua prazos reais e custos aproximados quando relevante
        5. Antecipe problemas comuns que brasileiros enfrentam
        6. Sempre termine com próximos passos claros e priorizados
        7. Use linguagem que um leigo entenderia facilmente
        8. Seja encorajador mas realista sobre desafios
        
        Responda em português brasileiro de forma clara, útil e específica para brasileiros.
        """
    
    async def _generate_ai_response(self, prompt: str) -> str:
        """Gera resposta usando OpenAI"""
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um tutor especialista em imigração americana para brasileiros. Forneça orientações claras, práticas e específicas para a realidade brasileira."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta da IA: {str(e)}")
            raise e
    
    async def _save_interaction(self, user_id: str, current_step: str, response: str, action: TutorAction):
        """Salva interação para aprendizado futuro"""
        try:
            interaction = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "current_step": current_step,
                "action": action.value,
                "response": response,
                "created_at": datetime.now(timezone.utc)
            }
            
            await self.db.tutor_interactions.insert_one(interaction)
            
        except Exception as e:
            logger.error(f"Erro ao salvar interação: {str(e)}")
    
    async def _get_fallback_guidance(self, current_step: str, visa_type: str) -> Dict[str, Any]:
        """Orientação de fallback quando a IA não está disponível"""
        
        fallback_guidance = {
            "document_upload": f"📄 Nesta etapa, você precisa carregar os documentos necessários para o visto {visa_type}. Certifique-se de que todos os documentos estejam em boa qualidade, legíveis e dentro da validade. Escaneie em alta resolução (300 DPI) e em formato PDF.",
            "form_filling": f"📝 Agora é hora de preencher o formulário oficial para o visto {visa_type}. Tenha em mãos todos os seus documentos e responda todas as perguntas com precisão e honestidade. Não deixe campos em branco.",
            "review": f"🔍 Revise cuidadosamente todas as informações antes de finalizar. Verifique se todos os documentos estão corretos, completos e correspondem às informações do formulário.",
            "payment": f"💳 Chegou a hora do pagamento das taxas consulares. Acesse o site oficial do consulado americano, tenha seu cartão de crédito internacional em mãos e guarde o comprovante de pagamento.",
            "interview_prep": f"🗣️ Prepare-se para a entrevista consular. Revise suas respostas do formulário, pratique com perguntas comuns em inglês e separe todos os documentos originais.",
            "default": f"ℹ️ Continue seguindo as etapas do processo para o visto {visa_type}. Mantenha todos os documentos organizados e acompanhe os prazos. Em caso de dúvidas, consulte nossa documentação."
        }
        
        guidance = fallback_guidance.get(current_step, fallback_guidance["default"])
        
        return {
            "guidance": guidance,
            "personality": TutorPersonality.FRIENDLY,
            "action": TutorAction.NEXT_STEPS,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fallback": True
        }

    async def _get_fallback_checklist(self, visa_type: str) -> Dict[str, Any]:
        """Checklist básico quando IA não está disponível"""
        basic_docs = {
            "h1b": ["passport", "photos", "education_diploma", "employment_letter"],
            "f1": ["passport", "photos", "education_transcript", "bank_statement"],
            "b1b2": ["passport", "photos", "bank_statement", "employment_letter"]
        }
        
        docs = basic_docs.get(visa_type, ["passport", "photos"])
        
        return {
            "checklist": {
                "required_documents": [{"document": doc, "status": "pending"} for doc in docs],
                "completion_percentage": 0
            },
            "fallback": True
        }

    async def _get_fallback_progress_analysis(self, visa_type: str) -> Dict[str, Any]:
        """Análise básica de progresso quando IA não está disponível"""
        return {
            "analysis": {
                "progress_percentage": 25,
                "current_phase": "Início do Processo",
                "next_milestones": ["Carregar documentos", "Preencher formulários"],
                "encouragement": f"Você está no caminho certo para o visto {visa_type}!"
            },
            "fallback": True
        }

    async def _get_fallback_mistakes_analysis(self, current_step: str, visa_type: str) -> Dict[str, Any]:
        """Análise básica de erros quando IA não está disponível"""
        return {
            "mistakes_analysis": {
                "step": current_step,
                "common_mistakes": [
                    {"mistake": "Não verificar todos os documentos", "severity": "high"}
                ],
                "prevention_tips": ["Revisar tudo com cuidado"]
            },
            "fallback": True
        }

    async def _get_fallback_interview_prep(self, visa_type: str) -> Dict[str, Any]:
        """Preparação básica de entrevista quando IA não está disponível"""
        return {
            "interview_prep": {
                "day_of_interview": {
                    "what_to_bring": ["Passaporte", "Todos os documentos originais"],
                    "what_to_wear": "Roupa formal e conservadora",
                    "arrival_time": "Chegue 15 minutos antes"
                },
                "practice_questions": [
                    {
                        "question": "What is the purpose of your trip?",
                        "portuguese_translation": "Qual é o propósito da sua viagem?",
                        "difficulty": "easy"
                    }
                ]
            },
            "fallback": True
        }

    async def get_user_progress(self, user_id: str, visa_type: str) -> UserProgress:
        """Busca ou cria progresso do usuário"""
        try:
            progress_data = await self.db.user_progress.find_one({
                "user_id": user_id,
                "visa_type": visa_type
            })
            
            if progress_data:
                return UserProgress(**progress_data)
            else:
                # Criar novo progresso
                new_progress = UserProgress(user_id=user_id, visa_type=visa_type)
                await self.db.user_progress.insert_one(new_progress.dict())
                return new_progress
                
        except Exception as e:
            logger.error(f"Error getting user progress: {e}")
            return UserProgress(user_id=user_id, visa_type=visa_type)

    async def update_user_progress(self, progress: UserProgress):
        """Atualiza progresso do usuário"""
        try:
            await self.db.user_progress.update_one(
                {"user_id": progress.user_id, "visa_type": progress.visa_type},
                {"$set": progress.dict()},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error updating user progress: {e}")

    def assess_user_level(self, progress: UserProgress) -> str:
        """Avalia nível do usuário baseado no progresso"""
        avg_knowledge = (
            progress.immigration_knowledge + 
            progress.documents_knowledge + 
            progress.forms_knowledge + 
            progress.process_knowledge
        ) / 4
        
        if avg_knowledge < 30:
            return "beginner"
        elif avg_knowledge < 70:
            return "intermediate"
        else:
            return "advanced"

    def get_contextual_explanation(self, visa_type: str, document_type: str, user_level: str) -> Dict[str, Any]:
        """Gera explicação contextual baseada no nível do usuário"""
        
        knowledge = self.knowledge_base.get(visa_type, {})
        doc_info = knowledge.get("documents", {}).get(document_type, {})
        
        if not doc_info:
            return {
                "explanation": f"Este documento é importante para seu processo de {visa_type}.",
                "tips": ["Certifique-se de que está legível e atualizado"],
                "next_steps": ["Faça upload quando estiver pronto"]
            }
        
        explanation = doc_info.get("explanation", "")
        tips = doc_info.get("tips", [])
        
        # Personalizar baseado no nível
        if user_level == "beginner":
            tips = tips[:2]  # Menos informações para iniciantes
            explanation += " Se tiver dúvidas, posso explicar cada passo detalhadamente."
        elif user_level == "advanced":
            tips.extend(doc_info.get("validation_rules", []))  # Mais detalhes para avançados
        
        return {
            "explanation": explanation,
            "tips": tips,
            "common_errors": doc_info.get("common_errors", []),
            "requirements": doc_info.get("requirements", [])
        }

    def generate_smart_message(
        self, 
        context: Dict[str, Any], 
        progress: UserProgress,
        action_type: TutorAction
    ) -> TutorMessage:
        """Gera mensagem inteligente baseada no contexto e progresso"""
        
        user_level = self.assess_user_level(progress)
        templates = self.personality_templates[progress.preferred_personality]
        
        # Construir mensagem baseada no tipo de ação
        if action_type == TutorAction.EXPLAIN:
            return self._generate_explanation_message(context, progress, user_level, templates)
        elif action_type == TutorAction.GUIDE:
            return self._generate_guide_message(context, progress, user_level, templates)
        elif action_type == TutorAction.VALIDATE:
            return self._generate_validation_message(context, progress, user_level, templates)
        elif action_type == TutorAction.WARN:
            return self._generate_warning_message(context, progress, user_level, templates)
        elif action_type == TutorAction.CELEBRATE:
            return self._generate_celebration_message(context, progress, user_level, templates)
        else:
            return self._generate_default_message(context, progress, user_level, templates)

    def _generate_explanation_message(self, context: Dict, progress: UserProgress, user_level: str, templates: Dict) -> TutorMessage:
        """Gera mensagem explicativa"""
        
        document_type = context.get("document_type", "documento")
        visa_type = progress.visa_type
        
        explanation_data = self.get_contextual_explanation(visa_type, document_type, user_level)
        
        # Construir mensagem personalizada
        message = f"📋 **{document_type.title()}** para {visa_type}\n\n"
        message += explanation_data["explanation"] + "\n\n"
        
        if explanation_data["tips"]:
            message += "💡 **Dicas importantes:**\n"
            for tip in explanation_data["tips"][:3]:  # Máximo 3 dicas
                message += f"• {tip}\n"
        
        quick_actions = [
            {"label": "Entendi", "action": "acknowledge"},
            {"label": "Explicar mais", "action": f"explain_detail_{document_type}"},
            {"label": "Ver exemplo", "action": f"show_example_{document_type}"}
        ]
        
        next_steps = [
            f"Prepare seu {document_type}",
            "Verifique se atende os requisitos",
            "Faça o upload quando pronto"
        ]
        
        return TutorMessage(
            id=f"explain_{document_type}_{datetime.now().timestamp()}",
            title=f"Explicação: {document_type.title()}",
            message=message,
            action_type=TutorAction.EXPLAIN,
            personality=progress.preferred_personality,
            visa_type=visa_type,
            current_step=context.get("current_step", "documents"),
            user_level=user_level,
            quick_actions=quick_actions,
            next_steps=next_steps,
            priority=7
        )

    def _generate_guide_message(self, context: Dict, progress: UserProgress, user_level: str, templates: Dict) -> TutorMessage:
        """Gera mensagem de orientação passo-a-passo"""
        
        current_step = context.get("current_step", "unknown")
        visa_type = progress.visa_type
        
        # Guias específicos por etapa
        step_guides = {
            "documents": {
                "title": "Guia: Upload de Documentos",
                "steps": [
                    "1️⃣ Verifique a lista de documentos necessários",
                    "2️⃣ Escaneie em alta resolução (300 DPI mínimo)",
                    "3️⃣ Salve em formato PDF ou JPG",
                    "4️⃣ Confira se o texto está legível",
                    "5️⃣ Faça upload de cada documento"
                ]
            },
            "friendly_form": {
                "title": "Guia: Preenchimento do Formulário",
                "steps": [
                    "1️⃣ Tenha seus documentos à mão",
                    "2️⃣ Preencha seção por seção",
                    "3️⃣ Use as informações exatas dos documentos",
                    "4️⃣ Salve frequentemente",
                    "5️⃣ Revise antes de finalizar"
                ]
            }
        }
        
        guide_info = step_guides.get(current_step, {
            "title": "Guia Geral",
            "steps": ["Siga as instruções na tela", "Não hesite em pedir ajuda"]
        })
        
        message = f"🎯 **{guide_info['title']}**\n\n"
        message += "Vamos fazer isso passo a passo:\n\n"
        
        for step in guide_info["steps"]:
            message += f"{step}\n"
        
        if user_level == "beginner":
            message += "\n💭 **Dica para iniciantes:** Vá devagar e leia cada instrução com atenção."
        
        quick_actions = [
            {"label": "Começar", "action": f"start_{current_step}"},
            {"label": "Ver checklist", "action": f"checklist_{current_step}"},
            {"label": "Preciso de ajuda", "action": "request_help"}
        ]
        
        return TutorMessage(
            id=f"guide_{current_step}_{datetime.now().timestamp()}",
            title=guide_info["title"],
            message=message,
            action_type=TutorAction.GUIDE,
            personality=progress.preferred_personality,
            visa_type=visa_type,
            current_step=current_step,
            user_level=user_level,
            quick_actions=quick_actions,
            priority=8
        )

    def _generate_validation_message(self, context: Dict, progress: UserProgress, user_level: str, templates: Dict) -> TutorMessage:
        """Gera mensagem de validação de dados"""
        
        validation_results = context.get("validation_results", {})
        errors = validation_results.get("errors", [])
        warnings = validation_results.get("warnings", [])
        
        if not errors and not warnings:
            message = f"✅ **Validação Concluída**\n\n"
            message += templates["completion"] + "\n\n"
            message += "Todos os dados estão corretos e completos!"
            
            quick_actions = [
                {"label": "Continuar", "action": "proceed_next"},
                {"label": "Revisar dados", "action": "review_data"}
            ]
            priority = 6
        
        else:
            message = f"🔍 **Validação dos Dados**\n\n"
            
            if errors:
                message += "❌ **Problemas encontrados:**\n"
                for error in errors[:3]:  # Máximo 3 erros por vez
                    message += f"• {error}\n"
                message += "\n"
            
            if warnings:
                message += "⚠️ **Atenção:**\n"
                for warning in warnings[:2]:
                    message += f"• {warning}\n"
                message += "\n"
            
            message += "Vamos corrigir isso juntos!"
            
            quick_actions = [
                {"label": "Corrigir agora", "action": "fix_errors"},
                {"label": "Explicar erro", "action": "explain_errors"},
                {"label": "Pedir ajuda", "action": "request_support"}
            ]
            priority = 9
        
        return TutorMessage(
            id=f"validation_{datetime.now().timestamp()}",
            title="Validação de Dados",
            message=message,
            action_type=TutorAction.VALIDATE,
            personality=progress.preferred_personality,
            visa_type=progress.visa_type,
            current_step=context.get("current_step", "validation"),
            user_level=user_level,
            quick_actions=quick_actions,
            priority=priority,
            requires_action=bool(errors)
        )

    def _generate_warning_message(self, context: Dict, progress: UserProgress, user_level: str, templates: Dict) -> TutorMessage:
        """Gera mensagem de aviso/alerta"""
        
        warning_type = context.get("warning_type", "general")
        message_content = context.get("message", "Atenção necessária")
        
        warnings_library = {
            "passport_expiry": {
                "title": "⚠️ Passaporte Expirando",
                "message": "Seu passaporte expira em menos de 6 meses. Para vistos americanos, é recomendado ter pelo menos 6 meses de validade.",
                "actions": [
                    {"label": "Renovar passaporte", "action": "guide_passport_renewal"},
                    {"label": "Verificar requisitos", "action": "check_passport_requirements"},
                    {"label": "Continuar mesmo assim", "action": "continue_with_warning"}
                ]
            },
            "missing_documents": {
                "title": "📄 Documentos Faltando",
                "message": "Alguns documentos importantes ainda não foram enviados. Isso pode atrasar seu processo.",
                "actions": [
                    {"label": "Ver lista completa", "action": "show_missing_docs"},
                    {"label": "Continuar depois", "action": "save_and_continue"},
                    {"label": "Não tenho documento", "action": "help_obtain_doc"}
                ]
            }
        }
        
        warning_info = warnings_library.get(warning_type, {
            "title": "⚠️ Atenção",
            "message": message_content,
            "actions": [{"label": "Entendi", "action": "acknowledge_warning"}]
        })
        
        return TutorMessage(
            id=f"warning_{warning_type}_{datetime.now().timestamp()}",
            title=warning_info["title"],
            message=warning_info["message"],
            action_type=TutorAction.WARN,
            personality=progress.preferred_personality,
            visa_type=progress.visa_type,
            current_step=context.get("current_step", "warning"),
            user_level=user_level,
            quick_actions=warning_info["actions"],
            priority=8,
            can_dismiss=True,
            show_duration=15
        )

    def _generate_celebration_message(self, context: Dict, progress: UserProgress, user_level: str, templates: Dict) -> TutorMessage:
        """Gera mensagem de parabenização"""
        
        achievement = context.get("achievement", "step_completed")
        
        celebrations = {
            "step_completed": {
                "title": "🎉 Etapa Concluída!",
                "message": "Parabéns! Você completou mais uma etapa importante do seu processo de imigração.",
                "achievement_points": 10
            },
            "all_documents_uploaded": {
                "title": "📁 Todos os Documentos Enviados!",
                "message": "Excelente trabalho! Você enviou todos os documentos necessários. Seu processo está 60% completo!",
                "achievement_points": 25
            },
            "form_completed": {
                "title": "📋 Formulário Completado!",
                "message": "Fantástico! Você preencheu todo o formulário corretamente. Agora vamos para a revisão final.",
                "achievement_points": 30
            },
            "process_completed": {
                "title": "🏆 Processo Concluído!",
                "message": "PARABÉNS! Você completou todo o processo de aplicação. Agora é só aguardar o resultado!",
                "achievement_points": 100
            }
        }
        
        celebration = celebrations.get(achievement, celebrations["step_completed"])
        
        message = f"{celebration['message']}\n\n"
        message += f"🌟 +{celebration['achievement_points']} pontos de progresso!\n\n"
        
        if progress.total_interactions > 10:
            message += "Você está se tornando um expert em imigração! 🚀"
        
        quick_actions = [
            {"label": "Continuar", "action": "proceed_next"},
            {"label": "Ver progresso", "action": "show_progress"},
            {"label": "Compartilhar conquista", "action": "share_achievement"}
        ]
        
        return TutorMessage(
            id=f"celebration_{achievement}_{datetime.now().timestamp()}",
            title=celebration["title"],
            message=message,
            action_type=TutorAction.CELEBRATE,
            personality=progress.preferred_personality,
            visa_type=progress.visa_type,
            current_step=context.get("current_step", "celebration"),
            user_level=user_level,
            quick_actions=quick_actions,
            priority=5,
            show_duration=8
        )

    def _generate_default_message(self, context: Dict, progress: UserProgress, user_level: str, templates: Dict) -> TutorMessage:
        """Gera mensagem padrão"""
        
        return TutorMessage(
            id=f"default_{datetime.now().timestamp()}",
            title="Orientação",
            message="Estou aqui para ajudar você com seu processo de imigração. Como posso ajudar?",
            action_type=TutorAction.SUGGEST,
            personality=progress.preferred_personality,
            visa_type=progress.visa_type,
            current_step=context.get("current_step", "general"),
            user_level=user_level,
            quick_actions=[
                {"label": "Explicar processo", "action": "explain_process"},
                {"label": "Verificar documentos", "action": "check_documents"},
                {"label": "Ajuda geral", "action": "general_help"}
            ],
            priority=5
        )

    async def get_proactive_suggestions(self, user_id: str, visa_type: str, current_context: Dict) -> List[TutorMessage]:
        """Gera sugestões proativas baseadas no contexto atual"""
        
        progress = await self.get_user_progress(user_id, visa_type)
        suggestions = []
        
        current_step = current_context.get("current_step", "")
        
        # Sugestões baseadas no passo atual
        if current_step == "documents" and len(progress.completed_steps) == 0:
            # Primeiro acesso - oferecer tour
            suggestions.append(self.generate_smart_message(
                {"current_step": "onboarding", "is_first_time": True},
                progress,
                TutorAction.GUIDE
            ))
        
        elif current_step == "friendly_form":
            # Verificar se tem todos os documentos
            uploaded_docs = current_context.get("uploaded_documents", [])
            required_docs = current_context.get("required_documents", [])
            
            if len(uploaded_docs) < len(required_docs):
                suggestions.append(self.generate_smart_message(
                    {"warning_type": "missing_documents", "current_step": current_step},
                    progress,
                    TutorAction.WARN
                ))
        
        # Sugestões baseadas em erros comuns
        if "passport_validation_error" in progress.common_mistakes:
            suggestions.append(self.generate_smart_message(
                {"warning_type": "passport_expiry", "current_step": current_step},
                progress,
                TutorAction.WARN
            ))
        
        return suggestions[:2]  # Máximo 2 sugestões proativas

    async def record_interaction(self, user_id: str, message: TutorMessage, user_action: str):
        """Registra interação do usuário com o tutor"""
        try:
            interaction = {
                "user_id": user_id,
                "message_id": message.id,
                "action_type": message.action_type.value,
                "user_action": user_action,
                "timestamp": datetime.now(timezone.utc),
                "context": {
                    "visa_type": message.visa_type,
                    "current_step": message.current_step,
                    "user_level": message.user_level
                }
            }
            
            await self.collection.insert_one(interaction)
            
            # Atualizar progresso do usuário
            progress = await self.get_user_progress(user_id, message.visa_type)
            progress.total_interactions += 1
            
            if user_action == "request_help":
                progress.help_requests += 1
            elif user_action.startswith("fix_"):
                progress.errors_corrected += 1
            elif message.action_type == TutorAction.CELEBRATE:
                progress.achievements_earned += 1
                
            await self.update_user_progress(progress)
            
        except Exception as e:
            logger.error(f"Error recording interaction: {e}")

    async def get_learning_analytics(self, user_id: str, visa_type: str) -> Dict[str, Any]:
        """Gera analytics de aprendizado do usuário"""
        try:
            progress = await self.get_user_progress(user_id, visa_type)
            
            # Buscar interações recentes
            recent_interactions = await self.collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": datetime.now(timezone.utc).replace(day=datetime.now().day-7)}
            }).to_list(length=50)
            
            # Analisar padrões
            interaction_types = {}
            help_topics = {}
            
            for interaction in recent_interactions:
                action_type = interaction.get("action_type", "unknown")
                interaction_types[action_type] = interaction_types.get(action_type, 0) + 1
                
                user_action = interaction.get("user_action", "")
                if "help" in user_action:
                    help_topics[user_action] = help_topics.get(user_action, 0) + 1
            
            analytics = {
                "user_progress": progress.dict(),
                "learning_patterns": {
                    "most_used_interactions": interaction_types,
                    "common_help_requests": help_topics,
                    "completion_rate": len(progress.completed_steps) / max(len(progress.completed_steps) + len(progress.common_mistakes), 1)
                },
                "recommendations": []
            }
            
            # Gerar recomendações personalizadas
            if progress.help_requests > 10:
                analytics["recommendations"].append("Considere agendar uma consultoria com especialista")
            
            if progress.immigration_knowledge < 50:
                analytics["recommendations"].append("Recomendamos estudar mais sobre o processo de imigração")
                
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting learning analytics: {e}")
            return {}