from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import AppException, ResourceNotFoundException, ResourceConflictException, DomainException

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handler for standard HTTP exceptions (like 404 Not Found, 405 Method Not Allowed).
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)},
    )

async def app_exception_handler(request: Request, exc: AppException):
    """
    Global handler for application exceptions.
    
    Maps application exceptions to appropriate HTTP responses.
    """
    
    if isinstance(exc, ResourceNotFoundException):
        response_status = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ResourceConflictException):
        response_status = status.HTTP_409_CONFLICT
    elif isinstance(exc, DomainException):
        response_status = status.HTTP_400_BAD_REQUEST
    else:
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        
    return JSONResponse(
        status_code=response_status,
        content={"detail": str(exc)},
    )
