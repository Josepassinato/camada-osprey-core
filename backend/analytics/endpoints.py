"""
Advanced Analytics API Endpoints
Endpoints para dashboards avançados de analytics
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, date, timedelta
import logging

from .models import (
    DocumentAnalyticsQuery, UserJourneyQuery, AIPerformanceQuery, AnalyticsQuery,
    DocumentAnalyticsResponse, UserJourneyResponse, AIPerformanceResponse,
    BusinessIntelligenceResponse, SystemHealthResponse
)
from .analyzer import AnalyticsAnalyzer
from .collector import get_analytics_collector

logger = logging.getLogger(__name__)

# Create analytics router
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])

def get_analytics_analyzer() -> AnalyticsAnalyzer:
    """Get analytics analyzer instance"""
    try:
        from server import db  # Import from main server module
        collector = get_analytics_collector()
        return AnalyticsAnalyzer(db, collector)
    except Exception as e:
        logger.error(f"Failed to get analytics analyzer: {e}")
        raise HTTPException(status_code=500, detail="Analytics service unavailable")

@analytics_router.get("/health")
async def analytics_health_check():
    """Health check for analytics service"""
    try:
        collector = get_analytics_collector()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "cache_size": len(collector.metrics_cache),
            "services": ["collector", "analyzer", "endpoints"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Document Processing Analytics
@analytics_router.post("/documents/analysis", response_model=DocumentAnalyticsResponse)
async def analyze_document_processing(
    query: DocumentAnalyticsQuery,
    analyzer: AnalyticsAnalyzer = Depends(get_analytics_analyzer)
):
    """
    Analyze document processing performance
    
    Provides insights into:
    - Processing times per validator type
    - Confidence score distributions  
    - Success rates and error patterns
    - Performance trends over time
    """
    try:
        result = await analyzer.analyze_document_processing(query)
        return result
    except Exception as e:
        logger.error(f"Document analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

@analytics_router.get("/documents/summary")
async def get_document_processing_summary(
    days: int = Query(7, description="Number of days to analyze"),
    validator_types: Optional[List[str]] = Query(None, description="Filter by validator types"),
    analyzer: AnalyticsAnalyzer = Depends(get_analytics_analyzer)
):
    """Get quick summary of document processing metrics"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        query = DocumentAnalyticsQuery(
            start_date=start_date,
            end_date=end_date,
            validator_types=validator_types,
            metrics=["processing_time", "confidence_score", "success_rate"]
        )
        
        result = await analyzer.analyze_document_processing(query)
        
        return {
            "period": f"Last {days} days",
            "total_documents": result.total_documents_processed,
            "average_processing_time_ms": result.average_processing_time_ms,
            "average_confidence_score": result.average_confidence_score,
            "success_rate": result.success_rate,
            "top_performing_validator": max(
                result.validator_performance.items(), 
                key=lambda x: x[1]['success_rate']
            )[0] if result.validator_performance else None
        }
    except Exception as e:
        logger.error(f"Document summary failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get document summary: {str(e)}")

# User Journey Analytics
@analytics_router.post("/journey/analysis", response_model=UserJourneyResponse)
async def analyze_user_journey(
    query: UserJourneyQuery,
    analyzer: AnalyticsAnalyzer = Depends(get_analytics_analyzer)
):
    """
    Analyze user journey and conversion funnel
    
    Provides insights into:
    - Conversion rates at each step
    - Drop-off analysis and patterns
    - Time to completion metrics
    - User retry behaviors
    """
    try:
        result = await analyzer.analyze_user_journey(query)
        return result
    except Exception as e:
        logger.error(f"Journey analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Journey analysis failed: {str(e)}")

