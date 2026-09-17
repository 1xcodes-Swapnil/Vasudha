"""Unit tests for the System Performance monitoring API endpoint."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_system_performance_endpoint():
    """Test GET /api/v1/performance returns correct latency, db status, and model memory metrics."""
    response = client.get("/api/v1/performance")
    assert response.status_code == 200
    data = response.json()

    assert "average_api_latency_ms" in data
    assert "database" in data
    assert "models" in data
    assert "system_resources" in data

    # Check database info
    db_info = data["database"]
    assert "status" in db_info
    assert "dialect" in db_info
    assert "pgvector_enabled" in db_info
    assert "connection_latency_ms" in db_info

    # Check models info
    models = data["models"]
    assert "embedding_model" in models
    assert "llm_model" in models
    assert models["embedding_model"]["estimated_memory_mb"] > 0
    assert models["llm_model"]["estimated_memory_mb"] > 0

    # Check system resources
    resources = data["system_resources"]
    assert "cpu_usage_percent" in resources
    assert "rss_memory_mb" in resources
    assert "active_threads" in resources
