import json
import logging
import os
import re
import socket
import sys
from datetime import datetime, timezone
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Industry-standard JSON formatter for structured logging.
    Compatible with Sentry, ELK Stack, Datadog, Splunk, Azure Sentinel, and other SIEMs.
    Follows the Elastic Common Schema (ECS) where applicable.

    Removes emojis for clean machine-readable logs.
    """

    def __init__(self, pretty: bool = False):
        super().__init__()
        self.pretty = pretty
        self.hostname = socket.gethostname()
        # Emoji removal regex
        self.emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map symbols
            "\U0001f1e0-\U0001f1ff"  # flags (iOS)
            "\U00002702-\U000027b0"
            "\U000024c2-\U0001f251"
            "\u2600-\u26ff"  # misc symbols
            "\u2700-\u27bf"
            "]+",
            flags=re.UNICODE,
        )

    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text for clean machine-readable logs"""
        return self.emoji_pattern.sub("", text).strip()

    def format(self, record: logging.LogRecord) -> str:
        # Clean message (remove emojis)
        clean_message = self._remove_emojis(record.getMessage())

        # Base log structure following ECS/industry standards
        log_data: Dict[str, Any] = {
            # Timestamp in ISO 8601 format (required by most SIEMs)
            "@timestamp": datetime.now(timezone.utc).isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat(),  # Backward compatibility
            # Log level and message
            "level": record.levelname,
            "log.level": record.levelname.lower(),  # ECS format
            "severity": self._get_severity_number(record.levelname),  # Numeric severity
            "message": clean_message,
            # Host information
            "host": {
                "name": self.hostname,
            },
            # Source information
            "logger": record.name,
            "log.logger": record.name,  # ECS format
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "file": {
                "path": record.pathname,
                "name": record.filename,
                "line": record.lineno,
            },
            # Process information
            "process": {
                "pid": record.process,
                "name": record.processName,
            },
            "thread": {
                "id": record.thread,
                "name": record.threadName,
            },
        }

        # Exception information (if present)
        if record.exc_info:
            log_data["error"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "stack_trace": self.formatException(record.exc_info),
            }
            log_data["exception"] = self.formatException(record.exc_info)  # Backward compatibility

        # Custom context fields (for tracing and correlation)
        if hasattr(record, "user_id"):
            log_data["user"] = {"id": record.user_id}
            log_data["user_id"] = record.user_id  # Backward compatibility

        if hasattr(record, "case_id"):
            log_data["case_id"] = record.case_id
            log_data["labels"] = log_data.get("labels", {})
            log_data["labels"]["case_id"] = record.case_id

        if hasattr(record, "request_id"):
            log_data["trace"] = {"id": record.request_id}
            log_data["request_id"] = record.request_id  # Backward compatibility

        # Service information (for distributed tracing)
        service_name = os.environ.get("SENTRY_SERVICE_NAME", "osprey-backend")
        environment = os.environ.get("SENTRY_ENVIRONMENT", "development")
        release = os.environ.get("SENTRY_RELEASE")

        log_data["service"] = {
            "name": service_name,
            "environment": environment,
        }
        if release:
            log_data["service"]["version"] = release

        log_data["environment"] = environment  # Backward compatibility
        if release:
            log_data["release"] = release

        # Additional custom fields from extra parameter
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
                "user_id",
                "case_id",
                "request_id",
                "service",
                "environment",
                "release",
                "taskName",
            } and not key.startswith("_"):
                log_data["custom"] = log_data.get("custom", {})
                log_data["custom"][key] = value

        # Format output
        if self.pretty:
            return json.dumps(log_data, ensure_ascii=False, indent=2, default=str)
        return json.dumps(log_data, ensure_ascii=False, default=str)

    def _get_severity_number(self, level_name: str) -> int:
        """Convert log level to numeric severity (RFC 5424 Syslog)"""
        severity_map = {
            "CRITICAL": 2,  # Critical
            "ERROR": 3,  # Error
            "WARNING": 4,  # Warning
            "INFO": 6,  # Informational
            "DEBUG": 7,  # Debug
        }
        return severity_map.get(level_name, 6)


