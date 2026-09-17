"""Abstract base class and schemas for Reranker providers (Phase 8)."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RerankResult(BaseModel):
    """Result item for a single document evaluated by a reranker."""

    index: int = Field(description="Original index in the input document list.")
    score: float = Field(description="Rerank relevance score (higher is more relevant).")
    document: str = Field(description="Document content.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Pass-through document metadata.")


class RerankerProvider(ABC):
    """Abstract interface for document reranking."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the unique identifier or model name (e.g. 'BAAI/bge-reranker-small')."""
        pass

    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """Whether reranking is active in the current environment."""
        pass

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: List[str],
        top_n: Optional[int] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[RerankResult]:
        """Rerank a list of candidate documents against a query string."""
        pass
