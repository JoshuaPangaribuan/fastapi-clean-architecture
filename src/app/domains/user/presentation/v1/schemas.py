"""
Pydantic Schemas for User API.

These are the request/response models for the API layer.
They are separate from the domain entities.
"""

from pydantic import BaseModel, EmailStr, Field


# ============== Request Schemas ==============

class UserCreateRequest(BaseModel):
    """Request schema for creating a user."""
    
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., min_length=1, max_length=255, description="User's name")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "john.doe@example.com",
                    "name": "John Doe"
                }
            ]
        }
    }


# ============== Response Schemas ==============

class UserResponse(BaseModel):
    """Response schema for a single user."""
    
    id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's name")
    is_active: bool = Field(..., description="Whether the user is active")
    
    model_config = {
        "from_attributes": True
    }


class UserDetailResponse(UserResponse):
    """Detailed response schema including timestamps."""
    
    created_at: str = Field(..., description="User creation timestamp")


class UserListResponse(BaseModel):
    """Response schema for a list of users."""
    
    users: list[UserDetailResponse]
    total: int = Field(..., description="Total number of users returned")


class MessageResponse(BaseModel):
    """Generic message response."""
    
    message: str
    success: bool = True
