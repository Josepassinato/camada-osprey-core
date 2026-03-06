"""
Maria WhatsApp Integration usando Baileys
Integração não-oficial do WhatsApp para mensagens proativas
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import aiohttp

logger = logging.getLogger(__name__)

# Baileys é uma biblioteca JavaScript, vamos usar via API bridge
# Você precisará rodar um servidor Baileys separado


class MariaWhatsAppService:
    """
    Serviço de WhatsApp para Maria usando Baileys

    Setup necessário:
    1. Instalar servidor Baileys (Node.js)
    2. Configurar QR Code para autenticação
    3. Manter conexão ativa
    """

    def __init__(self, baileys_api_url: str = None):
        # URL do servidor Baileys (rode separadamente)
        self.baileys_url = baileys_api_url or os.environ.get(
            "BAILEYS_API_URL", "http://localhost:3001"
        )
        self.session = None

    async def send_message(
        self, phone_number: str, message: str, quoted_message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia mensagem do WhatsApp

        Args:
            phone_number: Número no formato internacional (5511999999999)
            message: Texto da mensagem
            quoted_message_id: ID da mensagem para responder (opcional)

        Returns:
            Dict com status e message_id
        """
        try:
            # Formatar número para WhatsApp
            whatsapp_number = f"{phone_number}@s.whatsapp.net"

            payload = {"to": whatsapp_number, "message": message}

            if quoted_message_id:
                payload["quoted"] = quoted_message_id

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.baileys_url}/send-message",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ WhatsApp enviado para {phone_number}")
                        return {
                            "success": True,
                            "message_id": result.get("messageId"),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    else:
                        error = await response.text()
                        logger.error(f"❌ Erro ao enviar WhatsApp: {error}")
                        return {"success": False, "error": error}

        except Exception as e:
            logger.error(f"❌ Erro na integração WhatsApp: {e}")
            return {"success": False, "error": str(e)}

    async def send_welcome_message(
        self, phone_number: str, user_name: str, visa_type: str
    ) -> Dict[str, Any]:
        """
        Envia mensagem de boas-vindas da Maria via WhatsApp
        (Mensagem Opção B - Expandida)
        """
        message = f"""Olá {user_name}! 👋 Eu sou a Maria, sua assistente pessoal da Osprey!

Vi que você iniciou sua aplicação de {visa_type} e estou aqui para te apoiar em cada etapa dessa jornada. 🌟

Pode contar comigo para:
✅ Tirar dúvidas sobre o processo
✅ Te motivar nos momentos difíceis
✅ Lembrar de prazos importantes

Sempre que precisar, é só me chamar! Como posso te ajudar hoje?"""

        return await self.send_message(phone_number, message)

    async def send_progress_update(
        self, phone_number: str, user_name: str, progress_percentage: int, next_step: str
    ) -> Dict[str, Any]:
        """
        Envia atualização de progresso motivacional
        """
        message = f"""Oi {user_name}! 🌟

Você está indo muito bem! Já completou {progress_percentage}% da sua aplicação! 🎉

Próximo passo: {next_step}

Lembre-se: cada documento enviado te aproxima do seu sonho! Continue assim! 💪

Precisa de ajuda com algo?"""

        return await self.send_message(phone_number, message)

    async def send_document_reminder(
        self, phone_number: str, user_name: str, document_name: str, days_until_expiry: int
    ) -> Dict[str, Any]:
        """
        Envia lembrete sobre documento que vai expirar
        """
        urgency = "⚠️" if days_until_expiry <= 7 else "🔔"

        message = f"""{urgency} Oi {user_name}!

Lembrete importante: Seu documento "{document_name}" vai expirar em {days_until_expiry} dias.

Vamos garantir que tudo esteja em dia? Me chama se precisar de ajuda para renovar! 😊"""

        return await self.send_message(phone_number, message)

    async def send_case_stuck_reminder(
        self, phone_number: str, user_name: str, days_inactive: int
    ) -> Dict[str, Any]:
        """
        Envia lembrete quando caso está parado há muito tempo
        """
        message = f"""Oi {user_name}! 👋

Reparei que sua aplicação está parada há {days_inactive} dias. Tudo bem por aí?

Às vezes a jornada pode parecer longa, mas estou aqui para te ajudar a retomar! 💪

Que tal continuarmos hoje? Posso te ajudar com o próximo passo! 🌟"""

        return await self.send_message(phone_number, message)

    async def send_celebration(
        self, phone_number: str, user_name: str, achievement: str
    ) -> Dict[str, Any]:
        """
        Celebra conquistas do usuário
        """
        message = f"""🎉🎉🎉 PARABÉNS {user_name.upper()}! 🎉🎉🎉

{achievement}

Você merece comemorar! Estou tão orgulhosa do seu progresso! 🌟

Continue assim que logo você alcançará seu objetivo! 💪✨"""

        return await self.send_message(phone_number, message)

    async def send_uscis_update_alert(
        self, phone_number: str, user_name: str, update_type: str, update_details: str
    ) -> Dict[str, Any]:
        """
        Alerta sobre mudanças no USCIS relevantes ao caso do usuário
        """
        message = f"""🔔 Oi {user_name}!

Novidade importante do USCIS sobre {update_type}:

{update_details}

Isso pode afetar sua aplicação. Quer que eu explique melhor? Estou aqui para ajudar! 😊"""

        return await self.send_message(phone_number, message)

    async def check_connection_status(self) -> Dict[str, Any]:
        """
        Verifica se o WhatsApp está conectado
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.baileys_url}/status", timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "connected": result.get("connected", False),
                            "phone": result.get("phone"),
                            "status": result.get("status"),
                        }
        except Exception as e:
            logger.error(f"❌ Erro ao verificar status WhatsApp: {e}")
            return {"connected": False, "error": str(e)}


# Singleton instance
maria_whatsapp = MariaWhatsAppService()