@analytics_router.get("/journey/funnel")
async def get_conversion_funnel(
    days: int = Query(30, description="Number of days to analyze"),
    visa_types: Optional[List[str]] = Query(None, description="Filter by visa types"),
    analyzer: AnalyticsAnalyzer = Depends(get_analytics_analyzer)
):
    """Get conversion funnel data for specified period"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        query = UserJourneyQuery(
            start_date=start_date,
            end_date=end_date,
            visa_types=visa_types,
            metrics=["conversion_funnel", "drop_off_analysis"]
        )
        
        result = await analyzer.analyze_user_journey(query)
        
        return {
            "period": f"Last {days} days",
            "total_sessions": result.total_sessions,
            "conversion_funnel": result.conversion_funnel,
            "drop_off_analysis": result.drop_off_analysis,
            "overall_conversion_rate": result.conversion_funnel.get('case_completed', {}).get('percentage', 0)
        }
    except Exception as e:
        logger.error(f"Funnel analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversion funnel: {str(e)}")

# AI Performance Analytics
@analytics_router.post("/ai/analysis", response_model=AIPerformanceResponse)
async def analyze_ai_performance(
    query: AIPerformanceQuery,
    analyzer: AnalyticsAnalyzer = Depends(get_analytics_analyzer)
):
    """
    Analyze AI model performance
    
    Provides insights into:
    - Response times and throughput
    - Success rates and error patterns
    - Model-specific performance metrics
    - Confidence score distributions
    """
    try:
        result = await analyzer.analyze_ai_performance(query)
        return result
    except Exception as e:
        logger.error(f"AI analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@analytics_router.get("/ai/models/performance")
async def get_ai_models_performance(
    hours: int = Query(24, description="Number of hours to analyze"),
    model_names: Optional[List[str]] = Query(None, description="Filter by model names"),
    analyzer: AnalyticsAnalyzer = Depends(get_analytics_analyzer)
):
    """Get AI models performance summary"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=hours//24 + 1)
        
        query = AIPerformanceQuery(
            start_date=start_date,
            end_date=end_date,
            model_names=model_names,
            metrics=["response_time", "success_rate", "error_distribution"]
        )
        
        result = await analyzer.analyze_ai_performance(query)
        
        return {
            "period": f"Last {hours} hours",
            "total_requests": result.total_requests,
            "average_response_time_ms": result.average_response_time_ms,
            "success_rate": result.success_rate,
            "models_analyzed": len(result.model_performance),
            "fastest_model": min(
                result.model_performance.items(),
                key=lambda x: x[1]['average_response_time_ms']
            )[0] if result.model_performance else None,
            "most_reliable_model": max(
                result.model_performance.items(),
                key=lambda x: x[1]['success_rate']
            )[0] if result.model_performance else None
        }
    except Exception as e:
        logger.error(f"AI performance summary failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI performance: {str(e)}")

# Business Intelligence Analytics
@analytics_router.post("/business/analysis", response_model=BusinessIntelligenceResponse)
async def analyze_business_intelligence(
    query: AnalyticsQuery,
    analyzer: AnalyticsAnalyzer = Depends(get_analytics_analyzer)
):
    """
    Analyze business intelligence metrics
    
    Provides insights into:
    - User acquisition and retention
    - Visa type popularity trends
    - Geographic distribution
    - Revenue and growth metrics
    """
    try:
        result = await analyzer.analyze_business_intelligence(query)
        return result
    except Exception as e:
        logger.error(f"Business analytics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Business analysis failed: {str(e)}")

@analytics_router.get("/business/dashboard")
async def get_business_dashboard(
    period: str = Query("monthly", description="Period: daily, weekly, monthly"),
    analyzer: AnalyticsAnalyzer = Depends(get_analytics_analyzer)
):
    """Get business dashboard overview"""
    try:
        # Determine date range based on period
        end_date = date.today()
        if period == "daily":
            start_date = end_date - timedelta(days=1)
        elif period == "weekly":
            start_date = end_date - timedelta(weeks=1)
        else:  # monthly
            start_date = end_date - timedelta(days=30)
        
        query = AnalyticsQuery(
            start_date=start_date,
            end_date=end_date,
            group_by="summary",
            metrics=["users", "cases", "revenue", "growth"]
        )
        
        result = await analyzer.analyze_business_intelligence(query)
        
        return {
            "period": period,
            "date_range": f"{start_date} to {end_date}",
            "overview": {
                "total_users": result.total_users,
                "total_cases": result.total_cases,
                "revenue": result.revenue,
                "growth_metrics": result.growth_metrics
            },
            "insights": {
                "top_visa_type": result.visa_type_insights.get('most_popular_visa'),
                "top_country": result.geographic_insights.get('top_countries', [{}])[0] if result.geographic_insights.get('top_countries') else None,
                "user_growth_rate": result.growth_metrics.get('user_growth_rate', 0),
                "case_growth_rate": result.growth_metrics.get('case_growth_rate', 0)
            }
        }
    except Exception as e:
        logger.error(f"Business dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get business dashboard: {str(e)}")

# System Health and Real-time Monitoring
@analytics_router.get("/system/health", response_model=SystemHealthResponse)
async def get_system_health(
    analyzer: AnalyticsAnalyzer = Depends(get_analytics_analyzer)
):
    """
    Get real-time system health status
    
    Provides real-time monitoring of:
    - System resources (CPU, memory, disk)
    - API performance and error rates
    - Service health status
    - Active alerts and recommendations
    """
    try:
        result = await analyzer.get_system_health_status()
        return result
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"System health check failed: {str(e)}")

