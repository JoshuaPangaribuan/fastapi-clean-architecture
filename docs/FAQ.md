# Frequently Asked Questions - FastAPI Clean Architecture

Common questions about Clean Architecture, FastAPI, and this reference implementation.

[![FAQ](https://img.shields.io/badge/docs-FAQ-blue.svg)](#) [![Clean Architecture](https://img.shields.io/badge/architecture-clean%20arch-brightgreen.svg)](ARCHITECTURE.md)

## Table of Contents

- [Architecture Questions](#architecture-questions)
- [FastAPI-Specific Questions](#fastapi-specific-questions)
- [Database & ORM Questions](#database--orm-questions)
- [Testing Questions](#testing-questions)
- [Performance Questions](#performance-questions)
- [Project Structure Questions](#project-structure-questions)

---

## Architecture Questions

### What is Clean Architecture?

Clean Architecture is a software design philosophy that separates code into concentric layers with strict dependency rules. The core principle is **dependency inversion**: dependencies always point inward toward the domain (business logic), not outward toward frameworks or databases.

**Key benefits:**
- Business logic independent of frameworks
- Easy to test with mock dependencies
- Database can be swapped without changing business logic
- UI can be changed without affecting business rules

### Why use Clean Architecture with FastAPI?

**Traditional FastAPI challenges:**
- Business logic mixed with route handlers
- Direct database access throughout the application
- Tight coupling between components
- Difficult to test without database
- Business rules scattered across files

**Clean Architecture FastAPI benefits:**
- Business logic isolated in use cases
- Database access abstracted through repositories
- Loose coupling via interfaces
- Easy to test with mock dependencies
- Clear separation of concerns

### Is Clean Architecture overkill for small projects?

**For small, simple projects**: Yes, Clean Architecture may be overkill. If you're building:
- A simple CRUD API
- A prototype or MVP
- A project with minimal business logic

**For production projects**: Clean Architecture provides significant value:
- Scales well as business complexity grows
- Easier to maintain and refactor
- Clear patterns for team collaboration
- Testable business logic

**Recommendation**: Start with Clean Architecture if you anticipate growth. The initial investment pays off quickly as complexity increases.

### What's the difference between Clean Architecture and Hexagonal Architecture?

They're essentially the same concept with different terminology:

| Clean Architecture Term | Hexagonal Architecture Term |
|------------------------|----------------------------|
| Entity | Domain Model |
| Repository Interface | Port |
| Repository Implementation | Adapter |
| Use Case | Application Service |
| Presentation Layer | Driver/Primary Adapter |
| Infrastructure | Driven/Secondary Adapter |

Both emphasize:
- Dependency inversion
- Ports and adapters pattern
- Domain independence from frameworks

### Can I use this architecture for microservices?

**Yes!** This architecture is well-suited for microservices:

**Benefits:**
- Each domain can be a separate microservice
- Clear boundaries between services
- Shared domain logic can be extracted
- Independent deployment per service

**Considerations:**
- Split domains by business capability (not technical layers)
- Use API Gateway for routing
- Implement service-to-service communication via interfaces
- Consider event-driven architecture for cross-domain operations

---

## FastAPI-Specific Questions

### Why use dependency injection for everything?

FastAPI's dependency injection system provides:

1. **Testability**: Easy to inject mocks
2. **Automatic Validation**: Pydantic validates dependencies
3. **Request Scoping**: Fresh dependencies per request
4. **Type Safety**: Full type hints for IDE support
5. **Documentation**: Auto-generated docs show dependencies

```python
# Without DI: Hard to test
async def create_user(input_data: CreateUserSchema):
    repo = UserRepository()  # Can't mock
    return await repo.create(...)

# With DI: Easy to test
async def create_user(
    input_data: CreateUserSchema,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),  # Can mock
):
    return await use_case.execute(input_data)
```

### Where do I put FastAPI-specific code?

**Presentation layer only:**

```
presentation/
├── v1/
│   ├── router.py     # FastAPI routers
│   └── schemas.py    # Pydantic models
└── dependencies.py   # FastAPI Depends() factories
```

**Never put FastAPI code in:**
- Domain entities
- Repository interfaces
- Use cases
- Infrastructure implementations

### How do I handle authentication/authorization?

**Recommended approach:**

1. **Create auth domain** for authentication logic
2. **Use FastAPI dependencies** for route protection
3. **Store user context in request state**

```python
# presentation/v1/dependencies.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserEntity:
    """Get authenticated user from JWT token."""
    user = await auth_service.validate_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# presentation/v1/router.py
@router.get("/protected")
async def protected_route(
    user: UserEntity = Depends(get_current_user),
):
    return {"message": f"Hello {user.name}"}
```

### How do I implement file uploads?

**Use FastAPI's UploadFile in presentation layer:**

```python
# presentation/v1/schemas.py
from fastapi import UploadFile

# presentation/v1/router.py
@router.post("/upload")
async def upload_file(
    file: UploadFile,
    use_case: UploadFileUseCase = Depends(get_upload_file_use_case),
):
    # Validate file in presentation
    if not file.filename.endswith((".jpg", ".png")):
        raise HTTPException(400, "Invalid file type")

    # Pass to use case for business logic
    result = await use_case.execute(file)
    return result
```

### How do I handle WebSocket connections?

**WebSockets work with Clean Architecture:**

```python
# presentation/v1/router.py
from fastapi import WebSocket

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    use_case: WebSocketUseCase = Depends(get_websocket_use_case),
):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        response = await use_case.handle_message(data)
        await websocket.send_json(response)
```

---

## Database & ORM Questions

### Why use SQLAlchemy with Clean Architecture?

**Benefits:**
- Async support for high performance
- Mature, well-documented ORM
- Database-agnostic (switch databases easily)
- Migration support via Alembic
- Clean separation via repository pattern

**Repository abstraction keeps infrastructure details contained:**

```python
# Use case doesn't know about SQLAlchemy
class CreateUserUseCase:
    async def execute(self, input_data: CreateUserInput):
        # No SQLAlchemy here!
        user = await self.user_repository.create(...)
```

### How do I handle complex queries?

**Use repository methods for complex queries:**

```python
# repositories/user_repository.py
class UserRepositoryInterface(ABC):
    @abstractmethod
    async def search_users(
        self,
        name_filter: str | None = None,
        email_filter: str | None = None,
        created_after: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[UserEntity]:
        """Complex search with multiple filters."""
        pass
```

**Implementation in infrastructure layer:**

```python
# infrastructure/database/user_repository_impl.py
async def search_users(self, name_filter, email_filter, created_after, skip, limit):
    query = select(UserModel)

    if name_filter:
        query = query.where(UserModel.name.ilike(f"%{name_filter}%"))
    if email_filter:
        query = query.where(UserModel.email.ilike(f"%{email_filter}%"))
    if created_after:
        query = query.where(UserModel.created_at > created_after)

    query = query.offset(skip).limit(limit)
    result = await self.session.execute(query)
    return [self._to_entity(row) for row in result.scalars()]
```

### How do I handle database transactions?

**SQLAlchemy handles transactions automatically:**

```python
# core/database/session.py
async def get_db_session() -> AsyncSession:
    """Dependency that manages transactions."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()  # Commit on success
        except Exception:
            await session.rollback()  # Rollback on error
            raise
        finally:
            await session.close()
```

**For multi-operation transactions:**

```python
# use_cases/create_order.py
async def execute(self, input_data: CreateOrderInput):
    # All operations in same transaction
    order = await self.order_repository.create(order)
    await self.inventory_repository.decrease_stock(...)
    await self.payment_repository.charge(...)
    # Commit happens automatically
```

### How do I optimize database performance?

**Common optimizations:**

1. **Use indexes for frequently queried fields**
   ```python
   class UserModel(Base):
       email = Column(String, unique=True, index=True)  # Index
   ```

2. **Select only needed columns**
   ```python
   result = await session.execute(
       select(UserModel.id, UserModel.name).where(UserModel.is_active == True)
   )
   ```

3. **Use eager loading to avoid N+1 queries**
   ```python
   from sqlalchemy.orm import selectinload

   result = await session.execute(
       select(OrderModel).options(selectinload(OrderModel.items))
   )
   ```

4. **Connection pooling**
   ```python
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=10,      # Connection pool size
       max_overflow=20,   # Additional connections
   )
   ```

---

## Testing Questions

### How do I test use cases without a database?

**Use mock repositories:**

```python
# tests/unit/user/test_create_user_use_case.py
from unittest.mock import Mock

@pytest.mark.asyncio
async def test_create_user_success():
    # Arrange
    mock_repo = Mock(spec=UserRepositoryInterface)
    mock_repo.get_by_email.return_value = None  # User doesn't exist
    mock_repo.create.return_value = UserEntity(...)

    use_case = CreateUserUseCase(mock_repo, mock_mapper)
    input_data = CreateUserInput(email="test@example.com", name="Test")

    # Act
    result = await use_case.execute(input_data)

    # Assert
    assert result.email == "test@example.com"
    mock_repo.create.assert_called_once()
```

### How do I test API endpoints?

**Use FastAPI's TestClient:**

```python
# tests/integration/test_user_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user_endpoint():
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "name": "Test User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
```

### How do I test with a real database?

**Use pytest fixtures with test database:**

```python
# tests/conftest.py
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

# tests/integration/test_user_repository.py
@pytest.mark.asyncio
async def test_repository_create_user(test_db_session):
    repo = UserRepositoryImpl(test_db_session)
    user = await repo.create(UserEntity(...))
    assert user.id is not None
```

---

## Performance Questions

### Is Clean Architecture slower than traditional FastAPI?

**Minimal overhead:**

- Dependency injection adds ~1-2ms per request
- Mapper layer adds minimal overhead
- Database operations dominate response time anyway

**Benefits outweigh costs:**
- Easier to optimize when needed
- Better caching strategies
- Clear performance bottlenecks

### How do I cache results?

**Cache in use case layer:**

```python
# use_cases/get_user.py
from functools import lru_cache

class GetUserUseCase:
    def __init__(self, repository: UserRepositoryInterface, cache):
        self.repository = repository
        self.cache = cache

    async def execute(self, user_id: uuid.UUID) -> GetUserOutput:
        # Check cache first
        cached = await self.cache.get(f"user:{user_id}")
        if cached:
            return GetUserOutput(**cached)

        # Fetch from repository
        user = await self.repository.get_by_id(user_id)
        if user:
            # Cache for 5 minutes
            await self.cache.set(f"user:{user_id}", user.dict(), ttl=300)
            return GetUserOutput.from_entity(user)

        raise ResourceNotFoundError("User not found")
```

### How do I implement background tasks?

**Use FastAPI BackgroundTasks:**

```python
# presentation/v1/router.py
from fastapi import BackgroundTasks

@router.post("/users")
async def create_user(
    input_data: CreateUserSchema,
    background_tasks: BackgroundTasks,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
):
    result = await use_case.execute(input_data)

    # Add background task
    background_tasks.add_task(send_welcome_email, result.email)

    return result
```

---

## Project Structure Questions

### How do I organize multiple domains?

**Each domain is self-contained:**

```
domains/
├── user/           # Authentication & user management
├── product/        # Product catalog
├── order/          # Order processing
├── payment/        # Payment processing
└── inventory/      # Inventory management
```

**Cross-domain communication:**
- Use case from one domain can call use case from another
- Events for asynchronous communication
- Shared kernel for common concepts

### Where do I put shared code?

**Core utilities** (`src/app/core/`):
- Config, database, errors, logging, validation

**Shared kernel** (if needed):
```
src/app/shared/
├── entities/       # Shared entities (e.g., Money, Address)
├── value_objects/  # Value objects
└── utils/          # Common utilities
```

### How do I handle versioning?

**Version in presentation layer:**

```
presentation/
├── v1/            # Current API version
│   ├── router.py
│   └── schemas.py
└── v2/            # Future version
    ├── router.py
    └── schemas.py
```

**Register both versions in main.py:**

```python
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
```

---

## Additional Resources

- **[Architecture Guide](ARCHITECTURE.md)** - Complete technical deep-dive
- **[Domain Creation Tutorial](DOMAIN_CREATION.md)** - Step-by-step guide
- **[Migration Guide](MIGRATION_GUIDE.md)** - Transition from traditional FastAPI
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute

Still have questions? Open a [GitHub Discussion](https://github.com/JoshuaPangaribuan/fastapi-clean-architecture/discussions).

*Keywords: FastAPI clean architecture FAQ, Clean architecture Python questions, FastAPI best practices, FastAPI architecture patterns, Python DDD FAQ, FastAPI dependency injection, FastAPI repository pattern*
