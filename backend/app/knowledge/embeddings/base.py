"""Abstract base class for all embedding providers (Phase 8)."""

from abc import ABC, abstractmethod
from typing import List, Optional


class EmbeddingProvider(ABC):
    """Abstract interface for text embedding generation."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the unique identifier or model name (e.g. 'BAAI/bge-small-en-v1.5')."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the vector embedding dimensionality (e.g. 384)."""
        pass

    @property
    def device(self) -> str:
        """Execution device ('cpu' or 'cuda')."""
        return "cpu"

    @property
    def is_normalized(self) -> bool:
        """Whether vectors are L2-normalized for cosine similarity."""
        return True

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate an embedding vector for a single string of text."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embedding vectors for a batch of text strings."""
        pass

