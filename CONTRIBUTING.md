# Contributing to FastAPI Clean Architecture

Thank you for your interest in contributing to this FastAPI Clean Architecture reference implementation! This guide will help you get started with contributing code, documentation, tests, or bug reports.

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/JoshuaPangaribuan/fastapi-clean-architecture/issues)

## Table of Contents

- [Why Contribute?](#why-contribute)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Architecture Guidelines](#architecture-guidelines)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Pull Request Process](#pull-request-process)
- [Community Guidelines](#community-guidelines)

## Why Contribute?

Contributing to open-source FastAPI projects helps you:

- **Learn Clean Architecture** - Gain hands-on experience with production-ready patterns
- **Build Your Portfolio** - Showcase your expertise to potential employers
- **Help the Community** - Improve resources for Python developers worldwide
- **Get Feedback** - Have experienced developers review your code
- **Stay Current** - Work with modern FastAPI and Python best practices

## Development Setup

### Prerequisites

Ensure you have the following installed:

- **Python 3.12+** - [Download Python](https://www.python.org/downloads/)
- **uv** - Fast Python package manager: [Installation Guide](https://github.com/astral-sh/uv#installation)
- **Docker & Docker Compose** - For PostgreSQL: [Install Docker](https://docs.docker.com/get-docker/)
- **Git** - Version control: [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- **make** - Build automation (included with most Unix-like systems)

### Fork and Clone

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork locally
git clone https://github.com/JoshuaPangaribuan/fastapi-clean-architecture.git
cd fastapi-clean-architecture

# 3. Add upstream remote
git remote add upstream https://github.com/JoshuaPangaribuan/fastapi-clean-architecture.git
```

### Install Dependencies

```bash
# Install all dependencies with uv (fast)
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
```

### Start Development Environment

```bash
# Start PostgreSQL container
docker-compose up -d

# Run migrations and start dev server
make dev
```

Your development server is now running at http://localhost:8000

## Code Standards

### Python Style Guide

We follow **PEP 8** with project-specific modifications:

- **Line Length**: 100 characters (configured in ruff)
- **Quotes**: Double quotes for strings
- **Imports**: Grouped and sorted (stdlib, third-party, local)
- **Type Hints**: Required for all function signatures

### Code Formatting

We use **ruff** for fast linting and formatting:

```bash
# Format code automatically
make fmt

# Check for linting issues
make lint
```

### Naming Conventions

Follow these naming conventions:

| Type | Convention | Example |
|------|------------|---------|
| **Variables** | snake_case | `user_id`, `total_amount` |
| **Functions** | snake_case | `get_user()`, `create_order()` |
| **Classes** | PascalCase | `UserRepository`, `CreateOrderUseCase` |
| **Constants** | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| **Private** | _leading_underscore | `_internal_method()` |

### Import Organization

Imports should be organized in this order:

```python
# 1. Standard library imports
import uuid
from dataclasses import dataclass
from typing import Optional

# 2. Third-party imports
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local imports
from app.core.errors import ResourceNotFoundError
from app.domains.user.entities import UserEntity
```

### Type Annotations

**Required**: All functions must have type annotations

```python
# Good
async def get_user(user_id: uuid.UUID) -> Optional[UserEntity]:
    pass

# Bad
async def get_user(user_id):
    pass
```

## Architecture Guidelines

### Clean Architecture Principles

This project enforces **strict Clean Architecture** with these rules:

#### Layer Dependency Rules

```
Domain Layer (entities, repositories)
├─ Cannot import from ANY other layer
├─ Pure business logic only
└─ No framework dependencies

Use Case Layer (use_cases/)
├─ Can import from Domain only
├─ Orchestrate business logic
└─ Depends on interfaces, not implementations

Infrastructure Layer (infrastructure/)
├─ Can import from Domain and Use Cases
├─ Implements repository interfaces
└─ Database models and external services

Presentation Layer (presentation/)
├─ Can import from all layers
├─ Prefer Use Cases over direct Domain access
└─ FastAPI routers and schemas
```

#### Domain Creation Checklist

When adding new domains, follow this order:

1. ✅ **Entity** (`domains/<domain>/entities/`) - Pure business object
2. ✅ **Repository Interface** (`domains/<domain>/repositories/`) - Abstract base class
3. ✅ **Use Cases** (`domains/<domain>/use_cases/`) - Business logic orchestration
4. ✅ **Infrastructure Model** (`domains/<domain>/infrastructure/database/`) - SQLAlchemy model
5. ✅ **Repository Implementation** (`domains/<domain>/infrastructure/database/`) - Concrete implementation
6. ✅ **Mappers** (`domains/<domain>/mappers/`) - Entity ↔ Model ↔ DTO transformations
7. ✅ **Schemas** (`domains/<domain>/presentation/v1/`) - Pydantic request/response models
8. ✅ **Router** (`domains/<domain>/presentation/v1/`) - FastAPI routes
9. ✅ **Dependencies** (`domains/<domain>/dependencies.py`) - Dependency injection factories
10. ✅ **Migration** - Alembic migration script
11. ✅ **Registration** (`main.py`) - Router registration

See [docs/DOMAIN_CREATION.md](docs/DOMAIN_CREATION.md) for detailed examples.

### Dependency Injection Pattern

Use FastAPI's dependency injection system:

```python
# Good: Use Depends() for injection
@router.post("/users")
async def create_user(
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
    input_data: CreateUserSchema,
) -> UserResponseSchema:
    return await use_case.execute(input_data)

# Bad: Direct instantiation
@router.post("/users")
async def create_user(input_data: CreateUserSchema):
    use_case = CreateUserUseCase(...)  # Don't do this
    return await use_case.execute(input_data)
```

### Error Handling

Use structured error handling:

```python
# Good: Use custom exceptions
from app.core.errors import ResourceNotFoundError

if not user:
    raise ResourceNotFoundError(
        f"User with id {user_id} not found",
        code="USER_NOT_FOUND",
        details={"user_id": str(user_id)},
    )

# Bad: Generic exceptions
if not user:
    raise ValueError("User not found")  # Don't do this
```

## Testing Requirements

### Test Structure

Tests should mirror the source structure:

```
tests/
├── unit/
│   ├── domains/
│   │   └── user/
│   │       ├── test_entities.py
│   │       ├── test_use_cases.py
│   │       └── test_mappers.py
│   └── core/
│       └── test_validation.py
├── integration/
│   └── test_user_api.py
└── conftest.py
```

### Testing Best Practices

```python
# Good: Arrange-Act-Assert pattern
async def test_create_user_success():
    # Arrange
    mock_repo = Mock(spec=UserRepositoryInterface)
    mock_mapper = Mock(spec=UserEntityDtoMapper)
    use_case = CreateUserUseCase(mock_repo, mock_mapper)
    input_data = CreateUserInput(email="test@example.com", name="Test")

    # Act
    result = await use_case.execute(input_data)

    # Assert
    assert result.email == "test@example.com"
    mock_repo.create.assert_called_once()

# Good: Use pytest fixtures
@pytest.fixture
async def user_repository():
    # Setup test repository
    repo = InMemoryUserRepository()
    yield repo
    # Cleanup
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/user/test_use_cases.py

# Run with verbose output
pytest -v
```

### Test Coverage Requirements

- **Unit Tests**: Minimum 80% coverage for use cases and entities
- **Integration Tests**: Cover all API endpoints
- **Critical Path**: 100% coverage for authentication and authorization

## Documentation Standards

### Code Documentation

All public functions must have docstrings:

```python
async def get_user(user_id: uuid.UUID) -> Optional[UserEntity]:
    """
    Retrieve a user by their unique identifier.

    Args:
        user_id: The unique identifier of the user to retrieve.

    Returns:
        The user entity if found, None otherwise.

    Raises:
        DomainError: If the user_id is invalid.

    Example:
        >>> user = await get_user(uuid.uuid4())
        >>> if user:
        ...     print(user.email)
    """
    pass
```

### Architecture Documentation

When adding features, update documentation:

- **README.md** - Update features list, examples, or commands
- **docs/ARCHITECTURE.md** - Document architectural decisions
- **docs/DOMAIN_CREATION.md** - Add examples if introducing new patterns
- **CHANGELOG.md** - Document breaking changes

### SEO Best Practices

When writing documentation:

- ✅ Use semantic heading structure (H1 → H2 → H3)
- ✅ Include code examples for engagement
- ✅ Add keyword-rich descriptions
- ✅ Link to related documentation
- ✅ Write clear, concise prose
- ❌ Avoid jargon without explanation
- ❌ Don't duplicate information across files

## Pull Request Process

### Before Submitting

1. **Create a feature branch**: `git checkout -b feature/your-feature-name`
2. **Write clean commits**: Use conventional commit messages
3. **Format your code**: `make fmt`
4. **Run tests**: `pytest`
5. **Update documentation**: Add/modify relevant docs

### Commit Message Format

Follow conventional commits:

```
feat(domain): add user profile feature

- Add UserProfileEntity with validation
- Implement GetUserProfileUseCase
- Add GET /users/{id}/profile endpoint
- Update architecture documentation

Closes #123
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Architecture Compliance
- [ ] Follows Clean Architecture principles
- [ ] Respects layer dependency rules
- [ ] Includes proper error handling
- [ ] Has type annotations

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing

## Documentation
- [ ] Code documented with docstrings
- [ ] Architecture docs updated
- [ ] README updated (if needed)

## Checklist
- [ ] Code formatted with ruff
- [ ] No linting errors
- [ ] Commits follow conventional format
- [ ] PR description complete
```

### Review Process

1. **Automated Checks**: CI runs tests, linting, and formatting
2. **Code Review**: Maintainer reviews for architecture compliance
3. **Feedback**: Address review comments
4. **Approval**: PR approved when all checks pass
5. **Merge**: Squashed into main branch

### Review Criteria

Maintainers evaluate PRs based on:

- ✅ **Clean Architecture Compliance** - Follows layer dependency rules
- ✅ **Code Quality** - Clean, readable, well-documented code
- ✅ **Test Coverage** - Adequate tests for new functionality
- ✅ **Documentation** - Updated docs and code comments
- ✅ **Consistency** - Matches project patterns and conventions

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Welcome newcomers and help them learn
- Focus on what is best for the community

### Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Questions and architectural discussions
- **Pull Requests**: Code contributions and improvements

### Reporting Issues

When reporting bugs, include:

- **Python version**: `python --version`
- **FastAPI version**: `uv show fastapi`
- **Steps to reproduce**: Minimal reproduction code
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Error messages**: Full traceback if applicable

## Recognition

Contributors are recognized in:

- **CONTRIBUTORS.md** - List of all contributors
- **Release Notes** - Credits for each release
- **GitHub Stars** - Your contributions help the community grow

## Quick Reference

### Essential Commands

```bash
# Development
make dev              # Start dev server with migrations
make run              # Start server only
make fmt              # Format code
make lint             # Check code quality

# Database
make db-up            # Start PostgreSQL
make migrate-new MSG="description"  # Create migration
make migrate-up       # Apply migrations
make migrate-down     # Rollback migration
make db-reset         # Reset database

# Testing
pytest                # Run tests
pytest --cov          # Run with coverage
```

### Useful Links

- [Architecture Guide](docs/ARCHITECTURE.md) - Complete technical documentation
- [Domain Creation Tutorial](docs/DOMAIN_CREATION.md) - Step-by-step guide
- [FAQ](docs/FAQ.md) - Common questions and answers
- [Migration Guide](docs/MIGRATION_GUIDE.md) - Transition from traditional FastAPI

## Need More Help?

- Open a [GitHub Discussion](https://github.com/JoshuaPangaribuan/fastapi-clean-architecture/discussions)
- Check existing [Issues](https://github.com/JoshuaPangaribuan/fastapi-clean-architecture/issues)
- Review the [Architecture Documentation](docs/ARCHITECTURE.md)

---

**Happy Contributing!** 🚀

Your contributions help make FastAPI Clean Architecture better for everyone. Whether you're fixing bugs, adding features, improving documentation, or reporting issues, we appreciate your efforts in building a production-ready FastAPI reference implementation.

*Keywords: FastAPI open source contribution, Clean Architecture contribution guide, Python best practices, FastAPI development workflow, Clean Architecture Python tutorial*
