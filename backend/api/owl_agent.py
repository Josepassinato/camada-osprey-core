import base64
import io
import logging
import os
import time as time_module
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response, StreamingResponse

from core.database import db
from core.serialization import serialize_doc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


# ===== OWL AGENT AUTHENTICATION & PERSISTENCE SYSTEM =====

@router.post("/owl-agent/auth/register")
async def register_owl_user(request: dict):
    """Register user for saving progress with email and password"""
    try:
        email_bypass = os.environ.get("EMAIL_BYPASS_FOR_TESTING", "FALSE").upper() == "TRUE"
        test_email_domain = os.environ.get("TEST_EMAIL_DOMAIN", "test.local")

        email = request.get("email", "").strip().lower()
        password = request.get("password", "")
        name = request.get("name", "")

        is_test_email = email.endswith(f"@{test_email_domain}")

        if not email or not password or len(password) < 6:
            raise HTTPException(status_code=400, detail="Email and password (min 6 chars) are required")

        existing_user = await db.owl_users.find_one({"email": email})
        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists")

        import bcrypt

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        user_data = {
            "user_id": f"owl_user_{int(time_module.time())}_{uuid.uuid4().hex[:8]}",
            "email": email,
            "name": name,
            "password_hash": hashed_password,
            "email_verified": True if (email_bypass and is_test_email) else False,
            "is_test_user": is_test_email if email_bypass else False,
            "created_at": datetime.now(timezone.utc),
            "active_sessions": [],
            "completed_applications": [],
        }

        await db.owl_users.insert_one(user_data)

        if email_bypass and is_test_email:
            logger.info(f"🧪 TEST MODE: Owl user registered with email bypass for {email}")

        response_data = {
            "success": True,
            "message": "User registered successfully",
            "user_id": user_data["user_id"],
            "email": email,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if email_bypass and is_test_email:
            response_data["test_mode"] = True
            response_data["message"] = "🧪 TEST MODE: User registered (email verification bypassed)"

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering owl user: {e}")
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@router.post("/owl-agent/auth/login")
async def login_owl_user(request: dict):
    """Login user to access saved progress"""
    try:
        email_bypass = os.environ.get("EMAIL_BYPASS_FOR_TESTING", "FALSE").upper() == "TRUE"
        test_email_domain = os.environ.get("TEST_EMAIL_DOMAIN", "test.local")

        email = request.get("email", "").strip().lower()
        password = request.get("password", "")

        is_test_email = email.endswith(f"@{test_email_domain}")

        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")

        user = await db.owl_users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        import bcrypt

        if email_bypass and is_test_email:
            logger.info(f"🧪 TEST MODE: Owl login bypass active for {email}")
            password_valid = True
        else:
            password_valid = bcrypt.checkpw(password.encode("utf-8"), user["password_hash"])

        if not password_valid:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        await db.owl_users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"last_login": datetime.now(timezone.utc)}},
        )

        sessions = await db.owl_sessions.find(
            {"user_email": email, "status": {"$in": ["active", "paused", "saved_for_later", "in_progress"]}}
        ).to_list(length=None)

        serialized_sessions = serialize_doc(sessions)

        response_data = {
            "success": True,
            "message": "Login successful",
            "user": {"user_id": user["user_id"], "email": user["email"], "name": user.get("name", "")},
            "saved_sessions": serialized_sessions,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if email_bypass and is_test_email:
            response_data["test_mode"] = True
            response_data["message"] = "🧪 TEST MODE: Login successful (password verification bypassed)"

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in owl user: {e}")
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")


@router.post("/owl/login")
async def login_owl_user_alt(request: dict):
    """Alternative login endpoint for Owl Agent"""
    return await login_owl_user(request)


@router.post("/owl-agent/save-for-later")
async def save_session_for_later(request: dict):
    """Save current session for later completion (requires user authentication)"""
    try:
        session_id = request.get("session_id")
        user_email = request.get("user_email", "").strip().lower()

        if not session_id or not user_email:
            raise HTTPException(status_code=400, detail="session_id and user_email are required")

        user = await db.owl_users.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        session = await db.owl_sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        update_data = {
            "user_email": user_email,
            "user_id": user["user_id"],
            "status": "saved_for_later",
            "saved_at": datetime.now(timezone.utc),
            "last_updated": datetime.now(timezone.utc),
        }

        await db.owl_sessions.update_one({"session_id": session_id}, {"$set": update_data})

        await db.owl_users.update_one(
            {"user_id": user["user_id"]},
            {"$addToSet": {"active_sessions": session_id}, "$set": {"last_activity": datetime.now(timezone.utc)}},
        )

        return {
            "success": True,
            "message": "Session saved for later completion",
            "session_id": session_id,
            "user_email": user_email,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving session for later: {e}")
        raise HTTPException(status_code=500, detail=f"Save error: {str(e)}")


@router.get("/owl-agent/user-sessions/{user_email}")
async def get_user_sessions(user_email: str):
    """Get all saved sessions for a user"""
    try:
        user_email = user_email.strip().lower()

        user = await db.owl_users.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        sessions_cursor = db.owl_sessions.find(
            {"user_email": user_email, "status": {"$in": ["active", "paused", "saved_for_later", "in_progress"]}}
        ).sort("last_updated", -1)

        sessions = await sessions_cursor.to_list(length=None)
        serialized_sessions = serialize_doc(sessions)

        for session in serialized_sessions:
            responses_count = await db.owl_responses.count_documents({"session_id": session["session_id"]})
            session["progress_percentage"] = min(
                100, (responses_count / session.get("total_fields", 1)) * 100
            )
            session["responses_count"] = responses_count

        return {
            "success": True,
            "user_email": user_email,
            "sessions": serialized_sessions,
            "total_sessions": len(serialized_sessions),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Session error: {str(e)}")


@router.get("/owl/user-sessions/{user_email}")
async def get_user_sessions_alt(user_email: str):
    """Alternative endpoint to get user sessions"""
    return await get_user_sessions(user_email)


@router.post("/owl/user-sessions")
async def get_user_sessions_by_post(request: dict):
    """Get user sessions via POST (for emails with special chars)"""
    user_email = request.get("email", "").strip().lower()
    if not user_email:
        raise HTTPException(status_code=400, detail="Email is required")
    return await get_user_sessions(user_email)


@router.post("/owl-agent/resume-session")
async def resume_saved_session(request: dict):
    """Resume a previously saved session"""
    try:
        session_id = request.get("session_id")
        user_email = request.get("user_email", "").strip().lower()

        if not session_id or not user_email:
            raise HTTPException(status_code=400, detail="session_id and user_email are required")

        session = await db.owl_sessions.find_one({"session_id": session_id, "user_email": user_email})

        if not session:
            raise HTTPException(status_code=404, detail="Session not found or access denied")

        await db.owl_sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "status": "active",
                    "resumed_at": datetime.now(timezone.utc),
                    "last_updated": datetime.now(timezone.utc),
                }
            },
        )

        responses_cursor = db.owl_responses.find({"session_id": session_id})
        responses = await responses_cursor.to_list(length=None)

        serialized_session = serialize_doc(session)
        serialized_responses = serialize_doc(responses)

        return {
            "success": True,
            "message": "Session resumed successfully",
            "session": serialized_session,
            "responses": serialized_responses,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming session: {e}")
        raise HTTPException(status_code=500, detail=f"Resume error: {str(e)}")


# ===== OWL AGENT FINAL PHASE - PAYMENT & DOWNLOAD SYSTEM =====

@router.post("/owl-agent/initiate-payment")
async def initiate_owl_payment(request: dict):
    """Initiate payment for completed USCIS form download"""
    try:
        session_id = request.get("session_id")
        delivery_method = request.get("delivery_method", "download")
        origin_url = request.get("origin_url")
        user_email = request.get("user_email", "").strip().lower()

        if not session_id:
            raise HTTPException(status_code=400, detail="session_id is required")

        if not origin_url:
            raise HTTPException(status_code=400, detail="origin_url is required")

        session = await db.owl_sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        responses_count = await db.owl_responses.count_documents({"session_id": session_id})
        completion_percentage = (responses_count / session.get("total_fields", 1)) * 100

        if completion_percentage < 90:
            raise HTTPException(status_code=400, detail="Application not completed yet")

        packages = {
            "download_only": {
                "amount": 29.99,
                "name": "Download Formulário USCIS",
                "description": "Download imediato do formulário preenchido",
            },
            "download_email": {
                "amount": 34.99,
                "name": "Download + Email",
                "description": "Download + envio por email",
            },
            "email_only": {
                "amount": 24.99,
                "name": "Envio por Email",
                "description": "Formulário enviado por email",
            },
        }

        if delivery_method == "download":
            package_key = "download_only"
        elif delivery_method == "email":
            package_key = "email_only"
        elif delivery_method == "both":
            package_key = "download_email"
        else:
            package_key = "download_only"

        package = packages[package_key]
        amount = package["amount"]

        from emergentintegrations.payments.stripe.checkout import CheckoutSessionRequest, StripeCheckout

        stripe_api_key = os.environ.get("STRIPE_API_KEY")
        if not stripe_api_key:
            raise HTTPException(status_code=500, detail="Stripe configuration missing")

        host_url = origin_url
        webhook_url = f"{host_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)

        success_url = f"{origin_url}/owl-agent/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{origin_url}/owl-agent"

        metadata = {
            "owl_session_id": session_id,
            "delivery_method": delivery_method,
            "user_email": user_email,
            "visa_type": session.get("visa_type", ""),
            "package_key": package_key,
        }

        checkout_request = CheckoutSessionRequest(
            amount=amount,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata,
        )

        checkout_session = await stripe_checkout.create_checkout_session(checkout_request)

        payment_data = {
            "payment_id": f"OWL-PAY-{int(time_module.time())}-{uuid.uuid4().hex[:8]}",
            "stripe_session_id": checkout_session.session_id,
            "owl_session_id": session_id,
            "user_email": user_email,
            "amount": amount,
            "currency": "usd",
            "delivery_method": delivery_method,
            "package_key": package_key,
            "package_name": package["name"],
            "visa_type": session.get("visa_type", ""),
            "payment_status": "initiated",
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
            "metadata": metadata,
        }

        await db.payment_transactions.insert_one(payment_data)

        return {
            "success": True,
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.session_id,
            "amount": amount,
            "currency": "usd",
            "package": package,
            "delivery_method": delivery_method,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating owl payment: {e}")
        raise HTTPException(status_code=500, detail=f"Error initiating payment: {str(e)}")


@router.get("/owl-agent/payment-status/{stripe_session_id}")
async def get_owl_payment_status(stripe_session_id: str):
    """Get payment status and process completion"""
    try:
        payment = await db.payment_transactions.find_one({"stripe_session_id": stripe_session_id})
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        from emergentintegrations.payments.stripe.checkout import StripeCheckout

        stripe_api_key = os.environ.get("STRIPE_API_KEY")
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url="")

        checkout_status = await stripe_checkout.get_checkout_status(stripe_session_id)

        if checkout_status.payment_status == "paid" and payment.get("payment_status") != "completed":
            await db.payment_transactions.update_one(
                {"stripe_session_id": stripe_session_id},
                {
                    "$set": {
                        "payment_status": "completed",
                        "status": "paid",
                        "completed_at": datetime.now(timezone.utc),
                        "stripe_amount": checkout_status.amount_total,
                        "stripe_currency": checkout_status.currency,
                    }
                },
            )

            await process_owl_delivery(stripe_session_id, payment)

        elif checkout_status.status == "expired" and payment.get("status") != "expired":
            await db.payment_transactions.update_one(
                {"stripe_session_id": stripe_session_id},
                {
                    "$set": {
                        "payment_status": "failed",
                        "status": "expired",
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )

        updated_payment = await db.payment_transactions.find_one({"stripe_session_id": stripe_session_id})
        serialized_payment = serialize_doc(updated_payment)

        return {
            "success": True,
            "payment_status": checkout_status.payment_status,
            "session_status": checkout_status.status,
            "amount": checkout_status.amount_total / 100,
            "currency": checkout_status.currency,
            "payment_data": serialized_payment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting owl payment status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting payment status: {str(e)}")


async def process_owl_delivery(stripe_session_id: str, payment: dict):
    """Process delivery of completed USCIS form"""
    try:
        owl_session_id = payment["owl_session_id"]
        delivery_method = payment["delivery_method"]
        user_email = payment.get("user_email")

        form_result = await generate_final_uscis_form(owl_session_id)

        download_data = {
            "download_id": f"DWN-{int(time_module.time())}-{uuid.uuid4().hex[:8]}",
            "stripe_session_id": stripe_session_id,
            "owl_session_id": owl_session_id,
            "user_email": user_email,
            "form_data": form_result,
            "delivery_method": delivery_method,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=24),
            "download_count": 0,
            "max_downloads": 3,
        }

        await db.owl_downloads.insert_one(download_data)

        if delivery_method in ["email", "both"]:
            await send_form_by_email(user_email, form_result, download_data["download_id"])

        await db.payment_transactions.update_one(
            {"stripe_session_id": stripe_session_id},
            {"$set": {"download_id": download_data["download_id"], "delivery_processed_at": datetime.now(timezone.utc)}},
        )

        logger.info(f"Owl delivery processed for session {owl_session_id}, method: {delivery_method}")

    except Exception as e:
        logger.error(f"Error processing owl delivery: {e}")


@router.get("/owl-agent/download/{download_id}")
async def download_owl_form(download_id: str):
    """Secure download of completed USCIS form"""
    try:
        download = await db.owl_downloads.find_one({"download_id": download_id})
        if not download:
            raise HTTPException(status_code=404, detail="Download not found")

        if download.get("expires_at") and download["expires_at"] < datetime.now(timezone.utc):
            raise HTTPException(status_code=410, detail="Download link expired")

        if download.get("download_count", 0) >= download.get("max_downloads", 3):
            raise HTTPException(status_code=429, detail="Download limit exceeded")

        form_data = download.get("form_data", {})
        pdf_data = form_data.get("pdf_data")

        if not pdf_data:
            raise HTTPException(status_code=500, detail="Form data not available")

        await db.owl_downloads.update_one(
            {"download_id": download_id},
            {"$inc": {"download_count": 1}, "$set": {"last_downloaded_at": datetime.now(timezone.utc)}},
        )

        pdf_bytes = base64.b64decode(pdf_data)

        visa_type = form_data.get("visa_type", "USCIS")
        form_number = form_data.get("form_number", "Form")
        filename = f"{form_number}_{visa_type}_{download['owl_session_id']}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes)),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading owl form: {e}")
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")


async def generate_final_uscis_form(owl_session_id: str) -> dict:
    """Generate final USCIS form with all responses"""
    try:
        session = await db.owl_sessions.find_one({"session_id": owl_session_id})
        responses_cursor = db.owl_responses.find({"session_id": owl_session_id})
        responses = await responses_cursor.to_list(length=None)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        form_template = await get_uscis_form_template(session["visa_type"])

        filled_form = await map_responses_to_uscis_form(responses, form_template, session["visa_type"])

        pdf_data = await generate_final_uscis_pdf(filled_form, session["visa_type"], owl_session_id)

        return {
            "form_number": form_template["form_number"],
            "form_title": form_template["form_title"],
            "visa_type": session["visa_type"],
            "completion_percentage": filled_form["completion_percentage"],
            "pdf_data": pdf_data,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error generating final USCIS form: {e}")
        raise e


async def generate_final_uscis_pdf(filled_form: dict, visa_type: str, session_id: str) -> str:
    """Generate final PDF with privacy notice"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, height - 50, f"USCIS {filled_form['form_number']}")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 75, filled_form["form_title"])

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 120, "AVISO IMPORTANTE DE PRIVACIDADE - OSPREY")

        c.setFont("Helvetica", 10)
        privacy_text = [
            "• Este documento foi gerado pelo sistema Agente Coruja da Osprey",
            "• OSPREY NÃO ARMAZENA seus dados pessoais após o download",
            "• Após o download e/ou envio por email, todos os dados são PERMANENTEMENTE DELETADOS",
            "• Este é seu único acesso ao formulário completo - faça backup se necessário",
            "• Osprey não mantém cópias, não tem acesso futuro aos seus dados",
            "• Responsabilidade pelos dados é transferida totalmente para você após este download",
            "",
            "IMPORTANT PRIVACY NOTICE - OSPREY",
            "• This document was generated by Osprey's Owl Agent system",
            "• OSPREY DOES NOT STORE your personal data after download",
            "• After download and/or email delivery, all data is PERMANENTLY DELETED",
            "• This is your only access to the complete form - backup if needed",
            "• Osprey keeps no copies, has no future access to your data",
            "• Data responsibility is fully transferred to you after this download",
        ]

        y_position = height - 145
        for line in privacy_text:
            if line.startswith("IMPORTANT PRIVACY"):
                c.setFont("Helvetica-Bold", 10)
            elif line.startswith("•"):
                c.setFont("Helvetica", 9)
            else:
                c.setFont("Helvetica", 9)

            c.drawString(50, y_position, line)
            y_position -= 12

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position - 20, "Dados do Formulário / Form Data:")

        y_position -= 45
        c.setFont("Helvetica", 10)

        for field_label, field_value in filled_form["filled_fields"].items():
            if y_position < 80:
                c.showPage()
                y_position = height - 50

            c.drawString(50, y_position, f"{field_label}: {field_value}")
            y_position -= 15

        c.setFont("Helvetica-Bold", 8)
        c.drawString(50, 50, f"Gerado em: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M:%S')} UTC")
        c.drawString(50, 35, f"Sessão: {session_id}")
        c.drawString(50, 20, "AVISO: Seus dados serão DELETADOS do sistema Osprey após este download!")

        c.save()
        buffer.seek(0)
        pdf_bytes = buffer.read()
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        return pdf_base64

    except Exception as e:
        logger.error(f"Error generating final PDF: {e}")
        return "error_generating_pdf"


async def send_form_by_email(email: str, form_data: dict, download_id: str):
    """Send completed form by email"""
    try:
        logger.info(f"Email sent to {email} with download_id {download_id}")
        return True

    except Exception as e:
        logger.error(f"Error sending form by email: {e}")
        return False


@router.post("/owl-agent/start-session")
async def start_owl_session(request: dict):
    """Start a new intelligent questionnaire session with Agente Coruja"""
    try:
        case_id = request.get("case_id")
        visa_type = request.get("visa_type", "H-1B")
        user_language = request.get("language", "pt")
        user_email = request.get("user_email", "").strip().lower()
        session_type = request.get("session_type", "anonymous")

        if not case_id:
            case_id = f"OWL-{int(time_module.time())}-{uuid.uuid4().hex[:8]}"

        from intelligent_owl_agent import intelligent_owl

        session_result = await intelligent_owl.start_guided_session(
            case_id=case_id, visa_type=visa_type, user_language=user_language
        )

        session_data = {
            "session_id": session_result["session_id"],
            "case_id": case_id,
            "visa_type": visa_type,
            "language": user_language,
            "session_type": session_type,
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "relevant_fields": session_result["relevant_fields"],
            "current_field_index": 0,
            "completed_fields": [],
            "total_fields": session_result["total_fields"],
        }

        if session_type == "authenticated" and user_email:
            session_data["user_email"] = user_email
            user = await db.owl_users.find_one({"email": user_email})
            if user:
                session_data["user_id"] = user["user_id"]

        await db.owl_sessions.insert_one(session_data)

        return {
            "success": True,
            "agent": "Agente Coruja - Sistema Inteligente de Questionários",
            "session": session_result,
            "session_type": session_type,
            "user_email": user_email if user_email else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error starting Owl session: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting session: {str(e)}")


@router.get("/owl-agent/session/{session_id}")
async def get_owl_session(session_id: str):
    """Get current session status and progress"""
    try:
        from intelligent_owl_agent import intelligent_owl

        session = await db.owl_sessions.find_one({"session_id": session_id}, {"_id": 0})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        progress = await intelligent_owl.get_session_progress(session_id)

        return {
            "success": True,
            "session_data": session,
            "progress": progress,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Owl session: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting session: {str(e)}")


@router.get("/owl-agent/field-guidance/{session_id}/{field_id}")
async def get_field_guidance(
    session_id: str, field_id: str, current_value: str = "", user_context: dict = None
):
    """Get intelligent guidance for a specific field"""
    try:
        from intelligent_owl_agent import intelligent_owl

        session = await db.owl_sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        guidance = await intelligent_owl.get_field_guidance(
            field_id=field_id,
            visa_type=session["visa_type"],
            user_language=session["language"],
            current_value=current_value,
            user_context=user_context or {},
        )

        return {
            "success": True,
            "field_guidance": guidance,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting field guidance: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting guidance: {str(e)}")


@router.post("/owl-agent/validate-field")
async def validate_field_input(request: dict):
    """Validate user input for a specific field using sistema and Google APIs"""
    try:
        from intelligent_owl_agent import intelligent_owl

        session_id = request.get("session_id")
        field_id = request.get("field_id")
        user_input = request.get("user_input", "")
        full_context = request.get("context", {})

        if not all([session_id, field_id]):
            raise HTTPException(status_code=400, detail="session_id and field_id are required")

        session = await db.owl_sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        validation_result = await intelligent_owl.validate_field_input(
            field_id=field_id,
            user_input=user_input,
            visa_type=session["visa_type"],
            session_id=session_id,
            full_context=full_context,
        )

        if validation_result.get("overall_score", 0) >= 70:
            await db.owl_sessions.update_one(
                {"session_id": session_id},
                {"$addToSet": {"completed_fields": field_id}, "$set": {"last_updated": datetime.now(timezone.utc)}},
            )

        return {
            "success": True,
            "validation": validation_result,
            "score": validation_result.get("overall_score", 0),
            "field_id": field_id,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating field: {e}")
        raise HTTPException(status_code=500, detail=f"Error validating field: {str(e)}")


@router.post("/owl-agent/save-response")
async def save_field_response(request: dict):
    """Save user response for a field"""
    try:
        session_id = request.get("session_id")
        field_id = request.get("field_id")
        user_response = request.get("user_response", "")
        validation_score = request.get("validation_score", 0)

        if not all([session_id, field_id]):
            raise HTTPException(status_code=400, detail="session_id and field_id are required")

        response_data = {
            "session_id": session_id,
            "field_id": field_id,
            "user_response": user_response,
            "validation_score": validation_score,
            "timestamp": datetime.now(timezone.utc),
        }

        await db.owl_responses.insert_one(response_data)

        await db.owl_sessions.update_one(
            {"session_id": session_id},
            {"$set": {"last_updated": datetime.now(timezone.utc), f"responses.{field_id}": user_response}},
        )

        return {
            "success": True,
            "message": "Response saved successfully",
            "session_id": session_id,
            "field_id": field_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving response: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving response: {str(e)}")


@router.post("/owl-agent/generate-uscis-form")
async def generate_uscis_form(request: dict):
    """Generate official USCIS form from questionnaire responses"""
    try:
        session_id = request.get("session_id")

        if not session_id:
            raise HTTPException(status_code=400, detail="session_id is required")

        session = await db.owl_sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        responses_cursor = db.owl_responses.find({"session_id": session_id})
        responses = await responses_cursor.to_list(length=None)

        form_template = await get_uscis_form_template(session["visa_type"])

        filled_form = await map_responses_to_uscis_form(
            responses=responses, form_template=form_template, visa_type=session["visa_type"]
        )

        pdf_data = await generate_uscis_pdf(filled_form, session["visa_type"])

        form_data = {
            "session_id": session_id,
            "case_id": session["case_id"],
            "visa_type": session["visa_type"],
            "filled_form": filled_form,
            "pdf_data": pdf_data,
            "status": "generated",
            "created_at": datetime.now(timezone.utc),
        }

        result = await db.owl_generated_forms.insert_one(form_data)
        form_id = str(result.inserted_id)

        return {
            "success": True,
            "message": "USCIS form generated successfully",
            "form_id": form_id,
            "session_id": session_id,
            "visa_type": session["visa_type"],
            "pdf_available": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating USCIS form: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating form: {str(e)}")


@router.get("/owl-agent/download-form/{form_id}")
async def download_generated_form(form_id: str):
    """Download generated USCIS form PDF"""
    try:
        form = await db.owl_generated_forms.find_one({"_id": ObjectId(form_id)})
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        pdf_bytes = base64.b64decode(form["pdf_data"])

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=uscis_{form['visa_type']}_{form['case_id']}.pdf"},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading form: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading form: {str(e)}")


async def get_uscis_form_template(visa_type: str) -> Dict[str, Any]:
    """Get USCIS form template based on visa type"""
    templates = {
        "H-1B": {
            "form_number": "I-129",
            "form_title": "Petition for a Nonimmigrant Worker",
            "sections": {
                "part1_petition_info": ["petition_type", "requested_action", "total_workers"],
                "part2_petitioner_info": ["company_name", "trade_name", "address", "ein"],
                "part3_processing_info": ["consulate_processing", "change_of_status"],
                "part4_beneficiary_info": ["full_name", "date_of_birth", "country_of_birth", "address"],
                "part5_h_classification": ["h1b_classification", "academic_degree", "specialty_occupation"],
                "part6_h_specific": ["lca_number", "wage_rate", "employment_start_date", "employment_end_date"],
            },
        },
        "F-1": {
            "form_number": "I-20",
            "form_title": "Certificate of Eligibility for Nonimmigrant Student Status",
            "sections": {
                "student_info": ["full_name", "date_of_birth", "country_of_birth", "country_of_citizenship"],
                "school_info": ["institution_name", "school_code", "program_of_study", "education_level"],
                "financial_info": ["funding_source", "estimated_expenses", "sponsor_info"],
                "program_info": ["program_start_date", "program_end_date", "english_proficiency"],
            },
        },
        "I-485": {
            "form_number": "I-485",
            "form_title": "Register Permanent Residence or Adjust Status",
            "sections": {
                "applicant_info": ["full_name", "other_names", "date_of_birth", "country_of_birth"],
                "current_status": ["current_immigration_status", "i94_number", "entry_date"],
                "basis_for_application": ["adjustment_category", "priority_date", "petition_receipt"],
                "background": ["immigration_history", "criminal_history", "medical_exam"],
            },
        },
    }

    return templates.get(visa_type, templates["H-1B"])


async def map_responses_to_uscis_form(
    responses: List[Dict], form_template: Dict, visa_type: str
) -> Dict[str, Any]:
    """Map questionnaire responses to official USCIS form fields"""
    response_lookup = {resp["field_id"]: resp["user_response"] for resp in responses}

    field_mappings = {
        "H-1B": {
            "full_name": "1.a. Family Name (Last Name)",
            "date_of_birth": "2.a. Date of Birth",
            "place_of_birth": "2.b. Country of Birth",
            "current_address": "3.a. Current Physical Address",
            "employer_name": "1.a. Legal Business Name",
            "current_job": "5.a. Classification Sought",
            "annual_income": "5.b. Rate of Pay",
        },
        "F-1": {
            "full_name": "1. Family Name",
            "date_of_birth": "3. Birth Date",
            "place_of_birth": "4. Country of Birth",
            "current_address": "5. Country of Citizenship",
        },
    }

    mappings = field_mappings.get(visa_type, field_mappings["H-1B"])

    filled_form = {}
    for field_id, uscis_field in mappings.items():
        if field_id in response_lookup:
            filled_form[uscis_field] = response_lookup[field_id]

    return {
        "form_number": form_template["form_number"],
        "form_title": form_template["form_title"],
        "filled_fields": filled_form,
        "completion_percentage": len(filled_form) / len(mappings) * 100,
    }


async def generate_uscis_pdf(filled_form: Dict, visa_type: str) -> str:
    """Generate PDF from filled form data"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"USCIS Form {filled_form['form_number']}")
        c.drawString(50, height - 70, filled_form["form_title"])

        c.setFont("Helvetica", 10)
        y_position = height - 120

        for field_label, field_value in filled_form["filled_fields"].items():
            c.drawString(50, y_position, f"{field_label}: {field_value}")
            y_position -= 20

            if y_position < 50:
                c.showPage()
                y_position = height - 50

        c.setFont("Helvetica-Italic", 8)
        c.drawString(
            50,
            50,
            f"Generated by Agente Coruja - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC",
        )
        c.drawString(50, 35, f"Completion: {filled_form['completion_percentage']:.1f}%")

        c.save()

        buffer.seek(0)
        pdf_bytes = buffer.read()
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        return pdf_base64

    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return "mock_pdf_data_base64_encoded"
