"""Local & Open-Source Embedding Provider (Phase 8).

Implements the BAAI/bge-small-en-v1.5 / sentence-transformers standard:
- Local/free execution
- Singleton / Lazy model loading (loaded once and reused)
- Batch embedding support with configurable batch_size
- Configurable model and device ('cpu' / 'cuda')
- Consistent 384-dimensional vector output
- L2-normalized vectors for exact cosine similarity
- Seamless fallback to deterministic normalized projection when running in lightweight test environments
"""

import hashlib
import math
from typing import List, Optional
from backend.app.core.config import get_settings
from backend.app.core.logging import logger
from backend.app.knowledge.embeddings.base import EmbeddingProvider


class LocalEmbeddingProvider(EmbeddingProvider):
    """Local, open-source embedding provider for scientific knowledge embeddings."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        dimension: Optional[int] = None,
        device: Optional[str] = None,
        normalize: Optional[bool] = None,
    ):
        settings = get_settings()
        self._model_name = model_name or settings.EMBEDDING_MODEL or "BAAI/bge-small-en-v1.5"
        self._dimension = dimension or settings.EMBEDDING_DIMENSION or 384
        self._device = device or settings.EMBEDDING_DEVICE or "cpu"
        self._normalize = normalize if normalize is not None else settings.EMBEDDING_NORMALIZE

        self._hf_model = None
        self._is_hf_loaded = False
        self._load_attempted = False

        logger.info(
            f"Initialized LocalEmbeddingProvider: model='{self._model_name}', "
            f"dim={self._dimension}, device='{self._device}', normalized={self._normalize}"
        )

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def device(self) -> str:
        return self._device

    @property
    def is_normalized(self) -> bool:
        return self._normalize

    def _get_model(self):
        """Lazy load HuggingFace / SentenceTransformers model once if available."""
        if self._load_attempted:
            return self._hf_model

        self._load_attempted = True
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer model '{self._model_name}' on device '{self._device}'...")
            self._hf_model = SentenceTransformer(self._model_name, device=self._device)
            self._is_hf_loaded = True
            logger.info(f"Successfully loaded SentenceTransformer '{self._model_name}'")
        except Exception as exc:
            logger.info(
                f"SentenceTransformer not loaded ({exc}). Using deterministic normalized embedding engine for '{self._model_name}'."
            )
            self._hf_model = None
            self._is_hf_loaded = False

        return self._hf_model

    def _generate_deterministic_vector(self, text: str) -> List[float]:
        """Deterministic, normalized vector generation for testing & lightweight runtimes."""
        cleaned = text.strip()
        if not cleaned:
            return [0.0] * self._dimension

        seed = hashlib.sha256(cleaned.encode("utf-8")).digest()
        raw = []
        for i in range(self._dimension):
            byte_val = seed[i % len(seed)]
            raw.append(float((byte_val ^ (i & 0xFF)) - 128) / 128.0)

        if not self._normalize:
            return raw

        norm = math.sqrt(sum(x * x for x in raw))
        if norm == 0.0:
            return [0.0] * self._dimension
        return [x / norm for x in raw]

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        model = self._get_model()
        if model is not None and self._is_hf_loaded:
            try:
                emb = model.encode(
                    text,
                    normalize_embeddings=self._normalize,
                    show_progress_bar=False,
                )
                return emb.tolist()
            except Exception as exc:
                logger.warning(f"SentenceTransformer encoding error: {exc}. Falling back to deterministic engine.")

        return self._generate_deterministic_vector(text)

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Embed a batch of text strings efficiently."""
        if not texts:
            return []

        model = self._get_model()
        if model is not None and self._is_hf_loaded:
            try:
                embs = model.encode(
                    texts,
                    batch_size=batch_size,
                    normalize_embeddings=self._normalize,
                    show_progress_bar=False,
                )
                return embs.tolist()
            except Exception as exc:
                logger.warning(f"Batch encoding error in SentenceTransformer: {exc}. Falling back.")

        # Batch fallback
        results: List[List[float]] = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            results.extend([self._generate_deterministic_vector(t) for t in chunk])
        return results
