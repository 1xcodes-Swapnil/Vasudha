"""LLM provider package and factory (Phase 8)."""

from typing import Optional
from backend.app.core.config import get_settings
from backend.app.intelligence.llm.base import LLMProvider, LLMResponse
from backend.app.intelligence.llm.gemini import GeminiLLMProvider
from backend.app.intelligence.llm.local import LocalLLMProvider

_llm_instance: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    """Factory to retrieve configured singleton LLM provider instance."""
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    settings = get_settings()
    provider_name = settings.DEFAULT_LLM_PROVIDER.lower()

    if provider_name == "gemini":
        _llm_instance = GeminiLLMProvider(
            api_key=settings.GEMINI_API_KEY,
            model=settings.LLM_MODEL,
        )
    elif provider_name in ("local", "mock", "offline"):
        _llm_instance = LocalLLMProvider()
    else:
        _llm_instance = GeminiLLMProvider()

    return _llm_instance


def set_llm_provider(provider: Optional[LLMProvider]) -> None:
    """Explicitly set or override the active LLM provider (e.g. for testing)."""
    global _llm_instance
    _llm_instance = provider


def reset_llm_provider() -> None:
    """Reset the cached singleton instance."""
    global _llm_instance
    _llm_instance = None


__all__ = [
    "LLMProvider",
    "LLMResponse",
    "GeminiLLMProvider",
    "LocalLLMProvider",
    "get_llm_provider",
    "set_llm_provider",
    "reset_llm_provider",
]
