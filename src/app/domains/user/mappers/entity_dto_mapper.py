"""Mapper for User Entity ↔ DTO conversions."""

from app.domains.user.entities.user import User
from app.domains.user.mappers.base_mapper import BaseMapper
from app.domains.user.mappers.dtos import (
    CreateUserInputDTO,
    CreateUserOutputDTO,
    GetUserOutputDTO,
)


class UserEntityDtoMapper(BaseMapper):
    """Mapper for converting between User entity and DTOs."""

    def to_create_output(self, entity: User) -> CreateUserOutputDTO:
        """
        Convert User entity to CreateUserOutputDTO.

        Args:
            entity: User domain entity

        Returns:
            CreateUserOutputDTO
        """
        return CreateUserOutputDTO(
            id=self.convert_uuid_to_str(entity.id),
            email=entity.email,
            name=entity.name,
            is_active=entity.is_active,
        )

    def to_get_output(self, entity: User) -> GetUserOutputDTO:
        """
        Convert User entity to GetUserOutputDTO.

        Args:
            entity: User domain entity

        Returns:
            GetUserOutputDTO
        """
        return GetUserOutputDTO(
            id=self.convert_uuid_to_str(entity.id),
            email=entity.email,
            name=entity.name,
            is_active=entity.is_active,
            created_at=self.convert_datetime_to_iso(entity.created_at),
        )

    def from_create_input(self, dto: CreateUserInputDTO) -> User:
        """
        Convert CreateUserInputDTO to User entity.

        Args:
            dto: CreateUserInputDTO

        Returns:
            User domain entity
        """
        return User(email=dto.email, name=dto.name)

    def to_get_outputs(self, entities: list[User]) -> list[GetUserOutputDTO]:
        """
        Convert multiple User entities to GetUserOutputDTO.

        Args:
            entities: List of User entities

        Returns:
            List of GetUserOutputDTO
        """
        return [self.to_get_output(entity) for entity in entities]
