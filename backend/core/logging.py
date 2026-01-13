import json
import logging
import os
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def __init__(self, pretty: bool = False):
        super().__init__()
        self.pretty = pretty

    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "case_id"):
            log_data["case_id"] = record.case_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "service"):
            log_data["service"] = record.service
        if hasattr(record, "environment"):
            log_data["environment"] = record.environment
        if hasattr(record, "release") and record.release:
            log_data["release"] = record.release

        if self.pretty:
            return json.dumps(log_data, ensure_ascii=False, indent=2)
        return json.dumps(log_data, ensure_ascii=False)


class PlainTextFormatter(logging.Formatter):
    """Human-friendly single-line logs."""

    def format(self, record):
        timestamp = datetime.now(timezone.utc).isoformat()
        message = record.getMessage()
        return f"{timestamp} [{record.levelname}] {record.name}: {message}"


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.service = os.environ.get("SENTRY_SERVICE_NAME", "backend")
        record.environment = os.environ.get("SENTRY_ENVIRONMENT", "development")
        record.release = os.environ.get("SENTRY_RELEASE")
        return True


def setup_logging() -> logging.Logger:
    handler = logging.StreamHandler(sys.stdout)
    pretty_logs = os.environ.get("LOG_PRETTY", "false").lower() in {"1", "true", "yes", "on"}
    log_format = os.environ.get("LOG_FORMAT", "json").lower()

    if log_format == "plain":
        handler.setFormatter(PlainTextFormatter())
    else:
        handler.setFormatter(JSONFormatter(pretty=pretty_logs))

    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        handlers=[handler],
    )

    root_logger = logging.getLogger()
    root_logger.addFilter(ContextFilter())

    return logging.getLogger(__name__)
