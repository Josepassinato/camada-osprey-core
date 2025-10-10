"""
Document Storage System
Sistema para armazenar documentos aceitos organizados por caso/cliente
"""

import os
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path
import shutil
import json

logger = logging.getLogger(__name__)

class DocumentStorageSystem:
    """
    Sistema para armazenar e organizar documentos aceitos por caso
    """
    
    def __init__(self, base_storage_path: str = "/app/storage/client_documents"):
        """
        Inicializa o sistema de armazenamento
        
        Args:
            base_storage_path: Caminho base para armazenamento dos documentos
        """
        self.base_path = Path(base_storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Document Storage System initialized at: {self.base_path}")
    
    def _generate_file_hash(self, file_content: bytes) -> str:
        """Gera hash único para o arquivo"""
        return hashlib.sha256(file_content).hexdigest()[:16]
    
    def _get_case_directory(self, case_id: str) -> Path:
        """
        Retorna o diretório para um caso específico
        Estrutura: /storage/client_documents/{case_id}/
        """
        case_dir = self.base_path / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        return case_dir
    
    def _get_document_filename(self, document_type: str, original_filename: str, file_hash: str) -> str:
        """
        Gera nome padronizado para o arquivo
        Formato: {document_type}_{timestamp}_{hash}_{original_name}
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        file_extension = Path(original_filename).suffix
        safe_original = Path(original_filename).stem[:20]  # Limit length
        
        return f"{document_type}_{timestamp}_{file_hash}_{safe_original}{file_extension}"
    
    async def store_accepted_document(
        self,
        case_id: str,
        document_type: str,
        file_content: bytes,
        original_filename: str,
        analysis_result: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Armazena um documento aceito na pasta do caso
        
        Args:
            case_id: ID do caso do cliente
            document_type: Tipo do documento (passport, birth_certificate, etc.)
            file_content: Conteúdo binário do arquivo
            original_filename: Nome original do arquivo
            analysis_result: Resultado da análise do documento
            metadata: Metadados adicionais
        
        Returns:
            Dict com informações do armazenamento
        """
        try:
            # Verificar se o documento foi aceito
            if not self._is_document_accepted(analysis_result):
                logger.warning(f"❌ Document not accepted for storage: {original_filename}")
                return {
                    "success": False,
                    "reason": "document_not_accepted",
                    "message": "Documento não foi aceito pela análise"
                }
            
            # Gerar hash e nome do arquivo
            file_hash = self._generate_file_hash(file_content)
            case_dir = self._get_case_directory(case_id)
            filename = self._get_document_filename(document_type, original_filename, file_hash)
            file_path = case_dir / filename
            
            # Verificar se já existe documento idêntico
            existing_file = await self._check_duplicate_document(case_id, file_hash)
            if existing_file:
                logger.info(f"📄 Duplicate document found, skipping storage: {filename}")
                return {
                    "success": True,
                    "reason": "duplicate_found",
                    "file_path": str(existing_file),
                    "message": "Documento idêntico já existe no caso"
                }
            
            # Salvar o arquivo
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Criar arquivo de metadados
            metadata_info = {
                "case_id": case_id,
                "document_type": document_type,
                "original_filename": original_filename,
                "stored_filename": filename,
                "file_hash": file_hash,
                "file_size": len(file_content),
                "stored_at": datetime.now(timezone.utc).isoformat(),
                "analysis_result": analysis_result,
                "custom_metadata": metadata or {}
            }
            
            metadata_path = case_dir / f"{filename}.metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_info, f, indent=2, ensure_ascii=False)
            
            # Atualizar índice do caso
            await self._update_case_index(case_id, filename, metadata_info)
            
            logger.info(f"✅ Document stored successfully: {file_path}")
            
            return {
                "success": True,
                "file_path": str(file_path),
                "metadata_path": str(metadata_path),
                "filename": filename,
                "file_hash": file_hash,
                "case_directory": str(case_dir),
                "message": f"Documento {document_type} armazenado com sucesso"
            }
            
        except Exception as e:
            logger.error(f"❌ Error storing document: {str(e)}")
            return {
                "success": False,
                "reason": "storage_error",
                "error": str(e),
                "message": "Erro ao armazenar documento"
            }
    
    def _is_document_accepted(self, analysis_result: Dict[str, Any]) -> bool:
        """
        Verifica se o documento foi aceito pela análise
        """
        # Verificar diferentes formatos de resultado
        if analysis_result.get("valid") is True:
            return True
        
        if analysis_result.get("decision") == "accepted":
            return True
            
        # Verificar se a análise de texto contém "ACEITO"
        full_text = analysis_result.get("full_text_extracted", "")
        dra_paula = analysis_result.get("dra_paula_assessment", "")
        
        if "ACEITO" in full_text or "ACEITO" in dra_paula:
            return True
        
        # Se tem alta completeness e poucos issues, considerar aceito
        completeness = analysis_result.get("completeness", 0)
        issues = analysis_result.get("issues_found", [])
        
        if completeness >= 80 and len([i for i in issues if "❌" in str(i)]) == 0:
            return True
        
        return False
    
    async def _check_duplicate_document(self, case_id: str, file_hash: str) -> Optional[Path]:
        """
        Verifica se já existe um documento com o mesmo hash no caso
        """
        case_dir = self._get_case_directory(case_id)
        
        for file_path in case_dir.glob("*"):
            if file_path.is_file() and file_hash in file_path.name:
                return file_path
        
        return None
    
    async def _update_case_index(self, case_id: str, filename: str, metadata: Dict[str, Any]):
        """
        Atualiza o índice de documentos do caso
        """
        case_dir = self._get_case_directory(case_id)
        index_path = case_dir / "case_index.json"
        
        # Carregar índice existente ou criar novo
        index_data = {"case_id": case_id, "documents": [], "last_updated": ""}
        
        if index_path.exists():
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Could not read existing index: {e}")
        
        # Adicionar novo documento
        doc_entry = {
            "filename": filename,
            "document_type": metadata["document_type"],
            "original_filename": metadata["original_filename"],
            "stored_at": metadata["stored_at"],
            "file_hash": metadata["file_hash"],
            "file_size": metadata["file_size"]
        }
        
        # Evitar duplicatas
        existing_hashes = [d.get("file_hash") for d in index_data["documents"]]
        if metadata["file_hash"] not in existing_hashes:
            index_data["documents"].append(doc_entry)
        
        index_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        # Salvar índice atualizado
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    async def get_case_documents(self, case_id: str) -> Dict[str, Any]:
        """
        Retorna lista de todos os documentos de um caso
        """
        case_dir = self._get_case_directory(case_id)
        index_path = case_dir / "case_index.json"
        
        if not index_path.exists():
            return {"case_id": case_id, "documents": [], "count": 0}
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            index_data["count"] = len(index_data["documents"])
            return index_data
            
        except Exception as e:
            logger.error(f"❌ Error reading case index: {e}")
            return {"case_id": case_id, "documents": [], "count": 0, "error": str(e)}
    
    async def prepare_final_document_package(self, case_id: str) -> Dict[str, Any]:
        """
        Prepara pacote final com todos os documentos aceitos do caso
        """
        try:
            case_dir = self._get_case_directory(case_id)
            package_dir = case_dir / "final_package"
            package_dir.mkdir(exist_ok=True)
            
            # Obter lista de documentos
            case_docs = await self.get_case_documents(case_id)
            
            if not case_docs["documents"]:
                return {
                    "success": False,
                    "message": "Nenhum documento encontrado no caso"
                }
            
            # Copiar documentos para pasta do pacote final
            copied_files = []
            for doc in case_docs["documents"]:
                source_file = case_dir / doc["filename"]
                if source_file.exists():
                    dest_file = package_dir / doc["filename"]
                    shutil.copy2(source_file, dest_file)
                    copied_files.append(doc["filename"])
            
            # Criar manifesto do pacote
            manifest = {
                "case_id": case_id,
                "package_created_at": datetime.now(timezone.utc).isoformat(),
                "document_count": len(copied_files),
                "documents": case_docs["documents"],
                "package_directory": str(package_dir)
            }
            
            manifest_path = package_dir / "package_manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📦 Final package prepared for case {case_id}: {len(copied_files)} documents")
            
            return {
                "success": True,
                "package_directory": str(package_dir),
                "document_count": len(copied_files),
                "copied_files": copied_files,
                "manifest_path": str(manifest_path),
                "message": f"Pacote final criado com {len(copied_files)} documentos"
            }
            
        except Exception as e:
            logger.error(f"❌ Error preparing final package: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao preparar pacote final"
            }

# Global instance
document_storage = DocumentStorageSystem()

# Helper functions for easy integration
async def store_accepted_document(case_id: str, document_type: str, file_content: bytes, 
                                original_filename: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function for storing accepted documents"""
    return await document_storage.store_accepted_document(
        case_id, document_type, file_content, original_filename, analysis_result
    )

async def get_case_documents(case_id: str) -> Dict[str, Any]:
    """Helper function for getting case documents"""
    return await document_storage.get_case_documents(case_id)

async def prepare_final_package(case_id: str) -> Dict[str, Any]:
    """Helper function for preparing final document package"""
    return await document_storage.prepare_final_document_package(case_id)