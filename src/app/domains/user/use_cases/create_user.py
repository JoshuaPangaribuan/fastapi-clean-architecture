"""
Create User Use Case.

This contains the application business logic for creating a user.
It orchestrates the flow and uses the repository interface.
"""

from dataclasses import dataclass

from app.core.exceptions import ResourceConflictError
from app.domains.user.entities.user import User
from app.domains.user.repositories.user_repository import UserRepositoryInterface


class UserAlreadyExistsError(ResourceConflictError):
    """Raised when trying to create a user with an existing email."""

    pass


@dataclass
class CreateUserInput:
    """Input data for creating a user."""

    email: str
    name: str


@dataclass
class CreateUserOutput:
    """Output data after creating a user."""

    id: str
    email: str
    name: str
    is_active: bool


class CreateUserUseCase:
    """
    Use case for creating a new user.

    This class contains the application business logic for user creation.
    It depends on the repository interface, not the concrete implementation.
    """

    def __init__(self, user_repository: UserRepositoryInterface) -> None:
        """
        Initialize the use case with dependencies.

        Args:
            user_repository: Repository interface for user data access.
        """
        self._user_repository = user_repository

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
            raise UserAlreadyExistsError(f"User with email {input_data.email} already exists")

        # Create the user entity (this validates business rules)
        user = User(email=input_data.email, name=input_data.name)

        # Persist the user
        created_user = await self._user_repository.create(user)

        # Return the output
        return CreateUserOutput(
            id=str(created_user.id),
            email=created_user.email,
            name=created_user.name,
            is_active=created_user.is_active,
        )
