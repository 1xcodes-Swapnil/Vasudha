"""Centralized domain exceptions and HTTP error handlers."""

from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from backend.app.core.logging import logger


class BiodiversityAppError(Exception):
    """Base exception for all application-specific errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(BiodiversityAppError):
    """Raised when environment or module configuration is invalid."""
    pass


class DatabaseConnectionError(BiodiversityAppError):
    """Raised when database connection fails or is unavailable."""
    pass


class AIProviderError(BiodiversityAppError):
    """Raised when an AI provider call fails or provider is not configured."""
    pass


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers on the FastAPI app."""

    @app.exception_handler(BiodiversityAppError)
    async def app_error_handler(request: Request, exc: BiodiversityAppError) -> JSONResponse:
        logger.error(f"Application error on {request.method} {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "type": exc.__class__.__name__,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled error on {request.method} {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred. Please check server logs.",
                }
            },
        )
