"""
Analytics Data Collector
Sistema de coleta de dados para analytics avançados
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import psutil
import time
from contextlib import asynccontextmanager

from .models import (
    AnalyticsEvent, EventType, DocumentProcessingMetrics,
    UserJourneyMetrics, AIModelMetrics, BusinessIntelligenceMetrics,
    SystemHealthMetrics, PerformanceBenchmark
)

logger = logging.getLogger(__name__)

class AnalyticsCollector:
    """
    Advanced analytics data collector
    Coleta dados em tempo real para análises avançadas
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collections = {
            'events': db.analytics_events,
            'document_metrics': db.document_processing_metrics,
            'journey_metrics': db.user_journey_metrics,
            'ai_metrics': db.ai_model_metrics,
            'business_metrics': db.business_intelligence_metrics,
            'system_health': db.system_health_metrics,
            'benchmarks': db.performance_benchmarks
        }
        
        # Performance monitoring
        self.active_sessions = {}
        self.processing_times = {}
        
        # Metrics cache for real-time dashboards
        self.metrics_cache = {}
        self.cache_ttl = 60  # seconds
        
    async def track_event(self, event: AnalyticsEvent) -> str:
        """Track general analytics event"""
        try:
            result = await self.collections['events'].insert_one(event.dict())
            
            # Update real-time metrics cache
            await self._update_realtime_cache(event)
            
            logger.debug(f"Analytics event tracked: {event.event_type} - {event.id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to track analytics event: {e}")
            return ""
    
    async def track_document_processing(self, metrics: DocumentProcessingMetrics) -> str:
        """Track document processing metrics"""
        try:
            result = await self.collections['document_metrics'].insert_one(metrics.dict())
            
            # Update document processing cache
            await self._update_document_metrics_cache(metrics)
            
            logger.info(f"Document processing metrics tracked: {metrics.validator_type} - {metrics.confidence_score}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to track document processing metrics: {e}")
            return ""
    
    async def track_user_journey(self, metrics: UserJourneyMetrics) -> str:
        """Track user journey metrics"""
        try:
            # Update existing journey or create new one
            existing = await self.collections['journey_metrics'].find_one({
                "session_id": metrics.session_id
            })
            
            if existing:
                # Update existing journey
                await self.collections['journey_metrics'].update_one(
                    {"session_id": metrics.session_id},
                    {"$set": metrics.dict(exclude={'id', 'created_at'})}
                )
                journey_id = existing['id']
            else:
                # Create new journey
                result = await self.collections['journey_metrics'].insert_one(metrics.dict())
                journey_id = str(result.inserted_id)
            
            # Update journey metrics cache
            await self._update_journey_metrics_cache(metrics)
            
            logger.debug(f"User journey metrics updated: {metrics.session_id}")
            return journey_id
            
        except Exception as e:
            logger.error(f"Failed to track user journey metrics: {e}")
            return ""
    
    async def track_ai_model_performance(self, metrics: AIModelMetrics) -> str:
        """Track AI model performance metrics"""
        try:
            result = await self.collections['ai_metrics'].insert_one(metrics.dict())
            
            # Update AI performance cache
            await self._update_ai_metrics_cache(metrics)
            
            logger.debug(f"AI model metrics tracked: {metrics.model_name} - {metrics.response_time_ms}ms")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to track AI model metrics: {e}")
            return ""
    
    async def collect_system_health(self) -> SystemHealthMetrics:
        """Collect current system health metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get application-specific metrics
            active_requests = len(self.active_sessions)
            
            # Calculate requests per minute from recent events
            one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
            recent_requests = await self.collections['events'].count_documents({
                "event_type": EventType.API_CALL.value,
                "timestamp": {"$gte": one_minute_ago}
            })
            
            # Calculate average response time from recent API calls
            pipeline = [
                {
                    "$match": {
                        "event_type": EventType.API_CALL.value,
                        "timestamp": {"$gte": one_minute_ago},
                        "duration_ms": {"$exists": True}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "avg_response_time": {"$avg": "$duration_ms"},
                        "error_count": {
                            "$sum": {
                                "$cond": [{"$eq": ["$success", False]}, 1, 0]
                            }
                        },
                        "total_count": {"$sum": 1}
                    }
                }
            ]
            
            api_stats = await self.collections['events'].aggregate(pipeline).to_list(1)
            avg_response_time = api_stats[0]['avg_response_time'] if api_stats else 0
            error_rate = (api_stats[0]['error_count'] / max(api_stats[0]['total_count'], 1) * 100) if api_stats else 0
            
            # Check AI service health
            ai_service_status = await self._check_ai_services_health()
            
            # Get document processing queue size
            documents_in_queue = await self._get_processing_queue_size()
            
            # Generate alerts
            alerts = self._generate_health_alerts(cpu_percent, memory.percent, error_rate)
            
            health_metrics = SystemHealthMetrics(
                cpu_usage_percent=cpu_percent,
                memory_usage_percent=memory.percent,
                disk_usage_percent=disk.percent,
                active_requests=active_requests,
                requests_per_minute=recent_requests,
                average_response_time_ms=avg_response_time,
                error_rate_percent=error_rate,
                database_connections=10,  # Placeholder - would need actual DB monitoring
                query_average_time_ms=50,  # Placeholder
                ai_service_status=ai_service_status,
                ai_queue_size=0,  # Placeholder
                documents_in_queue=documents_in_queue,
                ocr_processing_active=0,  # Placeholder
                active_alerts=alerts
            )
            
            # Store health metrics
            await self.collections['system_health'].insert_one(health_metrics.dict())
            
            return health_metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system health metrics: {e}")
            # Return default metrics in case of error
            return SystemHealthMetrics(
                cpu_usage_percent=0,
                memory_usage_percent=0,
                disk_usage_percent=0,
                active_requests=0,
                requests_per_minute=0,
                average_response_time_ms=0,
                error_rate_percent=0,
                database_connections=0,
                query_average_time_ms=0,
                active_alerts=["Failed to collect system metrics"]
            )
    
    async def generate_daily_business_metrics(self, date: datetime.date = None) -> BusinessIntelligenceMetrics:
        """Generate daily business intelligence metrics"""
        if not date:
            date = datetime.utcnow().date()
        
        try:
            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())
            
            # New users
            new_users = await self.collections['events'].count_documents({
                "event_type": EventType.USER_SIGNUP.value,
                "timestamp": {"$gte": start_of_day, "$lte": end_of_day}
            })
            
            # Active users
            active_users = len(await self.collections['events'].distinct("user_id", {
                "timestamp": {"$gte": start_of_day, "$lte": end_of_day},
                "user_id": {"$exists": True, "$ne": None}
            }))
            
            # Cases started and completed
            cases_started = await self.collections['events'].count_documents({
                "event_type": EventType.CASE_STARTED.value,
                "timestamp": {"$gte": start_of_day, "$lte": end_of_day}
            })
            
            cases_completed = await self.collections['events'].count_documents({
                "event_type": EventType.CASE_COMPLETED.value,
                "timestamp": {"$gte": start_of_day, "$lte": end_of_day}
            })
            
            conversion_rate = (cases_completed / max(cases_started, 1)) * 100
            
            # Document metrics
            documents_uploaded = await self.collections['events'].count_documents({
                "event_type": EventType.DOCUMENT_UPLOADED.value,
                "timestamp": {"$gte": start_of_day, "$lte": end_of_day}
            })
            
            # Get average processing time
            doc_metrics = await self.collections['document_metrics'].find({
                "created_at": {"$gte": start_of_day, "$lte": end_of_day}
            }).to_list(None)
            
            avg_processing_time = sum(m['total_processing_time_ms'] for m in doc_metrics) / max(len(doc_metrics), 1)
            
            # Visa type distribution
            visa_distribution = {}
            visa_events = await self.collections['events'].find({
                "event_type": EventType.FORM_SELECTED.value,
                "timestamp": {"$gte": start_of_day, "$lte": end_of_day}
            }).to_list(None)
            
            for event in visa_events:
                visa_type = event.get('properties', {}).get('visa_type', 'unknown')
                visa_distribution[visa_type] = visa_distribution.get(visa_type, 0) + 1
            
            # Country distribution (placeholder - would need geo data)
            country_distribution = {"US": active_users // 2, "BR": active_users // 2}
            
            business_metrics = BusinessIntelligenceMetrics(
                date=date,
                new_users=new_users,
                active_users=active_users,
                returning_users=max(0, active_users - new_users),
                cases_started=cases_started,
                cases_completed=cases_completed,
                conversion_rate=conversion_rate,
                documents_uploaded=documents_uploaded,
                documents_processed=len(doc_metrics),
                average_processing_time_ms=avg_processing_time,
                visa_type_distribution=visa_distribution,
                country_distribution=country_distribution
            )
            
            # Store business metrics
            await self.collections['business_metrics'].insert_one(business_metrics.dict())
            
            return business_metrics
            
        except Exception as e:
            logger.error(f"Failed to generate business metrics: {e}")
            return BusinessIntelligenceMetrics(date=date)
    
    @asynccontextmanager
    async def track_processing_time(self, operation_name: str, context: Dict[str, Any] = None):
        """Context manager to track processing time"""
        start_time = time.time()
        operation_id = f"{operation_name}_{int(start_time * 1000)}"
        
        try:
            yield operation_id
        except Exception as e:
            # Track error event
            await self.track_event(AnalyticsEvent(
                event_type=EventType.ERROR_OCCURRED,
                properties={
                    "operation": operation_name,
                    "error": str(e),
                    **(context or {})
                },
                duration_ms=(time.time() - start_time) * 1000,
                success=False,
                error_message=str(e)
            ))
            raise
        finally:
            # Track processing time
            duration_ms = (time.time() - start_time) * 1000
            await self.track_event(AnalyticsEvent(
                event_type=EventType.PROCESSING_TIME,
                properties={
                    "operation": operation_name,
                    **(context or {})
                },
                duration_ms=duration_ms,
                success=True
            ))
    
    # Private helper methods
    async def _update_realtime_cache(self, event: AnalyticsEvent):
        """Update real-time metrics cache"""
        cache_key = f"realtime_{event.event_type.value}"
        current_time = datetime.utcnow()
        
        if cache_key not in self.metrics_cache:
            self.metrics_cache[cache_key] = {
                'count': 0,
                'last_updated': current_time
            }
        
        self.metrics_cache[cache_key]['count'] += 1
        self.metrics_cache[cache_key]['last_updated'] = current_time
    
    async def _update_document_metrics_cache(self, metrics: DocumentProcessingMetrics):
        """Update document processing metrics cache"""
        cache_key = f"document_{metrics.validator_type}"
        
        if cache_key not in self.metrics_cache:
            self.metrics_cache[cache_key] = {
                'total_processed': 0,
                'total_processing_time': 0,
                'confidence_scores': [],
                'success_count': 0
            }
        
        cache = self.metrics_cache[cache_key]
        cache['total_processed'] += 1
        cache['total_processing_time'] += metrics.total_processing_time_ms
        cache['confidence_scores'].append(metrics.confidence_score)
        
        if metrics.validation_status == 'VALID':
            cache['success_count'] += 1
    
    async def _update_journey_metrics_cache(self, metrics: UserJourneyMetrics):
        """Update user journey metrics cache"""
        cache_key = "user_journey"
        
        if cache_key not in self.metrics_cache:
            self.metrics_cache[cache_key] = {
                'active_sessions': 0,
                'completed_sessions': 0,
                'dropped_sessions': 0
            }
        
        cache = self.metrics_cache[cache_key]
        
        if metrics.completed_case:
            cache['completed_sessions'] += 1
        elif metrics.dropped_off:
            cache['dropped_sessions'] += 1
        else:
            cache['active_sessions'] += 1
    
    async def _update_ai_metrics_cache(self, metrics: AIModelMetrics):
        """Update AI performance metrics cache"""
        cache_key = f"ai_{metrics.model_name}"
        
        if cache_key not in self.metrics_cache:
            self.metrics_cache[cache_key] = {
                'total_requests': 0,
                'total_response_time': 0,
                'success_count': 0,
                'error_count': 0
            }
        
        cache = self.metrics_cache[cache_key]
        cache['total_requests'] += 1
        cache['total_response_time'] += metrics.response_time_ms
        
        if metrics.success:
            cache['success_count'] += 1
        else:
            cache['error_count'] += 1
    
    async def _check_ai_services_health(self) -> Dict[str, str]:
        """Check health of AI services"""
        # This would integrate with actual AI service health checks
        return {
            "dr_paula": "healthy",
            "document_validator": "healthy",
            "ocr_engine": "healthy",
            "translation_service": "healthy"
        }
    
    async def _get_processing_queue_size(self) -> int:
        """Get current document processing queue size"""
        # This would check actual processing queue
        return 0
    
    def _generate_health_alerts(self, cpu: float, memory: float, error_rate: float) -> List[str]:
        """Generate system health alerts"""
        alerts = []
        
        if cpu > 80:
            alerts.append(f"High CPU usage: {cpu:.1f}%")
        if memory > 85:
            alerts.append(f"High memory usage: {memory:.1f}%")
        if error_rate > 5:
            alerts.append(f"High error rate: {error_rate:.1f}%")
        
        return alerts
    
    def get_cached_metrics(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached metrics if available and not expired"""
        if cache_key in self.metrics_cache:
            cache_entry = self.metrics_cache[cache_key]
            if 'last_updated' in cache_entry:
                time_diff = (datetime.utcnow() - cache_entry['last_updated']).seconds
                if time_diff < self.cache_ttl:
                    return cache_entry
        return None

# Global collector instance
analytics_collector = None

def get_analytics_collector() -> AnalyticsCollector:
    """Get global analytics collector instance"""
    global analytics_collector
    if analytics_collector is None:
        raise RuntimeError("Analytics collector not initialized")
    return analytics_collector

def init_analytics_collector(db: AsyncIOMotorDatabase):
    """Initialize global analytics collector"""
    global analytics_collector
    analytics_collector = AnalyticsCollector(db)