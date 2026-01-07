"""
User Entity - Pure business object.

This is the core domain entity that represents a User in our system.
It contains only business logic and has NO dependencies on external frameworks.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.core.errors import ValidationError as DomainValidationError


@dataclass
class User:
    """
    User entity representing a user in the system.

    This is a pure domain object with no framework dependencies.
    All business rules and validations related to User should be here.
    """

    email: str
    name: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate entity after initialization."""
        self._validate_email()
        self._validate_name()

    def _validate_email(self) -> None:
        """Validate email format."""
        if not self.email or "@" not in self.email:
            raise DomainValidationError(
                "Invalid email format",
                code="INVALID_EMAIL_FORMAT",
                details={"email": self.email},
            )

    def _validate_name(self) -> None:
        """Validate name is not empty."""
        if not self.name or len(self.name.strip()) == 0:
            raise DomainValidationError(
                "Name cannot be empty",
                code="INVALID_NAME_FORMAT",
                details={"name": self.name},
            )

    def deactivate(self) -> None:
        """Deactivate the user."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        """Activate the user."""
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def update_name(self, new_name: str) -> None:
        """Update user's name."""
        if not new_name or len(new_name.strip()) == 0:
            raise DomainValidationError(
                "Name cannot be empty",
                code="INVALID_NAME_FORMAT",
                details={"name": new_name},
            )
        self.name = new_name.strip()
        self.updated_at = datetime.now(UTC)
