"""Unit and evaluation tests for Phase 8 Model Infrastructure Layer:
1. EmbeddingProvider (BAAI/bge-small-en-v1.5, vector dims, batch processing, L2-normalization, determinism)
2. RerankerProvider (Optional cross-encoder, scoring, fallback behavior, top_n)
3. LLMProvider (Gemini, Local/Mock, error handling, prompt guardrails, async execution)
4. RAG integration with embedding + reranking
"""

import math
import pytest
from backend.app.core.config import Settings
from backend.app.core.errors import AIProviderError
from backend.app.knowledge.embeddings.base import EmbeddingProvider
from backend.app.knowledge.embeddings.local import LocalEmbeddingProvider
from backend.app.knowledge.embeddings import (
    get_embedding_provider,
    set_embedding_provider,
    reset_embedding_provider,
)
from backend.app.knowledge.reranking.base import RerankResult, RerankerProvider
from backend.app.knowledge.reranking.local import LocalCrossEncoderReranker
from backend.app.knowledge.reranking import (
    get_reranker_provider,
    set_reranker_provider,
    reset_reranker_provider,
)
from backend.app.intelligence.llm.base import LLMProvider, LLMResponse
from backend.app.intelligence.llm.gemini import GeminiLLMProvider
from backend.app.intelligence.llm.local import LocalLLMProvider
from backend.app.intelligence.llm import (
    get_llm_provider,
    set_llm_provider,
    reset_llm_provider,
)
from backend.app.knowledge.rag_service import ScientificRAGService
from backend.app.schemas.scientific_rag import ScientificSearchQuery


class TestEmbeddingInfrastructure:
    """Evaluation tests for embedding generation and vector contracts."""

    def setup_method(self):
        reset_embedding_provider()

    def teardown_method(self):
        reset_embedding_provider()

    def test_default_embedding_provider_configuration(self):
        provider = get_embedding_provider()
        assert isinstance(provider, EmbeddingProvider)
        assert provider.model_name in ("BAAI/bge-small-en-v1.5", "sentence-transformers/all-MiniLM-L6-v2")
        assert provider.dimension == 384
        assert provider.device == "cpu"
        assert provider.is_normalized is True

    def test_embedding_vector_dimensions_and_normalization(self):
        provider = LocalEmbeddingProvider(model_name="BAAI/bge-small-en-v1.5", dimension=384, normalize=True)
        text = "Soil organic carbon sequestration dynamics in temperate agroforestry systems"
        vec = provider.embed_text(text)

        assert isinstance(vec, list)
        assert len(vec) == 384
        assert all(isinstance(x, float) for x in vec)

        # Verify unit L2 norm
        norm = math.sqrt(sum(x * x for x in vec))
        assert 0.99 <= norm <= 1.01

    def test_batch_embedding_processing(self):
        provider = LocalEmbeddingProvider(dimension=384)
        texts = [
            "Tropical rainforest canopy structure",
            "Arid grassland species richness",
            "Mangrove blue carbon stock",
            "Boreal peatland methane flux",
        ]
        batch_vecs = provider.embed_batch(texts, batch_size=2)
        assert len(batch_vecs) == 4
        for vec in batch_vecs:
            assert len(vec) == 384
            norm = math.sqrt(sum(x * x for x in vec))
            assert 0.99 <= norm <= 1.01

    def test_empty_and_whitespace_handling(self):
        provider = LocalEmbeddingProvider(dimension=384)
        empty_vec = provider.embed_text("")
        assert len(empty_vec) == 384
        assert all(x == 0.0 for x in empty_vec)

        batch_empty = provider.embed_batch([])
        assert batch_empty == []

    def test_deterministic_embedding_consistency(self):
        provider = LocalEmbeddingProvider(dimension=384)
        text = "Soil pH buffering capacity"
        vec1 = provider.embed_text(text)
        vec2 = provider.embed_text(text)
        assert vec1 == vec2


