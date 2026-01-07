# FastAPI Clean Architecture

A production-ready FastAPI application implementing Clean Architecture principles.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (Python package installer)
- [make](https://www.gnu.org/software/make/) (Build automation)

### Installation

```bash
# Install dependencies
uv sync

# Optional: Create .env file from example
cp .env.example .env
```

## 📦 Development Workflow 

### Quick Start (One Command)

```bash
# Run migrations + start server
make dev
```

This command:
1. ✅ Runs all pending database migrations
2. ✅ Starts FastAPI server with auto-reload
3. 📖 Opens at http://localhost:8000/docs

### Step-by-Step Development

```bash
# 1. Run migrations (after model changes)
make migrate-up

# 2. Start server (if not already running)
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
# Delete database and apply fresh migrations
make db-reset
```

**⚠️ Warning:** `db-reset` will delete all data in the database.

## 📝 Common Tasks

### Add New Domain/Entity

1. Create new domain structure under `src/app/domains/`
2. Add model in `<domain>/infrastructure/database/models.py`
3. Import model in `alembic/env.py`
4. Create migration: `make migrate-new MSG="add <domain> table"`
5. Apply migration: `make migrate-up`

### Code Quality

```bash
# Format code (requires ruff)
make fmt

# Lint code (requires ruff)
make lint
```

To enable linting, add ruff to dependencies:
```bash
uv pip add ruff
```

## 📚 Project Structure

```
fastapi-clean-arch/
├── alembic/                    # Database migrations
│   └── versions/               # Migration scripts
├── data/                       # Database files (gitignored)
│   └── fastapi-clean-arch.db   # SQLite database
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
| `make db-reset` | Delete DB + fresh migrations |
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
