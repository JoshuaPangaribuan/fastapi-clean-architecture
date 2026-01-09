# Code Examples and Templates

This directory contains practical code examples and templates for common FastAPI Clean Architecture patterns.

[![examples](https://img.shields.io/badge/examples-code--templates-blue.svg)](#) [![Clean Architecture](https://img.shields.io/badge/architecture-clean%20arch-brightgreen.svg)](../docs/ARCHITECTURE.md)

## Table of Contents

- [Domain Templates](#domain-templates)
- [Use Case Patterns](#use-case-patterns)
- [Repository Patterns](#repository-patterns)
- [API Patterns](#api-patterns)
- [Testing Examples](#testing-examples)

---

## Domain Templates

### 1. Simple CRUD Domain

A basic domain with Create, Read, Update, Delete operations.

**Entity:**
```python
from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class ProductEntity:
    id: Optional[uuid.UUID]
    name: str
    price: float
    description: str

    def __post_init__(self):
        if len(self.name) < 3:
            raise ValueError("Name must be at least 3 characters")
        if self.price <= 0:
            raise ValueError("Price must be positive")
```

**Repository Interface:**
```python
from abc import ABC, abstractmethod
from typing import Optional, List

class ProductRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, product: ProductEntity) -> ProductEntity:
        pass

    @abstractmethod
    async def get_by_id(self, product_id: uuid.UUID) -> Optional[ProductEntity]:
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[ProductEntity]:
        pass

    @abstractmethod
    async def update(self, product: ProductEntity) -> ProductEntity:
        pass

    @abstractmethod
    async def delete(self, product_id: uuid.UUID) -> None:
        pass
```

### 2. Domain with Business Rules

A domain with complex business logic and validation.

**Entity with Methods:**
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class OrderEntity:
    id: Optional[uuid.UUID]
    user_id: uuid.UUID
    status: str
    total: float
    created_at: datetime

    # Business rules
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    def can_cancel(self) -> bool:
        """Check if order can be cancelled."""
        return self.status in [self.STATUS_PENDING, self.STATUS_PROCESSING]

    def cancel(self) -> None:
        """Cancel the order if allowed."""
        if not self.can_cancel():
            raise ValueError("Cannot cancel order in current status")
        self.status = self.STATUS_CANCELLED

    def mark_shipped(self) -> None:
        """Mark order as shipped."""
        if self.status != self.STATUS_PROCESSING:
            raise ValueError("Order must be processing before shipping")
        self.status = self.STATUS_SHIPPED
```

---

## Use Case Patterns

### 1. Create Use Case

**Basic create pattern:**
```python
from dataclasses import dataclass

@dataclass
class CreateUserInput:
    email: str
    name: str
    password: str

@dataclass
class CreateUserOutput:
    id: uuid.UUID
    email: str
    name: str

class CreateUserUseCase:
    def __init__(
        self,
        repository: UserRepositoryInterface,
        password_hasher: PasswordHasherInterface,
    ):
        self.repository = repository
        self.password_hasher = password_hasher

    async def execute(self, input_data: CreateUserInput) -> CreateUserOutput:
        # 1. Validate uniqueness
        existing = await self.repository.get_by_email(input_data.email)
        if existing:
            raise ResourceConflictError("Email already exists")

        # 2. Transform input
        hashed_password = await self.password_hasher.hash(input_data.password)

        # 3. Create entity
        user = UserEntity(
            id=None,
            email=input_data.email,
            name=input_data.name,
            hashed_password=hashed_password,
        )

        # 4. Persist
        created_user = await self.repository.create(user)

        # 5. Return output
        return CreateUserOutput(
            id=created_user.id,
            email=created_user.email,
            name=created_user.name,
        )
```

### 2. Query Use Case

**Query with parameters:**
```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class SearchProductsInput:
    query: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    skip: int = 0
    limit: int = 20

@dataclass
class SearchProductsOutput:
    products: List[ProductSummaryOutput]
    total: int
    page: int
    pages: int

class SearchProductsUseCase:
    def __init__(self, repository: ProductRepositoryInterface):
        self.repository = repository

    async def execute(self, input_data: SearchProductsInput) -> SearchProductsOutput:
        # 1. Search products
        products = await self.repository.search(
            query=input_data.query,
            category_id=input_data.category_id,
            min_price=input_data.min_price,
            max_price=input_data.max_price,
            skip=input_data.skip,
            limit=input_data.limit,
        )

        # 2. Get total count
        total = await self.repository.count(
            query=input_data.query,
            category_id=input_data.category_id,
        )

        # 3. Calculate pagination
        pages = (total + input_data.limit - 1) // input_data.limit
        page = (input_data.skip // input_data.limit) + 1

        # 4. Map to output
        return SearchProductsOutput(
            products=[self._to_summary(p) for p in products],
            total=total,
            page=page,
            pages=pages,
        )
```

### 3. Command Use Case

**Command-style use case (no output):**
```python
class SendEmailUseCase:
    def __init__(
        self,
        email_service: EmailServiceInterface,
        user_repository: UserRepositoryInterface,
    ):
        self.email_service = email_service
        self.user_repository = user_repository

    async def execute(self, user_id: uuid.UUID, subject: str, body: str) -> None:
        # 1. Get user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User not found")

        # 2. Send email
        await self.email_service.send(
            to=user.email,
            subject=subject,
            body=body,
        )

        # No output needed - just side effects
```

### 4. Composite Use Case

**Use case that coordinates multiple use cases:**
```python
class CreateOrderUseCase:
    """Composite use case that orchestrates multiple operations."""

    def __init__(
        self,
        order_repository: OrderRepositoryInterface,
        product_repository: ProductRepositoryInterface,
        payment_service: PaymentServiceInterface,
        inventory_service: InventoryServiceInterface,
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.payment_service = payment_service
        self.inventory_service = inventory_service

    async def execute(self, input_data: CreateOrderInput) -> CreateOrderOutput:
        # 1. Validate products exist
        for item in input_data.items:
            product = await self.product_repository.get_by_id(item.product_id)
            if not product:
                raise ResourceNotFoundError(f"Product {item.product_id} not found")

        # 2. Check inventory
        await self.inventory_service.check_availability(input_data.items)

        # 3. Calculate total
        total = await self._calculate_total(input_data.items)

        # 4. Create order
        order = OrderEntity(
            id=None,
            user_id=input_data.user_id,
            status=OrderEntity.STATUS_PENDING,
            total=total,
            created_at=datetime.utcnow(),
        )

        # 5. Process payment
        payment_result = await self.payment_service.charge(
            amount=total,
            payment_method=input_data.payment_method,
        )

        if not payment_result.success:
            raise DomainError("Payment failed")

        # 6. Reserve inventory
        await self.inventory_service.reserve(input_data.items)

        # 7. Save order
        created_order = await self.order_repository.create(order)

        # 8. Mark as processing
        created_order.status = OrderEntity.STATUS_PROCESSING
        await self.order_repository.update(created_order)

        return CreateOrderOutput.from_entity(created_order)
```

---

## Repository Patterns

### 1. Basic CRUD Repository

```python
class ProductRepositoryImpl(ProductRepositoryInterface):
    def __init__(self, session: AsyncSession, mapper: ProductEntityModelMapper):
        self.session = session
        self.mapper = mapper

    async def create(self, product: ProductEntity) -> ProductEntity:
        db_model = self.mapper.to_model(product)
        self.session.add(db_model)
        await self.session.commit()
        await self.session.refresh(db_model)
        return self.mapper.to_entity(db_model)

    async def get_by_id(self, product_id: uuid.UUID) -> Optional[ProductEntity]:
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == str(product_id))
        )
        db_model = result.scalar_one_or_none()
        return self.mapper.to_entity(db_model) if db_model else None

    async def update(self, product: ProductEntity) -> ProductEntity:
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == str(product.id))
        )
        db_model = result.scalar_one_or_none()

        if db_model:
            db_model.name = product.name
            db_model.price = product.price
            db_model.description = product.description

            await self.session.commit()
            await self.session.refresh(db_model)
            return self.mapper.to_entity(db_model)

        return None

    async def delete(self, product_id: uuid.UUID) -> None:
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == str(product_id))
        )
        db_model = result.scalar_one_or_none()

        if db_model:
            await self.session.delete(db_model)
            await self.session.commit()
```

### 2. Search Repository

```python
from sqlalchemy import or_, and_

class ProductRepositoryImpl(ProductRepositoryInterface):
    async def search(
        self,
        query: Optional[str] = None,
        category_id: Optional[uuid.UUID] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[ProductEntity]:
        """Search products with multiple filters."""
        q = select(ProductModel)

        # Apply filters
        conditions = []

        if query:
            conditions.append(
                or_(
                    ProductModel.name.ilike(f"%{query}%"),
                    ProductModel.description.ilike(f"%{query}%"),
                )
            )

        if category_id:
            conditions.append(ProductModel.category_id == str(category_id))

        if min_price is not None:
            conditions.append(ProductModel.price >= min_price)

        if max_price is not None:
            conditions.append(ProductModel.price <= max_price)

        if conditions:
            q = q.where(and_(*conditions))

        # Apply pagination
        q = q.offset(skip).limit(limit)
        q = q.order_by(ProductModel.name)

        # Execute query
        result = await self.session.execute(q)
        db_models = result.scalars().all()

        return [self.mapper.to_entity(m) for m in db_models]
```

---

## API Patterns

### 1. RESTful CRUD Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductResponseSchema, status_code=201)
async def create_product(
    input_data: CreateProductSchema,
    use_case: CreateProductUseCase = Depends(get_create_product_use_case),
):
    """Create a new product."""
    try:
        return await use_case.execute(input_data)
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)

@router.get("/", response_model=ProductListSchema)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    use_case: ListProductsUseCase = Depends(get_list_products_use_case),
):
    """List all products with pagination."""
    input_data = ListProductsInput(skip=skip, limit=limit)
    return await use_case.execute(input_data)

@router.get("/{product_id}", response_model=ProductResponseSchema)
async def get_product(
    product_id: uuid.UUID,
    use_case: GetProductUseCase = Depends(get_get_product_use_case),
):
    """Get a product by ID."""
    try:
        return await use_case.execute(product_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)

@router.patch("/{product_id}", response_model=ProductResponseSchema)
async def update_product(
    product_id: uuid.UUID,
    input_data: UpdateProductSchema,
    use_case: UpdateProductUseCase = Depends(get_update_product_use_case),
):
    """Update a product."""
    try:
        update_input = UpdateProductInput(
            product_id=product_id,
            **input_data.dict(exclude_unset=True),
        )
        return await use_case.execute(update_input)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)

@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: uuid.UUID,
    use_case: DeleteProductUseCase = Depends(get_delete_product_use_case),
):
    """Delete a product."""
    try:
        await use_case.execute(product_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
```

### 2. Nested Resource Endpoints

```python
@router.get("/{product_id}/reviews", response_model=ReviewListSchema)
async def list_product_reviews(
    product_id: uuid.UUID,
    use_case: ListProductReviewsUseCase = Depends(get_list_product_reviews_use_case),
):
    """List all reviews for a product."""
    input_data = ListProductReviewsInput(product_id=product_id)
    return await use_case.execute(input_data)

@router.post("/{product_id}/reviews", response_model=ReviewResponseSchema, status_code=201)
async def create_product_review(
    product_id: uuid.UUID,
    input_data: CreateReviewSchema,
    use_case: CreateReviewUseCase = Depends(get_create_review_use_case),
):
    """Create a review for a product."""
    review_input = CreateReviewInput(
        product_id=product_id,
        **input_data.dict(),
    )
    return await use_case.execute(review_input)
```

### 3. Bulk Operations

```python
@router.post("/bulk", response_model=ProductListSchema)
async def bulk_create_products(
    input_data: List[CreateProductSchema],
    use_case: BulkCreateProductsUseCase = Depends(get_bulk_create_products_use_case),
):
    """Create multiple products at once."""
    bulk_input = BulkCreateProductsInput(products=input_data)
    return await use_case.execute(bulk_input)

@router.patch("/bulk", response_model=ProductListSchema)
async def bulk_update_products(
    input_data: BulkUpdateProductsSchema,
    use_case: BulkUpdateProductsUseCase = Depends(get_bulk_update_products_use_case),
):
    """Update multiple products at once."""
    return await use_case.execute(input_data)
```

---

## Testing Examples

### 1. Unit Test for Use Case

```python
import pytest
from unittest.mock import Mock, AsyncMock
from app.domains.product.use_cases import CreateProductUseCase, CreateProductInput
from app.core.errors import ResourceConflictError

@pytest.mark.asyncio
async def test_create_product_success():
    # Arrange
    mock_repo = Mock()
    mock_repo.get_by_sku = AsyncMock(return_value=None)
    mock_repo.create = AsyncMock(return_value=Mock(
        id="test-uuid",
        name="Test Product",
        description="Test description",
        price=29.99,
        sku="TEST-001",
        stock_quantity=100,
        is_active=True,
    ))

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
    assert result.price == 29.99
    mock_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_product_duplicate_sku():
    # Arrange
    mock_repo = Mock()
    mock_repo.get_by_sku = AsyncMock(return_value=Mock(id="existing"))

    use_case = CreateProductUseCase(mock_repo)
    input_data = CreateProductInput(
        name="Test Product",
        description="Test description",
        price=29.99,
        sku="TEST-001",
    )

    # Act & Assert
    with pytest.raises(ResourceConflictError):
        await use_case.execute(input_data)
```

### 2. Integration Test for API

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_product_endpoint():
    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Test Product",
            "description": "Test description",
            "price": 29.99,
            "sku": "TEST-001",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["sku"] == "TEST-001"
    assert "id" in data

def test_get_product_endpoint():
    # First create a product
    create_response = client.post(
        "/api/v1/products/",
        json={
            "name": "Test Product",
            "description": "Test description",
            "price": 29.99,
            "sku": "TEST-001",
        },
    )
    product_id = create_response.json()["id"]

    # Then get it
    response = client.get(f"/api/v1/products/{product_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Product"
```

### 3. Repository Test with Database

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture
async def test_db_session():
    """Create test database session."""
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_db")
    async_session_maker = sessionmaker(engine, class_=AsyncSession)

    async with async_session_maker() as session:
        yield session
        await session.rollback()

@pytest.mark.asyncio
async def test_repository_create_product(test_db_session):
    repo = ProductRepositoryImpl(test_db_session, ProductEntityModelMapper())

    product = ProductEntity(
        id=None,
        name="Test Product",
        description="Test description",
        price=29.99,
        sku="TEST-001",
        stock_quantity=100,
        is_active=True,
    )

    created = await repo.create(product)

    assert created.id is not None
    assert created.name == "Test Product"
    assert created.sku == "TEST-001"
```

---

## Advanced Patterns

### 1. Event-Driven Use Case

```python
class CreateOrderUseCase:
    def __init__(
        self,
        order_repository: OrderRepositoryInterface,
        event_publisher: EventPublisherInterface,
    ):
        self.order_repository = order_repository
        self.event_publisher = event_publisher

    async def execute(self, input_data: CreateOrderInput) -> CreateOrderOutput:
        # Create order
        order = await self.order_repository.create(OrderEntity(...))

        # Publish event
        await self.event_publisher.publish(
            OrderCreatedEvent(
                order_id=order.id,
                user_id=order.user_id,
                total=order.total,
            )
        )

        return CreateOrderOutput.from_entity(order)
```

### 2. Caching Use Case

```python
from functools import lru_cache

class GetUserUseCase:
    def __init__(
        self,
        repository: UserRepositoryInterface,
        cache: CacheInterface,
    ):
        self.repository = repository
        self.cache = cache

    async def execute(self, user_id: uuid.UUID) -> GetUserOutput:
        # Check cache
        cached = await self.cache.get(f"user:{user_id}")
        if cached:
            return GetUserOutput(**cached)

        # Fetch from repository
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User not found")

        output = GetUserOutput.from_entity(user)

        # Cache for 5 minutes
        await self.cache.set(f"user:{user_id}", output.dict(), ttl=300)

        return output
```

---

## Quick Templates

### Domain Template Checklist

```bash
# Create new domain
mkdir -p src/app/domains/{domain}/{entities,repositories,use_cases,infrastructure/database,mappers,presentation/v1}

# Create files
touch src/app/domains/{domain}/entities/{domain}.py
touch src/app/domains/{domain}/repositories/{domain}_repository.py
touch src/app/domains/{domain}/use_cases/create_{domain}.py
touch src/app/domains/{domain}/infrastructure/database/models.py
touch src/app/domains/{domain}/infrastructure/database/{domain}_repository_impl.py
touch src/app/domains/{domain}/mappers/entity_model_mapper.py
touch src/app/domains/{domain}/presentation/v1/schemas.py
touch src/app/domains/{domain}/presentation/v1/router.py
touch src/app/domains/{domain}/dependencies.py
touch src/app/domains/{domain}/__init__.py
```

---

## Additional Resources

- **[Architecture Guide](../docs/ARCHITECTURE.md)** - Complete technical deep-dive
- **[Domain Creation Tutorial](../docs/DOMAIN_CREATION.md)** - Step-by-step guide
- **[FAQ](../docs/FAQ.md)** - Common questions and answers

*Keywords: FastAPI code examples, Clean architecture templates, FastAPI use case patterns, Python repository pattern, FastAPI testing examples, Clean architecture code samples*
