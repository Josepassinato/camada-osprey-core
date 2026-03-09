"""
Filing Packages API for Imigrai B2B
Generates complete USCIS filing packages (ZIP) with form, cover letter, checklist, and summary.
"""

import io
import logging
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from backend.core.database import db
from backend.b2b_auth_api import get_b2b_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/packages", tags=["packages"])

DOWNLOADS_DIR = Path("/var/www/visa-application/osprey-core/downloads/packages")


class GeneratePackageRequest(BaseModel):
    include_cover_letter: Optional[bool] = True
    include_checklist: Optional[bool] = True
    include_summary: Optional[bool] = True
    special_instructions: Optional[str] = None


# ── Filing info by visa type ──────────────────────────────────────────────

FILING_INFO = {
    "H-1B": {
        "form": "I-129",
        "office": "USCIS Vermont Service Center",
        "address": "75 Lower Welden Street, St. Albans, VT 05479-0001",
        "fee": "$555 + $500 Anti-Fraud + $750/$1,500 ACWIA",
        "premium": "$2,805 (optional, 15 calendar days)",
        "processing": "2-4 months (regular)",
    },
    "O-1": {
        "form": "I-129",
        "office": "USCIS Vermont or California Service Center",
        "address": "75 Lower Welden Street, St. Albans, VT 05479-0001",
        "fee": "$555",
        "premium": "$2,805 (optional, 15 calendar days)",
        "processing": "2-4 months (regular)",
    },
    "L-1": {
        "form": "I-129",
        "office": "USCIS Vermont Service Center",
        "address": "75 Lower Welden Street, St. Albans, VT 05479-0001",
        "fee": "$555 + $500 Anti-Fraud",
        "premium": "$2,805 (optional, 15 calendar days)",
        "processing": "2-4 months (regular)",
    },
    "EB-1A": {
        "form": "I-140",
        "office": "USCIS Texas or Nebraska Service Center",
        "address": "Check USCIS website for current filing address",
        "fee": "$700",
        "premium": "$2,805 (optional, 15 business days)",
        "processing": "4-8 months (regular)",
    },
    "I-539": {
        "form": "I-539",
        "office": "USCIS Lockbox",
        "address": "USCIS, P.O. Box 660166, Dallas, TX 75266",
        "fee": "$370",
        "premium": "Not available",
        "processing": "3-6 months",
    },
}

REQUIRED_DOCS = {
    "H-1B": [
        ("Formulário I-129 preenchido e assinado", True),
        ("Labor Condition Application (LCA) certificada pelo DOL", True),
        ("Diploma de ensino superior (cópia autenticada)", True),
        ("Histórico acadêmico (tradução certificada)", True),
        ("Carta de oferta de emprego / job description", True),
        ("Currículo atualizado do beneficiário", True),
        ("Cópia do passaporte (válido 6+ meses)", True),
        ("Evidência de qualificações profissionais", True),
        ("Organograma da empresa", False),
        ("Últimos 3 contracheques (se já nos EUA)", False),
        ("Cópia do I-94 (se já nos EUA)", False),
        ("Cheque/money order para U.S. DHS", True),
    ],
    "O-1": [
        ("Formulário I-129 preenchido e assinado", True),
        ("Carta de suporte do agente/empregador", True),
        ("Evidência de habilidade extraordinária (8+ critérios)", True),
        ("Itinerário de eventos/trabalho", True),
        ("Cópia do passaporte (válido 6+ meses)", True),
        ("Currículo detalhado", True),
        ("Cartas de recomendação de especialistas", True),
        ("Advisory opinion do sindicato/peer group", True),
        ("Contratos de trabalho", False),
        ("Prêmios e reconhecimentos", False),
    ],
    "L-1": [
        ("Formulário I-129 preenchido e assinado", True),
        ("Carta de transferência da empresa", True),
        ("Evidência de vínculo com empresa estrangeira (1+ ano)", True),
        ("Cópia do passaporte (válido 6+ meses)", True),
        ("Organograma das duas entidades", True),
        ("Evidência de relação entre empresas", True),
        ("Descrição detalhada do cargo", True),
    ],
    "EB-1A": [
        ("Formulário I-140 preenchido e assinado", True),
        ("Evidência de habilidade extraordinária (3+ critérios)", True),
        ("Cartas de recomendação", True),
        ("Cópia do passaporte (válido 6+ meses)", True),
        ("Currículo detalhado", True),
        ("Publicações, citações, prêmios", False),
    ],
}


