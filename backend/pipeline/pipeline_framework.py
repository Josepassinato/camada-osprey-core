"""
Modular Pipeline Framework - Base Architecture
Framework base para pipeline modular de análise de documentos
"""

import time
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class PipelineContext:
    """Context object que passa pelos estágios do pipeline"""
    
    # Input data
    document_id: str
    document_type: str
    content_base64: str
    filename: str
    
    # Processing results (accumulated through pipeline)
    ocr_results: Dict[str, Any] = field(default_factory=dict)
    classification_results: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    mrz_data: Optional[Any] = None
    printed_data: Dict[str, Any] = field(default_factory=dict)
    
    # Pipeline metadata
    processing_start_time: float = field(default_factory=time.time)
    stage_results: Dict[str, Dict] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Final results
    final_confidence: float = 0.0
    final_verdict: str = "PENDING"
    should_stop: bool = False

class PipelineStage(ABC):
    """
    Base class para estágios do pipeline
    """
    
    def __init__(self, stage_name: str, enabled: bool = True):
        self.stage_name = stage_name
        self.enabled = enabled
        self.metrics = {
            'total_processed': 0,
            'total_time': 0.0,
            'success_count': 0,
            'error_count': 0
        }
    
    @abstractmethod
    async def process(self, context: PipelineContext) -> PipelineContext:
        """
        Processa o contexto e retorna contexto modificado
        Deve ser implementado por cada estágio específico
        """
        pass
    
    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        Wrapper que executa o estágio com métricas e error handling
        """
        if not self.enabled:
            logger.debug(f"Stage {self.stage_name} is disabled, skipping")
            context.stage_results[self.stage_name] = {
                'status': ProcessingStatus.SKIPPED.value,
                'message': 'Stage disabled'
            }
            return context
        
        start_time = time.time()
        
        try:
            logger.info(f"Starting stage: {self.stage_name}")
            
            # Execute stage processing
            result_context = await self.process(context)
            
            # Record success metrics
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, success=True)
            
            # Record stage result
            result_context.stage_results[self.stage_name] = {
                'status': ProcessingStatus.COMPLETED.value,
                'processing_time_ms': processing_time * 1000,
                'timestamp': time.time()
            }
            
            logger.info(f"Completed stage: {self.stage_name} in {processing_time:.3f}s")
            return result_context
            
        except Exception as e:
            # Record error metrics
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, success=False)
            
            error_msg = f"Stage {self.stage_name} failed: {str(e)}"
            logger.error(error_msg)
            
            context.errors.append(error_msg)
            context.stage_results[self.stage_name] = {
                'status': ProcessingStatus.FAILED.value,
                'error': error_msg,
                'processing_time_ms': processing_time * 1000,
                'timestamp': time.time()
            }
            
            return context
    
    def _update_metrics(self, processing_time: float, success: bool):
        """Atualiza métricas do estágio"""
        self.metrics['total_processed'] += 1
        self.metrics['total_time'] += processing_time
        
        if success:
            self.metrics['success_count'] += 1
        else:
            self.metrics['error_count'] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance do estágio"""
        total = self.metrics['total_processed']
        return {
            'stage_name': self.stage_name,
            'total_processed': total,
            'success_rate': self.metrics['success_count'] / total if total > 0 else 0,
            'avg_processing_time_ms': (self.metrics['total_time'] / total * 1000) if total > 0 else 0,
            'total_time_seconds': self.metrics['total_time'],
            'enabled': self.enabled
        }

