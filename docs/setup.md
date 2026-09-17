# Local Setup & Development Guide

## Prerequisites

- **Node.js**: v18+ (v20 recommended)
- **Python**: v3.10+ (v3.11 recommended)
- **Docker & Docker Compose** (for PostgreSQL + pgvector)

---

## 1. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Configure your parameters in `.env`:
- `GEMINI_API_KEY`: Your Google Gemini API Key.
- `DATABASE_URL`: PostgreSQL connection string (e.g. `postgresql+psycopg2://<username>:<password>@<host>:5432/<dbname>` or `sqlite:///./darukaa_earth.db` for local dev).
- `ENVIRONMENT`: `development`, `testing`, or `production`.

---

## 2. Dockerized Setup (Recommended)

To start PostgreSQL with `pgvector` and the application in isolated containers:

```bash
docker compose up -d
```

- **Frontend & Applet UI**: http://localhost:3000
- **FastAPI Backend Swagger Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/api/v1/health

---

## 3. Local Native Setup

### Backend Setup

1. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI development server:
   ```bash
   python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001 --reload
   ```

### Frontend Setup

1. Install frontend dependencies:
   ```bash
   npm install
   ```

2. Start the Vite development server:
   ```bash
   npm run dev
   ```

---

## 4. Running Tests

Run the complete test suite (backend pytest + frontend type check & build):

```bash
./scripts/run_tests.sh
```

Or run backend tests individually:

```bash
pytest backend/tests -v
```

Run frontend linting:

```bash
npm run lint
```
