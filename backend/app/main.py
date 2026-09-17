"""Main entry point for the VASUDHA Biodiversity Intelligence FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.router import api_router
from backend.app.core.config import get_settings
from backend.app.core.errors import register_exception_handlers
from backend.app.core.logging import logger
from backend.app.schemas.health import HealthResponse
from backend.app.db.session import check_db_health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager handling startup and shutdown events."""
    settings = get_settings()
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    try:
        from backend.app.db.session import SessionLocal
        from backend.app.knowledge.repository import KnowledgeRepository

        db = SessionLocal()
        try:
            KnowledgeRepository.seed_knowledge_base(db)
        finally:
            db.close()
    except Exception as exc:
        logger.warning(f"Initial knowledge base seeding skipped or deferred: {exc}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


def create_application() -> FastAPI:
    """Application factory configuring routes, middleware, and exception handlers."""
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=(
            "Hybrid Layered RAG Architecture with Knowledge-Based Ecological Reasoning "
            "for the VASUDHA Biodiversity Intelligence Platform."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # CORS configuration for development and frontend communication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Centralized exception handling
    register_exception_handlers(app)

    # Include API router (e.g. /api/v1/health)
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Top-level health check endpoint for deployment/container orchestrators
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def root_health() -> HealthResponse:
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

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "backend.app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG or settings.ENVIRONMENT == "development",
    )