class DocumentAnalysisPipeline:
    """
    Pipeline principal para análise de documentos
    Executa estágios de forma sequencial com controle de erro
    """
    
    def __init__(self, pipeline_name: str = "DocumentAnalysis"):
        self.pipeline_name = pipeline_name
        self.stages: List[PipelineStage] = []
        self.enabled = True
        
        # Pipeline-level metrics
        self.pipeline_metrics = {
            'total_documents': 0,
            'successful_documents': 0,
            'failed_documents': 0,
            'total_pipeline_time': 0.0
        }
    
    def add_stage(self, stage: PipelineStage) -> 'DocumentAnalysisPipeline':
        """Adiciona estágio ao pipeline"""
        self.stages.append(stage)
        logger.info(f"Added stage: {stage.stage_name} to pipeline {self.pipeline_name}")
        return self
    
    def add_stages(self, stages: List[PipelineStage]) -> 'DocumentAnalysisPipeline':
        """Adiciona múltiplos estágios ao pipeline"""
        for stage in stages:
            self.add_stage(stage)
        return self
    
    async def process_document(self, 
                             document_id: str,
                             document_type: str,
                             content_base64: str,
                             filename: str,
                             **kwargs) -> Dict[str, Any]:
        """
        Processa documento através do pipeline completo
        
        Returns:
            Dict com resultados finais no formato esperado pelo sistema atual
        """
        if not self.enabled:
            logger.warning(f"Pipeline {self.pipeline_name} is disabled")
            return self._create_fallback_result(document_id, "Pipeline disabled")
        
        pipeline_start = time.time()
        
        try:
            # Create pipeline context
            context = PipelineContext(
                document_id=document_id,
                document_type=document_type,
                content_base64=content_base64,
                filename=filename
            )
            
            # Execute all stages sequentially
            for stage in self.stages:
                if context.should_stop:
                    logger.warning(f"Pipeline execution stopped at stage: {stage.stage_name}")
                    break
                
                context = await stage.execute(context)
            
            # Calculate final results
            pipeline_time = time.time() - pipeline_start
            final_results = self._compile_final_results(context, pipeline_time)
            
            # Update pipeline metrics
            self._update_pipeline_metrics(pipeline_time, success=len(context.errors) == 0)
            
            return final_results
            
        except Exception as e:
            pipeline_time = time.time() - pipeline_start
            error_msg = f"Pipeline execution failed: {str(e)}"
            logger.error(error_msg)
            
            self._update_pipeline_metrics(pipeline_time, success=False)
            
            return self._create_fallback_result(document_id, error_msg)
    
    def _compile_final_results(self, context: PipelineContext, pipeline_time: float) -> Dict[str, Any]:
        """
        Compila resultados finais no formato esperado pelo sistema atual
        Mantém compatibilidade com a interface existente
        """
        # Extract key metrics
        has_errors = len(context.errors) > 0
        has_warnings = len(context.warnings) > 0
        
        # Determine final confidence and verdict
        if context.final_confidence > 0:
            confidence = context.final_confidence
        else:
            # Calculate based on stage successes
            successful_stages = sum(
                1 for result in context.stage_results.values() 
                if result.get('status') == ProcessingStatus.COMPLETED.value
            )
            total_stages = len(self.stages)
            confidence = (successful_stages / total_stages * 100) if total_stages > 0 else 50
        
        # Determine verdict
        if context.final_verdict != "PENDING":
            verdict = context.final_verdict
        elif has_errors:
            verdict = "REJEITADO"
        elif confidence >= 85:
            verdict = "APROVADO"
        else:
            verdict = "NECESSITA_REVISÃO"
        
        # Format results in expected structure
        result = {
            # Core analysis results (compatible with existing system)
            "completeness_score": confidence,
            "validity_status": "valid" if not has_errors else "invalid",
            "key_information": self._extract_key_information(context),
            "missing_information": context.errors if has_errors else [],
            "suggestions": self._generate_suggestions(context),
            "expiration_warnings": self._extract_expiration_warnings(context),
            "quality_issues": context.warnings,
            "next_steps": self._generate_next_steps(context, verdict),
            
            # Enhanced pipeline results
            "pipeline_analysis": {
                "verdict": verdict,
                "confidence_score": confidence,
                "pipeline_name": self.pipeline_name,
                "processing_time_ms": pipeline_time * 1000,
                "stages_executed": len(context.stage_results),
                "stages_successful": sum(
                    1 for result in context.stage_results.values() 
                    if result.get('status') == ProcessingStatus.COMPLETED.value
                ),
                "has_errors": has_errors,
                "has_warnings": has_warnings
            },
            
            # Detailed stage results (for debugging/monitoring)
            "stage_results": context.stage_results,
            
            # Specialized results (if available)
            "mrz_data": context.mrz_data,
            "ocr_results": context.ocr_results,
            "classification_results": context.classification_results,
            "validation_results": context.validation_results
        }
        
        return result
    
    def _extract_key_information(self, context: PipelineContext) -> List[str]:
        """Extrai informações-chave do contexto"""
        info = []
        
        if context.mrz_data:
            info.append(f"Document type: {getattr(context.mrz_data, 'document_type', 'Unknown')}")
            info.append(f"MRZ validation: {'Valid' if getattr(context.mrz_data, 'checksum_valid', False) else 'Invalid'}")
        
        if context.ocr_results:
            confidence = context.ocr_results.get('ocr_confidence', 0)
            info.append(f"OCR confidence: {confidence:.1%}")
        
        if context.classification_results:
            doc_type = context.classification_results.get('document_type', 'Unknown')
            info.append(f"Classified as: {doc_type}")
        
        return info if info else ["Documento processado pelo pipeline modular"]
    
    def _generate_suggestions(self, context: PipelineContext) -> List[str]:
        """Gera sugestões baseadas nos resultados"""
        suggestions = []
        
        if context.errors:
            suggestions.append("Revisar problemas identificados na validação")
        
        if context.warnings:
            suggestions.append("Atenção aos avisos de qualidade identificados")
        
        if context.mrz_data and hasattr(context.mrz_data, 'confidence_score'):
            if context.mrz_data.confidence_score < 0.8:
                suggestions.append("Considerar nova digitalização com melhor qualidade")
        
        return suggestions if suggestions else ["Documento processado com sucesso"]
    
    def _extract_expiration_warnings(self, context: PipelineContext) -> List[str]:
        """Extrai avisos de expiração"""
        warnings = []
        
        if context.mrz_data and hasattr(context.mrz_data, 'expiry_date'):
            from datetime import date, timedelta
            expiry = context.mrz_data.expiry_date
            today = date.today()
            
            if expiry < today:
                warnings.append("Documento expirado")
            elif expiry < today + timedelta(days=180):
                days_left = (expiry - today).days
                warnings.append(f"Documento expira em {days_left} dias")
        
        return warnings
    
    def _generate_next_steps(self, context: PipelineContext, verdict: str) -> List[str]:
        """Gera próximos passos recomendados"""
        if verdict == "APROVADO":
            return ["Documento validado - prosseguir com aplicação"]
        elif verdict == "REJEITADO":
            return ["Corrigir problemas identificados", "Fornecer documento válido"]
        else:
            return ["Revisão manual recomendada", "Verificar pontos de atenção"]
    
    def _create_fallback_result(self, document_id: str, error_msg: str) -> Dict[str, Any]:
        """Cria resultado de fallback quando pipeline falha"""
        return {
            "completeness_score": 25,
            "validity_status": "error",
            "key_information": ["Erro no processamento do pipeline"],
            "missing_information": [error_msg],
            "suggestions": ["Tentar novamente ou usar sistema anterior"],
            "expiration_warnings": [],
            "quality_issues": ["Pipeline execution failed"],
            "next_steps": ["Contactar suporte técnico"],
            "pipeline_analysis": {
                "verdict": "ERROR",
                "confidence_score": 0.0,
                "pipeline_name": self.pipeline_name,
                "error": error_msg
            }
        }
    
    def _update_pipeline_metrics(self, processing_time: float, success: bool):
        """Atualiza métricas do pipeline"""
        self.pipeline_metrics['total_documents'] += 1
        self.pipeline_metrics['total_pipeline_time'] += processing_time
        
        if success:
            self.pipeline_metrics['successful_documents'] += 1
        else:
            self.pipeline_metrics['failed_documents'] += 1
    
    def get_pipeline_performance(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance do pipeline completo"""
        total = self.pipeline_metrics['total_documents']
        
        pipeline_stats = {
            'pipeline_name': self.pipeline_name,
            'total_documents_processed': total,
            'success_rate': self.pipeline_metrics['successful_documents'] / total if total > 0 else 0,
            'avg_processing_time_ms': (self.pipeline_metrics['total_pipeline_time'] / total * 1000) if total > 0 else 0,
            'total_processing_time': self.pipeline_metrics['total_pipeline_time'],
            'enabled': self.enabled,
            'stages_count': len(self.stages)
        }
        
        # Add individual stage statistics
        stage_stats = [stage.get_performance_stats() for stage in self.stages]
        
        return {
            'pipeline': pipeline_stats,
            'stages': stage_stats
        }
    
    def enable_stage(self, stage_name: str):
        """Ativa estágio específico"""
        for stage in self.stages:
            if stage.stage_name == stage_name:
                stage.enabled = True
                logger.info(f"Enabled stage: {stage_name}")
                return
        logger.warning(f"Stage not found: {stage_name}")
    
    def disable_stage(self, stage_name: str):
        """Desativa estágio específico"""
        for stage in self.stages:
            if stage.stage_name == stage_name:
                stage.enabled = False
                logger.info(f"Disabled stage: {stage_name}")
                return
        logger.warning(f"Stage not found: {stage_name}")
    
    def enable_pipeline(self):
        """Ativa pipeline completo"""
        self.enabled = True
        logger.info(f"Enabled pipeline: {self.pipeline_name}")
    
    def disable_pipeline(self):
        """Desativa pipeline completo"""
        self.enabled = False
        logger.info(f"Disabled pipeline: {self.pipeline_name}")