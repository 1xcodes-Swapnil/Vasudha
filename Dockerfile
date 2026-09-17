# Multi-stage Dockerfile for VASUDHA Biodiversity Intelligence

# Stage 1: Build the React + TypeScript frontend
FROM node:20-slim AS frontend-builder

WORKDIR /app

COPY package*.json tsconfig*.json vite.config.ts ./
RUN npm install

COPY index.html ./
COPY src/ ./src/

RUN npm run build


# Stage 2: Python Backend & Production Runtime
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code, migrations, and configuration
COPY backend/ ./backend/
COPY alembic.ini pytest.ini .env.example ./

# Copy built frontend
COPY --from=frontend-builder /app/dist ./dist

# Runtime configuration
ENV BACKEND_HOST="0.0.0.0"
ENV ENVIRONMENT="production"

EXPOSE 10000

# Start FastAPI
CMD ["sh", "-c", "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
