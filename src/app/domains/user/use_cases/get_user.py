"""
Get User Use Case.

This contains the application business logic for retrieving users.
"""

from dataclasses import dataclass
from uuid import UUID

from app.core.exceptions import DomainError, ResourceNotFoundError
from app.domains.user.repositories.user_repository import UserRepositoryInterface


class UserNotFoundError(ResourceNotFoundError):
    """Raised when a user is not found."""

    pass


@dataclass
class GetUserOutput:
    """Output data for a single user."""

    id: str
    email: str
    name: str
    is_active: bool
    created_at: str


class GetUserByIdUseCase:
    """Use case for getting a user by their ID."""

    def __init__(self, user_repository: UserRepositoryInterface) -> None:
        """Initialize the use case with dependencies."""
        self._user_repository = user_repository

    async def execute(self, user_id: str) -> GetUserOutput:
        """
        Execute the get user by ID use case.

        Args:
            user_id: The user's UUID as a string.

        Returns:
            Output data with the user information.

        Raises:
            UserNotFoundError: If the user is not found.
            DomainError: If the user_id is not a valid UUID.
        """
        try:
            uuid = UUID(user_id)
        except ValueError:
            raise DomainError(f"Invalid user ID format: {user_id}")

        user = await self._user_repository.get_by_id(uuid)
        if user is None:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        return GetUserOutput(
            id=str(user.id),
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        )


class GetAllUsersUseCase:
    """Use case for getting all users with pagination."""

    def __init__(self, user_repository: UserRepositoryInterface) -> None:
        """Initialize the use case with dependencies."""
        self._user_repository = user_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> list[GetUserOutput]:
        """
        Execute the get all users use case.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of user output data.
        """
        users = await self._user_repository.get_all(skip=skip, limit=limit)

        return [
            GetUserOutput(
                id=str(user.id),
                email=user.email,
                name=user.name,
                is_active=user.is_active,
                created_at=user.created_at.isoformat(),
            )
            for user in users
        ]
