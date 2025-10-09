"""
Real Data Integrator - Phase 4A Enhancement
Integração com dados reais do MongoDB para Final Package Assembly
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import base64
import tempfile
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorDatabase
import gridfs
from bson import ObjectId

logger = logging.getLogger(__name__)

class RealDataIntegrator:
    """
    Integra dados reais do MongoDB para criação do pacote final
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.temp_dir = Path("/tmp/package_assembly")
        self.temp_dir.mkdir(exist_ok=True)
    
    async def get_case_complete_data(self, case_id: str) -> Dict[str, Any]:
        """
        Recupera todos os dados de um caso para assemblagem do pacote
        """
        try:
            logger.info(f"🔄 Retrieving complete data for case: {case_id}")
            
            # 1. Dados básicos do caso
            case_data = await self.db.cases.find_one({"case_id": case_id})
            if not case_data:
                raise ValueError(f"Case {case_id} not found")
            
            # 2. Documentos validados (Phase 1)
            documents = await self.db.documents.find({"case_id": case_id}).to_list(None)
            
            # 3. Dados do formulário friendly (Phase 2)
            form_data = await self.db.friendly_forms.find_one({"case_id": case_id})
            
            # 4. Formulários oficiais gerados
            official_forms = await self.db.official_forms.find({"case_id": case_id}).to_list(None)
            
            # 5. Cartas de apresentação (Phase 3)
            cover_letters = await self.db.cover_letters.find({"case_id": case_id}).to_list(None)
            
            # 6. Análises de consistência
            consistency_reports = await self.db.consistency_reports.find({"case_id": case_id}).to_list(None)
            
            complete_data = {
                "case_info": {
                    "case_id": case_id,
                    "visa_type": case_data.get("form_code", "Unknown"),
                    "created_at": case_data.get("created_at"),
                    "last_updated": case_data.get("updated_at"),
                    "status": case_data.get("status", "active")
                },
                "documents": self._process_documents_data(documents),
                "form_data": self._process_form_data(form_data) if form_data else {},
                "official_forms": official_forms or [],
                "cover_letters": cover_letters or [],
                "consistency_reports": consistency_reports or [],
                "statistics": {
                    "total_documents": len(documents),
                    "validated_documents": len([d for d in documents if d.get("validation_status") == "validated"]),
                    "forms_completed": len(official_forms),
                    "letters_generated": len(cover_letters)
                }
            }
            
            logger.info(f"✅ Complete data retrieved: {complete_data['statistics']}")
            return complete_data
            
        except Exception as e:
            logger.error(f"❌ Error retrieving case data: {e}")
            raise
    
    def _process_documents_data(self, documents: List[Dict]) -> List[Dict[str, Any]]:
        """
        Processa dados de documentos para assemblagem
        """
        processed_docs = []
        
        for doc in documents:
            try:
                doc_info = {
                    "document_id": doc.get("document_id"),
                    "filename": doc.get("filename", "unknown.pdf"),
                    "document_type": doc.get("document_type", "unknown"),
                    "upload_date": doc.get("upload_date"),
                    "validation_status": doc.get("validation_status", "pending"),
                    "confidence_score": doc.get("confidence_score", 0.0),
                    "file_size": doc.get("file_size", 0),
                    "pages_count": doc.get("pages_count", 1),
                    "analysis_result": doc.get("analysis_result", {}),
                    "issues": doc.get("issues", []),
                    "extracted_data": doc.get("extracted_data", {}),
                    
                    # Para assemblagem do PDF
                    "file_path": None,  # Será preenchido quando necessário
                    "include_in_packet": doc.get("validation_status") == "validated",
                    "packet_order": self._get_document_order(doc.get("document_type", "unknown"))
                }
                
                processed_docs.append(doc_info)
                
            except Exception as e:
                logger.warning(f"Error processing document {doc.get('document_id', 'unknown')}: {e}")
                continue
        
        # Ordenar documentos por ordem no pacote
        processed_docs.sort(key=lambda x: x['packet_order'])
        
        return processed_docs
    
    def _process_form_data(self, form_data: Dict) -> Dict[str, Any]:
        """
        Processa dados do formulário friendly para assemblagem
        """
        if not form_data:
            return {}
        
        return {
            "personal_info": form_data.get("personal_info", {}),
            "address_info": form_data.get("address_info", {}),
            "employment_info": form_data.get("employment_info", {}),
            "education_info": form_data.get("education_info", {}),
            "completeness_score": form_data.get("completeness_score", 0),
            "validation_results": form_data.get("validation_results", {}),
            "official_conversion": form_data.get("official_conversion", {}),
            "last_updated": form_data.get("updated_at")
        }
    
    def _get_document_order(self, document_type: str) -> int:
        """
        Define ordem dos documentos no pacote final
        """
        order_map = {
            # Formulários oficiais primeiro
            "i129": 10,
            "i485": 10,
            "i130": 10,
            "i539": 10,
            
            # Cartas de apresentação
            "cover_letter": 20,
            
            # Documentos de identidade
            "passport": 30,
            "birth_certificate": 31,
            "marriage_certificate": 32,
            
            # Documentos educacionais
            "diploma": 40,
            "transcript": 41,
            "certificate": 42,
            
            # Documentos de trabalho
            "employment_letter": 50,
            "i797": 51,
            "paystub": 52,
            "tax_return": 53,
            
            # Documentos financeiros
            "bank_statement": 60,
            "affidavit_support": 61,
            
            # Documentos médicos
            "medical_exam": 70,
            "vaccination_record": 71,
            
            # Outros documentos
            "police_clearance": 80,
            "photos": 90,
            "other": 99
        }
        
        return order_map.get(document_type.lower(), 99)
    
    async def get_document_file_data(self, document_id: str) -> Optional[bytes]:
        """
        Recupera dados binários do arquivo de documento
        """
        try:
            # Tentar encontrar o documento no GridFS ou na collection documents
            document = await self.db.documents.find_one({"document_id": document_id})
            
            if not document:
                logger.warning(f"Document {document_id} not found")
                return None
            
            # Se tem file_data como base64
            if "file_data" in document:
                return base64.b64decode(document["file_data"])
            
            # Se tem GridFS file_id
            if "file_id" in document:
                fs = gridfs.GridFS(self.db)
                grid_out = await fs.open_download_stream(ObjectId(document["file_id"]))
                return await grid_out.read()
            
            # Se tem file_path
            if "file_path" in document and document["file_path"]:
                file_path = Path(document["file_path"])
                if file_path.exists():
                    return file_path.read_bytes()
            
            logger.warning(f"No file data found for document {document_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document file data for {document_id}: {e}")
            return None
    
    async def save_temporary_file(self, file_data: bytes, filename: str) -> Path:
        """
        Salva dados de arquivo temporariamente para processamento
        """
        try:
            temp_file = self.temp_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            temp_file.write_bytes(file_data)
            return temp_file
            
        except Exception as e:
            logger.error(f"Error saving temporary file {filename}: {e}")
            raise
    
    async def get_packet_metadata(self, case_id: str) -> Dict[str, Any]:
        """
        Gera metadata para o pacote final
        """
        try:
            complete_data = await self.get_case_complete_data(case_id)
            
            # Calcular estatísticas do pacote
            total_documents = len(complete_data["documents"])
            included_documents = len([d for d in complete_data["documents"] if d["include_in_packet"]])
            total_pages = sum(d.get("pages_count", 1) for d in complete_data["documents"] if d["include_in_packet"])
            
            # Calcular score de qualidade geral
            quality_scores = [d.get("confidence_score", 0) for d in complete_data["documents"] if d["include_in_packet"]]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # Identificar issues críticos
            all_issues = []
            for doc in complete_data["documents"]:
                if doc.get("issues"):
                    all_issues.extend(doc["issues"])
            
            critical_issues = [issue for issue in all_issues if "critical" in issue.lower() or "error" in issue.lower()]
            
            metadata = {
                "case_id": case_id,
                "visa_type": complete_data["case_info"]["visa_type"],
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "packet_statistics": {
                    "total_documents_uploaded": total_documents,
                    "documents_included": included_documents,
                    "total_pages": total_pages,
                    "avg_quality_score": round(avg_quality, 2),
                    "forms_completed": complete_data["statistics"]["forms_completed"],
                    "letters_generated": complete_data["statistics"]["letters_generated"]
                },
                "quality_assessment": {
                    "overall_score": min(100, int(avg_quality * 100)),
                    "completeness": "complete" if included_documents >= total_documents * 0.8 else "incomplete",
                    "critical_issues": len(critical_issues),
                    "total_issues": len(all_issues),
                    "recommendation": self._get_packet_recommendation(avg_quality, len(critical_issues))
                },
                "document_breakdown": self._get_document_breakdown(complete_data["documents"])
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error generating packet metadata: {e}")
            raise
    
    def _get_packet_recommendation(self, avg_quality: float, critical_issues: int) -> str:
        """
        Gera recomendação baseada na qualidade do pacote
        """
        if critical_issues > 0:
            return "NEEDS_CORRECTION"
        elif avg_quality >= 0.9:
            return "READY_FOR_SUBMISSION"
        elif avg_quality >= 0.7:
            return "REVIEW_RECOMMENDED"
        else:
            return "NEEDS_IMPROVEMENT"
    
    def _get_document_breakdown(self, documents: List[Dict]) -> Dict[str, Any]:
        """
        Gera breakdown dos documentos por categoria
        """
        categories = {}
        
        for doc in documents:
            doc_type = doc.get("document_type", "other")
            category = self._get_document_category(doc_type)
            
            if category not in categories:
                categories[category] = {
                    "count": 0,
                    "included": 0,
                    "avg_quality": 0.0,
                    "documents": []
                }
            
            categories[category]["count"] += 1
            if doc["include_in_packet"]:
                categories[category]["included"] += 1
            
            categories[category]["documents"].append({
                "filename": doc["filename"],
                "quality": doc["confidence_score"],
                "included": doc["include_in_packet"]
            })
        
        # Calcular médias de qualidade por categoria
        for category in categories:
            docs = categories[category]["documents"]
            if docs:
                avg_quality = sum(d["quality"] for d in docs) / len(docs)
                categories[category]["avg_quality"] = round(avg_quality, 2)
        
        return categories
    
    def _get_document_category(self, document_type: str) -> str:
        """
        Mapeia tipos de documento para categorias
        """
        category_map = {
            "passport": "Identity Documents",
            "birth_certificate": "Identity Documents", 
            "marriage_certificate": "Identity Documents",
            "diploma": "Educational Documents",
            "transcript": "Educational Documents",
            "certificate": "Educational Documents",
            "employment_letter": "Employment Documents",
            "i797": "USCIS Documents",
            "paystub": "Employment Documents",
            "tax_return": "Financial Documents",
            "bank_statement": "Financial Documents",
            "medical_exam": "Medical Documents",
            "i129": "Official Forms",
            "i485": "Official Forms",
            "cover_letter": "Supporting Letters"
        }
        
        return category_map.get(document_type.lower(), "Other Documents")

# Instância global será injetada pelo servidor principal
real_data_integrator: Optional[RealDataIntegrator] = None