class TestRerankerInfrastructure:
    """Evaluation tests for optional cross-encoder reranking and graceful fallbacks."""

    def setup_method(self):
        reset_reranker_provider()

    def teardown_method(self):
        reset_reranker_provider()

    def test_reranker_disabled_behavior(self):
        """When reranking is disabled, candidate orders are preserved gracefully."""
        reranker = LocalCrossEncoderReranker(enabled=False)
        assert reranker.is_enabled is False

        query = "soil water retention"
        docs = [
            "Biochar application increases soil water holding capacity by 15-25%.",
            "Nitrogen fertilizers may accelerate soil acidification in tropical oxisols.",
            "Riparian buffer strips reduce pesticide runoff into aquatic streams.",
        ]
        results = reranker.rerank(query, docs, top_n=2)
        assert len(results) == 2
        assert results[0].index == 0
        assert results[1].index == 1
        assert results[0].document == docs[0]

    def test_reranker_enabled_fallback_scoring(self):
        """When enabled without neural cross-encoder, uses algorithmic keyword-semantic alignment."""
        reranker = LocalCrossEncoderReranker(enabled=True)
        query = "soil water retention capacity"
        docs = [
            "Riparian tree planting buffers wind speed in open agricultural fields.",
            "Organic mulch improves soil water retention capacity significantly in semi-arid zones.",
            "Urban concrete surfaces create local heat island effects.",
        ]
        results = reranker.rerank(query, docs, top_n=3)
        assert len(results) == 3
        # Most relevant document should be ranked first
        assert results[0].index == 1
        assert "Organic mulch improves soil water retention" in results[0].document
        assert results[0].score > results[1].score

    def test_empty_document_list_reranking(self):
        reranker = LocalCrossEncoderReranker(enabled=True)
        results = reranker.rerank("any query", [])
        assert results == []


class TestLLMInfrastructure:
    """Evaluation tests for LLM provider abstractions, guardrails, and mock execution."""

    def setup_method(self):
        reset_llm_provider()

    def teardown_method(self):
        reset_llm_provider()

    def test_gemini_provider_interface(self):
        provider = GeminiLLMProvider(api_key="test_key", model="gemini-2.5-flash")
        assert provider.provider_name == "gemini"
        assert provider.default_model == "gemini-2.5-flash"

    def test_gemini_provider_unconfigured_error(self):
        provider = GeminiLLMProvider(api_key="")
        with pytest.raises(AIProviderError) as exc_info:
            provider.generate(prompt="Explain soil carbon")
        assert "GEMINI_API_KEY is not configured" in str(exc_info.value)

    def test_local_mock_llm_provider_execution(self):
        provider = LocalLLMProvider(model="test-mock-v1")
        assert provider.provider_name == "local"
        assert provider.default_model == "test-mock-v1"

        prompt = "Synthesize evidence for agroforestry in drylands."
        response = provider.generate(prompt=prompt)
        assert isinstance(response, LLMResponse)
        assert response.provider_name == "local"
        assert response.model_name == "test-mock-v1"
        assert len(response.content) > 20
        assert response.prompt_tokens > 0

    @pytest.mark.anyio
    async def test_local_mock_llm_async_execution(self):
        provider = LocalLLMProvider()
        response = await provider.generate_async(prompt="Async explanation test")
        assert isinstance(response, LLMResponse)
        assert response.provider_name == "local"


class TestRAGModelIntegration:
    """Evaluation tests verifying RAG pipeline with updated Embedding and Reranker providers."""

    def test_rag_retrieval_with_reranking_enabled(self):
        embedding_provider = LocalEmbeddingProvider(dimension=384)
        reranker_provider = LocalCrossEncoderReranker(enabled=True)
        rag_service = ScientificRAGService(
            embedding_provider=embedding_provider,
            reranker_provider=reranker_provider,
        )

        query = ScientificSearchQuery(
            query="tropical deforestation and forest fragmentation impact on species richness",
            ecosystem="tropical_forest",
            top_k=5,
        )
        packet = rag_service.search_evidence(query)
        assert packet.total_found > 0
        assert packet.selected_count <= 5
        assert packet.insufficient_evidence is False
        assert len(packet.evidence_chunks) > 0
        # Ensure highest-ranked chunks have positive relevance score
        assert packet.evidence_chunks[0].relevance_score > 0.0
