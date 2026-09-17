"""Reranker provider package and factory (Phase 8)."""

from typing import Optional
from backend.app.core.config import get_settings
from backend.app.knowledge.reranking.base import RerankResult, RerankerProvider
from backend.app.knowledge.reranking.local import LocalCrossEncoderReranker

_reranker_instance: Optional[RerankerProvider] = None


def get_reranker_provider() -> RerankerProvider:
    """Factory to retrieve configured singleton reranker provider instance."""
    global _reranker_instance
    if _reranker_instance is not None:
        return _reranker_instance

    settings = get_settings()
    _reranker_instance = LocalCrossEncoderReranker(
        model_name=settings.RERANKER_MODEL,
        enabled=settings.RERANKING_ENABLED,
        device=settings.EMBEDDING_DEVICE,
    )
    return _reranker_instance


def set_reranker_provider(provider: Optional[RerankerProvider]) -> None:
    """Explicitly set or override the active reranker provider (e.g. for testing)."""
    global _reranker_instance
    _reranker_instance = provider


def reset_reranker_provider() -> None:
    """Reset the cached singleton instance."""
    global _reranker_instance
    _reranker_instance = None


__all__ = [
    "RerankResult",
    "RerankerProvider",
    "LocalCrossEncoderReranker",
    "get_reranker_provider",
    "set_reranker_provider",
    "reset_reranker_provider",
]
