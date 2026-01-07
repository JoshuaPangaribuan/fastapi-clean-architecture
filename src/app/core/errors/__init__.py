"""Errors module."""

from app.core.errors.exceptions import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    BusinessRuleError,
    DomainError,
    InvalidOperationError,
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)
from app.core.errors.handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.errors.schemas import ErrorDetail, ErrorResponse

__all__ = [
    "AppError",
    "AuthenticationError",
    "AuthorizationError",
    "BusinessRuleError",
    "DomainError",
    "ErrorDetail",
    "ErrorResponse",
    "InvalidOperationError",
    "ResourceConflictError",
    "ResourceNotFoundError",
    "ValidationError",
    "app_exception_handler",
    "http_exception_handler",
    "validation_exception_handler",
]
