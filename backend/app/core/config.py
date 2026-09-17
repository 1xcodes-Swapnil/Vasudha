"""Application configuration management using Pydantic Settings."""

import re
from functools import lru_cache
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration settings for the Biodiversity Intelligence Backend."""

    PROJECT_NAME: str = "VASUDHA — Biodiversity Intelligence"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = False

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8001

    # Database Configuration (PostgreSQL + pgvector when configured in env, SQLite default for local/dev)
    DATABASE_URL: str = "sqlite:///./vasudha_earth.db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # Test/In-Memory Fallback if Postgres not yet spun up
    ALLOW_SQLITE_TEST_FALLBACK: bool = True

    # AI Provider Settings (Phase 8 Model Infrastructure)
    DEFAULT_LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-2.5-flash"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_OUTPUT_TOKENS: int = 2048

    DEFAULT_EMBEDDING_PROVIDER: str = "local"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIMENSION: int = 384
    EMBEDDING_DEVICE: str = "cpu"
    EMBEDDING_NORMALIZE: bool = True

    RERANKING_ENABLED: bool = False
    RERANKER_MODEL: str = "BAAI/bge-reranker-small"
    RERANKER_TOP_N: int = 5
    
    GEMINI_API_KEY: Optional[str] = None
    APP_URL: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @property
    def database_url_safe(self) -> str:
        """Return database URL with password credentials safely masked."""
        if not self.DATABASE_URL:
            return ""
        # Match user:password@
        return re.sub(r":([^:@]+)@", r":***@", self.DATABASE_URL)

    @property
    def is_gemini_configured(self) -> bool:
        """Check whether a non-empty valid Gemini API key is configured."""
        return bool(
            self.GEMINI_API_KEY
            and self.GEMINI_API_KEY.strip()
            and self.GEMINI_API_KEY not in ("MY_GEMINI_API_KEY", "placeholder", "your-gemini-api-key")
        )

    def validate_production_configuration(self) -> None:
        """Validate production configuration requirements and raise ValueError on missing secrets."""
        if self.ENVIRONMENT == "production":
            errors = []
            if self.DEFAULT_LLM_PROVIDER == "gemini" and not self.is_gemini_configured:
                errors.append("GEMINI_API_KEY is required in production when DEFAULT_LLM_PROVIDER='gemini'")
            if not self.DATABASE_URL or self.DATABASE_URL.strip() == "":
                errors.append("DATABASE_URL must be specified in production")
            if errors:
                raise ValueError(f"Production configuration validation failed: {'; '.join(errors)}")

    def __repr__(self) -> str:
        """Safely represent Settings without revealing sensitive credentials."""
        return (
            f"Settings(ENVIRONMENT={self.ENVIRONMENT!r}, "
            f"DEBUG={self.DEBUG!r}, "
            f"BACKEND_PORT={self.BACKEND_PORT!r}, "
            f"DATABASE_URL={self.database_url_safe!r}, "
            f"GEMINI_API_KEY={'***' if self.GEMINI_API_KEY else None!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()



@lru_cache()
def get_settings() -> Settings:
    """Retrieve cached application settings instance."""
    return Settings()
