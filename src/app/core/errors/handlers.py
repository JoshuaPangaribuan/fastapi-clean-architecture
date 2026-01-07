"""
Global exception handlers for the application.

This module provides centralized exception handling with structured error responses.
"""

import logging
from datetime import UTC, datetime

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .exceptions import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    DomainError,
    ResourceConflictError,
    ResourceNotFoundError,
)

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handler for standard HTTP exceptions.

    Handles standard Starlette HTTP exceptions like 404 Not Found,
    405 Method Not Allowed, etc.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": _get_http_error_code(exc.status_code),
                "message": str(exc.detail),
                "timestamp": datetime.now(UTC).isoformat(),
                "request_id": _get_request_id(request),
            }
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError | ValidationError
) -> JSONResponse:
    """Handler for Pydantic validation errors.

    Handles both RequestValidationError (from FastAPI) and ValidationError
    (from Pydantic directly), providing structured field-level error details.
    """
    errors = []
    if isinstance(exc, RequestValidationError):
        errors = exc.errors()
    elif isinstance(exc, ValidationError):
        errors = exc.errors()

    formatted_errors = [
        {
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in errors
    ]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": formatted_errors},
                "timestamp": datetime.now(UTC).isoformat(),
                "request_id": _get_request_id(request),
            }
        },
    )


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    """
    Global handler for application exceptions.

    Maps application exceptions to appropriate HTTP responses with
    structured error format including error codes, details, and logging.
    """
    # Determine HTTP status code
    status_code = _get_status_code_for_exception(exc)

    # Build error response
    error_response = {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details if exc.details else None,
            "timestamp": datetime.now(UTC).isoformat(),
            "request_id": _get_request_id(request),
        }
    }

    # Log error with appropriate level
    _log_error(exc, request, status_code)

    return JSONResponse(
        status_code=status_code,
        content=error_response,
    )


def _get_status_code_for_exception(exc: AppError) -> int:
    """Map exception type to HTTP status code.

    Returns the appropriate HTTP status code for each exception type,
    following REST API conventions.
    """
    status_map = {
        ResourceNotFoundError: status.HTTP_404_NOT_FOUND,
        ResourceConflictError: status.HTTP_409_CONFLICT,
        DomainError: status.HTTP_400_BAD_REQUEST,
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AuthorizationError: status.HTTP_403_FORBIDDEN,
    }

    for exc_class, code in status_map.items():
        if isinstance(exc, exc_class):
            return code

    return status.HTTP_500_INTERNAL_SERVER_ERROR


def _get_http_error_code(status_code: int) -> str:
    """Convert HTTP status code to error code string.

    Provides consistent error codes for standard HTTP errors.
    """
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR",
    }
    return code_map.get(status_code, "HTTP_ERROR")


def _get_request_id(request: Request) -> str | None:
    """Extract request ID from headers for tracing.

    Looks for X-Request-ID header to support distributed tracing.
    """
    return request.headers.get("X-Request-ID")


def _log_error(exc: AppError, request: Request, status_code: int) -> None:
    """Log error with appropriate level and context.

    Client errors (4xx) are logged as WARNING.
    Server errors (5xx) are logged as ERROR with full traceback.
    """
    # Client errors (4xx): log as warning
    if 400 <= status_code < 500:
        logger.warning(
            f"Client error: {exc.code} - {exc.message}",
            extra={
                "error_code": exc.code,
                "path": request.url.path,
                "method": request.method,
                "status_code": status_code,
            },
        )
    # Server errors (5xx): log as error
    else:
        logger.error(
            f"Server error: {exc.code} - {exc.message}",
            exc_info=exc,
            extra={
                "error_code": exc.code,
                "path": request.url.path,
                "method": request.method,
                "status_code": status_code,
            },
        )
