"""
Delete User Use Case.

This contains the application business logic for deleting a user.
"""

from uuid import UUID

from app.core.exceptions import DomainError
from app.domains.user.repositories.user_repository import UserRepositoryInterface
from app.domains.user.use_cases.get_user import UserNotFoundError


class DeleteUserUseCase:
    """Use case for deleting a user."""

    def __init__(self, user_repository: UserRepositoryInterface) -> None:
        """Initialize the use case with dependencies."""
        self._user_repository = user_repository

    async def execute(self, user_id: str) -> bool:
        """
        Execute the delete user use case.

        Args:
            user_id: The user's UUID as a string.

        Returns:
            True if the user was deleted.

        Raises:
            UserNotFoundError: If user is not found.
            DomainError: If user_id is not a valid UUID.
        """
        try:
            uuid = UUID(user_id)
        except ValueError:
            raise DomainError(f"Invalid user ID format: {user_id}")

        deleted = await self._user_repository.delete(uuid)
        if not deleted:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        return True
