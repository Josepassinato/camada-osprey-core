import logging

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import Response

from backend.admin.security import require_admin
from core.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/admin/knowledge-base/upload")
async def upload_knowledge_document(
    file: UploadFile,
    category: str = Form(...),
    subcategory: str = Form(...),
    form_types: str = Form(...),  # Comma-separated
    description: str = Form(...),
    uploaded_by: str = Form("admin"),
    admin=Depends(require_admin),
):
    """Upload documento para a base de conhecimento interna (admin-only)."""
    try:
        from backend.knowledge.manager import KnowledgeBaseManager

        kb_manager = KnowledgeBaseManager(db)
        file_data = await file.read()
        form_types_list = [ft.strip() for ft in form_types.split(",")]

        result = await kb_manager.upload_document(
            file_data=file_data,
            filename=file.filename,
            category=category,
            subcategory=subcategory,
            form_types=form_types_list,
            description=description,
            uploaded_by=uploaded_by,
        )

        return result

    except Exception as e:
        logger.error(f"Erro ao fazer upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/knowledge-base/list")
async def list_knowledge_documents(skip: int = 0, limit: int = 50, admin=Depends(require_admin)):
    """Lista todos os documentos da base de conhecimento (admin-only)."""
    try:
        from backend.knowledge.manager import KnowledgeBaseManager

        kb_manager = KnowledgeBaseManager(db)
        return await kb_manager.list_all_documents(skip, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/knowledge-base/categories")
async def get_knowledge_categories(admin=Depends(require_admin)):
    """Retorna categorias disponíveis (admin-only)."""
    from backend.knowledge.manager import KNOWLEDGE_BASE_CATEGORIES, SUPPORTED_FORM_TYPES

    return {"categories": KNOWLEDGE_BASE_CATEGORIES, "form_types": SUPPORTED_FORM_TYPES}


@router.get("/admin/knowledge-base/{document_id}")
async def get_knowledge_document(document_id: str, admin=Depends(require_admin)):
    """Busca documento específico por ID (admin-only)."""
    try:
        from backend.knowledge.manager import KnowledgeBaseManager

        kb_manager = KnowledgeBaseManager(db)
        doc = await kb_manager.get_document_by_id(document_id)

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/knowledge-base/{document_id}/download")
async def download_knowledge_document(document_id: str, admin=Depends(require_admin)):
    """Download do arquivo PDF (admin-only)."""
    try:
        from backend.knowledge.manager import KnowledgeBaseManager

        kb_manager = KnowledgeBaseManager(db)
        doc = await kb_manager.get_document_by_id(document_id)

        if not doc or "file_data" not in doc:
            raise HTTPException(status_code=404, detail="Document not found")

        return Response(
            content=doc["file_data"],
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={doc['filename']}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/admin/knowledge-base/{document_id}")
async def delete_knowledge_document(document_id: str, admin=Depends(require_admin)):
    """Deleta documento da base (admin-only)."""
    try:
        from backend.knowledge.manager import KnowledgeBaseManager

        kb_manager = KnowledgeBaseManager(db)
        return await kb_manager.delete_document(document_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/knowledge-base/stats/overview")
async def get_knowledge_stats(admin=Depends(require_admin)):
    """Estatísticas da base de conhecimento (admin-only)."""
    try:
        from backend.knowledge.manager import KnowledgeBaseManager

        kb_manager = KnowledgeBaseManager(db)
        return await kb_manager.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/knowledge-base/search")
async def search_knowledge_base(q: str, admin=Depends(require_admin)):
    """Busca na base de conhecimento (admin-only)."""
    try:
        from backend.knowledge.manager import KnowledgeBaseManager

        kb_manager = KnowledgeBaseManager(db)
        return await kb_manager.search_documents(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
