"""Health check and diagnostic API endpoints."""

from fastapi import APIRouter, status
from backend.app.core.config import get_settings
from backend.app.db.session import check_db_health
from backend.app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Health Check",
    description="Check operational health, database connectivity, and configured AI abstractions.",
)
async def get_health() -> HealthResponse:
    """Return health status of the application, database, and subsystems."""
    settings = get_settings()
    db_health = check_db_health()

    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=db_health,
        ai_providers={
            "llm": settings.DEFAULT_LLM_PROVIDER,
            "embeddings": settings.DEFAULT_EMBEDDING_PROVIDER,
            "embedding_model": settings.EMBEDDING_MODEL,
        },
    )
