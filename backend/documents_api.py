"""
Documents API — Receives documents from WhatsApp gateway.
Uses Gemini Vision to identify document type and extract metadata.
"""

import os
import uuid
import base64
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import google.generativeai as genai

from tools.definitions import DOC_TYPE_LABELS

router = APIRouter(prefix="/api/documents", tags=["documents"])

INTERNAL_TOKEN = os.environ.get("BACKEND_INTERNAL_TOKEN", "imigrai-internal-2024")

GEMINI_API_KEY = (
    os.environ.get("GEMINI_API_KEY")
    or os.environ.get("EMERGENT_LLM_KEY")
    or os.environ.get("GOOGLE_API_KEY")
)

# MongoDB reference
db = None


def init_db(database):
    global db
    db = database


UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Supported MIME types for Gemini Vision
VISION_MIMES = {
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "application/pdf",
}

VISION_PROMPT = """You are a document classification expert for a U.S. immigration law firm.
Analyze this document and return ONLY a JSON object with these fields:

{
  "document_type": "<one of: passport, i94, diploma, transcript, resume_cv, lca, org_chart, job_offer, pay_stub, ev_letter, recommendation_letter, photos, tax_return, birth_certificate, marriage_certificate, apostille, translation, other>",
  "confidence": <0.0 to 1.0>,
  "description": "<brief description of what was identified, e.g. 'Brazilian passport valid until 03/2029'>",
  "expiry_date": "<if applicable, ISO date or null>",
  "person_name": "<name found on document or null>",
  "issues": "<any issues: expired, blurry, missing stamp, needs apostille, or null>"
}

Be precise. Only output the JSON, no extra text."""


async def identify_document(file_bytes: bytes, mime_type: str, filename: str) -> dict:
    """Use Gemini Vision to identify a document from its image/PDF."""
    if not GEMINI_API_KEY:
        return {
            "document_type": "other",
            "confidence": 0.0,
            "description": f"Arquivo recebido: {filename} (Gemini Vision não configurado)",
            "expiry_date": None,
            "person_name": None,
            "issues": None,
        }

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Build image part
        image_part = {
            "mime_type": mime_type,
            "data": file_bytes,
        }

        response = model.generate_content(
            [VISION_PROMPT, image_part],
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=500,
            ),
        )

        text = response.text.strip()
        # Clean markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        import json
        result = json.loads(text)
        return result

    except Exception as e:
        print(f"⚠️ Gemini Vision error: {e}")
        # Fallback: guess from filename
        doc_type = _guess_type_from_filename(filename)
        return {
            "document_type": doc_type,
            "confidence": 0.3,
            "description": f"Arquivo: {filename} (classificação por nome)",
            "expiry_date": None,
            "person_name": None,
            "issues": None,
        }


def _guess_type_from_filename(filename: str) -> str:
    """Fallback document type detection from filename."""
    fn = filename.lower()
    patterns = {
        "passport": ["passport", "passaporte"],
        "i94": ["i-94", "i94"],
        "diploma": ["diploma", "degree", "certificado"],
        "transcript": ["transcript", "historico"],
        "resume_cv": ["resume", "cv", "curriculo"],
        "lca": ["lca", "labor condition"],
        "pay_stub": ["pay", "stub", "contracheque", "holerite"],
        "tax_return": ["tax", "imposto", "1040", "w2"],
        "birth_certificate": ["birth", "nascimento"],
        "marriage_certificate": ["marriage", "casamento"],
        "recommendation_letter": ["recommendation", "recomendacao"],
        "photos": ["photo", "foto"],
    }
    for doc_type, keywords in patterns.items():
        if any(kw in fn for kw in keywords):
            return doc_type
    return "other"


@router.post("/identify")
async def identify_uploaded_document(
    file: UploadFile = File(...),
    office_id: Optional[str] = Form(None),
    sender_phone: Optional[str] = Form(None),
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
):
    """
    Receive a document (image or PDF) from WhatsApp gateway,
    identify it with Gemini Vision, and store metadata.
    Returns identification result for the chat to use.
    """
    # Auth: internal token from gateway
    if x_internal_token != INTERNAL_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not file.content_type or file.content_type not in VISION_MIMES:
        # Accept anyway but skip vision
        file_bytes = await file.read()
        return JSONResponse(content={
            "document_type": "other",
            "confidence": 0.0,
            "description": f"Arquivo recebido: {file.filename} (tipo não suportado para análise visual)",
            "filename": file.filename,
            "size_bytes": len(file_bytes),
        })

    file_bytes = await file.read()
    if len(file_bytes) > 20 * 1024 * 1024:  # 20MB limit
        raise HTTPException(status_code=413, detail="Arquivo muito grande (max 20MB)")

    # Save file to disk
    doc_id = "DOC-" + str(uuid.uuid4())[:8].upper()
    ext = os.path.splitext(file.filename or "file")[1] or ".bin"
    saved_filename = f"{doc_id}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    with open(saved_path, "wb") as f:
        f.write(file_bytes)

    # Identify with Gemini Vision
    result = await identify_document(file_bytes, file.content_type, file.filename or "file")
    result["doc_id"] = doc_id
    result["filename"] = file.filename
    result["saved_path"] = saved_path
    result["size_bytes"] = len(file_bytes)
    result["mime_type"] = file.content_type

    # Store in MongoDB
    if db is not None:
        await db.document_uploads.insert_one({
            "doc_id": doc_id,
            "office_id": office_id,
            "sender_phone": sender_phone,
            "original_filename": file.filename,
            "saved_path": saved_path,
            "mime_type": file.content_type,
            "size_bytes": len(file_bytes),
            "identification": result,
            "attached_to_case": None,  # Will be set when attorney confirms
            "created_at": datetime.now(timezone.utc),
        })

    label = DOC_TYPE_LABELS.get(result.get("document_type", "other"), result.get("document_type", "other"))
    result["label"] = label

    return JSONResponse(content=result)


@router.get("/pending")
async def list_pending_documents(
    office_id: str,
    x_internal_token: Optional[str] = Header(None, alias="X-Internal-Token"),
):
    """List documents received but not yet attached to a case."""
    if x_internal_token != INTERNAL_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if db is None:
        return []

    docs = await db.document_uploads.find(
        {"office_id": office_id, "attached_to_case": None},
        {"_id": 0, "doc_id": 1, "original_filename": 1, "identification": 1, "created_at": 1},
    ).sort("created_at", -1).to_list(length=50)

    return docs
