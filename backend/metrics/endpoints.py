"""
Endpoints de Métricas - Separados dos endpoints principais
Não modifica funcionalidade existente, apenas adiciona observabilidade
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import logging
from .passive_collector import passive_metrics
from .instrumentation import enable_instrumentation, disable_instrumentation

logger = logging.getLogger(__name__)

# Router separado para métricas
metrics_router = APIRouter(prefix="/metrics", tags=["metrics"])

@metrics_router.get("/health")
async def metrics_health_check():
    """Health check do sistema de métricas"""
    return {
        "status": "healthy",
        "collector_enabled": passive_metrics.enabled,
        "metrics_count": len(passive_metrics.metrics_history),
        "version": "1.0.0"
    }

@metrics_router.get("/summary")
async def get_performance_summary(hours: int = Query(24, ge=1, le=168)):
    """
    Retorna resumo de performance das últimas N horas
    
    Args:
        hours: Número de horas para análise (1-168)
    """
    try:
        summary = passive_metrics.get_performance_summary(hours)
        return {
            "status": "success",
            "data": summary,
            "note": "Metrics collected passively - no impact on current functionality"
        }
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving metrics")

@metrics_router.get("/realtime")
async def get_realtime_stats():
    """Estatísticas em tempo real"""
    try:
        stats = passive_metrics.get_real_time_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting realtime stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving realtime stats")

@metrics_router.get("/dashboard")
async def get_dashboard_data():
    """
    Dados completos para dashboard de métricas
    Combina resumo + estatísticas em tempo real
    """
    try:
        summary_24h = passive_metrics.get_performance_summary(24)
        summary_1h = passive_metrics.get_performance_summary(1)
        realtime = passive_metrics.get_real_time_stats()
        
        return {
            "status": "success",
            "data": {
                "last_24_hours": summary_24h,
                "last_hour": summary_1h,
                "realtime": realtime,
                "trends": {
                    "hourly_vs_daily_throughput": {
                        "hourly": summary_1h.get('throughput_per_hour', 0),
                        "daily_avg": summary_24h.get('throughput_per_hour', 0)
                    }
                }
            },
            "metadata": {
                "dashboard_version": "1.0.0",
                "data_freshness": "real-time",
                "collection_method": "passive"
            }
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving dashboard data")

@metrics_router.get("/export")
async def export_metrics(hours: int = Query(24, ge=1, le=168)):
    """
    Exporta métricas em formato JSON para análise externa
    
    Args:
        hours: Número de horas para exportar
    """
    try:
        export_data = passive_metrics.export_metrics_json(hours)
        return {
            "status": "success",
            "export_data": export_data,
            "content_type": "application/json"
        }
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}")
        raise HTTPException(status_code=500, detail="Error exporting metrics")

@metrics_router.post("/control/enable")
async def enable_metrics_collection():
    """Ativa coleta de métricas"""
    try:
        enable_instrumentation()
        return {
            "status": "success",
            "message": "Metrics collection enabled",
            "collector_status": passive_metrics.enabled
        }
    except Exception as e:
        logger.error(f"Error enabling metrics: {e}")
        raise HTTPException(status_code=500, detail="Error enabling metrics collection")

@metrics_router.post("/control/disable")
async def disable_metrics_collection():
    """Desativa coleta de métricas"""
    try:
        disable_instrumentation()
        return {
            "status": "success", 
            "message": "Metrics collection disabled",
            "collector_status": passive_metrics.enabled
        }
    except Exception as e:
        logger.error(f"Error disabling metrics: {e}")
        raise HTTPException(status_code=500, detail="Error disabling metrics collection")

@metrics_router.post("/control/clear")
async def clear_metrics_history():
    """
    Limpa histórico de métricas
    Útil para reset ou quando dados ficam muito antigos
    """
    try:
        old_count = len(passive_metrics.metrics_history)
        passive_metrics.clear_history()
        
        return {
            "status": "success",
            "message": f"Cleared {old_count} metrics from history",
            "current_count": len(passive_metrics.metrics_history)
        }
    except Exception as e:
        logger.error(f"Error clearing metrics: {e}")
        raise HTTPException(status_code=500, detail="Error clearing metrics history")

@metrics_router.get("/analysis/document-types")
async def analyze_document_type_performance(hours: int = Query(24, ge=1, le=168)):
    """
    Análise detalhada de performance por tipo de documento
    """
    try:
        summary = passive_metrics.get_performance_summary(hours)
        doc_distribution = summary.get('document_type_distribution', {})
        
        # Calcular performance por tipo (se temos dados suficientes)
        analysis = {}
        for doc_type, count in doc_distribution.items():
            if count > 0:
                analysis[doc_type] = {
                    "total_documents": count,
                    "percentage_of_total": round((count / summary['total_documents']) * 100, 2) if summary['total_documents'] > 0 else 0,
                    "note": "Detailed performance metrics coming in next phase"
                }
        
        return {
            "status": "success",
            "timeframe_hours": hours,
            "analysis": analysis,
            "total_documents": summary['total_documents']
        }
    except Exception as e:
        logger.error(f"Error analyzing document types: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing document type performance")

@metrics_router.get("/kpis/baseline")
async def get_baseline_kpis():
    """
    Retorna KPIs baseline para estabelecer targets
    Esta é a base para a implementação completa de KPIs
    """
    try:
        summary = passive_metrics.get_performance_summary(168)  # 1 week
        
        # KPIs básicos que podemos calcular agora
        baseline_kpis = {
            "current_performance": {
                "avg_processing_time_ms": summary.get('avg_processing_time_ms', 0),
                "p95_processing_time_ms": summary.get('p95_processing_time_ms', 0),
                "success_rate": summary.get('success_rate', 0),
                "avg_confidence": summary.get('avg_confidence', 0),
                "throughput_per_hour": summary.get('throughput_per_hour', 0)
            },
            "targets": {
                "processing_time_ms": 5000,
                "success_rate": 0.95,
                "confidence_score": 85,
                "throughput_per_hour": 100,
                "note": "Targets from high-precision plan"
            },
            "gaps_identified": {
                "missing_f1_score": "Not yet implemented - needs ground truth data",
                "missing_exact_match": "Not yet implemented - needs field-level validation",
                "missing_false_fail_rate": "Not yet implemented - needs human review data"
            }
        }
        
        return {
            "status": "success",
            "baseline_established": True,
            "data": baseline_kpis,
            "next_steps": [
                "Collect ground truth data for F1 score calculation",
                "Implement field-level exact match tracking",
                "Add human review feedback loop",
                "Enable advanced KPI monitoring"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting baseline KPIs: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving baseline KPIs")