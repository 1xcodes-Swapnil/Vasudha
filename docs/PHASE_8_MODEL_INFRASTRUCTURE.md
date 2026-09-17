# Phase 8: Modular Model Infrastructure Layer

## 1. Overview & Architecture

Phase 8 creates a modular, clean, provider-agnostic model infrastructure layer for **Darukaa.Earth Biodiversity Intelligence**:
1. **Embedding Layer**: Local/free model execution (`BAAI/bge-small-en-v1.5`, 384-dimension vector standard), singleton reuse, batching, L2-normalization for cosine distance compatibility, and deterministic fallback.
2. **Reranker Layer**: Optional cross-encoder reranking (`BAAI/bge-reranker-small`), configurable via settings, with graceful fallback to vector retrieval ordering.
3. **LLM Interaction Layer**: Strict decoupling interface (`LLMProvider`) with Google Gemini as primary provider and local deterministic mock for testing and offline environments.
4. **Strict Grounding Boundary**: The LLM acts purely as a natural language synthesis and clarification interface, and is **NEVER** treated as the scientific source of truth, calculation engine, or citation generator.

```
                  ┌────────────────────────────────────────┐
                  │          Settings Configuration         │
                  │  EMBEDDING_MODEL, RERANKER_MODEL, LLM   │
                  └───────────────────┬────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
 ┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
 │  EmbeddingProvider   │   │   RerankerProvider   │   │     LLMProvider      │
 ├──────────────────────┤   ├──────────────────────┤   ├──────────────────────┤
 │ • BAAI/bge-small-v1.5│   │ • BAAI/bge-reranker  │   │ • GeminiLLMProvider  │
 │ • 384-dimensional    │   │ • Configurable on/off│   │ • LocalLLMProvider   │
 │ • L2-Normalized      │   │ • CrossEncoder /     │   │ • Strict Grounding   │
 │ • Single & Batch     │   │   Fallback Scoring   │   │   Guardrails         │
 │ • Lazy Singleton     │   │ • Graceful Fallback  │   │ • Decoupled Vendor   │
 └──────────┬───────────┘   └──────────┬───────────┘   └──────────────────────┘
            │                          │
            └────────────┬─────────────┘
                         ▼
        ┌──────────────────────────────────┐
        │       ScientificRAGService       │
        │  Two-Stage Retrieval + Reranking │
        └──────────────────────────────────┘
```

---

## 2. Models & Providers

| Component | Abstract Interface | Default Provider | Model Identifier | Properties |
| :--- | :--- | :--- | :--- | :--- |
| **Embeddings** | `EmbeddingProvider` | `LocalEmbeddingProvider` | `BAAI/bge-small-en-v1.5` | 384 dimensions, L2-normalized, batch chunking, CPU/CUDA |
| **Reranker** | `RerankerProvider` | `LocalCrossEncoderReranker` | `BAAI/bge-reranker-small` | Optional, normalized [0.0, 1.0], top_n truncation, fallback ranking |
| **LLM** | `LLMProvider` | `GeminiLLMProvider` / `LocalLLMProvider` | `gemini-2.5-flash` | Structured grounding prompt, temperature 0.2, max tokens 2048 |

---

## 3. Configuration & Environment Variables

```env
# AI Model Infrastructure (Phase 8)
DEFAULT_LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=2048

DEFAULT_EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSION=384
EMBEDDING_DEVICE=cpu
EMBEDDING_NORMALIZE=True

RERANKING_ENABLED=False
RERANKER_MODEL=BAAI/bge-reranker-small
RERANKER_TOP_N=5

GEMINI_API_KEY=
```

---

## 4. Reliability & Graceful Degradation Matrix

| Failure Mode | Detection | System Action | Result |
| :--- | :--- | :--- | :--- |
| **Embedding Unavailable** | Import / model failure | Falls back to deterministic normalized projection engine | Vector dimensions and unit norm preserved without runtime interruption |
| **Reranker Disabled / Unavailable** | `is_enabled=False` or model missing | Retains vector composite relevance score ranking | Retrieval proceeds smoothly without disruption |
| **LLM Key Missing** | `GEMINI_API_KEY` empty / unconfigured | Raises `AIProviderError` or falls back to structured reasoning | Prevents silent failure or hallucinated output |
| **Invalid Payload** | Out-of-bounds metrics / empty queries | Returns explicit `insufficient_evidence` flag and audit log | Scientific integrity preserved |

---

## 5. Test Suite & Evaluation

- **Total Backend Tests**: **113 passed** in 0.93s (`pytest backend/tests/`).
- **Tests Added in `backend/tests/test_model_infrastructure.py`**:
  - `test_default_embedding_provider_configuration`: Validates model defaults, dimensions (384), normalization flag, and CPU device.
  - `test_embedding_vector_dimensions_and_normalization`: Verifies 384 dimensions and unit L2 norm ($0.99 \le \|v\|_2 \le 1.01$).
  - `test_batch_embedding_processing`: Validates batch chunking, dimension consistency, and norm preservation across batches.
  - `test_empty_and_whitespace_handling`: Validates zero vector for empty inputs and empty array for empty batches.
  - `test_deterministic_embedding_consistency`: Confirms repeatable vector outputs for identical inputs.
  - `test_reranker_disabled_behavior`: Validates original vector order preservation when reranking is inactive.
  - `test_reranker_enabled_fallback_scoring`: Validates top candidate scoring and ranking based on query-document alignment.
  - `test_empty_document_list_reranking`: Graceful handling of empty input lists.
  - `test_gemini_provider_interface`: Validates Gemini provider attributes and model configuration.
  - `test_gemini_provider_unconfigured_error`: Verifies clear error when API key is missing.
  - `test_local_mock_llm_provider_execution`: Validates deterministic offline LLM generation and token metrics.
  - `test_local_mock_llm_async_execution`: Validates async generation support.
  - `test_rag_retrieval_with_reranking_enabled`: Validates end-to-end RAG retrieval pipeline with reranker integration.
