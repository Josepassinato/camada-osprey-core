"""
Configuration validation utilities.

This module provides utilities for validating configuration at startup
and providing helpful error messages when configuration is invalid.
"""

import sys
from typing import List, Tuple
from pydantic import ValidationError


def validate_configuration() -> Tuple[bool, List[str]]:
    """
    Validate all configuration settings.
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Validate main settings
    try:
        from .settings import settings
        # Access a required field to trigger validation
        _ = settings.jwt_secret
    except ValidationError as e:
        errors.append(f"Settings validation failed: {e}")
    except Exception as e:
        errors.append(f"Unexpected error loading settings: {e}")
    
    # Validate LLM settings
    try:
        from .llm_config import llm_settings
        # Access fields to trigger validation
        _ = llm_settings.default_model
        
        # Check Portkey configuration if enabled
        if llm_settings.enable_portkey:
            if not llm_settings.portkey_api_key:
                errors.append(
                    "Portkey is enabled but PORTKEY_API_KEY is not set. "
                    "Either set PORTKEY_API_KEY or set LLM_ENABLE_PORTKEY=false"
                )
    except ValidationError as e:
        errors.append(f"LLM settings validation failed: {e}")
    except Exception as e:
        errors.append(f"Unexpected error loading LLM settings: {e}")
    
    return len(errors) == 0, errors


def validate_or_exit():
    """
    Validate configuration and exit if invalid.
    
    This function should be called at application startup to ensure
    all required configuration is present and valid.
    """
    is_valid, errors = validate_configuration()
    
    if not is_valid:
        print("=" * 80)
        print("CONFIGURATION VALIDATION FAILED")
        print("=" * 80)
        print()
        print("The following configuration errors were found:")
        print()
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")
        print()
        print("Please check your .env file and ensure all required variables are set.")
        print("See backend/config/README.md for configuration documentation.")
        print("=" * 80)
        sys.exit(1)
    
    print("✓ Configuration validation passed")


def print_configuration_summary():
    """
    Print a summary of the current configuration.
    
    Useful for debugging and verifying configuration in different environments.
    """
    from .settings import settings
    from .llm_config import llm_settings
    
    print()
    print("=" * 80)
    print("CONFIGURATION SUMMARY")
    print("=" * 80)
    print()
    
    print("Database:")
    print(f"  MongoDB URI: {settings.mongodb_uri}")
    print(f"  Database: {settings.mongodb_db}")
    print()
    
    print("Logging:")
    print(f"  Level: {settings.log_level}")
    print(f"  Format: {settings.log_format}")
    print(f"  Pretty: {settings.log_pretty}")
    print()
    
    print("LLM Configuration:")
    print(f"  Portkey Enabled: {llm_settings.enable_portkey}")
    print(f"  Default Model: {llm_settings.default_model}")
    print(f"  Caching Enabled: {llm_settings.enable_caching}")
    print(f"  Fallbacks Enabled: {llm_settings.enable_fallbacks}")
    print(f"  Cost Tracking Enabled: {llm_settings.enable_cost_tracking}")
    print()
    
    print("Rate Limits:")
    print(f"  Requests/minute: {llm_settings.rate_limit_requests_per_minute}")
    print(f"  Tokens/minute: {llm_settings.rate_limit_tokens_per_minute}")
    print()
    
    print("Cost Budgets:")
    print(f"  Daily: ${llm_settings.cost_budget_daily_usd}")
    print(f"  Monthly: ${llm_settings.cost_budget_monthly_usd}")
    print(f"  Alert Threshold: {llm_settings.cost_alert_threshold}%")
    print()
    
    print("Integrations:")
    print(f"  Sentry: {'Enabled' if settings.sentry_dsn else 'Disabled'}")
    print(f"  Google Cloud: {'Configured' if settings.google_cloud_project_id else 'Not configured'}")
    print(f"  Stripe: {'Configured' if settings.stripe_secret_key else 'Not configured'}")
    print(f"  Resend Email: {'Configured' if settings.resend_api_key else 'Not configured'}")
    print()
    
    print("=" * 80)
    print()


if __name__ == "__main__":
    # Allow running this module directly to validate configuration
    validate_or_exit()
    print_configuration_summary()