class CEFFormatter(logging.Formatter):
    """
    Common Event Format (CEF) formatter for security tools.
    Compatible with ArcSight, Splunk Enterprise Security, Azure Sentinel, QRadar.

    CEF Format:
    CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension
    """

    def __init__(self):
        super().__init__()
        self.hostname = socket.gethostname()
        self.device_vendor = "Osprey"
        self.device_product = "Immigration Platform"
        self.device_version = os.environ.get("SENTRY_RELEASE", "2.0.0")
        # Emoji removal regex
        self.emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"
            "\U0001f300-\U0001f5ff"
            "\U0001f680-\U0001f6ff"
            "\U0001f1e0-\U0001f1ff"
            "\U00002702-\U000027b0"
            "\U000024c2-\U0001f251"
            "\u2600-\u26ff"
            "\u2700-\u27bf"
            "]+",
            flags=re.UNICODE,
        )

    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text"""
        return self.emoji_pattern.sub("", text).strip()

    def _escape_cef(self, value: str) -> str:
        """Escape special characters for CEF format"""
        if not isinstance(value, str):
            value = str(value)
        # Escape pipe, backslash, equals, newline, carriage return
        value = value.replace("\\", "\\\\")
        value = value.replace("|", "\\|")
        value = value.replace("=", "\\=")
        value = value.replace("\n", "\\n")
        value = value.replace("\r", "\\r")
        return value

    def format(self, record: logging.LogRecord) -> str:
        # Clean message
        clean_message = self._remove_emojis(record.getMessage())

        # CEF severity (0-10 scale)
        severity = self._get_cef_severity(record.levelname)

        # Signature ID (logger name + level)
        signature_id = f"{record.name}:{record.levelname}"

        # Name (short description)
        name = clean_message[:50] if len(clean_message) > 50 else clean_message

        # Build CEF header
        cef_header = f"CEF:0|{self.device_vendor}|{self.device_product}|{self.device_version}|{signature_id}|{self._escape_cef(name)}|{severity}"

        # Build CEF extensions
        extensions = []
        extensions.append(f"msg={self._escape_cef(clean_message)}")
        extensions.append(f"shost={self.hostname}")
        extensions.append(f"src={self.hostname}")
        extensions.append(f"dvchost={self.hostname}")
        extensions.append(f"fname={record.filename}")
        extensions.append(f"fline={record.lineno}")
        extensions.append(f"sproc={record.processName}")
        extensions.append(f"spid={record.process}")

        # Add custom fields
        if hasattr(record, "user_id"):
            extensions.append(f"suser={self._escape_cef(record.user_id)}")
        if hasattr(record, "case_id"):
            extensions.append(f"cs1={self._escape_cef(record.case_id)}")
            extensions.append(f"cs1Label=CaseID")
        if hasattr(record, "request_id"):
            extensions.append(f"cs2={self._escape_cef(record.request_id)}")
            extensions.append(f"cs2Label=RequestID")

        # Add environment
        environment = os.environ.get("SENTRY_ENVIRONMENT", "development")
        extensions.append(f"cs3={environment}")
        extensions.append(f"cs3Label=Environment")

        # Exception information
        if record.exc_info:
            exc_type = record.exc_info[0].__name__ if record.exc_info[0] else "Unknown"
            exc_msg = str(record.exc_info[1]) if record.exc_info[1] else ""
            extensions.append(f"cs4={self._escape_cef(exc_type)}")
            extensions.append(f"cs4Label=ExceptionType")
            extensions.append(f"cs5={self._escape_cef(exc_msg)}")
            extensions.append(f"cs5Label=ExceptionMessage")

        # Combine header and extensions
        return f"{cef_header}|{' '.join(extensions)}"

    def _get_cef_severity(self, level_name: str) -> int:
        """Convert log level to CEF severity (0-10)"""
        severity_map = {
            "DEBUG": 1,
            "INFO": 3,
            "WARNING": 6,
            "ERROR": 8,
            "CRITICAL": 10,
        }
        return severity_map.get(level_name, 5)


class PlainTextFormatter(logging.Formatter):
    """Human-friendly single-line logs for development with emojis."""

    def __init__(self, pretty: bool = False):
        super().__init__()
        self.pretty = pretty

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        message = record.getMessage()

        # Add emoji prefix based on level if not already present
        message = self._ensure_emoji(message, record.levelname)

        if self.pretty:
            # Pretty format: clean output with emojis (development)
            return f"{timestamp} [{record.levelname}] {message}"
        else:
            # Non-pretty: include logger name for debugging
            return f"{timestamp} [{record.levelname}] {record.name}: {message}"

    def _ensure_emoji(self, message: str, level: str) -> str:
        """Ensure message has appropriate emoji prefix"""
        # Check if message already has an emoji
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"
            "\U0001f300-\U0001f5ff"
            "\U0001f680-\U0001f6ff"
            "\U0001f1e0-\U0001f1ff"
            "\U00002702-\U000027b0"
            "\U000024c2-\U0001f251"
            "\u2600-\u26ff"
            "\u2700-\u27bf"
            "]+",
            flags=re.UNICODE,
        )

        if emoji_pattern.match(message):
            return message  # Already has emoji

        # Add emoji based on level
        emoji_map = {
            "DEBUG": "🔍",
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🚨",
        }

        emoji = emoji_map.get(level, "ℹ️")
        return f"{emoji} {message}"


class ContextFilter(logging.Filter):
    """Add service context to all log records for distributed tracing."""

    def filter(self, record: logging.LogRecord) -> bool:
        # Add service metadata to every log record
        record.service = os.environ.get("SENTRY_SERVICE_NAME", "osprey-backend")
        record.environment = os.environ.get("SENTRY_ENVIRONMENT", "development")
        record.release = os.environ.get("SENTRY_RELEASE")
        return True


def setup_logging() -> logging.Logger:
    """
    Setup logging based on environment variables.

    Environment Variables:
        LOG_LEVEL: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
        LOG_FORMAT: plain, json, or cef (default: plain for dev, json for prod)
            - plain: Human-readable format with emojis for development
            - json: Structured JSON for SIEM integration (ECS-compliant, no emojis)
            - cef: Common Event Format for security tools (ArcSight, Splunk ES, Azure Sentinel)
        LOG_PRETTY: true/false (default: false)
            - For json: pretty-printed JSON with indentation
            - For plain: simplified format without logger names
            - For cef: ignored (CEF is always single-line)

    Format Recommendations:
        Development:
            LOG_FORMAT=plain, LOG_PRETTY=true
            Clean, readable logs with emojis

        Production (Application Logs):
            LOG_FORMAT=json, LOG_PRETTY=false
            Structured logs for: Datadog, ELK Stack, Splunk, CloudWatch, Azure Monitor

        Production (Security Logs):
            LOG_FORMAT=cef, LOG_PRETTY=false
            Security event logs for: ArcSight, Splunk ES, Azure Sentinel, QRadar
    """
    handler = logging.StreamHandler(sys.stdout)

    # Parse environment variables
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_format = os.environ.get("LOG_FORMAT", "plain").lower()
    pretty_logs = os.environ.get("LOG_PRETTY", "false").lower() in {"1", "true", "yes", "on"}

    # Set formatter based on format type
    if log_format == "cef":
        handler.setFormatter(CEFFormatter())
    elif log_format == "json":
        handler.setFormatter(JSONFormatter(pretty=pretty_logs))
    else:  # plain (default for development)
        handler.setFormatter(PlainTextFormatter(pretty=pretty_logs))

    # Configure root logger
    logging.basicConfig(
        level=log_level, handlers=[handler], force=True  # Override any existing configuration
    )

    root_logger = logging.getLogger()
    root_logger.addFilter(ContextFilter())

    return logging.getLogger(__name__)
