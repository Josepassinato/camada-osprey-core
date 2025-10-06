"""
Performance Monitoring System - Advanced Metrics
Sistema avançado de monitoramento de performance
"""

import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    operation: str
    duration: float
    timestamp: datetime
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OperationStats:
    """Statistics for a specific operation"""
    operation_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    avg_duration: float = 0.0
    percentile_95: float = 0.0
    success_rate: float = 0.0
    
    # Recent measurements for percentile calculation
    recent_durations: deque = field(default_factory=lambda: deque(maxlen=1000))

class PerformanceMonitor:
    """
    Advanced performance monitoring system
    """
    
    def __init__(self, max_metrics: int = 10000):
        self.metrics: deque = deque(maxlen=max_metrics)
        self.operation_stats: Dict[str, OperationStats] = {}
        self.alert_thresholds = {
            'ocr_processing': {'max_duration': 5.0, 'min_success_rate': 0.9},
            'document_validation': {'max_duration': 2.0, 'min_success_rate': 0.95},
            'consistency_check': {'max_duration': 3.0, 'min_success_rate': 0.85}
        }
        self.alerts = []
    
    def record_metric(self, 
                     operation: str, 
                     duration: float, 
                     success: bool = True,
                     metadata: Dict[str, Any] = None):
        """Record a performance metric"""
        
        metric = PerformanceMetric(
            operation=operation,
            duration=duration,
            timestamp=datetime.now(),
            success=success,
            metadata=metadata or {}
        )
        
        self.metrics.append(metric)
        self._update_operation_stats(metric)
        self._check_alerts(operation)
    
    def _update_operation_stats(self, metric: PerformanceMetric):
        """Update statistics for an operation"""
        
        operation = metric.operation
        if operation not in self.operation_stats:
            self.operation_stats[operation] = OperationStats(operation_name=operation)
        
        stats = self.operation_stats[operation]
        
        # Update counters
        stats.total_calls += 1
        if metric.success:
            stats.successful_calls += 1
        else:
            stats.failed_calls += 1
        
        # Update duration stats
        stats.total_duration += metric.duration
        stats.min_duration = min(stats.min_duration, metric.duration)
        stats.max_duration = max(stats.max_duration, metric.duration)
        stats.avg_duration = stats.total_duration / stats.total_calls
        
        # Add to recent durations for percentile calculation
        stats.recent_durations.append(metric.duration)
        
        # Calculate percentiles
        if len(stats.recent_durations) >= 10:
            sorted_durations = sorted(stats.recent_durations)
            p95_index = int(0.95 * len(sorted_durations))
            stats.percentile_95 = sorted_durations[p95_index]
        
        # Update success rate
        stats.success_rate = stats.successful_calls / stats.total_calls
    
    def _check_alerts(self, operation: str):
        """Check if operation exceeds alert thresholds"""
        
        if operation not in self.alert_thresholds:
            return
        
        stats = self.operation_stats.get(operation)
        if not stats or stats.total_calls < 5:  # Need minimum data
            return
        
        thresholds = self.alert_thresholds[operation]
        
        # Check duration threshold
        if 'max_duration' in thresholds and stats.avg_duration > thresholds['max_duration']:
            alert = {
                'type': 'PERFORMANCE_DEGRADATION',
                'operation': operation,
                'metric': 'avg_duration',
                'current_value': stats.avg_duration,
                'threshold': thresholds['max_duration'],
                'timestamp': datetime.now(),
                'severity': 'WARNING' if stats.avg_duration < thresholds['max_duration'] * 1.5 else 'CRITICAL'
            }
            self.alerts.append(alert)
            logger.warning(f"Performance alert: {operation} average duration {stats.avg_duration:.2f}s exceeds threshold {thresholds['max_duration']}s")
        
        # Check success rate threshold
        if 'min_success_rate' in thresholds and stats.success_rate < thresholds['min_success_rate']:
            alert = {
                'type': 'SUCCESS_RATE_DROP',
                'operation': operation,
                'metric': 'success_rate',
                'current_value': stats.success_rate,
                'threshold': thresholds['min_success_rate'],
                'timestamp': datetime.now(),
                'severity': 'CRITICAL' if stats.success_rate < 0.8 else 'WARNING'
            }
            self.alerts.append(alert)
            logger.warning(f"Performance alert: {operation} success rate {stats.success_rate:.2%} below threshold {thresholds['min_success_rate']:.2%}")
    
    def get_operation_stats(self, operation: str = None) -> Dict[str, Any]:
        """Get statistics for specific operation or all operations"""
        
        if operation:
            stats = self.operation_stats.get(operation)
            if not stats:
                return {}
            
            return {
                'operation_name': stats.operation_name,
                'total_calls': stats.total_calls,
                'successful_calls': stats.successful_calls,
                'failed_calls': stats.failed_calls,
                'success_rate_percent': round(stats.success_rate * 100, 2),
                'avg_duration_seconds': round(stats.avg_duration, 3),
                'min_duration_seconds': round(stats.min_duration, 3),
                'max_duration_seconds': round(stats.max_duration, 3),
                'percentile_95_seconds': round(stats.percentile_95, 3),
                'total_duration_seconds': round(stats.total_duration, 2)
            }
        else:
            # Return all operations
            return {
                op_name: self.get_operation_stats(op_name) 
                for op_name in self.operation_stats.keys()
            }
    
    def get_recent_metrics(self, hours: int = 1, operation: str = None) -> List[Dict[str, Any]]:
        """Get recent metrics within specified timeframe"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = []
        
        for metric in self.metrics:
            if metric.timestamp >= cutoff_time:
                if operation is None or metric.operation == operation:
                    recent_metrics.append({
                        'operation': metric.operation,
                        'duration': metric.duration,
                        'timestamp': metric.timestamp.isoformat(),
                        'success': metric.success,
                        'metadata': metric.metadata
                    })
        
        return recent_metrics
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health assessment"""
        
        if not self.operation_stats:
            return {
                'health_status': 'UNKNOWN',
                'message': 'No performance data available'
            }
        
        # Analyze overall health
        critical_issues = len([a for a in self.alerts if a.get('severity') == 'CRITICAL'])
        warning_issues = len([a for a in self.alerts if a.get('severity') == 'WARNING'])
        
        # Calculate overall metrics
        total_operations = sum(stats.total_calls for stats in self.operation_stats.values())
        total_failures = sum(stats.failed_calls for stats in self.operation_stats.values())
        overall_success_rate = 1 - (total_failures / total_operations) if total_operations > 0 else 1
        
        avg_response_times = [
            stats.avg_duration for stats in self.operation_stats.values() 
            if stats.total_calls >= 5
        ]
        overall_avg_response = statistics.mean(avg_response_times) if avg_response_times else 0
        
        # Determine health status
        if critical_issues > 0 or overall_success_rate < 0.9:
            health_status = 'CRITICAL'
        elif warning_issues > 0 or overall_success_rate < 0.95:
            health_status = 'WARNING'
        elif overall_avg_response > 3.0:
            health_status = 'DEGRADED'
        else:
            health_status = 'HEALTHY'
        
        return {
            'health_status': health_status,
            'overall_success_rate_percent': round(overall_success_rate * 100, 2),
            'overall_avg_response_time_seconds': round(overall_avg_response, 3),
            'total_operations': total_operations,
            'critical_alerts': critical_issues,
            'warning_alerts': warning_issues,
            'monitored_operations_count': len(self.operation_stats),
            'data_collection_period_hours': 24,  # Based on metric retention
            'last_updated': datetime.now().isoformat()
        }
    
    def get_alerts(self, severity: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        
        filtered_alerts = self.alerts
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a.get('severity') == severity.upper()]
        
        # Sort by timestamp descending and limit
        sorted_alerts = sorted(
            filtered_alerts, 
            key=lambda x: x.get('timestamp', datetime.min), 
            reverse=True
        )
        
        return sorted_alerts[:limit]
    
    def clear_alerts(self) -> int:
        """Clear all alerts"""
        count = len(self.alerts)
        self.alerts.clear()
        logger.info(f"Cleared {count} alerts")
        return count

