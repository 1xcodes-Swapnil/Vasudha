"""Integration tests for application health endpoints."""

from fastapi.testclient import TestClient


def test_root_health_endpoint(client: TestClient):
    """Verify that root /health returns HTTP 200 with valid health payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "VASUDHA" in data["service"]
    assert "version" in data
    assert "database" in data
    assert "ai_providers" in data


def test_api_v1_health_endpoint(client: TestClient):
    """Verify that /api/v1/health returns HTTP 200 and matches the HealthResponse schema."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "VASUDHA — Biodiversity Intelligence"
    assert "llm" in data["ai_providers"]
    assert "embeddings" in data["ai_providers"]


def test_health_endpoints_do_not_expose_secrets(client: TestClient):
    """Verify health endpoints never expose passwords, API keys, or raw env secrets."""
    for path in ("/health", "/api/v1/health"):
        response = client.get(path)
        assert response.status_code == 200
        text = response.text.lower()
        # Ensure sensitive variable names or token values never leak into payload
        assert "password" not in text
        assert "gemini_api_key" not in text
        assert "secret" not in text
        assert "aiza" not in text
        assert "bearer" not in text
