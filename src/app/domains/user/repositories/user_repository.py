"""
User Repository Interface (Port).

This defines the contract for user data access.
The actual implementation is in the infrastructure layer.
This follows the Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.domains.user.entities.user import User


class UserRepositoryInterface(ABC):
    """
    Abstract base class defining the User repository interface.
    
    This is a "port" in hexagonal architecture terms.
    Concrete implementations (adapters) will be in the infrastructure layer.
    """
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Create a new user.
        
        Args:
            user: User entity to create.
            
        Returns:
            Created user entity.
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Get a user by their ID.
        
        Args:
            user_id: The user's UUID.
            
        Returns:
            User entity if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """
        Get a user by their email.
        
        Args:
            email: The user's email address.
            
        Returns:
            User entity if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            List of user entities.
        """
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Update an existing user.
        
        Args:
            user: User entity with updated data.
            
        Returns:
            Updated user entity.
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """
        Delete a user by their ID.
        
        Args:
            user_id: The user's UUID.
            
        Returns:
            True if deleted, False if not found.
        """
        pass
