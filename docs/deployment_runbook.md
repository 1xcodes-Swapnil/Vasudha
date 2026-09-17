# Darukaa.Earth - Production Deployment & Operations Runbook

This runbook details the architecture configuration, environment variables, migration workflows, startup procedures, and troubleshooting steps for deploying Darukaa.Earth in production for live demonstrations.

---

## 1. Environment Configuration

Darukaa.Earth separates environment configurations using `.env` files and Pydantic Settings.

### Required Environment Variables (`.env`)

```env
# Runtime Environment ('development', 'testing', 'production')
ENVIRONMENT="production"
DEBUG=false

# Server Bindings
BACKEND_HOST="0.0.0.0"
BACKEND_PORT=8001

# PostgreSQL + pgvector Connection String (e.g., Supabase, Neon, or Cloud SQL)
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@YOUR_DB_HOST:5432/postgres"

# AI Model Credentials & Settings
DEFAULT_LLM_PROVIDER="gemini"
LLM_MODEL="gemini-2.5-flash"
GEMINI_API_KEY="your-gemini-api-key"

# Embedding & RAG Configuration
DEFAULT_EMBEDDING_PROVIDER="local"
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION=384

# Application Public URL
APP_URL="https://your-domain.run.app"
```

---

## 2. Installation & Dependencies

### Backend Dependencies (Python 3.11+)
```bash
pip install -r requirements.txt
```

### Frontend Dependencies (Node.js 18+)
```bash
npm install
```

---

## 3. Database Migrations & pgvector Initialization

Darukaa.Earth uses SQLAlchemy 2.0 and Alembic for database schema management, supporting PostgreSQL with `pgvector`.

1. **Verify Database Connection**:
   Ensure `DATABASE_URL` in `.env` is correctly configured and reachable.

2. **Enable pgvector Extension (Run once on PostgreSQL)**:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Run Alembic Migrations**:
   ```bash
   cd backend
   alembic upgrade head
   ```

---

## 4. Dataset & Model Initialization

- **Scientific Knowledge Corpus**: The curated corpus of IPBES, IPCC, FAO, UNEP, and CBD evidence chunks is automatically initialized on startup via `curated_corpus.py` and `rag_service.py`.
- **Local Embeddings**: The lightweight `all-MiniLM-L6-v2` embedding model runs locally on CPU (`embedding_dimension = 384`), avoiding heavy external downloads during container startup.
- **LLM Abstraction**: Connects to Gemini via `@google/genai` with automatic fallback to local deterministic reasoning if API quotas or rate limits are reached.

---

## 5. Startup Commands

### Start Backend (FastAPI + Uvicorn)
```bash
cd backend
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8001 --reload
```
*(Or via project root using Python module path)*:
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8001
```

### Build & Start Frontend (Vite SPA)
```bash
# Build production bundle
npm run build

# Preview production build locally
npm run preview -- --port 3000 --host 0.0.0.0
```

---

## 6. Health Checks & Operational Telemetry

Darukaa.Earth provides built-in health and telemetry endpoints for monitoring:

- **API Health**: `GET /api/v1/health`
- **System Performance Dashboard**: `GET /api/v1/performance` (returns live API latency, database connection health, pgvector status, and model memory footprints).

---

## 7. Troubleshooting & Common Issues

1. **Database Connection Refused**:
   - Check that `DATABASE_URL` credentials are correct and percent-encoded if passwords contain special characters.
   - Verify network access / SSL mode for cloud databases (Supabase, Neon).

2. **pgvector Extension Missing**:
   - Run `CREATE EXTENSION IF NOT EXISTS vector;` in your PostgreSQL SQL editor.

3. **Gemini API Rate Limit / Quota Exceeded**:
   - The system automatically triggers graceful fallback to local deterministic ecological reasoning and evidence matching without interrupting live demonstrations.