class PerformanceDecorator:
    """
    Decorator for automatic performance monitoring
    """
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str = None):
        self.monitor = monitor
        self.operation_name = operation_name
    
    def __call__(self, func):
        async def async_wrapper(*args, **kwargs):
            operation = self.operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            success = True
            metadata = {}
            
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Extract metadata from result if available
                if hasattr(result, 'confidence'):
                    metadata['confidence'] = result.confidence
                if hasattr(result, 'engine'):
                    metadata['engine'] = result.engine
                
                return result
                
            except Exception as e:
                success = False
                metadata['error'] = str(e)
                raise
            
            finally:
                duration = time.time() - start_time
                self.monitor.record_metric(operation, duration, success, metadata)
        
        def sync_wrapper(*args, **kwargs):
            operation = self.operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            success = True
            metadata = {}
            
            try:
                result = func(*args, **kwargs)
                
                # Extract metadata from result if available
                if hasattr(result, 'confidence'):
                    metadata['confidence'] = result.confidence
                if hasattr(result, 'engine'):
                    metadata['engine'] = result.engine
                
                return result
                
            except Exception as e:
                success = False
                metadata['error'] = str(e)
                raise
            
            finally:
                duration = time.time() - start_time
                self.monitor.record_metric(operation, duration, success, metadata)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Convenience decorator
def monitor_performance(operation_name: str = None):
    """Decorator for monitoring function performance"""
    return PerformanceDecorator(performance_monitor, operation_name)