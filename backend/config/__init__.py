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

from .llm_config import (
    DEFAULT_MODELS,
    CostBudgetConfig,
    LLMProvider,
    LLMSettings,
    ModelConfig,
    PortkeyConfig,
    RateLimitConfig,
    get_model_config,
    get_provider_virtual_key,
    llm_settings,
)
from .settings import Settings, settings
from .validation import (
    print_configuration_summary,
    validate_configuration,
    validate_or_exit,
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
