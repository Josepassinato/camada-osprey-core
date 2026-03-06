# Configuration Management

This package provides centralized configuration management for the Osprey backend using Pydantic BaseSettings for type-safe, validated configuration loaded from environment variables.

## Overview

The configuration system is split into two main modules:

1. **`settings.py`** - Core application settings (database, auth, logging, integrations)
2. **`llm_config.py`** - LLM provider configuration, routing, cost management, and Portkey integration

## Quick Start

### Basic Usage

```python
from backend.config import settings, llm_settings

# Access application settings
db_uri = settings.mongodb_uri
jwt_secret = settings.jwt_secret

# Access LLM settings
portkey_key = llm_settings.portkey_api_key
default_model = llm_settings.default_model
```

### Environment Variables

All configuration is loaded from environment variables. Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Core Settings (`settings.py`)

### Required Variables

- `JWT_SECRET` - Secret key for JWT token generation (REQUIRED)

### Database Configuration

- `MONGODB_URI` - MongoDB connection URI (default: `mongodb://localhost:27017`)
- `MONGODB_DB` - Database name (default: `test_database`)

### CORS Configuration

- `CORS_ORIGINS` - Allowed origins, comma-separated or `*` (default: `*`)

### Logging Configuration

- `LOG_LEVEL` - Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: `INFO`)
- `LOG_PRETTY` - Pretty-print logs for development (default: `false`)
- `LOG_FORMAT` - Log format: `json` or `text` (default: `json`)
- `BACKUP_DIR` - Directory for backups (default: `./backups`)

### Optional Integrations

#### Sentry Error Tracking
- `SENTRY_DSN` - Sentry DSN for error tracking
- `SENTRY_ENVIRONMENT` - Environment name (default: `development`)
- `SENTRY_SERVICE_NAME` - Service name (default: `backend`)
- `SENTRY_TRACES_SAMPLE_RATE` - Traces sample rate 0.0-1.0 (default: `0.0`)

#### Google Cloud
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to credentials JSON
- `GOOGLE_CLOUD_PROJECT_ID` - GCP project ID
- `GOOGLE_CLOUD_LOCATION` - GCP region (default: `us`)
- `GEMINI_API_KEY` - Google Gemini API key

#### Stripe Payments
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_PUBLISHABLE_KEY` - Stripe publishable key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret

#### Email (Resend)
- `RESEND_API_KEY` - Resend email service API key

## LLM Configuration (`llm_config.py`)

### Portkey Integration

Portkey.ai provides a unified gateway for all LLM providers with observability, cost tracking, and routing.

#### Required Variables

- `PORTKEY_API_KEY` - Your Portkey API key (get from https://app.portkey.ai/)

#### Optional Variables

- `PORTKEY_BASE_URL` - Portkey API base URL (default: `https://api.portkey.ai/v1`)

### Virtual Keys (Recommended)

Instead of storing provider API keys in environment variables, use Portkey virtual keys:

- `PORTKEY_VIRTUAL_KEY_OPENAI` - Virtual key for OpenAI
- `PORTKEY_VIRTUAL_KEY_ANTHROPIC` - Virtual key for Anthropic
- `PORTKEY_VIRTUAL_KEY_GOOGLE` - Virtual key for Google

**Benefits:**
- Centralized key management in Portkey dashboard
- Easy key rotation without code changes
- Better security (keys never leave Portkey)

### Model Configuration

- `LLM_DEFAULT_MODEL` - Default model to use (default: `gpt-4o`)
- `LLM_DEFAULT_TEMPERATURE` - Default temperature (default: `0.7`)
- `LLM_DEFAULT_MAX_TOKENS` - Default max tokens (default: `4096`)

### Feature Flags

- `LLM_ENABLE_PORTKEY` - Enable Portkey integration (default: `true`)
- `LLM_ENABLE_CACHING` - Enable response caching (default: `true`)
- `LLM_ENABLE_FALLBACKS` - Enable automatic fallbacks (default: `true`)
- `LLM_ENABLE_COST_TRACKING` - Enable cost tracking (default: `true`)

### Rate Limiting

- `LLM_RATE_LIMIT_REQUESTS_PER_MINUTE` - Max requests/minute (default: `60`)
- `LLM_RATE_LIMIT_TOKENS_PER_MINUTE` - Max tokens/minute (default: `90000`)

### Cost Budgets

- `LLM_COST_BUDGET_DAILY_USD` - Daily budget in USD (default: `100.0`)
- `LLM_COST_BUDGET_MONTHLY_USD` - Monthly budget in USD (default: `3000.0`)
- `LLM_COST_ALERT_THRESHOLD` - Alert at % of budget (default: `80.0`)

