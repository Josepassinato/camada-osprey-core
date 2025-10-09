"""
Notification System - Phase 4D  
Sistema de notificações automáticas para processos de imigração
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from motor.motor_asyncio import AsyncIOMotorDatabase
import aiohttp

logger = logging.getLogger(__name__)

class NotificationChannel(Enum):
    """Canais de notificação disponíveis"""
    EMAIL = "email"
    SMS = "sms"  
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    PUSH = "push"

class NotificationPriority(Enum):
    """Prioridades de notificação"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatus(Enum):
    """Status de entrega da notificação"""
    PENDING = "pending"
    SENT = "sent" 
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"

@dataclass
class NotificationTemplate:
    """Template para notificações"""
    template_id: str
    name: str
    subject_template: str
    body_template: str
    channel: NotificationChannel
    language: str = "pt"
    variables: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)

@dataclass
class NotificationRecipient:
    """Destinatário da notificação"""
    user_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    language: str = "pt"
    timezone: str = "America/Sao_Paulo"
    preferences: Dict[str, bool] = field(default_factory=dict)

@dataclass
class Notification:
    """Notificação individual"""
    notification_id: str
    template_id: str
    recipient: NotificationRecipient
    channel: NotificationChannel
    priority: NotificationPriority
    subject: str
    content: str
    variables: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)
    
    # Scheduling
    send_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Status tracking
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    attempts: int = 0
    error: Optional[str] = None
    
    # Context
    case_id: Optional[str] = None
    workflow_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class NotificationSystem:
    """
    Sistema de notificações automáticas
    """
    
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self.db = db
        self.templates: Dict[str, NotificationTemplate] = {}
        self.pending_notifications: Dict[str, Notification] = {}
        
        # Email configuration
        self.email_config = {
            "smtp_server": os.environ.get("SMTP_SERVER", "localhost"),
            "smtp_port": int(os.environ.get("SMTP_PORT", "587")),
            "smtp_username": os.environ.get("SMTP_USERNAME", ""),
            "smtp_password": os.environ.get("SMTP_PASSWORD", ""),
            "from_email": os.environ.get("FROM_EMAIL", "noreply@osprey.com"),
            "from_name": os.environ.get("FROM_NAME", "OSPREY Immigration")
        }
        
        # SMS configuration (placeholder for future integration)
        self.sms_config = {
            "provider": os.environ.get("SMS_PROVIDER", "twilio"),
            "api_key": os.environ.get("SMS_API_KEY", ""),
            "from_number": os.environ.get("SMS_FROM_NUMBER", "+1234567890")
        }
        
        # Webhook configuration
        self.webhook_config = {
            "timeout": 30,
            "retry_attempts": 3
        }
        
        # Register default templates
        self._register_default_templates()
        
        # Start background processor
        asyncio.create_task(self._process_notifications())
    
    def _register_default_templates(self):
        """
        Registra templates padrão para notificações
        """
        
        # Templates para processo H-1B
        self.templates["h1b_documents_validated"] = NotificationTemplate(
            template_id="h1b_documents_validated",
            name="H-1B: Documentos Validados",
            subject_template="✅ Seus documentos H-1B foram validados",
            body_template="""
Olá {user_name},

Ótimas notícias! Seus documentos para a petição H-1B foram validados com sucesso.

📊 **Resumo da Validação:**
- Documentos analisados: {documents_count}
- Score de qualidade: {quality_score}%
- Issues encontrados: {issues_count}

🎯 **Próximos Passos:**
Agora vamos prosseguir para o preenchimento dos formulários oficiais.

📞 **Precisa de ajuda?**
Nossa equipe está disponível 24/7 para auxiliar você.

Atenciosamente,
Equipe OSPREY Immigration

---
Caso: {case_id}
Data: {current_date}
            """,
            channel=NotificationChannel.EMAIL,
            variables=["user_name", "documents_count", "quality_score", "issues_count", "case_id", "current_date"]
        )
        
        self.templates["h1b_forms_completed"] = NotificationTemplate(
            template_id="h1b_forms_completed", 
            name="H-1B: Formulários Preenchidos",
            subject_template="📝 Formulários H-1B preenchidos - Revisar antes do envio",
            body_template="""
Olá {user_name},

Seus formulários H-1B foram preenchidos com base nos documentos enviados!

📋 **Formulários Preenchidos:**
- I-129 (Petition for Nonimmigrant Worker)
- H Classification Supplement  
- Completude: {completeness}%

🔍 **Ação Necessária:**
Por favor, revise todos os dados antes da submissão final.

👀 **Revisar Agora:** {review_link}

Atenciosamente,
Equipe OSPREY Immigration
            """,
            channel=NotificationChannel.EMAIL,
            variables=["user_name", "completeness", "review_link"]
        )
        
        self.templates["package_ready"] = NotificationTemplate(
            template_id="package_ready",
            name="Pacote Final Pronto",
            subject_template="🎉 Seu pacote de imigração está pronto para envio!",
            body_template="""
Parabéns {user_name}!

Seu pacote de imigração foi finalizado e está pronto para envio ao USCIS.

📦 **Detalhes do Pacote:**
- Tipo de visto: {visa_type}
- Total de páginas: {total_pages}
- Documentos incluídos: {documents_count}
- Score de qualidade: {quality_score}%

📮 **Instruções de Envio:**
{shipping_instructions}

💰 **Taxas do USCIS:**
Total: ${total_fees}

📧 **Downloads:**
- Pacote completo: {download_link}
- Instruções detalhadas: {instructions_link}

Boa sorte com sua petição!

Equipe OSPREY Immigration
            """,
            channel=NotificationChannel.EMAIL,
            variables=["user_name", "visa_type", "total_pages", "documents_count", "quality_score", 
                      "shipping_instructions", "total_fees", "download_link", "instructions_link"]
        )
        
        # Templates para F-1
        self.templates["f1_sevis_payment_reminder"] = NotificationTemplate(
            template_id="f1_sevis_payment_reminder",
            name="F-1: Lembrete Pagamento SEVIS",
            subject_template="⏰ Lembrete: Pagamento SEVIS necessário para visto F-1",
            body_template="""
Olá {user_name},

Este é um lembrete importante sobre seu processo de visto F-1.

💰 **Pagamento SEVIS Pendente:**
- Valor: $350 USD
- Prazo: Pelo menos 3 dias antes da entrevista
- Link: https://www.fmjfee.com/

⚠️ **Importante:**
O pagamento SEVIS é obrigatório antes da entrevista no consulado.

📞 **Precisa de ajuda?**
Nossa equipe pode orientar você através do processo.

Atenciosamente,
Equipe OSPREY Immigration
            """,
            channel=NotificationChannel.EMAIL,
            variables=["user_name"]
        )
        
        # Templates para I-485
        self.templates["i485_priority_date_current"] = NotificationTemplate(
            template_id="i485_priority_date_current",
            name="I-485: Priority Date Current",
            subject_template="🚨 Sua Priority Date está current - Ação imediata necessária!",
            body_template="""
URGENTE: {user_name}

Excelentes notícias! Sua priority date para I-485 está CURRENT no Visa Bulletin!

⚡ **Ação Imediata Necessária:**
- Janela para filing: Este mês
- Exame médico deve estar atualizado
- Todos os documentos devem estar prontos

📋 **Próximos Passos:**
1. Confirmar exame médico I-693 válido
2. Revisar formulário I-485 preenchido  
3. Preparar documentos de apoio
4. Submeter antes do fim do mês

🏃‍♂️ **Tempo é Crítico:**
Priority dates podem retroceder no próximo mês.

Entre em contato IMEDIATAMENTE: {contact_number}

Equipe OSPREY Immigration
            """,
            channel=NotificationChannel.EMAIL,
            variables=["user_name", "contact_number"]
        )
        
        # Templates para notificações de sistema
        self.templates["workflow_started"] = NotificationTemplate(
            template_id="workflow_started",
            name="Workflow Iniciado",
            subject_template="🚀 Processo automatizado iniciado - {workflow_name}",
            body_template="""
Olá {user_name},

Seu processo de imigração foi iniciado automaticamente!

🔄 **Detalhes do Processo:**
- Tipo: {workflow_name}
- Caso: {case_id}
- ID de Execução: {execution_id}
- Iniciado em: {current_date} às {current_time}

📋 **Próximos Passos:**
O sistema processará automaticamente:
1. Validação de documentos
2. Preenchimento de formulários  
3. Geração de carta de apresentação
4. Finalização do pacote

📱 **Acompanhe o Progresso:**
Você receberá atualizações a cada etapa concluída.

Atenciosamente,
Equipe OSPREY Immigration
            """,
            channel=NotificationChannel.EMAIL,
            variables=["user_name", "workflow_name", "case_id", "execution_id", "current_date", "current_time"]
        )
        
        self.templates["workflow_failed"] = NotificationTemplate(
            template_id="workflow_failed",
            name="Falha no Workflow",
            subject_template="⚠️ Problema detectado no seu processo - Suporte necessário",
            body_template="""
Olá {user_name},

Detectamos um problema no processamento do seu caso que requer atenção.

🔍 **Detalhes do Problema:**
- Workflow: {workflow_name}
- Erro: {error_message}
- Horário: {error_time}

🛠️ **Nossa Resposta:**
Nossa equipe técnica foi notificada e está trabalhando na resolução.

📞 **Suporte:**
Se desejar falar conosco: {support_contact}

Pedimos desculpas pelo inconveniente.

Equipe OSPREY Immigration
            """,
            channel=NotificationChannel.EMAIL,
            variables=["user_name", "workflow_name", "error_message", "error_time", "support_contact"]
        )
        
        # Templates SMS
        self.templates["urgent_sms"] = NotificationTemplate(
            template_id="urgent_sms",
            name="SMS Urgente",
            subject_template="",
            body_template="OSPREY: {message}. Caso: {case_id}. Mais detalhes no app.",
            channel=NotificationChannel.SMS,
            variables=["message", "case_id"]
        )
        
        # Templates Webhook
        self.templates["webhook_status_update"] = NotificationTemplate(
            template_id="webhook_status_update",
            name="Webhook Status Update",
            subject_template="",
            body_template=json.dumps({
                "event": "case_status_changed",
                "case_id": "{case_id}",
                "new_status": "{new_status}",
                "timestamp": "{timestamp}",
                "data": "{additional_data}"
            }),
            channel=NotificationChannel.WEBHOOK,
            variables=["case_id", "new_status", "timestamp", "additional_data"]
        )
    
    async def send_notification(self,
                              template_id: str,
                              recipient: NotificationRecipient,
                              variables: Dict[str, Any] = None,
                              priority: NotificationPriority = NotificationPriority.MEDIUM,
                              send_at: Optional[datetime] = None,
                              case_id: Optional[str] = None,
                              workflow_id: Optional[str] = None) -> str:
        """
        Envia notificação usando template
        """
        if template_id not in self.templates:
            raise ValueError(f"Template '{template_id}' não encontrado")
        
        template = self.templates[template_id]
        variables = variables or {}
        
        # Add default variables
        variables.update({
            "current_date": datetime.now().strftime("%d/%m/%Y"),
            "current_time": datetime.now().strftime("%H:%M"),
            "user_name": recipient.name,
            "user_email": recipient.email or "N/A"
        })
        
        # Render template
        subject = self._render_template(template.subject_template, variables)
        content = self._render_template(template.body_template, variables)
        
        # Create notification
        notification = Notification(
            notification_id=str(uuid.uuid4()),
            template_id=template_id,
            recipient=recipient,
            channel=template.channel,
            priority=priority,
            subject=subject,
            content=content,
            variables=variables,
            send_at=send_at,
            case_id=case_id,
            workflow_id=workflow_id
        )
        
        # Add to queue
        self.pending_notifications[notification.notification_id] = notification
        
        # Save to database if available
        if self.db is not None:
            await self._save_notification_to_db(notification)
        
        logger.info(f"📬 Queued notification {notification.notification_id} for {recipient.name}")
        
        return notification.notification_id
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Renderiza template com variáveis
        """
        try:
            return template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing variable in template: {e}")
            return template
    
    async def _process_notifications(self):
        """
        Processa fila de notificações em background
        """
        while True:
            try:
                # Process pending notifications
                notifications_to_send = [
                    n for n in self.pending_notifications.values()
                    if n.status == NotificationStatus.PENDING and 
                       (n.send_at is None or n.send_at <= datetime.now(timezone.utc))
                ]
                
                for notification in notifications_to_send:
                    await self._send_notification(notification)
                
                # Clean up old notifications
                cutoff_time = datetime.now(timezone.utc) - timedelta(days=7)
                old_notifications = [
                    nid for nid, n in self.pending_notifications.items()
                    if n.created_at < cutoff_time and n.status in [NotificationStatus.SENT, NotificationStatus.FAILED]
                ]
                
                for nid in old_notifications:
                    self.pending_notifications.pop(nid, None)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in notification processor: {e}")
                await asyncio.sleep(30)
    
    async def _send_notification(self, notification: Notification):
        """
        Envia notificação individual
        """
        notification.attempts += 1
        notification.status = NotificationStatus.PENDING
        
        try:
            if notification.channel == NotificationChannel.EMAIL:
                await self._send_email(notification)
            elif notification.channel == NotificationChannel.SMS:
                await self._send_sms(notification) 
            elif notification.channel == NotificationChannel.WEBHOOK:
                await self._send_webhook(notification)
            elif notification.channel == NotificationChannel.IN_APP:
                await self._send_in_app(notification)
            else:
                raise ValueError(f"Unsupported channel: {notification.channel}")
            
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now(timezone.utc)
            
            logger.info(f"✅ Sent {notification.channel.value} notification {notification.notification_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send notification {notification.notification_id}: {e}")
            notification.error = str(e)
            
            # Retry logic
            if notification.attempts < 3:
                notification.status = NotificationStatus.RETRY
                # Schedule retry with exponential backoff
                retry_delay = min(300, 30 * (2 ** (notification.attempts - 1)))  # Max 5 minutes
                notification.send_at = datetime.now(timezone.utc) + timedelta(seconds=retry_delay)
            else:
                notification.status = NotificationStatus.FAILED
        
        # Update in database
        if self.db is not None:
            await self._save_notification_to_db(notification)
    
    async def _send_email(self, notification: Notification):
        """
        Envia notificação por email
        """
        if not notification.recipient.email:
            raise ValueError("Recipient email not provided")
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.email_config['from_name']} <{self.email_config['from_email']}>"
            msg['To'] = notification.recipient.email
            msg['Subject'] = notification.subject
            
            # Add body
            msg.attach(MIMEText(notification.content, 'plain', 'utf-8'))
            
            # Add attachments if any
            for attachment_path in notification.attachments:
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)
            
            # Send via SMTP
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                if self.email_config['smtp_username']:
                    server.starttls()
                    server.login(self.email_config['smtp_username'], self.email_config['smtp_password'])
                
                server.send_message(msg)
                
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            raise
    
    async def _send_sms(self, notification: Notification):
        """
        Envia notificação por SMS (placeholder)
        """
        if not notification.recipient.phone:
            raise ValueError("Recipient phone not provided")
        
        # Placeholder - integrate with SMS provider (Twilio, etc.)
        logger.info(f"📱 SMS to {notification.recipient.phone}: {notification.content}")
        
        # Simulate sending
        await asyncio.sleep(1)
    
    async def _send_webhook(self, notification: Notification):
        """
        Envia notificação via webhook
        """
        webhook_url = notification.metadata.get("webhook_url")
        if not webhook_url:
            raise ValueError("Webhook URL not provided")
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'OSPREY-Notification-System/1.0',
            'X-Notification-ID': notification.notification_id
        }
        
        # Add authentication if provided
        auth_token = notification.metadata.get("auth_token")
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                data=notification.content,
                headers=headers,
                timeout=self.webhook_config['timeout']
            ) as response:
                if response.status >= 400:
                    raise Exception(f"Webhook failed with status {response.status}")
    
    async def _send_in_app(self, notification: Notification):
        """
        Envia notificação in-app
        """
        if self.db is None:
            raise ValueError("Database not available for in-app notifications")
        
        in_app_notification = {
            "notification_id": notification.notification_id,
            "user_id": notification.recipient.user_id,
            "title": notification.subject,
            "message": notification.content,
            "priority": notification.priority.value,
            "read": False,
            "created_at": notification.created_at,
            "case_id": notification.case_id,
            "workflow_id": notification.workflow_id,
            "metadata": notification.metadata
        }
        
        await self.db.in_app_notifications.insert_one(in_app_notification)
    
    async def _save_notification_to_db(self, notification: Notification):
        """
        Salva notificação no banco
        """
        try:
            notification_dict = {
                "notification_id": notification.notification_id,
                "template_id": notification.template_id,
                "recipient": {
                    "user_id": notification.recipient.user_id,
                    "name": notification.recipient.name,
                    "email": notification.recipient.email,
                    "phone": notification.recipient.phone
                },
                "channel": notification.channel.value,
                "priority": notification.priority.value,
                "subject": notification.subject,
                "content": notification.content,
                "status": notification.status.value,
                "created_at": notification.created_at,
                "sent_at": notification.sent_at,
                "delivered_at": notification.delivered_at,
                "attempts": notification.attempts,
                "error": notification.error,
                "case_id": notification.case_id,
                "workflow_id": notification.workflow_id,
                "metadata": notification.metadata
            }
            
            await self.db.notifications.replace_one(
                {"notification_id": notification.notification_id},
                notification_dict,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error saving notification to database: {e}")
    
    # ===========================================
    # PUBLIC METHODS
    # ===========================================
    
    def get_notification_status(self, notification_id: str) -> Optional[Notification]:
        """
        Obtém status de uma notificação
        """
        return self.pending_notifications.get(notification_id)
    
    def list_templates(self) -> List[NotificationTemplate]:
        """
        Lista templates disponíveis
        """
        return list(self.templates.values())
    
    async def send_workflow_notification(self, 
                                       workflow_name: str,
                                       event: str,
                                       recipient: NotificationRecipient,
                                       case_id: str,
                                       context: Dict[str, Any] = None):
        """
        Envia notificação baseada em evento de workflow
        """
        context = context or {}
        
        # Mapping de eventos para templates
        event_template_map = {
            "h1b_documents_validated": "h1b_documents_validated",
            "h1b_forms_completed": "h1b_forms_completed", 
            "package_ready": "package_ready",
            "workflow_failed": "workflow_failed",
            "f1_sevis_reminder": "f1_sevis_payment_reminder",
            "i485_priority_current": "i485_priority_date_current"
        }
        
        template_id = event_template_map.get(event)
        if not template_id:
            logger.warning(f"No template found for event: {event}")
            return None
        
        # Determine priority based on event
        priority = NotificationPriority.MEDIUM
        if "urgent" in event or "priority" in event:
            priority = NotificationPriority.URGENT
        elif "failed" in event or "error" in event:
            priority = NotificationPriority.HIGH
        
        return await self.send_notification(
            template_id=template_id,
            recipient=recipient,
            variables=context,
            priority=priority,
            case_id=case_id
        )
    
    async def send_bulk_notifications(self, 
                                    template_id: str,
                                    recipients: List[NotificationRecipient],
                                    variables: Dict[str, Any] = None) -> List[str]:
        """
        Envia notificações em massa
        """
        notification_ids = []
        
        for recipient in recipients:
            try:
                nid = await self.send_notification(
                    template_id=template_id,
                    recipient=recipient,
                    variables=variables
                )
                notification_ids.append(nid)
            except Exception as e:
                logger.error(f"Failed to send notification to {recipient.name}: {e}")
        
        return notification_ids
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do sistema de notificações
        """
        total = len(self.pending_notifications)
        by_status = {}
        by_channel = {}
        
        for notification in self.pending_notifications.values():
            status = notification.status.value
            channel = notification.channel.value
            
            by_status[status] = by_status.get(status, 0) + 1
            by_channel[channel] = by_channel.get(channel, 0) + 1
        
        return {
            "total_notifications": total,
            "by_status": by_status,
            "by_channel": by_channel,
            "templates_available": len(self.templates),
            "email_config_valid": bool(self.email_config.get("smtp_server")),
            "sms_config_valid": bool(self.sms_config.get("api_key"))
        }

# Instância global
notification_system: Optional[NotificationSystem] = None