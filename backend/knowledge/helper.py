"""
Helper para Agentes IA acessarem a Base de Conhecimento
Facilita consulta de documentos durante o processamento
"""

import logging
from typing import List, Dict, Optional
from backend.knowledge.manager import KnowledgeBaseManager

logger = logging.getLogger(__name__)


class AgentKnowledgeHelper:
    """
    Helper para agentes consultarem documentos da base de conhecimento
    """
    
    def __init__(self, db):
        self.db = db
        self.kb_manager = KnowledgeBaseManager(db)
    
    async def get_relevant_documents(
        self,
        form_type: str,
        category: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> List[Dict]:
        """
        Busca documentos relevantes para o agente
        
        Args:
            form_type: Tipo de formulário (O-1, I-485, etc.)
            category: Categoria (uscis_instructions, formatting_guides, etc.)
            search_query: Busca por texto específico
        
        Returns:
            Lista de documentos relevantes com texto extraído
        """
        try:
            documents = []
            
            # Buscar por categoria e form_type
            if category:
                docs = await self.kb_manager.get_documents_by_category(
                    category=category,
                    form_type=form_type
                )
                documents.extend(docs)
            else:
                # Buscar em todas as categorias
                for cat in ["uscis_instructions", "formatting_guides", "document_requirements"]:
                    docs = await self.kb_manager.get_documents_by_category(
                        category=cat,
                        form_type=form_type
                    )
                    documents.extend(docs)
            
            # Se tem query de busca, filtrar por relevância
            if search_query and documents:
                filtered_docs = []
                for doc in documents:
                    # Buscar no texto extraído
                    text = doc.get('extracted_text', '').lower()
                    if search_query.lower() in text:
                        # Adicionar snippet relevante
                        doc['relevant_snippet'] = self._extract_snippet(text, search_query)
                        filtered_docs.append(doc)
                documents = filtered_docs
            
            logger.info(
                f"Documentos encontrados para {form_type}",
                extra={
                    "form_type": form_type,
                    "category": category,
                    "count": len(documents)
                }
            )
            
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao buscar documentos: {str(e)}")
            return []
    
    def _extract_snippet(self, text: str, query: str, context_chars: int = 300) -> str:
        """Extrai snippet relevante do texto"""
        try:
            query_lower = query.lower()
            text_lower = text.lower()
            
            index = text_lower.find(query_lower)
            if index == -1:
                return text[:context_chars] + "..."
            
            start = max(0, index - context_chars // 2)
            end = min(len(text), index + len(query) + context_chars // 2)
            
            snippet = text[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."
            
            return snippet
        except:
            return text[:300] + "..."
    
    async def get_checklist(self, form_type: str) -> Optional[str]:
        """
        Obtém checklist específico para um tipo de formulário
        
        Args:
            form_type: Tipo de formulário (O-1, I-485, etc.)
        
        Returns:
            Texto do checklist ou None
        """
        try:
            # Buscar documentos de checklist
            docs = await self.kb_manager.get_documents_by_category(
                category="document_requirements",
                form_type=form_type
            )
            
            # Procurar por checklist específico
            for doc in docs:
                if 'checklist' in doc['filename'].lower():
                    return doc.get('extracted_text', '')
            
            # Fallback: qualquer documento de requirements
            if docs:
                return docs[0].get('extracted_text', '')
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar checklist: {str(e)}")
            return None
    
    async def get_formatting_guide(self, form_type: str) -> Optional[str]:
        """
        Obtém guia de formatação para um tipo de formulário
        
        Args:
            form_type: Tipo de formulário
        
        Returns:
            Texto do guia ou None
        """
        try:
            docs = await self.kb_manager.get_documents_by_category(
                category="formatting_guides",
                form_type=form_type
            )
            
            if docs:
                return docs[0].get('extracted_text', '')
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar guia de formatação: {str(e)}")
            return None
    
    async def get_uscis_instructions(self, form_type: str) -> Optional[str]:
        """
        Obtém instruções oficiais USCIS para um tipo de formulário
        
        Args:
            form_type: Tipo de formulário
        
        Returns:
            Texto das instruções ou None
        """
        try:
            docs = await self.kb_manager.get_documents_by_category(
                category="uscis_instructions",
                form_type=form_type
            )
            
            if docs:
                # Priorizar Policy Manual se existir
                for doc in docs:
                    if 'policy' in doc['filename'].lower() and 'manual' in doc['filename'].lower():
                        return doc.get('extracted_text', '')
                
                # Senão, retornar primeiro documento
                return docs[0].get('extracted_text', '')
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar instruções USCIS: {str(e)}")
            return None
    
    async def search_knowledge_base(self, query: str, form_type: Optional[str] = None) -> List[Dict]:
        """
        Busca livre na base de conhecimento
        
        Args:
            query: Texto de busca
            form_type: Filtrar por tipo de formulário (opcional)
        
        Returns:
            Lista de resultados relevantes
        """
        try:
            results = await self.kb_manager.search_documents(query)
            
            # Filtrar por form_type se fornecido
            if form_type:
                results = [r for r in results if form_type in r.get('form_types', [])]
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca: {str(e)}")
            return []
    
    async def get_context_for_agent(
        self,
        form_type: str,
        agent_role: str = "general"
    ) -> str:
        """
        Obtém contexto consolidado para um agente baseado em seu papel
        
        Args:
            form_type: Tipo de formulário
            agent_role: Papel do agente (document_collector, form_filler, etc.)
        
        Returns:
            Contexto formatado como string
        """
        try:
            context_parts = []
            
            # Buscar documentos relevantes
            if agent_role == "document_collector":
                # Foco em checklists e requirements
                checklist = await self.get_checklist(form_type)
                if checklist:
                    context_parts.append(f"### CHECKLIST DE DOCUMENTOS:\n{checklist[:2000]}\n")
            
            elif agent_role == "form_filler":
                # Foco em guias de formatação
                guide = await self.get_formatting_guide(form_type)
                if guide:
                    context_parts.append(f"### GUIA DE PREENCHIMENTO:\n{guide[:2000]}\n")
            
            elif agent_role == "qa_reviewer":
                # Foco em instruções USCIS
                instructions = await self.get_uscis_instructions(form_type)
                if instructions:
                    context_parts.append(f"### INSTRUÇÕES USCIS:\n{instructions[:2000]}\n")
            
            else:
                # Contexto geral - um pouco de tudo
                checklist = await self.get_checklist(form_type)
                guide = await self.get_formatting_guide(form_type)
                
                if checklist:
                    context_parts.append(f"### CHECKLIST:\n{checklist[:1000]}\n")
                if guide:
                    context_parts.append(f"### GUIA:\n{guide[:1000]}\n")
            
            # Consolidar contexto
            if context_parts:
                full_context = "\n".join(context_parts)
                return f"""
=== CONHECIMENTO DA BASE DE DOCUMENTOS ===

{full_context}

=== FIM DO CONHECIMENTO ===
"""
            
            return ""
            
        except Exception as e:
            logger.error(f"Erro ao obter contexto: {str(e)}")
            return ""


# Singleton instance
_helper_instance = None

def get_knowledge_helper(db):
    """Get or create knowledge helper instance"""
    global _helper_instance
    if _helper_instance is None:
        _helper_instance = AgentKnowledgeHelper(db)
    return _helper_instance
