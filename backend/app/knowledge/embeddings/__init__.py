"""Embedding provider package and factory (Phase 8)."""

from typing import Optional
from backend.app.core.config import get_settings
from backend.app.knowledge.embeddings.base import EmbeddingProvider
from backend.app.knowledge.embeddings.local import LocalEmbeddingProvider

_provider_instance: Optional[EmbeddingProvider] = None


def get_embedding_provider() -> EmbeddingProvider:
    """Factory to retrieve configured singleton embedding provider instance."""
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    settings = get_settings()
    provider_type = settings.DEFAULT_EMBEDDING_PROVIDER.lower()

    if provider_type in ("local", "free", "bge", "sentence_transformers"):
        _provider_instance = LocalEmbeddingProvider(
            model_name=settings.EMBEDDING_MODEL,
            dimension=settings.EMBEDDING_DIMENSION,
            device=settings.EMBEDDING_DEVICE,
            normalize=settings.EMBEDDING_NORMALIZE,
        )
    else:
        # Default fallback to LocalEmbeddingProvider
        _provider_instance = LocalEmbeddingProvider()

    return _provider_instance


def set_embedding_provider(provider: Optional[EmbeddingProvider]) -> None:
    """Explicitly set or override the active embedding provider (e.g. for testing)."""
    global _provider_instance
    _provider_instance = provider


def reset_embedding_provider() -> None:
    """Reset the cached singleton instance."""
    global _provider_instance
    _provider_instance = None


__all__ = [
    "EmbeddingProvider",
    "LocalEmbeddingProvider",
    "get_embedding_provider",
    "set_embedding_provider",
    "reset_embedding_provider",
]

