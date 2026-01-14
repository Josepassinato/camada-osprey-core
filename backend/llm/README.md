# LLM Abstraction Layer

This package provides a unified interface for LLM operations with Portkey.ai integration, offering observability, cost tracking, and multi-provider routing capabilities.

## Components

### `portkey_client.py` - Main LLM Client

The `LLMClient` class provides a consistent interface for all LLM operations:

```python
from backend.llm.portkey_client import LLMClient
from backend.llm.types import ChatMessage, MessageRole

# Initialize client
client = LLMClient(
    api_key="your-portkey-api-key",  # Or set PORTKEY_API_KEY env var
    virtual_key="your-virtual-key",   # Optional: for provider routing
    max_retries=3,
    timeout=60.0
)

# Chat completion
messages = [
    ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
    ChatMessage(role=MessageRole.USER, content="Hello!")
]

response = await client.chat_completion(
    messages=messages,
    model="gpt-4o",
    temperature=0.7,
    max_tokens=1000
)

print(response.content)
print(f"Tokens used: {response.usage.total_tokens}")
```

### `types.py` - Data Models

Pydantic models for type-safe LLM operations:

- `MessageRole`: Enum for message roles (system, user, assistant, developer)
- `ChatMessage`: Individual chat message
- `LLMRequest`: Complete request specification
- `LLMResponse`: Standardized response format
- `PromptMetadata`: Metadata for Portkey prompt templates
- `ModelConfig`: Configuration for specific models

### `exceptions.py` - Exception Classes

Custom exceptions for detailed error handling:

- `LLMException`: Base exception
- `LLMProviderError`: Provider-specific errors
- `LLMRateLimitError`: Rate limit exceeded
- `LLMCostLimitError`: Cost budget exceeded
- `LLMTimeoutError`: Request timeout
- `PromptNotFoundError`: Portkey prompt not found
- `LLMValidationError`: Input validation failed
- `LLMCircuitBreakerError`: Circuit breaker open
- `LLMContentFilterError`: Content filtered by provider

### `helpers.py` - Utility Functions

Helper classes for advanced features:

#### Provider Router

```python
from backend.llm.helpers import get_provider_router

router = get_provider_router()
provider, virtual_key = router.get_provider_for_model("gpt-4o")
```

#### Fallback Chain

```python
from backend.llm.helpers import get_fallback_chain

chain = get_fallback_chain()
fallbacks = chain.get_fallback_chain("gpt-4o")
# Returns: ["gpt-4-turbo", "gpt-3.5-turbo"]

next_model = chain.get_next_fallback("gpt-4o", failed_models=["gpt-4o"])
# Returns: "gpt-4-turbo"
```

#### Cache Manager

```python
from backend.llm.helpers import get_cache_manager

cache = get_cache_manager()

# Check cache
cached_response = cache.get(model, messages, temperature, max_tokens)
if cached_response:
    return cached_response

# Cache response
cache.set(model, messages, temperature, max_tokens, response)

# Get stats
stats = cache.get_stats()
print(f"Cache hit rate: {stats['hit_rate_percent']}%")
```

#### Metrics Collector

```python
from backend.llm.helpers import get_metrics_collector

metrics = get_metrics_collector()

# Record request
metrics.record_request(
    model="gpt-4o",
    input_tokens=100,
    output_tokens=50,
    latency_ms=1234.5,
    success=True
)

# Get summary
summary = metrics.get_metrics_summary()
print(f"Total cost: ${summary['total_cost_usd']}")
print(f"Average latency: {summary['average_latency_ms']}ms")
```

## Features

### 1. Automatic Retries with Exponential Backoff

The client automatically retries failed requests with exponential backoff:

```python
client = LLMClient(max_retries=3)  # Will retry up to 3 times
```

### 2. Circuit Breaker

Prevents cascading failures by temporarily disabling failing providers:

```python
client = LLMClient(enable_circuit_breaker=True)
```

### 3. Streaming Responses

Stream responses for better UX:

```python
async for chunk in client.stream_completion(messages=messages, model="gpt-4o"):
    print(chunk, end="", flush=True)
```

### 4. Portkey Prompt Templates

Use managed prompts from Portkey:

```python
response = await client.completion_with_prompt(
    prompt_id="pp-greeting-v1",
    variables={"user_name": "John", "language": "English"}
)
```

