"""
Sistema de Métricas Passivo - Não-Intrusivo
Coleta métricas sem afetar funcionalidade atual
"""

from .passive_collector import passive_metrics, PassiveMetricsCollector
from .instrumentation import monitor_document_analysis, enable_instrumentation, disable_instrumentation
from .endpoints import metrics_router

__version__ = "1.0.0"
__all__ = [
    "passive_metrics",
    "PassiveMetricsCollector", 
    "monitor_document_analysis",
    "enable_instrumentation",
    "disable_instrumentation",
    "metrics_router"
]