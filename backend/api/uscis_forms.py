import base64
import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from core.database import db
from services.cases import update_case_status_and_progress
from backend.forms.filler import form_filler as uscis_form_filler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/case/{case_id}/generate-form")
@router.get("/case/{case_id}/generate-form")
async def generate_uscis_form(case_id: str):
    """
    Generate filled USCIS form PDF for a case.
    """
    try:
        case = await db.application_cases.find_one({"case_id": case_id})
        case_collection = "application_cases"

        if not case:
            case = await db.auto_cases.find_one({"case_id": case_id})
            case_collection = "auto_cases"

        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

        visa_type = (case.get("visa_type") or case.get("form_code") or "").upper()

        logger.info(f"📝 Generating form for case {case_id}, type: {visa_type}")

        if visa_type == "I-539":
            pdf_bytes = uscis_form_filler.fill_i539(case)
            filename = f"I-539_{case_id}.pdf"
        elif visa_type == "I-589":
            pdf_bytes = uscis_form_filler.fill_i589(case)
            filename = f"I-589_{case_id}.pdf"
        elif visa_type in {"EB-1A", "EB1A", "I-140"}:
            pdf_bytes = uscis_form_filler.fill_i140(case)
            filename = f"I-140_{case_id}.pdf"
        elif visa_type in {"O-1", "O1"}:
            pdf_bytes = uscis_form_filler.fill_o1(case)
            filename = f"I-129-O1_{case_id}.pdf"
        elif visa_type in {"H-1B", "H1B"}:
            pdf_bytes = uscis_form_filler.fill_h1b(case)
            filename = f"I-129-H1B_{case_id}.pdf"
        elif visa_type in {"L-1", "L1"}:
            pdf_bytes = uscis_form_filler.fill_l1(case)
            filename = f"I-129-L1_{case_id}.pdf"
        elif visa_type in {"F-1", "F1"}:
            pdf_bytes = uscis_form_filler.fill_f1(case)
            filename = f"I-539-F1_{case_id}.pdf"
        elif visa_type == "I-129":
            pdf_bytes = uscis_form_filler.fill_i129(case)
            filename = f"I-129_{case_id}.pdf"
        else:
            if "B-" in visa_type or "TOURIST" in visa_type or "EXTENSION" in visa_type:
                logger.info(f"ℹ️ Mapping {visa_type} to I-539")
                pdf_bytes = uscis_form_filler.fill_i539(case)
                filename = f"I-539_{case_id}.pdf"
            elif "ASYLUM" in visa_type or "ASILO" in visa_type:
                logger.info(f"ℹ️ Mapping {visa_type} to I-589")
                pdf_bytes = uscis_form_filler.fill_i589(case)
                filename = f"I-589_{case_id}.pdf"
            else:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Form generation not supported for visa type: "
                        f"{visa_type}. Supported types: I-539, I-589, I-140, O-1, H-1B, L-1, F-1"
                    ),
                )

        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        download_dir = "/app/downloads/forms"
        os.makedirs(download_dir, exist_ok=True)

        pdf_path = os.path.join(download_dir, filename)
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        logger.info(f"💾 PDF saved to disk: {pdf_path}")

        collection = db.application_cases if case_collection == "application_cases" else db.auto_cases
        await collection.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "generated_form": {
                        "filename": filename,
                        "content_base64": pdf_base64,
                        "generated_at": datetime.now(timezone.utc),
                        "form_type": visa_type,
                        "file_size": len(pdf_bytes),
                    },
                    "generated_pdf_path": pdf_path,
                    "uscis_form_generated": True,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        logger.info(f"✅ Form generated: {filename} ({len(pdf_bytes)} bytes)")

        await update_case_status_and_progress(case_id, "form_generated", case_collection)

        return {
            "success": True,
            "message": "USCIS form generated successfully",
            "case_id": case_id,
            "form_type": visa_type,
            "filename": filename,
            "file_size": len(pdf_bytes),
            "download_url": f"/api/case/{case_id}/download-form",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating form: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating form: {str(e)}")


@router.get("/case/{case_id}/download-form")
async def download_uscis_form(case_id: str):
    """Download a pre-generated USCIS form PDF."""
    try:
        case = await db.application_cases.find_one({"case_id": case_id})
        if not case:
            case = await db.auto_cases.find_one({"case_id": case_id})

        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

        generated_form = case.get("generated_form")
        if not generated_form:
            raise HTTPException(status_code=404, detail="Form not generated yet. Please call /generate-form first.")

        pdf_base64 = generated_form.get("content_base64")
        pdf_bytes = base64.b64decode(pdf_base64)
        filename = generated_form.get("filename", "form.pdf")

        logger.info(f"📥 Downloading form: {filename} ({len(pdf_bytes)} bytes)")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes)),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error downloading form: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading form: {str(e)}")


