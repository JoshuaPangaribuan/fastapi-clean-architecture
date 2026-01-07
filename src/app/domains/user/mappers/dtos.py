"""Pydantic DTOs for User domain."""

from pydantic import BaseModel, Field


class CreateUserInputDTO(BaseModel):
    """Input DTO for creating a user."""

    email: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=255)


class CreateUserOutputDTO(BaseModel):
    """Output DTO after creating a user."""

    id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's name")
    is_active: bool = Field(..., description="Whether the user is active")


class GetUserOutputDTO(BaseModel):
    """Output DTO for retrieving a user."""

    id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's name")
    is_active: bool = Field(..., description="Whether the user is active")
    created_at: str = Field(..., description="User creation timestamp in ISO format")
