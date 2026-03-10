"""
Claude Agents API — Endpoints for Claude-powered specialized agents.

Agents:
- POST /api/agents/carlos/analyze       — Eligibility analysis
- POST /api/agents/miguel/review        — Document review
- POST /api/agents/patricia/advise      — Strategy & compliance
- POST /api/agents/ricardo/letter       — Letter writing (on-demand)
- POST /api/agents/comprehensive-analysis — Carlos → Miguel → Patricia pipeline

All endpoints accept either:
  - {"case_id": "..."} to auto-fetch from MongoDB
  - {"case_data": {...}, "visa_type": "..."} for direct data
"""

import logging
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from backend.llm.claude_client import ClaudeClient
from backend.core.database import db
from backend.agents.claude import (
    CarlosEligibilityAgent,
    MiguelDocumentAgent,
    PatriciaStrategyAgent,
    RicardoLetterAgent,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["claude-agents"])

# Shared Claude client (singleton per process)
_claude_client: Optional[ClaudeClient] = None


def get_claude_client() -> ClaudeClient:
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client


# ── HELPER: Fetch case from MongoDB ──────────────────────────────

async def _resolve_case(case_id: Optional[str], case_data: Optional[dict], visa_type: Optional[str]) -> tuple:
    """
    Resolve case data from case_id (MongoDB lookup) or direct case_data.
    Returns (case_data_dict, visa_type_str, office_name_str).
    """
    if case_data and visa_type:
        return case_data, visa_type, case_data.get("office_name", "este escritório")

    if not case_id:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'case_id' to fetch from database, or 'case_data' + 'visa_type' directly."
        )

    case = await db.b2b_cases.find_one({"case_id": case_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found in database.")

    resolved_visa = visa_type or case.get("visa_type", "")
    if not resolved_visa:
        raise HTTPException(status_code=400, detail=f"Case '{case_id}' has no visa_type set.")

    # Flatten case into a dict suitable for agents
    basic = case.get("basic_data", {})
    quals = case.get("qualifications", {})
    resolved_data = {
        **basic,
        **quals,
        "client_name": case.get("client_name", basic.get("full_name", "")),
        "documents_received": case.get("documents_received", []),
        "documents_required": case.get("documents_required", []),
        "notes": case.get("notes", []),
        "case_id": case_id,
        "status": case.get("status", ""),
        "priority": case.get("priority", ""),
        "deadline": case.get("deadline", ""),
    }

    # Fetch office name
    office_id = case.get("office_id")
    office_name = "este escritório"
    if office_id:
        office = await db.b2b_users.find_one({"office_id": office_id}, {"firm_name": 1})
        if office and office.get("firm_name"):
            office_name = office["firm_name"]

    return resolved_data, resolved_visa, office_name


# ── REQUEST SCHEMAS ──────────────────────────────────────────────

class CaseAnalysisRequest(BaseModel):
    case_id: Optional[str] = None
    case_data: Optional[dict] = Field(default=None, description="Case data (client info, docs, notes)")
    visa_type: Optional[str] = Field(default=None, description="Target visa type (H-1B, EB-1A, etc.)")
    office_name: Optional[str] = Field(default=None, description="Law firm name")


class LetterRequest(BaseModel):
    case_id: Optional[str] = None
    case_data: Optional[dict] = Field(default=None, description="Case data")
    visa_type: Optional[str] = Field(default=None, description="Target visa type")
    letter_type: str = Field(default="cover_letter", description="cover_letter, support_letter, rfe_response, etc.")
    additional_instructions: Optional[str] = None
    office_name: Optional[str] = Field(default=None)


# ── INDIVIDUAL AGENT ENDPOINTS ───────────────────────────────────

@router.post("/carlos/analyze")
async def carlos_analyze(req: CaseAnalysisRequest):
    """Dr. Carlos — Eligibility analysis for a case."""
    case_data, visa_type, office_name = await _resolve_case(
        req.case_id, req.case_data, req.visa_type
    )
    if req.office_name:
        office_name = req.office_name

    client = get_claude_client()
    carlos = CarlosEligibilityAgent(claude_client=client)

    result = await carlos.analyze(
        case_data=case_data,
        visa_type=visa_type,
        office_name=office_name,
    )

    if "error" in result and not result.get("eligible"):
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.post("/miguel/review")
async def miguel_review(req: CaseAnalysisRequest):
    """Dr. Miguel — Document completeness review."""
    case_data, visa_type, office_name = await _resolve_case(
        req.case_id, req.case_data, req.visa_type
    )
    if req.office_name:
        office_name = req.office_name

    client = get_claude_client()
    miguel = MiguelDocumentAgent(claude_client=client)

    result = await miguel.review(
        case_data=case_data,
        visa_type=visa_type,
        office_name=office_name,
    )

    if "error" in result and not result.get("ready_to_file"):
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.post("/patricia/advise")
async def patricia_advise(req: CaseAnalysisRequest):
    """
    Dra. Patricia — Strategy & compliance.
    Accepts case_id OR case_data with carlos_analysis + miguel_analysis.
    If only case_id is given, runs Carlos + Miguel first automatically.
    """
    case_data, visa_type, office_name = await _resolve_case(
        req.case_id, req.case_data, req.visa_type
    )
    if req.office_name:
        office_name = req.office_name

    carlos_analysis = case_data.pop("carlos_analysis", {})
    miguel_analysis = case_data.pop("miguel_analysis", {})

    # If no prior analyses, run Carlos + Miguel first
    if not carlos_analysis or not miguel_analysis:
        llm_client = get_claude_client()

        if not carlos_analysis:
            logger.info(f"[patricia] Running Carlos first for {visa_type}")
            carlos = CarlosEligibilityAgent(claude_client=llm_client)
            carlos_analysis = await carlos.analyze(
                case_data=case_data, visa_type=visa_type, office_name=office_name
            )

        if not miguel_analysis:
            logger.info(f"[patricia] Running Miguel first for {visa_type}")
            miguel = MiguelDocumentAgent(claude_client=llm_client)
            miguel_analysis = await miguel.review(
                case_data=case_data, visa_type=visa_type, office_name=office_name,
                carlos_analysis=carlos_analysis,
            )

    client = get_claude_client()
    patricia = PatriciaStrategyAgent(claude_client=client)

    result = await patricia.advise(
        case_data=case_data,
        visa_type=visa_type,
        carlos_analysis=carlos_analysis,
        miguel_analysis=miguel_analysis,
        office_name=office_name,
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.post("/ricardo/letter")
async def ricardo_letter(req: LetterRequest):
    """Dr. Ricardo — Write immigration letter (on-demand only)."""
    case_data, visa_type, office_name = await _resolve_case(
        req.case_id, req.case_data, req.visa_type
    )
    if req.office_name:
        office_name = req.office_name

    client = get_claude_client()
    ricardo = RicardoLetterAgent(claude_client=client)

    result = await ricardo.write_letter(
        case_data=case_data,
        letter_type=req.letter_type,
        visa_type=visa_type,
        additional_instructions=req.additional_instructions,
        office_name=office_name,
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


# ── COMPREHENSIVE ANALYSIS PIPELINE ─────────────────────────────

@router.post("/comprehensive-analysis")
async def comprehensive_analysis(req: CaseAnalysisRequest):
    """
    Full analysis pipeline: Carlos → Miguel → Patricia.

    Orchestrates three agents in sequence:
    1. Carlos analyzes eligibility
    2. Miguel reviews documents (with Carlos context)
    3. Patricia synthesizes strategy (with Carlos + Miguel context)

    Accepts either case_id or case_data + visa_type.
    Returns combined result from all three agents.
    """
    case_data, visa_type, office_name = await _resolve_case(
        req.case_id, req.case_data, req.visa_type
    )
    if req.office_name:
        office_name = req.office_name

    start_time = time.time()
    client = get_claude_client()

    # ── STEP 1: Carlos — Eligibility ─────────────────────────────
    logger.info(f"[comprehensive] Starting Carlos for {visa_type}")
    carlos = CarlosEligibilityAgent(claude_client=client)
    carlos_result = await carlos.analyze(
        case_data=case_data,
        visa_type=visa_type,
        office_name=office_name,
    )

    if "error" in carlos_result and not carlos_result.get("parse_error"):
        return {
            "pipeline": "failed",
            "failed_at": "carlos",
            "carlos": carlos_result,
            "miguel": None,
            "patricia": None,
        }

    # ── STEP 2: Miguel — Documents ───────────────────────────────
    logger.info(f"[comprehensive] Starting Miguel for {visa_type}")
    miguel = MiguelDocumentAgent(claude_client=client)
    miguel_result = await miguel.review(
        case_data=case_data,
        visa_type=visa_type,
        office_name=office_name,
        carlos_analysis=carlos_result,
    )

    if "error" in miguel_result and not miguel_result.get("parse_error"):
        return {
            "pipeline": "partial",
            "failed_at": "miguel",
            "carlos": carlos_result,
            "miguel": miguel_result,
            "patricia": None,
        }

    # ── STEP 3: Patricia — Strategy ──────────────────────────────
    logger.info(f"[comprehensive] Starting Patricia for {visa_type}")
    patricia = PatriciaStrategyAgent(claude_client=client)
    patricia_result = await patricia.advise(
        case_data=case_data,
        visa_type=visa_type,
        carlos_analysis=carlos_result,
        miguel_analysis=miguel_result,
        office_name=office_name,
    )

    total_time = time.time() - start_time

    return {
        "pipeline": "completed",
        "visa_type": visa_type,
        "case_id": req.case_id,
        "total_time_seconds": round(total_time, 2),
        "carlos": carlos_result,
        "miguel": miguel_result,
        "patricia": patricia_result,
        "verdict": patricia_result.get("verdict", "REVISAR_PRIMEIRO"),
        "summary": patricia_result.get("summary", "Análise completa disponível acima."),
    }
