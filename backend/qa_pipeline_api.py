"""
QA Pipeline API for Imigrai B2B
Validates case completeness before USCIS filing using professional QA agent.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.database import db
from backend.b2b_auth_api import get_b2b_user
from backend.agents.qa import get_qa_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/qa", tags=["qa-pipeline"])


class ValidateCaseRequest(BaseModel):
    strict: Optional[bool] = False  # Strict mode = higher threshold


@router.post("/{case_id}/validate")
async def validate_case(
    case_id: str,
    body: ValidateCaseRequest = ValidateCaseRequest(),
    current_user: dict = Depends(get_b2b_user),
):
    """
    Run QA validation on a B2B case.
    Returns score, issues, missing items, and approval status.
    """
    office_id = current_user["office_id"]

    case = await db.b2b_cases.find_one(
        {"case_id": case_id, "office_id": office_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    visa_type = (case.get("visa_type") or case.get("form_code") or "").upper()
    if not visa_type:
        raise HTTPException(
            status_code=400,
            detail="Case has no visa_type or form_code set. Cannot validate.",
        )

    # Normalize form_code for QA agent compatibility
    # The QA agent expects form_code in the case dict
    case_for_qa = dict(case)
    case_for_qa["form_code"] = _normalize_visa_type(visa_type)

    qa_agent = get_qa_agent()
    logger.info(f"🔍 Running QA validation for case {case_id} ({visa_type})")

    qa_report = qa_agent.comprehensive_review(case_for_qa)

    # Adjust threshold for strict mode
    if body.strict and qa_report["overall_score"] < 95:
        qa_report["approval"]["approved"] = False
        qa_report["approval"]["reason"] = (
            f"Strict mode: score {qa_report['overall_score']:.1f}% below 95% threshold"
        )

    # Save QA results to case
    now = datetime.now(timezone.utc)
    await db.b2b_cases.update_one(
        {"case_id": case_id, "office_id": office_id},
        {
            "$set": {
                "qa_review": qa_report,
                "qa_approved": qa_report["approval"]["approved"],
                "qa_score": qa_report["overall_score"],
                "qa_review_date": now,
                "updated_at": now,
            },
            "$push": {
                "history": {
                    "action": "qa_validation",
                    "timestamp": now.isoformat(),
                    "detail": (
                        f"QA score: {qa_report['overall_score']:.1f}% — "
                        f"{'APPROVED' if qa_report['approval']['approved'] else 'NEEDS REVIEW'}"
                    ),
                }
            },
        },
    )

    logger.info(
        f"{'✅' if qa_report['approval']['approved'] else '⚠️'} "
        f"QA for {case_id}: {qa_report['overall_score']:.1f}% — "
        f"{len(qa_report.get('critical_issues', []))} critical, "
        f"{len(qa_report.get('missing_items', []))} missing"
    )

    return {
        "case_id": case_id,
        "visa_type": visa_type,
        "overall_score": qa_report["overall_score"],
        "approved": qa_report["approval"]["approved"],
        "approval_reason": qa_report["approval"].get("reason", ""),
        "categories": qa_report.get("categories", {}),
        "critical_issues": qa_report.get("critical_issues", []),
        "missing_items": qa_report.get("missing_items", []),
        "warnings": qa_report.get("warnings", []),
        "recommendations": qa_report.get("recommendations", []),
        "required_actions": qa_report["approval"].get("required_actions", []),
        "validated_at": now.isoformat(),
    }


@router.get("/{case_id}/status")
async def get_qa_status(case_id: str, current_user: dict = Depends(get_b2b_user)):
    """Get the latest QA validation status for a case."""
    office_id = current_user["office_id"]

    case = await db.b2b_cases.find_one(
        {"case_id": case_id, "office_id": office_id},
        {"_id": 0, "qa_review": 1, "qa_approved": 1, "qa_score": 1, "qa_review_date": 1},
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if not case.get("qa_review"):
        return {
            "case_id": case_id,
            "validated": False,
            "message": "No QA validation has been run. Call POST /api/qa/{case_id}/validate first.",
        }

    review = case["qa_review"]
    return {
        "case_id": case_id,
        "validated": True,
        "overall_score": case.get("qa_score", 0),
        "approved": case.get("qa_approved", False),
        "critical_issues": len(review.get("critical_issues", [])),
        "missing_items": len(review.get("missing_items", [])),
        "warnings": len(review.get("warnings", [])),
        "validated_at": case.get("qa_review_date", "").isoformat()
        if hasattr(case.get("qa_review_date", ""), "isoformat")
        else str(case.get("qa_review_date", "")),
    }


def _normalize_visa_type(visa_type: str) -> str:
    """Normalize visa type to QA agent's expected form_code format."""
    mapping = {
        "H-1B": "H-1B",
        "H1B": "H-1B",
        "O-1": "O-1",
        "O1": "O-1",
        "O-1A": "O-1",
        "O-1B": "O-1",
        "L-1": "L-1",
        "L1": "L-1",
        "L-1A": "L-1",
        "L-1B": "L-1",
        "EB-1A": "EB-1A",
        "EB1A": "EB-1A",
        "EB-1B": "EB-1A",
        "EB-2 NIW": "EB-2 NIW",
        "EB2 NIW": "EB-2 NIW",
        "EB-2NIW": "EB-2 NIW",
        "EB2NIW": "EB-2 NIW",
        "EB-2": "EB-2 NIW",
        "NIW": "EB-2 NIW",
        "I-140": "EB-1A",
        "F-1": "F-1",
        "F1": "F-1",
        "I-539": "I-539",
        "I-589": "I-589",
    }
    return mapping.get(visa_type, visa_type)
