"""
Letters API for Imigrai B2B
Generate and manage USCIS cover letters per case.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.core.database import db
from backend.b2b_auth_api import get_b2b_user
from letter_generator import LetterGenerator

router = APIRouter(prefix="/api/letters", tags=["letters"])

VALID_LETTER_TYPES = [
    "initial_filing",
    "rfe_response",
    "appeal",
    "withdrawal",
    "status_inquiry",
]


class GenerateLetterRequest(BaseModel):
    case_id: str
    letter_type: str
    special_instructions: Optional[str] = None


@router.post("/generate")
async def generate_letter(
    data: GenerateLetterRequest, current_user: dict = Depends(get_b2b_user)
):
    if data.letter_type not in VALID_LETTER_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid letter_type. Valid: {', '.join(VALID_LETTER_TYPES)}",
        )

    case = await db.b2b_cases.find_one(
        {"case_id": data.case_id, "office_id": current_user["office_id"]}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Enrich case with office name
    office = await db.offices.find_one({"office_id": current_user["office_id"]})
    case["office_name"] = office["name"] if office else "Immigration Law Office"

    content = await LetterGenerator.generate_cover_letter(
        case, data.letter_type, data.special_instructions or ""
    )

    now = datetime.now(timezone.utc)
    letter_id = "LTR-" + str(uuid.uuid4())[:8].upper()

    letter_doc = {
        "letter_id": letter_id,
        "case_id": data.case_id,
        "office_id": current_user["office_id"],
        "letter_type": data.letter_type,
        "content": content,
        "created_at": now,
        "created_by_user_id": current_user["user_id"],
    }

    await db.letters.insert_one(letter_doc)

    return {
        "letter_id": letter_id,
        "content": content,
        "case_id": data.case_id,
        "letter_type": data.letter_type,
        "created_at": now.isoformat(),
    }


@router.get("/{case_id}")
async def list_letters(case_id: str, current_user: dict = Depends(get_b2b_user)):
    letters = (
        await db.letters.find(
            {"case_id": case_id, "office_id": current_user["office_id"]},
            {"_id": 0, "content": 0},
        )
        .sort("created_at", -1)
        .to_list(length=50)
    )

    result = []
    for lt in letters:
        # Fetch content for preview
        full = await db.letters.find_one(
            {"letter_id": lt["letter_id"]}, {"_id": 0, "content": 1}
        )
        preview = (full.get("content", "")[:200] + "...") if full else ""
        result.append(
            {
                "letter_id": lt["letter_id"],
                "letter_type": lt["letter_type"],
                "created_at": lt["created_at"].isoformat()
                if hasattr(lt["created_at"], "isoformat")
                else str(lt["created_at"]),
                "preview": preview,
            }
        )

    return result


@router.get("/content/{letter_id}")
async def get_letter_content(
    letter_id: str, current_user: dict = Depends(get_b2b_user)
):
    letter = await db.letters.find_one(
        {"letter_id": letter_id, "office_id": current_user["office_id"]}, {"_id": 0}
    )
    if not letter:
        raise HTTPException(status_code=404, detail="Letter not found")

    return {
        "letter_id": letter["letter_id"],
        "case_id": letter["case_id"],
        "letter_type": letter["letter_type"],
        "content": letter["content"],
        "created_at": letter["created_at"].isoformat()
        if hasattr(letter["created_at"], "isoformat")
        else str(letter["created_at"]),
    }


@router.delete("/{letter_id}")
async def delete_letter(letter_id: str, current_user: dict = Depends(get_b2b_user)):
    result = await db.letters.delete_one(
        {"letter_id": letter_id, "office_id": current_user["office_id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Letter not found")
    return {"message": "Letter deleted", "letter_id": letter_id}
