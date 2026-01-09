# FastAPI Clean Architecture - Complete Technical Guide

This document provides a comprehensive technical deep-dive into the Clean Architecture implementation for FastAPI. It covers layer separation, dependency inversion, mapper patterns, and production-ready patterns for building scalable Python web applications.

[![architecture](https://img.shields.io/badge/architecture-clean%20arch-brightgreen.svg)](#) [![DDD](https://img.shields.io/badge/design-DDD-orange.svg)](#)

## Table of Contents

- [Introduction](#introduction)
- [Core Principles](#core-principles)
- [Layer Architecture](#layer-architecture)
- [Dependency Inversion](#dependency-inversion)
- [Mapper System](#mapper-system)
- [Dependency Injection](#dependency-injection)
- [Error Handling](#error-handling)
- [Validation](#validation)
- [Logging](#logging)
- [Database Integration](#database-integration)
- [API Structure](#api-structure)

## Introduction

### What is Clean Architecture?

Clean Architecture is a software design philosophy that separates the code into layers with strict dependency rules. The core principle is **dependency inversion**: dependencies always point inward toward the domain.

### Why Clean Architecture for FastAPI?

**Traditional FastAPI** challenges:
- Business logic mixed with route handlers
- Direct database access throughout the application
- Tight coupling between components
- Difficult to test without database
- Business rules scattered across files

**Clean Architecture FastAPI** benefits:
- Business logic isolated in use cases
- Database access abstracted through repositories
- Loose coupling via interfaces
- Easy to test with mock dependencies
- Clear separation of concerns

### This Implementation

This project demonstrates production-ready Clean Architecture with:
- Pure domain layer with entities and repository interfaces
- Use case orchestration layer for business logic
- Infrastructure adapters implementing domain interfaces
- Presentation layer with FastAPI routers and schemas
- Three-level mapper system for data transformation
- Complex dependency injection for loose coupling

## Core Principles

### 1. Dependency Rule

**Dependencies only point inward.**

```
┌──────────────────────────────────────────┐
│            Presentation Layer            │  ← FastAPI, Schemas
│  (Can import from all inner layers)      │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────▼───────────────────────┐
│            Use Case Layer                │  ← Business Logic
│     (Can import from Domain only)        │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────▼───────────────────────┐      ┌─────────────────────┐
│            Domain Layer                  │◄─────│  Infrastructure     │
│     (Cannot import from any layer)       │      │  (Implements Domain)│
│  ┌─────────────────────────────────┐    │      │  ┌───────────────┐  │
│  │  Entities (Business Objects)    │    │      │  │  SQLAlchemy    │  │
│  │  Repository Interfaces (ABCs)   │    │      │  │  Models        │  │
│  └─────────────────────────────────┘    │      │  │  Repositories  │  │
└──────────────────────────────────────────┘      │  └───────────────┘  │
                                                   └─────────────────────┘
```

### 2. Domain Independence

The domain layer has **zero dependencies** on:
- FastAPI
- SQLAlchemy
- Pydantic
- Any other framework or library

This makes the domain:
- Testable without frameworks
- Reusable across different presentations
- Focused on business logic only

### 3. Use Case Orchestration

Use cases orchestrate business logic by:
1. Receiving input from presentation layer
2. Validating business rules
3. Coordinating repository operations
4. Returning output to presentation layer

### 4. Interface Segregation

Repository interfaces define contracts:
- Domain defines what it needs
- Infrastructure implements the contract
- Presentation depends on the interface, not implementation

## Layer Architecture

### Domain Layer

**Location**: `src/app/domains/<domain>/entities/`, `repositories/`

**Purpose**: Pure business objects and contracts

**Components**:

1. **Entities** (`entities/`)
   - Pure dataclasses with business rules
   - No framework dependencies
   - Domain logic only

   ```python
   # src/app/domains/user/entities/user.py
   from dataclasses import dataclass
   from typing import Optional
   import uuid

   @dataclass
   class UserEntity:
       id: Optional[uuid.UUID]
       email: str
       name: str

       def __post_init__(self):
           # Business rule: validate email format
           if "@" not in self.email:
               raise DomainError("Invalid email format")
   ```

2. **Repository Interfaces** (`repositories/`)
   - Abstract base classes (ABCs)
   - Define data access contracts
   - No implementation details

   ```python
   # src/app/domains/user/repositories/user_repository.py
   from abc import ABC, abstractmethod
   from typing import Optional
   import uuid

   class UserRepositoryInterface(ABC):
       @abstractmethod
       async def create(self, user: UserEntity) -> UserEntity:
           pass

       @abstractmethod
       async def get_by_id(self, user_id: uuid.UUID) -> Optional[UserEntity]:
           pass

       @abstractmethod
       async def get_by_email(self, email: str) -> Optional[UserEntity]:
           pass
   ```

**Dependency Rules**:
- ❌ Cannot import from any other layer
- ✅ Can use standard library only
- ✅ Can define business rules

### Use Case Layer

**Location**: `src/app/domains/<domain>/use_cases/`

**Purpose**: Orchestrate business logic

**Components**:

- **Use Cases** - Business logic coordination classes
- Each use case has an `execute()` method
- Depends on repository interfaces, not implementations

```python
# src/app/domains/user/use_cases/create_user.py
from app.domains.user.entities import UserEntity
from app.domains.user.repositories import UserRepositoryInterface
from app.core.errors import ResourceConflictError, DomainError

class CreateUserUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        # Add mappers and other dependencies here
    ):
        self.user_repository = user_repository

    async def execute(self, input_data: CreateUserInput) -> CreateUserOutput:
        # 1. Validate business rules
        existing = await self.user_repository.get_by_email(input_data.email)
        if existing:
            raise ResourceConflictError(
                f"User with email {input_data.email} already exists",
                code="USER_EMAIL_EXISTS",
            )

        # 2. Create entity
        user = UserEntity(
            id=None,
            email=input_data.email,
            name=input_data.name,
        )

        # 3. Persist through repository
        created_user = await self.user_repository.create(user)

        # 4. Return output (via mapper)
        return self.mapper.to_dto(created_user)
```

**Dependency Rules**:
- ✅ Can import from Domain layer
- ❌ Cannot import from Infrastructure
- ❌ Cannot import from Presentation
- ✅ Must depend on interfaces, not concrete implementations

### Infrastructure Layer

**Location**: `src/app/domains/<domain>/infrastructure/`

**Purpose**: Implement domain interfaces and integrate external services

**Components**:

1. **SQLAlchemy Models** (`infrastructure/database/models.py`)
   - Database table definitions
   - ORM-specific concerns

   ```python
   # src/app/domains/user/infrastructure/database/models.py
   from sqlalchemy import Column, String
   from sqlalchemy.orm import declarative_base
   import uuid

   Base = declarative_base()

   class UserModel(Base):
       __tablename__ = "users"

       id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
       email = Column(String, unique=True, nullable=False)
       name = Column(String, nullable=False)
   ```

2. **Repository Implementations** (`infrastructure/database/<domain>_repository_impl.py`)
   - Concrete implementations of repository interfaces
   - Database access logic

   ```python
   # src/app/domains/user/infrastructure/database/user_repository_impl.py
   from app.domains.user.entities import UserEntity
   from app.domains.user.repositories import UserRepositoryInterface
   from app.domains.user.infrastructure.database.models import UserModel
   from app.domains.user.mappers import UserEntityModelMapper
   from sqlalchemy.ext.asyncio import AsyncSession
   from sqlalchemy import select
   from typing import Optional
   import uuid

   class UserRepositoryImpl(UserRepositoryInterface):
       def __init__(
           self,
           session: AsyncSession,
           mapper: UserEntityModelMapper,
       ):
           self.session = session
           self.mapper = mapper

       async def create(self, user: UserEntity) -> UserEntity:
           db_model = self.mapper.to_model(user)
           self.session.add(db_model)
           await self.session.commit()
           await self.session.refresh(db_model)
           return self.mapper.to_entity(db_model)

       async def get_by_id(self, user_id: uuid.UUID) -> Optional[UserEntity]:
           result = await self.session.execute(
               select(UserModel).where(UserModel.id == str(user_id))
           )
           db_model = result.scalar_one_or_none()
           if db_model:
               return self.mapper.to_entity(db_model)
           return None
   ```

**Dependency Rules**:
- ✅ Can import from Domain layer
- ✅ Can import from Use Case layer
- ❌ Cannot import from Presentation layer

### Presentation Layer

**Location**: `src/app/domains/<domain>/presentation/v1/`

**Purpose**: Handle HTTP requests and responses

**Components**:

1. **Schemas** (`schemas.py`) - Pydantic models for validation
2. **Routers** (`router.py`) - FastAPI route handlers

```python
# src/app/domains/user/presentation/v1/schemas.py
from pydantic import BaseModel, EmailStr
import uuid

class CreateUserSchema(BaseModel):
    email: EmailStr
    name: str

class UserResponseSchema(BaseModel):
    id: uuid.UUID
    email: str
    name: str

    class Config:
        from_attributes = True

# src/app/domains/user/presentation/v1/router.py
from fastapi import APIRouter, Depends, HTTPException
from app.domains.user.use_cases import CreateUserUseCase
from app.domains.user.presentation.v1.schemas import CreateUserSchema, UserResponseSchema

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponseSchema)
async def create_user(
    input_data: CreateUserSchema,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
):
    try:
        return await use_case.execute(input_data)
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)
```

**Dependency Rules**:
- ✅ Can import from all layers
- ✅ Prefer importing from Use Cases over direct Domain access
- ✅ Use dependency injection for use cases

## Dependency Inversion

### The Dependency Inversion Principle

**High-level modules should not depend on low-level modules. Both should depend on abstractions.**

In this implementation:

```
┌────────────────────────────────────────┐
│         Presentation Layer             │
│  Depends on Use Cases (not Domain)    │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│          Use Case Layer                │
│  Depends on Domain Interfaces         │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐      ┌──────────────────────┐
│          Domain Layer                 │◄─────│  Infrastructure      │
│    Defines Interfaces (ABCs)          │      │  Implements ABCs     │
└───────────────────────────────────────┘      └──────────────────────┘
```

### Benefits

1. **Testability**: Mock any dependency
2. **Flexibility**: Swap implementations without changing use cases
3. **Maintainability**: Changes in infrastructure don't affect business logic

### Example: Testing with Mocks

```python
# tests/unit/user/test_create_user_use_case.py
from unittest.mock import Mock
from app.domains.user.use_cases import CreateUserUseCase
from app.domains.user.entities import UserEntity

async def test_create_user_success():
    # Arrange
    mock_repo = Mock(spec=UserRepositoryInterface)
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = UserEntity(
        id=uuid.uuid4(),
        email="test@example.com",
        name="Test User",
    )

    use_case = CreateUserUseCase(mock_repo, mock_mapper)
    input_data = CreateUserInput(email="test@example.com", name="Test User")

    # Act
    result = await use_case.execute(input_data)

    # Assert
    assert result.email == "test@example.com"
    mock_repo.create.assert_called_once()
```

## Mapper System

### Three-Level Mapping

This implementation uses three levels of mapping for clean separation:

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Entity  │◄───►│  Model   │◄───►│ Database │
│ (Domain) │     │ (Infra)  │     │          │
└──────────┘     └──────────┘     └──────────┘
     │                                   │
     │ Entity → DTO                      │
     ▼                                   │
┌──────────┐                              │
│   DTO    │                              │
│ (Pres.)  │                              │
└──────────┘                              │
     │                                   │
     ▼                                   ▼
   API Response                       Database Storage
```

### 1. Entity ↔ Model Mapper

**Location**: `src/app/domains/<domain>/mappers/entity_model_mapper.py`

**Purpose**: Map between Domain entities and SQLAlchemy models

```python
# src/app/domains/user/mappers/entity_model_mapper.py
from app.domains.user.entities import UserEntity
from app.domains.user.infrastructure.database.models import UserModel
import uuid

class UserEntityModelMapper:
    def to_model(self, entity: UserEntity) -> UserModel:
        return UserModel(
            id=str(entity.id) if entity.id else None,
            email=entity.email,
            name=entity.name,
        )

    def to_entity(self, model: UserModel) -> UserEntity:
        return UserEntity(
            id=uuid.UUID(model.id) if model.id else None,
            email=model.email,
            name=model.name,
        )
```

### 2. Entity ↔ DTO Mapper

**Location**: `src/app/domains/<domain>/mappers/entity_dto_mapper.py`

**Purpose**: Map between Domain entities and API schemas

```python
# src/app/domains/user/mappers/entity_dto_mapper.py
from app.domains.user.entities import UserEntity
from app.domains.user.presentation.v1.schemas import UserResponseSchema

class UserEntityDtoMapper:
    def to_dto(self, entity: UserEntity) -> UserResponseSchema:
        return UserResponseSchema(
            id=entity.id,
            email=entity.email,
            name=entity.name,
        )

    def to_entity(self, dto: CreateUserSchema) -> UserEntity:
        return UserEntity(
            id=None,
            email=dto.email,
            name=dto.name,
        )
```

### 3. Base Mapper Utilities

**Location**: `src/app/domains/<domain>/mappers/base_mapper.py`

**Purpose**: Common mapping utilities

```python
# src/app/domains/user/mappers/base_mapper.py
from datetime import datetime
import uuid

class BaseMapper:
    @staticmethod
    def uuid_to_str(uuid_obj: uuid.UUID | None) -> str | None:
        return str(uuid_obj) if uuid_obj else None

    @staticmethod
    def str_to_uuid(uuid_str: str | None) -> uuid.UUID | None:
        return uuid.UUID(uuid_str) if uuid_str else None

    @staticmethod
    def format_datetime(dt: datetime) -> str:
        return dt.isoformat()
```

## Dependency Injection

### FastAPI Dependency Injection

FastAPI's dependency injection system is used throughout:

```python
# src/app/domains/user/dependencies.py
from fastapi import Depends
from app.core.database import get_db_session
from app.domains.user.mappers import UserEntityModelMapper, UserEntityDtoMapper
from app.domains.user.infrastructure.database import UserRepositoryImpl
from app.domains.user.use_cases import CreateUserUseCase, GetUserUseCase

# Mapper factories (singleton instances)
def get_user_entity_model_mapper() -> UserEntityModelMapper:
    return UserEntityModelMapper()

def get_user_entity_dto_mapper() -> UserEntityDtoMapper:
    return UserEntityDtoMapper()

# Repository factory
def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
    mapper: UserEntityModelMapper = Depends(get_user_entity_model_mapper),
) -> UserRepositoryImpl:
    return UserRepositoryImpl(session, mapper)

# Use case factories
def get_create_user_use_case(
    repository: UserRepositoryImpl = Depends(get_user_repository),
    dto_mapper: UserEntityDtoMapper = Depends(get_user_entity_dto_mapper),
) -> CreateUserUseCase:
    return CreateUserUseCase(repository, dto_mapper)

# Usage in router
@router.post("/")
async def create_user(
    input_data: CreateUserSchema,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
):
    return await use_case.execute(input_data)
```

### Benefits

1. **Loose Coupling**: Components depend on abstractions
2. **Testability**: Easy to inject mocks
3. **Singleton Management**: Mappers reused across requests
4. **Request Scoping**: Repositories created per request

## Error Handling

### Exception Hierarchy

**Location**: `src/app/core/errors/exceptions.py`

```python
# Base error class
class AppError(Exception):
    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code or self._generate_code()
        self.details = details or {}
        super().__init__(self.message)

    def _generate_code(self) -> str:
        # Auto-generate error code from class name
        class_name = self.__class__.__name__
        return "".join(
            "_" + c.lower() if c.isupper() else c
            for c in class_name
            if c != "Error"
        ).lstrip("_")

# Resource errors (404, 409)
class ResourceNotFoundError(AppError):
    """Raised when a resource is not found."""

class ResourceConflictError(AppError):
    """Raised when a resource already exists."""

# Business logic errors (422)
class DomainError(AppError):
    """Raised when business rules are violated."""

# Authentication/Authorization (401, 403)
class AuthenticationError(AppError):
    """Raised when authentication fails."""

class AuthorizationError(AppError):
    """Raised when authorization fails."""
```

### Global Exception Handlers

**Location**: `src/app/core/errors/handlers.py`

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse

async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request.state.request_id,
        },
    )

async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request.state.request_id,
        },
    )
```

### Usage in Use Cases

```python
async def execute(self, input_data: CreateUserInput) -> CreateUserOutput:
    # Check for existing user
    existing = await self.user_repository.get_by_email(input_data.email)
    if existing:
        raise ResourceConflictError(
            f"User with email {input_data.email} already exists",
            code="USER_EMAIL_EXISTS",
            details={"email": input_data.email},
        )

    # Validate business rules
    if len(input_data.name) < 2:
        raise DomainError(
            "Name must be at least 2 characters",
            code="NAME_TOO_SHORT",
            details={"min_length": 2},
        )
```

## Validation

### Pydantic Schemas

**Location**: `src/app/domains/<domain>/presentation/v1/schemas.py`

```python
from pydantic import BaseModel, EmailStr, Field, field_validator

class CreateUserSchema(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)

    @field_validator("name")
    @classmethod
    def name_must_not_contain_numbers(cls, v: str) -> str:
        if any(c.isdigit() for c in v):
            raise ValueError("Name must not contain numbers")
        return v
```

### Shared Validation Utilities

**Location**: `src/app/core/validation/utils.py`

```python
import uuid
from app.core.errors import DomainError

def parse_uuid(uuid_str: str, field_name: str = "ID") -> uuid.UUID:
    """Parse and validate a UUID string."""
    try:
        return uuid.UUID(uuid_str)
    except ValueError:
        raise DomainError(
            f"Invalid {field_name} format",
            code="INVALID_UUID",
            details={"field_name": field_name, "value": uuid_str},
        )
```

## Logging

### Structured Logging Configuration

**Location**: `src/app/core/logging/logging_config.py`

```python
import logging
import sys
from pathlib import Path

def setup_logging(debug: bool = False, log_file: Path = None):
    """Configure structured logging for the application."""

    log_level = logging.DEBUG if debug else logging.INFO

    # Suppress noisy logs
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Configure root logger
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )
```

### Usage in Code

```python
import logging

logger = logging.getLogger(__name__)

async def execute(self, input_data: CreateUserInput):
    logger.info(f"Creating user with email: {input_data.email}")

    try:
        result = await self.user_repository.create(user)
        logger.info(f"User created successfully: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to create user: {e}", exc_info=True)
        raise
```

## Database Integration

### Async Session Management

**Location**: `src/app/core/database/session.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db_session() -> AsyncSession:
    """Dependency for database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Migration with Alembic

**Important**: Models must be imported in `alembic/env.py` for autogenerate:

```python
# alembic/env.py
from app.domains.user.infrastructure.database.models import UserModel  # noqa
from app.domains.product.infrastructure.database.models import ProductModel  # noqa
```

## API Structure

### Router Registration

**Location**: `src/app/main.py`

```python
from fastapi import FastAPI
from app.domains.user.presentation.v1.router import router as user_router
from app.core.config import get_settings

app = FastAPI(title="FastAPI Clean Architecture")
settings = get_settings()

# Register routers
app.include_router(user_router, prefix=settings.API_V1_PREFIX)

# Note: No central presentation/api.py - routers registered directly
```

### Versioning

APIs are versioned in the presentation layer:

```
presentation/
├── v1/          # Current API version
│   ├── router.py
│   └── schemas.py
└── v2/          # Future version (when needed)
    ├── router.py
    └── schemas.py
```

## Summary

This Clean Architecture implementation provides:

✅ **Strict layer separation** - Clear boundaries between concerns
✅ **Dependency inversion** - All dependencies point toward domain
✅ **Testability** - Easy to mock and test business logic
✅ **Scalability** - Modular domain structure supports growth
✅ **Maintainability** - Consistent patterns across codebase
✅ **Production-ready** - Error handling, validation, logging included

For step-by-step domain creation, see [DOMAIN_CREATION.md](DOMAIN_CREATION.md).

*Keywords: FastAPI clean architecture, Clean architecture Python, Domain-driven design FastAPI, FastAPI project structure, Production-ready FastAPI template, Hexagonal architecture FastAPI, FastAPI best practices, Python async architecture, SQLAlchemy repository pattern, FastAPI dependency injection*
