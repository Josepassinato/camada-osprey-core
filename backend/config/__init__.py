"""
Configuration Management Package

This package handles all configuration settings for the Osprey backend,
including environment variables, LLM provider settings, and application-wide
configuration management using Pydantic BaseSettings.

Modules:
    - settings.py: Core application settings and environment configuration
    - llm_config.py: LLM provider configuration, routing, and cost management
    - validation.py: Configuration validation utilities
"""

from .settings import Settings, settings
from .llm_config import (
    LLMSettings,
    LLMProvider,
    ModelConfig,
    PortkeyConfig,
    RateLimitConfig,
    CostBudgetConfig,
    llm_settings,
    get_model_config,
    get_provider_virtual_key,
    DEFAULT_MODELS,
)
from .validation import (
    validate_configuration,
    validate_or_exit,
    print_configuration_summary,
)

__all__ = [
    # Main settings
    "Settings",
    "settings",
    # LLM settings
    "LLMSettings",
    "llm_settings",
    # LLM types
    "LLMProvider",
    "ModelConfig",
    "PortkeyConfig",
    "RateLimitConfig",
    "CostBudgetConfig",
    # LLM utilities
    "get_model_config",
    "get_provider_virtual_key",
    "DEFAULT_MODELS",
    # Validation utilities
    "validate_configuration",
    "validate_or_exit",
    "print_configuration_summary",
]
