"""Database engine, connection pooling, and session management for PostgreSQL + pgvector (with SQLite fallback)."""

from typing import Generator, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from backend.app.core.config import get_settings
from backend.app.core.logging import logger
from backend.app.db.base import Base

# Ensure all database models are imported so Base.metadata is fully populated
import backend.app.models.environmental_state  # noqa: F401
import backend.app.models.knowledge  # noqa: F401
import backend.app.models.scientific_corpus  # noqa: F401
import backend.app.models.dataset  # noqa: F401

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None
_using_fallback: bool = False


def reset_engine() -> None:
    """Reset the cached engine and sessionmaker (primarily for testing)."""
    global _engine, _SessionLocal, _using_fallback
    _engine = None
    _SessionLocal = None
    _using_fallback = False


def get_engine() -> Engine:
    """Initialize or retrieve the database engine with automatic fallback when configured."""
    global _engine, _using_fallback
    if _engine is not None:
        return _engine

    settings = get_settings()
    db_url = settings.DATABASE_URL

    connect_args: Dict[str, Any] = {}
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        _engine = create_engine(
            db_url,
            connect_args=connect_args,
            echo=settings.DEBUG,
        )
        Base.metadata.create_all(bind=_engine)
        _using_fallback = False
        logger.info(f"Database engine initialized for SQLite: {db_url}")
        return _engine

    # PostgreSQL candidate connection
    try:
        candidate_engine = create_engine(
            db_url,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=min(settings.DB_POOL_TIMEOUT, 3),
            pool_pre_ping=True,
            connect_args={"connect_timeout": 2},
            echo=settings.DEBUG,
        )
        # Probe connection to verify PostgreSQL is truly accessible
        with candidate_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        _engine = candidate_engine
        _using_fallback = False
        logger.info(f"Database engine initialized for PostgreSQL dialect: {_engine.dialect.name}")
        return _engine
    except Exception:
        if settings.ALLOW_SQLITE_TEST_FALLBACK:
            logger.info(
                f"Configured database at {settings.database_url_safe} is not accessible. "
                "Activating local SQLite fallback database (vasudha_earth.db)."
            )
            fallback_url = "sqlite:///./vasudha_earth.db"
            _engine = create_engine(
                fallback_url,
                connect_args={"check_same_thread": False},
                echo=settings.DEBUG,
            )
            _using_fallback = True
            # Create all registered tables on the local SQLite store
            Base.metadata.create_all(bind=_engine)
            logger.info("Local SQLite database initialized with all metadata tables.")
            return _engine
        else:
            logger.error("Primary database connection failed and fallback is disabled.")
            raise exc


def get_sessionmaker() -> sessionmaker[Session]:
    """Retrieve or create the sessionmaker factory."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for obtaining a database session."""
    session_factory = get_sessionmaker()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def check_db_health() -> Dict[str, Any]:
    """Check database connectivity and verify if pgvector is enabled."""
    try:
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()

            # Check pgvector extension if connected to PostgreSQL
            has_pgvector = False
            if engine.dialect.name == "postgresql":
                vec_check = connection.execute(
                    text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                )
                has_pgvector = vec_check.fetchone() is not None

            return {
                "status": "connected",
                "dialect": engine.dialect.name,
                "pgvector_enabled": has_pgvector,
                "fallback_active": _using_fallback,
            }
    except Exception:
        logger.warning("Database health check failed")
        return {
            "status": "disconnected",
            "error": "Database connectivity check failed",
            "pgvector_enabled": False,
            "fallback_active": False,
        }

