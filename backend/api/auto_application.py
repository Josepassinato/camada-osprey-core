import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user, get_current_user_optional
from core.database import db
from models.auto_application import AutoApplicationCase, CaseCreate, CaseUpdate
from services.cases import get_progress_percentage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/auto-application/start")
async def start_auto_application(
    case_data: CaseCreate,
    current_user=Depends(get_current_user_optional),
):
    """Start a new auto-application case (anonymous or authenticated)."""
    try:
        initial_basic_data = {
            "full_name": "",
            "email": "",
            "phone": "",
            "date_of_birth": "",
            "country_of_birth": "",
            "passport_number": "",
            "passport_country": "",
            "passport_issue_date": "",
            "passport_expiration_date": "",
            "current_address": "",
            "mailing_address": "",
        }

        if current_user:
            user_profile = await db.users.find_one({"id": current_user["id"]})
            if user_profile:
                if user_profile.get("email"):
                    initial_basic_data["email"] = user_profile["email"]
                if user_profile.get("full_name"):
                    initial_basic_data["full_name"] = user_profile["full_name"]
                if user_profile.get("phone"):
                    initial_basic_data["phone"] = user_profile["phone"]

            case = AutoApplicationCase(
                form_code=case_data.form_code,
                process_type=case_data.process_type,
                session_token=case_data.session_token,
                user_id=current_user["id"],
                basic_data=initial_basic_data,
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            )
        else:
            case = AutoApplicationCase(
                form_code=case_data.form_code,
                process_type=case_data.process_type,
                session_token=case_data.session_token,
                basic_data=initial_basic_data,
                expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            )

        await db.auto_cases.insert_one(case.dict())

        return {"message": "Auto-application case created successfully", "case": case}

    except Exception as e:
        logger.error(f"Error starting auto-application: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting auto-application: {str(e)}")


@router.get("/auto-application/case/{case_id}")
async def get_case_anonymous(
    case_id: str,
    session_token: Optional[str] = None,
    current_user=Depends(get_current_user_optional),
):
    """Get a specific case by ID (anonymous or authenticated)."""
    try:
        if current_user:
            case = await db.auto_cases.find_one({"case_id": case_id, "user_id": current_user["id"]})
            if case:
                case.pop("_id", None)
                return {"case": case}

        if session_token:
            case = await db.auto_cases.find_one(
                {"case_id": case_id, "session_token": session_token}
            )
        else:
            case = await db.auto_cases.find_one({"case_id": case_id, "user_id": None})

        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        case.pop("_id", None)
        return {"case": case}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting case: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting case: {str(e)}")


@router.put("/auto-application/case/{case_id}")
async def update_case_anonymous(
    case_id: str,
    case_update: CaseUpdate,
    session_token: Optional[str] = None,
    current_user=Depends(get_current_user_optional),
):
    """Update a specific case (anonymous or authenticated)."""
    try:
        if current_user:
            case = await db.auto_cases.find_one({"case_id": case_id, "user_id": current_user["id"]})
            if case:
                update_data = case_update.dict(exclude_none=True)
                update_data["updated_at"] = datetime.now(timezone.utc)

                if "current_step" in update_data and "progress_percentage" not in update_data:
                    update_data["progress_percentage"] = get_progress_percentage(
                        update_data["current_step"]
                    )

                if "form_code" in update_data and case.get("status") == "created":
                    update_data["status"] = "form_selected"
                    if "progress_percentage" not in update_data:
                        update_data["progress_percentage"] = 20

                await db.auto_cases.update_one({"case_id": case_id}, {"$set": update_data})

                updated_case = await db.auto_cases.find_one({"case_id": case_id})
                updated_case.pop("_id", None)
                return {"message": "Case updated successfully", "case": updated_case}

        query = {"case_id": case_id}
        if session_token:
            query["session_token"] = session_token
        else:
            query["user_id"] = None

        case = await db.auto_cases.find_one(query)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        update_data = case_update.dict(exclude_none=True)
        update_data["updated_at"] = datetime.now(timezone.utc)

        if "current_step" in update_data and "progress_percentage" not in update_data:
            update_data["progress_percentage"] = get_progress_percentage(
                update_data["current_step"]
            )

        if "form_code" in update_data and case.get("status") == "created":
            update_data["status"] = "form_selected"
            if "progress_percentage" not in update_data:
                update_data["progress_percentage"] = 20

        await db.auto_cases.update_one({"case_id": case_id}, {"$set": update_data})

        updated_case = await db.auto_cases.find_one({"case_id": case_id})
        updated_case.pop("_id", None)
        return {"message": "Case updated successfully", "case": updated_case}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating case: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating case: {str(e)}")


