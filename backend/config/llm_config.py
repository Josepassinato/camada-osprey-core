"""
LLM configuration and provider management.

This module provides configuration for LLM providers, models, routing,
fallbacks, and cost management through Portkey.ai integration.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure-openai"


class ModelConfig(BaseModel):
    """Configuration for a specific LLM model."""

    name: str = Field(..., description="Model identifier (e.g., 'gpt-4o', 'claude-3-opus')")
    provider: LLMProvider = Field(..., description="Provider for this model")
    max_tokens: int = Field(default=4096, ge=1, description="Maximum tokens for model output")
    context_window: int = Field(default=128000, ge=1, description="Maximum context window size")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Default temperature for generation"
    )
    fallback_models: List[str] = Field(
        default_factory=list, description="List of fallback model names if this model fails"
    )
    cost_per_1k_input_tokens: float = Field(
        default=0.0, ge=0.0, description="Cost per 1000 input tokens in USD"
    )
    cost_per_1k_output_tokens: float = Field(
        default=0.0, ge=0.0, description="Cost per 1000 output tokens in USD"
    )
    supports_streaming: bool = Field(
        default=True, description="Whether model supports streaming responses"
    )
    supports_function_calling: bool = Field(
        default=True, description="Whether model supports function/tool calling"
    )
    supports_vision: bool = Field(default=False, description="Whether model supports image inputs")


class PortkeyConfig(BaseModel):
    """Portkey-specific configuration."""

    retry_count: int = Field(
        default=3, ge=0, le=10, description="Number of retries for failed requests"
    )
    retry_delay: float = Field(
        default=1.0, ge=0.0, description="Initial delay between retries in seconds"
    )
    timeout: int = Field(default=60, ge=1, description="Request timeout in seconds")
    enable_caching: bool = Field(default=True, description="Enable Portkey semantic caching")
    cache_ttl: int = Field(default=3600, ge=0, description="Cache TTL in seconds (0 = no expiry)")
    enable_fallbacks: bool = Field(
        default=True, description="Enable automatic fallback to alternative models"
    )
    enable_load_balancing: bool = Field(
        default=False, description="Enable load balancing across providers"
    )
    trace_requests: bool = Field(
        default=True, description="Enable request tracing in Portkey dashboard"
    )


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""

    requests_per_minute: int = Field(default=60, ge=1, description="Maximum requests per minute")
    tokens_per_minute: int = Field(default=90000, ge=1, description="Maximum tokens per minute")
    requests_per_day: int = Field(default=10000, ge=1, description="Maximum requests per day")


class CostBudgetConfig(BaseModel):
    """Cost budget configuration."""

    daily_budget_usd: float = Field(default=100.0, ge=0.0, description="Maximum daily spend in USD")
    monthly_budget_usd: float = Field(
        default=3000.0, ge=0.0, description="Maximum monthly spend in USD"
    )
    alert_threshold_percent: float = Field(
        default=80.0, ge=0.0, le=100.0, description="Alert when budget reaches this percentage"
    )
    hard_limit: bool = Field(
        default=False, description="Hard stop when budget exceeded (vs. alert only)"
    )


class LLMSettings(BaseSettings):
    """LLM configuration settings loaded from environment variables."""

    # Portkey Configuration
    portkey_api_key: Optional[str] = Field(
        default=None, description="Portkey API key for LLM gateway", alias="PORTKEY_API_KEY"
    )
    portkey_base_url: str = Field(
        default="https://api.portkey.ai/v1", description="Portkey API base URL"
    )

    # Virtual Keys (per provider)
    portkey_virtual_key_openai: Optional[str] = Field(
        default=None, description="Portkey virtual key for OpenAI"
    )
    portkey_virtual_key_anthropic: Optional[str] = Field(
        default=None, description="Portkey virtual key for Anthropic"
    )
    portkey_virtual_key_google: Optional[str] = Field(
        default=None, description="Portkey virtual key for Google"
    )

    # Default Model Configuration
    default_model: str = Field(default="gpt-4o", description="Default model to use for LLM calls")
    default_temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Default temperature for generation"
    )
    default_max_tokens: int = Field(
        default=4096, ge=1, description="Default max tokens for generation"
    )

    # Feature Flags
    enable_portkey: bool = Field(
        default=True, description="Enable Portkey integration (disable for local dev)", alias="ENABLE_PORTKEY"
    )
    enable_caching: bool = Field(default=True, description="Enable LLM response caching")
    enable_fallbacks: bool = Field(default=True, description="Enable automatic model fallbacks")
    enable_cost_tracking: bool = Field(default=True, description="Enable cost tracking and budgets")

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(
        default=60, ge=1, description="Maximum LLM requests per minute"
    )
    rate_limit_tokens_per_minute: int = Field(
        default=90000, ge=1, description="Maximum tokens per minute"
    )

    # Cost Budgets
    cost_budget_daily_usd: float = Field(
        default=100.0, ge=0.0, description="Daily cost budget in USD"
    )
    cost_budget_monthly_usd: float = Field(
        default=3000.0, ge=0.0, description="Monthly cost budget in USD"
    )
    cost_alert_threshold: float = Field(
        default=80.0, ge=0.0, le=100.0, description="Alert threshold as percentage of budget"
    )

    @validator("portkey_api_key")
    def validate_portkey_key(cls, v, values):
        """Validate Portkey API key is set when Portkey is enabled."""
        if values.get("enable_portkey", True) and not v:
            # Log warning but don't fail - allow fallback to direct OpenAI
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                "⚠️  PORTKEY_API_KEY not set. Portkey features disabled. "
                "LLM client will fall back to direct OpenAI. "
                "Set PORTKEY_API_KEY for observability and cost tracking."
            )
        return v

    @property
    def portkey_config(self) -> PortkeyConfig:
        """Get Portkey configuration."""
        return PortkeyConfig(
            enable_caching=self.enable_caching,
            enable_fallbacks=self.enable_fallbacks,
            trace_requests=True,
        )

    @property
    def rate_limit_config(self) -> RateLimitConfig:
        """Get rate limit configuration."""
        return RateLimitConfig(
            requests_per_minute=self.rate_limit_requests_per_minute,
            tokens_per_minute=self.rate_limit_tokens_per_minute,
        )

    @property
    def cost_budget_config(self) -> CostBudgetConfig:
        """Get cost budget configuration."""
        return CostBudgetConfig(
            daily_budget_usd=self.cost_budget_daily_usd,
            monthly_budget_usd=self.cost_budget_monthly_usd,
            alert_threshold_percent=self.cost_alert_threshold,
        )

    @property
    def virtual_keys(self) -> Dict[str, Optional[str]]:
        """Get all virtual keys by provider."""
        return {
            LLMProvider.OPENAI: self.portkey_virtual_key_openai,
            LLMProvider.ANTHROPIC: self.portkey_virtual_key_anthropic,
            LLMProvider.GOOGLE: self.portkey_virtual_key_google,
        }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Removed env_prefix to allow direct variable names (PORTKEY_API_KEY, ENABLE_PORTKEY)
        # Individual fields use aliases where needed
        extra = "ignore"  # Ignore extra fields from .env that don't belong to LLMSettings


# Predefined model configurations
DEFAULT_MODELS: Dict[str, ModelConfig] = {
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        provider=LLMProvider.OPENAI,
        max_tokens=4096,
        context_window=128000,
        temperature=0.7,
        fallback_models=["gpt-4-turbo", "gpt-3.5-turbo"],
        cost_per_1k_input_tokens=0.005,
        cost_per_1k_output_tokens=0.015,
        supports_streaming=True,
        supports_function_calling=True,
        supports_vision=True,
    ),
    "gpt-4-turbo": ModelConfig(
        name="gpt-4-turbo",
        provider=LLMProvider.OPENAI,
        max_tokens=4096,
        context_window=128000,
        temperature=0.7,
        fallback_models=["gpt-3.5-turbo"],
        cost_per_1k_input_tokens=0.01,
        cost_per_1k_output_tokens=0.03,
        supports_streaming=True,
        supports_function_calling=True,
        supports_vision=True,
    ),
    "gpt-3.5-turbo": ModelConfig(
        name="gpt-3.5-turbo",
        provider=LLMProvider.OPENAI,
        max_tokens=4096,
        context_window=16385,
        temperature=0.7,
        fallback_models=[],
        cost_per_1k_input_tokens=0.0005,
        cost_per_1k_output_tokens=0.0015,
        supports_streaming=True,
        supports_function_calling=True,
        supports_vision=False,
    ),
    "gemini-1.5-pro": ModelConfig(
        name="gemini-1.5-pro",
        provider=LLMProvider.GOOGLE,
        max_tokens=8192,
        context_window=1000000,
        temperature=0.7,
        fallback_models=["gemini-1.5-flash"],
        cost_per_1k_input_tokens=0.00125,
        cost_per_1k_output_tokens=0.005,
        supports_streaming=True,
        supports_function_calling=True,
        supports_vision=True,
    ),
    "gemini-1.5-flash": ModelConfig(
        name="gemini-1.5-flash",
        provider=LLMProvider.GOOGLE,
        max_tokens=8192,
        context_window=1000000,
        temperature=0.7,
        fallback_models=[],
        cost_per_1k_input_tokens=0.000075,
        cost_per_1k_output_tokens=0.0003,
        supports_streaming=True,
        supports_function_calling=True,
        supports_vision=True,
    ),
    "claude-3-opus": ModelConfig(
        name="claude-3-opus-20240229",
        provider=LLMProvider.ANTHROPIC,
        max_tokens=4096,
        context_window=200000,
        temperature=0.7,
        fallback_models=["claude-3-sonnet"],
        cost_per_1k_input_tokens=0.015,
        cost_per_1k_output_tokens=0.075,
        supports_streaming=True,
        supports_function_calling=True,
        supports_vision=True,
    ),
    "claude-3-sonnet": ModelConfig(
        name="claude-3-sonnet-20240229",
        provider=LLMProvider.ANTHROPIC,
        max_tokens=4096,
        context_window=200000,
        temperature=0.7,
        fallback_models=["claude-3-haiku"],
        cost_per_1k_input_tokens=0.003,
        cost_per_1k_output_tokens=0.015,
        supports_streaming=True,
        supports_function_calling=True,
        supports_vision=True,
    ),
    "claude-3-haiku": ModelConfig(
        name="claude-3-haiku-20240307",
        provider=LLMProvider.ANTHROPIC,
        max_tokens=4096,
        context_window=200000,
        temperature=0.7,
        fallback_models=[],
        cost_per_1k_input_tokens=0.00025,
        cost_per_1k_output_tokens=0.00125,
        supports_streaming=True,
        supports_function_calling=True,
        supports_vision=True,
    ),
}


# Global LLM settings instance
llm_settings = LLMSettings()


def get_model_config(model_name: str) -> ModelConfig:
    """
    Get configuration for a specific model.

    Args:
        model_name: Name of the model

    Returns:
        ModelConfig for the specified model

    Raises:
        ValueError: If model is not configured
    """
    if model_name not in DEFAULT_MODELS:
        raise ValueError(
            f"Model '{model_name}' not configured. "
            f"Available models: {list(DEFAULT_MODELS.keys())}"
        )
    return DEFAULT_MODELS[model_name]


def get_provider_virtual_key(provider: LLMProvider) -> Optional[str]:
    """
    Get Portkey virtual key for a specific provider.

    Args:
        provider: LLM provider

    Returns:
        Virtual key for the provider, or None if not configured
    """
    return llm_settings.virtual_keys.get(provider)
