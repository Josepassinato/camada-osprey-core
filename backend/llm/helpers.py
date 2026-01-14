"""
LLM Helper Functions

Utilities for provider routing, fallback chains, caching, and metrics collection.
"""

import hashlib
import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

try:
    from backend.config.llm_config import (
        LLMProvider,
        get_model_config,
        get_provider_virtual_key,
        llm_settings,
    )
except ImportError:
    from config.llm_config import (
        LLMProvider,
        get_model_config,
        get_provider_virtual_key,
        llm_settings,
    )

logger = logging.getLogger(__name__)


class ProviderRouter:
    """
    Provider routing logic for LLM requests
    
    Handles intelligent routing of requests to appropriate providers
    based on model availability, cost, and performance.
    """
    
    def __init__(self):
        self.provider_health: Dict[str, bool] = defaultdict(lambda: True)
        self.provider_latency: Dict[str, List[float]] = defaultdict(list)
    
    def get_provider_for_model(self, model: str) -> Tuple[LLMProvider, Optional[str]]:
        """
        Get provider and virtual key for a model
        
        Args:
            model: Model name
            
        Returns:
            Tuple of (provider, virtual_key)
        """
        try:
            config = get_model_config(model)
            provider = config.provider
            virtual_key = get_provider_virtual_key(provider)
            
            if not virtual_key:
                logger.warning(
                    f"No virtual key configured for provider {provider}. "
                    f"Set PORTKEY_VIRTUAL_KEY_{provider.upper()} environment variable."
                )
            
            return provider, virtual_key
            
        except ValueError as e:
            logger.error(f"Model configuration not found: {e}")
            # Default to OpenAI
            return LLMProvider.OPENAI, get_provider_virtual_key(LLMProvider.OPENAI)
    
    def record_provider_health(self, provider: str, is_healthy: bool) -> None:
        """Record provider health status"""
        self.provider_health[provider] = is_healthy
        if not is_healthy:
            logger.warning(f"Provider {provider} marked as unhealthy")
    
    def record_provider_latency(self, provider: str, latency_ms: float) -> None:
        """Record provider latency"""
        self.provider_latency[provider].append(latency_ms)
        # Keep only last 100 measurements
        if len(self.provider_latency[provider]) > 100:
            self.provider_latency[provider] = self.provider_latency[provider][-100:]
    
    def get_average_latency(self, provider: str) -> float:
        """Get average latency for provider"""
        latencies = self.provider_latency.get(provider, [])
        if not latencies:
            return 0.0
        return sum(latencies) / len(latencies)
    
    def is_provider_healthy(self, provider: str) -> bool:
        """Check if provider is healthy"""
        return self.provider_health.get(provider, True)


class FallbackChain:
    """
    Fallback model chain management
    
    Handles automatic fallback to alternative models when primary model fails.
    """
    
    def __init__(self):
        self.fallback_attempts: Dict[str, int] = defaultdict(int)
    
    def get_fallback_chain(self, model: str) -> List[str]:
        """
        Get fallback chain for a model
        
        Args:
            model: Primary model name
            
        Returns:
            List of fallback model names in order of preference
        """
        try:
            config = get_model_config(model)
            return config.fallback_models
        except ValueError:
            logger.warning(f"No fallback chain configured for model {model}")
            return []
    
    def get_next_fallback(self, model: str, failed_models: List[str]) -> Optional[str]:
        """
        Get next fallback model
        
        Args:
            model: Primary model name
            failed_models: List of models that have already failed
            
        Returns:
            Next fallback model name, or None if no fallbacks available
        """
        chain = self.get_fallback_chain(model)
        
        for fallback in chain:
            if fallback not in failed_models:
                self.fallback_attempts[model] += 1
                logger.info(
                    f"Falling back from {model} to {fallback} "
                    f"(attempt {self.fallback_attempts[model]})"
                )
                return fallback
        
        logger.error(f"No more fallbacks available for model {model}")
        return None
    
    def reset_attempts(self, model: str) -> None:
        """Reset fallback attempt counter"""
        self.fallback_attempts[model] = 0
    
    def get_fallback_stats(self) -> Dict[str, int]:
        """Get fallback statistics"""
        return dict(self.fallback_attempts)


