"""Health check endpoints."""

from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db_session
from ...core.redis import get_redis
from redis.asyncio import Redis

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, str]:
    """Basic health check."""
    return {"status": "healthy", "service": "neighborhood-sharing-platform"}


@router.get("/ready")
async def readiness_check(
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> Dict[str, str]:
    """Readiness check with database and Redis connectivity."""
    try:
        # Test database connection
        await db.execute("SELECT 1")
        
        # Test Redis connection
        await redis.ping()
        
        return {
            "status": "ready",
            "database": "connected",
            "redis": "connected",
        }
    except Exception as e:
        return {
            "status": "not ready",
            "error": str(e),
        }