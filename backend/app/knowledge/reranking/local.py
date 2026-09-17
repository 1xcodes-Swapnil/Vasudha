"""Local Cross-Encoder & Fallback Reranker Provider (Phase 8).

Implements BAAI/bge-reranker-small / cross-encoder abstraction:
- Optional & configurable (enabled/disabled via settings)
- Lazy model loading (loaded once and reused)
- Graceful fallback: If disabled or uninstalled, preserves candidate vector ranks seamlessly
- Normalizes scores into standard [0.0, 1.0] range
"""

import math
import re
from typing import Any, Dict, List, Optional
from backend.app.core.config import get_settings
from backend.app.core.logging import logger
from backend.app.knowledge.reranking.base import RerankResult, RerankerProvider


class LocalCrossEncoderReranker(RerankerProvider):
    """Local Cross-Encoder reranker provider with graceful fallback."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        enabled: Optional[bool] = None,
        device: Optional[str] = None,
    ):
        settings = get_settings()
        self._model_name = model_name or settings.RERANKER_MODEL or "BAAI/bge-reranker-small"
        self._enabled = enabled if enabled is not None else settings.RERANKING_ENABLED
        self._device = device or settings.EMBEDDING_DEVICE or "cpu"

        self._cross_encoder = None
        self._is_loaded = False
        self._load_attempted = False

        logger.info(
            f"Initialized LocalCrossEncoderReranker: model='{self._model_name}', "
            f"enabled={self._enabled}, device='{self._device}'"
        )

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def _get_model(self):
        """Lazy load CrossEncoder model once if enabled and available."""
        if not self._enabled:
            return None

        if self._load_attempted:
            return self._cross_encoder

        self._load_attempted = True
        try:
            from sentence_transformers import CrossEncoder
            logger.info(f"Loading CrossEncoder '{self._model_name}' on device '{self._device}'...")
            self._cross_encoder = CrossEncoder(self._model_name, device=self._device)
            self._is_loaded = True
            logger.info(f"Successfully loaded CrossEncoder '{self._model_name}'")
        except Exception as exc:
            logger.info(
                f"CrossEncoder not loaded ({exc}). Using lightweight fallback scoring for '{self._model_name}'."
            )
            self._cross_encoder = None
            self._is_loaded = False

        return self._cross_encoder

    def _calculate_fallback_score(self, query: str, document: str) -> float:
        """Lightweight lexical + token overlap score for fallback reranking."""
        q_tokens = set(re.findall(r"\b\w{3,}\b", query.lower()))
        if not q_tokens:
            return 0.5

        d_lower = document.lower()
        d_tokens = set(re.findall(r"\b\w{3,}\b", d_lower))

        overlap = len(q_tokens.intersection(d_tokens))
        jaccard = overlap / len(q_tokens.union(d_tokens)) if q_tokens.union(d_tokens) else 0.0

        # Exact phrase bonus
        phrase_bonus = 0.2 if query.lower() in d_lower else 0.0

        raw_score = 0.5 * (overlap / len(q_tokens)) + 0.3 * jaccard + phrase_bonus
        return round(min(1.0, max(0.0, raw_score)), 4)

    def rerank(
        self,
        query: str,
        documents: List[str],
        top_n: Optional[int] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[RerankResult]:
        """Rerank candidates against query."""
        if not documents:
            return []

        if metadatas is None or len(metadatas) != len(documents):
            metadatas = [{} for _ in documents]

        # If reranking is disabled, preserve original vector rank order
        if not self._enabled:
            results = [
                RerankResult(
                    index=i,
                    score=round(1.0 - (i * 0.05), 4),
                    document=doc,
                    metadata=metadatas[i],
                )
                for i, doc in enumerate(documents)
            ]
            if top_n is not None:
                results = results[:top_n]
            return results

        model = self._get_model()

        # Try cross-encoder inference if loaded
        if model is not None and self._is_loaded:
            try:
                pairs = [[query, doc] for doc in documents]
                scores = model.predict(pairs)
                # Convert logits to probabilities via sigmoid if raw logits
                results = []
                for i, (doc, meta, score) in enumerate(zip(documents, metadatas, scores)):
                    s = float(score)
                    # Apply sigmoid if unbounded logits
                    prob = 1.0 / (1.0 + math.exp(-s)) if (s < -2.0 or s > 2.0) else (s + 2.0) / 4.0
                    normalized_score = round(min(1.0, max(0.0, prob)), 4)
                    results.append(
                        RerankResult(
                            index=i,
                            score=normalized_score,
                            document=doc,
                            metadata=meta,
                        )
                    )
                results.sort(key=lambda r: r.score, reverse=True)
                if top_n is not None:
                    results = results[:top_n]
                return results
            except Exception as exc:
                logger.warning(f"CrossEncoder inference failed ({exc}). Falling back to algorithmic reranker.")

        # Algorithmic fallback
        fallback_results = []
        for i, (doc, meta) in enumerate(zip(documents, metadatas)):
            score = self._calculate_fallback_score(query, doc)
            fallback_results.append(
                RerankResult(
                    index=i,
                    score=score,
                    document=doc,
                    metadata=meta,
                )
            )

        fallback_results.sort(key=lambda r: r.score, reverse=True)
        if top_n is not None:
            fallback_results = fallback_results[:top_n]
        return fallback_results
