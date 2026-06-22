from datetime import UTC, datetime
import json
import logging
import sys
from typing import Any


RESERVED_LOG_RECORD_KEYS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}

SENSITIVE_LOG_KEYS = {
    "authorization",
    "cookie",
    "password",
    "session_token",
    "token",
}


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key in RESERVED_LOG_RECORD_KEYS:
                continue
            payload[key] = _redact_if_sensitive(key, value)

        if record.exc_info:
            payload["error_category"] = payload.get("error_category", record.exc_info[0].__name__)

        return json.dumps(payload, default=str, separators=(",", ":"))


def configure_logging(log_level: str) -> None:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    root_logger.addHandler(handler)


def _redact_if_sensitive(key: str, value: Any) -> Any:
    if key.lower() in SENSITIVE_LOG_KEYS:
        return "[REDACTED]"
    return value
