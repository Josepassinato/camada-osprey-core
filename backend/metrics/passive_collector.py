"""
Sistema de Coleta Passiva de Métricas - Implementação Segura
Não interfere no funcionamento atual, apenas coleta dados para análise
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import deque, defaultdict
import statistics

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    PASSPORT = "passport"
    BIRTH_CERTIFICATE = "birth_certificate" 
    MARRIAGE_CERT = "marriage_certificate"
    I797_NOTICE = "i797_notice"
    I94_RECORD = "i94_record"
    TAX_RETURN = "tax_return"
    EMPLOYMENT_LETTER = "employment_letter"
    DEGREE_CERTIFICATE = "degree_certificate"
    UNKNOWN = "unknown"

@dataclass
class DocumentAnalysisMetric:
    """Métrica individual de análise de documento"""
    document_id: str
    document_type: str
    analysis_start_time: float
    analysis_end_time: float
    processing_time_ms: float
    confidence_score: float
    verdict: str  # APROVADO, REJEITADO, NECESSITA_REVISÃO
    ai_agent_used: str  # dr_miguel, dra_paula, etc
    user_session: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

@dataclass 
class PerformanceSnapshot:
    """Snapshot de performance do sistema"""
    total_documents_analyzed: int
    avg_processing_time_ms: float
    p95_processing_time_ms: float
    success_rate: float
    confidence_distribution: Dict[str, int]
    document_type_distribution: Dict[str, int]
    hourly_throughput: float
    timestamp: datetime
    
class PassiveMetricsCollector:
    """
    Coletor passivo que não interfere no funcionamento atual
    Thread-safe e com impacto mínimo na performance
    """
    
    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size
        self.metrics_history = deque(maxlen=max_history_size)
        self.performance_snapshots = deque(maxlen=168)  # 1 semana de snapshots hourly
        self._lock = threading.RLock()
        self.enabled = True
        
        # Contadores em tempo real (thread-safe)
        self.real_time_stats = {
            'total_documents': 0,
            'documents_last_hour': 0,
            'last_reset_time': time.time()
        }
        
        logger.info("✅ PassiveMetricsCollector initialized (non-intrusive mode)")
    
    def record_document_analysis(self, 
                               document_id: str,
                               document_type: str,
                               start_time: float,
                               end_time: float,
                               confidence: float,
                               verdict: str,
                               ai_agent: str = "dr_miguel",
                               user_session: str = None) -> None:
        """
        Registra métrica de análise de documento de forma thread-safe
        Esta função é chamada de forma passiva, não bloqueia o fluxo principal
        """
        if not self.enabled:
            return
            
        try:
            processing_time = (end_time - start_time) * 1000  # Convert to ms
            
            metric = DocumentAnalysisMetric(
                document_id=document_id,
                document_type=document_type,
                analysis_start_time=start_time,
                analysis_end_time=end_time,
                processing_time_ms=processing_time,
                confidence_score=confidence,
                verdict=verdict,
                ai_agent_used=ai_agent,
                user_session=user_session
            )
            
            with self._lock:
                self.metrics_history.append(metric)
                self.real_time_stats['total_documents'] += 1
                self.real_time_stats['documents_last_hour'] += 1
                
                # Reset hourly counter
                current_time = time.time()
                if current_time - self.real_time_stats['last_reset_time'] >= 3600:  # 1 hour
                    self.real_time_stats['documents_last_hour'] = 0
                    self.real_time_stats['last_reset_time'] = current_time
                    
        except Exception as e:
            # Nunca deve falhar - apenas log silent
            logger.debug(f"Metrics collection error (non-critical): {e}")
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Retorna resumo de performance das últimas N horas
        Operação read-only, não afeta performance
        """
        with self._lock:
            if not self.metrics_history:
                return self._empty_summary()
            
            # Filter metrics for the specified timeframe
            cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)
            recent_metrics = [
                m for m in self.metrics_history 
                if m.analysis_end_time >= cutoff_time
            ]
            
            if not recent_metrics:
                return self._empty_summary()
            
            return self._calculate_performance_stats(recent_metrics, hours)
    
    def _calculate_performance_stats(self, metrics: List[DocumentAnalysisMetric], hours: int) -> Dict[str, Any]:
        """Calcula estatísticas de performance"""
        processing_times = [m.processing_time_ms for m in metrics]
        confidences = [m.confidence_score for m in metrics]
        verdicts = [m.verdict for m in metrics]
        doc_types = [m.document_type for m in metrics]
        
        # Performance stats
        avg_processing_time = statistics.mean(processing_times)
        p95_processing_time = statistics.quantiles(processing_times, n=20)[18] if len(processing_times) >= 20 else max(processing_times)
        
        # Success rate (APROVADO + NECESSITA_REVISÃO como success)
        successful = sum(1 for v in verdicts if v in ['APROVADO', 'NECESSITA_REVISÃO'])
        success_rate = successful / len(verdicts) if verdicts else 0
        
        # Confidence distribution
        confidence_ranges = {
            '90-100%': sum(1 for c in confidences if c >= 90),
            '70-89%': sum(1 for c in confidences if 70 <= c < 90),
            '50-69%': sum(1 for c in confidences if 50 <= c < 70),
            '<50%': sum(1 for c in confidences if c < 50)
        }
        
        # Document type distribution
        doc_type_counts = defaultdict(int)
        for doc_type in doc_types:
            doc_type_counts[doc_type] += 1
        
        return {
            'timeframe_hours': hours,
            'total_documents': len(metrics),
            'avg_processing_time_ms': round(avg_processing_time, 2),
            'p95_processing_time_ms': round(p95_processing_time, 2),
            'success_rate': round(success_rate, 4),
            'avg_confidence': round(statistics.mean(confidences), 2),
            'confidence_distribution': dict(confidence_ranges),
            'document_type_distribution': dict(doc_type_counts),
            'throughput_per_hour': len(metrics) / hours if hours > 0 else 0,
            'verdict_distribution': {
                verdict: verdicts.count(verdict) for verdict in set(verdicts)
            }
        }
    
    def _empty_summary(self) -> Dict[str, Any]:
        """Retorna summary vazio quando não há dados"""
        return {
            'timeframe_hours': 0,
            'total_documents': 0,
            'avg_processing_time_ms': 0,
            'p95_processing_time_ms': 0,
            'success_rate': 0,
            'avg_confidence': 0,
            'confidence_distribution': {'90-100%': 0, '70-89%': 0, '50-69%': 0, '<50%': 0},
            'document_type_distribution': {},
            'throughput_per_hour': 0,
            'verdict_distribution': {}
        }
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas em tempo real"""
        with self._lock:
            return {
                'total_documents_processed': self.real_time_stats['total_documents'],
                'documents_last_hour': self.real_time_stats['documents_last_hour'],
                'metrics_history_size': len(self.metrics_history),
                'collector_enabled': self.enabled,
                'last_update': datetime.now(timezone.utc).isoformat()
            }
    
    def enable(self):
        """Ativa coleta de métricas"""
        self.enabled = True
        logger.info("✅ Metrics collection enabled")
    
    def disable(self):
        """Desativa coleta de métricas"""
        self.enabled = False
        logger.info("⏸️ Metrics collection disabled")
    
    def clear_history(self):
        """Limpa histórico de métricas (útil para reset)"""
        with self._lock:
            self.metrics_history.clear()
            self.real_time_stats = {
                'total_documents': 0,
                'documents_last_hour': 0,
                'last_reset_time': time.time()
            }
        logger.info("🗑️ Metrics history cleared")
    
    def export_metrics_json(self, hours: int = 24) -> str:
        """Exporta métricas em formato JSON"""
        summary = self.get_performance_summary(hours)
        real_time = self.get_real_time_stats()
        
        export_data = {
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'performance_summary': summary,
            'real_time_stats': real_time,
            'system_info': {
                'collector_version': '1.0.0',
                'max_history_size': self.max_history_size,
                'current_history_size': len(self.metrics_history)
            }
        }
        
        return json.dumps(export_data, indent=2)

# Instância global (singleton pattern)
passive_metrics = PassiveMetricsCollector()