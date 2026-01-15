# How to Get Stack Traces in Logs

## Problem
When exceptions occur, you only see:
```
INFO:     127.0.0.1:51394 - "GET /api/dashboard HTTP/1.1" 500 Internal Server Error
```

No stack trace is shown, even in DEBUG mode.

## Root Cause

Python's `logger.error()` doesn't include stack traces by default. You must explicitly pass `exc_info=True`:

```python
# ❌ WRONG - No stack trace
try:
    result = await some_operation()
except Exception as e:
    logger.error(f"Error: {str(e)}")
    raise HTTPException(500, detail=str(e))

# ✅ CORRECT - Includes full stack trace
try:
    result = await some_operation()
except Exception as e:
    logger.error(f"Error: {str(e)}", exc_info=True)
    raise HTTPException(500, detail=str(e))
```

## Solution Applied

Updated error handlers throughout the codebase to include `exc_info=True`:

```python
# backend/server.py - Dashboard endpoint
except Exception as e:
    logger.error(f"Error getting dashboard: {str(e)}", exc_info=True)
    raise HTTPException(status_code=500, detail=f"Error getting dashboard: {str(e)}")
```

## How It Works

When `exc_info=True` is passed:
1. Python captures the current exception context
2. The logging formatter extracts the traceback
3. Stack trace is included in the log output

### Plain Format (Development)
```
2026-01-15 02:18:32 [ERROR] ❌ Error getting dashboard: Database not initialized
Traceback (most recent call last):
  File "backend/server.py", line 1750, in get_dashboard
    applications = await db.applications.find(...)
  File "backend/core/database.py", line 20, in __getattr__
    raise AttributeError("Database not initialized")
AttributeError: Database not initialized
```

### JSON Format (Production)
```json
{
  "@timestamp": "2026-01-15T02:18:32.123Z",
  "level": "ERROR",
  "message": "Error getting dashboard: Database not initialized",
  "error": {
    "type": "AttributeError",
    "message": "Database not initialized",
    "stack_trace": "Traceback (most recent call last):\n  File..."
  },
  "file": {
    "path": "backend/server.py",
    "line": 1878
  }
}
```

## Best Practices

### 1. Always Use exc_info=True in Exception Handlers
```python
try:
    # Your code
except Exception as e:
    logger.error("Operation failed", exc_info=True)
    # Handle error
```

### 2. Add Context with extra Parameter
```python
try:
    user = await get_user(user_id)
except Exception as e:
    logger.error(
        "Failed to get user",
        exc_info=True,
        extra={"user_id": user_id}
    )
```

### 3. Use Appropriate Log Levels
```python
# Critical errors that need immediate attention
logger.critical("Database connection lost", exc_info=True)

# Errors that should be investigated
logger.error("Failed to process payment", exc_info=True)

# Warnings for recoverable issues
logger.warning("Rate limit approaching", exc_info=True)

# Info for normal operations (no exc_info needed)
logger.info("User logged in successfully")

# Debug for development (no exc_info needed)
logger.debug("Processing step 3 of 5")
```

### 4. Don't Log Twice
```python
# ❌ WRONG - Logs the same error twice
try:
    result = await operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)
    raise  # This will be logged again by outer handler

# ✅ CORRECT - Log once at the appropriate level
try:
    result = await operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)
    raise HTTPException(500, "Operation failed")  # Generic message to user
```

## Environment Configuration

The logging system respects these environment variables:

```bash
# .env file
LOG_LEVEL=DEBUG          # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=plain         # plain (dev), json (prod), cef (security)
LOG_PRETTY=true          # true (dev), false (prod)
```

### Development Setup
```bash
LOG_LEVEL=DEBUG
LOG_FORMAT=plain
LOG_PRETTY=true
```
- Human-readable logs with emojis
- Full stack traces when exc_info=True
- Logger names hidden for cleaner output

### Production Setup
```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_PRETTY=false
```
- Structured JSON for SIEM integration
- Stack traces in `error.stack_trace` field
- Compatible with Datadog, ELK, Splunk, etc.

## Testing Stack Traces

To verify stack traces are working:

```python
# Add a test endpoint
@api_router.get("/test-error")
async def test_error():
    try:
        raise ValueError("This is a test error")
    except Exception as e:
        logger.error("Test error occurred", exc_info=True)
        raise HTTPException(500, "Test error")
```

Then call it:
```bash
curl http://localhost:8001/api/test-error
```

You should see the full stack trace in your logs.

## Common Patterns

### FastAPI Dependency Errors
```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY)
        return payload
    except jwt.ExpiredSignatureError as e:
        logger.warning("Token expired", exc_info=True, extra={"token": token[:10]})
        raise HTTPException(401, "Token expired")
    except Exception as e:
        logger.error("Auth failed", exc_info=True)
        raise HTTPException(401, "Invalid token")
```

### Database Operations
```python
async def create_case(case_data: dict):
    try:
        result = await db.cases.insert_one(case_data)
        return result.inserted_id
    except Exception as e:
        logger.error(
            "Failed to create case",
            exc_info=True,
            extra={"case_data": case_data}
        )
        raise HTTPException(500, "Failed to create case")
```

### External API Calls
```python
async def call_external_api(url: str):
    try:
        response = await httpx.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException as e:
        logger.warning(f"API timeout: {url}", exc_info=True)
        raise HTTPException(504, "External service timeout")
    except Exception as e:
        logger.error(f"API call failed: {url}", exc_info=True)
        raise HTTPException(502, "External service error")
```

## Summary

✅ **Always use `exc_info=True`** in exception handlers  
✅ **Add context** with the `extra` parameter  
✅ **Use appropriate log levels** (ERROR for exceptions)  
✅ **Don't log the same error twice**  
✅ **Test your logging** to ensure stack traces appear  

This ensures you get full diagnostic information when debugging production issues.
