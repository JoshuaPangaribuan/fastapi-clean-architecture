from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domains.user.infrastructure.database.user_repository_impl import SQLAlchemyUserRepository
from app.domains.user.use_cases.create_user import CreateUserUseCase
from app.domains.user.use_cases.delete_user import DeleteUserUseCase
from app.domains.user.use_cases.get_user import (
    GetAllUsersUseCase,
    GetUserByIdUseCase,
)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyUserRepository:
    """Get the user repository with database session."""
    return SQLAlchemyUserRepository(db)


def get_create_user_use_case(
    repo: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> CreateUserUseCase:
    """Get the create user use case."""
    return CreateUserUseCase(repo)


def get_user_by_id_use_case(
    repo: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> GetUserByIdUseCase:
    """Get the get user by ID use case."""
    return GetUserByIdUseCase(repo)


def get_all_users_use_case(
    repo: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> GetAllUsersUseCase:
    """Get the get all users use case."""
    return GetAllUsersUseCase(repo)


def get_delete_user_use_case(
    repo: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> DeleteUserUseCase:
    """Get the delete user use case."""
    return DeleteUserUseCase(repo)
