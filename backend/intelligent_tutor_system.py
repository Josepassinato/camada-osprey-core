"""
Sistema de Tutor Inteligente para Usuários Leigos
Versão melhorada com foco em orientação prática e suporte personalizado
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from pydantic import BaseModel
import logging
import json

logger = logging.getLogger(__name__)

class TutorAction(str, Enum):
    """Ações disponíveis do tutor"""
    EXPLAIN = "explain"          # Explicar um conceito
    GUIDE = "guide"              # Guiar através de um processo
    VALIDATE = "validate"        # Validar informações do usuário
    SUGGEST = "suggest"          # Sugerir próximos passos
    WARN = "warn"               # Avisar sobre possíveis problemas
    CELEBRATE = "celebrate"     # Parabenizar conquistas
    CORRECT = "correct"         # Corrigir erros comuns

class TutorPersonality(str, Enum):
    """Personalidades do tutor"""
    FRIENDLY = "friendly"        # Amigável e encorajador
    PROFESSIONAL = "professional" # Profissional e direto
    MENTOR = "mentor"           # Como um mentor experiente
    PATIENT = "patient"         # Paciente com iniciantes

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
    """Sistema de Tutor Inteligente melhorado"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db.tutor_interactions
        
        # Base de conhecimento estruturada por visa
        self.knowledge_base = {
            "H-1B": {
                "documents": {
                    "passport": {
                        "explanation": "Seu passaporte é o documento mais importante. Deve ter pelo menos 6 meses de validade.",
                        "tips": [
                            "Verifique a data de expiração antes de começar o processo",
                            "Se expira em menos de 6 meses, renove antes de aplicar",
                            "Faça cópias coloridas de todas as páginas com carimbos"
                        ],
                        "common_errors": [
                            "Passaporte vencido ou próximo do vencimento",
                            "Foto borrada ou páginas danificadas",
                            "Nome no passaporte diferente de outros documentos"
                        ]
                    },
                    "diploma": {
                        "explanation": "Para H-1B, precisa de diploma de nível superior (bacharel ou mais alto) em área relacionada ao trabalho.",
                        "tips": [
                            "Diploma deve ser de universidade reconhecida",
                            "Se estudou no exterior, pode precisar de avaliação de credenciais",
                            "Área de estudo deve estar relacionada ao cargo H-1B"
                        ],
                        "validation_rules": [
                            "Verificar se é bacharel ou superior",
                            "Confirmar se área está relacionada ao cargo",
                            "Validar se universidade é reconhecida"
                        ]
                    }
                },
                "forms": {
                    "i129": {
                        "explanation": "Formulário I-129 é preenchido pelo seu empregador, não por você diretamente.",
                        "your_role": "Você fornece informações pessoais precisas para o empregador preencher",
                        "key_fields": [
                            "Informações pessoais (nome, endereço, etc.)",
                            "Histórico educacional",
                            "Experiência profissional",
                            "Detalhes do cargo nos EUA"
                        ]
                    }
                },
                "process": {
                    "timeline": "Processo H-1B demora 3-8 meses dependendo do premium processing",
                    "key_dates": [
                        "1° de abril: Abertura das inscrições",
                        "Primeiros 5 dias: Período de submissão",
                        "Maio-Outubro: Processamento",
                        "1° de outubro: Início do trabalho"
                    ]
                }
            },
            "B-1/B-2": {
                "documents": {
                    "financial_proof": {
                        "explanation": "Comprovante financeiro é crucial para mostrar que você pode se manter nos EUA sem trabalhar.",
                        "requirements": [
                            "Extratos bancários dos últimos 3 meses",
                            "Carta do empregador confirmando salário",
                            "Declaração de Imposto de Renda",
                            "Comprovante de outros investimentos"
                        ],
                        "minimum_amounts": {
                            "tourist_month": "USD 2,000-5,000 por mês de viagem",
                            "business": "Depende da duração e propósito"
                        }
                    },
                    "ties_to_brazil": {
                        "explanation": "Vínculos com o Brasil são essenciais para provar que você vai retornar.",
                        "strong_ties": [
                            "Emprego estável no Brasil",
                            "Família (cônjuge, filhos)",
                            "Propriedades (imóveis, investimentos)",
                            "Estudos em andamento",
                            "Negócios próprios"
                        ]
                    }
                }
            }
        }
        
        # Templates de mensagens por personalidade
        self.personality_templates = {
            TutorPersonality.FRIENDLY: {
                "greeting": "Olá! 😊 Estou aqui para ajudar você com seu processo de imigração.",
                "encouragement": "Você está indo muito bem! Continue assim! 🌟",
                "error": "Ops! Vamos corrigir isso juntos. Não se preocupe, é normal! 💪",
                "completion": "Parabéns! Você concluiu mais uma etapa! 🎉"
            },
            TutorPersonality.PROFESSIONAL: {
                "greeting": "Bem-vindo ao sistema de orientação para imigração.",
                "encouragement": "Progresso satisfatório. Continue seguindo as instruções.",
                "error": "Identificamos um erro. Por favor, revise as informações abaixo:",
                "completion": "Etapa concluída com sucesso. Prossiga para a próxima fase."
            },
            TutorPersonality.MENTOR: {
                "greeting": "Como seu mentor em imigração, vou guiá-lo por todo o processo.",
                "encouragement": "Excelente trabalho! Sua dedicação fará a diferença no resultado.",
                "error": "Vamos ver isso como uma oportunidade de aprendizado. Vou explicar o que precisa ser ajustado.",
                "completion": "Mais uma conquista importante! Você está se tornando um expert no processo."
            },
            TutorPersonality.PATIENT: {
                "greeting": "Não tenha pressa. Vamos fazer isso passo a passo, no seu ritmo.",
                "encouragement": "Cada pequeno progresso conta. Você está no caminho certo.",
                "error": "Tudo bem, vamos revisar isso com calma. Não há problema em errar.",
                "completion": "Perfeito! Vamos celebrar essa conquista antes de continuar."
            }
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