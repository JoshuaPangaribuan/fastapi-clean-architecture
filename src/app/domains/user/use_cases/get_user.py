"""
Get User Use Case.

This contains the application business logic for retrieving users.
"""

from app.core.exceptions import ResourceNotFoundError
from app.core.validation import parse_uuid
from app.domains.user.mappers.dtos import GetUserOutputDTO as GetUserOutput
from app.domains.user.mappers.entity_dto_mapper import UserEntityDtoMapper
from app.domains.user.repositories.user_repository import UserRepositoryInterface


class UserNotFoundError(ResourceNotFoundError):
    """Raised when a user is not found."""

    pass


class GetUserByIdUseCase:
    """Use case for getting a user by their ID."""

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        mapper: UserEntityDtoMapper,
    ) -> None:
        """Initialize the use case with dependencies."""
        self._user_repository = user_repository
        self._mapper = mapper

    async def execute(self, user_id: str) -> GetUserOutput:
        """
        Execute the get user by ID use case.

        Args:
            user_id: The user's UUID as a string.

        Returns:
            Output data with the user information.

        Raises:
            UserNotFoundError: If user is not found.
            DomainError: If the user_id is not a valid UUID.
        """
        uuid = parse_uuid(user_id, "user_id")

        user = await self._user_repository.get_by_id(uuid)
        if user is None:
            raise UserNotFoundError(
                f"User with ID {user_id} not found",
                code="USER_NOT_FOUND",
                details={"user_id": user_id},
            )

        return self._mapper.to_get_output(user)


class GetAllUsersUseCase:
    """Use case for getting all users with pagination."""

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        mapper: UserEntityDtoMapper,
    ) -> None:
        """Initialize the use case with dependencies."""
        self._user_repository = user_repository
        self._mapper = mapper

    async def execute(self, skip: int = 0, limit: int = 100) -> list[GetUserOutput]:
        """
        Execute get all users use case.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of user output data.
        """
        users = await self._user_repository.get_all(skip=skip, limit=limit)

        return self._mapper.to_get_outputs(users)
