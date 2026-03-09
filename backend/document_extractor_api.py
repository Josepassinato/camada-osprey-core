"""
Document Extractor API for Imigrai B2B
Extracts structured data from uploaded documents (passport, I-20, etc.)
and auto-populates case basic_data fields.
"""

import base64
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend.core.database import db
from backend.b2b_auth_api import get_b2b_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/extractor", tags=["document-extractor"])

# Max 20MB uploads
MAX_FILE_SIZE = 20 * 1024 * 1024

SUPPORTED_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "image",
    "image/jpg": "image",
    "image/png": "image",
    "image/tiff": "image",
}

# Mapping from extracted passport fields to basic_data.beneficiary keys
PASSPORT_TO_BENEFICIARY = {
    "surname": "last_name",
    "given_names": "first_name",
    "nationality": "citizenship",
    "date_of_birth": "date_of_birth",
    "date_of_expiry": "passport_expiry",
    "passport_number": "passport_number",
    "place_of_birth": "country_of_birth",
}


@router.post("/{case_id}/extract")
async def extract_document(
    case_id: str,
    file: UploadFile = File(...),
    document_type: Optional[str] = "auto",
    current_user: dict = Depends(get_b2b_user),
):
    """
    Upload a document, extract structured data via OCR, and auto-populate case fields.

    Supported document types: passport, i20, employment_letter, diploma, auto (auto-detect).
    """
    office_id = current_user["office_id"]

    case = await db.b2b_cases.find_one(
        {"case_id": case_id, "office_id": office_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Validate file
    content_type = file.content_type or "application/octet-stream"
    if content_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Supported: PDF, JPEG, PNG, TIFF",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum 20MB.")
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file.")

    filename = file.filename or "document"

    logger.info(
        f"📄 Extracting document for case {case_id}: {filename} "
        f"({len(file_bytes)} bytes, type={document_type})"
    )

    # Use Google Document AI / Vision for OCR
    try:
        from backend.integrations.google import hybrid_validator

        google_proc = hybrid_validator.google_processor
        result = await google_proc.process_document(file_bytes, filename, content_type)

        extracted_text = result.get("full_text", "")
        entities = result.get("entities", [])
        confidence = result.get("confidence", 0)

        logger.info(
            f"🔍 OCR result: {len(extracted_text)} chars, "
            f"{len(entities)} entities, confidence={confidence}"
        )

    except Exception as e:
        logger.error(f"❌ OCR failed: {e}")
        return {
            "success": False,
            "case_id": case_id,
            "error": f"Document processing failed: {str(e)}",
            "suggestion": "Try uploading a clearer image or PDF.",
        }

    # Extract structured fields based on document type
    extracted_fields = {}
    fields_mapped = {}

    if document_type in ("passport", "auto"):
        try:
            from backend.integrations.google import hybrid_validator as hv

            passport_fields = hv.google_processor.extract_passport_fields(entities)

            # Map to basic_data.beneficiary format
            for passport_key, beneficiary_key in PASSPORT_TO_BENEFICIARY.items():
                field_data = passport_fields.get(passport_key)
                if field_data and field_data.get("value"):
                    val = field_data["value"]
                    if isinstance(val, dict):
                        val = val.get("text", str(val))
                    extracted_fields[passport_key] = val
                    fields_mapped[f"beneficiary.{beneficiary_key}"] = val

            if extracted_fields:
                document_type = "passport"
        except Exception as e:
            logger.warning(f"Passport extraction failed: {e}")

    # Auto-populate basic_data if fields were extracted
    updates_applied = {}
    if fields_mapped:
        update_set = {"updated_at": datetime.now(timezone.utc)}
        for dotted_key, value in fields_mapped.items():
            section, field = dotted_key.split(".", 1)
            update_set[f"basic_data.{section}.{field}"] = value
            updates_applied[f"{section}.{field}"] = value

        now = datetime.now(timezone.utc)
        await db.b2b_cases.update_one(
            {"case_id": case_id, "office_id": office_id},
            {
                "$set": update_set,
                "$push": {
                    "history": {
                        "action": "document_extracted",
                        "timestamp": now.isoformat(),
                        "detail": (
                            f"Extracted {len(updates_applied)} fields from {document_type}: "
                            f"{', '.join(updates_applied.keys())}"
                        ),
                    }
                },
            },
        )

        # Update client_name if we got a full name
        if "beneficiary.first_name" in updates_applied or "beneficiary.last_name" in updates_applied:
            first = updates_applied.get("beneficiary.first_name", "")
            last = updates_applied.get("beneficiary.last_name", "")
            if first or last:
                full_name = f"{first} {last}".strip()
                await db.b2b_cases.update_one(
                    {"case_id": case_id, "office_id": office_id},
                    {"$set": {"client_name": full_name, "basic_data.beneficiary.full_name": full_name}},
                )
                updates_applied["client_name"] = full_name

    logger.info(
        f"{'✅' if updates_applied else '⚠️'} "
        f"Extraction for {case_id}: {len(updates_applied)} fields auto-populated"
    )

    return {
        "success": True,
        "case_id": case_id,
        "document_type": document_type,
        "filename": filename,
        "file_size": len(file_bytes),
        "ocr_confidence": confidence,
        "extracted_fields": extracted_fields,
        "fields_auto_populated": updates_applied,
        "total_fields_extracted": len(updates_applied),
        "text_preview": extracted_text[:500] if extracted_text else None,
    }
