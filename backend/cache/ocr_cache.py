"""
OCR Cache System - Performance Optimization
Sistema de cache inteligente para resultados OCR
"""

import hashlib
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import asyncio
import os

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry for OCR results"""
    key: str
    data: Dict[str, Any]
    timestamp: datetime
    hit_count: int = 0
    processing_time: float = 0.0
    confidence_score: float = 0.0
    document_type: str = ""
    
    def is_expired(self, ttl_hours: int = 24) -> bool:
        """Check if cache entry is expired"""
        return (datetime.now() - self.timestamp) > timedelta(hours=ttl_hours)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'key': self.key,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'hit_count': self.hit_count,
            'processing_time': self.processing_time,
            'confidence_score': self.confidence_score,
            'document_type': self.document_type
        }

class OCRCache:
    """
    Intelligent cache system for OCR results
    Improves performance by caching expensive OCR operations
    """
    
    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_time_saved': 0.0
        }
        
        # Load cache from file if exists
        self._load_cache()
    
    def _generate_cache_key(self, image_data: str, mode: str = "auto", language: str = "eng") -> str:
        """Generate unique cache key for image + parameters"""
        # FIXED: Use full content hash to prevent cache collisions between different documents
        # Previous bug: Used only first 100 bytes + length, causing different documents to share cache keys
        full_content_hash = hashlib.sha256(image_data.encode() if isinstance(image_data, str) else image_data).hexdigest()
        content = f"{full_content_hash}{mode}{language}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def get_or_compute(self, 
                           image_data: str, 
                           ocr_function,
                           mode: str = "auto",
                           language: str = "eng",
                           document_type: str = "") -> Tuple[Dict[str, Any], bool]:
        """
        Get cached result or compute new one
        
        Returns:
            Tuple of (result, was_cached)
        """
        try:
            cache_key = self._generate_cache_key(image_data, mode, language)
            
            # Check cache first
            cached_result = self._get_cached(cache_key)
            if cached_result:
                self.stats['hits'] += 1
                self.stats['total_time_saved'] += cached_result.processing_time
                logger.info(f"Cache HIT for key {cache_key} (saved {cached_result.processing_time:.2f}s)")
                return cached_result.data, True
            
            # Cache miss - compute result
            self.stats['misses'] += 1
            logger.info(f"Cache MISS for key {cache_key} - computing OCR result")
            
            start_time = time.time()
            
            # Execute OCR function
            if asyncio.iscoroutinefunction(ocr_function):
                result = await ocr_function(image_data, mode=mode, language=language)
            else:
                result = ocr_function(image_data, mode=mode, language=language)
            
            processing_time = time.time() - start_time
            
            # Convert result to dictionary format
            if hasattr(result, '__dict__'):
                result_dict = asdict(result) if hasattr(result, '__dataclass_fields__') else vars(result)
            else:
                result_dict = result
            
            # Cache the result
            self._store_cached(
                cache_key, 
                result_dict, 
                processing_time,
                getattr(result, 'confidence', 0.8),
                document_type
            )
            
            logger.info(f"OCR result cached with key {cache_key} (processing time: {processing_time:.2f}s)")
            
            return result_dict, False
            
        except Exception as e:
            logger.error(f"Cache system error: {e}")
            # Fallback to direct computation
            if asyncio.iscoroutinefunction(ocr_function):
                result = await ocr_function(image_data, mode=mode, language=language)
            else:
                result = ocr_function(image_data, mode=mode, language=language)
            
            if hasattr(result, '__dict__'):
                result_dict = asdict(result) if hasattr(result, '__dataclass_fields__') else vars(result)
            else:
                result_dict = result
                
            return result_dict, False
    
    def _get_cached(self, key: str) -> Optional[CacheEntry]:
        """Get cached entry if valid"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if entry.is_expired(self.ttl_hours):
            del self.cache[key]
            return None
        
        # Update hit count
        entry.hit_count += 1
        return entry
    
    def _store_cached(self, 
                     key: str, 
                     data: Dict[str, Any], 
                     processing_time: float,
                     confidence_score: float = 0.8,
                     document_type: str = ""):
        """Store result in cache"""
        
        # Check cache size and evict if necessary
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Store new entry
        entry = CacheEntry(
            key=key,
            data=data,
            timestamp=datetime.now(),
            processing_time=processing_time,
            confidence_score=confidence_score,
            document_type=document_type
        )
        
        self.cache[key] = entry
    
    def _evict_lru(self):
        """Evict least recently used entries"""
        if not self.cache:
            return
        
        # Sort by timestamp (oldest first) and remove 10% of cache
        entries_to_remove = sorted(
            self.cache.items(), 
            key=lambda x: x[1].timestamp
        )[:max(1, len(self.cache) // 10)]
        
        for key, _ in entries_to_remove:
            del self.cache[key]
            self.stats['evictions'] += 1
        
        logger.info(f"Evicted {len(entries_to_remove)} cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate_percentage': round(hit_rate, 2),
            'total_hits': self.stats['hits'],
            'total_misses': self.stats['misses'],
            'total_evictions': self.stats['evictions'],
            'total_time_saved_seconds': round(self.stats['total_time_saved'], 2),
            'average_processing_time_saved': round(
                self.stats['total_time_saved'] / max(1, self.stats['hits']), 2
            )
        }
    
    def clear_cache(self):
        """Clear all cache entries"""
        cleared_count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cleared {cleared_count} cache entries")
        return cleared_count
    
    def _load_cache(self):
        """Load cache from persistent storage (simplified)"""
        try:
            # In a production system, this would load from Redis or database
            # For now, we'll keep it in memory only
            logger.info("OCR Cache initialized (in-memory)")
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
    
    def _save_cache(self):
        """Save cache to persistent storage"""
        try:
            # In production, save to Redis or database
            logger.info("Cache state would be persisted here")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

class BatchOCRProcessor:
    """
    Batch processor for multiple documents with intelligent caching
    """
    
    def __init__(self, cache: OCRCache):
        self.cache = cache
        self.max_concurrent = 3  # Limit concurrent OCR operations
    
    async def process_batch(self, 
                          documents: List[Dict[str, Any]], 
                          ocr_function) -> List[Dict[str, Any]]:
        """
        Process multiple documents with caching and concurrency control
        
        Args:
            documents: List of documents with image_data, mode, language
            ocr_function: OCR function to use
        
        Returns:
            List of OCR results
        """
        try:
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def process_single(doc: Dict[str, Any]) -> Dict[str, Any]:
                async with semaphore:
                    result, was_cached = await self.cache.get_or_compute(
                        image_data=doc.get('image_data', ''),
                        ocr_function=ocr_function,
                        mode=doc.get('mode', 'auto'),
                        language=doc.get('language', 'eng'),
                        document_type=doc.get('document_type', '')
                    )
                    
                    return {
                        'document_id': doc.get('document_id', ''),
                        'result': result,
                        'was_cached': was_cached,
                        'document_type': doc.get('document_type', '')
                    }
            
            # Process all documents concurrently
            tasks = [process_single(doc) for doc in documents]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and return successful results
            successful_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error for document {i}: {result}")
                    successful_results.append({
                        'document_id': documents[i].get('document_id', ''),
                        'result': None,
                        'error': str(result),
                        'was_cached': False
                    })
                else:
                    successful_results.append(result)
            
            logger.info(f"Batch processing completed: {len(successful_results)} documents processed")
            
            return successful_results
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise

# Global cache instance
ocr_cache = OCRCache(max_size=1000, ttl_hours=24)
batch_processor = BatchOCRProcessor(ocr_cache)