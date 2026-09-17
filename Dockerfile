# Multi-stage Dockerfile for Darukaa.Earth Biodiversity Intelligence
# Stage 1: Build the React + TypeScript frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app
COPY package*.json tsconfig*.json vite.config.ts ./
RUN npm install
COPY index.html ./
COPY src/ ./src/
COPY public/ ./public/
RUN npm run build

# Stage 2: Python Backend & Production Runtime
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for psycopg2 and utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code, migrations, and scripts
COPY backend/ ./backend/
COPY alembic.ini pytest.ini .env.example ./

# Copy built frontend assets from builder stage
COPY --from=frontend-builder /app/dist ./dist

# Set environment defaults
ENV PORT=3000
ENV BACKEND_HOST="0.0.0.0"
ENV BACKEND_PORT=8001
ENV ENVIRONMENT="production"

EXPOSE 3000 8001

# Start the FastAPI service
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
