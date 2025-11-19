"""
Sistema de Knowledge Base para Agentes Internos
Gerencia documentos de referência, templates e padrões
NÃO fornece aconselhamento jurídico - apenas organização interna
"""

from datetime import datetime
from typing import Dict, List, Optional
import PyPDF2
import io
import json
import re

class KnowledgeBaseManager:
    """Gerenciador da Base de Conhecimento Interna"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db.knowledge_base
    
    async def upload_document(self, 
                             file_data: bytes,
                             filename: str,
                             category: str,
                             subcategory: str,
                             form_types: List[str],
                             description: str,
                             uploaded_by: str) -> Dict:
        """
        Faz upload de documento para a base de conhecimento
        
        Categorias:
        - document_requirements: Listas de documentos necessários
        - letter_templates: Templates de cartas e cover letters
        - organization_standards: Padrões de organização de arquivos
        - formatting_guides: Guias de formatação
        - uscis_instructions: Instruções oficiais do USCIS
        """
        
        # Extrair texto do PDF se possível
        extracted_text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + "\n"
        except:
            extracted_text = "Text extraction not available"
        
        # Criar documento
        document = {
            "document_id": f"KB-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "filename": filename,
            "category": category,
            "subcategory": subcategory,
            "form_types": form_types,  # Lista de vistos aplicáveis (I-539, F-1, etc)
            "description": description,
            "file_data": file_data,
            "file_size": len(file_data),
            "extracted_text": extracted_text,
            "uploaded_by": uploaded_by,
            "upload_date": datetime.utcnow(),
            "last_updated": datetime.utcnow(),
            "version": 1,
            "status": "active",
            "access_count": 0,
            "metadata": {
                "file_type": "pdf",
                "pages": len(PyPDF2.PdfReader(io.BytesIO(file_data)).pages) if file_data else 0
            }
        }
        
        # Inserir no banco
        result = await self.collection.insert_one(document)
        
        return {
            "success": True,
            "document_id": document["document_id"],
            "message": f"Document '{filename}' uploaded successfully"
        }
    
    async def get_documents_by_category(self, category: str, form_type: Optional[str] = None) -> List[Dict]:
        """Busca documentos por categoria e opcionalmente por tipo de formulário"""
        query = {"category": category, "status": "active"}
        
        if form_type:
            query["form_types"] = form_type
        
        documents = await self.collection.find(query).to_list(length=100)
        
        # Remover file_data para não sobrecarregar resposta
        for doc in documents:
            doc['_id'] = str(doc['_id'])
            doc.pop('file_data', None)
            doc.pop('extracted_text', None)
        
        return documents
    
    async def get_document_by_id(self, document_id: str) -> Optional[Dict]:
        """Busca documento específico por ID"""
        document = await self.collection.find_one({"document_id": document_id})
        
        if document:
            document['_id'] = str(document['_id'])
            # Incrementar contador de acesso
            await self.collection.update_one(
                {"document_id": document_id},
                {"$inc": {"access_count": 1}}
            )
        
        return document
    
    async def get_required_documents_for_visa(self, form_type: str) -> List[Dict]:
        """
        Obtém lista de documentos necessários para um tipo de visto
        Consulta documentos da categoria 'document_requirements'
        """
        docs = await self.get_documents_by_category("document_requirements", form_type)
        
        # Parsear informações dos documentos
        required_docs = []
        for doc in docs:
            # Tentar extrair lista de documentos do texto
            text = doc.get('extracted_text', '')
            # Você pode melhorar isso com regex ou parsers específicos
            required_docs.append({
                "source_document": doc['filename'],
                "document_id": doc['document_id'],
                "description": doc['description'],
                "last_updated": doc['last_updated']
            })
        
        return required_docs
    
    async def get_letter_template(self, form_type: str) -> Optional[Dict]:
        """Obtém template de carta para um tipo de visto"""
        templates = await self.get_documents_by_category("letter_templates", form_type)
        
        if templates:
            # Retornar o mais recente
            templates.sort(key=lambda x: x['upload_date'], reverse=True)
            return templates[0]
        
        return None
    
    async def get_organization_standards(self, form_type: str) -> Optional[Dict]:
        """Obtém padrões de organização para um tipo de visto"""
        standards = await self.get_documents_by_category("organization_standards", form_type)
        
        if standards:
            standards.sort(key=lambda x: x['upload_date'], reverse=True)
            return standards[0]
        
        return None
    
    async def list_all_documents(self, skip: int = 0, limit: int = 50) -> Dict:
        """Lista todos os documentos com paginação"""
        total = await self.collection.count_documents({"status": "active"})
        
        documents = await self.collection.find({"status": "active"}) \
            .skip(skip) \
            .limit(limit) \
            .to_list(length=limit)
        
        # Limpar dados pesados
        for doc in documents:
            doc['_id'] = str(doc['_id'])
            doc.pop('file_data', None)
            doc.pop('extracted_text', None)
        
        return {
            "total": total,
            "documents": documents,
            "page": skip // limit + 1,
            "per_page": limit
        }
    
    async def update_document(self, document_id: str, updates: Dict) -> Dict:
        """Atualiza documento existente"""
        updates['last_updated'] = datetime.utcnow()
        updates['$inc'] = {"version": 1}
        
        result = await self.collection.update_one(
            {"document_id": document_id},
            {"$set": updates}
        )
        
        if result.modified_count > 0:
            return {"success": True, "message": "Document updated successfully"}
        else:
            return {"success": False, "message": "Document not found or no changes made"}
    
    async def delete_document(self, document_id: str) -> Dict:
        """Soft delete - marca como inativo"""
        result = await self.collection.update_one(
            {"document_id": document_id},
            {"$set": {"status": "deleted", "deleted_at": datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            return {"success": True, "message": "Document deleted successfully"}
        else:
            return {"success": False, "message": "Document not found"}
    
    async def search_documents(self, query: str) -> List[Dict]:
        """Busca documentos por texto"""
        # Busca no filename, description e extracted_text
        # Use string pattern directly with MongoDB
        documents = await self.collection.find({
            "$or": [
                {"filename": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"extracted_text": {"$regex": query, "$options": "i"}}
            ],
            "status": "active"
        }).to_list(length=50)
        
        for doc in documents:
            doc['_id'] = str(doc['_id'])
            doc.pop('file_data', None)
            doc.pop('extracted_text', None)
        
        return documents
    
    async def get_statistics(self) -> Dict:
        """Obtém estatísticas da base de conhecimento"""
        total_docs = await self.collection.count_documents({"status": "active"})
        
        # Por categoria
        pipeline = [
            {"$match": {"status": "active"}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]
        by_category = await self.collection.aggregate(pipeline).to_list(length=100)
        
        # Por tipo de formulário
        pipeline_forms = [
            {"$match": {"status": "active"}},
            {"$unwind": "$form_types"},
            {"$group": {"_id": "$form_types", "count": {"$sum": 1}}}
        ]
        by_form = await self.collection.aggregate(pipeline_forms).to_list(length=100)
        
        # Mais acessados
        most_accessed = await self.collection.find({"status": "active"}) \
            .sort("access_count", -1) \
            .limit(10) \
            .to_list(length=10)
        
        for doc in most_accessed:
            doc['_id'] = str(doc['_id'])
            doc.pop('file_data', None)
            doc.pop('extracted_text', None)
        
        return {
            "total_documents": total_docs,
            "by_category": {item['_id']: item['count'] for item in by_category},
            "by_form_type": {item['_id']: item['count'] for item in by_form},
            "most_accessed": most_accessed
        }


# Categorias padrão
KNOWLEDGE_BASE_CATEGORIES = {
    "document_requirements": "Document Requirements Checklists",
    "letter_templates": "Letter and Cover Letter Templates",
    "organization_standards": "Package Organization Standards",
    "formatting_guides": "Formatting and Style Guides",
    "uscis_instructions": "Official USCIS Instructions"
}

# Tipos de formulário suportados
SUPPORTED_FORM_TYPES = [
    "I-539",
    "F-1",
    "I-130",
    "I-765",
    "I-90",
    "EB-2 NIW",
    "EB-1A",
    "I-589",
    "ALL"  # Aplicável a todos os tipos
]
