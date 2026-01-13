import base64
import logging
import mimetypes
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from core.auth import get_current_user
from core.database import db
from models.documents import DocumentStatus, DocumentType, DocumentUpdate, UserDocument
from services.cases import update_case_status_and_progress
from services.documents import analyze_document_with_ai, determine_document_priority, validate_file_type

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/case/{case_id}/upload-document")
async def upload_document_to_case(
    case_id: str,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    description: Optional[str] = Form(None),
):
    """
    Upload de documento para um caso específico - SEM AUTENTICAÇÃO (para testes)
    """
    try:
        case = await db.application_cases.find_one({"case_id": case_id})
        if not case:
            case = await db.auto_cases.find_one({"case_id": case_id})

        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")

        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")

        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")

        content_base64 = base64.b64encode(content).decode("utf-8")
        mime_type = file.content_type or "application/octet-stream"

        doc_id = str(uuid.uuid4())
        document_record = {
            "id": doc_id,
            "case_id": case_id,
            "filename": file.filename,
            "document_type": document_type,
            "description": description,
            "content_base64": content_base64,
            "mime_type": mime_type,
            "file_size": len(content),
            "uploaded_at": datetime.now(timezone.utc),
            "status": "uploaded",
        }

        result = await db.application_cases.update_one(
            {"case_id": case_id},
            {"$push": {"documents": document_record, "uploaded_documents": document_record}, "$set": {"updated_at": datetime.now(timezone.utc)}},
        )

        if result.matched_count == 0:
            await db.auto_cases.update_one(
                {"case_id": case_id},
                {"$push": {"documents": document_record, "uploaded_documents": document_record}, "$set": {"updated_at": datetime.now(timezone.utc)}},
            )

        logger.info(f"✅ Document uploaded: {file.filename} ({len(content)} bytes) - Type: {document_type}")

        extraction_result = None
        try:
            from document_data_extractor import process_document_and_update_user
            from google_document_ai_integration import GoogleDocumentAIProcessor

            doc_processor = GoogleDocumentAIProcessor()
            ocr_result = await doc_processor.process_document(
                file_content=content, filename=file.filename, mime_type=mime_type
            )

            if ocr_result.get("success") and ocr_result.get("extracted_text"):
                user_id = case.get("user_id") or case.get("applicant_email")
                if user_id:
                    extraction_result = await process_document_and_update_user(
                        document_text=ocr_result["extracted_text"],
                        document_type=document_type,
                        user_id=user_id,
                        db=db,
                    )

                    if extraction_result.get("auto_corrected"):
                        logger.info(f"🔄 User data auto-corrected based on {document_type}")
                        logger.info(f"📝 Corrections: {extraction_result.get('corrections_made')}")

        except Exception as extract_error:
            logger.warning(f"⚠️ Document extraction/correction failed: {str(extract_error)}")

        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            case = await db.application_cases.find_one({"case_id": case_id})

        if case:
            doc_count = len(case.get("uploaded_documents", []))
            if doc_count >= 3:
                collection_name = "auto_cases" if case.get("session_token") else "application_cases"
                await update_case_status_and_progress(case_id, "documents_uploaded", collection_name)

        response_data = {
            "success": True,
            "message": "Document uploaded successfully",
            "document_id": doc_id,
            "case_id": case_id,
            "filename": file.filename,
            "document_type": document_type,
            "file_size": len(content),
        }

        if extraction_result:
            response_data["extraction"] = {
                "successful": extraction_result.get("extraction_successful", False),
                "auto_corrected": extraction_result.get("auto_corrected", False),
                "corrections_made": extraction_result.get("corrections_made"),
                "message": extraction_result.get("message"),
            }

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro no upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    tags: str = Form(""),
    expiration_date: Optional[str] = Form(None),
    issue_date: Optional[str] = Form(None),
    current_user=Depends(get_current_user),
):
    """Upload a document with sistema analysis."""
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")

        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")

        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")

        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        if not validate_file_type(mime_type):
            raise HTTPException(status_code=400, detail="Unsupported file type")

        content_base64 = base64.b64encode(content).decode("utf-8")

        exp_date = None
        iss_date = None
        try:
            if expiration_date:
                exp_date = datetime.fromisoformat(expiration_date.replace("Z", "+00:00"))
            if issue_date:
                iss_date = datetime.fromisoformat(issue_date.replace("Z", "+00:00"))
        except ValueError:
            pass

        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

        priority = determine_document_priority(document_type, exp_date)

        document = UserDocument(
            user_id=current_user["id"],
            filename=f"{document_type}_{uuid.uuid4().hex[:8]}_{file.filename}",
            original_filename=file.filename,
            document_type=document_type,
            content_base64=content_base64,
            mime_type=mime_type,
            file_size=len(content),
            expiration_date=exp_date,
            issue_date=iss_date,
            priority=priority,
            tags=tag_list,
        )

        await db.documents.insert_one(document.dict())

        try:
            ai_analysis = await analyze_document_with_ai(document)

            suggestions = ai_analysis.get("suggestions", [])
            status = (
                DocumentStatus.approved
                if ai_analysis.get("validity_status") == "valid"
                else DocumentStatus.requires_improvement
            )

            await db.documents.update_one(
                {"id": document.id},
                {
                    "$set": {
                        "ai_analysis": ai_analysis,
                        "ai_suggestions": suggestions,
                        "status": status.value,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )

        except Exception as ai_error:
            logger.error(f"sistema analysis failed: {str(ai_error)}")

        return {
            "message": "Document uploaded successfully",
            "document_id": document.id,
            "filename": document.filename,
            "status": "uploaded",
            "ai_analysis_status": "completed",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/documents")
async def get_user_documents(current_user=Depends(get_current_user)):
    """Get all user documents."""
    try:
        documents = (
            await db.documents.find({"user_id": current_user["id"]}, {"_id": 0, "content_base64": 0})
            .sort("created_at", -1)
            .to_list(100)
        )

        total_docs = len(documents)
        approved_docs = len([doc for doc in documents if doc.get("status") == "approved"])
        expired_docs = len([doc for doc in documents if doc.get("status") == "expired"])
        pending_docs = len([doc for doc in documents if doc.get("status") == "pending_review"])

        upcoming_expirations = []
        now = datetime.now(timezone.utc)
        for doc in documents:
            exp_date = doc.get("expiration_date")
            if exp_date:
                if isinstance(exp_date, str):
                    exp_date = datetime.fromisoformat(exp_date.replace("Z", "+00:00"))
                days_to_expire = (exp_date - now).days
                if 0 <= days_to_expire <= 90:
                    upcoming_expirations.append(
                        {
                            "document_id": doc["id"],
                            "document_type": doc["document_type"],
                            "filename": doc["original_filename"],
                            "expiration_date": exp_date.isoformat(),
                            "days_to_expire": days_to_expire,
                        }
                    )

        upcoming_expirations.sort(key=lambda x: x["days_to_expire"])

        return {
            "documents": documents,
            "stats": {
                "total": total_docs,
                "approved": approved_docs,
                "expired": expired_docs,
                "pending": pending_docs,
                "completion_rate": int((approved_docs / total_docs * 100)) if total_docs > 0 else 0,
            },
            "upcoming_expirations": upcoming_expirations[:10],
        }

    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting documents: {str(e)}")


@router.get("/documents/validation-capabilities")
async def get_validation_capabilities(current_user=Depends(get_current_user)):
    """Get information about available validation capabilities."""
    try:
        return {
            "status": "success",
            "capabilities": {
                "phase_2_features": {
                    "enhanced_field_extraction": True,
                    "translation_gate": True,
                    "advanced_regex_patterns": True,
                    "high_precision_validators": True,
                    "language_detection": True,
                },
                "phase_3_features": {
                    "auto_document_classification": True,
                    "cross_document_consistency": True,
                    "multi_document_validation": True,
                    "advanced_ocr_integration": True,
                    "comprehensive_scoring": True,
                },
                "supported_document_types": [
                    "PASSPORT_ID_PAGE",
                    "BIRTH_CERTIFICATE",
                    "MARRIAGE_CERT",
                    "DEGREE_CERTIFICATE",
                    "EMPLOYMENT_OFFER_LETTER",
                    "I797_NOTICE",
                    "I94_RECORD",
                    "PAY_STUB",
                    "TAX_RETURN_1040",
                    "TRANSLATION_CERTIFICATE",
                ],
                "supported_languages": ["english", "portuguese", "spanish"],
                "validation_engines": {
                    "policy_engine": "Enhanced YAML-based validation",
                    "field_extractor": "Advanced regex with ML validation",
                    "translation_gate": "Language detection and requirements",
                    "consistency_engine": "Cross-document verification",
                    "document_classifier": "sistema-powered type detection",
                },
            },
            "version": "2.0.0-phase3",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting validation capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")


@router.get("/documents/{document_id}")
async def get_document_details(document_id: str, current_user=Depends(get_current_user)):
    """Get document details including sistema analysis."""
    try:
        document = await db.documents.find_one({"id": document_id, "user_id": current_user["id"]}, {"_id": 0})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return document

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting document details: {str(e)}")


@router.put("/documents/{document_id}")
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    current_user=Depends(get_current_user),
):
    """Update document information."""
    try:
        document = await db.documents.find_one({"id": document_id, "user_id": current_user["id"]})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        update_dict = update_data.dict(exclude_unset=True)

        if "expiration_date" in update_dict and update_dict["expiration_date"]:
            try:
                update_dict["expiration_date"] = datetime.fromisoformat(
                    update_dict["expiration_date"].replace("Z", "+00:00")
                )
            except ValueError:
                del update_dict["expiration_date"]

        if "issue_date" in update_dict and update_dict["issue_date"]:
            try:
                update_dict["issue_date"] = datetime.fromisoformat(
                    update_dict["issue_date"].replace("Z", "+00:00")
                )
            except ValueError:
                del update_dict["issue_date"]

        update_dict["updated_at"] = datetime.now(timezone.utc)

        await db.documents.update_one({"id": document_id}, {"$set": update_dict})

        updated_doc = await db.documents.find_one({"id": document_id}, {"_id": 0})
        return {"message": "Document updated successfully", "document": updated_doc}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating document: {str(e)}")


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, current_user=Depends(get_current_user)):
    """Delete a document."""
    try:
        document = await db.documents.find_one({"id": document_id, "user_id": current_user["id"]})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        await db.documents.delete_one({"id": document_id})

        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@router.post("/documents/{document_id}/reanalyze")
async def reanalyze_document(document_id: str, current_user=Depends(get_current_user)):
    """Reanalyze document with sistema."""
    try:
        document_data = await db.documents.find_one({"id": document_id, "user_id": current_user["id"]})
        if not document_data:
            raise HTTPException(status_code=404, detail="Document not found")

        document = UserDocument(**document_data)
        ai_analysis = await analyze_document_with_ai(document)

        suggestions = ai_analysis.get("suggestions", [])
        status = (
            DocumentStatus.approved
            if ai_analysis.get("validity_status") == "valid"
            else DocumentStatus.requires_improvement
        )

        await db.documents.update_one(
            {"id": document_id},
            {"$set": {"ai_analysis": ai_analysis, "ai_suggestions": suggestions, "status": status.value, "updated_at": datetime.now(timezone.utc)}},
        )

        return {"message": "Document reanalyzed successfully", "analysis": ai_analysis, "status": status.value}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reanalyzing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reanalyzing document: {str(e)}")
