class AppException(Exception):
    """Base exception for the application."""
    pass

class ResourceNotFoundException(AppException):
    """Raised when a requested resource is not found."""
    pass

class ResourceConflictException(AppException):
    """Raised when a resource conflict occurs (e.g. unique constraint violation)."""
    pass

class DomainException(AppException):
    """Base exception for domain rules violations."""
    pass
