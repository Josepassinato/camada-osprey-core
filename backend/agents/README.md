# AI Agents Package

This package contains all AI agent implementations for the Osprey platform, including conversational assistants, document processors, and specialized immigration consultants.

## Package Structure

```
agents/
├── base.py              # Base agent class (inherit from this)
├── maria/               # Maria conversational assistant
├── dra_paula/           # Dra. Paula immigration specialist
├── owl/                 # Owl intelligent agent
├── specialized/         # Specialized agents (validators, analysts)
├── qa/                  # Quality assurance agents
└── oracle/              # Oracle consultant agent
```

## BaseAgent Class

All agents should inherit from `BaseAgent`, which provides:

- **Unified LLM Interface**: Consistent way to call LLMs through Portkey
- **Error Handling**: Automatic retry logic and comprehensive error handling
- **Metrics Collection**: Track calls, tokens, latency, and errors
- **Logging**: Structured logging for all agent operations

### Creating a New Agent

```python
from backend.agents.base import BaseAgent
from typing import Dict, Any

class MyAgent(BaseAgent):
    """My custom agent"""
    
    def __init__(self):
        super().__init__(
            agent_name="my_agent",
            default_model="gpt-4o",
            default_temperature=0.7
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result"""
        # Build messages
        messages = self._build_messages(
            system_prompt="You are a helpful assistant.",
            user_message=input_data.get("message")
        )
        
        # Call LLM
        response = await self._call_llm(messages)
        
        return {
            "success": True,
            "response": response
        }
```

### BaseAgent Methods

#### Required Methods

- `async def process(input_data: Dict[str, Any]) -> Dict[str, Any]`
  - **Must be implemented by all subclasses**
  - Main entry point for agent processing

#### Helper Methods

- `async def _call_llm(messages, model=None, temperature=None, **kwargs) -> str`
  - Call LLM and return content string
  - Handles errors, retries, and metrics automatically
  - Supports Portkey prompt templates via `prompt_id` parameter

- `async def _call_llm_with_response(messages, **kwargs) -> LLMResponse`
  - Call LLM and return full response object
  - Use when you need usage stats or metadata

- `def _build_messages(system_prompt=None, user_message=None, conversation_history=None) -> List[ChatMessage]`
  - Helper to construct message lists
  - Handles system prompts, user messages, and conversation history

#### Metrics Methods

- `def get_metrics() -> Dict[str, Any]`
  - Get agent performance metrics
  - Returns: total_calls, success_rate, avg_tokens, avg_latency, errors

- `def reset_metrics() -> None`
  - Reset metrics to zero

### Error Handling

The BaseAgent automatically handles these LLM errors:

- **LLMRateLimitError**: Rate limit exceeded (automatic retry with backoff)
- **LLMTimeoutError**: Request timeout (automatic retry)
- **LLMCircuitBreakerError**: Circuit breaker open (provider temporarily disabled)
- **LLMProviderError**: Provider-specific errors (automatic retry)
- **LLMException**: Generic LLM errors

All errors are logged with appropriate context and included in metrics.

### Using Portkey Prompt Templates

```python
# Instead of hardcoded prompts
response = await self._call_llm(
    messages=[],  # Empty messages
    prompt_id="pp-my-prompt-v1",  # Portkey prompt ID
    variables={  # Variables to substitute
        "user_name": "John",
        "language": "English"
    }
)
```

### Metrics Example

```python
agent = MyAgent()

# After some processing...
metrics = agent.get_metrics()

print(f"Total calls: {metrics['total_calls']}")
print(f"Success rate: {metrics['success_rate']:.2f}%")
print(f"Avg tokens: {metrics['avg_tokens_per_call']:.0f}")
print(f"Avg latency: {metrics['avg_latency_ms']:.0f}ms")
print(f"Errors: {metrics['errors']}")
```

## Best Practices

1. **Always inherit from BaseAgent** - Don't create agents from scratch
2. **Use `_call_llm()` for LLM calls** - Don't call Portkey directly
3. **Implement proper error handling** - Let BaseAgent handle retries, but catch exceptions in `process()`
4. **Log important operations** - Use `logger.info()` for key events
5. **Return consistent response format** - Include `success` boolean and relevant data
6. **Use Portkey prompts** - Migrate hardcoded prompts to Portkey for versioning
7. **Monitor metrics** - Check agent metrics regularly to identify issues

## Migration from Legacy Agents

If you have an existing agent that doesn't use BaseAgent:

1. Make it inherit from `BaseAgent`
2. Replace direct OpenAI/Gemini calls with `_call_llm()`
3. Remove manual error handling (BaseAgent handles it)
4. Remove manual metrics tracking (BaseAgent handles it)
5. Update imports to use relative imports (`from ..llm import ...`)

Example migration:

```python
# Before
class OldAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def process(self, data):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": data["message"]}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error: {e}")
            raise

# After
class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="new_agent")
    
    async def process(self, data):
        messages = self._build_messages(user_message=data["message"])
        response = await self._call_llm(messages)
        return {"success": True, "response": response}
```

## Testing Agents

```python
import pytest
from backend.agents.my_agent import MyAgent

@pytest.mark.asyncio
async def test_my_agent():
    agent = MyAgent()
    
    result = await agent.process({
        "message": "Test message"
    })
    
    assert result["success"] is True
    assert "response" in result
    
    # Check metrics
    metrics = agent.get_metrics()
    assert metrics["total_calls"] == 1
    assert metrics["successful_calls"] == 1
```

## Requirements

- Python 3.11+
- Portkey AI SDK (`portkey-ai>=1.0.0`)
- OpenAI SDK v2 (`openai>=2.0.0`)
- Environment variable: `PORTKEY_API_KEY`

## Related Documentation

- [LLM Package README](../llm/README.md) - LLM client and Portkey integration
- [Config Package README](../config/README.md) - Configuration management
- [Design Document](../../.kiro/specs/backend-refactoring-portkey/design.md) - Architecture details
