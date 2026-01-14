import logging
import os
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException

from core.auth import create_jwt_token, get_current_user, hash_password, verify_password
from core.database import db
from models.user import (
    UserCreate,
    UserLogin,
    UserProfile,
    UserProfileUpdate,
    UserProgress,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/auth/signup")
async def signup(user_data: UserCreate):
    """Create user"""
    try:
        # EMAIL BYPASS FOR TESTING
        email_bypass = os.environ.get("EMAIL_BYPASS_FOR_TESTING", "FALSE").upper() == "TRUE"
        test_email_domain = os.environ.get("TEST_EMAIL_DOMAIN", "test.local")

        is_test_email = user_data.email.endswith(f"@{test_email_domain}")

        if email_bypass and is_test_email:
            logger.info(f"🧪 TEST MODE: Email bypass active for {user_data.email}")
            email_verified = True
        else:
            email_verified = False

        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        user_id = str(uuid.uuid4())
        hashed_password = hash_password(user_data.password)

        user_doc = {
            "id": user_id,
            "email": user_data.email,
            "password": hashed_password,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "phone": user_data.phone,
            "role": user_data.role if user_data.role in ["user", "admin", "superadmin"] else "user",
            "country_of_birth": None,
            "current_country": None,
            "date_of_birth": None,
            "passport_number": None,
            "email_verified": email_verified,
            "is_test_user": is_test_email if email_bypass else False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        await db.users.insert_one(user_doc)

        # Initialize user progress
        progress = UserProgress(user_id=user_id)
        await db.user_progress.insert_one(progress.dict())

        # Create JWT token
        token = create_jwt_token(user_id, user_data.email)

        response_data = {
            "message": "User created successfully",
            "token": token,
            "user": {
                "id": user_id,
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
            },
        }

        if email_bypass and is_test_email:
            response_data["test_mode"] = True
            response_data["message"] = "🧪 TEST MODE: User created (email verification bypassed)"

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in signup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.post("/auth/login")
async def login(login_data: UserLogin):
    """Login user"""
    try:
        # EMAIL BYPASS FOR TESTING
        email_bypass = os.environ.get("EMAIL_BYPASS_FOR_TESTING", "FALSE").upper() == "TRUE"
        test_email_domain = os.environ.get("TEST_EMAIL_DOMAIN", "test.local")

        is_test_email = login_data.email.endswith(f"@{test_email_domain}")

        user = await db.users.find_one({"email": login_data.email})

        if email_bypass and is_test_email and user:
            logger.info(f"🧪 TEST MODE: Login bypass active for {login_data.email}")
            password_valid = True
        elif user:
            stored_hash = (
                user.get("password") or user.get("hashed_password") or user.get("password_hash")
            )
            password_valid = verify_password(login_data.password, stored_hash)
        else:
            password_valid = False

        if not user or not password_valid:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_jwt_token(user["id"], user["email"])

        response_data = {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
            },
        }

        if email_bypass and is_test_email:
            response_data["test_mode"] = True
            response_data["message"] = (
                "🧪 TEST MODE: Login successful (password verification bypassed)"
            )

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error logging in: {str(e)}")


@router.post("/auth/google-callback")
async def google_auth_callback(request: dict):
    """Process Google OAuth callback from Emergent Auth"""
    try:
        session_token = request.get("session_token")
        email = request.get("email")
        name = request.get("name")
        picture = request.get("picture")
        google_id = request.get("id")

        if not email or not session_token:
            raise HTTPException(status_code=400, detail="Missing required fields")

        logger.info(f"🔐 Google OAuth callback for: {email}")

        existing_user = await db.users.find_one({"email": email})

        if existing_user:
            logger.info(f"✅ Existing user found: {email}")
            user_id = existing_user["id"]
            await db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "google_id": google_id,
                        "picture": picture,
                        "email_verified": True,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )
        else:
            logger.info(f"📝 Creating new user from Google OAuth: {email}")
            user_id = str(uuid.uuid4())
            name_parts = name.split(" ", 1) if name else ["", ""]
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            user_doc = {
                "id": user_id,
                "email": email,
                "password": None,
                "first_name": first_name,
                "last_name": last_name,
                "phone": None,
                "role": "user",
                "google_id": google_id,
                "picture": picture,
                "email_verified": True,
                "country_of_birth": None,
                "current_country": None,
                "date_of_birth": None,
                "passport_number": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }

            await db.users.insert_one(user_doc)

            progress = UserProgress(user_id=user_id)
            await db.user_progress.insert_one(progress.dict())

        session_doc = {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
            "created_at": datetime.now(timezone.utc),
        }
        await db.oauth_sessions.insert_one(session_doc)

        token = create_jwt_token(user_id, email)

        user = await db.users.find_one({"id": user_id})

        logger.info(f"✅ Google OAuth successful for: {email}")

        return {
            "message": "Google authentication successful",
            "token": token,
            "session_token": session_token,
            "user": {
                "id": user_id,
                "email": email,
                "first_name": user.get("first_name", ""),
                "last_name": user.get("last_name", ""),
                "picture": picture,
            },
        }

    except Exception as e:
        logger.error(f"Error in Google OAuth callback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user=Depends(get_current_user)):
    """Get user profile"""
    return UserProfile(**current_user)


@router.put("/profile")
async def update_profile(profile_data: UserProfileUpdate, current_user=Depends(get_current_user)):
    """Update user profile"""
    try:
        update_data = profile_data.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)

        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": update_data},
        )

        updated_user = await db.users.find_one({"id": current_user["id"]})
        return {"message": "Profile updated successfully", "user": UserProfile(**updated_user)}

    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")
