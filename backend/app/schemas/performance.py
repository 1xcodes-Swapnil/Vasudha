"""System performance and resource monitoring schemas."""

from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import BaseModel, Field


class ModelMemoryInfo(BaseModel):
    provider: str
    model_name: str
    estimated_memory_mb: float
    cache_entries: int
    status: str


class DatabasePerformanceInfo(BaseModel):
    status: str
    dialect: str
    pgvector_enabled: bool
    fallback_active: bool
    pool_size: int
    connection_latency_ms: float


class SystemPerformanceResponse(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    average_api_latency_ms: float
    database: DatabasePerformanceInfo
    models: Dict[str, ModelMemoryInfo]
    system_resources: Dict[str, Any]