class CacheManager:
    """
    LLM response caching
    
    Provides semantic caching for LLM responses to reduce costs and latency.
    """
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def _generate_cache_key(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> str:
        """Generate cache key from request parameters"""
        # Create deterministic string representation
        cache_data = {
            "model": model,
            "messages": messages,
            "temperature": round(temperature, 2),
            "max_tokens": max_tokens
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()
    
    def get(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> Optional[Any]:
        """
        Get cached response
        
        Returns:
            Cached response if found and not expired, None otherwise
        """
        if not llm_settings.enable_caching:
            return None
        
        key = self._generate_cache_key(model, messages, temperature, max_tokens)
        
        if key in self.cache:
            response, timestamp = self.cache[key]
            
            # Check if expired
            if datetime.now() - timestamp < timedelta(seconds=self.ttl_seconds):
                self.hits += 1
                logger.debug(f"Cache hit for key {key[:8]}...")
                return response
            else:
                # Remove expired entry
                del self.cache[key]
                logger.debug(f"Cache expired for key {key[:8]}...")
        
        self.misses += 1
        return None
    
    def set(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        response: Any
    ) -> None:
        """Cache response"""
        if not llm_settings.enable_caching:
            return
        
        key = self._generate_cache_key(model, messages, temperature, max_tokens)
        self.cache[key] = (response, datetime.now())
        logger.debug(f"Cached response for key {key[:8]}...")
    
    def clear(self) -> None:
        """Clear all cached responses"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "cache_size": len(self.cache)
        }


class MetricsCollector:
    """
    LLM metrics collection
    
    Collects and aggregates metrics for monitoring and cost tracking.
    """
    
    def __init__(self):
        self.request_count: Dict[str, int] = defaultdict(int)
        self.token_usage: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"input": 0, "output": 0, "total": 0}
        )
        self.costs: Dict[str, float] = defaultdict(float)
        self.latencies: Dict[str, List[float]] = defaultdict(list)
        self.errors: Dict[str, int] = defaultdict(int)
        self.start_time = datetime.now()
    
    def record_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        success: bool = True
    ) -> None:
        """
        Record LLM request metrics
        
        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            latency_ms: Request latency in milliseconds
            success: Whether request succeeded
        """
        self.request_count[model] += 1
        
        if success:
            # Update token usage
            self.token_usage[model]["input"] += input_tokens
            self.token_usage[model]["output"] += output_tokens
            self.token_usage[model]["total"] += input_tokens + output_tokens
            
            # Calculate cost
            try:
                config = get_model_config(model)
                input_cost = (input_tokens / 1000) * config.cost_per_1k_input_tokens
                output_cost = (output_tokens / 1000) * config.cost_per_1k_output_tokens
                self.costs[model] += input_cost + output_cost
            except ValueError:
                logger.warning(f"Could not calculate cost for model {model}")
            
            # Record latency
            self.latencies[model].append(latency_ms)
            if len(self.latencies[model]) > 1000:
                self.latencies[model] = self.latencies[model][-1000:]
        else:
            self.errors[model] += 1
    
    def get_total_cost(self) -> float:
        """Get total cost across all models"""
        return sum(self.costs.values())
    
    def get_total_tokens(self) -> int:
        """Get total tokens across all models"""
        return sum(usage["total"] for usage in self.token_usage.values())
    
    def get_average_latency(self, model: Optional[str] = None) -> float:
        """Get average latency for model or all models"""
        if model:
            latencies = self.latencies.get(model, [])
        else:
            latencies = [lat for lats in self.latencies.values() for lat in lats]
        
        if not latencies:
            return 0.0
        return sum(latencies) / len(latencies)
    
    def get_error_rate(self, model: Optional[str] = None) -> float:
        """Get error rate as percentage"""
        if model:
            total = self.request_count.get(model, 0)
            errors = self.errors.get(model, 0)
        else:
            total = sum(self.request_count.values())
            errors = sum(self.errors.values())
        
        if total == 0:
            return 0.0
        return (errors / total) * 100
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "uptime_seconds": uptime,
            "total_requests": sum(self.request_count.values()),
            "total_tokens": self.get_total_tokens(),
            "total_cost_usd": round(self.get_total_cost(), 4),
            "average_latency_ms": round(self.get_average_latency(), 2),
            "error_rate_percent": round(self.get_error_rate(), 2),
            "by_model": {
                model: {
                    "requests": self.request_count[model],
                    "tokens": self.token_usage[model],
                    "cost_usd": round(self.costs[model], 4),
                    "avg_latency_ms": round(self.get_average_latency(model), 2),
                    "errors": self.errors[model],
                    "error_rate_percent": round(self.get_error_rate(model), 2)
                }
                for model in self.request_count.keys()
            }
        }
    
    def reset(self) -> None:
        """Reset all metrics"""
        self.request_count.clear()
        self.token_usage.clear()
        self.costs.clear()
        self.latencies.clear()
        self.errors.clear()
        self.start_time = datetime.now()
        logger.info("Metrics reset")


# Global instances
provider_router = ProviderRouter()
fallback_chain = FallbackChain()
cache_manager = CacheManager(ttl_seconds=llm_settings.portkey_config.cache_ttl)
metrics_collector = MetricsCollector()


def get_provider_router() -> ProviderRouter:
    """Get global provider router instance"""
    return provider_router


def get_fallback_chain() -> FallbackChain:
    """Get global fallback chain instance"""
    return fallback_chain


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    return cache_manager


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    return metrics_collector
