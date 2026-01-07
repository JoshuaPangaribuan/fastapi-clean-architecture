"""Mapper for User Entity ↔ Pydantic Schema conversions."""

from app.domains.user.entities.user import User
from app.domains.user.mappers.base_mapper import BaseMapper
from app.domains.user.presentation.v1.schemas import (
    UserCreateRequest,
    UserDetailResponse,
    UserListResponse,
    UserResponse,
)


class UserEntitySchemaMapper(BaseMapper):
    """Mapper for converting between User entity and Pydantic schemas."""

    def to_response(self, entity: User) -> UserResponse:
        """
        Convert User entity to UserResponse schema.

        Args:
            entity: User domain entity

        Returns:
            UserResponse schema
        """
        return UserResponse.model_validate(
            {
                "id": self.convert_uuid_to_str(entity.id),
                "email": entity.email,
                "name": entity.name,
                "is_active": entity.is_active,
            }
        )

    def to_detail_response(self, entity: User) -> UserDetailResponse:
        """
        Convert User entity to UserDetailResponse schema.

        Args:
            entity: User domain entity

        Returns:
            UserDetailResponse schema
        """
        return UserDetailResponse.model_validate(
            {
                "id": self.convert_uuid_to_str(entity.id),
                "email": entity.email,
                "name": entity.name,
                "is_active": entity.is_active,
                "created_at": self.convert_datetime_to_iso(entity.created_at),
            }
        )

    def from_create_request(self, request: UserCreateRequest) -> User:
        """
        Convert UserCreateRequest schema to User entity.

        Args:
            request: UserCreateRequest schema

        Returns:
            User domain entity
        """
        return User(email=request.email, name=request.name)

    def to_list_response(self, entities: list[User]) -> UserListResponse:
        """
        Convert list of User entities to UserListResponse schema.

        Args:
            entities: List of User domain entities

        Returns:
            UserListResponse schema
        """
        return UserListResponse(
            users=[self.to_detail_response(entity) for entity in entities],
            total=len(entities),
        )

    def to_responses(self, entities: list[User]) -> list[UserResponse]:
        """
        Convert multiple User entities to UserResponse schemas.

        Args:
            entities: List of User domain entities

        Returns:
            List of UserResponse schemas
        """
        return [self.to_response(entity) for entity in entities]
