"""
Application settings and configuration management.

This module provides centralized configuration using Pydantic BaseSettings,
loading values from environment variables with validation and type safety.
"""

from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Main application settings loaded from environment variables."""
    
    # Database Configuration
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI"
    )
    mongodb_db: str = Field(
        default="test_database",
        description="MongoDB database name"
    )
    
    # Authentication
    jwt_secret: str = Field(
        ...,
        description="Secret key for JWT token generation"
    )
    
    # CORS Configuration
    cors_origins: str = Field(
        default="*",
        description="Allowed CORS origins (comma-separated or *)"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_pretty: bool = Field(
        default=False,
        description="Enable pretty-printed logs (for development)"
    )
    log_format: str = Field(
        default="json",
        description="Log format (json or text)"
    )
    backup_dir: str = Field(
        default="./backups",
        description="Directory for database backups"
    )
    
    # Sentry Configuration (Optional)
    sentry_dsn: Optional[str] = Field(
        default=None,
        description="Sentry DSN for error tracking"
    )
    sentry_environment: str = Field(
        default="development",
        description="Sentry environment name"
    )
    sentry_service_name: str = Field(
        default="backend",
        description="Service name for Sentry"
    )
    sentry_server_name: Optional[str] = Field(
        default=None,
        description="Server name for Sentry"
    )
    sentry_tags: str = Field(
        default="service=backend,component=api",
        description="Comma-separated key=value tags for Sentry"
    )
    sentry_release: Optional[str] = Field(
        default=None,
        description="Release version for Sentry"
    )
    sentry_traces_sample_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Sentry traces sample rate (0.0-1.0)"
    )
    sentry_profiles_sample_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Sentry profiles sample rate (0.0-1.0)"
    )
    sentry_debug: bool = Field(
        default=False,
        description="Enable Sentry debug mode"
    )
    sentry_send_pii: bool = Field(
        default=False,
        description="Send personally identifiable information to Sentry"
    )
    
    # Google Cloud Configuration (Optional)
    google_application_credentials: Optional[str] = Field(
        default=None,
        description="Path to Google Cloud credentials JSON file"
    )
    google_cloud_project_id: Optional[str] = Field(
        default=None,
        description="Google Cloud project ID"
    )
    google_cloud_location: str = Field(
        default="us",
        description="Google Cloud location/region"
    )
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Google Gemini API key"
    )
    
    # Stripe Configuration (Optional)
    stripe_secret_key: Optional[str] = Field(
        default=None,
        description="Stripe secret key"
    )
    stripe_api_key: Optional[str] = Field(
        default=None,
        description="Stripe API key (legacy, use stripe_secret_key)"
    )
    stripe_publishable_key: Optional[str] = Field(
        default=None,
        description="Stripe publishable key"
    )
    stripe_webhook_secret: Optional[str] = Field(
        default=None,
        description="Stripe webhook secret"
    )
    
    # Email Configuration (Optional)
    resend_api_key: Optional[str] = Field(
        default=None,
        description="Resend email service API key"
    )
    
    # Portkey Configuration
    portkey_api_key: Optional[str] = Field(
        default=None,
        description="Portkey API key for LLM routing and observability"
    )
    enable_portkey: bool = Field(
        default=False,
        description="Enable Portkey integration for LLM calls"
    )
    
    # Legacy LLM Keys (to be deprecated)
    emergent_llm_key: Optional[str] = Field(
        default=None,
        description="Legacy Emergent LLM key (deprecated, use Portkey)"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key (legacy, use Portkey virtual keys)"
    )
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level is one of the allowed values."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v.upper()
    
    @validator("log_format")
    def validate_log_format(cls, v):
        """Validate log format is one of the allowed values."""
        allowed = ["json", "text", "plain"]
        v_lower = v.lower()
        if v_lower not in allowed:
            raise ValueError(f"log_format must be one of {allowed}")
        # Map 'plain' to 'text' for backward compatibility with logging.py
        # Both 'plain' and 'text' mean human-readable format
        return "plain" if v_lower in ["plain", "text"] else v_lower
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields that don't belong to this Settings class


# Global settings instance
settings = Settings()
