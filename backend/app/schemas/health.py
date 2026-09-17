"""Health check and system status schemas."""

from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema for service health and operational status."""

    status: str = Field(default="ok", description="Overall health status of the application.")
    service: str = Field(description="Name of the service.")
    version: str = Field(description="Semver version of the service.")
    environment: str = Field(description="Runtime environment (development/testing/production).")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the health check."
    )
    database: Dict[str, Any] = Field(description="Database connectivity and extension status.")
    ai_providers: Dict[str, str] = Field(description="Configured AI providers (LLM and Embeddings).")
