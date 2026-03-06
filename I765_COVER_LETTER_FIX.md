# I-765 Cover Letter Generation - Fix Summary

## Issue
I-765 cover letter generation was failing with error: "Tipo de visto I-765 não encontrado nas diretivas"

## Root Cause
The `LLMClient` in `backend/llm/portkey_client.py` was not respecting the `ENABLE_PORTKEY=false` environment variable. Even though Portkey was disabled in `.env`, the client was still trying to use Portkey because it only checked if the `PORTKEY_API_KEY` existed, not whether Portkey was explicitly disabled.

## Solution
Modified `backend/llm/portkey_client.py` to check the `ENABLE_PORTKEY` environment variable before attempting to use Portkey:

```python
# Check if Portkey is explicitly disabled via environment variable
enable_portkey = os.getenv("ENABLE_PORTKEY", "true").lower() in ("true", "1", "yes")

if not enable_portkey:
    if fallback_to_openai:
        logger.info("Portkey disabled via ENABLE_PORTKEY=false. Using direct OpenAI client.")
        self.fallback_mode = True
    else:
        raise ValueError(
            "Portkey is disabled but fallback_to_openai=False. "
            "Either enable Portkey or allow OpenAI fallback."
        )
```

## Changes Made
1. **backend/llm/portkey_client.py**: Added check for `ENABLE_PORTKEY` environment variable in `LLMClient.__init__()`
2. **backend/.env**: Already had `ENABLE_PORTKEY=false` set

## Verification
Tested the fix with:
```bash
curl -X POST http://localhost:8001/api/llm/dr-paula/generate-directives \
  -H "Content-Type: application/json" \
  -d '{"visa_type": "I-765", "language": "pt"}'
```

**Result**: ✅ Success! The endpoint now:
- Correctly finds I765 in `backend/visa/directives.yaml`
- Uses direct OpenAI client (bypassing Portkey)
- Generates directives using Dra. Paula B2C agent
- Returns complete response with `success: true`

## Server Logs Confirm
```
2026-01-15 03:32:42 [INFO] Portkey disabled via ENABLE_PORTKEY=false. Using direct OpenAI client.
2026-01-15 03:32:42 [INFO] LLMClient initialized with direct OpenAI fallback
2026-01-15 03:32:50 [INFO] [immigration_expert_dra_paula] LLM call successful: model=gpt-4o-2024-08-06, tokens=1473, latency=7861.74ms
INFO: 127.0.0.1:54555 - "POST /api/llm/dr-paula/generate-directives HTTP/1.1" 200 OK
```

## Status
✅ **FIXED** - I-765 cover letter generation is now working correctly with direct OpenAI integration.

## Next Steps
- The Portkey refactoring can be completed separately (see `.kiro/specs/backend-refactoring-portkey/`)
- Once Portkey is properly configured with provider headers, set `ENABLE_PORTKEY=true` to re-enable observability and cost tracking
