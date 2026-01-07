"""
User API Router.

This is the presentation layer - it handles HTTP requests/responses.
It uses dependency injection to get use cases.
"""

from fastapi import APIRouter, Depends, status

from app.domains.user.dependencies import (
    get_all_users_use_case,
    get_create_user_use_case,
    get_delete_user_use_case,
    get_user_by_id_use_case,
)
from app.domains.user.presentation.v1.schemas import (
    MessageResponse,
    UserCreateRequest,
    UserDetailResponse,
    UserListResponse,
    UserResponse,
)
from app.domains.user.use_cases.create_user import (
    CreateUserInput,
    CreateUserUseCase,
)
from app.domains.user.use_cases.delete_user import DeleteUserUseCase
from app.domains.user.use_cases.get_user import (
    GetAllUsersUseCase,
    GetUserByIdUseCase,
)

router = APIRouter(prefix="/users", tags=["Users"])


# ============== API Endpoints ==============


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with the provided email and name.",
)
async def create_user(
    request: UserCreateRequest, use_case: CreateUserUseCase = Depends(get_create_user_use_case)
) -> UserResponse:
    """Create a new user."""
    input_data = CreateUserInput(email=request.email, name=request.name)
    output = await use_case.execute(input_data)

    return UserResponse(
        id=output.id, email=output.email, name=output.name, is_active=output.is_active
    )


@router.get(
    "",
    response_model=UserListResponse,
    summary="Get all users",
    description="Retrieve a list of all users with pagination.",
)
async def get_users(
    skip: int = 0, limit: int = 100, use_case: GetAllUsersUseCase = Depends(get_all_users_use_case)
) -> UserListResponse:
    """Get all users with pagination."""
    users = await use_case.execute(skip=skip, limit=limit)

    return UserListResponse(
        users=[
            UserDetailResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                is_active=user.is_active,
                created_at=user.created_at,
            )
            for user in users
        ],
        total=len(users),
    )


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Get a user by ID",
    description="Retrieve a specific user by their unique identifier.",
)
async def get_user(
    user_id: str, use_case: GetUserByIdUseCase = Depends(get_user_by_id_use_case)
) -> UserDetailResponse:
    """Get a user by their ID."""
    output = await use_case.execute(user_id)

    return UserDetailResponse(
        id=output.id,
        email=output.email,
        name=output.name,
        is_active=output.is_active,
        created_at=output.created_at,
    )


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete a user",
    description="Delete a user by their unique identifier.",
)
async def delete_user(
    user_id: str, use_case: DeleteUserUseCase = Depends(get_delete_user_use_case)
) -> MessageResponse:
    """Delete a user by their ID."""
    await use_case.execute(user_id)
    return MessageResponse(message=f"User {user_id} deleted successfully", success=True)