### 5. Cost Tracking

Automatic cost calculation and tracking:

```python
metrics = get_metrics_collector()
total_cost = metrics.get_total_cost()
print(f"Total spend: ${total_cost:.4f}")
```

### 6. Response Caching

Semantic caching to reduce costs:

```python
# Caching is enabled by default
# Set LLM_ENABLE_CACHING=false to disable
```

## Configuration

Configuration is managed through environment variables (see `backend/config/llm_config.py`):

```bash
# Portkey Configuration
PORTKEY_API_KEY=your-api-key
PORTKEY_VIRTUAL_KEY_OPENAI=your-openai-virtual-key
PORTKEY_VIRTUAL_KEY_ANTHROPIC=your-anthropic-virtual-key
PORTKEY_VIRTUAL_KEY_GOOGLE=your-google-virtual-key

# Default Settings
LLM_DEFAULT_MODEL=gpt-4o
LLM_DEFAULT_TEMPERATURE=0.7
LLM_DEFAULT_MAX_TOKENS=4096

# Feature Flags
LLM_ENABLE_PORTKEY=true
LLM_ENABLE_CACHING=true
LLM_ENABLE_FALLBACKS=true
LLM_ENABLE_COST_TRACKING=true

# Rate Limiting
LLM_RATE_LIMIT_REQUESTS_PER_MINUTE=60
LLM_RATE_LIMIT_TOKENS_PER_MINUTE=90000

# Cost Budgets
LLM_COST_BUDGET_DAILY_USD=100.0
LLM_COST_BUDGET_MONTHLY_USD=3000.0
LLM_COST_ALERT_THRESHOLD=80.0
```

## Error Handling

Always wrap LLM calls in try-except blocks:

```python
from backend.llm.exceptions import (
    LLMRateLimitError,
    LLMTimeoutError,
    LLMProviderError
)

try:
    response = await client.chat_completion(messages=messages)
except LLMRateLimitError as e:
    logger.warning(f"Rate limited: {e}")
    # Wait and retry
except LLMTimeoutError as e:
    logger.error(f"Request timed out: {e}")
    # Use cached response or return error
except LLMProviderError as e:
    logger.error(f"Provider error: {e}")
    # Try fallback model
```

## Best Practices

1. **Use Type Hints**: Always use `ChatMessage` objects for type safety
2. **Handle Errors**: Wrap all LLM calls in try-except blocks
3. **Set Timeouts**: Configure appropriate timeouts for your use case
4. **Monitor Costs**: Regularly check metrics to track spending
5. **Use Caching**: Enable caching for repeated queries
6. **Configure Fallbacks**: Set up fallback chains for reliability
7. **Log Metadata**: Include metadata in requests for better observability

## Testing

Mock the LLM client in tests:

```python
from unittest.mock import AsyncMock, patch
from backend.llm.portkey_client import LLMClient
from backend.llm.types import LLMResponse, LLMUsage

@pytest.mark.asyncio
async def test_my_agent():
    mock_response = LLMResponse(
        content="Test response",
        model="gpt-4o",
        usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        finish_reason="stop"
    )
    
    with patch.object(LLMClient, 'chat_completion', new_callable=AsyncMock) as mock:
        mock.return_value = mock_response
        
        # Test your code
        result = await my_function()
        assert result == "expected"
```

## Migration from Direct OpenAI/Gemini

### Before (Direct OpenAI):

```python
import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
content = response.choices[0].message.content
```

### After (LLMClient):

```python
from backend.llm.portkey_client import LLMClient
from backend.llm.types import ChatMessage, MessageRole

client = LLMClient()
response = await client.chat_completion(
    messages=[ChatMessage(role=MessageRole.USER, content="Hello")],
    model="gpt-4o"
)
content = response.content
```

## Observability

All requests are automatically tracked in the Portkey dashboard:

1. **Request Logs**: View all LLM requests with full context
2. **Cost Analytics**: Track spending by model, user, or feature
3. **Performance Metrics**: Monitor latency and error rates
4. **Prompt Versions**: A/B test different prompt versions

Access the dashboard at: https://app.portkey.ai

## Support

For issues or questions:
- Check the [Portkey documentation](https://docs.portkey.ai)
- Review the design document: `.kiro/specs/backend-refactoring-portkey/design.md`
- Contact the backend team
