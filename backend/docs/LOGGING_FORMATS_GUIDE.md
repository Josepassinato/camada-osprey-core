# Logging Formats Guide - Enterprise Grade

## Overview

Osprey supports three logging formats optimized for different use cases:

1. **PLAIN** - Human-readable with emojis (Development/Debugging)
2. **JSON** - Structured ECS-compliant (Production/SIEMs)
3. **CEF** - Common Event Format (Security/SIEM Correlation)

---

## Format Comparison

### 1. PLAIN Format (Development)

**Use Case:** Local development, debugging, log review

**Configuration:**
```bash
LOG_FORMAT=plain
LOG_PRETTY=true
LOG_LEVEL=INFO
```

**Output Example:**
```
2026-01-14 22:43:59 [INFO] ℹ️ Service initialized successfully
2026-01-14 22:43:59 [INFO] ℹ️ Especialista registrado: H-1B
2026-01-14 22:43:59 [INFO] ℹ️ Google Document AI initialized with service account
2026-01-14 22:43:59 [WARNING] ⚠️ Translation service degraded - using fallback
2026-01-14 22:43:59 [ERROR] ❌ Database connection failed - retrying
```

**Features:**
- ✅ Human-readable timestamps
- ✅ Emojis for visual scanning (ℹ️ INFO, ⚠️ WARNING, ❌ ERROR, 🚨 CRITICAL)
- ✅ Clean single-line format
- ✅ Perfect for terminal output
- ✅ Easy to grep and filter

**Emoji Legend:**
- 🔍 DEBUG - Detailed diagnostic information
- ℹ️ INFO - General informational messages
- ⚠️ WARNING - Warning messages
- ❌ ERROR - Error messages
- 🚨 CRITICAL - Critical system failures

---

### 2. JSON Format (Production - Application Logs)

**Use Case:** Production logging, SIEM integration, log aggregation

**Configuration:**
```bash
LOG_FORMAT=json
LOG_PRETTY=false
LOG_LEVEL=WARNING
```

**Output Example (formatted for readability):**
```json
{
  "@timestamp": "2026-01-14T22:43:59.025176+00:00",
  "timestamp": "2026-01-14T22:43:59.025182+00:00",
  "level": "INFO",
  "log.level": "info",
  "severity": 6,
  "message": "Service initialized successfully",
  "host": {
    "name": "osprey-prod-01"
  },
  "logger": "backend.core.logging",
  "log.logger": "backend.core.logging",
  "module": "server",
  "function": "startup",
  "line": 165,
  "file": {
    "path": "/app/backend/server.py",
    "name": "server.py",
    "line": 165
  },
  "process": {
    "pid": 1234,
    "name": "MainProcess"
  },
  "thread": {
    "id": 140234567890,
    "name": "MainThread"
  },
  "service": {
    "name": "osprey-backend",
    "environment": "production",
    "version": "2.0.0"
  },
  "environment": "production",
  "release": "2.0.0"
}
```

**With Context (user action):**
```json
{
  "@timestamp": "2026-01-14T22:43:59.025386+00:00",
  "level": "INFO",
  "message": "Case created successfully",
  "user": {
    "id": "user_123"
  },
  "user_id": "user_123",
  "case_id": "case_456",
  "labels": {
    "case_id": "case_456"
  },
  "trace": {
    "id": "req_789"
  },
  "request_id": "req_789",
  "custom": {
    "duration_ms": 234
  },
  "service": {
    "name": "osprey-backend",
    "environment": "production",
    "version": "2.0.0"
  }
}
```

**Features:**
- ✅ ECS (Elastic Common Schema) compliant
- ✅ No emojis (clean machine-readable)
- ✅ Structured fields for easy parsing
- ✅ Distributed tracing support (trace.id, request_id)
- ✅ User and case correlation (user.id, case_id)
- ✅ Numeric severity levels (RFC 5424)
- ✅ Host and service metadata
- ✅ Exception stack traces included

**Compatible With:**
- ✅ Datadog
- ✅ ELK Stack (Elasticsearch, Logstash, Kibana)
- ✅ Splunk
- ✅ Azure Monitor
- ✅ AWS CloudWatch
- ✅ Google Cloud Logging
- ✅ Sentry

