"""
B2B Authentication API for Imigrai
Multi-tenant auth system for immigration law offices.
"""

import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, EmailStr
from typing import Optional

from core.rate_limit import limiter

from backend.core.database import db

JWT_SECRET = os.environ.get("JWT_SECRET", "osprey-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

router = APIRouter(prefix="/api/auth/b2b", tags=["b2b-auth"])


# ============================================================================
# MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    firm_name: str
    owner_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class InviteRequest(BaseModel):
    email: EmailStr
    name: str
    role: str = "paralegal"


# ============================================================================
# HELPERS
# ============================================================================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    if not hashed:
        return False
    hashed_bytes = hashed if isinstance(hashed, (bytes, bytearray)) else str(hashed).encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), hashed_bytes)


def create_b2b_token(user_id: str, office_id: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "office_id": office_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_b2b_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_b2b_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "")
    payload = decode_b2b_token(token)
    user = await db.b2b_users.find_one({"user_id": payload["user_id"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {**payload, "name": user.get("name", ""), "email": user.get("email", "")}


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/register")
@limiter.limit("10/minute")
@limiter.limit("50/day")
async def b2b_register(request: Request, data: RegisterRequest):
    existing = await db.b2b_users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    office_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    office_doc = {
        "office_id": office_id,
        "name": data.firm_name,
        "plan": "trial",
        "is_active": True,
        "whatsapp_numbers": [],
        "telegram_chat_ids": [],
        "telegram_invite_codes": [],
        "created_at": now,
        "trial_ends_at": now + timedelta(days=14),
    }

    user_doc = {
        "user_id": user_id,
        "office_id": office_id,
        "email": data.email,
        "name": data.owner_name,
        "role": "owner",
        "password_hash": hash_password(data.password),
        "is_active": True,
        "created_at": now,
        "last_login": now,
    }

    await db.offices.insert_one(office_doc)
    await db.b2b_users.insert_one(user_doc)

    token = create_b2b_token(user_id, office_id, "owner")

    return {
        "message": "Office created successfully",
        "token": token,
        "office_id": office_id,
        "user": {
            "user_id": user_id,
            "office_id": office_id,
            "name": data.owner_name,
            "email": data.email,
            "role": "owner",
            "firm_name": data.firm_name,
            "plan": "trial",
        },
    }


@router.post("/login")
@limiter.limit("10/minute")
@limiter.limit("50/day")
async def b2b_login(request: Request, data: LoginRequest):
    user = await db.b2b_users.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account deactivated")

    office = await db.offices.find_one({"office_id": user["office_id"]})
    if not office or not office.get("is_active", True):
        raise HTTPException(status_code=403, detail="Office deactivated")

    await db.b2b_users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"last_login": datetime.now(timezone.utc)}},
    )

    token = create_b2b_token(user["user_id"], user["office_id"], user["role"])

    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "user_id": user["user_id"],
            "office_id": user["office_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "firm_name": office["name"],
            "plan": office.get("plan", "trial"),
        },
    }


@router.get("/me")
async def b2b_me(current_user: dict = Depends(get_b2b_user)):
    user = await db.b2b_users.find_one({"user_id": current_user["user_id"]})
    office = await db.offices.find_one({"office_id": current_user["office_id"]})

    if not user or not office:
        raise HTTPException(status_code=404, detail="User or office not found")

    return {
        "user_id": user["user_id"],
        "office_id": user["office_id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "firm_name": office["name"],
        "plan": office.get("plan", "trial"),
        "is_active": office.get("is_active", True),
        "trial_ends_at": office.get("trial_ends_at", "").isoformat() if office.get("trial_ends_at") else None,
    }


@router.post("/invite")
async def b2b_invite(data: InviteRequest, current_user: dict = Depends(get_b2b_user)):
    if current_user["role"] not in ("owner", "attorney"):
        raise HTTPException(status_code=403, detail="Only owners and attorneys can invite users")

    existing = await db.b2b_users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if data.role not in ("attorney", "paralegal"):
        raise HTTPException(status_code=400, detail="Role must be attorney or paralegal")

    temp_password = secrets.token_urlsafe(8)[:8]
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
        "message": "User invited successfully",
        "email": data.email,
        "temp_password": temp_password,
    }
