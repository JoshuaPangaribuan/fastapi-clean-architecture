# FastAPI Clean Architecture

A production-ready FastAPI application implementing Clean Architecture principles.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (Python package installer)
- [make](https://www.gnu.org/software/make/) (Build automation)
- Docker & Docker Compose (for PostgreSQL)
- PostgreSQL 16+

### Installation

```bash
# Install dependencies
uv sync

# Optional: Create .env file from example
cp .env.example .env

# Start PostgreSQL
docker-compose up -d
```

## 🛠️ Tech Stack

### Core Framework
- **FastAPI** - Modern, fast web framework for building APIs with Python 3.12+
- **Python** - Primary language (3.12+)

### Database & ORM
- **PostgreSQL 16** - Relational database
- **SQLAlchemy 2.0** - Python SQL toolkit and ORM
- **asyncpg** - High-performance PostgreSQL driver for asyncio
- **Alembic** - Database migration tool

### Data Validation
- **Pydantic** - Data validation using Python type annotations (included in FastAPI)

### Development Tools
- **uv** - Fast Python package installer and resolver
- **make** - Build automation and task runner
- **Docker & Docker Compose** - Containerization for PostgreSQL

### Architecture
- **Clean Architecture** - Layered architecture pattern for maintainable and testable code

## 📦 Development Workflow 

### Quick Start (One Command)

```bash
# Run migrations + start server
make db-up  # First time only
make dev
```

This command:
1. ✅ Runs all pending database migrations
2. ✅ Starts FastAPI server with auto-reload
3. 📖 Opens at http://localhost:8000/docs

### Step-by-Step Development

```bash
# 1. Start PostgreSQL (if not already running)
make db-up

# 2. Run migrations (after model changes)
make migrate-up

# 3. Start server (if not already running)
make run
```

## 🗄️ Database Migrations

### Create New Migration

```bash
# After modifying models, create a migration
make migrate-new MSG="add phone column to users"
```

### Apply Migrations

```bash
# Apply all pending migrations
make migrate-up

# Rollback last migration
make migrate-down

# Downgrade then upgrade (useful for testing)
make migrate-refresh
```

### Reset Database

```bash
# Delete PostgreSQL data and apply fresh migrations
make db-reset
```

**⚠️ Warning:** `db-reset` will delete all data in the database and recreate the PostgreSQL container.

### PostgreSQL Management

```bash
# Start PostgreSQL container
make db-up

# Stop PostgreSQL container
make db-down

# View PostgreSQL logs
make db-logs
```

## 📝 Common Tasks

### Add New Domain/Entity

1. Create new domain structure under `src/app/domains/`
2. Add model in `<domain>/infrastructure/database/models.py`
3. Import model in `alembic/env.py`
4. Create migration: `make migrate-new MSG="add <domain> table"`
5. Apply migration: `make migrate-up`

### Code Quality

```bash
# Format code
make fmt

# Lint code
make lint
```

## 📚 Project Structure

```
fastapi-clean-arch/
├── alembic/                    # Database migrations
│   └── versions/               # Migration scripts
├── src/
│   └── app/
│       ├── core/               # Core configuration
│       │   ├── config.py       # App settings
│       │   ├── database.py     # Database engine & session
│       │   └── ...
│       └── domains/            # Business domains
│           └── user/            # Example domain
│               ├── entities/   # Domain entities
│               ├── infrastructure/
│               │   └── database/
│               │       └── models.py  # SQLAlchemy models
│               ├── presentation/
│               │   └── v1/
│               │       └── router.py  # API endpoints
│               ├── use_cases/  # Business logic
│               └── ...
├── .env.example                # Environment variables template
├── Makefile                    # Build automation
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # PostgreSQL container
├── pyproject.toml              # Python dependencies
└── README.md
```

## 🎯 Available Commands

Run `make help` or `make` for a complete list of available commands.

### Command Reference

| Command | Description |
|---------|-------------|
| `make dev` | Run migrations + start dev server |
| `make migrate-up` | Apply database migrations |
| `make migrate-down` | Rollback last migration |
| `make migrate-new MSG='desc'` | Create new migration |
| `make migrate-refresh` | Downgrade then upgrade |
| `make db-reset` | Reset PostgreSQL + fresh migrations |
| `make db-up` | Start PostgreSQL container |
| `make db-down` | Stop PostgreSQL container |
| `make db-logs` | View PostgreSQL logs |
| `make run` | Start server only |
| `make fmt` | Format code (requires ruff) |
| `make lint` | Lint code (requires ruff) |

## 🏗️ Architecture

This project follows **Clean Architecture** principles:

- **Entities**: Core business logic (domain-independent)
- **Use Cases**: Application-specific business rules
- **Infrastructure**: External concerns (database, frameworks)
- **Interface Adapters**: Data transformation (API controllers)
- **Frameworks & Drivers**: External tools (FastAPI, SQLAlchemy)

## 📖 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🧪 Testing (Optional)

To add testing capabilities:

```bash
# Install test dependencies
uv pip add pytest pytest-asyncio httpx

# Run tests (add to Makefile)
make test
```

## 🔒 Security

- Never commit `.env` files or database files
- Use environment variables for sensitive configuration
- Keep `DEBUG=False` in production

## 🤝 Contributing

1. Create a new branch
2. Make your changes
3. Create migrations for any schema changes
4. Test thoroughly
5. Submit a pull request
