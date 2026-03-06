import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.case.completeness_analyzer import CompletenessAnalyzer, CompletenessLevel
from backend.core.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

completeness_analyzer = CompletenessAnalyzer()


class CompletenessAnalysisRequest(BaseModel):
    """Request para análise de completude"""

    visa_type: str
    user_data: Dict[str, Any]
    context: Optional[str] = None


class SubmissionValidationRequest(BaseModel):
    """Request para validação de submissão"""

    case_id: str
    confirm_warnings: bool = False


@router.post("/analyze-completeness")
async def analyze_completeness(request: CompletenessAnalysisRequest):
    """Analisa completude e qualidade das informações fornecidas"""
    try:
        analysis = await completeness_analyzer.analyze_application_completeness(
            visa_type=request.visa_type,
            user_data=request.user_data,
            application_context=request.context,
        )

        return {
            "success": True,
            "analysis": analysis,
        }

    except Exception as e:
        logger.error(f"Error analyzing completeness: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing completeness: {str(e)}")


@router.get("/visa-checklist/{visa_type}")
async def get_visa_checklist(visa_type: str):
    """Retorna checklist de requisitos para um tipo de visto"""
    try:
        checklist = completeness_analyzer.get_visa_checklist(visa_type)

        if not checklist.get("success"):
            raise HTTPException(status_code=404, detail=checklist.get("message"))

        return checklist

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting visa checklist: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting checklist: {str(e)}")


@router.post("/validate-submission")
async def validate_submission(request: SubmissionValidationRequest):
    """Valida se uma aplicação está pronta para submissão"""
    try:
        case = await db.auto_cases.find_one({"id": request.case_id})

        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        visa_type = case.get("form_code")
        if not visa_type:
            raise HTTPException(status_code=400, detail="Visa type not specified in case")

        user_data = {
            "full_name": case.get("applicant_name"),
            "dob": case.get("date_of_birth"),
            "passport": case.get("passport_number"),
            "current_address": case.get("current_address"),
            "email": case.get("email"),
            "phone": case.get("phone"),
            **case.get("responses", {}),
        }

        analysis = await completeness_analyzer.analyze_application_completeness(
            visa_type=visa_type,
            user_data=user_data,
            application_context=f"Case validation for {request.case_id}",
        )

        can_submit = False
        submission_message = ""

        if analysis["level"] == CompletenessLevel.CRITICAL:
            can_submit = False
            submission_message = "❌ Esta aplicação não pode ser finalizada no estado atual. Informações críticas estão faltando."
        elif analysis["level"] == CompletenessLevel.WARNING:
            if request.confirm_warnings:
                can_submit = True
                submission_message = "⚠️ Você optou por prosseguir mesmo com avisos. Recomendamos fortemente revisar com um advogado."
            else:
                can_submit = False
                submission_message = "⚠️ Esta aplicação necessita melhorias. Você pode prosseguir assumindo os riscos, mas recomendamos completar as informações."
        else:
            can_submit = True
            submission_message = "✅ Aplicação pronta para revisão final. Recomendamos revisar com advogado antes do envio ao USCIS."

        return {
            "success": True,
            "can_submit": can_submit,
            "submission_message": submission_message,
            "analysis": analysis,
            "requires_confirmation": analysis["level"] == CompletenessLevel.WARNING
            and not request.confirm_warnings,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating submission: {e}")
        raise HTTPException(status_code=500, detail=f"Error validating submission: {str(e)}")
