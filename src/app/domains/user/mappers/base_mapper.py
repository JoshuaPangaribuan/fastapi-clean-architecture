"""Base Mapper with common utilities for type conversions."""

from datetime import datetime
from uuid import UUID


class BaseMapper:
    """Base mapper with common type conversion utilities."""

    @staticmethod
    def convert_uuid_to_str(uuid_obj: UUID | None) -> str | None:
        """
        Convert UUID to string representation.

        Args:
            uuid_obj: UUID object or None

        Returns:
            String representation of UUID or None
        """
        return str(uuid_obj) if uuid_obj else None

    @staticmethod
    def convert_str_to_uuid(uuid_str: str | None) -> UUID | None:
        """
        Convert string to UUID.

        Args:
            uuid_str: String representation of UUID or None

        Returns:
            UUID object or None

        Raises:
            ValueError: If string is not a valid UUID
        """
        return UUID(uuid_str) if uuid_str else None

    @staticmethod
    def convert_datetime_to_iso(dt: datetime | None) -> str | None:
        """
        Convert datetime to ISO 8601 string.

        Args:
            dt: Datetime object or None

        Returns:
            ISO 8601 formatted string or None
        """
        return dt.isoformat() if dt else None

    @staticmethod
    def convert_iso_to_datetime(iso_str: str | None) -> datetime | None:
        """
        Convert ISO 8601 string to datetime.

        Args:
            iso_str: ISO 8601 formatted string or None

        Returns:
            Datetime object or None

        Raises:
            ValueError: If string is not a valid ISO format
        """
        return datetime.fromisoformat(iso_str) if iso_str else None
