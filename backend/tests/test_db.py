"""Unit tests for database session and model configuration."""

from sqlalchemy import text
from backend.app.db.base import Base, TimestampMixin
from backend.app.db.session import check_db_health, get_engine


def test_base_metadata_initialized():
    """Verify that SQLAlchemy declarative base is properly configured."""
    assert Base.metadata is not None
    assert isinstance(TimestampMixin, type)


def test_check_db_health_returns_structured_dict():
    """Verify check_db_health returns expected keys even if DB is unavailable."""
    health = check_db_health()
    assert "status" in health
    assert "pgvector_enabled" in health
    assert health["status"] in ("connected", "disconnected")


def test_sqlite_in_memory_engine():
    """Verify that SQLite engine can execute a query for local testing."""
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        res = conn.execute(text("SELECT 1"))
        assert res.scalar() == 1


def test_database_engine_factory():
    """Verify get_engine constructs an engine instance."""
    engine = get_engine()
    assert engine is not None
    assert hasattr(engine, "dialect")
