"""
LLM Abstraction Layer

This package provides a unified interface for LLM operations with Portkey integration.
It abstracts provider-specific details and provides observability, cost tracking,
and multi-provider routing capabilities.

Key Components:
- portkey_client: Main LLM client with Portkey integration
- types: Data models for LLM requests/responses
- exceptions: LLM-specific exception classes
- helpers: Provider routing, fallback chains, caching, and metrics
"""

from .exceptions import (
    LLMCircuitBreakerError,
    LLMContentFilterError,
    LLMCostLimitError,
    LLMException,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMValidationError,
    PromptNotFoundError,
)
from .helpers import (
    CacheManager,
    FallbackChain,
    MetricsCollector,
    ProviderRouter,
    get_cache_manager,
    get_fallback_chain,
    get_metrics_collector,
    get_provider_router,
)
from .types import (
    ChatMessage,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    MessageRole,
    ModelConfig,
    PromptMetadata,
)

__all__ = [
    # Types
    "MessageRole",
    "ChatMessage",
    "LLMRequest",
    "LLMResponse",
    "PromptMetadata",
    "LLMProvider",
    "ModelConfig",
    # Exceptions
    "LLMException",
    "LLMProviderError",
    "LLMRateLimitError",
    "LLMCostLimitError",
    "LLMTimeoutError",
    "PromptNotFoundError",
    "LLMValidationError",
    "LLMCircuitBreakerError",
    "LLMContentFilterError",
    # Helpers
    "ProviderRouter",
    "FallbackChain",
    "CacheManager",
    "MetricsCollector",
    "get_provider_router",
    "get_fallback_chain",
    "get_cache_manager",
    "get_metrics_collector",
]
