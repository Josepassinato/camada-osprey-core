"""
Settings API for Imigrai B2B
Manage office settings, team, WhatsApp and Telegram connections.
"""

import secrets
import uuid
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

from backend.core.database import db
from backend.b2b_auth_api import get_b2b_user, hash_password

router = APIRouter(prefix="/api/settings", tags=["settings"])


# ============================================================================
# MODELS
# ============================================================================

class UpdateOfficeName(BaseModel):
    name: str


class InviteUserRequest(BaseModel):
    email: EmailStr
    name: str
    role: str


class AddWhatsAppRequest(BaseModel):
    phone: str
    user_name: str
    role: str


# ============================================================================
# OFFICE
# ============================================================================

@router.get("/office")
async def get_office_settings(current_user: dict = Depends(get_b2b_user)):
    office = await db.offices.find_one(
        {"office_id": current_user["office_id"]}, {"_id": 0}
    )
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")

    users = await db.b2b_users.find(
        {"office_id": current_user["office_id"], "is_active": True},
        {"_id": 0, "password_hash": 0},
    ).to_list(length=100)

    return {
        "name": office["name"],
        "plan": office.get("plan", "trial"),
        "trial_ends_at": office.get("trial_ends_at", "").isoformat()
        if office.get("trial_ends_at")
        else None,
        "whatsapp_numbers": office.get("whatsapp_numbers", []),
        "telegram_chat_ids": office.get("telegram_chat_ids", []),
        "users": users,
    }


@router.patch("/office")
async def update_office_name(
    data: UpdateOfficeName, current_user: dict = Depends(get_b2b_user)
):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Only owners can update office name")

    await db.offices.update_one(
        {"office_id": current_user["office_id"]},
        {"$set": {"name": data.name}},
    )
    return {"message": "Office name updated", "name": data.name}


# ============================================================================
# USERS / TEAM
# ============================================================================

@router.get("/users")
async def list_users(current_user: dict = Depends(get_b2b_user)):
    users = await db.b2b_users.find(
        {"office_id": current_user["office_id"]},
        {"_id": 0, "password_hash": 0},
    ).to_list(length=100)

    return [
        {
            "user_id": u["user_id"],
            "name": u.get("name", ""),
            "email": u.get("email", ""),
            "role": u.get("role", ""),
            "last_login": u.get("last_login", "").isoformat()
            if u.get("last_login")
            else None,
            "is_active": u.get("is_active", True),
        }
        for u in users
    ]


@router.post("/users/invite")
async def invite_user(
    data: InviteUserRequest, current_user: dict = Depends(get_b2b_user)
):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Only owners can invite users")

    if data.role not in ("attorney", "paralegal"):
        raise HTTPException(status_code=400, detail="Role must be attorney or paralegal")

    existing = await db.b2b_users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    temp_password = secrets.token_urlsafe(6)
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    user_doc = {
        "user_id": user_id,
        "office_id": current_user["office_id"],
        "email": data.email,
        "name": data.name,
        "role": data.role,
        "password_hash": hash_password(temp_password),
        "is_active": True,
        "created_at": now,
        "last_login": None,
    }

    await db.b2b_users.insert_one(user_doc)

    return {
        "message": "User invited",
        "email": data.email,
        "temp_password": temp_password,
    }


@router.delete("/users/{user_id}")
async def deactivate_user(user_id: str, current_user: dict = Depends(get_b2b_user)):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Only owners can deactivate users")

    if user_id == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    result = await db.b2b_users.update_one(
        {"user_id": user_id, "office_id": current_user["office_id"]},
        {"$set": {"is_active": False}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deactivated", "user_id": user_id}


# ============================================================================
# WHATSAPP
# ============================================================================

async def _reload_whatsapp():
    """Notify WhatsApp gateway to reload offices."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(
                "http://localhost:3003/reload-offices",
                headers={"X-Internal-Token": "imigrai-internal"},
            )
    except Exception:
        pass  # Gateway might not be running


@router.post("/whatsapp/add")
async def add_whatsapp(
    data: AddWhatsAppRequest, current_user: dict = Depends(get_b2b_user)
):
    phone = "".join(c for c in data.phone if c.isdigit())
    if len(phone) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone number")

    entry = {
        "phone": phone,
        "user_name": data.user_name,
        "role": data.role,
        "added_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.offices.update_one(
        {"office_id": current_user["office_id"]},
        {"$push": {"whatsapp_numbers": entry}},
    )

    await _reload_whatsapp()

    office = await db.offices.find_one({"office_id": current_user["office_id"]})
    return office.get("whatsapp_numbers", [])


@router.delete("/whatsapp/{phone}")
async def remove_whatsapp(phone: str, current_user: dict = Depends(get_b2b_user)):
    clean_phone = "".join(c for c in phone if c.isdigit())
    await db.offices.update_one(
        {"office_id": current_user["office_id"]},
        {"$pull": {"whatsapp_numbers": {"phone": clean_phone}}},
    )
    await _reload_whatsapp()
    return {"message": "WhatsApp number removed"}


# ============================================================================
# TELEGRAM
# ============================================================================

@router.post("/telegram/invite-code")
async def generate_telegram_code(current_user: dict = Depends(get_b2b_user)):
    code = secrets.token_urlsafe(4)[:6].upper()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    await db.offices.update_one(
        {"office_id": current_user["office_id"]},
        {
            "$push": {
                "telegram_invite_codes": {
                    "code": code,
                    "expires_at": expires_at,
                    "created_by": current_user["user_id"],
                }
            }
        },
    )

    return {
        "code": code,
        "expires_at": expires_at.isoformat(),
        "instructions": "Envie este código para o bot @imigrai_bot no Telegram",
    }


@router.get("/telegram/connections")
async def list_telegram_connections(current_user: dict = Depends(get_b2b_user)):
    office = await db.offices.find_one({"office_id": current_user["office_id"]})
    return office.get("telegram_chat_ids", []) if office else []


@router.delete("/telegram/{chat_id}")
async def remove_telegram(chat_id: str, current_user: dict = Depends(get_b2b_user)):
    await db.offices.update_one(
        {"office_id": current_user["office_id"]},
        {"$pull": {"telegram_chat_ids": {"chat_id": chat_id}}},
    )
    return {"message": "Telegram connection removed"}