@router.patch("/auto-application/case/{case_id}")
async def patch_case_data(
    case_id: str,
    update_data: dict,
    current_user=Depends(get_current_user_optional),
):
    """Efficiently update specific case fields with optimized data persistence."""
    try:
        query = {"case_id": case_id}
        if current_user:
            query["user_id"] = current_user["id"]
        else:
            session_token = update_data.get("session_token")
            if session_token:
                query["session_token"] = session_token
            else:
                query["user_id"] = None

        case = await db.auto_cases.find_one(query)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        sanitized_update = {}
        allowed_fields = [
            "status",
            "basic_data",
            "user_story_text",
            "simplified_form_responses",
            "progress_percentage",
            "current_step",
            "documents",
            "extracted_facts",
            "official_form_data",
            "ai_generated_uscis_form",
        ]

        for field in allowed_fields:
            if field in update_data and update_data[field] is not None:
                sanitized_update[field] = update_data[field]

        sanitized_update["updated_at"] = datetime.now(timezone.utc)

        result = await db.auto_cases.update_one({"case_id": case_id}, {"$set": sanitized_update})

        if result.modified_count == 0:
            return {"message": "No changes made to case"}

        updated_case = await db.auto_cases.find_one({"case_id": case_id})
        updated_case.pop("_id", None)

        return {
            "message": "Case updated efficiently",
            "case": updated_case,
            "fields_updated": list(sanitized_update.keys()),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error patching case: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error patching case: {str(e)}")


@router.post("/auto-application/case/{case_id}/batch-update")
async def batch_update_case_data(
    case_id: str,
    request: dict,
    current_user=Depends(get_current_user_optional),
):
    """Process multiple case updates in a single transaction for better performance."""
    try:
        query = {"case_id": case_id}
        if current_user:
            query["user_id"] = current_user["id"]

        case = await db.auto_cases.find_one(query)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        updates = request.get("updates", [])
        combined_update = {"updated_at": datetime.now(timezone.utc)}

        for update in updates:
            operation = update.get("operation", "set")
            field = update.get("field")
            value = update.get("value")

            if not field:
                continue

            if operation == "set":
                combined_update[field] = value
            elif operation == "append" and field in case and isinstance(case[field], list):
                if field not in combined_update:
                    combined_update[field] = case[field].copy()
                if isinstance(combined_update[field], list):
                    combined_update[field].append(value)
            elif operation == "merge" and isinstance(value, dict):
                if field not in combined_update:
                    combined_update[field] = (
                        case.get(field, {}).copy() if isinstance(case.get(field), dict) else {}
                    )
                combined_update[field].update(value)

        result = await db.auto_cases.update_one({"case_id": case_id}, {"$set": combined_update})

        if result.modified_count == 0:
            return {"message": "No changes made in batch update"}

        return {
            "message": "Batch update completed successfully",
            "updates_processed": len(updates),
            "fields_modified": list(combined_update.keys()),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch update: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in batch update: {str(e)}")


@router.post("/auto-application/case/{case_id}/claim")
async def claim_anonymous_case(case_id: str, current_user=Depends(get_current_user)):
    """Claim an anonymous case when user registers/logs in."""
    try:
        case = await db.auto_cases.find_one({"case_id": case_id, "user_id": None})

        if not case:
            raise HTTPException(status_code=404, detail="Anonymous case not found")

        await db.auto_cases.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "user_id": current_user["id"],
                    "session_token": None,
                    "expires_at": None,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        return {"message": "Case claimed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error claiming case: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error claiming case: {str(e)}")
