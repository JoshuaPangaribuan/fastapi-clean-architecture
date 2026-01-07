import re
from typing import Any


class AppError(Exception):
    """Base exception for application with structured error data."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code or self._default_code()
        self.details = details or {}
        super().__init__(message)

    def _default_code(self) -> str:
        """Generate default error code from class name.

        Converts "UserNotFoundError" to "USER_NOT_FOUND".
        """
        class_name = self.__class__.__name__
        return re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).upper()


class ResourceNotFoundError(AppError):
    """Raised when a requested resource is not found."""

    pass


class ResourceConflictError(AppError):
    """Raised when a resource conflict occurs (e.g. unique constraint violation)."""

    pass


class DomainError(AppError):
    """Base exception for domain rules violations."""

    pass


class ValidationError(DomainError):
    """Raised when input validation fails."""

    pass


class BusinessRuleError(DomainError):
    """Raised when domain-specific business rules are violated."""

    pass


class InvalidOperationError(DomainError):
    """Raised when an operation is invalid for the current state."""

    pass


class AuthenticationError(AppError):
    """Raised when authentication fails (401)."""

    pass


class AuthorizationError(AppError):
    """Raised when authorization fails (403)."""

    pass
