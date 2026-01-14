"""
Admin Knowledge Base Management
Sistema para upload e gerenciamento de documentos PDF para os agentes de IA
"""

import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pathlib import Path
import uuid
import PyPDF2
import io

logger = logging.getLogger(__name__)

# Diretório para armazenar PDFs
KNOWLEDGE_BASE_DIR = Path("/app/knowledge_base_uploads")


def _ensure_knowledge_base_dir():
    """Ensure the knowledge base directory exists (lazy initialization)"""
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)


async def save_pdf_to_knowledge_base(
    file_content: bytes,
    filename: str,
    category: str,
    description: str,
    uploaded_by: str,
    db
) -> Dict:
    """
    Salva PDF na base de conhecimento e extrai texto
    
    Args:
        file_content: Conteúdo do arquivo PDF
        filename: Nome original do arquivo
        category: Categoria do documento (visa_type, general, forms, etc.)
        description: Descrição do documento
        uploaded_by: ID do usuário que fez upload
        db: Conexão MongoDB
    
    Returns:
        Dict com informações do documento salvo
    """
    try:
        # Ensure directory exists
        _ensure_knowledge_base_dir()
        
        # Gerar ID único para o documento
        doc_id = str(uuid.uuid4())
        
        # Sanitizar filename
        safe_filename = filename.replace(" ", "_").replace("/", "_")
        file_extension = Path(safe_filename).suffix.lower()
        
        if file_extension != '.pdf':
            return {
                "success": False,
                "error": "Apenas arquivos PDF são permitidos"
            }
        
        # Caminho para salvar o arquivo
        file_path = KNOWLEDGE_BASE_DIR / f"{doc_id}_{safe_filename}"
        
        # Salvar arquivo no disco
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Extrair texto do PDF
        extracted_text = extract_text_from_pdf(file_content)
        
        if not extracted_text:
            logger.warning(f"Não foi possível extrair texto do PDF: {filename}")
            extracted_text = "[Texto não pôde ser extraído - PDF pode ser imagem]"
        
        # Informações do documento
        doc_info = {
            "id": doc_id,
            "filename": safe_filename,
            "original_filename": filename,
            "category": category,
            "description": description,
            "file_path": str(file_path),
            "file_size": len(file_content),
            "extracted_text": extracted_text[:50000],  # Limitar a 50k chars para MongoDB
            "text_length": len(extracted_text),
            "uploaded_by": uploaded_by,
            "uploaded_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "status": "active"
        }
        
        # Salvar no MongoDB
        await db.knowledge_base_documents.insert_one(doc_info)
        
        logger.info(
            f"Documento salvo na base de conhecimento",
            extra={
                "doc_id": doc_id,
                "filename": filename,
                "category": category,
                "text_length": len(extracted_text)
            }
        )
        
        return {
            "success": True,
            "document": {
                "id": doc_id,
                "filename": safe_filename,
                "category": category,
                "description": description,
                "file_size": len(file_content),
                "text_length": len(extracted_text),
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Erro ao salvar documento: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def extract_text_from_pdf(pdf_content: bytes) -> str:
    """
    Extrai texto de um arquivo PDF
    
    Args:
        pdf_content: Conteúdo do PDF em bytes
    
    Returns:
        Texto extraído do PDF
    """
    try:
        # Criar objeto PDF
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extrair texto de todas as páginas
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n\n"
        
        return text.strip()
    
    except Exception as e:
        logger.error(f"Erro ao extrair texto do PDF: {str(e)}")
        return ""


async def list_knowledge_base_documents(
    db,
    category: Optional[str] = None,
    limit: int = 100
) -> List[Dict]:
    """
    Lista documentos da base de conhecimento
    
    Args:
        db: Conexão MongoDB
        category: Filtrar por categoria (opcional)
        limit: Número máximo de documentos
    
    Returns:
        Lista de documentos
    """
    try:
        query = {"status": "active"}
        
        if category:
            query["category"] = category
        
        documents = await db.knowledge_base_documents.find(query)\
            .sort("uploaded_at", -1)\
            .limit(limit)\
            .to_list(length=limit)
        
        # Remover campos pesados
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            # Não enviar texto completo na listagem
            if 'extracted_text' in doc:
                doc['text_preview'] = doc['extracted_text'][:500] + "..."
                del doc['extracted_text']
        
        return documents
    
    except Exception as e:
        logger.error(f"Erro ao listar documentos: {str(e)}")
        return []


async def get_knowledge_base_document(db, doc_id: str) -> Optional[Dict]:
    """
    Obtém um documento específico da base de conhecimento
    
    Args:
        db: Conexão MongoDB
        doc_id: ID do documento
    
    Returns:
        Informações do documento ou None
    """
    try:
        document = await db.knowledge_base_documents.find_one({
            "id": doc_id,
            "status": "active"
        })
        
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        
        return document
    
    except Exception as e:
        logger.error(f"Erro ao buscar documento: {str(e)}")
        return None


async def delete_knowledge_base_document(db, doc_id: str, deleted_by: str) -> Dict:
    """
    Remove um documento da base de conhecimento
    
    Args:
        db: Conexão MongoDB
        doc_id: ID do documento
        deleted_by: ID do usuário que está deletando
    
    Returns:
        Dict com resultado da operação
    """
    try:
        # Buscar documento
        document = await db.knowledge_base_documents.find_one({
            "id": doc_id,
            "status": "active"
        })
        
        if not document:
            return {
                "success": False,
                "error": "Documento não encontrado"
            }
        
        # Marcar como deletado (soft delete)
        await db.knowledge_base_documents.update_one(
            {"id": doc_id},
            {
                "$set": {
                    "status": "deleted",
                    "deleted_by": deleted_by,
                    "deleted_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Opcionalmente, deletar arquivo físico
        # (comentado para manter backup)
        # file_path = Path(document['file_path'])
        # if file_path.exists():
        #     file_path.unlink()
        
        logger.info(
            f"Documento removido da base de conhecimento",
            extra={
                "doc_id": doc_id,
                "deleted_by": deleted_by
            }
        )
        
        return {
            "success": True,
            "message": "Documento removido com sucesso"
        }
    
    except Exception as e:
        logger.error(f"Erro ao deletar documento: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def search_knowledge_base(db, query: str, category: Optional[str] = None) -> List[Dict]:
    """
    Busca na base de conhecimento
    
    Args:
        db: Conexão MongoDB
        query: Texto de busca
        category: Filtrar por categoria (opcional)
    
    Returns:
        Lista de documentos relevantes
    """
    try:
        # Criar filtro de busca
        search_filter = {
            "status": "active",
            "$or": [
                {"extracted_text": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"filename": {"$regex": query, "$options": "i"}}
            ]
        }
        
        if category:
            search_filter["category"] = category
        
        # Buscar documentos
        documents = await db.knowledge_base_documents.find(search_filter)\
            .limit(20)\
            .to_list(length=20)
        
        # Preparar resultados
        results = []
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            
            # Encontrar trecho relevante
            text = doc.get('extracted_text', '')
            query_lower = query.lower()
            
            # Buscar primeira ocorrência
            index = text.lower().find(query_lower)
            if index != -1:
                start = max(0, index - 100)
                end = min(len(text), index + 200)
                snippet = "..." + text[start:end] + "..."
            else:
                snippet = text[:300] + "..."
            
            results.append({
                "id": doc['id'],
                "filename": doc['filename'],
                "category": doc['category'],
                "description": doc['description'],
                "snippet": snippet,
                "uploaded_at": doc['uploaded_at'].isoformat() if doc.get('uploaded_at') else None
            })
        
        return results
    
    except Exception as e:
        logger.error(f"Erro ao buscar na base de conhecimento: {str(e)}")
        return []


async def get_knowledge_base_stats(db) -> Dict:
    """
    Obtém estatísticas da base de conhecimento
    
    Args:
        db: Conexão MongoDB
    
    Returns:
        Dict com estatísticas
    """
    try:
        total_documents = await db.knowledge_base_documents.count_documents({"status": "active"})
        
        # Documentos por categoria
        pipeline = [
            {"$match": {"status": "active"}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]
        by_category = await db.knowledge_base_documents.aggregate(pipeline).to_list(length=100)
        
        # Tamanho total
        pipeline_size = [
            {"$match": {"status": "active"}},
            {"$group": {"_id": None, "total_size": {"$sum": "$file_size"}}}
        ]
        size_result = await db.knowledge_base_documents.aggregate(pipeline_size).to_list(length=1)
        total_size = size_result[0]['total_size'] if size_result else 0
        
        return {
            "total_documents": total_documents,
            "by_category": {item['_id']: item['count'] for item in by_category},
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2)
        }
    
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return {}
