"""
Shared validation utilities for common operations.

This module provides reusable validation functions used across the application.
"""

from uuid import UUID

from ..errors import DomainError


def parse_uuid(value: str, field_name: str = "ID") -> UUID:
    """
    Parse and validate a UUID from string.

    Args:
        value: The string value to parse as UUID.
        field_name: The name of the field being validated (for error messages).

    Returns:
        The parsed UUID object.

    Raises:
        DomainError: If the value is not a valid UUID format.
    """
    try:
        return UUID(value)
    except ValueError as exc:
        raise DomainError(
            f"Invalid {field_name.lower()} format: {value}",
            code=f"INVALID_{field_name.upper()}_FORMAT",
            details={field_name.lower(): value},
        ) from exc
