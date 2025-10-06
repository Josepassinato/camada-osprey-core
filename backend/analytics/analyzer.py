"""
Analytics Data Analyzer
Sistema de análise de dados para dashboards avançados
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import statistics

from .models import (
    AnalyticsQuery, DocumentAnalyticsQuery, UserJourneyQuery, AIPerformanceQuery,
    DocumentAnalyticsResponse, UserJourneyResponse, AIPerformanceResponse,
    BusinessIntelligenceResponse, SystemHealthResponse, SystemHealthMetrics
)
from .collector import AnalyticsCollector

logger = logging.getLogger(__name__)

class AnalyticsAnalyzer:
    """
    Advanced analytics data analyzer
    Processa dados coletados e gera insights para dashboards
    """
    
    def __init__(self, db: AsyncIOMotorDatabase, collector: AnalyticsCollector):
        self.db = db
        self.collector = collector
        self.collections = collector.collections
    
    async def analyze_document_processing(self, query: DocumentAnalyticsQuery) -> DocumentAnalyticsResponse:
        """Analyze document processing performance"""
        try:
            # Build query filters
            match_filter = {
                "created_at": {
                    "$gte": datetime.combine(query.start_date, datetime.min.time()),
                    "$lte": datetime.combine(query.end_date, datetime.max.time())
                }
            }
            
            if query.document_types:
                match_filter["document_type"] = {"$in": query.document_types}
            
            if query.validator_types:
                match_filter["validator_type"] = {"$in": query.validator_types}
            
            if query.confidence_threshold:
                match_filter["confidence_score"] = {"$gte": query.confidence_threshold}
            
            # Get document processing metrics
            documents = await self.collections['document_metrics'].find(match_filter).to_list(None)
            
            if not documents:
                return DocumentAnalyticsResponse(
                    query=query,
                    results=[],
                    summary={},
                    total_documents_processed=0,
                    average_processing_time_ms=0,
                    average_confidence_score=0,
                    success_rate=0,
                    validation_status_distribution={},
                    validator_performance={}
                )
            
            # Calculate metrics
            total_docs = len(documents)
            processing_times = [d['total_processing_time_ms'] for d in documents]
            confidence_scores = [d['confidence_score'] for d in documents]
            
            avg_processing_time = statistics.mean(processing_times)
            avg_confidence = statistics.mean(confidence_scores)
            
            # Validation status distribution
            status_dist = {}
            for doc in documents:
                status = doc['validation_status']
                status_dist[status] = status_dist.get(status, 0) + 1
            
            success_rate = (status_dist.get('VALID', 0) / total_docs) * 100
            
            # Validator performance analysis
            validator_performance = {}
            validators = set(d['validator_type'] for d in documents)
            
            for validator in validators:
                validator_docs = [d for d in documents if d['validator_type'] == validator]
                
                validator_performance[validator] = {
                    'total_processed': len(validator_docs),
                    'average_processing_time_ms': statistics.mean([d['total_processing_time_ms'] for d in validator_docs]),
                    'average_confidence_score': statistics.mean([d['confidence_score'] for d in validator_docs]),
                    'success_rate': (len([d for d in validator_docs if d['validation_status'] == 'VALID']) / len(validator_docs)) * 100,
                    'average_fields_extracted': statistics.mean([d['fields_extracted'] for d in validator_docs]),
                    'common_issues': self._get_common_issues([d['issues_found'] for d in validator_docs])
                }
            
            # Time series data for charts
            results = []
            if query.group_by == 'day':
                results = await self._group_document_metrics_by_day(documents, query.start_date, query.end_date)
            elif query.group_by == 'validator':
                results = [{'validator': v, **metrics} for v, metrics in validator_performance.items()]
            else:
                results = [doc for doc in documents]
            
            return DocumentAnalyticsResponse(
                query=query,
                results=results,
                summary={
                    'date_range': f"{query.start_date} to {query.end_date}",
                    'total_validators': len(validators),
                    'median_processing_time_ms': statistics.median(processing_times),
                    'median_confidence_score': statistics.median(confidence_scores),
                    'processing_time_percentiles': {
                        'p50': statistics.median(processing_times),
                        'p90': statistics.quantiles(processing_times, n=10)[8] if len(processing_times) > 10 else max(processing_times),
                        'p95': statistics.quantiles(processing_times, n=20)[18] if len(processing_times) > 20 else max(processing_times)
                    }
                },
                total_documents_processed=total_docs,
                average_processing_time_ms=avg_processing_time,
                average_confidence_score=avg_confidence,
                success_rate=success_rate,
                validation_status_distribution=status_dist,
                validator_performance=validator_performance
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze document processing: {e}")
            return DocumentAnalyticsResponse(
                query=query,
                results=[],
                summary={'error': str(e)},
                total_documents_processed=0,
                average_processing_time_ms=0,
                average_confidence_score=0,
                success_rate=0,
                validation_status_distribution={},
                validator_performance={}
            )
    
    async def analyze_user_journey(self, query: UserJourneyQuery) -> UserJourneyResponse:
        """Analyze user journey and conversion funnel"""
        try:
            # Build query filters
            match_filter = {
                "created_at": {
                    "$gte": datetime.combine(query.start_date, datetime.min.time()),
                    "$lte": datetime.combine(query.end_date, datetime.max.time())
                }
            }
            
            # Get user journey data
            journeys = await self.collections['journey_metrics'].find(match_filter).to_list(None)
            
            if not journeys:
                return UserJourneyResponse(
                    query=query,
                    results=[],
                    summary={},
                    total_sessions=0,
                    conversion_funnel={},
                    average_time_to_complete_ms=0,
                    drop_off_analysis={},
                    retry_patterns={}
                )
            
            total_sessions = len(journeys)
            
            # Conversion funnel analysis
            funnel_stages = {
                'started': sum(1 for j in journeys),
                'form_selected': sum(1 for j in journeys if j.get('completed_form_selection')),
                'basic_data_completed': sum(1 for j in journeys if j.get('completed_basic_data')),
                'documents_started': sum(1 for j in journeys if j.get('started_document_upload')),
                'documents_completed': sum(1 for j in journeys if j.get('completed_document_upload')),
                'case_completed': sum(1 for j in journeys if j.get('completed_case'))
            }
            
            # Convert to percentages
            conversion_funnel = {}
            for stage, count in funnel_stages.items():
                conversion_funnel[stage] = {
                    'count': count,
                    'percentage': (count / total_sessions) * 100 if total_sessions > 0 else 0
                }
            
            # Drop-off analysis
            drop_off_analysis = {}
            for journey in journeys:
                if journey.get('dropped_off') and journey.get('drop_off_stage'):
                    stage = journey['drop_off_stage']
                    drop_off_analysis[stage] = drop_off_analysis.get(stage, 0) + 1
            
            # Calculate completion times
            completion_times = []
            for journey in journeys:
                if journey.get('case_completion_time') and journey.get('journey_start'):
                    start_time = journey['journey_start']
                    end_time = journey['case_completion_time']
                    if isinstance(start_time, str):
                        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    if isinstance(end_time, str):
                        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    
                    duration = (end_time - start_time).total_seconds() * 1000
                    completion_times.append(duration)
            
            avg_completion_time = statistics.mean(completion_times) if completion_times else 0
            
            # Retry patterns analysis
            retry_patterns = {}
            for journey in journeys:
                if journey.get('retry_attempts'):
                    for stage, attempts in journey['retry_attempts'].items():
                        if stage not in retry_patterns:
                            retry_patterns[stage] = []
                        retry_patterns[stage].append(attempts)
            
            # Calculate average retries per stage
            avg_retry_patterns = {}
            for stage, attempts_list in retry_patterns.items():
                avg_retry_patterns[stage] = statistics.mean(attempts_list)
            
            # Time series data
            results = []
            if query.group_by == 'day':
                results = await self._group_journey_metrics_by_day(journeys, query.start_date, query.end_date)
            else:
                results = journeys
            
            return UserJourneyResponse(
                query=query,
                results=results,
                summary={
                    'date_range': f"{query.start_date} to {query.end_date}",
                    'overall_conversion_rate': conversion_funnel['case_completed']['percentage'],
                    'median_completion_time_ms': statistics.median(completion_times) if completion_times else 0,
                    'completion_rate_by_stage': conversion_funnel
                },
                total_sessions=total_sessions,
                conversion_funnel=conversion_funnel,
                average_time_to_complete_ms=avg_completion_time,
                drop_off_analysis=drop_off_analysis,
                retry_patterns=avg_retry_patterns
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze user journey: {e}")
            return UserJourneyResponse(
                query=query,
                results=[],
                summary={'error': str(e)},
                total_sessions=0,
                conversion_funnel={},
                average_time_to_complete_ms=0,
                drop_off_analysis={},
                retry_patterns={}
            )
    
    async def analyze_ai_performance(self, query: AIPerformanceQuery) -> AIPerformanceResponse:
        """Analyze AI model performance"""
        try:
            # Build query filters
            match_filter = {
                "created_at": {
                    "$gte": datetime.combine(query.start_date, datetime.min.time()),
                    "$lte": datetime.combine(query.end_date, datetime.max.time())
                }
            }
            
            if query.model_names:
                match_filter["model_name"] = {"$in": query.model_names}
            
            if query.success_only:
                match_filter["success"] = True
            
            # Get AI metrics
            ai_metrics = await self.collections['ai_metrics'].find(match_filter).to_list(None)
            
            if not ai_metrics:
                return AIPerformanceResponse(
                    query=query,
                    results=[],
                    summary={},
                    total_requests=0,
                    average_response_time_ms=0,
                    success_rate=0,
                    model_performance={},
                    error_distribution={}
                )
            
            total_requests = len(ai_metrics)
            response_times = [m['response_time_ms'] for m in ai_metrics]
            avg_response_time = statistics.mean(response_times)
            
            success_count = sum(1 for m in ai_metrics if m['success'])
            success_rate = (success_count / total_requests) * 100
            
            # Model performance analysis
            models = set(m['model_name'] for m in ai_metrics)
            model_performance = {}
            
            for model in models:
                model_metrics = [m for m in ai_metrics if m['model_name'] == model]
                model_response_times = [m['response_time_ms'] for m in model_metrics]
                model_success_count = sum(1 for m in model_metrics if m['success'])
                
                # Calculate confidence scores if available
                confidence_scores = [m['confidence_score'] for m in model_metrics if m.get('confidence_score')]
                
                model_performance[model] = {
                    'total_requests': len(model_metrics),
                    'average_response_time_ms': statistics.mean(model_response_times),
                    'median_response_time_ms': statistics.median(model_response_times),
                    'success_rate': (model_success_count / len(model_metrics)) * 100,
                    'average_confidence_score': statistics.mean(confidence_scores) if confidence_scores else None,
                    'p95_response_time_ms': statistics.quantiles(model_response_times, n=20)[18] if len(model_response_times) > 20 else max(model_response_times),
                    'error_count': len(model_metrics) - model_success_count,
                    'requests_by_type': self._analyze_request_types([m.get('request_type') for m in model_metrics])
                }
            
            # Error distribution
            error_distribution = {}
            for metric in ai_metrics:
                if not metric['success'] and metric.get('error_type'):
                    error_type = metric['error_type']
                    error_distribution[error_type] = error_distribution.get(error_type, 0) + 1
            
            # Time series data
            results = []
            if query.group_by == 'day':
                results = await self._group_ai_metrics_by_day(ai_metrics, query.start_date, query.end_date)
            elif query.group_by == 'model':
                results = [{'model': m, **perf} for m, perf in model_performance.items()]
            else:
                results = ai_metrics
            
            return AIPerformanceResponse(
                query=query,
                results=results,
                summary={
                    'date_range': f"{query.start_date} to {query.end_date}",
                    'total_models': len(models),
                    'median_response_time_ms': statistics.median(response_times),
                    'response_time_percentiles': {
                        'p50': statistics.median(response_times),
                        'p90': statistics.quantiles(response_times, n=10)[8] if len(response_times) > 10 else max(response_times),
                        'p95': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times)
                    }
                },
                total_requests=total_requests,
                average_response_time_ms=avg_response_time,
                success_rate=success_rate,
                model_performance=model_performance,
                error_distribution=error_distribution
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze AI performance: {e}")
            return AIPerformanceResponse(
                query=query,
                results=[],
                summary={'error': str(e)},
                total_requests=0,
                average_response_time_ms=0,
                success_rate=0,
                model_performance={},
                error_distribution={}
            )
    
    async def analyze_business_intelligence(self, query: AnalyticsQuery) -> BusinessIntelligenceResponse:
        """Analyze business intelligence metrics"""
        try:
            # Get business metrics for date range
            match_filter = {
                "date": {
                    "$gte": query.start_date,
                    "$lte": query.end_date
                }
            }
            
            business_metrics = await self.collections['business_metrics'].find(match_filter).to_list(None)
            
            if not business_metrics:
                return BusinessIntelligenceResponse(
                    query=query,
                    results=[],
                    summary={},
                    total_users=0,
                    total_cases=0,
                    revenue=0,
                    growth_metrics={},
                    geographic_insights={},
                    visa_type_insights={}
                )
            
            # Aggregate metrics
            total_users = sum(m['new_users'] for m in business_metrics)
            total_cases = sum(m['cases_started'] for m in business_metrics)
            total_revenue = sum(m.get('revenue', 0) for m in business_metrics)
            
            # Growth metrics
            if len(business_metrics) > 1:
                # Sort by date
                sorted_metrics = sorted(business_metrics, key=lambda x: x['date'])
                
                # Calculate growth rates
                first_period = sorted_metrics[0]
                last_period = sorted_metrics[-1]
                
                user_growth = ((last_period['new_users'] - first_period['new_users']) / max(first_period['new_users'], 1)) * 100
                case_growth = ((last_period['cases_started'] - first_period['cases_started']) / max(first_period['cases_started'], 1)) * 100
                revenue_growth = ((last_period.get('revenue', 0) - first_period.get('revenue', 0)) / max(first_period.get('revenue', 1), 1)) * 100
                
                growth_metrics = {
                    'user_growth_rate': user_growth,
                    'case_growth_rate': case_growth,
                    'revenue_growth_rate': revenue_growth,
                    'daily_average_users': total_users / len(business_metrics),
                    'daily_average_cases': total_cases / len(business_metrics)
                }
            else:
                growth_metrics = {
                    'user_growth_rate': 0,
                    'case_growth_rate': 0,
                    'revenue_growth_rate': 0,
                    'daily_average_users': total_users,
                    'daily_average_cases': total_cases
                }
            
            # Geographic insights
            country_totals = {}
            for metric in business_metrics:
                for country, count in metric.get('country_distribution', {}).items():
                    country_totals[country] = country_totals.get(country, 0) + count
            
            geographic_insights = {
                'top_countries': sorted(country_totals.items(), key=lambda x: x[1], reverse=True)[:10],
                'total_countries': len(country_totals),
                'country_distribution': country_totals
            }
            
            # Visa type insights
            visa_totals = {}
            for metric in business_metrics:
                for visa_type, count in metric.get('visa_type_distribution', {}).items():
                    visa_totals[visa_type] = visa_totals.get(visa_type, 0) + count
            
            visa_type_insights = {
                'most_popular_visa': max(visa_totals.items(), key=lambda x: x[1])[0] if visa_totals else None,
                'visa_distribution': visa_totals,
                'total_visa_types': len(visa_totals)
            }
            
            # Time series data
            results = business_metrics if query.group_by != 'summary' else []
            
            return BusinessIntelligenceResponse(
                query=query,
                results=results,
                summary={
                    'date_range': f"{query.start_date} to {query.end_date}",
                    'period_days': (query.end_date - query.start_date).days + 1,
                    'average_conversion_rate': statistics.mean([m['conversion_rate'] for m in business_metrics]) if business_metrics else 0
                },
                total_users=total_users,
                total_cases=total_cases,
                revenue=total_revenue,
                growth_metrics=growth_metrics,
                geographic_insights=geographic_insights,
                visa_type_insights=visa_type_insights
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze business intelligence: {e}")
            return BusinessIntelligenceResponse(
                query=query,
                results=[],
                summary={'error': str(e)},
                total_users=0,
                total_cases=0,
                revenue=0,
                growth_metrics={},
                geographic_insights={},
                visa_type_insights={}
            )
    
    async def get_system_health_status(self) -> SystemHealthResponse:
        """Get current system health status"""
        try:
            # Get latest system health metrics
            latest_health = await self.collector.collect_system_health()
            
            # Determine overall status
            overall_status = "healthy"
            
            if (latest_health.cpu_usage_percent > 80 or 
                latest_health.memory_usage_percent > 85 or 
                latest_health.error_rate_percent > 5):
                overall_status = "degraded"
            
            if (latest_health.cpu_usage_percent > 95 or 
                latest_health.memory_usage_percent > 95 or 
                latest_health.error_rate_percent > 10):
                overall_status = "critical"
            
            # Service statuses
            service_statuses = {
                "database": "healthy" if latest_health.database_connections > 0 else "degraded",
                "api_server": "healthy" if latest_health.average_response_time_ms < 2000 else "degraded",
                **latest_health.ai_service_status
            }
            
            # Generate recommendations
            recommendations = []
            if latest_health.cpu_usage_percent > 70:
                recommendations.append("Consider scaling up CPU resources")
            if latest_health.memory_usage_percent > 80:
                recommendations.append("Monitor memory usage and consider optimization")
            if latest_health.error_rate_percent > 3:
                recommendations.append("Investigate API errors and implement fixes")
            if latest_health.average_response_time_ms > 1000:
                recommendations.append("Optimize API response times")
            
            return SystemHealthResponse(
                overall_status=overall_status,
                system_metrics=latest_health,
                service_statuses=service_statuses,
                active_alerts=latest_health.active_alerts,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to get system health status: {e}")
            return SystemHealthResponse(
                overall_status="unknown",
                system_metrics=SystemHealthMetrics(
                    cpu_usage_percent=0,
                    memory_usage_percent=0,
                    disk_usage_percent=0,
                    active_requests=0,
                    requests_per_minute=0,
                    average_response_time_ms=0,
                    error_rate_percent=0,
                    database_connections=0,
                    query_average_time_ms=0,
                    active_alerts=[f"Failed to collect system health: {e}"]
                ),
                service_statuses={"all": "unknown"},
                active_alerts=[f"System health check failed: {e}"],
                recommendations=["Check system health monitoring setup"]
            )
    
    # Helper methods for time series grouping
    async def _group_document_metrics_by_day(self, documents: List[Dict], start_date: date, end_date: date) -> List[Dict]:
        """Group document metrics by day"""
        daily_groups = {}
        
        current_date = start_date
        while current_date <= end_date:
            daily_groups[current_date] = []
            current_date += timedelta(days=1)
        
        for doc in documents:
            doc_date = doc['created_at'].date()
            if doc_date in daily_groups:
                daily_groups[doc_date].append(doc)
        
        results = []
        for date_key, docs in daily_groups.items():
            if docs:
                results.append({
                    'date': date_key.isoformat(),
                    'documents_processed': len(docs),
                    'average_processing_time': statistics.mean([d['total_processing_time_ms'] for d in docs]),
                    'average_confidence': statistics.mean([d['confidence_score'] for d in docs]),
                    'success_rate': (len([d for d in docs if d['validation_status'] == 'VALID']) / len(docs)) * 100
                })
            else:
                results.append({
                    'date': date_key.isoformat(),
                    'documents_processed': 0,
                    'average_processing_time': 0,
                    'average_confidence': 0,
                    'success_rate': 0
                })
        
        return results
    
    async def _group_journey_metrics_by_day(self, journeys: List[Dict], start_date: date, end_date: date) -> List[Dict]:
        """Group journey metrics by day"""
        daily_groups = {}
        
        current_date = start_date
        while current_date <= end_date:
            daily_groups[current_date] = []
            current_date += timedelta(days=1)
        
        for journey in journeys:
            journey_date = journey['created_at'].date()
            if journey_date in daily_groups:
                daily_groups[journey_date].append(journey)
        
        results = []
        for date_key, day_journeys in daily_groups.items():
            if day_journeys:
                completed = len([j for j in day_journeys if j.get('completed_case')])
                results.append({
                    'date': date_key.isoformat(),
                    'sessions_started': len(day_journeys),
                    'sessions_completed': completed,
                    'conversion_rate': (completed / len(day_journeys)) * 100,
                    'dropped_sessions': len([j for j in day_journeys if j.get('dropped_off')])
                })
            else:
                results.append({
                    'date': date_key.isoformat(),
                    'sessions_started': 0,
                    'sessions_completed': 0,
                    'conversion_rate': 0,
                    'dropped_sessions': 0
                })
        
        return results
    
    async def _group_ai_metrics_by_day(self, ai_metrics: List[Dict], start_date: date, end_date: date) -> List[Dict]:
        """Group AI metrics by day"""
        daily_groups = {}
        
        current_date = start_date
        while current_date <= end_date:
            daily_groups[current_date] = []
            current_date += timedelta(days=1)
        
        for metric in ai_metrics:
            metric_date = metric['created_at'].date()
            if metric_date in daily_groups:
                daily_groups[metric_date].append(metric)
        
        results = []
        for date_key, day_metrics in daily_groups.items():
            if day_metrics:
                success_count = len([m for m in day_metrics if m['success']])
                results.append({
                    'date': date_key.isoformat(),
                    'total_requests': len(day_metrics),
                    'successful_requests': success_count,
                    'success_rate': (success_count / len(day_metrics)) * 100,
                    'average_response_time': statistics.mean([m['response_time_ms'] for m in day_metrics])
                })
            else:
                results.append({
                    'date': date_key.isoformat(),
                    'total_requests': 0,
                    'successful_requests': 0,
                    'success_rate': 0,
                    'average_response_time': 0
                })
        
        return results
    
    def _get_common_issues(self, issues_lists: List[List[str]]) -> List[Tuple[str, int]]:
        """Get most common issues from lists of issues"""
        issue_counts = {}
        
        for issues_list in issues_lists:
            for issue in issues_list:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        # Return top 5 most common issues
        return sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _analyze_request_types(self, request_types: List[str]) -> Dict[str, int]:
        """Analyze distribution of AI request types"""
        type_counts = {}
        
        for req_type in request_types:
            if req_type:
                type_counts[req_type] = type_counts.get(req_type, 0) + 1
        
        return type_counts