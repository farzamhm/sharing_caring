"""FastAPI application main module."""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..core.config import get_settings
from ..core.database import create_tables
from ..core.logging import configure_logging, log_api_request
from ..core.redis import close_redis, init_redis
from .routers import admin, auth, buildings, credits, exchanges, foods, health, users, webhook

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Configure logging
    configure_logging()
    
    # Initialize Redis
    await init_redis()
    
    # Create database tables
    await create_tables()
    
    yield
    
    # Cleanup
    await close_redis()


# Create FastAPI application
app = FastAPI(
    title="Neighborhood Sharing Platform API",
    description="API for the neighborhood food sharing platform",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    """Log all API requests."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # Extract user ID from JWT if available
    user_id = getattr(request.state, "user_id", None)
    
    log_api_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=process_time,
        user_id=user_id,
        query_params=str(request.query_params) if request.query_params else None,
    )
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    from ..core.logging import get_logger
    
    logger = get_logger("api")
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        exception=str(exc),
        exception_type=type(exc).__name__,
    )
    
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "type": type(exc).__name__,
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )


# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(buildings.router, prefix="/buildings", tags=["buildings"])
app.include_router(foods.router, prefix="/foods", tags=["foods"])
app.include_router(exchanges.router, prefix="/exchanges", tags=["exchanges"])
app.include_router(credits.router, prefix="/credits", tags=["credits"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "Neighborhood Sharing Platform API",
        "version": "0.1.0",
        "environment": settings.environment,
    }