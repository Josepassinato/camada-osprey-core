---
inclusion: fileMatch
fileMatchPattern: '**/agents/**/*.py'
---

# AI/LLM Integration Patterns

## AI Stack
- **OpenAI GPT-4o** - Primary LLM for form generation and validation
- **Google Gemini 1.5 Pro** - Alternative LLM provider
- **Google Document AI** - OCR and document processing

## Agent Architecture Pattern

```python
import openai
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

async def process_with_agent(
    data: Dict[str, Any],
    model: str = "gpt-4o",
    temperature: float = 0.3
) -> Dict[str, Any]:
    """
    Specialized agent for specific task.

    Args:
        data: Input data for processing
        model: LLM model to use
        temperature: Sampling temperature (0.0-1.0)

    Returns:
        dict: Processing results with confidence score
    """
    try:
        logger.info(
            "Processing with AI agent",
            extra={
                "model": model,
                "temperature": temperature,
                "data_keys": list(data.keys())
            }
        )

        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert immigration specialist..."
                },
                {
                    "role": "user",
                    "content": f"Process the following data: {data}"
                }
            ],
            temperature=temperature
        )

        result = response.choices[0].message.content

        logger.info(
            "AI agent processing completed",
            extra={
                "model": model,
                "tokens_used": response.usage.total_tokens
            }
        )

        return {
            "status": "completed",
            "result": result,
            "confidence": 0.95,
            "model": model,
            "tokens_used": response.usage.total_tokens
        }

    except Exception as e:
        logger.error(
            "AI agent processing failed",
            extra={
                "model": model,
                "error": str(e)
            }
        )
        raise
```

## Best Practices

### 1. Always Use Async
```python
# ✅ CORRECT
response = await openai.ChatCompletion.acreate(...)

# ❌ WRONG
response = openai.ChatCompletion.create(...)  # Blocks event loop
```

### 2. Log Token Usage
```python
logger.info(
    "LLM call completed",
    extra={
        "model": model,
        "tokens_used": response.usage.total_tokens,
        "cost_estimate": calculate_cost(response.usage)
    }
)
```

### 3. Handle Rate Limits
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_llm_with_retry(prompt: str):
    return await openai.ChatCompletion.acreate(...)
```

### 4. Validate LLM Output
```python
from pydantic import BaseModel

class LLMResponse(BaseModel):
    field_name: str
    field_value: str
    confidence: float

# Parse and validate
result = LLMResponse.model_validate_json(response.choices[0].message.content)
```

### 5. Use Structured Outputs
```python
response = await openai.ChatCompletion.acreate(
    model="gpt-4o",
    messages=[...],
    response_format={"type": "json_object"}  # Force JSON output
)
```

## Multi-Agent Orchestration

```python
async def orchestrate_agents(case_data: dict) -> dict:
    """
    Orchestrate multiple AI agents for complex processing.
    """
    # Step 1: Document extraction
    extracted_data = await document_extraction_agent(case_data["documents"])
    
    # Step 2: Validation
    validation_result = await validation_agent(extracted_data)
    
    # Step 3: Form generation
    if validation_result["is_valid"]:
        form_data = await form_generation_agent(extracted_data)
        return form_data
    else:
        return {"error": "Validation failed", "details": validation_result}
```

## Error Handling

```python
try:
    result = await openai.ChatCompletion.acreate(...)
except openai.error.RateLimitError:
    logger.warning("Rate limit hit, retrying...")
    await asyncio.sleep(5)
    result = await openai.ChatCompletion.acreate(...)
except openai.error.APIError as e:
    logger.error(f"OpenAI API error: {e}")
    raise HTTPException(503, "AI service temporarily unavailable")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(500, "Internal server error")
```