**Key Fields:**
- `@timestamp` - ISO 8601 timestamp (required by most SIEMs)
- `log.level` - Lowercase level (ECS standard)
- `severity` - Numeric severity (2=CRITICAL, 3=ERROR, 4=WARNING, 6=INFO, 7=DEBUG)
- `trace.id` - Distributed tracing ID
- `user.id` - User identifier for correlation
- `service.name` - Service identifier
- `service.environment` - Environment (dev/staging/prod)
- `service.version` - Release version

---

### 3. CEF Format (Production - Security Logs)

**Use Case:** Security monitoring, SIEM correlation, compliance

**Configuration:**
```bash
LOG_FORMAT=cef
LOG_PRETTY=false
LOG_LEVEL=INFO
```

**Output Example:**
```
CEF:0|Osprey|Immigration Platform|2.0.0|backend.core.logging:INFO|Service initialized successfully|3|msg=Service initialized successfully shost=osprey-prod-01 src=osprey-prod-01 dvchost=osprey-prod-01 fname=server.py fline=165 sproc=MainProcess spid=1234 cs3=production cs3Label=Environment
```

**With User Context:**
```
CEF:0|Osprey|Immigration Platform|2.0.0|backend.core.logging:INFO|Case created successfully|3|msg=Case created successfully shost=osprey-prod-01 src=osprey-prod-01 dvchost=osprey-prod-01 fname=server.py fline=43 sproc=MainProcess spid=1234 suser=user_123 cs1=case_456 cs1Label=CaseID cs2=req_789 cs2Label=RequestID cs3=production cs3Label=Environment
```

**With Exception:**
```
CEF:0|Osprey|Immigration Platform|2.0.0|backend.core.logging:ERROR|Validation failed|8|msg=Validation failed shost=osprey-prod-01 src=osprey-prod-01 dvchost=osprey-prod-01 fname=validator.py fline=57 sproc=MainProcess spid=1234 cs3=production cs3Label=Environment cs4=ValueError cs4Label=ExceptionType cs5=Invalid visa type: XYZ cs5Label=ExceptionMessage
```

**CEF Format Structure:**
```
CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension
```

**Features:**
- ✅ Industry-standard security event format
- ✅ No emojis (clean machine-readable)
- ✅ Single-line format for easy parsing
- ✅ Severity scale 0-10 (10=CRITICAL, 8=ERROR, 6=WARNING, 3=INFO, 1=DEBUG)
- ✅ Custom fields for user, case, request correlation
- ✅ Exception type and message included
- ✅ Host and process information

**Compatible With:**
- ✅ ArcSight (Micro Focus)
- ✅ Splunk Enterprise Security
- ✅ Azure Sentinel
- ✅ IBM QRadar
- ✅ LogRhythm
- ✅ AlienVault OSSIM

**CEF Extension Fields:**
- `msg` - Log message
- `shost` - Source hostname
- `src` - Source IP/hostname
- `dvchost` - Device hostname
- `fname` - Source filename
- `fline` - Source line number
- `sproc` - Source process name
- `spid` - Source process ID
- `suser` - Source user ID
- `cs1` - Custom string 1 (Case ID)
- `cs2` - Custom string 2 (Request ID)
- `cs3` - Custom string 3 (Environment)
- `cs4` - Custom string 4 (Exception Type)
- `cs5` - Custom string 5 (Exception Message)

---

## Configuration Examples

### Development (Local)
```bash
# .env
LOG_LEVEL=INFO
LOG_FORMAT=plain
LOG_PRETTY=true
SENTRY_ENVIRONMENT=development
```

**Result:** Clean, readable logs with emojis for easy debugging

---

### Staging (Pre-Production)
```bash
# .env
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_PRETTY=false
SENTRY_ENVIRONMENT=staging
SENTRY_RELEASE=2.0.0-rc.1
```

**Result:** Structured JSON logs for testing SIEM integration

---

### Production (Application Logs)
```bash
# .env
LOG_LEVEL=WARNING
LOG_FORMAT=json
LOG_PRETTY=false
SENTRY_ENVIRONMENT=production
SENTRY_RELEASE=2.0.0
SENTRY_SERVICE_NAME=osprey-backend
```

**Result:** Structured JSON logs sent to Datadog/ELK/Splunk

