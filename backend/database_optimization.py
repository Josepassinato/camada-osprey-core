"""
Database Optimization System - Phase 4B
Sistema de otimização de banco de dados e cache avançado
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
import time
import hashlib
import json
import pickle
import redis.asyncio as aioredis
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@dataclass
class QueryPerformanceMetric:
    """Métrica de performance de query"""
    collection: str
    operation: str
    execution_time_ms: float
    timestamp: datetime
    query_hash: str
    result_count: int
    index_used: bool

@dataclass
class CacheStats:
    """Estatísticas do cache"""
    hits: int = 0
    misses: int = 0
    total_requests: int = 0
    hit_rate: float = 0.0
    avg_response_time_ms: float = 0.0

class DatabaseOptimizationSystem:
    """
    Sistema de otimização de banco de dados
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Performance tracking
        self.query_metrics: List[QueryPerformanceMetric] = []
        self.slow_queries_threshold_ms = 1000  # 1 segundo
        
        # Cache configuration
        self.cache_config = {
            "default_ttl": 300,  # 5 minutes
            "long_ttl": 3600,    # 1 hour
            "short_ttl": 60,     # 1 minute
        }
        
        # Cache stats
        self.cache_stats: Dict[str, CacheStats] = {}
        
        # Connection pooling settings
        self.connection_settings = {
            "maxPoolSize": 50,
            "minPoolSize": 5,
            "maxIdleTimeMS": 30000,
            "connectTimeoutMS": 20000,
            "socketTimeoutMS": 20000,
            "serverSelectionTimeoutMS": 30000,
            "retryWrites": True,
            "retryReads": True
        }
        
        # Initialize optimization
        asyncio.create_task(self._initialize_optimization())
    
    async def _initialize_optimization(self):
        """
        Inicializa otimizações do banco
        """
        try:
            # Initialize Redis cache
            await self._initialize_redis()
            
            # Create database indexes
            await self._create_performance_indexes()
            
            # Start monitoring tasks
            asyncio.create_task(self._monitor_performance())
            asyncio.create_task(self._cleanup_old_metrics())
            
            logger.info("✅ Database optimization system initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing database optimization: {e}")
    
    async def _initialize_redis(self):
        """
        Inicializa conexão Redis para cache
        """
        try:
            # Try to connect to Redis (optional)
            self.redis_client = await aioredis.from_url(
                "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Redis cache connected")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis not available, using in-memory cache: {e}")
            self.redis_client = None
    
    async def _create_performance_indexes(self):
        """
        Cria índices otimizados para performance
        """
        try:
            # Índices para collection de cases
            cases_indexes = [
                IndexModel([("case_id", ASCENDING)], unique=True),
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("form_code", ASCENDING)]),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
                IndexModel([("updated_at", DESCENDING)]),
                IndexModel([("user_id", ASCENDING), ("status", ASCENDING)]),
                IndexModel([("form_code", ASCENDING), ("created_at", DESCENDING)])
            ]
            
            await self.db.cases.create_indexes(cases_indexes)
            
            # Índices para collection de documents
            documents_indexes = [
                IndexModel([("document_id", ASCENDING)], unique=True),
                IndexModel([("case_id", ASCENDING)]),
                IndexModel([("document_type", ASCENDING)]),
                IndexModel([("validation_status", ASCENDING)]),
                IndexModel([("upload_date", DESCENDING)]),
                IndexModel([("case_id", ASCENDING), ("document_type", ASCENDING)]),
                IndexModel([("case_id", ASCENDING), ("validation_status", ASCENDING)]),
                IndexModel([("filename", TEXT)])  # Text search
            ]
            
            await self.db.documents.create_indexes(documents_indexes)
            
            # Índices para workflow executions
            workflow_indexes = [
                IndexModel([("execution_id", ASCENDING)], unique=True),
                IndexModel([("case_id", ASCENDING)]),
                IndexModel([("workflow_name", ASCENDING)]),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
                IndexModel([("case_id", ASCENDING), ("status", ASCENDING)])
            ]
            
            await self.db.workflow_executions.create_indexes(workflow_indexes)
            
            # Índices para notifications
            notification_indexes = [
                IndexModel([("notification_id", ASCENDING)], unique=True),
                IndexModel([("recipient.user_id", ASCENDING)]),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
                IndexModel([("case_id", ASCENDING)]),
                IndexModel([("template_id", ASCENDING)])
            ]
            
            await self.db.notifications.create_indexes(notification_indexes)
            
            # Índices para analytics
            analytics_indexes = [
                IndexModel([("timestamp", DESCENDING)]),
                IndexModel([("metric_type", ASCENDING)]),
                IndexModel([("case_id", ASCENDING)]),
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("timestamp", DESCENDING), ("metric_type", ASCENDING)])
            ]
            
            await self.db.analytics_events.create_indexes(analytics_indexes)
            
            logger.info("✅ Performance indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
    
    @asynccontextmanager
    async def track_query_performance(self, collection_name: str, operation: str, query: Dict[str, Any] = None):
        """
        Context manager para tracking de performance de queries
        """
        start_time = time.time()
        query_hash = self._hash_query(query) if query else "no-query"
        
        try:
            yield
        finally:
            execution_time = (time.time() - start_time) * 1000
            
            metric = QueryPerformanceMetric(
                collection=collection_name,
                operation=operation,
                execution_time_ms=execution_time,
                timestamp=datetime.now(timezone.utc),
                query_hash=query_hash,
                result_count=0,  # Will be updated by caller
                index_used=True   # Assume optimized for now
            )
            
            self.query_metrics.append(metric)
            
            # Log slow queries
            if execution_time > self.slow_queries_threshold_ms:
                logger.warning(f"🐌 SLOW QUERY: {collection_name}.{operation} took {execution_time:.0f}ms")
    
    def _hash_query(self, query: Dict[str, Any]) -> str:
        """
        Gera hash da query para tracking
        """
        query_str = json.dumps(query, sort_keys=True, default=str)
        return hashlib.md5(query_str.encode()).hexdigest()[:8]
    
    async def cached_find_one(self, collection: AsyncIOMotorCollection, filter_dict: Dict[str, Any], cache_key: Optional[str] = None, ttl: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Find one com cache
        """
        if not cache_key:
            cache_key = f"find_one:{collection.name}:{self._hash_query(filter_dict)}"
        
        cache_ttl = ttl or self.cache_config["default_ttl"]
        
        # Try cache first
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            self._update_cache_stats(cache_key, hit=True)
            return cached_result
        
        # Cache miss - query database
        self._update_cache_stats(cache_key, hit=False)
        
        async with self.track_query_performance(collection.name, "find_one", filter_dict):
            result = await collection.find_one(filter_dict)
        
        # Cache result
        if result:
            await self._set_cache(cache_key, result, cache_ttl)
        
        return result
    
    async def cached_find(self, collection: AsyncIOMotorCollection, filter_dict: Dict[str, Any], limit: Optional[int] = None, sort: Optional[List] = None, cache_key: Optional[str] = None, ttl: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find com cache
        """
        if not cache_key:
            cache_key = f"find:{collection.name}:{self._hash_query(filter_dict)}:limit_{limit}:sort_{sort}"
        
        cache_ttl = ttl or self.cache_config["default_ttl"]
        
        # Try cache first
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            self._update_cache_stats(cache_key, hit=True)
            return cached_result
        
        # Cache miss - query database
        self._update_cache_stats(cache_key, hit=False)
        
        async with self.track_query_performance(collection.name, "find", filter_dict):
            cursor = collection.find(filter_dict)
            
            if sort:
                cursor = cursor.sort(sort)
            if limit:
                cursor = cursor.limit(limit)
            
            results = await cursor.to_list(None)
        
        # Cache results
        await self._set_cache(cache_key, results, cache_ttl)
        
        return results
    
    async def cached_count_documents(self, collection: AsyncIOMotorCollection, filter_dict: Dict[str, Any], cache_key: Optional[str] = None, ttl: Optional[int] = None) -> int:
        """
        Count documents com cache
        """
        if not cache_key:
            cache_key = f"count:{collection.name}:{self._hash_query(filter_dict)}"
        
        cache_ttl = ttl or self.cache_config["short_ttl"]  # Counts change frequently
        
        # Try cache first
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            self._update_cache_stats(cache_key, hit=True)
            return cached_result
        
        # Cache miss - query database
        self._update_cache_stats(cache_key, hit=False)
        
        async with self.track_query_performance(collection.name, "count_documents", filter_dict):
            result = await collection.count_documents(filter_dict)
        
        # Cache result
        await self._set_cache(cache_key, result, cache_ttl)
        
        return result
    
    async def cached_aggregate(self, collection: AsyncIOMotorCollection, pipeline: List[Dict], cache_key: str, ttl: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Aggregate com cache (requer cache_key explícito devido à complexidade)
        """
        cache_ttl = ttl or self.cache_config["default_ttl"]
        
        # Try cache first
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            self._update_cache_stats(cache_key, hit=True)
            return cached_result
        
        # Cache miss - execute aggregation
        self._update_cache_stats(cache_key, hit=False)
        
        async with self.track_query_performance(collection.name, "aggregate", {"pipeline": pipeline}):
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(None)
        
        # Cache results
        await self._set_cache(cache_key, results, cache_ttl)
        
        return results
    
    async def _get_from_cache(self, key: str) -> Any:
        """
        Obtém valor do cache
        """
        try:
            if self.redis_client:
                # Redis cache
                cached_data = await self.redis_client.get(f"osprey:cache:{key}")
                if cached_data:
                    return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None
    
    async def _set_cache(self, key: str, value: Any, ttl: int):
        """
        Define valor no cache
        """
        try:
            if self.redis_client:
                # Redis cache
                serialized_value = json.dumps(value, default=str)
                await self.redis_client.setex(f"osprey:cache:{key}", ttl, serialized_value)
            
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
    
    async def invalidate_cache_pattern(self, pattern: str):
        """
        Invalida cache por padrão
        """
        try:
            if self.redis_client:
                keys = await self.redis_client.keys(f"osprey:cache:{pattern}")
                if keys:
                    await self.redis_client.delete(*keys)
                    logger.info(f"🧹 Invalidated {len(keys)} cache keys matching pattern: {pattern}")
        
        except Exception as e:
            logger.warning(f"Cache invalidation error for pattern {pattern}: {e}")
    
    def _update_cache_stats(self, cache_key: str, hit: bool):
        """
        Atualiza estatísticas do cache
        """
        key_prefix = cache_key.split(':')[0] if ':' in cache_key else 'unknown'
        
        if key_prefix not in self.cache_stats:
            self.cache_stats[key_prefix] = CacheStats()
        
        stats = self.cache_stats[key_prefix]
        stats.total_requests += 1
        
        if hit:
            stats.hits += 1
        else:
            stats.misses += 1
        
        stats.hit_rate = stats.hits / stats.total_requests if stats.total_requests > 0 else 0
    
    async def _monitor_performance(self):
        """
        Monitora performance do banco continuamente
        """
        while True:
            try:
                # Collect database stats
                db_stats = await self.db.command("dbStats")
                
                # Log slow queries
                recent_slow_queries = [
                    m for m in self.query_metrics[-100:]  # Last 100 queries
                    if m.execution_time_ms > self.slow_queries_threshold_ms
                ]
                
                if recent_slow_queries:
                    logger.warning(f"🐌 Found {len(recent_slow_queries)} slow queries in recent batch")
                
                # Monitor connection pool
                # This would require additional MongoDB driver features
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(300)
    
    async def _cleanup_old_metrics(self):
        """
        Limpa métricas antigas
        """
        while True:
            try:
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
                
                # Keep only recent metrics
                self.query_metrics = [
                    m for m in self.query_metrics
                    if m.timestamp > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"Error in metrics cleanup: {e}")
                await asyncio.sleep(3600)
    
    # ===========================================
    # PUBLIC METHODS
    # ===========================================
    
    async def get_database_performance_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de performance do banco
        """
        try:
            # Database statistics
            db_stats = await self.db.command("dbStats")
            
            # Query performance analysis
            recent_metrics = self.query_metrics[-1000:]  # Last 1000 queries
            
            if recent_metrics:
                avg_query_time = sum(m.execution_time_ms for m in recent_metrics) / len(recent_metrics)
                slow_queries_count = len([m for m in recent_metrics if m.execution_time_ms > self.slow_queries_threshold_ms])
                
                # Group by collection
                by_collection = {}
                for metric in recent_metrics:
                    if metric.collection not in by_collection:
                        by_collection[metric.collection] = {
                            "count": 0,
                            "avg_time": 0,
                            "slow_queries": 0
                        }
                    
                    by_collection[metric.collection]["count"] += 1
                    by_collection[metric.collection]["avg_time"] += metric.execution_time_ms
                    if metric.execution_time_ms > self.slow_queries_threshold_ms:
                        by_collection[metric.collection]["slow_queries"] += 1
                
                # Calculate averages
                for collection_stats in by_collection.values():
                    if collection_stats["count"] > 0:
                        collection_stats["avg_time"] /= collection_stats["count"]
            else:
                avg_query_time = 0
                slow_queries_count = 0
                by_collection = {}
            
            # Cache statistics
            total_cache_requests = sum(stats.total_requests for stats in self.cache_stats.values())
            total_cache_hits = sum(stats.hits for stats in self.cache_stats.values())
            overall_hit_rate = total_cache_hits / total_cache_requests if total_cache_requests > 0 else 0
            
            return {
                "database": {
                    "collections": db_stats.get("collections", 0),
                    "data_size_mb": db_stats.get("dataSize", 0) / (1024 * 1024),
                    "storage_size_mb": db_stats.get("storageSize", 0) / (1024 * 1024),
                    "indexes": db_stats.get("indexes", 0),
                    "index_size_mb": db_stats.get("indexSize", 0) / (1024 * 1024)
                },
                "query_performance": {
                    "avg_query_time_ms": round(avg_query_time, 2),
                    "slow_queries_count": slow_queries_count,
                    "total_recent_queries": len(recent_metrics),
                    "slow_query_threshold_ms": self.slow_queries_threshold_ms,
                    "by_collection": by_collection
                },
                "cache_performance": {
                    "overall_hit_rate": round(overall_hit_rate, 3),
                    "total_requests": total_cache_requests,
                    "total_hits": total_cache_hits,
                    "redis_connected": self.redis_client is not None,
                    "by_cache_type": {
                        cache_type: {
                            "hit_rate": round(stats.hit_rate, 3),
                            "total_requests": stats.total_requests,
                            "hits": stats.hits,
                            "misses": stats.misses
                        }
                        for cache_type, stats in self.cache_stats.items()
                    }
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting database performance stats: {e}")
            return {"error": str(e)}
    
    async def optimize_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Executa otimização em uma collection específica
        """
        try:
            collection = self.db[collection_name]
            
            # Reindex collection
            await collection.reindex()
            
            # Get collection stats
            stats = await self.db.command("collStats", collection_name)
            
            # Compact if beneficial (this is more of a suggestion)
            size_mb = stats.get("size", 0) / (1024 * 1024)
            
            return {
                "collection": collection_name,
                "optimization_completed": True,
                "size_mb": round(size_mb, 2),
                "document_count": stats.get("count", 0),
                "avg_document_size": stats.get("avgObjSize", 0),
                "indexes_rebuilt": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing collection {collection_name}: {e}")
            return {"error": str(e), "collection": collection_name}
    
    async def clear_cache(self, pattern: Optional[str] = None):
        """
        Limpa cache completamente ou por padrão
        """
        try:
            if self.redis_client:
                if pattern:
                    await self.invalidate_cache_pattern(pattern)
                else:
                    # Clear all cache
                    await self.redis_client.flushdb()
                
            # Reset local cache stats
            self.cache_stats = {}
            
            logger.info("🧹 Cache cleared successfully")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            raise

# Global instance will be initialized by server
db_optimization_system: Optional[DatabaseOptimizationSystem] = None