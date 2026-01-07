from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domains.user.infrastructure.database.user_repository_impl import SQLAlchemyUserRepository
from app.domains.user.mappers.entity_dto_mapper import UserEntityDtoMapper
from app.domains.user.mappers.entity_model_mapper import UserEntityModelMapper
from app.domains.user.use_cases.create_user import CreateUserUseCase
from app.domains.user.use_cases.delete_user import DeleteUserUseCase
from app.domains.user.use_cases.get_user import (
    GetAllUsersUseCase,
    GetUserByIdUseCase,
)


def get_entity_model_mapper() -> UserEntityModelMapper:
    """Get the entity-model mapper (singleton)."""
    return UserEntityModelMapper()


def get_entity_dto_mapper() -> UserEntityDtoMapper:
    """Get the entity-DTO mapper (singleton)."""
    return UserEntityDtoMapper()


def get_user_repository(
    db: AsyncSession = Depends(get_db),
    mapper: UserEntityModelMapper = Depends(get_entity_model_mapper),
) -> SQLAlchemyUserRepository:
    """Get the user repository with database session."""
    return SQLAlchemyUserRepository(db, mapper)


def get_create_user_use_case(
    repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    mapper: UserEntityDtoMapper = Depends(get_entity_dto_mapper),
) -> CreateUserUseCase:
    """Get the create user use case."""
    return CreateUserUseCase(repo, mapper)


def get_user_by_id_use_case(
    repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    mapper: UserEntityDtoMapper = Depends(get_entity_dto_mapper),
) -> GetUserByIdUseCase:
    """Get the get user by ID use case."""
    return GetUserByIdUseCase(repo, mapper)


def get_all_users_use_case(
    repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    mapper: UserEntityDtoMapper = Depends(get_entity_dto_mapper),
) -> GetAllUsersUseCase:
    """Get the get all users use case."""
    return GetAllUsersUseCase(repo, mapper)


def get_delete_user_use_case(
    repo: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> DeleteUserUseCase:
    """Get the delete user use case."""
    return DeleteUserUseCase(repo)
