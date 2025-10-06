"""
Pipeline Integration Module
Integra o pipeline modular com o sistema atual de forma não-intrusiva
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from .pipeline_framework import DocumentAnalysisPipeline
from .passport_stages import passport_pipeline, PassportOCRStage, MRZParsingStage
from .i797_stages import i797_pipeline, I797OCRStage, I797ValidationStage
from .birth_certificate_validator import birth_certificate_validation_stage
from .i765_validator import i765_validation_stage

logger = logging.getLogger(__name__)

# Create individual stage instances for pipeline factory
passport_ocr_stage = PassportOCRStage()
passport_mrz_stage = MRZParsingStage()
i797_ocr_stage = I797OCRStage()
i797_validation_stage = I797ValidationStage()

class PipelineIntegrator:
    """
    Integrador que permite usar pipeline modular como alternativa ao sistema atual
    """
    
    def __init__(self):
        self.enabled = True
        self.fallback_to_legacy = True
        self.document_type_mapping = {
            'passport': passport_pipeline,
            'i797_notice': i797_pipeline,
            'i797': i797_pipeline,
            'uscis_notice': i797_pipeline,
            # Mais pipelines serão adicionados aqui
        }
    
    async def analyze_document_with_pipeline(self, 
                                           document_id: str,
                                           document_type: str,
                                           content_base64: str,
                                           filename: str,
                                           legacy_analyze_function=None) -> Dict[str, Any]:
        """
        Analisa documento usando pipeline modular com fallback para sistema legado
        
        Args:
            document_id: ID do documento
            document_type: Tipo detectado (passport, etc)
            content_base64: Conteúdo base64
            filename: Nome do arquivo
            legacy_analyze_function: Função legada para fallback
            
        Returns:
            Resultado da análise no formato compatível
        """
        
        if not self.enabled:
            logger.info("Pipeline disabled, using legacy system")
            return await self._fallback_to_legacy(legacy_analyze_function, 
                                                document_id, content_base64, filename)
        
        try:
            # Detectar pipeline apropriado baseado no tipo de documento
            pipeline = self._get_pipeline_for_document(document_type, content_base64)
            
            if not pipeline:
                logger.info(f"No specialized pipeline for document type: {document_type}, using legacy")
                return await self._fallback_to_legacy(legacy_analyze_function,
                                                    document_id, content_base64, filename)
            
            logger.info(f"Using {pipeline.pipeline_name} for document {document_id}")
            
            # Processar documento através do pipeline
            result = await pipeline.process_document(
                document_id=document_id,
                document_type=document_type,
                content_base64=content_base64,
                filename=filename
            )
            
            # Adicionar metadados sobre o método usado
            result['processing_method'] = 'modular_pipeline'
            result['pipeline_used'] = pipeline.pipeline_name
            
            logger.info(f"Pipeline analysis completed for {document_id}. "
                       f"Verdict: {result.get('pipeline_analysis', {}).get('verdict', 'Unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline analysis failed for {document_id}: {e}")
            
            if self.fallback_to_legacy and legacy_analyze_function:
                logger.info("Falling back to legacy system due to pipeline error")
                return await self._fallback_to_legacy(legacy_analyze_function,
                                                    document_id, content_base64, filename)
            else:
                raise
    
    def _get_pipeline_for_document(self, document_type: str, content_base64: str) -> Optional[Any]:
        """
        Determina qual pipeline usar baseado no tipo de documento
        """
        # Mapeamento direto por tipo
        if document_type.lower() in self.document_type_mapping:
            return self.document_type_mapping[document_type.lower()]
        
        # Detecção baseada em conteúdo (fallback)
        return self._detect_pipeline_from_content(content_base64)
    
    def _detect_pipeline_from_content(self, content_base64: str) -> Optional[Any]:
        """
        Detecta pipeline baseado no conteúdo do documento
        Análise simples de conteúdo para escolher pipeline apropriado
        """
        try:
            # In production, would analyze actual content
            # For now, simple content-based detection
            
            # Mock content analysis - in reality would decode and analyze image/text
            import random
            
            # Simulate content detection based on probability
            # 35% passport, 18% I-797, 47% outros
            rand = random.random()
            
            if rand < 0.35:
                return passport_pipeline
            elif rand < 0.53:  # 35% + 18% = 53%
                return i797_pipeline
            else:
                # For other document types, default to passport pipeline for now
                return passport_pipeline
                
        except Exception as e:
            logger.error(f"Content detection error: {e}")
            return passport_pipeline
    
    async def _fallback_to_legacy(self, legacy_function, document_id: str, 
                                content_base64: str, filename: str) -> Dict[str, Any]:
        """
        Executa fallback para sistema legado
        """
        if not legacy_function:
            # Se não temos função legada, criar resposta básica
            return {
                "completeness_score": 50,
                "validity_status": "unknown",
                "key_information": ["Processamento pelo sistema legado não disponível"],
                "missing_information": [],
                "suggestions": ["Sistema modular em desenvolvimento"],
                "expiration_warnings": [],
                "quality_issues": [],
                "next_steps": ["Aguardar implementação completa"],
                "processing_method": "legacy_unavailable"
            }
        
        try:
            # Criar mock UserDocument para compatibilidade
            from server import UserDocument
            
            mock_document = UserDocument(
                name=filename,
                content_base64=content_base64,
                size=len(content_base64) * 3 // 4,  # Approximate size
                content_type="application/octet-stream"
            )
            
            # Chamar função legada
            result = await legacy_function(mock_document)
            result['processing_method'] = 'legacy_fallback'
            
            return result
            
        except Exception as e:
            logger.error(f"Legacy fallback failed: {e}")
            return {
                "completeness_score": 25,
                "validity_status": "error",
                "key_information": ["Erro no sistema legado"],
                "missing_information": [str(e)],
                "suggestions": ["Tentar novamente"],
                "expiration_warnings": [],
                "quality_issues": ["Fallback system error"],
                "next_steps": ["Contactar suporte"],
                "processing_method": "legacy_error"
            }
    
    def enable_pipeline(self):
        """Ativa uso do pipeline modular"""
        self.enabled = True
        logger.info("Pipeline integration enabled")
    
    def disable_pipeline(self):
        """Desativa uso do pipeline modular (força uso do legado)"""
        self.enabled = False
        logger.info("Pipeline integration disabled - using legacy only")
    
    def enable_fallback(self):
        """Ativa fallback para sistema legado em caso de erro"""
        self.fallback_to_legacy = True
        logger.info("Legacy fallback enabled")
    
    def disable_fallback(self):
        """Desativa fallback (pipeline deve sempre funcionar ou falhar)"""
        self.fallback_to_legacy = False
        logger.info("Legacy fallback disabled")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Retorna status da integração"""
        return {
            'pipeline_enabled': self.enabled,
            'fallback_enabled': self.fallback_to_legacy,
            'available_pipelines': list(self.document_type_mapping.keys()),
            'default_pipeline': 'passport',
            'integration_version': '2.0.0'
        }

