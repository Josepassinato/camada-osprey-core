import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

import stripe
from fastapi import APIRouter, HTTPException, Request

from backend.admin.products import get_product_for_checkout
from core.database import db
from integrations.stripe import create_checkout_session, verify_payment_status
from packages.payment_packages import (
    calculate_final_price,
    get_all_packages,
    get_visa_package,
)
from utils.vouchers import get_all_active_vouchers, validate_voucher

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/payment/create-payment-intent")
async def create_payment_intent_endpoint(request: Request):
    """Cria PaymentIntent para checkout integrado (Stripe Elements) com suporte a vouchers"""
    try:
        body = await request.json()
        visa_code = body.get("visa_code")
        case_id = body.get("case_id")
        voucher_code = body.get("voucher_code")

        if not visa_code or not case_id:
            raise HTTPException(status_code=400, detail="visa_code e case_id são obrigatórios")

        skip_payment = os.environ.get("SKIP_PAYMENT_FOR_TESTING", "FALSE").upper() == "TRUE"

        if skip_payment:
            logger.info(f"🧪 TESTING MODE: Skipping payment for {visa_code} - {case_id}")

            product = await get_product_for_checkout(db, visa_code)
            original_price = product["price"] if product else 0

            transaction = {
                "transaction_id": f"TEST-{case_id}",
                "case_id": case_id,
                "visa_code": visa_code,
                "amount": 0.0,
                "original_amount": original_price,
                "discount_percentage": 100.0,
                "voucher_code": "TESTING_MODE",
                "currency": "usd",
                "status": "completed",
                "payment_method": "testing_mode",
                "created_at": datetime.now(timezone.utc),
            }
            await db.payment_transactions.insert_one(transaction)

            await db.auto_cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "payment_status": "completed",
                        "payment_info": {
                            "amount": 0.0,
                            "original_amount": original_price,
                            "discount": 100.0,
                            "voucher_code": "TESTING_MODE",
                            "payment_date": datetime.now(timezone.utc),
                            "method": "testing_bypass",
                        },
                    }
                },
            )

            return {
                "success": True,
                "free": True,
                "testing_mode": True,
                "message": "🧪 TESTING MODE: Payment skipped for testing purposes",
                "original_price": original_price,
                "final_price": 0.0,
                "discount_percentage": 100.0,
                "package": product,
            }

        product = await get_product_for_checkout(db, visa_code)
        if not product:
            raise HTTPException(status_code=404, detail=f"Produto {visa_code} não encontrado")

        original_price = product["price"]
        final_price = original_price
        discount_percentage = 0.0
        voucher_applied = None

        if voucher_code:
            from backend.utils.vouchers import increment_voucher_usage

            validation_result = await validate_voucher(voucher_code, visa_code, db)

            if validation_result.valid:
                discount_percentage = validation_result.discount_percentage
                final_price = original_price * (1 - discount_percentage / 100)
                voucher_applied = voucher_code
                await increment_voucher_usage(voucher_code, db)
                logger.info(
                    f"✅ Voucher {voucher_code} aplicado: {discount_percentage}% de desconto"
                )
            else:
                logger.warning(f"⚠️  Voucher {voucher_code} inválido: {validation_result.message}")

        if discount_percentage >= 100.0:
            logger.info(f"🎁 GRATUIDADE TOTAL com voucher {voucher_code} - Pulando pagamento")

            transaction = {
                "transaction_id": f"FREE-{case_id}",
                "case_id": case_id,
                "visa_code": visa_code,
                "amount": 0.0,
                "original_amount": original_price,
                "discount_percentage": 100.0,
                "voucher_code": voucher_code,
                "currency": "usd",
                "status": "completed",
                "payment_method": "voucher_100",
                "created_at": datetime.now(timezone.utc),
            }
            await db.payment_transactions.insert_one(transaction)

            await db.auto_cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "payment_status": "completed",
                        "payment_info": {
                            "amount": 0.0,
                            "original_amount": original_price,
                            "discount": 100.0,
                            "voucher_code": voucher_code,
                            "payment_date": datetime.now(timezone.utc),
                            "method": "free_voucher",
                        },
                    }
                },
            )

            return {
                "success": True,
                "free": True,
                "message": "🎁 Voucher de gratuidade aplicado! Processo liberado sem custo.",
                "voucher_code": voucher_code,
                "original_price": original_price,
                "final_price": 0.0,
                "discount_percentage": 100.0,
                "package": product,
            }

        stripe_api_key = os.environ.get("STRIPE_API_KEY")
        if not stripe_api_key:
            raise HTTPException(status_code=503, detail="Stripe API key not configured")
        stripe.api_key = stripe_api_key

        payment_intent = stripe.PaymentIntent.create(
            amount=max(50, int(final_price * 100)),
            currency="usd",
            metadata={
                "visa_code": visa_code,
                "case_id": case_id,
                "voucher_code": voucher_code or "",
                "discount_percentage": str(discount_percentage),
                "original_price": str(original_price),
            },
            description=f"{product['name']} - {visa_code}"
            + (f" (Voucher: {voucher_code})" if voucher_code else ""),
        )

        transaction = {
            "transaction_id": payment_intent.id,
            "case_id": case_id,
            "visa_code": visa_code,
            "amount": final_price,
            "original_amount": original_price,
            "discount_percentage": discount_percentage,
            "voucher_code": voucher_applied,
            "currency": "usd",
            "status": "pending",
            "payment_method": "card",
            "created_at": datetime.now(timezone.utc),
        }
        await db.payment_transactions.insert_one(transaction)

        logger.info(
            f"✅ PaymentIntent criado: {payment_intent.id} - "
            f"${final_price:.2f} (Original: ${original_price:.2f}, "
            f"Desconto: {discount_percentage}%)"
        )

        return {
            "success": True,
            "client_secret": payment_intent.client_secret,
            "payment_intent_id": payment_intent.id,
            "package": product,
            "pricing": {
                "original_price": original_price,
                "discount_percentage": discount_percentage,
                "final_price": final_price,
                "voucher_code": voucher_applied,
            },
        }

    except stripe.error.StripeError as e:
        logger.error(f"❌ Erro Stripe: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Erro ao criar PaymentIntent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payment/create-checkout")
