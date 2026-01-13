import glob
import logging
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/download/package/{filename}")
async def download_package(filename: str):
    """
    Download de pacotes gerados (arquivos ZIP ou PDF).
    """
    try:
        file_path = f"/app/{filename}"

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")

        if not (filename.endswith(".zip") or filename.endswith(".pdf")):
            raise HTTPException(status_code=400, detail="Apenas arquivos ZIP ou PDF são permitidos")

        media_type = "application/pdf" if filename.endswith(".pdf") else "application/zip"

        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer download do pacote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/report/{filename}")
async def download_report(filename: str):
    """
    Download de relatórios gerados (arquivos Markdown).
    """
    try:
        file_path = f"/app/{filename}"

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")

        if not filename.endswith(".md"):
            raise HTTPException(status_code=400, detail="Apenas arquivos Markdown são permitidos")

        return FileResponse(
            path=file_path,
            media_type="text/markdown",
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer download do relatório: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/list")
async def list_downloads():
    """
    Lista todos os arquivos disponíveis para download.
    """
    try:
        downloads = {"packages": [], "reports": []}

        zip_files = glob.glob("/app/*.zip")
        for file_path in zip_files:
            filename = os.path.basename(file_path)
            size = os.path.getsize(file_path)
            downloads["packages"].append(
                {
                    "filename": filename,
                    "size": size,
                    "size_human": f"{size / 1024:.1f} KB"
                    if size < 1024 * 1024
                    else f"{size / (1024 * 1024):.1f} MB",
                    "download_url": f"/api/download/package/{filename}",
                }
            )

        md_files = glob.glob("/app/*.md")
        for file_path in md_files:
            filename = os.path.basename(file_path)
            if filename in ["test_result.md", "README.md"]:
                continue
            size = os.path.getsize(file_path)
            downloads["reports"].append(
                {
                    "filename": filename,
                    "size": size,
                    "size_human": f"{size / 1024:.1f} KB",
                    "download_url": f"/api/download/report/{filename}",
                }
            )

        return {
            "success": True,
            "total_packages": len(downloads["packages"]),
            "total_reports": len(downloads["reports"]),
            "downloads": downloads,
        }
    except Exception as e:
        logger.error(f"Erro ao listar downloads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
