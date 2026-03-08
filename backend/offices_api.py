"""
Offices API for Imigrai
Manage WhatsApp numbers and Telegram integration per office.
"""

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.core.database import db
from backend.b2b_auth_api import get_b2b_user

router = APIRouter(prefix="/api/offices", tags=["offices"])


# ============================================================================
# MODELS
# ============================================================================

class WhatsAppAddRequest(BaseModel):
    phone: str
    user_name: str
    role: str = "attorney"


# ============================================================================
# WHATSAPP ENDPOINTS
# ============================================================================

@router.post("/whatsapp/add")
async def add_whatsapp_number(data: WhatsAppAddRequest, current_user: dict = Depends(get_b2b_user)):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Only owners can manage WhatsApp numbers")

    office = await db.offices.find_one({"office_id": current_user["office_id"]})
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")

    entry = {"phone": data.phone, "user_name": data.user_name, "role": data.role}

    await db.offices.update_one(
        {"office_id": current_user["office_id"]},
        {"$push": {"whatsapp_numbers": entry}},
    )

    return {"message": "WhatsApp number added", "phone": data.phone}


@router.delete("/whatsapp/{phone}")
async def remove_whatsapp_number(phone: str, current_user: dict = Depends(get_b2b_user)):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Only owners can manage WhatsApp numbers")

    await db.offices.update_one(
        {"office_id": current_user["office_id"]},
        {"$pull": {"whatsapp_numbers": {"phone": phone}}},
    )

    return {"message": "WhatsApp number removed", "phone": phone}


# ============================================================================
# TELEGRAM ENDPOINTS
# ============================================================================

@router.post("/telegram/invite-code")
async def generate_telegram_invite_code(current_user: dict = Depends(get_b2b_user)):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Only owners can generate invite codes")

    code = secrets.token_hex(3).upper()[:6]
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=1)

    code_doc = {
        "code": code,
        "created_at": now,
        "expires_at": expires_at,
    }

    await db.offices.update_one(
        {"office_id": current_user["office_id"]},
        {"$push": {"telegram_invite_codes": code_doc}},
    )

    return {"code": code, "expires_at": expires_at.isoformat()}


@router.post("/telegram/verify-code")
async def verify_telegram_code(data: dict):
    """Internal endpoint for Telegram bot to verify invite codes."""
    code = data.get("code", "").upper()
    if not code:
        raise HTTPException(status_code=400, detail="Code required")

    now = datetime.now(timezone.utc)

    office = await db.offices.find_one({
        "telegram_invite_codes": {
            "$elemMatch": {
                "code": code,
                "expires_at": {"$gt": now},
            }
        }
    })

    if not office:
        raise HTTPException(status_code=404, detail="Invalid or expired code")

    # Remove used code
    await db.offices.update_one(
        {"office_id": office["office_id"]},
        {"$pull": {"telegram_invite_codes": {"code": code}}},
    )

    return {"office_id": office["office_id"], "firm_name": office["name"]}
