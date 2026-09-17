# System Architecture: Hybrid Layered RAG

VASUDHA — Biodiversity Intelligence implements a decoupled, five-tier architecture designed for scientific rigor, extensibility, and maintainability.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   1. PRESENTATION LAYER (React / TS)                   │
│   • Conversational UI with state persistence across turns             │
│   • Multi-metric environmental state inspector                        │
│   • Geographic context & interactive map grounding                    │
│   • "Why this intervention?" explainability chain visualization        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / JSON API (:3000 -> :8001)
┌───────────────────────────────────▼────────────────────────────────────┐
│                  2. APPLICATION / API LAYER (FastAPI)                  │
│   • FastAPI routers (/api/v1/health, /api/v1/intelligence)             │
│   • Strict Pydantic v2 schemas and validation                          │
│   • Centralized domain exception handlers and structured logging       │
│   • Decoupled provider dependency injection                            │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
┌───────────────────▼────────────────────────────┐   │
│         3. INTELLIGENCE LAYER (Python)         │   │
│   • Environmental state manager                │   │
│   • Multi-metric ecological reasoner (≥3 vars) │   │
│   • Nature risk profiler & intervention engine │   │
│   • Scientific claim validator (anti-hallucin.)│   │
│   • Abstracted LLM provider (Gemini / others)  │   │
└───────────────────┬────────────────────────────┘   │
                    │                                │
┌───────────────────▼────────────────────────────▼───▼───────────────────┐
│                   4. KNOWLEDGE LAYER (Python)                          │
│   • Scientific evidence store (IPCC, IPBES, FAO, UNEP, CBD)           │
│   • Structured ecological rules and relationships                      │
│   • Abstracted embedding provider (Local all-MiniLM-L6-v2)             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    5. DATA LAYER (PostgreSQL + pgvector)               │
│   • High-dimensional vector similarity search                          │
│   • Structured ecological baseline tables                              │
│   • SQLAlchemy 2.0 ORM + Alembic schema migrations                    │
│   • SQLite memory fallback for lightweight unit testing               │
└────────────────────────────────────────────────────────────────────────┘
```

## Architectural Layers

### 1. Presentation Layer (`src/`)
- Built with React 19, TypeScript, and Tailwind CSS.
- Communicates exclusively through the typed API client (`src/services/api.ts`).
- Uses Vite proxy during development to route `/api/*` requests to FastAPI on `:8001`.

### 2. Application Layer (`backend/app/api/`)
- FastAPI application entry point in `backend/app/main.py`.
- Sub-routers versioned under `backend/app/api/v1/`.
- Pydantic Settings (`backend/app/core/config.py`) managing all configuration from environment variables.
- Domain error handlers (`backend/app/core/errors.py`) transforming internal exceptions to standard error payloads.

### 3. Intelligence Layer (`backend/app/intelligence/`)
- Contains the ecological reasoning logic, intervention engine, and claim validation rules.
- Decoupled from LLM vendors via `LLMProvider` (`backend/app/intelligence/llm/base.py`).
- Default `GeminiLLMProvider` configured through dependency injection.

### 4. Knowledge Layer (`backend/app/knowledge/`)
- Houses peer-reviewed scientific citations and ecological mechanism definitions.
- Decoupled from vector embedding providers via `EmbeddingProvider` (`backend/app/knowledge/embeddings/base.py`).
- Default `LocalEmbeddingProvider` using normalized 384-dimensional vectors.

### 5. Data Layer (`backend/app/db/` & `backend/app/models/`)
- PostgreSQL 16 with the `pgvector` extension for semantic search over scientific abstracts.
- SQLAlchemy 2.0 declarative models with `TimestampMixin`.
- Alembic database migration environment (`backend/alembic/`).
