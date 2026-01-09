# Domain Creation Guide - Step-by-Step Tutorial

This guide provides a comprehensive, step-by-step tutorial for adding new domains to your FastAPI Clean Architecture project. Follow this process to ensure consistency and maintain architectural principles.

[![tutorial](https://img.shields.io/badge/guide-step--by--step-blue.svg)](#) [![Clean Architecture](https://img.shields.io/badge/architecture-clean%20arch-brightgreen.svg)](ARCHITECTURE.md)

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Step-by-Step Guide](#step-by-step-guide)
- [Testing Your Domain](#testing-your-domain)
- [Common Pitfalls](#common-pitfalls)
- [Examples](#examples)

## Overview

### What is a Domain?

A domain represents a bounded context in your application - a distinct area of business logic. Examples include:
- **User** - Authentication and user management
- **Product** - E-commerce product catalog
- **Order** - Order processing and management
- **Payment** - Payment processing

### Domain Structure

Each domain follows this structure:

```
src/app/domains/<domain>/
├── entities/           # Pure business objects
├── repositories/       # Repository interfaces (ABCs)
├── use_cases/          # Business logic orchestration
├── infrastructure/     # Database implementations
│   └── database/
│       ├── models.py
│       └── <domain>_repository_impl.py
├── mappers/            # Entity ↔ Model ↔ DTO transformations
├── presentation/       # API layer
│   └── v1/
│       ├── router.py
│       └── schemas.py
└── dependencies.py     # Dependency injection factories
```

## Prerequisites

Before creating a new domain, ensure you have:

- ✅ The development environment running (`make dev`)
- ✅ PostgreSQL container up (`make db-up`)
- ✅ Basic understanding of Clean Architecture principles
- ✅ Read the [Architecture Guide](ARCHITECTURE.md)

## Step-by-Step Guide

### Example: Creating a Product Domain

We'll create a complete **Product** domain with CRUD operations.

---

## Step 1: Create Domain Directory Structure

```bash
# Create the domain directory
mkdir -p src/app/domains/product/{entities,repositories,use_cases,infrastructure/database,mappers,presentation/v1}
```

---

## Step 2: Create the Entity

**File**: `src/app/domains/product/entities/product.py`

The entity is a pure business object with no framework dependencies.

```python
# src/app/domains/product/entities/product.py
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
import uuid

@dataclass
class ProductEntity:
    """
    Represents a product in the system.

    Business Rules:
    - Name must be at least 3 characters
    - Price must be positive
    - SKU must be unique (enforced by repository)
    """
    id: Optional[uuid.UUID]
    name: str
    description: str
    price: Decimal
    sku: str
    stock_quantity: int
    is_active: bool

    def __post_init__(self):
        """Validate business rules."""
        if len(self.name) < 3:
            raise ValueError("Product name must be at least 3 characters")

        if self.price <= 0:
            raise ValueError("Product price must be positive")

        if self.stock_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")

    def is_in_stock(self) -> bool:
        """Check if product is in stock."""
        return self.stock_quantity > 0

    def decrease_stock(self, quantity: int) -> None:
        """Decrease stock quantity."""
        if quantity > self.stock_quantity:
            raise ValueError("Insufficient stock")
        self.stock_quantity -= quantity

    def increase_stock(self, quantity: int) -> None:
        """Increase stock quantity."""
        if quantity < 0:
            raise ValueError("Quantity must be positive")
        self.stock_quantity += quantity
```

**File**: `src/app/domains/product/entities/__init__.py`

```python
# src/app/domains/product/entities/__init__.py
from app.domains.product.entities.product import ProductEntity

__all__ = ["ProductEntity"]
```

---

## Step 3: Create Repository Interface

**File**: `src/app/domains/product/repositories/product_repository.py`

Define the contract for data access without implementation details.

```python
# src/app/domains/product/repositories/product_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
import uuid

from app.domains.product.entities import ProductEntity

class ProductRepositoryInterface(ABC):
    """
    Repository interface for Product entities.

    This interface defines the contract for product data access.
    Implementations must not contain business logic.
    """

    @abstractmethod
    async def create(self, product: ProductEntity) -> ProductEntity:
        """Create a new product."""
        pass

    @abstractmethod
    async def get_by_id(self, product_id: uuid.UUID) -> Optional[ProductEntity]:
        """Get a product by ID."""
        pass

    @abstractmethod
    async def get_by_sku(self, sku: str) -> Optional[ProductEntity]:
        """Get a product by SKU."""
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> List[ProductEntity]:
        """List all products with pagination."""
        pass

    @abstractmethod
    async def update(self, product: ProductEntity) -> ProductEntity:
        """Update an existing product."""
        pass

    @abstractmethod
    async def delete(self, product_id: uuid.UUID) -> None:
        """Delete a product by ID."""
        pass
```

**File**: `src/app/domains/product/repositories/__init__.py`

```python
# src/app/domains/product/repositories/__init__.py
from app.domains.product.repositories.product_repository import ProductRepositoryInterface

__all__ = ["ProductRepositoryInterface"]
```

---

## Step 4: Create Use Cases

**File**: `src/app/domains/product/use_cases/create_product.py`

```python
# src/app/domains/product/use_cases/create_product.py
from dataclasses import dataclass
from typing import Optional
import uuid

from app.domains.product.entities import ProductEntity
from app.domains.product.repositories import ProductRepositoryInterface
from app.core.errors import ResourceConflictError, DomainError

@dataclass
class CreateProductInput:
    """Input data for creating a product."""
    name: str
    description: str
    price: float
    sku: str
    stock_quantity: int = 0
    is_active: bool = True

@dataclass
class CreateProductOutput:
    """Output data after creating a product."""
    id: uuid.UUID
    name: str
    description: str
    price: float
    sku: str
    stock_quantity: int
    is_active: bool

class CreateProductUseCase:
    """Use case for creating a new product."""

    def __init__(
        self,
        repository: ProductRepositoryInterface,
        # Add mappers later
    ):
        self.repository = repository

    async def execute(self, input_data: CreateProductInput) -> CreateProductOutput:
        """
        Execute the create product use case.

        Business Logic:
        1. Validate SKU uniqueness
        2. Create product entity
        3. Persist through repository
        4. Return output DTO
        """
        # 1. Check if SKU already exists
        existing = await self.repository.get_by_sku(input_data.sku)
        if existing:
            raise ResourceConflictError(
                f"Product with SKU {input_data.sku} already exists",
                code="PRODUCT_SKU_EXISTS",
                details={"sku": input_data.sku},
            )

        # 2. Create entity (business rules validated in __post_init__)
        product = ProductEntity(
            id=None,
            name=input_data.name,
            description=input_data.description,
            price=input_data.price,
            sku=input_data.sku,
            stock_quantity=input_data.stock_quantity,
            is_active=input_data.is_active,
        )

        # 3. Persist
        created_product = await self.repository.create(product)

        # 4. Return output (simplified - use mapper in real implementation)
        return CreateProductOutput(
            id=created_product.id,
            name=created_product.name,
            description=created_product.description,
            price=float(created_product.price),
            sku=created_product.sku,
            stock_quantity=created_product.stock_quantity,
            is_active=created_product.is_active,
        )
```

**File**: `src/app/domains/product/use_cases/get_product.py`

```python
# src/app/domains/product/use_cases/get_product.py
from dataclasses import dataclass
from typing import Optional
import uuid

from app.domains.product.entities import ProductEntity
from app.domains.product.repositories import ProductRepositoryInterface
from app.core.errors import ResourceNotFoundError

@dataclass
class GetProductOutput:
    """Output data for getting a product."""
    id: uuid.UUID
    name: str
    description: str
    price: float
    sku: str
    stock_quantity: int
    is_active: bool

class GetProductUseCase:
    """Use case for retrieving a product by ID."""

    def __init__(self, repository: ProductRepositoryInterface):
        self.repository = repository

    async def execute(self, product_id: uuid.UUID) -> GetProductOutput:
        """Execute the get product use case."""
        product = await self.repository.get_by_id(product_id)

        if not product:
            raise ResourceNotFoundError(
                f"Product with ID {product_id} not found",
                code="PRODUCT_NOT_FOUND",
                details={"product_id": str(product_id)},
            )

        return GetProductOutput(
            id=product.id,
            name=product.name,
            description=product.description,
            price=float(product.price),
            sku=product.sku,
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
        )
```

**File**: `src/app/domains/product/use_cases/__init__.py`

```python
# src/app/domains/product/use_cases/__init__.py
from app.domains.product.use_cases.create_product import (
    CreateProductUseCase,
    CreateProductInput,
    CreateProductOutput,
)
from app.domains.product.use_cases.get_product import (
    GetProductUseCase,
    GetProductOutput,
)

__all__ = [
    "CreateProductUseCase",
    "CreateProductInput",
    "CreateProductOutput",
    "GetProductUseCase",
    "GetProductOutput",
]
```

---

## Step 5: Create Infrastructure Model

**File**: `src/app/domains/product/infrastructure/database/models.py`

```python
# src/app/domains/product/infrastructure/database/models.py
from sqlalchemy import Column, String, Numeric, Boolean, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ProductModel(Base):
    """SQLAlchemy model for products table."""

    __tablename__ = "products"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Numeric(precision=10, scale=2), nullable=False)
    sku = Column(String, unique=True, nullable=False, index=True)
    stock_quantity = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
```

---

## Step 6: Create Repository Implementation

**File**: `src/app/domains/product/infrastructure/database/product_repository_impl.py`

```python
# src/app/domains/product/infrastructure/database/product_repository_impl.py
from typing import Optional, List
import uuid
from decimal import Decimal

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.product.entities import ProductEntity
from app.domains.product.repositories import ProductRepositoryInterface
from app.domains.product.infrastructure.database.models import ProductModel

class ProductRepositoryImpl(ProductRepositoryInterface):
    """PostgreSQL implementation of product repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, product: ProductEntity) -> ProductEntity:
        """Create a new product in the database."""
        # Generate new ID if needed
        product_id = product.id or uuid.uuid4()

        db_model = ProductModel(
            id=str(product_id),
            name=product.name,
            description=product.description,
            price=product.price,
            sku=product.sku,
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
        )

        self.session.add(db_model)
        await self.session.commit()
        await self.session.refresh(db_model)

        return self._to_entity(db_model)

    async def get_by_id(self, product_id: uuid.UUID) -> Optional[ProductEntity]:
        """Get a product by ID."""
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == str(product_id))
        )
        db_model = result.scalar_one_or_none()
        return self._to_entity(db_model) if db_model else None

    async def get_by_sku(self, sku: str) -> Optional[ProductEntity]:
        """Get a product by SKU."""
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.sku == sku)
        )
        db_model = result.scalar_one_or_none()
        return self._to_entity(db_model) if db_model else None

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> List[ProductEntity]:
        """List all products with pagination."""
        query = select(ProductModel)

        if active_only:
            query = query.where(ProductModel.is_active == True)

        query = query.offset(skip).limit(limit)
        query = query.order_by(ProductModel.name)

        result = await self.session.execute(query)
        db_models = result.scalars().all()

        return [self._to_entity(model) for model in db_models]

    async def update(self, product: ProductEntity) -> ProductEntity:
        """Update an existing product."""
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == str(product.id))
        )
        db_model = result.scalar_one_or_none()

        if db_model:
            db_model.name = product.name
            db_model.description = product.description
            db_model.price = product.price
            db_model.sku = product.sku
            db_model.stock_quantity = product.stock_quantity
            db_model.is_active = product.is_active

            await self.session.commit()
            await self.session.refresh(db_model)

            return self._to_entity(db_model)

        return None

    async def delete(self, product_id: uuid.UUID) -> None:
        """Delete a product by ID."""
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == str(product_id))
        )
        db_model = result.scalar_one_or_none()

        if db_model:
            await self.session.delete(db_model)
            await self.session.commit()

    def _to_entity(self, model: ProductModel) -> ProductEntity:
        """Convert database model to domain entity."""
        return ProductEntity(
            id=uuid.UUID(model.id) if model.id else None,
            name=model.name,
            description=model.description,
            price=Decimal(str(model.price)),
            sku=model.sku,
            stock_quantity=model.stock_quantity,
            is_active=model.is_active,
        )
```

---

## Step 7: Create Mappers

**File**: `src/app/domains/product/mappers/entity_model_mapper.py`

```python
# src/app/domains/product/mappers/entity_model_mapper.py
from decimal import Decimal
import uuid

from app.domains.product.entities import ProductEntity
from app.domains.product.infrastructure.database.models import ProductModel

class ProductEntityModelMapper:
    """Mapper for Entity ↔ Model transformations."""

    def to_model(self, entity: ProductEntity) -> ProductModel:
        """Convert entity to database model."""
        return ProductModel(
            id=str(entity.id) if entity.id else None,
            name=entity.name,
            description=entity.description,
            price=entity.price,
            sku=entity.sku,
            stock_quantity=entity.stock_quantity,
            is_active=entity.is_active,
        )

    def to_entity(self, model: ProductModel) -> ProductEntity:
        """Convert database model to entity."""
        return ProductEntity(
            id=uuid.UUID(model.id) if model.id else None,
            name=model.name,
            description=model.description,
            price=Decimal(str(model.price)),
            sku=model.sku,
            stock_quantity=model.stock_quantity,
            is_active=model.is_active,
        )
```

**File**: `src/app/domains/product/mappers/__init__.py`

```python
# src/app/domains/product/mappers/__init__.py
from app.domains.product.mappers.entity_model_mapper import ProductEntityModelMapper

__all__ = ["ProductEntityModelMapper"]
```

---

## Step 8: Create Presentation Schemas

**File**: `src/app/domains/product/presentation/v1/schemas.py`

```python
# src/app/domains/product/presentation/v1/schemas.py
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
import uuid

class CreateProductSchema(BaseModel):
    """Request schema for creating a product."""
    name: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    price: Decimal = Field(..., gt=0)
    sku: str = Field(..., min_length=3, max_length=50)
    stock_quantity: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)

    @field_validator("sku")
    @classmethod
    def sku_must_be_alphanumeric(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("SKU must contain only alphanumeric characters, hyphens, and underscores")
        return v.upper()

class ProductResponseSchema(BaseModel):
    """Response schema for a product."""
    id: uuid.UUID
    name: str
    description: str
    price: Decimal
    sku: str
    stock_quantity: int
    is_active: bool

    class Config:
        from_attributes = True

class ProductListSchema(BaseModel):
    """Response schema for product list."""
    products: list[ProductResponseSchema]
    total: int
    skip: int
    limit: int
```

---

## Step 9: Create Router

**File**: `src/app/domains/product/presentation/v1/router.py`

```python
# src/app/domains/product/presentation/v1/router.py
from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from app.domains.product.use_cases import (
    CreateProductUseCase,
    CreateProductInput,
    CreateProductOutput,
    GetProductUseCase,
    GetProductOutput,
)
from app.domains.product.presentation.v1.schemas import (
    CreateProductSchema,
    ProductResponseSchema,
    ProductListSchema,
)
from app.core.errors import ResourceNotFoundError, ResourceConflictError

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductResponseSchema, status_code=201)
async def create_product(
    input_data: CreateProductSchema,
    use_case: CreateProductUseCase = Depends(get_create_product_use_case),
):
    """
    Create a new product.

    - **name**: Product name (3-200 characters)
    - **description**: Product description (10-2000 characters)
    - **price**: Product price (must be positive)
    - **sku**: Product SKU (unique identifier)
    - **stock_quantity**: Initial stock quantity (default: 0)
    - **is_active**: Whether the product is active (default: true)
    """
    try:
        use_case_input = CreateProductInput(
            name=input_data.name,
            description=input_data.description,
            price=float(input_data.price),
            sku=input_data.sku,
            stock_quantity=input_data.stock_quantity,
            is_active=input_data.is_active,
        )
        output = await use_case.execute(use_case_input)
        return ProductResponseSchema(
            id=output.id,
            name=output.name,
            description=output.description,
            price=output.price,
            sku=output.sku,
            stock_quantity=output.stock_quantity,
            is_active=output.is_active,
        )
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/{product_id}", response_model=ProductResponseSchema)
async def get_product(
    product_id: uuid.UUID,
    use_case: GetProductUseCase = Depends(get_get_product_use_case),
):
    """
    Get a product by ID.

    - **product_id**: UUID of the product
    """
    try:
        output = await use_case.execute(product_id)
        return ProductResponseSchema(
            id=output.id,
            name=output.name,
            description=output.description,
            price=output.price,
            sku=output.sku,
            stock_quantity=output.stock_quantity,
            is_active=output.is_active,
        )
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
```

---

## Step 10: Create Dependencies

**File**: `src/app/domains/product/dependencies.py`

```python
# src/app/domains/product/dependencies.py
from fastapi import Depends

from app.core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.product.infrastructure.database import ProductRepositoryImpl
from app.domains.product.mappers import ProductEntityModelMapper
from app.domains.product.use_cases import CreateProductUseCase, GetProductUseCase

# Mapper factory
def get_product_entity_model_mapper() -> ProductEntityModelMapper:
    """Provide product entity-model mapper."""
    return ProductEntityModelMapper()

# Repository factory
def get_product_repository(
    session: AsyncSession = Depends(get_db_session),
    mapper: ProductEntityModelMapper = Depends(get_product_entity_model_mapper),
) -> ProductRepositoryImpl:
    """Provide product repository."""
    return ProductRepositoryImpl(session)

# Use case factories
def get_create_product_use_case(
    repository: ProductRepositoryImpl = Depends(get_product_repository),
) -> CreateProductUseCase:
    """Provide create product use case."""
    return CreateProductUseCase(repository)

def get_get_product_use_case(
    repository: ProductRepositoryImpl = Depends(get_product_repository),
) -> GetProductUseCase:
    """Provide get product use case."""
    return GetProductUseCase(repository)
```

**File**: `src/app/domains/product/__init__.py`

```python
# src/app/domains/product/__init__.py
# This file can be empty or contain domain-level exports
```

---

## Step 11: Import Model in Alembic

**File**: `alembic/env.py`

Add the model import for autogenerate to detect it:

```python
# alembic/env.py
# ... existing imports ...

# Import all domain models for autogenerate
from app.domains.user.infrastructure.database.models import UserModel  # noqa
from app.domains.product.infrastructure.database.models import ProductModel  # noqa: E401

# ... rest of file ...
```

---

## Step 12: Create Migration

```bash
# Create migration
make migrate-new MSG="add products table"

# Apply migration
make migrate-up
```

---

## Step 13: Register Router

**File**: `src/app/main.py`

```python
# src/app/main.py
from fastapi import FastAPI
from app.core.config import get_settings
from app.domains.user.presentation.v1.router import router as user_router
from app.domains.product.presentation.v1.router import router as product_router  # New

settings = get_settings()

app = FastAPI(
    title="FastAPI Clean Architecture",
    description="Production-ready Clean Architecture implementation",
)

# Register routers
app.include_router(user_router, prefix=settings.API_V1_PREFIX)
app.include_router(product_router, prefix=settings.API_V1_PREFIX)  # New
```

---

## Step 14: Test Your Domain

### Manual Testing

```bash
# Start the server
make dev

# Test creating a product
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "description": "This is a test product description",
    "price": 29.99,
    "sku": "TEST-001",
    "stock_quantity": 100
  }'

# Test getting the product
curl "http://localhost:8000/api/v1/products/{product_id}"
```

### Unit Testing

```python
# tests/unit/product/test_create_product_use_case.py
from unittest.mock import Mock
import pytest
from app.domains.product.use_cases import CreateProductUseCase, CreateProductInput

@pytest.mark.asyncio
async def test_create_product_success():
    # Arrange
    mock_repo = Mock()
    mock_repo.get_by_sku.return_value = None
    mock_repo.create.return_value = Mock(
        id="mock-uuid",
        name="Test Product",
        description="Test description",
        price=29.99,
        sku="TEST-001",
        stock_quantity=100,
        is_active=True,
    )

    use_case = CreateProductUseCase(mock_repo)
    input_data = CreateProductInput(
        name="Test Product",
        description="Test description",
        price=29.99,
        sku="TEST-001",
        stock_quantity=100,
    )

    # Act
    result = await use_case.execute(input_data)

    # Assert
    assert result.name == "Test Product"
    mock_repo.create.assert_called_once()
```

---

## Common Pitfalls

### ❌ Importing from Wrong Layer

```python
# WRONG: Domain importing from Infrastructure
# src/app/domains/product/entities/product.py
from sqlalchemy import Column  # ❌ Don't do this!

# CORRECT: Domain has no framework imports
# src/app/domains/product/entities/product.py
from dataclasses import dataclass  # ✅ Standard library only
```

### ❌ Business Logic in Wrong Layer

```python
# WRONG: Business logic in repository
# src/app/domains/product/infrastructure/database/product_repository_impl.py
async def create(self, product: ProductEntity):
    if len(product.name) < 3:  # ❌ Business rule in infrastructure!
        raise ValueError("Name too short")
    # ...

# CORRECT: Business logic in entity
# src/app/domains/product/entities/product.py
def __post_init__(self):
    if len(self.name) < 3:  # ✅ Business rule in domain!
        raise ValueError("Name too short")
```

### ❌ Direct Instantiation in Routes

```python
# WRONG: Direct use case instantiation
# src/app/domains/product/presentation/v1/router.py
@router.post("/")
async def create_product(input_data: CreateProductSchema):
    use_case = CreateProductUseCase(...)  # ❌ Don't do this!
    return await use_case.execute(...)

# CORRECT: Use dependency injection
# src/app/domains/product/presentation/v1/router.py
@router.post("/")
async def create_product(
    input_data: CreateProductSchema,
    use_case: CreateProductUseCase = Depends(get_create_product_use_case),  # ✅
):
    return await use_case.execute(...)
```

### ❌ Missing Model Import in Alembic

If you forget to import your model in `alembic/env.py`, autogenerate won't create a migration for your new table.

---

## Quick Reference Checklist

Use this checklist when creating new domains:

- [ ] Create directory structure
- [ ] Create entity with business rules
- [ ] Create repository interface (ABC)
- [ ] Create use cases with input/output DTOs
- [ ] Create SQLAlchemy model
- [ ] Create repository implementation
- [ ] Create mappers (entity ↔ model)
- [ ] Create Pydantic schemas
- [ ] Create FastAPI router
- [ ] Create dependency injection factories
- [ ] Import model in `alembic/env.py`
- [ ] Create and apply migration
- [ ] Register router in `main.py`
- [ ] Write tests
- [ ] Update documentation

---

## Next Steps

- Add more use cases (update, delete, list)
- Implement advanced queries (search, filtering)
- Add caching layer
- Implement event sourcing
- Add background tasks for stock management

For more architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md).

*Keywords: FastAPI clean architecture, Clean architecture Python tutorial, Domain creation FastAPI, FastAPI project structure, FastAPI best practices, Clean Architecture step by step, Python DDD tutorial, FastAPI use case pattern*
