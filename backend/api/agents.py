import logging

from fastapi import APIRouter, Form, HTTPException, UploadFile

from backend.core.agents import (
    analyze_uploaded_document,
    document_analyzer,
    fill_form_automatically,
    form_filler,
    oracle,
    translate_text,
    translator,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/agent/document-analyzer/analyze")
async def analyze_document_endpoint(file: UploadFile, document_type: str = Form(...)):
    """Analisa um documento usando OCR e extração de dados."""
    try:
        if not document_analyzer or not analyze_uploaded_document:
            raise HTTPException(status_code=503, detail="Document Analyzer not available")

        file_content = await file.read()
        result = analyze_uploaded_document(file_content, document_type, file.filename)

        return result
    except Exception as e:
        logger.error(f"Erro no Document Analyzer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/document-analyzer/supported-types")
async def get_supported_document_types():
    """Retorna tipos de documentos suportados pelo analisador."""
    if not document_analyzer:
        raise HTTPException(status_code=503, detail="Document Analyzer not available")

    return {"success": True, "supported_types": document_analyzer.supported_documents}


@router.get("/agent/document-analyzer/consult-kb/{document_type}")
async def consult_kb_for_document(document_type: str):
    """Consulta a base de conhecimento sobre um tipo de documento."""
    try:
        if not document_analyzer:
            raise HTTPException(status_code=503, detail="Document Analyzer not available")

        result = document_analyzer.consult_kb_for_document(document_type)

        return {"success": True, "consultation": result}
    except Exception as e:
        logger.error(f"Erro ao consultar KB: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/form-filler/fill")
async def fill_form_endpoint(data: dict):
    """Preenche um formulário automaticamente com dados do usuário."""
    try:
        if not form_filler or not fill_form_automatically:
            raise HTTPException(status_code=503, detail="Form Filler not available")

        form_code = data.get("form_code")
        user_data = data.get("user_data")

        result = fill_form_automatically(form_code, user_data)

        return result
    except Exception as e:
        logger.error(f"Erro no Form Filler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/form-filler/missing-fields/{form_code}")
async def get_missing_fields_endpoint(form_code: str, user_data: dict = None):
    """Retorna campos obrigatórios faltantes."""
    try:
        if not form_filler:
            raise HTTPException(status_code=503, detail="Form Filler not available")

        if not user_data:
            user_data = {}

        missing = form_filler.get_missing_fields(form_code, user_data)

        return {
            "success": True,
            "form_code": form_code,
            "missing_fields": missing,
            "total_missing": len(missing),
        }
    except Exception as e:
        logger.error(f"Erro ao buscar campos faltantes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/form-filler/field-map/{form_code}")
async def get_form_field_map(form_code: str):
    """Retorna mapa completo de campos do formulário."""
    try:
        if not form_filler:
            raise HTTPException(status_code=503, detail="Form Filler not available")

        field_map = form_filler.generate_field_map(form_code)

        return {"success": True, "field_map": field_map}
    except Exception as e:
        logger.error(f"Erro ao gerar field map: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/form-filler/guide/{form_code}")
async def get_form_guide(form_code: str):
    """Busca o guia completo de preenchimento do formulário na KB."""
    try:
        if not form_filler:
            raise HTTPException(status_code=503, detail="Form Filler not available")

        result = form_filler.get_form_guide_from_kb(form_code)

        return {"success": True, "guide": result}
    except Exception as e:
        logger.error(f"Erro ao buscar guia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/form-filler/field-instructions/{form_code}/{field_name}")
async def get_field_instructions(form_code: str, field_name: str):
    """Busca instruções específicas para um campo."""
    try:
        if not form_filler:
            raise HTTPException(status_code=503, detail="Form Filler not available")

        result = form_filler.get_field_instructions(form_code, field_name)

        return {"success": True, "instructions": result}
    except Exception as e:
        logger.error(f"Erro ao buscar instruções: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/translator/translate")
async def translate_endpoint(data: dict):
    """Traduz texto de um idioma para outro."""
    try:
        if not translator or not translate_text:
            raise HTTPException(status_code=503, detail="Translator not available")

        text = data.get("text")
        source_lang = data.get("source_lang", "pt")
        target_lang = data.get("target_lang", "en")
        data.get("document_type")

        result = translate_text(text, source_lang, target_lang)

        return result
    except Exception as e:
        logger.error(f"Erro no Translator: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/translator/detect-language")
async def detect_language_endpoint(data: dict):
    """Detecta o idioma de um texto."""
    try:
        if not translator:
            raise HTTPException(status_code=503, detail="Translator not available")

        text = data.get("text")
        result = translator.detect_language(text)

        return {"success": True, "detection": result}
    except Exception as e:
        logger.error(f"Erro ao detectar idioma: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent/translator/supported-languages")
async def get_supported_languages():
    """Retorna idiomas suportados pelo tradutor."""
    if not translator:
        raise HTTPException(status_code=503, detail="Translator not available")

    return {"success": True, "supported_languages": translator.supported_languages}


@router.get("/agents/status")
async def get_all_agents_status():
    """Retorna status de todos os agentes."""
    agents_status = {
        "oracle": oracle is not None,
        "document_analyzer": document_analyzer is not None,
        "form_filler": form_filler is not None,
        "translator": translator is not None,
    }

    return {
        "success": True,
        "agents": agents_status,
        "total_active": sum(agents_status.values()),
        "total_agents": len(agents_status),
    }
