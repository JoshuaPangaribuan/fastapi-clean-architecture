"""
Create User Use Case.

This contains the application business logic for creating a user.
It orchestrates the flow and uses the repository interface.
"""

from app.core.errors import ResourceConflictError
from app.domains.user.mappers.dtos import (
    CreateUserInputDTO as CreateUserInput,
)
from app.domains.user.mappers.dtos import (
    CreateUserOutputDTO as CreateUserOutput,
)
from app.domains.user.mappers.entity_dto_mapper import UserEntityDtoMapper
from app.domains.user.repositories.user_repository import UserRepositoryInterface


class UserAlreadyExistsError(ResourceConflictError):
    """Raised when trying to create a user with an existing email."""

    pass


class CreateUserUseCase:
    """
    Use case for creating a new user.

    This class contains the application business logic for user creation.
    It depends on the repository interface, not the concrete implementation.
    """

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        mapper: UserEntityDtoMapper,
    ) -> None:
        """
        Initialize the use case with dependencies.

        Args:
            user_repository: Repository interface for user data access.
            mapper: User entity-DTO mapper.
        """
        self._user_repository = user_repository
        self._mapper = mapper

    async def execute(self, input_data: CreateUserInput) -> CreateUserOutput:
        """
        Execute the create user use case.

        Args:
            input_data: Input data containing email and name.

        Returns:
            Output data with the created user information.

        Raises:
            UserAlreadyExistsError: If a user with the email already exists.
            ValueError: If the input data is invalid.
        """
        # Check if user already exists
        existing_user = await self._user_repository.get_by_email(input_data.email)
        if existing_user is not None:
            raise UserAlreadyExistsError(
                f"User with email {input_data.email} already exists",
                code="USER_ALREADY_EXISTS",
                details={"email": input_data.email},
            )

        # Create the user entity from input DTO (this validates business rules)
        user = self._mapper.from_create_input(input_data)

        # Persist the user
        created_user = await self._user_repository.create(user)

        # Return the output using mapper
        return self._mapper.to_create_output(created_user)
