"""
FastAPI Clean Architecture Application.

This is the main entry point for the application.
It wires together all the components and starts the server.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings, reloader
from app.core.errors import (
    AppError,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging
from app.domains.user.presentation.v1.router import router as user_router

# Setup logging before creating the app
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup: Start settings reloader
    await reloader.start()

    yield

    # Shutdown: Stop settings reloader
    await reloader.stop()


app = FastAPI(
    title=get_settings().APP_NAME,
    description="A FastAPI application implementing Clean Architecture principles",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router, prefix=get_settings().API_V1_PREFIX)

# Register exception handlers
app.add_exception_handler(AppError, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": get_settings().APP_NAME}


@app.get("/api/v1", tags=["Health"])
def api_info():
    """API information endpoint."""
    return {
        "message": "Welcome to FastAPI Clean Architecture",
        "version": "v1",
        "docs": "/docs",
    }