def _get_filing_info(visa_type: str) -> dict:
    """Get filing info, normalizing visa type."""
    vt = visa_type.upper().replace("H1B", "H-1B").replace("O1", "O-1").replace("L1", "L-1")
    for key in FILING_INFO:
        if key in vt:
            return FILING_INFO[key]
    return FILING_INFO.get(vt, {
        "form": visa_type,
        "office": "USCIS — check website",
        "address": "See USCIS.gov for filing address",
        "fee": "Check USCIS fee schedule",
        "processing": "Varies",
    })


def _get_required_docs(visa_type: str) -> list:
    vt = visa_type.upper().replace("H1B", "H-1B").replace("O1", "O-1").replace("L1", "L-1")
    for key in REQUIRED_DOCS:
        if key in vt:
            return REQUIRED_DOCS[key]
    return REQUIRED_DOCS.get(vt, [])


def _build_checklist(case: dict) -> str:
    """Build document checklist text."""
    visa = case.get("visa_type") or case.get("form_code") or "Unknown"
    docs = _get_required_docs(visa)
    basic = case.get("basic_data", {})
    client = case.get("client_name") or basic.get("beneficiary", {}).get("full_name", "")
    case_id = case.get("case_id", "")

    lines = [
        "=" * 60,
        "DOCUMENT CHECKLIST",
        f"Case: {case_id} — {client}",
        f"Visa Type: {visa}",
        f"Generated: {datetime.now(timezone.utc).strftime('%m/%d/%Y')}",
        "=" * 60,
        "",
    ]

    if docs:
        lines.append("REQUIRED DOCUMENTS:")
        lines.append("-" * 40)
        for i, (doc, required) in enumerate(docs, 1):
            marker = "[  ]" if required else "[  ] (optional)"
            lines.append(f"  {i:2d}. {marker} {doc}")
        lines.append("")

    # Check which documents the case already has
    existing = case.get("documents", [])
    if existing:
        lines.append("DOCUMENTS ON FILE:")
        lines.append("-" * 40)
        for d in existing:
            name = d.get("name") or d.get("document_type", "Unknown")
            lines.append(f"  ✓ {name}")
        lines.append("")

    info = _get_filing_info(visa)
    lines.extend([
        "FILING INFORMATION:",
        "-" * 40,
        f"  Form: {info.get('form', visa)}",
        f"  Filing Office: {info.get('office', 'N/A')}",
        f"  Address: {info.get('address', 'N/A')}",
        f"  Filing Fee: {info.get('fee', 'N/A')}",
        f"  Premium Processing: {info.get('premium', 'N/A')}",
        f"  Processing Time: {info.get('processing', 'N/A')}",
        "",
        "IMPORTANT NOTES:",
        "-" * 40,
        "  • All documents must be in English or accompanied by certified translations",
        "  • Include a cover letter listing all enclosed documents",
        "  • Make copies of everything before mailing",
        "  • Send via trackable courier (USPS Priority, FedEx, UPS)",
        "  • Keep the tracking number for your records",
    ])

    return "\n".join(lines)


