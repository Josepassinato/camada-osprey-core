# Logging Configuration Guide

## Overview

The Osprey backend uses a flexible, production-ready logging system that supports both development and production environments with multiple output formats.

## Configuration

Logging is configured via environment variables in `backend/.env`:

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log format: plain (human-readable) or json (structured)
LOG_FORMAT=plain

# Pretty print: true (clean output) or false (detailed output)
LOG_PRETTY=true
```

## Format Options

### 1. Plain Format (Development)

**Plain + Pretty** (Recommended for development)
```bash
LOG_FORMAT=plain
LOG_PRETTY=true
```

Output:
```
2026-01-14 22:26:22 [INFO] ✅ Service account credentials loaded successfully
2026-01-14 22:26:22 [WARNING] ⚠️ Translation service degraded
2026-01-14 22:26:22 [ERROR] ❌ Database connection failed
```

**Plain + Not Pretty** (Debugging)
```bash
LOG_FORMAT=plain
LOG_PRETTY=false
```

Output:
```
2026-01-14 22:26:22 [INFO] core.logging: ✅ Service account credentials loaded successfully
2026-01-14 22:26:22 [WARNING] utils.translation: ⚠️ Translation service degraded
2026-01-14 22:26:22 [ERROR] core.database: ❌ Database connection failed
```

### 2. JSON Format (Production)

**JSON + Not Pretty** (Recommended for production)
```bash
LOG_FORMAT=json
LOG_PRETTY=false
```

Output (single line per log):
```json
{"@timestamp":"2026-01-14T22:26:22.123456+00:00","level":"INFO","message":"✅ Service loaded","logger":"core.logging","module":"server","function":"startup","line":42,"file":{"path":"/app/server.py","name":"server.py","line":42},"process":{"pid":1234,"name":"MainProcess"},"thread":{"id":12345,"name":"MainThread"},"service":{"name":"backend","environment":"production"}}
```

**JSON + Pretty** (Production debugging)
```bash
LOG_FORMAT=json
LOG_PRETTY=true
```

Output (formatted for readability):
```json
{
  "@timestamp": "2026-01-14T22:26:22.123456+00:00",
  "level": "INFO",
  "log.level": "info",
  "message": "✅ Service loaded",
  "logger": "core.logging",
  "module": "server",
  "function": "startup",
  "line": 42,
  "file": {
    "path": "/app/server.py",
    "name": "server.py",
    "line": 42
  },
  "process": {
    "pid": 1234,
    "name": "MainProcess"
  },
  "thread": {
    "id": 12345,
    "name": "MainThread"
  },
  "service": {
    "name": "backend",
    "environment": "production"
  }
}
```

## Structured Logging with Context

Add context to logs using the `extra` parameter:

```python
import logging
logger = logging.getLogger(__name__)

logger.info(
    "Case created successfully",
    extra={
        "user_id": "user_123",
        "case_id": "case_456",
        "request_id": "req_789",
        "duration_ms": 234
    }
)
```

In JSON format, this context is automatically structured:
```json
{
  "@timestamp": "2026-01-14T22:26:22.123456+00:00",
  "level": "INFO",
  "message": "Case created successfully",
  "user": {"id": "user_123"},
  "case_id": "case_456",
  "trace": {"id": "req_789"},
  "custom": {"duration_ms": 234}
}
```

## SIEM Integration

The JSON format follows the **Elastic Common Schema (ECS)** and is compatible with:

- ✅ **Sentry** - Error tracking and performance monitoring
- ✅ **ELK Stack** - Elasticsearch, Logstash, Kibana
- ✅ **Datadog** - Application performance monitoring
- ✅ **Splunk** - Security information and event management
- ✅ **AWS CloudWatch** - AWS native logging
- ✅ **Google Cloud Logging** - GCP native logging
- ✅ **Azure Monitor** - Azure native logging

### Key ECS Fields

- `@timestamp` - ISO 8601 timestamp (required by most SIEMs)
- `log.level` - Lowercase log level (ECS standard)
- `log.logger` - Logger name (ECS standard)
- `file.path`, `file.name`, `file.line` - Source location
- `process.pid`, `process.name` - Process information
- `thread.id`, `thread.name` - Thread information
- `service.name`, `service.environment` - Service metadata
- `user.id` - User context (when available)
- `trace.id` - Distributed tracing ID (when available)
- `error.type`, `error.message`, `error.stack_trace` - Exception details

## Environment-Specific Recommendations

### Development
```bash
LOG_LEVEL=INFO
LOG_FORMAT=plain
LOG_PRETTY=true
```
- Clean, readable output with emojis
- Easy to scan during development
- No logger names cluttering output

### Staging
```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_PRETTY=false
```
- Structured logs for analysis
- Compatible with log aggregation tools
- Single-line format for efficient parsing

### Production
```bash
LOG_LEVEL=WARNING
LOG_FORMAT=json
LOG_PRETTY=false
SENTRY_ENVIRONMENT=production
```
- Only warnings and errors logged
- Structured JSON for SIEM ingestion
- Sentry integration for error tracking
- Reduced log volume for cost optimization

## Testing Logging Configuration

Run the test script to verify all format combinations:

```bash
cd backend
python3 test_logging.py
```

This will test all 4 combinations:
1. plain + pretty
2. plain + not-pretty
3. json + pretty
4. json + not-pretty

## Implementation Details

The logging system is implemented in `backend/core/logging.py`:

- `JSONFormatter` - Structured JSON output with ECS compliance
- `PlainTextFormatter` - Human-readable single-line output
- `ContextFilter` - Adds service metadata to all logs
- `setup_logging()` - Configures logging based on environment variables

## Best Practices

1. **Use structured logging** - Always use `logger.info()` with `extra` parameter for context
2. **Never use print()** - All output should go through the logging system
3. **Log at appropriate levels**:
   - `DEBUG` - Detailed diagnostic information
   - `INFO` - General informational messages (service startup, configuration)
   - `WARNING` - Warning messages (degraded service, fallback mode)
   - `ERROR` - Error messages (failed operations, exceptions)
   - `CRITICAL` - Critical errors (system failure, data corruption)
4. **Include context** - Add user_id, case_id, request_id for traceability
5. **Use emojis consistently** - ✅ success, ⚠️ warning, ❌ error, 🔗 connection, 🔑 credentials

## Troubleshooting

### Logs not appearing
- Check `LOG_LEVEL` - set to `INFO` or `DEBUG`
- Verify logging is configured: `from backend.core.logging import setup_logging; setup_logging()`

### JSON logs not parsing in SIEM
- Ensure `LOG_PRETTY=false` for single-line JSON
- Verify `@timestamp` field is present
- Check SIEM expects ECS format

### Too many logs in production
- Increase `LOG_LEVEL` to `WARNING` or `ERROR`
- Review log statements - use appropriate levels
- Consider sampling for high-volume operations

## Migration Notes

### From Previous Configuration

The logging system now supports both `plain` and `text` as format values (they are equivalent). The Settings model has been updated to accept both for backward compatibility.

**Before:**
```bash
LOG_FORMAT=text  # Old format name
```

**After:**
```bash
LOG_FORMAT=plain  # New format name (text still works)
```

Both values produce the same human-readable output.