async def create_payment_checkout(request: Request):
    """Cria uma sessão de checkout do Stripe."""
    try:
        data = await request.json()
        visa_code = data.get("visa_code")
        case_id = data.get("case_id")
        voucher_code = data.get("voucher_code", "").strip()

        if not visa_code or not case_id:
            raise HTTPException(status_code=400, detail="visa_code e case_id são obrigatórios")

        skip_payment = os.environ.get("SKIP_PAYMENT_FOR_TESTING", "FALSE").upper() == "TRUE"

        if skip_payment:
            logger.info(f"🧪 TESTING MODE: Skipping checkout for {visa_code} - {case_id}")

            product = await get_product_for_checkout(db, visa_code)
            original_price = product["price"] if product else 0
            fake_session_id = f"test_session_{case_id}_{datetime.now(timezone.utc).timestamp()}"

            transaction = {
                "transaction_id": f"TEST-CHECKOUT-{case_id}",
                "stripe_session_id": fake_session_id,
                "case_id": case_id,
                "visa_code": visa_code,
                "amount": 0.0,
                "original_amount": original_price,
                "discount_percentage": 100.0,
                "voucher_code": "TESTING_MODE",
                "currency": "usd",
                "status": "completed",
                "payment_method": "testing_mode",
                "created_at": datetime.now(timezone.utc),
            }
            await db.payment_transactions.insert_one(transaction)

            await db.auto_cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "payment_status": "completed",
                        "payment_info": {
                            "amount": 0.0,
                            "original_amount": original_price,
                            "discount": 100.0,
                            "voucher_code": "TESTING_MODE",
                            "payment_date": datetime.now(timezone.utc),
                            "method": "testing_bypass",
                            "session_id": fake_session_id,
                        },
                    }
                },
            )

            frontend_url = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:3000")

            return {
                "success": True,
                "testing_mode": True,
                "message": "🧪 Payment skipped for testing",
                "session_id": fake_session_id,
                "redirect_url": f"{frontend_url}/payment/success?session_id={fake_session_id}&case_id={case_id}",
                "skip_checkout": True,
            }

        if not os.environ.get("STRIPE_API_KEY"):
            raise HTTPException(status_code=503, detail="Stripe API key not configured")

        frontend_url = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:3000")
        success_url = (
            f"{frontend_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}&case_id={case_id}"
        )
        cancel_url = f"{frontend_url}/payment/cancel?case_id={case_id}"

        result = await create_checkout_session(
            visa_code=visa_code,
            case_id=case_id,
            voucher_code=voucher_code if voucher_code else None,
            success_url=success_url,
            cancel_url=cancel_url,
            db=None,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400, detail=result.get("error", "Erro ao criar checkout")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar checkout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payment/status/{session_id}")
async def get_payment_status(session_id: str):
    """Verifica o status de um pagamento."""
    try:
        if not os.environ.get("STRIPE_API_KEY"):
            raise HTTPException(status_code=503, detail="Stripe API key not configured")

        result = await verify_payment_status(session_id, db)
        if not result.get("success"):
            raise HTTPException(
                status_code=400, detail=result.get("error", "Erro ao verificar pagamento")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vouchers/validate/{voucher_code}")
async def validate_voucher_endpoint(voucher_code: str, visa_code: str):
    """Valida um voucher para um visto específico."""
    try:
        result = await validate_voucher(voucher_code, visa_code, db)
        return result.dict()
    except Exception as e:
        logger.error(f"Erro ao validar voucher: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vouchers/active")
async def get_active_vouchers():
    """Retorna lista de vouchers ativos."""
    try:
        vouchers = get_all_active_vouchers()
        return {"success": True, "vouchers": vouchers}
    except Exception as e:
        logger.error(f"Erro ao listar vouchers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/packages")
async def get_payment_packages():
    """Retorna todos os pacotes de pagamento disponíveis."""
    try:
        packages = get_all_packages()
        return {"success": True, "packages": packages}
    except Exception as e:
        logger.error(f"Erro ao listar pacotes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/packages/{visa_code}")
async def get_visa_package_info(visa_code: str, voucher_code: Optional[str] = None):
    """Retorna informações de pacote e preço para um visto específico."""
    try:
        package = get_visa_package(visa_code)

        discount_percentage = 0.0
        voucher_info = None

        if voucher_code:
            voucher_validation = await validate_voucher(voucher_code, visa_code, db)
            if voucher_validation.valid:
                discount_percentage = voucher_validation.discount_percentage
                voucher_info = {
                    "code": voucher_validation.voucher_code,
                    "discount_percentage": discount_percentage,
                    "message": voucher_validation.message,
                }

        price_info = calculate_final_price(visa_code, discount_percentage)

        return {
            "success": True,
            "package": package,
            "price_info": price_info,
            "voucher_info": voucher_info,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao obter pacote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-application/process-payment")
async def process_payment(request: dict):
    """Process payment for auto-application package"""
    try:
        case_id = request.get("case_id")
        package_id = request.get("package_id")
        payment_method = request.get("payment_method")
        amount = request.get("amount")

        if not all([case_id, package_id, payment_method, amount]):
            raise HTTPException(status_code=400, detail="Missing required payment information")

        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        payment_id = f"PAY-{str(uuid.uuid4())[:8].upper()}"

        payment_data = {
            "payment_id": payment_id,
            "case_id": case_id,
            "package_id": package_id,
            "payment_method": payment_method,
            "amount": amount,
            "currency": "USD",
            "status": "completed",
            "processed_at": datetime.now(timezone.utc),
            "transaction_fee": amount * 0.029 if payment_method == "credit_card" else 0,
        }

        await db.auto_cases.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "payment_status": "completed",
                    "payment_id": payment_id,
                    "package_selected": package_id,
                    "payment_data": payment_data,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        await db.payments.insert_one(payment_data)

        return {
            "message": "Payment processed successfully",
            "payment_id": payment_id,
            "status": "completed",
            "amount_charged": amount,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing payment: {str(e)}")
