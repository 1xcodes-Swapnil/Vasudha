"""Logging foundation for the Biodiversity Intelligence platform with automated credential redaction."""

import logging
import re
import sys
from typing import Any
from backend.app.core.config import get_settings


class SecretRedactionFilter(logging.Filter):
    """Logging filter that redacts API keys, database passwords, and authorization tokens."""

    # Patterns matching sensitive data
    PATTERNS = [
        # PostgreSQL / MySQL connection strings with passwords: protocol://user:password@host
        (re.compile(r"([a-zA-Z0-9_+]+://[^:]+:)([^@\s]+)(@)", re.IGNORECASE), r"\1***\3"),
        # HTTP Bearer / Basic tokens
        (re.compile(r"(Bearer\s+)[A-Za-z0-9_\-\.]{8,}", re.IGNORECASE), r"\1[REDACTED_TOKEN]"),
        (re.compile(r"(Basic\s+)[A-Za-z0-9+/=]{8,}", re.IGNORECASE), r"\1[REDACTED_AUTH]"),
        # Google AI Studio / Cloud API keys (AIza...)
        (re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "[REDACTED_GOOGLE_API_KEY]"),
        # Key-value secret parameters (e.g., api_key=..., password=...)
        (re.compile(r"(?i)(api[_-]?key|client[_-]?secret|password|auth[_-]?token|secret[_-]?key)\s*([=:]\s*)['\"]?([^\s,'\"&;]+)['\"]?"), r"\1\2[REDACTED]"),
    ]

    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self._exact_secrets: list[str] = []
        try:
            settings = get_settings()
            if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 5:
                self._exact_secrets.append(settings.GEMINI_API_KEY.strip())
        except Exception:
            pass

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.redact(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self.redact(str(v)) if isinstance(v, str) else v for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self.redact(str(arg)) if isinstance(arg, str) else arg for arg in record.args)
        return True

    def redact(self, message: str) -> str:
        """Sanitize a text message by stripping sensitive credentials."""
        for pattern, replacement in self.PATTERNS:
            message = pattern.sub(replacement, message)
        for secret in self._exact_secrets:
            if secret in message:
                message = message.replace(secret, "[REDACTED_SECRET]")
        return message


def setup_logging() -> logging.Logger:
    """Configure and initialize structured application logging with security filters."""
    settings = get_settings()
    log_level = logging.DEBUG if settings.DEBUG or settings.ENVIRONMENT == "development" else logging.INFO

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.addFilter(SecretRedactionFilter())

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
        handlers=[stream_handler],
        force=True,
    )

    logger = logging.getLogger("vasudha.earth")
    logger.setLevel(log_level)
    return logger


logger = setup_logging()

