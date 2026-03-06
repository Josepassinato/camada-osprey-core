import logging

from fastapi import APIRouter, HTTPException

from backend.core.agents import consult_oracle, oracle

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/oracle/consult")
async def oracle_consult(query: dict):
    """
    Endpoint para consultar o Oráculo Jurídico.
    """
    try:
        if not consult_oracle:
            raise HTTPException(status_code=503, detail="Oracle not available")

        query_type = query.get("type")
        params = query.get("params", {})

        result = consult_oracle(query_type, **params)

        return {"success": True, "query_type": query_type, "result": result}
    except Exception as e:
        logger.error(f"Erro ao consultar oráculo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/oracle/form/{form_code}/requirements")
async def get_form_requirements(form_code: str):
    """Retorna todos os requisitos para um formulário específico."""
    try:
        if not oracle:
            raise HTTPException(status_code=503, detail="Oracle not available")

        result = oracle.consult_form_requirements(form_code)
        return {"success": True, "form_code": form_code, "requirements": result}
    except Exception as e:
        logger.error(f"Erro ao buscar requisitos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/oracle/form/{form_code}/documents")
async def get_required_documents(form_code: str, visa_category: str = None):
    """Retorna lista de documentos obrigatórios para um formulário."""
    try:
        if not oracle:
            raise HTTPException(status_code=503, detail="Oracle not available")

        documents = oracle.get_required_documents(form_code, visa_category)
        return {
            "success": True,
            "form_code": form_code,
            "visa_category": visa_category,
            "required_documents": documents,
            "total_count": len(documents),
        }
    except Exception as e:
        logger.error(f"Erro ao buscar documentos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/oracle/validate-checklist")
async def validate_checklist(data: dict):
    """Valida se todos os documentos obrigatórios foram submetidos."""
    try:
        if not oracle:
            raise HTTPException(status_code=503, detail="Oracle not available")

        form_code = data.get("form_code")
        submitted_docs = data.get("submitted_documents", [])

        result = oracle.validate_document_checklist(form_code, submitted_docs)

        return {"success": True, "validation": result}
    except Exception as e:
        logger.error(f"Erro ao validar checklist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/oracle/kb/stats")
async def get_kb_stats():
    """Retorna estatísticas da base de conhecimento."""
    try:
        if not oracle:
            raise HTTPException(status_code=503, detail="Oracle not available")

        kb = oracle.knowledge_base
        docs = kb.get("documents", [])

        categories = {}
        for doc in docs:
            cat = doc.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "success": True,
            "total_documents": len(docs),
            "categories": categories,
            "total_text_length": sum(doc.get("full_length", 0) for doc in docs),
        }
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
