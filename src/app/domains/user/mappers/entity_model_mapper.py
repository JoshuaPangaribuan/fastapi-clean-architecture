"""Mapper for User Entity ↔ UserModel conversions."""

from app.domains.user.entities.user import User
from app.domains.user.infrastructure.database.models import UserModel
from app.domains.user.mappers.base_mapper import BaseMapper


class UserEntityModelMapper(BaseMapper):
    """Mapper for converting between User entity and UserModel."""

    def to_entity(self, model: UserModel) -> User:
        """
        Convert SQLAlchemy model to domain entity.

        Args:
            model: SQLAlchemy UserModel instance

        Returns:
            User domain entity
        """
        return User(
            id=self.convert_str_to_uuid(model.id),
            email=model.email,
            name=model.name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: User) -> UserModel:
        """
        Convert domain entity to SQLAlchemy model.

        Args:
            entity: User domain entity

        Returns:
            SQLAlchemy UserModel instance
        """
        return UserModel(
            id=self.convert_uuid_to_str(entity.id),
            email=entity.email,
            name=entity.name,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def to_entities(self, models: list[UserModel]) -> list[User]:
        """
        Convert multiple SQLAlchemy models to domain entities.

        Args:
            models: List of UserModel instances

        Returns:
            List of User domain entities
        """
        return [self.to_entity(model) for model in models]

    def to_models(self, entities: list[User]) -> list[UserModel]:
        """
        Convert multiple domain entities to SQLAlchemy models.

        Args:
            entities: List of User entities

        Returns:
            List of UserModel instances
        """
        return [self.to_model(entity) for entity in entities]
