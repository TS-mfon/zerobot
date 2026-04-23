"""Structured JSON logging for production."""

import json
import logging
import os
import sys


class JsonFormatter(logging.Formatter):
    """Format log records as JSON lines."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "module": record.module,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging(level: str | None = None) -> None:
    """Configure root logger for structured output on stdout."""
    log_level = (level or os.environ.get("LOG_LEVEL", "INFO")).upper()

    root = logging.getLogger()
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    # Use JSON format in production; human-readable locally
    if os.environ.get("LOG_FORMAT", "").lower() == "json" or os.environ.get("RENDER"):
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)-7s %(module)s: %(message)s",
            datefmt="%H:%M:%S",
        ))

    root.setLevel(log_level)
    root.addHandler(handler)

    # Tame noisy libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext.Application").setLevel(logging.INFO)