@analytics_router.get("/system/realtime")
async def get_realtime_metrics(
    analyzer: AnalyticsAnalyzer = Depends(get_analytics_analyzer)
):
    """Get real-time system metrics for dashboard"""
    try:
        collector = get_analytics_collector()
        health = await collector.collect_system_health()
        
        # Get cached metrics for quick response
        cached_metrics = {
            "system_health": {
                "cpu_usage": health.cpu_usage_percent,
                "memory_usage": health.memory_usage_percent,
                "active_requests": health.active_requests,
                "requests_per_minute": health.requests_per_minute,
                "error_rate": health.error_rate_percent,
                "status": "healthy" if health.cpu_usage_percent < 80 and health.memory_usage_percent < 85 else "warning"
            },
            "processing_queue": {
                "documents_in_queue": health.documents_in_queue,
                "ai_queue_size": health.ai_queue_size,
                "ocr_processing_active": health.ocr_processing_active
            },
            "services": health.ai_service_status,
            "alerts": health.active_alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return cached_metrics
    except Exception as e:
        logger.error(f"Real-time metrics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get real-time metrics: {str(e)}")

# Performance Benchmarks
@analytics_router.get("/benchmarks")
async def get_performance_benchmarks(
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    analyzer: AnalyticsAnalyzer = Depends(get_analytics_analyzer)
):
    """Get performance benchmarks and thresholds"""
    try:
        collector = get_analytics_collector()
        
        # Get recent performance data for benchmarking
        benchmarks = {
            "document_processing": {
                "target_processing_time_ms": 5000,
                "target_confidence_score": 0.8,
                "target_success_rate": 95,
                "current_performance": collector.get_cached_metrics("document_processing")
            },
            "ai_models": {
                "target_response_time_ms": 2000,
                "target_success_rate": 98,
                "target_error_rate": 2,
                "current_performance": collector.get_cached_metrics("ai_performance")
            },
            "user_journey": {
                "target_conversion_rate": 60,
                "target_completion_time_hours": 2,
                "target_drop_off_rate": 30,
                "current_performance": collector.get_cached_metrics("user_journey")
            },
            "system_health": {
                "target_cpu_usage": 70,
                "target_memory_usage": 80,
                "target_response_time_ms": 500,
                "target_uptime": 99.9
            }
        }
        
        if metric_type and metric_type in benchmarks:
            return {metric_type: benchmarks[metric_type]}
        
        return benchmarks
    except Exception as e:
        logger.error(f"Benchmarks query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get benchmarks: {str(e)}")

# Custom Analytics Queries
@analytics_router.post("/query/custom")
async def execute_custom_analytics_query(
    query: dict,
    analyzer: AnalyticsAnalyzer = Depends(get_analytics_analyzer)
):
    """
    Execute custom analytics query
    
    Allows for flexible analytics queries with custom filters,
    grouping, and aggregations for advanced analysis needs.
    """
    try:
        # Validate and sanitize custom query
        collection_name = query.get("collection")
        filters = query.get("filters", {})
        group_by = query.get("group_by")
        limit = min(query.get("limit", 1000), 10000)  # Cap at 10k results
        
        if not collection_name or collection_name not in analyzer.collections:
            raise HTTPException(status_code=400, detail="Invalid collection name")
        
        # Execute query
        collection = analyzer.collections[collection_name]
        
        if group_by:
            # Aggregation pipeline
            pipeline = [
                {"$match": filters},
                {"$group": {
                    "_id": f"${group_by}",
                    "count": {"$sum": 1},
                    "avg_value": {"$avg": "$value"} if "value" in query.get("avg_fields", []) else None
                }},
                {"$limit": limit}
            ]
            results = await collection.aggregate([stage for stage in pipeline if stage is not None]).to_list(None)
        else:
            # Simple find
            results = await collection.find(filters).limit(limit).to_list(None)
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "executed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Custom query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Custom query failed: {str(e)}")

# Data Export
@analytics_router.get("/export/{data_type}")
async def export_analytics_data(
    data_type: str,
    start_date: date = Query(..., description="Start date for export"),
    end_date: date = Query(..., description="End date for export"),
    format: str = Query("json", description="Export format: json or csv"),
    analyzer: AnalyticsAnalyzer = Depends(get_analytics_analyzer)
):
    """Export analytics data for external analysis"""
    try:
        if data_type not in ["documents", "journeys", "ai_metrics", "business"]:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        # Build query based on data type
        if data_type == "documents":
            query = DocumentAnalyticsQuery(start_date=start_date, end_date=end_date)
            result = await analyzer.analyze_document_processing(query)
            export_data = result.results
        elif data_type == "journeys":
            query = UserJourneyQuery(start_date=start_date, end_date=end_date)
            result = await analyzer.analyze_user_journey(query)
            export_data = result.results
        elif data_type == "ai_metrics":
            query = AIPerformanceQuery(start_date=start_date, end_date=end_date)
            result = await analyzer.analyze_ai_performance(query)
            export_data = result.results
        else:  # business
            query = AnalyticsQuery(start_date=start_date, end_date=end_date)
            result = await analyzer.analyze_business_intelligence(query)
            export_data = result.results
        
        # Format response
        if format == "csv":
            # Would implement CSV conversion here
            return {"message": "CSV export not implemented yet", "data": export_data}
        else:
            return {
                "data_type": data_type,
                "period": f"{start_date} to {end_date}",
                "format": format,
                "record_count": len(export_data),
                "data": export_data,
                "exported_at": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Data export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Data export failed: {str(e)}")