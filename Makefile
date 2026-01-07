.PHONY: help dev migrate-up migrate-down migrate-new migrate-refresh db-reset run fmt lint

# Default target
help:
	@echo "FastAPI Clean Architecture - Go-Style Migration Workflow"
	@echo ""
	@echo "Available commands:"
	@echo "  make dev              - Run migrations + start dev server (Go-style)"
	@echo "  make migrate-up       - Run database migrations"
	@echo "  make migrate-down     - Rollback last migration"
	@echo "  make migrate-new MSG='desc' - Create new migration"
	@echo "  make migrate-refresh  - Downgrade then upgrade"
	@echo "  make db-reset         - Delete DB + fresh migrations"
	@echo "  make run              - Start server only"
	@echo "  make fmt              - Format code with ruff"
	@echo "  make lint             - Lint code with ruff"

# Development workflow (Go-style - migrations first!)
dev:
	@echo "🚀 Starting development server (Go-style: migrations first)..."
	@export PYTHONPATH=src:$$PYTHONPATH && make migrate-up
	@echo "✅ Migrations completed"
	@export PYTHONPATH=src:$$PYTHONPATH && make run

# Migration commands
migrate-up:
	@echo "📦 Running migrations..."
	@export PYTHONPATH=src:$$PYTHONPATH && alembic upgrade head
	@echo "✅ Migrations applied successfully"

migrate-down:
	@echo "↩️  Rolling back last migration..."
	@export PYTHONPATH=src:$$PYTHONPATH && alembic downgrade -1
	@echo "✅ Migration rolled back"

migrate-new:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: MSG parameter required. Usage: make migrate-new MSG='description'"; \
		exit 1; \
	fi
	@echo "📝 Creating new migration: $(MSG)"
	@export PYTHONPATH=src:$$PYTHONPATH && alembic revision --autogenerate -m "$(MSG)"
	@echo "✅ Migration file created"

migrate-refresh: migrate-down migrate-up

# Database management
db-reset:
	@echo "🗑️  Resetting database..."
	@rm -f data/fastapi-clean-arch.db
	@echo "✅ Database deleted"
	@make migrate-up

# Application
run:
	@echo "🎯 Starting FastAPI server..."
	@echo "   Docs: http://localhost:8000/docs"
	@echo "   Health: http://localhost:8000/"
	@export PYTHONPATH=src:$$PYTHONPATH && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Code quality (ruff - add to project when needed)
fmt:
	@echo "🎨 Formatting code..."
	@uv run ruff format .

lint:
	@echo "🔍 Linting code..."
	@uv run ruff check .
