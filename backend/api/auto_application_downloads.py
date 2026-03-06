import glob
import logging
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.core.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/auto-application/case/{case_id}/download-package")
async def download_package_by_case_id(case_id: str):
    """
    Download do pacote completo por Case ID.
    """
    try:
        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case não encontrado")

        search_patterns = [
            f"/app/*{case_id}*.pdf",
            f"/app/output/*{case_id}*.pdf",
            f"/app/packages/*{case_id}*.pdf",
            f"/app/*PACOTE*.pdf",
        ]

        file_path = None
        for pattern in search_patterns:
            matches = glob.glob(pattern)
            if matches:
                file_path = matches[0]
                break

        if not file_path or not os.path.exists(file_path):
            logger.warning(
                f"Arquivo do pacote não encontrado para case {case_id}. Gerando PDF básico."
            )

            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.lib.units import inch
                from reportlab.pdfgen import canvas

                temp_pdf_path = f"/app/Pacote_Completo_{case_id}.pdf"
                c = canvas.Canvas(temp_pdf_path, pagesize=letter)

                c.setFont("Helvetica-Bold", 20)
                c.drawString(1 * inch, 10 * inch, f"Pacote Completo - Case {case_id}")

                c.setFont("Helvetica", 12)
                y_position = 9 * inch

                c.drawString(1 * inch, y_position, f"Case ID: {case_id}")
                y_position -= 0.5 * inch

                form_code = case.get("form_code", "N/A")
                c.drawString(1 * inch, y_position, f"Tipo de Visto: {form_code}")
                y_position -= 0.5 * inch

                status = case.get("status", "N/A")
                c.drawString(1 * inch, y_position, f"Status: {status}")
                y_position -= 0.5 * inch

                basic_data = case.get("basic_data", {})
                if basic_data:
                    y_position -= 0.5 * inch
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(1 * inch, y_position, "Dados do Aplicante:")
                    y_position -= 0.3 * inch

                    c.setFont("Helvetica", 11)
                    if basic_data.get("full_name"):
                        c.drawString(1.2 * inch, y_position, f"Nome: {basic_data['full_name']}")
                        y_position -= 0.25 * inch
                    if basic_data.get("email"):
                        c.drawString(1.2 * inch, y_position, f"Email: {basic_data['email']}")
                        y_position -= 0.25 * inch
                    if basic_data.get("country_of_birth"):
                        c.drawString(
                            1.2 * inch, y_position, f"País: {basic_data['country_of_birth']}"
                        )

                c.setFont("Helvetica-Oblique", 9)
                c.drawString(1 * inch, 1 * inch, "Este é um documento gerado automaticamente.")
                c.drawString(
                    1 * inch,
                    0.7 * inch,
                    "Para o pacote completo, aguarde a finalização do processo.",
                )

                c.save()
                file_path = temp_pdf_path

            except ImportError:
                raise HTTPException(
                    status_code=404,
                    detail="Pacote ainda não foi gerado. Complete o processo de finalização primeiro.",
                )

        filename = os.path.basename(file_path)
        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Case-ID": case_id,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer download do pacote para case {case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar download: {str(e)}")
