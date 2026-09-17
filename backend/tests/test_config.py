"""Unit tests for configuration, environment handling, and security hardening."""

import subprocess
import pytest
from backend.app.core.config import Settings, get_settings


def test_default_settings_load_successfully():
    """Verify that settings can be instantiated and contain default project configuration."""
    settings = get_settings()
    assert settings.PROJECT_NAME == "VASUDHA — Biodiversity Intelligence"
    assert settings.VERSION == "0.1.0"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.DEFAULT_LLM_PROVIDER in ("gemini", "mock", "local")
    assert settings.DEFAULT_EMBEDDING_PROVIDER in ("local", "free", "dummy", "sentence_transformers")
    assert settings.EMBEDDING_DIMENSION > 0


def test_settings_environment_override():
    """Verify custom environment values override defaults cleanly."""
    custom = Settings(
        ENVIRONMENT="testing",
        BACKEND_PORT=9000,
        DEBUG=True,
    )
    assert custom.ENVIRONMENT == "testing"
    assert custom.BACKEND_PORT == 9000
    assert custom.DEBUG is True


def test_database_url_masking_security():
    """Verify that database_url_safe properly redacts database passwords."""
    raw_url = "postgresql+psycopg2://testuser:supersecretpass@db.example.com:5432/vasudha_earth"
    custom = Settings(DATABASE_URL=raw_url)
    safe_url = custom.database_url_safe
    assert "supersecretpass" not in safe_url
    assert "testuser:***@db.example.com" in safe_url


def test_settings_repr_does_not_leak_secrets():
    """Verify that Settings __repr__ and __str__ mask secret values."""
    custom = Settings(
        DATABASE_URL="postgresql://admin:mypassword@localhost:5432/mydb",
        GEMINI_API_KEY="AIzaSyDummySecretKey1234567890",
    )
    repr_str = repr(custom)
    str_str = str(custom)
    assert "mypassword" not in repr_str
    assert "AIzaSyDummySecretKey1234567890" not in repr_str
    assert "mypassword" not in str_str
    assert "AIzaSyDummySecretKey1234567890" not in str_str


def test_production_validation_catches_missing_secrets():
    """Verify production configuration fails with clear message when required secrets are missing."""
    invalid_prod_settings = Settings(
        ENVIRONMENT="production",
        DEFAULT_LLM_PROVIDER="gemini",
        GEMINI_API_KEY=None,
    )
    with pytest.raises(ValueError, match="Production configuration validation failed"):
        invalid_prod_settings.validate_production_configuration()


def test_production_validation_succeeds_with_valid_configuration():
    """Verify production configuration passes when valid parameters are provided."""
    valid_prod_settings = Settings(
        ENVIRONMENT="production",
        DEFAULT_LLM_PROVIDER="gemini",
        GEMINI_API_KEY="valid-secret-key-prod-12345",
        DATABASE_URL="postgresql+psycopg2://user:pass@db:5432/vasudha_earth",
    )
    # Should not raise
    valid_prod_settings.validate_production_configuration()


def test_sensitive_files_are_ignored_by_git():
    """Verify gitignore rules properly prevent tracking of secrets and temporary files."""
    test_files = [
        ".env",
        ".env.local",
        ".env.production",
        "credentials.json",
        "service-account.json",
        "server.key",
        "temp.db",
        "test.sqlite",
    ]
    result = subprocess.run(
        ["git", "check-ignore", "-v"] + test_files,
        capture_output=True,
        text=True,
    )
    # git check-ignore exits with 0 if all or some files match
    assert result.returncode == 0
    for filename in test_files:
        assert filename in result.stdout

    # Verify that tracked templates and source files are NOT ignored
    unignored_files = [".env.example", ".env.template", "README.md", "src/App.tsx"]
    unignored_check = subprocess.run(
        ["git", "check-ignore", "-v"] + unignored_files,
        capture_output=True,
        text=True,
    )
    # For unignored files, they should either not appear or match negation patterns !.env.example
    assert ".env.example" in unignored_check.stdout  # Matches negation !.env.example
    assert "README.md" not in unignored_check.stdout

