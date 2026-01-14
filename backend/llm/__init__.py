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

from .types import (
    MessageRole,
    ChatMessage,
    LLMRequest,
    LLMResponse,
    PromptMetadata,
    LLMProvider,
    ModelConfig,
)
from .exceptions import (
    LLMException,
    LLMProviderError,
    LLMRateLimitError,
    LLMCostLimitError,
    LLMTimeoutError,
    PromptNotFoundError,
    LLMValidationError,
    LLMCircuitBreakerError,
    LLMContentFilterError,
)
from .helpers import (
    ProviderRouter,
    FallbackChain,
    CacheManager,
    MetricsCollector,
    get_provider_router,
    get_fallback_chain,
    get_cache_manager,
    get_metrics_collector,
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