**Datadog Integration:**
```bash
# Ship logs to Datadog
tail -f /var/log/osprey/app.log | datadog-agent logs
```

**ELK Stack Integration:**
```yaml
# Filebeat configuration
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/osprey/*.log
    json.keys_under_root: true
    json.add_error_key: true
```

---

### Production (Security Logs)
```bash
# .env
LOG_LEVEL=INFO
LOG_FORMAT=cef
LOG_PRETTY=false
SENTRY_ENVIRONMENT=production
SENTRY_RELEASE=2.0.0
```

**Result:** CEF-formatted security events for SIEM correlation

**Azure Sentinel Integration:**
```bash
# Ship CEF logs to Azure Sentinel
rsyslog configuration to forward to Log Analytics workspace
```

**Splunk Enterprise Security:**
```bash
# Splunk inputs.conf
[monitor:///var/log/osprey/security.log]
sourcetype = cef
index = security
```

---

## Structured Logging Best Practices

### Adding Context to Logs

```python
import logging

logger = logging.getLogger(__name__)

# Basic log
logger.info("Case created")

# With context (RECOMMENDED)
logger.info(
    "Case created successfully",
    extra={
        "user_id": user.id,
        "case_id": case.id,
        "request_id": request.headers.get("X-Request-ID"),
        "visa_type": "H-1B",
        "duration_ms": 234
    }
)
```

**JSON Output:**
```json
{
  "message": "Case created successfully",
  "user": {"id": "user_123"},
  "case_id": "case_456",
  "trace": {"id": "req_789"},
  "custom": {
    "visa_type": "H-1B",
    "duration_ms": 234
  }
}
```

**CEF Output:**
```
CEF:0|Osprey|...|msg=Case created successfully suser=user_123 cs1=case_456 cs1Label=CaseID cs2=req_789 cs2Label=RequestID...
```

---

### Exception Logging

```python
try:
    process_visa_application(case_id)
except ValueError as e:
    logger.error(
        "Visa application validation failed",
        exc_info=True,  # Include stack trace
        extra={
            "case_id": case_id,
            "user_id": user_id,
            "error_type": "validation_error"
        }
    )
```

**JSON Output:**
```json
{
  "level": "ERROR",
  "message": "Visa application validation failed",
  "error": {
    "type": "ValueError",
    "message": "Invalid visa type: XYZ",
    "stack_trace": "Traceback (most recent call last):\n  File..."
  },
  "case_id": "case_456",
  "user": {"id": "user_123"}
}
```

---

## Performance Considerations

### Log Volume

**Development:**
- LOG_LEVEL=INFO or DEBUG
- All logs visible for debugging

**Production:**
- LOG_LEVEL=WARNING or ERROR
- Reduces log volume by 80-90%
- Only important events logged

### Log Rotation

```bash
# logrotate configuration
/var/log/osprey/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 osprey osprey
    sharedscripts
    postrotate
        systemctl reload osprey
    endscript
}
```

---

## Querying Logs

### Datadog

```
# Find all errors for a specific user
@user.id:user_123 @level:ERROR

# Find slow operations
@custom.duration_ms:>1000

# Find all case creations
message:"Case created successfully"
```

### ELK Stack (Kibana)

```
# Find authentication failures
log.level:error AND message:*authentication*

# Find operations by case
labels.case_id:"case_456"

# Find distributed trace
trace.id:"req_789"
```

### Splunk

```
# Find security events
sourcetype=cef severity>=8

# Find user activity
suser="user_123"

# Find exceptions
cs4Label="ExceptionType" cs4="ValueError"
```

---

## Summary

| Format | Use Case | Emojis | Structure | Best For |
|--------|----------|--------|-----------|----------|
| **PLAIN** | Development | ✅ Yes | Single-line | Human reading, debugging |
| **JSON** | Production | ❌ No | Structured | SIEMs, log aggregation, analytics |
| **CEF** | Security | ❌ No | Single-line | Security tools, compliance, correlation |

**Recommendation:**
- **Development:** `LOG_FORMAT=plain, LOG_PRETTY=true`
- **Production:** `LOG_FORMAT=json, LOG_PRETTY=false`
- **Security:** `LOG_FORMAT=cef, LOG_PRETTY=false`

---

**Last Updated:** January 14, 2026  
**Version:** 2.0.0