def _build_summary(case: dict) -> str:
    """Build case summary text."""
    basic = case.get("basic_data", {})
    beneficiary = basic.get("beneficiary", {})
    employer = basic.get("employer", {})
    position = basic.get("position", {})
    case_info = basic.get("case", {})

    visa = case.get("visa_type") or case.get("form_code") or "Unknown"
    client = case.get("client_name") or beneficiary.get("full_name", "")

    lines = [
        "=" * 60,
        "CASE SUMMARY",
        f"Case ID: {case.get('case_id', '')}",
        f"Generated: {datetime.now(timezone.utc).strftime('%m/%d/%Y %H:%M UTC')}",
        "=" * 60,
        "",
        "BENEFICIARY:",
        f"  Name: {client}",
        f"  Date of Birth: {beneficiary.get('date_of_birth', 'N/A')}",
        f"  Country of Birth: {beneficiary.get('country_of_birth', 'N/A')}",
        f"  Citizenship: {beneficiary.get('citizenship', 'N/A')}",
        f"  Passport: {beneficiary.get('passport_number', 'N/A')}",
        "",
        "PETITIONER / EMPLOYER:",
        f"  Company: {employer.get('company_name', 'N/A')}",
        f"  EIN: {employer.get('ein', 'N/A')}",
        f"  Address: {employer.get('address', 'N/A')}",
        "",
        "POSITION:",
        f"  Job Title: {position.get('job_title', 'N/A')}",
        f"  Salary: {position.get('salary', 'N/A')}",
        f"  LCA #: {position.get('lca_number', 'N/A')}",
        f"  Start Date: {position.get('start_date', 'N/A')}",
        f"  End Date: {position.get('end_date', 'N/A')}",
        "",
        "CASE DETAILS:",
        f"  Visa Type: {visa}",
        f"  Status: {case.get('status', 'N/A')}",
        f"  Priority: {case.get('priority', 'N/A')}",
        f"  Created: {case.get('created_at', 'N/A')}",
    ]

    # Notes
    notes = case.get("notes", [])
    if notes:
        lines.extend(["", "NOTES:"])
        for n in notes[-5:]:  # last 5 notes
            ts = n.get("timestamp", "")
            text = n.get("text", "")
            lines.append(f"  [{ts}] {text}")

    return "\n".join(lines)