def create_document_pipeline(document_type: str) -> Pipeline:
    """
    Create a specialized pipeline based on document type
    
    Args:
        document_type: Type of document (passport, i797, birth_certificate, i765, etc.)
    
    Returns:
        Configured Pipeline instance
    """
    pipeline_name = f"{document_type}_pipeline"
    
    # Create pipeline based on document type
    if document_type.lower() in ['passport', 'passaporte']:
        pipeline = Pipeline(pipeline_name)
        pipeline.add_stage(passport_ocr_stage)
        pipeline.add_stage(passport_mrz_stage)
        
    elif document_type.lower() in ['i797', 'i-797', 'notice_of_action']:
        pipeline = Pipeline(pipeline_name)
        pipeline.add_stage(i797_ocr_stage)
        pipeline.add_stage(i797_validation_stage)
        
    elif document_type.lower() in ['birth_certificate', 'birth_cert', 'certidao_nascimento', 'certidão_nascimento']:
        pipeline = Pipeline(pipeline_name)
        pipeline.add_stage(birth_certificate_validation_stage)
        
    elif document_type.lower() in ['i765', 'i-765', 'ead', 'employment_authorization', 'employment_authorization_document']:
        pipeline = Pipeline(pipeline_name)
        pipeline.add_stage(i765_validation_stage)
        
    else:
        # Generic pipeline for unknown document types
        logger.warning(f"Unknown document type: {document_type}, using generic pipeline")
        pipeline = Pipeline(f"generic_{document_type}_pipeline")
        # Add basic OCR stage for unknown documents
        # This can be expanded with more generic stages
        
    logger.info(f"Created pipeline for document type: {document_type}")
    return pipeline

# Global integrator instance
pipeline_integrator = PipelineIntegrator()