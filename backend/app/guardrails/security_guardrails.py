"""Security guardrails, sensitive information redaction, and error payload sanitization."""

import re
from typing import Any, Dict, List, Optional
from backend.app.guardrails.models import (
    GuardrailAction,
    GuardrailResult,
    GuardrailSeverity,
)


class SecurityGuardrails:
    """Ensures responses, logs, and error messages never expose credentials or internal infrastructure details."""

    SECRET_REGEXES = [
        # Google / Gemini API keys
        (re.compile(r"AIza[0-9A-Za-z\-_]{35}"), "[REDACTED_GOOGLE_API_KEY]"),
        # PostgreSQL / Database connection URI with passwords
        (re.compile(r"postgresql(?:\+[a-z0-9]+)?://([^:]+):([^@]+)@"), r"postgresql://\1:***@"),
        # Bearer tokens & JWTs
        (re.compile(r"Bearer\s+eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_.+/=]*", re.IGNORECASE), "Bearer [REDACTED_JWT]"),
        # Supabase API keys
        (re.compile(r"sbp_[a-zA-Z0-9]{30,}"), "[REDACTED_SUPABASE_TOKEN]"),
        # Private Keys
        (re.compile(r"-----BEGIN (?:RSA|EC|PGP|OPENSSH)? ?PRIVATE KEY-----[^-]+-----END [^-]+-----", re.DOTALL), "[REDACTED_PRIVATE_KEY]"),
    ]

    @classmethod
    def redact_secrets(cls, text: str) -> str:
        """Sanitize any sensitive credentials or tokens from string."""
        if not text:
            return ""
        sanitized = text
        for pattern, replacement in cls.SECRET_REGEXES:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized

    @classmethod
    def sanitize_error_payload(cls, exc: Exception) -> str:
        """Return safe, non-leaking user-facing error message from an exception."""
        raw_msg = str(exc)
        # Check if contains database credentials
        if "postgresql://" in raw_msg or "password" in raw_msg.lower() or "aiza" in raw_msg.lower():
            return "An internal data operation failed. Details have been logged securely."

        # Redact any stray tokens
        safe_msg = cls.redact_secrets(raw_msg)
        return safe_msg

    @classmethod
    def scan_outgoing_payload(cls, payload: Any) -> GuardrailResult:
        """Verify outgoing payload does not contain leaked environment credentials."""
        text_repr = str(payload)
        for pattern, _ in cls.SECRET_REGEXES:
            if pattern.search(text_repr):
                return GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.BLOCK,
                    code="SECURITY_CREDENTIAL_LEAK_IN_PAYLOAD",
                    message="Sensitive credential detected in outgoing response payload and blocked.",
                    details={},
                    action=GuardrailAction.BLOCK,
                )

        return GuardrailResult(
            passed=True,
            severity=GuardrailSeverity.INFO,
            code="SECURITY_PAYLOAD_SAFE",
            message="Payload verified free of credential leaks.",
            details={},
            action=GuardrailAction.ALLOW,
        )
