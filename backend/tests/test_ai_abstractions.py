"""Unit tests for AI Provider abstractions (EmbeddingProvider and LLMProvider)."""

import pytest
from backend.app.knowledge.embeddings.base import EmbeddingProvider
from backend.app.knowledge.embeddings.local import LocalEmbeddingProvider
from backend.app.knowledge.embeddings import get_embedding_provider
from backend.app.intelligence.llm.base import LLMProvider, LLMResponse
from backend.app.intelligence.llm.gemini import GeminiLLMProvider
from backend.app.intelligence.llm import get_llm_provider
from backend.app.core.errors import AIProviderError


def test_embedding_provider_interface():
    """Verify LocalEmbeddingProvider adheres to EmbeddingProvider abstract contract."""
    provider = get_embedding_provider()
    assert isinstance(provider, EmbeddingProvider)
    assert provider.dimension == 384
    assert isinstance(provider.model_name, str)

    # Test single embedding
    vec = provider.embed_text("Forest soil biodiversity in tropical ecosystems")
    assert isinstance(vec, list)
    assert len(vec) == 384
    # Check normalized
    norm = sum(x * x for x in vec)
    assert 0.99 <= norm <= 1.01

    # Test batch embedding
    batch = provider.embed_batch(["Soil moisture", "Species richness"])
    assert len(batch) == 2
    assert len(batch[0]) == 384
    assert len(batch[1]) == 384


def test_llm_provider_interface():
    """Verify GeminiLLMProvider adheres to LLMProvider abstract contract."""
    provider = get_llm_provider()
    assert isinstance(provider, LLMProvider)
    assert provider.provider_name == "gemini"
    assert provider.default_model == "gemini-2.5-flash"


def test_llm_provider_error_when_key_missing():
    """Verify Gemini provider raises AIProviderError with clear message if API key missing."""
    provider = GeminiLLMProvider(api_key="")
    with pytest.raises(AIProviderError) as exc_info:
        provider.generate(prompt="Test prompt")
    assert "GEMINI_API_KEY is not configured" in str(exc_info.value)
