"""
Intake Wizard API for Imigrai B2B
Guided case creation with step-by-step question flow.
Collects beneficiary, employer, position, and case data to populate basic_data.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.database import db
from backend.b2b_auth_api import get_b2b_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/intake", tags=["intake-wizard"])


# ── Step definitions ──────────────────────────────────────────────────────

STEPS = {
    "beneficiary": {
        "title": "Beneficiary Information",
        "description": "Personal details of the visa applicant",
        "fields": [
            {"key": "full_name", "label": "Full Legal Name", "type": "text", "required": True},
            {"key": "first_name", "label": "First Name", "type": "text", "required": True},
            {"key": "last_name", "label": "Last Name", "type": "text", "required": True},
            {"key": "date_of_birth", "label": "Date of Birth", "type": "date", "required": True},
            {"key": "country_of_birth", "label": "Country of Birth", "type": "text", "required": True},
            {"key": "citizenship", "label": "Country of Citizenship", "type": "text", "required": True},
            {"key": "passport_number", "label": "Passport Number", "type": "text", "required": True},
            {"key": "passport_country", "label": "Passport Issuing Country", "type": "text", "required": False},
            {"key": "passport_expiry", "label": "Passport Expiry Date", "type": "date", "required": False},
            {"key": "email", "label": "Email Address", "type": "email", "required": False},
            {"key": "phone", "label": "Phone Number", "type": "text", "required": False},
            {"key": "us_address", "label": "U.S. Address (if applicable)", "type": "text", "required": False},
            {"key": "us_city", "label": "U.S. City", "type": "text", "required": False},
            {"key": "us_state", "label": "U.S. State", "type": "text", "required": False},
            {"key": "us_zip", "label": "U.S. ZIP Code", "type": "text", "required": False},
        ],
    },
    "employer": {
        "title": "Petitioner / Employer Information",
        "description": "Details of the sponsoring employer or petitioner",
        "fields": [
            {"key": "company_name", "label": "Company / Organization Name", "type": "text", "required": True},
            {"key": "ein", "label": "Employer Identification Number (EIN)", "type": "text", "required": False},
            {"key": "address", "label": "Company Address", "type": "text", "required": True},
            {"key": "city", "label": "City", "type": "text", "required": False},
            {"key": "state", "label": "State", "type": "text", "required": False},
            {"key": "zip", "label": "ZIP Code", "type": "text", "required": False},
            {"key": "phone", "label": "Company Phone", "type": "text", "required": False},
            {"key": "contact_name", "label": "Contact Person Name", "type": "text", "required": False},
            {"key": "contact_email", "label": "Contact Email", "type": "email", "required": False},
            {"key": "num_employees", "label": "Number of Employees", "type": "number", "required": False},
            {"key": "year_established", "label": "Year Established", "type": "text", "required": False},
            {"key": "business_type", "label": "Type of Business", "type": "text", "required": False},
        ],
    },
    "position": {
        "title": "Position / Job Information",
        "description": "Details about the offered position",
        "fields": [
            {"key": "job_title", "label": "Job Title", "type": "text", "required": True},
            {"key": "soc_code", "label": "SOC Code (if known)", "type": "text", "required": False},
            {"key": "salary", "label": "Annual Salary", "type": "text", "required": True},
            {"key": "hours_per_week", "label": "Hours per Week", "type": "number", "required": False},
            {"key": "lca_number", "label": "LCA Case Number", "type": "text", "required": False},
            {"key": "start_date", "label": "Employment Start Date", "type": "date", "required": True},
            {"key": "end_date", "label": "Employment End Date", "type": "date", "required": False},
            {"key": "work_address", "label": "Work Site Address", "type": "text", "required": False},
            {"key": "work_city", "label": "Work Site City", "type": "text", "required": False},
            {"key": "work_state", "label": "Work Site State", "type": "text", "required": False},
            {"key": "work_zip", "label": "Work Site ZIP", "type": "text", "required": False},
            {"key": "job_description", "label": "Brief Job Description", "type": "textarea", "required": False},
        ],
    },
    "case": {
        "title": "Case Information",
        "description": "Visa type and case details",
        "fields": [
            {
                "key": "visa_type",
                "label": "Visa Type",
                "type": "select",
                "required": True,
                "options": ["H-1B", "O-1", "L-1", "EB-1A", "EB-2 NIW", "I-539", "I-589", "F-1", "Other"],
            },
            {
                "key": "priority",
                "label": "Priority",
                "type": "select",
                "required": False,
                "options": ["normal", "high", "urgent"],
            },
            {"key": "notes", "label": "Additional Notes", "type": "textarea", "required": False},
        ],
    },
}

STEP_ORDER = ["beneficiary", "employer", "position", "case"]


class IntakeStepData(BaseModel):
    step: str
    data: Dict[str, Any]


class IntakeStartRequest(BaseModel):
    client_name: str
    visa_type: Optional[str] = None


@router.get("/steps")
async def get_intake_steps(current_user: dict = Depends(get_b2b_user)):
    """Get the intake wizard step definitions."""
    return {
        "steps": STEP_ORDER,
        "definitions": STEPS,
        "total_steps": len(STEP_ORDER),
    }


@router.post("/start")
async def start_intake(
    body: IntakeStartRequest,
    current_user: dict = Depends(get_b2b_user),
):
    """Start a new intake wizard session, creating a draft case."""
    office_id = current_user["office_id"]
    case_id = "CASE-" + str(uuid.uuid4())[:8].upper()
    now = datetime.now(timezone.utc)

    case_doc = {
        "case_id": case_id,
        "office_id": office_id,
        "client_name": body.client_name,
        "visa_type": (body.visa_type or "").upper() if body.visa_type else "",
        "status": "intake",
        "priority": "normal",
        "basic_data": {
            "beneficiary": {},
            "employer": {},
            "position": {},
            "case": {},
        },
        "intake_progress": {
            "current_step": STEP_ORDER[0],
            "completed_steps": [],
            "started_at": now,
        },
        "documents": [],
        "notes": [],
        "history": [
            {
                "action": "intake_started",
                "timestamp": now.isoformat(),
                "detail": f"Intake wizard started by {current_user.get('name', current_user['user_id'])}",
            }
        ],
        "created_at": now,
        "created_by": current_user["user_id"],
        "updated_at": now,
    }

    await db.b2b_cases.insert_one(case_doc)

    logger.info(f"📋 Intake started: {case_id} for {body.client_name} by office {office_id}")

    return {
        "case_id": case_id,
        "client_name": body.client_name,
        "current_step": STEP_ORDER[0],
        "step_definition": STEPS[STEP_ORDER[0]],
        "total_steps": len(STEP_ORDER),
        "progress": 0,
    }


@router.post("/{case_id}/step")
async def submit_intake_step(
    case_id: str,
    body: IntakeStepData,
    current_user: dict = Depends(get_b2b_user),
):
    """Submit data for a specific intake step."""
    office_id = current_user["office_id"]

    case = await db.b2b_cases.find_one(
        {"case_id": case_id, "office_id": office_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if body.step not in STEPS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid step: {body.step}. Valid steps: {', '.join(STEP_ORDER)}",
        )

    # Validate required fields
    step_def = STEPS[body.step]
    missing = []
    for field in step_def["fields"]:
        if field["required"] and not body.data.get(field["key"]):
            missing.append(field["label"])

    if missing:
        return {
            "success": False,
            "case_id": case_id,
            "step": body.step,
            "validation_errors": [f"Required: {f}" for f in missing],
        }

    # Update basic_data for this step
    now = datetime.now(timezone.utc)
    basic_data = case.get("basic_data", {})
    basic_data[body.step] = body.data

    # Track completed steps
    intake = case.get("intake_progress", {})
    completed = intake.get("completed_steps", [])
    if body.step not in completed:
        completed.append(body.step)

    # Determine next step
    step_idx = STEP_ORDER.index(body.step) if body.step in STEP_ORDER else -1
    next_step = STEP_ORDER[step_idx + 1] if step_idx + 1 < len(STEP_ORDER) else None
    progress = int((len(completed) / len(STEP_ORDER)) * 100)

    update = {
        "$set": {
            f"basic_data.{body.step}": body.data,
            "intake_progress.current_step": next_step or "complete",
            "intake_progress.completed_steps": completed,
            "updated_at": now,
        },
        "$push": {
            "history": {
                "action": "intake_step_completed",
                "timestamp": now.isoformat(),
                "detail": f"Step '{body.step}' completed ({progress}%)",
            }
        },
    }

    # If the case step provides visa_type, update top-level
    if body.step == "case" and body.data.get("visa_type"):
        update["$set"]["visa_type"] = body.data["visa_type"].upper()
    if body.step == "case" and body.data.get("priority"):
        update["$set"]["priority"] = body.data["priority"]

    # If beneficiary provides full_name, update client_name
    if body.step == "beneficiary" and body.data.get("full_name"):
        update["$set"]["client_name"] = body.data["full_name"]

    # If all steps complete, change status to active
    if not next_step:
        update["$set"]["status"] = "active"
        update["$set"]["intake_progress.completed_at"] = now

    await db.b2b_cases.update_one(
        {"case_id": case_id, "office_id": office_id}, update
    )

    result = {
        "success": True,
        "case_id": case_id,
        "step_completed": body.step,
        "progress": progress,
    }

    if next_step:
        result["next_step"] = next_step
        result["step_definition"] = STEPS[next_step]
    else:
        result["intake_complete"] = True
        result["message"] = f"Intake complete for {case.get('client_name', case_id)}. Case is now active."

    return result


@router.get("/{case_id}/progress")
async def get_intake_progress(case_id: str, current_user: dict = Depends(get_b2b_user)):
    """Get current intake wizard progress for a case."""
    office_id = current_user["office_id"]

    case = await db.b2b_cases.find_one(
        {"case_id": case_id, "office_id": office_id},
        {"_id": 0, "intake_progress": 1, "client_name": 1, "basic_data": 1, "status": 1},
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    intake = case.get("intake_progress", {})
    completed = intake.get("completed_steps", [])
    progress = int((len(completed) / len(STEP_ORDER)) * 100) if STEP_ORDER else 0

    return {
        "case_id": case_id,
        "client_name": case.get("client_name"),
        "status": case.get("status"),
        "current_step": intake.get("current_step"),
        "completed_steps": completed,
        "remaining_steps": [s for s in STEP_ORDER if s not in completed],
        "progress": progress,
        "total_steps": len(STEP_ORDER),
    }
