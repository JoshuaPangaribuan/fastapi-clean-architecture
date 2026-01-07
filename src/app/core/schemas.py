"""
Core schemas for error responses.

This module defines Pydantic models for structured error responses.
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed error information for validation errors."""

    field: str | None = Field(None, description="Field path where error occurred")
    message: str = Field(..., description="Error message")
    type: str | None = Field(None, description="Error type identifier")
    value: str | None = Field(None, description="Invalid value that caused the error")


class ErrorResponse(BaseModel):
    """Standardized error response structure.

    This schema provides a consistent format for all error responses across the API.
    """

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(None, description="Additional error context")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Error timestamp (UTC)",
    )
    request_id: str | None = Field(None, description="Request ID for tracing")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "code": "USER_NOT_FOUND",
                "message": "User with ID 123 not found",
                "details": {"user_id": "123"},
                "timestamp": "2025-01-07T20:30:00Z",
                "request_id": "uuid-here",
            }
        }
