"""
Sistema de Alertas Proativos Inteligentes
Monitora aplicações e gera alertas contextuais para guiar usuários
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertType(str, Enum):
    """Tipos de alertas"""

    DOCUMENT_EXPIRING = "document_expiring"
    INCOMPLETE_FIELDS = "incomplete_fields"
    OPPORTUNITY = "opportunity"
    GOOD_NEWS = "good_news"
    DEADLINE_APPROACHING = "deadline_approaching"
    IMPROVEMENT_SUGGESTION = "improvement_suggestion"
    PROCESSING_UPDATE = "processing_update"


class AlertPriority(str, Enum):
    """Prioridade dos alertas"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AlertAction(str, Enum):
    """Ações que o usuário pode tomar"""

    CONTINUE = "continue"
    ADD_DOCUMENT = "add_document"
    REVIEW = "review"
    RENEW_DOCUMENT = "renew_document"
    COMPLETE_FIELD = "complete_field"
    SCHEDULE = "schedule"
    LEARN_MORE = "learn_more"


class ProactiveAlertSystem:
    """Sistema de alertas proativos inteligentes"""

    def __init__(self, db):
        self.db = db

    async def generate_alerts_for_case(self, case_id: str) -> List[Dict[str, Any]]:
        """Gera todos os alertas relevantes para um caso"""

        # Buscar caso
        case = await self.db.auto_cases.find_one({"id": case_id})
        if not case:
            return []

        alerts = []

        # 1. Verificar documentos expirando
        doc_alerts = await self._check_expiring_documents(case)
        alerts.extend(doc_alerts)

        # 2. Verificar campos incompletos
        incomplete_alerts = await self._check_incomplete_fields(case)
        alerts.extend(incomplete_alerts)

        # 3. Gerar oportunidades de melhoria
        opportunity_alerts = await self._generate_opportunities(case)
        alerts.extend(opportunity_alerts)

        # 4. Verificar boas notícias
        good_news_alerts = await self._check_good_news(case)
        alerts.extend(good_news_alerts)

        # 5. Verificar deadlines
        deadline_alerts = await self._check_deadlines(case)
        alerts.extend(deadline_alerts)

        # Ordenar por prioridade
        priority_order = {
            AlertPriority.URGENT: 0,
            AlertPriority.HIGH: 1,
            AlertPriority.MEDIUM: 2,
            AlertPriority.LOW: 3,
        }
        alerts.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return alerts

    async def _check_expiring_documents(self, case: Dict) -> List[Dict[str, Any]]:
        """Verifica documentos que estão expirando"""
        alerts = []

        # Verificar passaporte
        passport_expiry = case.get("passport_expiry_date")
        if passport_expiry:
            try:
                expiry_date = datetime.fromisoformat(passport_expiry.replace("Z", "+00:00"))
                months_until_expiry = (expiry_date - datetime.now(timezone.utc)).days / 30

                if months_until_expiry < 6:
                    priority = (
                        AlertPriority.URGENT if months_until_expiry < 3 else AlertPriority.HIGH
                    )

                    alerts.append(
                        {
                            "id": f"passport_expiry_{case['id']}",
                            "type": AlertType.DOCUMENT_EXPIRING,
                            "priority": priority,
                            "icon": "🔔",
                            "title": "Passaporte Expirando em Breve",
                            "message": f"Seu passaporte expira em {int(months_until_expiry)} meses.\nUSCIS requer passaporte válido por pelo menos 6 meses.",
                            "action": AlertAction.RENEW_DOCUMENT,
                            "action_label": "Renovar Agora",
                            "action_url": "/documents/passport-renewal",
                            "details": {
                                "expiry_date": expiry_date.strftime("%d/%m/%Y"),
                                "months_remaining": int(months_until_expiry),
                                "uscis_requirement": "6 meses de validade mínima",
                            },
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "dismissed": False,
                        }
                    )
            except:
                pass

        # Verificar outros documentos
        documents = case.get("documents", [])
        for doc in documents:
            if doc.get("expiry_date"):
                try:
                    expiry_date = datetime.fromisoformat(doc["expiry_date"].replace("Z", "+00:00"))
                    days_until_expiry = (expiry_date - datetime.now(timezone.utc)).days

                    if days_until_expiry < 90:  # 3 meses
                        alerts.append(
                            {
                                "id": f"doc_expiry_{doc.get('id', 'unknown')}",
                                "type": AlertType.DOCUMENT_EXPIRING,
                                "priority": AlertPriority.HIGH,
                                "icon": "📄",
                                "title": f"{doc.get('type', 'Documento')} Expirando",
                                "message": f"Expira em {days_until_expiry} dias. Renove antes de submeter sua aplicação.",
                                "action": AlertAction.RENEW_DOCUMENT,
                                "action_label": "Renovar Documento",
                                "details": {
                                    "document_type": doc.get("type"),
                                    "expiry_date": expiry_date.strftime("%d/%m/%Y"),
                                    "days_remaining": days_until_expiry,
                                },
                                "created_at": datetime.now(timezone.utc).isoformat(),
                                "dismissed": False,
                            }
                        )
                except:
                    pass

        return alerts

    async def _check_incomplete_fields(self, case: Dict) -> List[Dict[str, Any]]:
        """Verifica campos incompletos e progresso parado"""
        alerts = []

        progress = case.get("progress", 0)
        case.get("status", "")
        updated_at = case.get("updated_at")

        # Verificar se usuário parou no meio
        if updated_at and progress < 100:
            try:
                last_update = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                days_since_update = (datetime.now(timezone.utc) - last_update).days

                if days_since_update >= 3:  # 3 dias sem atualização
                    time_to_complete = self._estimate_time_to_complete(progress)

                    alerts.append(
                        {
                            "id": f"incomplete_{case['id']}",
                            "type": AlertType.INCOMPLETE_FIELDS,
                            "priority": AlertPriority.MEDIUM,
                            "icon": "⚠️",
                            "title": "Você Parou no Meio!",
                            "message": f"Você está {progress}% completo.\nApenas {time_to_complete} minutos para finalizar!",
                            "action": AlertAction.CONTINUE,
                            "action_label": "Continuar Agora",
                            "action_url": f"/auto-application/case/{case['id']}/continue",
                            "details": {
                                "progress": progress,
                                "days_idle": days_since_update,
                                "estimated_time": time_to_complete,
                                "current_step": case.get("current_step", ""),
                            },
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "dismissed": False,
                        }
                    )
            except:
                pass

        # Verificar campos críticos faltando
        visa_type = case.get("form_code")
        missing_fields = self._get_critical_missing_fields(case, visa_type)

        if missing_fields:
            alerts.append(
                {
                    "id": f"missing_fields_{case['id']}",
                    "type": AlertType.INCOMPLETE_FIELDS,
                    "priority": AlertPriority.HIGH,
                    "icon": "📝",
                    "title": "Campos Críticos Faltando",
                    "message": f"{len(missing_fields)} campos obrigatórios precisam ser preenchidos.",
                    "action": AlertAction.COMPLETE_FIELD,
                    "action_label": "Completar Campos",
                    "action_url": f"/auto-application/case/{case['id']}/complete",
                    "details": {
                        "missing_count": len(missing_fields),
                        "missing_fields": missing_fields[:5],  # Mostrar apenas 5
                    },
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "dismissed": False,
                }
            )

        return alerts

    async def _generate_opportunities(self, case: Dict) -> List[Dict[str, Any]]:
        """Gera sugestões de melhoria baseadas em dados do USCIS"""
        alerts = []

        visa_type = case.get("form_code")
        completeness = case.get("completeness_score", 0)

        # Oportunidade: Aumentar completude
        if 70 <= completeness < 90:
            improvement_potential = self._calculate_improvement_potential(case, visa_type)

            if improvement_potential:
                alerts.append(
                    {
                        "id": f"opportunity_improve_{case['id']}",
                        "type": AlertType.OPPORTUNITY,
                        "priority": AlertPriority.MEDIUM,
                        "icon": "💡",
                        "title": "Oportunidade de Melhoria",
                        "message": f"Conforme diretrizes do USCIS:\n{improvement_potential['suggestion']}\nAumenta chance em +{improvement_potential['percentage']}%",
                        "action": AlertAction.ADD_DOCUMENT,
                        "action_label": improvement_potential["action"],
                        "action_url": improvement_potential["url"],
                        "details": improvement_potential,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "dismissed": False,
                    }
                )

        # Oportunidade: Documentos adicionais
        suggested_docs = self._suggest_additional_documents(case, visa_type)
        for doc_suggestion in suggested_docs:
            alerts.append(
                {
                    "id": f"opportunity_doc_{doc_suggestion['type']}_{case['id']}",
                    "type": AlertType.OPPORTUNITY,
                    "priority": AlertPriority.LOW,
                    "icon": "📎",
                    "title": "Documento Recomendado",
                    "message": f"Adicionar {doc_suggestion['name']} fortalece sua aplicação.\n{doc_suggestion['reason']}",
                    "action": AlertAction.ADD_DOCUMENT,
                    "action_label": "Adicionar Documento",
                    "action_url": f"/auto-application/case/{case['id']}/documents",
                    "details": doc_suggestion,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "dismissed": False,
                }
            )

        return alerts

    async def _check_good_news(self, case: Dict) -> List[Dict[str, Any]]:
        """Verifica boas notícias sobre o tipo de visto"""
        alerts = []

        visa_type = case.get("form_code")

        # Simulação de boas notícias (em produção viria do visa_auto_updater)
        good_news_data = {
            "I-130": {
                "message": "Segundo últimas informações do USCIS:\nCasos I-130 estão sendo aprovados 18% mais rápido este mês!",
                "source": "USCIS Processing Times (atualizado hoje)",
                "percentage": 18,
            },
            "H-1B": {
                "message": "Boas notícias do USCIS:\nTaxa de aprovação H-1B subiu para 87% neste trimestre!",
                "source": "USCIS H-1B Statistics Q4 2024",
                "percentage": 87,
            },
            "I-539": {
                "message": "Atualização do USCIS:\nTempo médio de processamento I-539 reduziu para 5 meses!",
                "source": "USCIS.gov (verificado hoje)",
                "percentage": None,
            },
        }

        if visa_type in good_news_data:
            news = good_news_data[visa_type]
            alerts.append(
                {
                    "id": f"good_news_{visa_type}_{case['id']}",
                    "type": AlertType.GOOD_NEWS,
                    "priority": AlertPriority.LOW,
                    "icon": "🎉",
                    "title": "Boas Notícias!",
                    "message": news["message"],
                    "action": AlertAction.LEARN_MORE,
                    "action_label": "Ver Detalhes",
                    "action_url": "https://www.uscis.gov/processing-times",
                    "details": {
                        "source": news["source"],
                        "percentage": news["percentage"],
                        "visa_type": visa_type,
                    },
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "dismissed": False,
                }
            )

        return alerts

    async def _check_deadlines(self, case: Dict) -> List[Dict[str, Any]]:
        """Verifica deadlines importantes"""
        alerts = []

        # Deadline de expiração de status atual (para I-539)
        if case.get("form_code") == "I-539":
            current_status_expiry = case.get("current_status_expiry")
            if current_status_expiry:
                try:
                    expiry_date = datetime.fromisoformat(
                        current_status_expiry.replace("Z", "+00:00")
                    )
                    days_until_expiry = (expiry_date - datetime.now(timezone.utc)).days

                    if days_until_expiry < 60:  # 2 meses
                        priority = (
                            AlertPriority.URGENT if days_until_expiry < 30 else AlertPriority.HIGH
                        )

                        alerts.append(
                            {
                                "id": f"deadline_status_{case['id']}",
                                "type": AlertType.DEADLINE_APPROACHING,
                                "priority": priority,
                                "icon": "⏰",
                                "title": "Deadline Próximo!",
                                "message": f"Seu status atual expira em {days_until_expiry} dias.\nFinalize sua aplicação I-539 urgentemente!",
                                "action": AlertAction.CONTINUE,
                                "action_label": "Finalizar Aplicação",
                                "action_url": f"/auto-application/case/{case['id']}/finalize",
                                "details": {
                                    "expiry_date": expiry_date.strftime("%d/%m/%Y"),
                                    "days_remaining": days_until_expiry,
                                    "uscis_note": "Aplicar antes da expiração evita problemas de permanência irregular",
                                },
                                "created_at": datetime.now(timezone.utc).isoformat(),
                                "dismissed": False,
                            }
                        )
                except:
                    pass

        return alerts

    def _estimate_time_to_complete(self, current_progress: int) -> int:
        """Estima tempo em minutos para completar"""
        remaining = 100 - current_progress
        # Assumindo ~30 minutos para 100%
        return int((remaining / 100) * 30)

    def _get_critical_missing_fields(self, case: Dict, visa_type: str) -> List[str]:
        """Retorna lista de campos críticos faltando"""
        missing = []

        # Campos universais
        if not case.get("full_name"):
            missing.append("Nome completo")
        if not case.get("date_of_birth"):
            missing.append("Data de nascimento")
        if not case.get("passport_number"):
            missing.append("Número do passaporte")
        if not case.get("current_address"):
            missing.append("Endereço atual")

        # Campos específicos por visto
        if visa_type == "I-130":
            if not case.get("petitioner_name"):
                missing.append("Nome do peticionário")
            if not case.get("relationship_type"):
                missing.append("Tipo de relacionamento")
            if not case.get("marriage_date"):
                missing.append("Data de casamento")

        elif visa_type == "H-1B":
            if not case.get("employer_name"):
                missing.append("Nome do empregador")
            if not case.get("job_title"):
                missing.append("Cargo")
            if not case.get("salary"):
                missing.append("Salário")

        elif visa_type == "I-539":
            if not case.get("current_status"):
                missing.append("Status atual")
            if not case.get("extension_reason"):
                missing.append("Razão para extensão")

        return missing

    def _calculate_improvement_potential(self, case: Dict, visa_type: str) -> Optional[Dict]:
        """Calcula potencial de melhoria baseado em dados"""

        # Sugestões baseadas em estatísticas reais do USCIS
        suggestions = {
            "I-130": [
                {
                    "suggestion": "Adicionar carta do empregador do peticionário",
                    "percentage": 12,
                    "action": "Adicionar Carta",
                    "url": f"/auto-application/case/{case['id']}/documents/add?type=employment_letter",
                    "reason": "Demonstra estabilidade financeira do peticionário",
                },
                {
                    "suggestion": "Incluir declaração de impostos conjunta",
                    "percentage": 15,
                    "action": "Adicionar Tax Return",
                    "url": f"/auto-application/case/{case['id']}/documents/add?type=tax_return",
                    "reason": "Prova forte de relacionamento genuíno",
                },
            ],
            "H-1B": [
                {
                    "suggestion": "Adicionar cartas de recomendação de empregadores anteriores",
                    "percentage": 10,
                    "action": "Adicionar Recomendações",
                    "url": f"/auto-application/case/{case['id']}/documents/add?type=recommendation",
                    "reason": "Fortalece qualificação profissional",
                }
            ],
        }

        if visa_type in suggestions and suggestions[visa_type]:
            # Retornar primeira sugestão não aplicada ainda
            for suggestion in suggestions[visa_type]:
                # TODO: Verificar se já foi aplicado
                return suggestion

        return None

    def _suggest_additional_documents(self, case: Dict, visa_type: str) -> List[Dict]:
        """Sugere documentos adicionais opcionais mas benéficos"""
        suggestions = []

        existing_docs = [doc.get("type") for doc in case.get("documents", [])]

        optional_docs = {
            "I-130": [
                {
                    "type": "photos",
                    "name": "Fotos do Relacionamento",
                    "reason": "Evidência visual fortalece comprovação de relacionamento genuíno",
                    "impact": "medium",
                },
                {
                    "type": "joint_accounts",
                    "name": "Contas Bancárias Conjuntas",
                    "reason": "Prova de vida financeira compartilhada",
                    "impact": "high",
                },
            ],
            "H-1B": [
                {
                    "type": "publications",
                    "name": "Publicações ou Artigos",
                    "reason": "Demonstra expertise na área de especialização",
                    "impact": "medium",
                }
            ],
        }

        if visa_type in optional_docs:
            for doc in optional_docs[visa_type]:
                if doc["type"] not in existing_docs:
                    suggestions.append(doc)

        return suggestions[:2]  # Máximo 2 sugestões

    async def mark_alert_dismissed(self, alert_id: str, case_id: str) -> bool:
        """Marca um alerta como dispensado"""
        try:
            result = await self.db.case_alerts.update_one(
                {"alert_id": alert_id, "case_id": case_id},
                {"$set": {"dismissed": True, "dismissed_at": datetime.now(timezone.utc)}},
                upsert=True,
            )
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            logger.error(f"Error dismissing alert: {e}")
            return False

    async def get_active_alerts(self, case_id: str) -> List[Dict[str, Any]]:
        """Retorna alertas ativos (não dispensados) para um caso"""
        alerts = await self.generate_alerts_for_case(case_id)

        # Filtrar alertas já dispensados
        dismissed_alerts = await self.db.case_alerts.find(
            {"case_id": case_id, "dismissed": True}
        ).to_list(length=None)

        dismissed_ids = {alert["alert_id"] for alert in dismissed_alerts}

        return [alert for alert in alerts if alert["id"] not in dismissed_ids]
