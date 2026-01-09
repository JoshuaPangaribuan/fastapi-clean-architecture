# Migration Guide - Transition to FastAPI Clean Architecture

A comprehensive guide for migrating existing FastAPI applications to Clean Architecture principles.

[![migration](https://img.shields.io/badge/guide-migration-orange.svg)](#) [![Clean Architecture](https://img.shields.io/badge/architecture-clean%20arch-brightgreen.svg)](ARCHITECTURE.md)

## Table of Contents

- [Why Migrate?](#why-migrate)
- [Migration Strategy](#migration-strategy)
- [Step-by-Step Migration](#step-by-step-migration)
- [Common Migration Patterns](#common-migration-patterns)
- [Troubleshooting](#troubleshooting)

---

## Why Migrate?

### Problems with Traditional FastAPI

**Before (Traditional):**
```python
# Business logic mixed with routes
@router.post("/users")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Validation mixed in
    existing = db.query(UserModel).filter(UserModel.email == user_data.email).first()
    if existing:
        raise HTTPException(409, "Email already exists")

    # Business logic in route
    user = UserModel(**user_data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)

    # Direct database access
    return user
```

**Problems:**
- ❌ Hard to test without database
- ❌ Business logic scattered
- ❌ Can't swap database implementation
- ❌ Tight coupling between layers

### Benefits After Migration

**After (Clean Architecture):**
```python
# Presentation layer - thin and testable
@router.post("/users")
async def create_user(
    input_data: CreateUserSchema,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
):
    return await use_case.execute(input_data)

# Use case layer - business logic isolated
class CreateUserUseCase:
    async def execute(self, input_data: CreateUserInput) -> CreateUserOutput:
        existing = await self.repository.get_by_email(input_data.email)
        if existing:
            raise ResourceConflictError("Email already exists")
        # ... business logic
```

**Benefits:**
- ✅ Easy to test with mocks
- ✅ Business logic organized
- ✅ Database independent
- ✅ Clear layer separation

---

## Migration Strategy

### Recommended Approaches

#### 1. Incremental Migration (Recommended)

Migrate one endpoint/domain at a time while keeping existing code working.

**Pros:**
- Zero downtime
- Learn as you migrate
- Easy to rollback
- Gradual improvement

**Cons:**
- Two patterns coexist temporarily
- Longer migration timeline

#### 2. Big Bang Rewrite

Rewrite everything at once in Clean Architecture.

**Pros:**
- Consistent architecture
- Clean break from old patterns

**Cons:**
- High risk
- Long downtime
- Hard to validate
- Not recommended for production

### Recommended: Incremental Migration

Migrate following this order:
1. **Low-risk domains** (e.g., read-only endpoints)
2. **Medium-risk domains** (e.g., CRUD operations)
3. **High-risk domains** (e.g., payment processing)

---

## Step-by-Step Migration

### Phase 1: Preparation (1-2 days)

#### Step 1: Analyze Current Codebase

Map your existing code to domains:

```bash
# Identify all routers
find . -name "router.py" -o -name "routes.py"

# Identify all models
find . -name "models.py"

# Identify all Pydantic schemas
find . -name "schemas.py" -o -name "dto.py"
```

**Create a mapping document:**

```
Current Structure → Target Structure
├── routers/users.py → domains/user/presentation/v1/router.py
├── models/user.py → domains/user/infrastructure/database/models.py
├── schemas/user.py → domains/user/presentation/v1/schemas.py
└── services/user.py → domains/user/use_cases/
```

#### Step 2: Create New Directory Structure

```bash
# Create new directories
mkdir -p src/app/domains
mkdir -p src/app/core
mkdir -p docs
mkdir -p tests/{unit,integration}
```

#### Step 3: Setup Core Infrastructure

Copy/adapt core components from this template:

```bash
# Copy core utilities
cp -r template/src/app/core/* src/app/core/

# Setup database
cp template/src/app/core/database/session.py src/app/core/database/

# Setup error handling
cp -r template/src/app/core/errors/* src/app/core/errors/

# Setup logging
cp -r template/src/app/core/logging/* src/app/core/logging/
```

---

### Phase 2: Migrate First Domain (3-5 days)

#### Example: Migrating User Domain

**Step 1: Create domain structure**

```bash
mkdir -p src/app/domains/user/{entities,repositories,use_cases,infrastructure/database,mappers,presentation/v1}
```

**Step 2: Extract entity from existing model**

**Before:**
```python
# models/user.py
class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
```

**After:**
```python
# domains/user/entities/user.py
from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class UserEntity:
    id: Optional[uuid.UUID]
    email: str
    name: str

    def __post_init__(self):
        # Business rules
        if "@" not in self.email:
            raise DomainError("Invalid email format")
```

**Step 3: Create repository interface**

```python
# domains/user/repositories/user_repository.py
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

**Step 4: Implement repository**

```python
# domains/user/infrastructure/database/user_repository_impl.py
class UserRepositoryImpl(UserRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserEntity) -> UserEntity:
        # Use existing UserModel
        db_model = UserModel(
            id=str(user.id) if user.id else str(uuid.uuid4()),
            email=user.email,
            name=user.name,
        )
        self.session.add(db_model)
        await self.session.commit()
        await self.session.refresh(db_model)
        return self._to_entity(db_model)

    def _to_entity(self, model: UserModel) -> UserEntity:
        return UserEntity(
            id=uuid.UUID(model.id),
            email=model.email,
            name=model.name,
        )
```

**Step 5: Create use case**

```python
# domains/user/use_cases/create_user.py
from app.core.errors import ResourceConflictError

class CreateUserUseCase:
    def __init__(self, repository: UserRepositoryInterface):
        self.repository = repository

    async def execute(self, input_data: CreateUserInput) -> CreateUserOutput:
        # Business logic
        existing = await self.repository.get_by_email(input_data.email)
        if existing:
            raise ResourceConflictError("Email already exists")

        user = UserEntity(
            id=None,
            email=input_data.email,
            name=input_data.name,
        )

        created = await self.repository.create(user)
        return CreateUserOutput.from_entity(created)
```

**Step 6: Update presentation layer**

```python
# domains/user/presentation/v1/router.py
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/")
async def create_user(
    input_data: CreateUserSchema,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
):
    try:
        return await use_case.execute(input_data)
    except ResourceConflictError as e:
        raise HTTPException(status_code=409, detail=e.message)
```

**Step 7: Add dependency injection**

```python
# domains/user/dependencies.py
def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepositoryImpl:
    return UserRepositoryImpl(session)

def get_create_user_use_case(
    repository: UserRepositoryImpl = Depends(get_user_repository),
) -> CreateUserUseCase:
    return CreateUserUseCase(repository)
```

**Step 8: Register new router**

```python
# main.py
from app.domains.user.presentation.v1.router import router as user_router_v2

# Keep old router temporarily
app.include_router(user_router_v1, prefix="/api/v1/old")

# Add new router
app.include_router(user_router_v2, prefix="/api/v1/new")
```

**Step 9: Test new implementation**

```bash
# Test new endpoint
curl -X POST "http://localhost:8000/api/v1/new/users/" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test"}'
```

**Step 10: Switch over (after validation)**

```python
# main.py
# Remove old router
# app.include_router(user_router_v1, prefix="/api/v1/old")

# Use new router at main path
app.include_router(user_router_v2, prefix="/api/v1")
```

---

### Phase 3: Migrate Remaining Domains (1-2 weeks)

Repeat the process for each domain:

1. **Analyze domain** - Identify endpoints, models, business logic
2. **Create structure** - Set up directories
3. **Extract entity** - Create domain entity from model
4. **Create repository** - Define interface and implementation
5. **Create use cases** - Extract business logic
6. **Update presentation** - Create new router
7. **Test thoroughly** - Unit and integration tests
8. **Switch over** - Replace old implementation

---

### Phase 4: Cleanup (2-3 days)

#### Remove Old Code

```bash
# Remove old routers
rm -f routers/users_old.py

# Remove old services
rm -f services/user_service.py

# Remove unused imports
# Run: make lint
```

#### Update Tests

Migrate tests to new structure:

```python
# Before
def test_create_user(client):
    response = client.post("/users", json={...})
    assert response.status_code == 201

# After
def test_create_user_use_case():
    mock_repo = Mock(spec=UserRepositoryInterface)
    use_case = CreateUserUseCase(mock_repo)
    result = await use_case.execute(input_data)
    assert result.email == "test@example.com"
```

#### Update Documentation

- Update README with new architecture
- Add architecture diagrams
- Document migration decisions

---

## Common Migration Patterns

### Pattern 1: Direct Database Access → Repository

**Before:**
```python
@router.get("/users/{user_id}")
async def get_user(user_id: str, db: Session = Depends(get_db)):
    return db.query(UserModel).filter(UserModel.id == user_id).first()
```

**After:**
```python
# Use case
class GetUserUseCase:
    async def execute(self, user_id: uuid.UUID) -> GetUserOutput:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User not found")
        return GetUserOutput.from_entity(user)

# Router
@router.get("/users/{user_id}")
async def get_user(
    user_id: uuid.UUID,
    use_case: GetUserUseCase = Depends(get_get_user_use_case),
):
    return await use_case.execute(user_id)
```

### Pattern 2: Business Logic in Routes → Use Cases

**Before:**
```python
@router.post("/orders")
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    # Validation logic
    if order_data.total <= 0:
        raise HTTPException(400, "Invalid total")

    # Business logic
    product = db.query(ProductModel).get(order_data.product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    if product.stock < order_data.quantity:
        raise HTTPException(400, "Insufficient stock")

    # Database operations
    order = OrderModel(**order_data.dict())
    db.add(order)
    db.commit()
    return order
```

**After:**
```python
# Use case handles all business logic
class CreateOrderUseCase:
    async def execute(self, input_data: CreateOrderInput) -> CreateOrderOutput:
        # Validation
        if input_data.total <= 0:
            raise DomainError("Invalid total")

        # Business logic
        product = await self.product_repository.get_by_id(input_data.product_id)
        if not product:
            raise ResourceNotFoundError("Product not found")

        if product.stock < input_data.quantity:
            raise DomainError("Insufficient stock")

        # Create order
        order = OrderEntity(...)
        created = await self.order_repository.create(order)
        return CreateOrderOutput.from_entity(created)
```

### Pattern 3: Service Classes → Use Cases

**Before:**
```python
# services/user_service.py
class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: dict):
        # Business logic
        user = UserModel(**user_data)
        self.db.add(user)
        self.db.commit()
        return user

# router.py
@router.post("/users")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create_user(user_data.dict())
```

**After:**
```python
# use_cases/create_user.py
class CreateUserUseCase:
    def __init__(self, repository: UserRepositoryInterface):
        self.repository = repository

    async def execute(self, input_data: CreateUserInput) -> CreateUserOutput:
        # Business logic
        user = UserEntity.from_input(input_data)
        created = await self.repository.create(user)
        return CreateUserOutput.from_entity(created)

# router.py
@router.post("/users")
async def create_user(
    input_data: CreateUserSchema,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
):
    return await use_case.execute(input_data)
```

### Pattern 4: Pydantic Models → Entities + Schemas

**Before:**
```python
# schemas.py
class UserCreate(BaseModel):
    email: str
    name: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str

# Used for both validation and business logic
```

**After:**
```python
# entities/user.py
@dataclass
class UserEntity:
    id: Optional[uuid.UUID]
    email: str
    name: str

    def __post_init__(self):
        if "@" not in self.email:
            raise DomainError("Invalid email")

# presentation/v1/schemas.py
class CreateUserSchema(BaseModel):
    email: EmailStr
    name: str

class UserResponseSchema(BaseModel):
    id: uuid.UUID
    email: str
    name: str
```

---

## Troubleshooting

### Issue: Circular Imports

**Problem:**
```
ImportError: cannot import name 'UserEntity' from partially initialized module
```

**Solution:**
- Import inside functions, not at module level
- Use forward references: `'UserEntity'` instead of `UserEntity`
- Check layer dependency rules

### Issue: Database Session Not Found

**Problem:**
```
Could not find dependency for 'AsyncSession'
```

**Solution:**
```python
# Ensure database dependency is registered
# core/database/session.py
async def get_db_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
```

### Issue: Tests Failing After Migration

**Problem:** Tests worked before but fail after migration

**Solution:**
1. Update test fixtures to use new dependencies
2. Mock repository interfaces instead of database
3. Check that all imports are correct

### Issue: Performance Degradation

**Problem:** Slower after migration

**Common causes:**
- Too many mapper conversions
- N+1 query problems
- Missing database indexes

**Solutions:**
- Profile database queries
- Add indexes to frequently queried fields
- Use eager loading for relationships

---

## Migration Checklist

Use this checklist to track your migration progress:

### Preparation
- [ ] Analyze current codebase
- [ ] Create domain mapping document
- [ ] Setup new directory structure
- [ ] Copy core infrastructure
- [ ] Setup database session management
- [ ] Setup error handling
- [ ] Setup logging

### Domain Migration (Repeat for each domain)
- [ ] Create domain directory structure
- [ ] Extract entity from model
- [ ] Create repository interface
- [ ] Implement repository
- [ ] Create mappers
- [ ] Create use cases
- [ ] Create presentation schemas
- [ ] Create presentation router
- [ ] Add dependency injection
- [ ] Write tests
- [ ] Validate functionality
- [ ] Switch over traffic

### Cleanup
- [ ] Remove old code
- [ ] Update all tests
- [ ] Update documentation
- [ ] Performance testing
- [ ] Security review
- [ ] Deploy to production

---

## Next Steps

After migration:

1. **Add comprehensive tests** - Unit and integration tests
2. **Performance optimization** - Profile and optimize bottlenecks
3. **Documentation** - Keep architecture docs updated
4. **Team training** - Ensure team understands Clean Architecture
5. **Continuous improvement** - Refactor as needed

---

## Additional Resources

- **[Architecture Guide](ARCHITECTURE.md)** - Complete technical deep-dive
- **[Domain Creation Tutorial](DOMAIN_CREATION.md)** - Step-by-step guide
- **[FAQ](FAQ.md)** - Common questions and answers

Need help? Open a [GitHub Discussion](https://github.com/JoshuaPangaribuan/fastapi-clean-architecture/discussions).

*Keywords: FastAPI migration guide, Clean architecture migration, Refactor FastAPI, FastAPI to Clean Architecture, Python code migration, FastAPI best practices migration, Legacy FastAPI refactoring*
