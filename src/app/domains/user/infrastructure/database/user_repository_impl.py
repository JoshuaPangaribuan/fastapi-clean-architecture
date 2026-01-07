"""
User Repository Implementation (Adapter).

This is the concrete implementation of the UserRepositoryInterface.
It uses SQLAlchemy to interact with the database.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.entities.user import User
from app.domains.user.infrastructure.database.models import UserModel
from app.domains.user.repositories.user_repository import UserRepositoryInterface


class SQLAlchemyUserRepository(UserRepositoryInterface):
    """
    SQLAlchemy implementation of the User repository.
    
    This is an "adapter" in hexagonal architecture terms.
    It implements the port (UserRepositoryInterface) using SQLAlchemy.
    """
    
    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the repository with a database session.
        
        Args:
            db: SQLAlchemy database session.
        """
        self._db = db
    
    def _to_entity(self, model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        return User(
            id=UUID(model.id),
            email=model.email,
            name=model.name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _to_model(self, entity: User) -> UserModel:
        """Convert domain entity to SQLAlchemy model."""
        return UserModel(
            id=str(entity.id),
            email=entity.email,
            name=entity.name,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    async def create(self, user: User) -> User:
        """Create a new user in the database."""
        model = self._to_model(user)
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return self._to_entity(model)
    
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get a user by their ID."""
        query = select(UserModel).where(UserModel.id == str(user_id))
        result = await self._db.execute(query)
        model = result.scalars().first()
        
        if model is None:
            return None
        
        return self._to_entity(model)
    
    async def get_by_email(self, email: str) -> User | None:
        """Get a user by their email."""
        query = select(UserModel).where(UserModel.email == email)
        result = await self._db.execute(query)
        model = result.scalars().first()
        
        if model is None:
            return None
        
        return self._to_entity(model)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        query = select(UserModel).offset(skip).limit(limit)
        result = await self._db.execute(query)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
    
    async def update(self, user: User) -> User:
        """Update an existing user."""
        query = select(UserModel).where(UserModel.id == str(user.id))
        result = await self._db.execute(query)
        model = result.scalars().first()
        
        if model is None:
            raise ValueError(f"User with ID {user.id} not found")
        
        model.email = user.email
        model.name = user.name
        model.is_active = user.is_active
        model.updated_at = user.updated_at
        
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        
        return self._to_entity(model)
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by their ID."""
        query = select(UserModel).where(UserModel.id == str(user_id))
        result = await self._db.execute(query)
        model = result.scalars().first()
        
        if model is None:
            return False
        
        await self._db.delete(model)
        await self._db.commit()
        
        return True
