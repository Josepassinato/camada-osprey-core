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