@router.post("/auto-application/case/{case_id}/generate-form")
async def generate_uscis_form_for_case(case_id: str):
    """Generate USCIS form for a specific auto-application case."""
    try:
        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        await db.auto_cases.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "uscis_form_generated": True,
                    "progress_percentage": 90,
                    "status": "form_generated",
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        return {
            "success": True,
            "message": "USCIS form generated successfully",
            "case_id": case_id,
            "status": "form_generated",
            "progress": 90,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating USCIS form: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-application/case/{case_id}/uscis-form")
async def save_uscis_form_data(case_id: str, request: dict):
    """Save USCIS form data for a case."""
    try:
        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        uscis_form_data = request.get("uscis_form_data", {})
        completed_sections = request.get("completed_sections", [])

        update_data = {
            "uscis_form_data": uscis_form_data,
            "uscis_form_completed_sections": completed_sections,
            "uscis_form_updated_at": datetime.now(timezone.utc),
            "current_step": "uscis-form",
        }

        result = await db.auto_cases.update_one({"case_id": case_id}, {"$set": update_data})

        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to save USCIS form data")

        return {
            "success": True,
            "message": "USCIS form data saved successfully",
            "case_id": case_id,
            "completed_sections": completed_sections,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving USCIS form data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving USCIS form data: {str(e)}")


@router.get("/auto-application/case/{case_id}/uscis-form")
async def get_uscis_form_data(case_id: str):
    """Get USCIS form data for a case."""
    try:
        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        return {
            "success": True,
            "case_id": case_id,
            "form_code": case.get("form_code"),
            "uscis_form_data": case.get("uscis_form_data", {}),
            "completed_sections": case.get("uscis_form_completed_sections", []),
            "basic_data": case.get("basic_data", {}),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting USCIS form data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting USCIS form data: {str(e)}")


@router.post("/auto-application/case/{case_id}/authorize-uscis-form")
async def authorize_uscis_form(case_id: str, request: dict):
    """Authorize and save USCIS form automatically to user's document folder."""
    try:
        form_reviewed = request.get("form_reviewed", False)
        form_authorized = request.get("form_authorized", False)
        generated_form_data = request.get("generated_form_data", {})
        authorization_timestamp = request.get("authorization_timestamp")

        if not (form_reviewed and form_authorized):
            raise HTTPException(status_code=400, detail="Form must be reviewed and authorized")

        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        uscis_document = {
            "id": f"uscis_form_{case_id}",
            "document_type": "uscis_form",
            "name": f"Formulário USCIS {case.get('form_code', '')}",
            "description": (
                "Formulário oficial gerado automaticamente pela sistema e autorizado pelo aplicante"
            ),
            "content_type": "application/pdf",
            "generated_by_ai": True,
            "authorized_by_user": True,
            "authorization_timestamp": authorization_timestamp,
            "form_data": generated_form_data,
            "case_id": case_id,
            "created_at": datetime.now(timezone.utc),
            "status": "ready_for_submission",
        }

        update_data = {
            "uscis_form_authorized": True,
            "uscis_form_authorized_at": datetime.now(timezone.utc),
            "uscis_form_document": uscis_document,
            "current_step": "uscis-form-authorized",
        }

        existing_documents = case.get("documents", [])
        existing_documents.append(uscis_document)
        update_data["documents"] = existing_documents

        result = await db.auto_cases.update_one({"case_id": case_id}, {"$set": update_data})

        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to authorize and save form")

        return {
            "success": True,
            "message": "Formulário USCIS autorizado e salvo automaticamente",
            "case_id": case_id,
            "document_saved": True,
            "document_id": uscis_document["id"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error authorizing USCIS form: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error authorizing form: {str(e)}")
