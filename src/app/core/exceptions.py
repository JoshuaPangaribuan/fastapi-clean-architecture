class AppError(Exception):
    """Base exception for application."""

    pass


class ResourceNotFoundError(AppError):
    """Raised when a requested resource is not found."""

    pass


class ResourceConflictError(AppError):
    """Raised when a resource conflict occurs (e.g. unique constraint violation)."""

    pass


class DomainError(AppError):
    """Base exception for domain rules violations."""

    pass