## Supported Models

The following models are pre-configured with cost and capability information:

### OpenAI
- `gpt-4o` - Latest GPT-4 Omni (vision, function calling)
- `gpt-4-turbo` - GPT-4 Turbo (vision, function calling)
- `gpt-3.5-turbo` - GPT-3.5 Turbo (function calling)

### Google
- `gemini-1.5-pro` - Gemini 1.5 Pro (1M context, vision)
- `gemini-1.5-flash` - Gemini 1.5 Flash (1M context, vision, fast)

### Anthropic
- `claude-3-opus` - Claude 3 Opus (200K context, vision)
- `claude-3-sonnet` - Claude 3 Sonnet (200K context, vision)
- `claude-3-haiku` - Claude 3 Haiku (200K context, vision, fast)

## Usage Examples

### Getting Model Configuration

```python
from backend.config import get_model_config

# Get configuration for a specific model
config = get_model_config("gpt-4o")
print(f"Max tokens: {config.max_tokens}")
print(f"Cost per 1K input tokens: ${config.cost_per_1k_input_tokens}")
print(f"Fallback models: {config.fallback_models}")
```

### Getting Provider Virtual Key

```python
from backend.config import get_provider_virtual_key, LLMProvider

# Get virtual key for OpenAI
openai_key = get_provider_virtual_key(LLMProvider.OPENAI)
```

### Accessing Configuration Objects

```python
from backend.config import llm_settings

# Get Portkey configuration
portkey_config = llm_settings.portkey_config
print(f"Caching enabled: {portkey_config.enable_caching}")
print(f"Retry count: {portkey_config.retry_count}")

# Get rate limit configuration
rate_limits = llm_settings.rate_limit_config
print(f"Requests per minute: {rate_limits.requests_per_minute}")

# Get cost budget configuration
budgets = llm_settings.cost_budget_config
print(f"Daily budget: ${budgets.daily_budget_usd}")
```

## Validation

All configuration is validated at startup using Pydantic validators:

- **Type checking**: Ensures correct types (int, float, bool, str)
- **Range validation**: Ensures values are within valid ranges
- **Required fields**: Raises error if required fields are missing
- **Custom validation**: Business logic validation (e.g., log level must be valid)

### Example Validation Error

```python
# If PORTKEY_API_KEY is missing when LLM_ENABLE_PORTKEY=true
ValidationError: portkey_api_key is required when enable_portkey=True. 
Set PORTKEY_API_KEY environment variable.
```

## Environment-Specific Configuration

Use different `.env` files for different environments:

```bash
# Development
cp .env.example .env.development
# Edit .env.development

# Staging
cp .env.example .env.staging
# Edit .env.staging

# Production
cp .env.example .env.production
# Edit .env.production
```

Load the appropriate file:

```bash
# Development
export ENV_FILE=.env.development
python server.py

# Production
export ENV_FILE=.env.production
python server.py
```

## Security Best Practices

1. **Never commit `.env` files** - They contain secrets
2. **Use virtual keys** - Store provider keys in Portkey, not environment
3. **Rotate keys regularly** - Update keys quarterly
4. **Use strong JWT secrets** - Generate with `openssl rand -hex 32`
5. **Enable Sentry in production** - Track errors and performance
6. **Set cost budgets** - Prevent unexpected LLM costs
7. **Use rate limiting** - Prevent abuse and control costs

## Migration from Legacy Configuration

If you're migrating from the old configuration system:

### Before (Legacy)
```python
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
```

### After (New)
```python
from backend.config import llm_settings

# Use Portkey virtual keys instead
portkey_key = llm_settings.portkey_api_key
openai_virtual_key = llm_settings.portkey_virtual_key_openai
```

## Troubleshooting

### Configuration not loading

1. Check `.env` file exists in backend directory
2. Verify environment variable names match (case-insensitive)
3. Check for validation errors in startup logs

### Portkey integration not working

1. Verify `PORTKEY_API_KEY` is set
2. Check `LLM_ENABLE_PORTKEY=true`
3. Verify virtual keys are configured in Portkey dashboard
4. Check Portkey dashboard for request logs

### Cost tracking not working

1. Verify `LLM_ENABLE_COST_TRACKING=true`
2. Check Portkey dashboard for usage data
3. Ensure virtual keys are properly configured

## Additional Resources

- [Portkey Documentation](https://docs.portkey.ai/)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Environment Variables Best Practices](https://12factor.net/config)
