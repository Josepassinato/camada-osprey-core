import base64
import logging
import os
from datetime import datetime, timezone

import resend
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from core.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "noreply@iaimmigration.com")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    logger.info(f"✅ Resend configured with sender: {SENDER_EMAIL}")
else:
    logger.warning("⚠️ RESEND_API_KEY not configured")


class SendPackageEmailRequest(BaseModel):
    """Request model for sending package via email."""

    user_email: EmailStr
    user_name: str
    package_filename: str
    application_type: str = "I-539"
    case_id: str


class RequestPackageEmailRequest(BaseModel):
    """Request model for user requesting package via email."""

    case_id: str
    user_email: EmailStr


@router.post("/email/send-package")
async def send_package_email(request: SendPackageEmailRequest):
    """
    Envia o pacote de aplicação por email usando Resend.com.
    """
    try:
        if not RESEND_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Email service not configured. Please contact support.",
            )

        pdf_filename = request.package_filename.replace(".zip", "_DETALHADO.pdf").replace(
            "_F1_COMPLETE_PACKAGE", "_PACOTE_COMPLETO"
        )
        file_path = f"/app/{pdf_filename}"

        if not os.path.exists(file_path):
            pdf_filename = request.package_filename.replace(".zip", ".pdf")
            file_path = f"/app/{pdf_filename}"

        if not os.path.exists(file_path):
            file_path = f"/app/{request.package_filename}"
            pdf_filename = request.package_filename

        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"Package file not found: {request.package_filename}",
            )

        with open(file_path, "rb") as f:
            file_content = f.read()

        file_base64 = base64.b64encode(file_content).decode("utf-8")

        backend_url = os.environ.get(
            "BACKEND_URL", "https://formfiller-26.preview.emergentagent.com"
        )
        download_link = f"{backend_url}/api/download/package/{pdf_filename}"

        html_content = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                    }}
                    .header {{
                        background-color: #2563eb;
                        color: white;
                        padding: 20px;
                        text-align: center;
                    }}
                    .content {{
                        padding: 30px 20px;
                        background-color: #f9fafb;
                    }}
                    .info-box {{
                        background-color: white;
                        border-left: 4px solid #2563eb;
                        padding: 15px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        background-color: #1f2937;
                        color: #9ca3af;
                        padding: 20px;
                        text-align: center;
                        font-size: 12px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 24px;
                        background-color: #2563eb;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Seu Pacote de Aplicação Está Pronto!</h1>
                </div>

                <div class="content">
                    <p>Olá <strong>{request.user_name}</strong>,</p>

                    <p>Seu pacote de aplicação para <strong>{request.application_type}</strong> foi gerado com sucesso e está anexado a este email.</p>

                    <div class="info-box">
                        <p><strong>📋 Informações do Seu Caso:</strong></p>
                        <p>
                            <strong>Case ID:</strong> {request.case_id}<br>
                            <strong>Tipo de Aplicação:</strong> {request.application_type}<br>
                            <strong>Nome do Arquivo:</strong> {request.package_filename}
                        </p>
                    </div>

                    <h3>📦 O que está incluído no pacote:</h3>
                    <ul>
                        <li>Informações completas do caso</li>
                        <li>Dados pessoais e do passaporte</li>
                        <li>Informações acadêmicas/profissionais</li>
                        <li>Documentos de suporte (passaporte, cartas, comprovantes)</li>
                        <li>Timeline do processo</li>
                        <li>Instruções para submissão ao USCIS</li>
                    </ul>

                    <h3>💾 Como Acessar o Pacote:</h3>
                    <div style="background-color: #e0f2fe; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>OPÇÃO 1:</strong> O arquivo PDF está anexado a este email. Basta abrir o anexo.</p>
                        <p><strong>OPÇÃO 2:</strong> Clique no botão abaixo para baixar direto do navegador:</p>
                        <div style="text-align: center;">
                            <a href="{download_link}" class="button" style="background-color: #10b981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">
                                📥 BAIXAR PACOTE COMPLETO
                            </a>
                        </div>
                        <p style="font-size: 12px; color: #666; margin-top: 10px;">O arquivo é um PDF único com todas as informações - fácil de abrir e imprimir!</p>
                    </div>

                    <h3>📝 Próximos Passos:</h3>
                    <ol>
                        <li>Abra o PDF anexado (ou baixe pelo link acima)</li>
                        <li>Revise todos os documentos cuidadosamente</li>
                        <li>Imprima as páginas necessárias em papel branco</li>
                        <li>Assine onde indicado</li>
                        <li>Envie ao USCIS conforme as instruções incluídas</li>
                    </ol>

                    <p><strong>⚠️ Aviso Importante:</strong><br>
                    Este pacote foi gerado automaticamente. Por favor, revise todas as informações para garantir precisão antes de submeter ao USCIS. Para questões complexas, recomendamos consultar um advogado de imigração.</p>

                    <p>Se você tiver alguma dúvida, por favor responda a este email ou entre em contato com nossa equipe de suporte.</p>

                    <p>Boa sorte com sua aplicação!</p>

                    <p>Atenciosamente,<br>
                    <strong>Equipe OSPREY Immigration</strong></p>
                </div>

                <div class="footer">
                    <p>OSPREY Immigration System<br>
                    Este é um email automático. Por favor não responda.</p>
                    <p>© 2025 IA Immigration. Todos os direitos reservados.</p>
                </div>
            </body>
        </html>
        """

        params: resend.Emails.SendParams = {
            "from": SENDER_EMAIL,
            "to": [request.user_email],
            "subject": f"✅ Seu Pacote de Aplicação {request.application_type} - Case ID: {request.case_id}",
            "html": html_content,
            "attachments": [{"content": file_base64, "filename": pdf_filename}],
        }

        logger.info(f"Enviando pacote por email para {request.user_email}")
        email_response = resend.Emails.send(params)

        logger.info(f"Email enviado com sucesso. Email ID: {email_response.get('id')}")

        return {
            "success": True,
            "email_id": email_response.get("id"),
            "message": f"Pacote enviado para {request.user_email}",
            "recipient": request.user_email,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao enviar email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar email: {str(e)}")


@router.post("/auto-application/case/{case_id}/send-email")
async def request_package_by_email(case_id: str, request: RequestPackageEmailRequest):
    """
    Endpoint para o USUÁRIO solicitar o envio do pacote por email.
    """
    try:
        if case_id != request.case_id:
            raise HTTPException(status_code=400, detail="Case ID não corresponde")

        case = await db.auto_application_cases.find_one({"case_id": case_id})

        if not case:
            raise HTTPException(status_code=404, detail="Caso não encontrado")

        if case.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail="O caso precisa estar completo para enviar por email. Complete todas as etapas primeiro.",
            )

        progress = case.get("progress_percentage", 0)
        if progress < 100:
            raise HTTPException(
                status_code=400,
                detail=f"O caso está {progress}% completo. Complete 100% antes de solicitar envio por email.",
            )

        await db.auto_application_cases.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "basic_data.email": request.user_email,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        user_name = case.get("basic_data", {}).get("full_name", "Usuário")
        application_type = case.get("form_code", "I-539")

        base_filename = user_name.replace(" ", "_")
        pdf_filenames = [
            f"{base_filename}_PACOTE_COMPLETO_DETALHADO.pdf",
            f"{base_filename}_I539_COMPLETE_PACKAGE.pdf",
            f"{base_filename}_I539_F1_COMPLETE_PACKAGE.zip",
        ]

        package_filename = None
        for filename in pdf_filenames:
            if os.path.exists(f"/app/{filename}"):
                package_filename = filename
                break

        if not package_filename:
            logger.info(f"Pacote não encontrado para {case_id}, tentando gerar...")
            raise HTTPException(
                status_code=404,
                detail="Pacote não encontrado. Por favor, entre em contato com o suporte.",
            )

        email_request = SendPackageEmailRequest(
            user_email=request.user_email,
            user_name=user_name,
            package_filename=package_filename,
            application_type=application_type,
            case_id=case_id,
        )

        result = await send_package_email(email_request)

        await db.auto_application_cases.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "email_sent": True,
                    "email_sent_at": datetime.now(timezone.utc),
                    "email_sent_to": request.user_email,
                }
            },
        )

        return {
            "success": True,
            "message": f"Pacote enviado com sucesso para {request.user_email}",
            "email_id": result.get("email_id"),
            "case_id": case_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao solicitar envio de pacote por email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
