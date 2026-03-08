"""
Cases API for Imigrai B2B
Manage immigration cases per office (multi-tenant).
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Optional, List

from backend.core.database import db
from backend.b2b_auth_api import get_b2b_user
from core.rate_limit import limiter

router = APIRouter(prefix="/api/cases", tags=["cases"])

VALID_STATUSES = [
    "intake", "docs_pending", "docs_review", "forms_gen",
    "attorney_review", "ready_to_file", "filed",
    "rfe_received", "rfe_response", "approved", "denied", "withdrawn",
]


# ============================================================================
# MODELS
# ============================================================================

class CaseCreateRequest(BaseModel):
    client_name: str
    visa_type: str
    notes: Optional[str] = None


class CaseUpdateRequest(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    client_name: Optional[str] = None
    visa_type: Optional[str] = None


class DeadlineRequest(BaseModel):
    title: str
    due_date: str  # ISO format
    notes: Optional[str] = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("")
async def list_cases(
    status: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    skip: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_b2b_user),
):
    query = {"office_id": current_user["office_id"]}
    if status and status in VALID_STATUSES:
        query["status"] = status

    cursor = db.b2b_cases.find(query, {"_id": 0}).sort("updated_at", -1).skip(skip).limit(limit)
    cases = await cursor.to_list(length=limit)

    # Add next deadline info
    now = datetime.now(timezone.utc)
    for case in cases:
        deadlines = case.get("deadlines", [])
        future = [d for d in deadlines if d.get("due_date") and datetime.fromisoformat(str(d["due_date"]).replace("Z", "+00:00")) > now]
        if future:
            future.sort(key=lambda d: d["due_date"])
            case["deadline_next"] = future[0].get("due_date")
            delta = datetime.fromisoformat(str(future[0]["due_date"]).replace("Z", "+00:00")) - now
            case["deadline_days"] = delta.days
        else:
            case["deadline_next"] = None
            case["deadline_days"] = None
        # Remove heavy fields from list
        case.pop("documents", None)
        case.pop("deadlines", None)

    return cases


@router.post("")
@limiter.limit("30/minute")
async def create_case(request: Request, data: CaseCreateRequest, current_user: dict = Depends(get_b2b_user)):
    now = datetime.now(timezone.utc)
    case_id = "CASE-" + str(uuid.uuid4())[:8].upper()

    case_doc = {
        "case_id": case_id,
        "office_id": current_user["office_id"],
        "client_name": data.client_name,
        "visa_type": data.visa_type,
        "status": "intake",
        "notes": data.notes or "",
        "documents": [],
        "deadlines": [],
        "created_at": now,
        "updated_at": now,
        "created_by": current_user["user_id"],
    }

    await db.b2b_cases.insert_one(case_doc)

    return {
        "message": "Case created",
        "case_id": case_id,
        "status": "intake",
    }


@router.get("/stats")
async def case_stats(current_user: dict = Depends(get_b2b_user)):
    office_id = current_user["office_id"]
    now = datetime.now(timezone.utc)
    week_from_now = now + timedelta(days=7)

    total = await db.b2b_cases.count_documents({"office_id": office_id})

    active_statuses = ["intake", "docs_pending", "docs_review", "forms_gen", "attorney_review", "ready_to_file", "filed", "rfe_received", "rfe_response"]
    active = await db.b2b_cases.count_documents({"office_id": office_id, "status": {"$in": active_statuses}})

    pending_review = await db.b2b_cases.count_documents({"office_id": office_id, "status": "attorney_review"})

    # Critical: cases with deadline in next 7 days
    pipeline = [
        {"$match": {"office_id": office_id, "status": {"$in": active_statuses}}},
        {"$unwind": {"path": "$deadlines", "preserveNullAndEmptyArrays": False}},
        {"$match": {"deadlines.due_date": {"$lte": week_from_now, "$gte": now}}},
        {"$group": {"_id": "$case_id"}},
        {"$count": "total"},
    ]
    critical_result = await db.b2b_cases.aggregate(pipeline).to_list(length=1)
    critical = critical_result[0]["total"] if critical_result else 0

    return {
        "total": total,
        "active": active,
        "critical": critical,
        "pending_review": pending_review,
    }


@router.get("/{case_id}")
async def get_case(case_id: str, current_user: dict = Depends(get_b2b_user)):
    case = await db.b2b_cases.find_one(
        {"case_id": case_id, "office_id": current_user["office_id"]},
        {"_id": 0},
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.patch("/{case_id}")
async def update_case(case_id: str, data: CaseUpdateRequest, current_user: dict = Depends(get_b2b_user)):
    update_fields = {}
    if data.status:
        if data.status not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status. Valid: {', '.join(VALID_STATUSES)}")
        update_fields["status"] = data.status
    if data.notes is not None:
        update_fields["notes"] = data.notes
    if data.client_name:
        update_fields["client_name"] = data.client_name
    if data.visa_type:
        update_fields["visa_type"] = data.visa_type

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_fields["updated_at"] = datetime.now(timezone.utc)

    result = await db.b2b_cases.update_one(
        {"case_id": case_id, "office_id": current_user["office_id"]},
        {"$set": update_fields},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Case not found")

    return {"message": "Case updated", "case_id": case_id}


@router.post("/{case_id}/deadlines")
async def add_deadline(case_id: str, data: DeadlineRequest, current_user: dict = Depends(get_b2b_user)):
    deadline_doc = {
        "id": str(uuid.uuid4())[:8],
        "title": data.title,
        "due_date": data.due_date,
        "notes": data.notes or "",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = await db.b2b_cases.update_one(
        {"case_id": case_id, "office_id": current_user["office_id"]},
        {
            "$push": {"deadlines": deadline_doc},
            "$set": {"updated_at": datetime.now(timezone.utc)},
        },
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Case not found")

    return {"message": "Deadline added", "deadline": deadline_doc}