@router.post("/{case_id}/generate")
async def generate_package(
    case_id: str,
    body: GeneratePackageRequest = GeneratePackageRequest(),
    current_user: dict = Depends(get_b2b_user),
):
    """Generate a complete USCIS filing package (ZIP) for a B2B case."""
    office_id = current_user["office_id"]

    case = await db.b2b_cases.find_one(
        {"case_id": case_id, "office_id": office_id}, {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    visa_type = (case.get("visa_type") or case.get("form_code") or "").upper()
    client_name = case.get("client_name", "client")
    safe_name = client_name.replace(" ", "_")

    zip_buffer = io.BytesIO()
    files_included = []

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Form PDF — try to generate
        try:
            from backend.forms.filler import form_filler

            pdf_bytes = None
            form_name = visa_type

            if visa_type in {"H-1B", "H1B"}:
                pdf_bytes = form_filler.fill_h1b(case)
                form_name = "I-129_H-1B"
            elif visa_type in {"O-1", "O1"}:
                pdf_bytes = form_filler.fill_o1(case)
                form_name = "I-129_O-1"
            elif visa_type in {"L-1", "L1"}:
                pdf_bytes = form_filler.fill_l1(case)
                form_name = "I-129_L-1"
            elif visa_type in {"EB-1A", "EB1A", "I-140"}:
                pdf_bytes = form_filler.fill_i140(case)
                form_name = "I-140"
            elif visa_type == "I-539" or "B-" in visa_type:
                pdf_bytes = form_filler.fill_i539(case)
                form_name = "I-539"
            elif visa_type == "I-589":
                pdf_bytes = form_filler.fill_i589(case)
                form_name = "I-589"
            elif visa_type in {"F-1", "F1"}:
                pdf_bytes = form_filler.fill_f1(case)
                form_name = "I-539_F-1"

            if pdf_bytes:
                fname = f"{form_name}_{safe_name}.pdf"
                zf.writestr(fname, pdf_bytes)
                files_included.append({"name": fname, "type": "uscis_form"})
                logger.info(f"📄 Added form PDF: {fname} ({len(pdf_bytes)} bytes)")
        except Exception as e:
            logger.warning(f"⚠️ Could not generate form PDF: {e}")

        # 2. Cover letter
        if body.include_cover_letter:
            try:
                from letter_generator import LetterGenerator

                office = await db.offices.find_one({"office_id": office_id})
                case["office_name"] = office["name"] if office else "Immigration Law Office"
                content = await LetterGenerator.generate_cover_letter(
                    case, "initial_filing", body.special_instructions or ""
                )
                fname = f"Cover_Letter_{safe_name}.txt"
                zf.writestr(fname, content)
                files_included.append({"name": fname, "type": "cover_letter"})
                logger.info(f"📄 Added cover letter: {fname}")
            except Exception as e:
                logger.warning(f"⚠️ Could not generate cover letter: {e}")

        # 3. Document checklist
        if body.include_checklist:
            checklist = _build_checklist(case)
            fname = f"Document_Checklist_{safe_name}.txt"
            zf.writestr(fname, checklist)
            files_included.append({"name": fname, "type": "checklist"})

        # 4. Case summary
        if body.include_summary:
            summary = _build_summary(case)
            fname = f"Case_Summary_{safe_name}.txt"
            zf.writestr(fname, summary)
            files_included.append({"name": fname, "type": "summary"})

    zip_bytes = zip_buffer.getvalue()

    # Save to disk
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    pkg_id = "PKG-" + str(uuid.uuid4())[:8].upper()
    zip_filename = f"{pkg_id}_{safe_name}.zip"
    zip_path = DOWNLOADS_DIR / zip_filename

    with open(zip_path, "wb") as f:
        f.write(zip_bytes)

    # Update case in DB
    now = datetime.now(timezone.utc)
    await db.b2b_cases.update_one(
        {"case_id": case_id, "office_id": office_id},
        {
            "$set": {
                "package_generated": True,
                "package_id": pkg_id,
                "package_path": str(zip_path),
                "package_generated_at": now,
                "updated_at": now,
            },
            "$push": {
                "history": {
                    "action": "package_generated",
                    "timestamp": now.isoformat(),
                    "detail": f"Filing package generated: {len(files_included)} files",
                }
            },
        },
    )

    logger.info(
        f"✅ Package {pkg_id} generated for case {case_id}: "
        f"{len(files_included)} files, {len(zip_bytes)} bytes"
    )

    return {
        "success": True,
        "package_id": pkg_id,
        "case_id": case_id,
        "client_name": client_name,
        "visa_type": visa_type,
        "files": files_included,
        "total_files": len(files_included),
        "size_bytes": len(zip_bytes),
        "download_url": f"/api/packages/{case_id}/download",
    }


@router.get("/{case_id}/download")
async def download_package(case_id: str, current_user: dict = Depends(get_b2b_user)):
    """Download a previously generated filing package ZIP."""
    office_id = current_user["office_id"]

    case = await db.b2b_cases.find_one(
        {"case_id": case_id, "office_id": office_id},
        {"_id": 0, "package_path": 1, "package_id": 1, "client_name": 1},
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    pkg_path = case.get("package_path")
    if not pkg_path or not Path(pkg_path).exists():
        raise HTTPException(
            status_code=404,
            detail="Package not generated yet. Call POST /api/packages/{case_id}/generate first.",
        )

    zip_bytes = Path(pkg_path).read_bytes()
    safe_name = (case.get("client_name") or "package").replace(" ", "_")
    filename = f"{case.get('package_id', 'PKG')}_{safe_name}.zip"

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(zip_bytes)),
        },
    )
