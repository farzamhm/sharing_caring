"""Building management endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db_session
from ...core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/")
async def list_buildings(
    db: AsyncSession = Depends(get_db_session),
) -> List[dict]:
    """List all buildings."""
    # TODO: Implement building listing
    logger.info("Building list requested")
    
    # Placeholder implementation
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{building_id}")
async def get_building(
    building_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get building by ID."""
    # TODO: Implement get building by ID
    logger.info("Building details requested", building_id=building_id)
    
    # Placeholder implementation
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{building_id}/users")
async def list_building_users(
    building_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> List[dict]:
    """List users in a building."""
    # TODO: Implement building user listing
    logger.info("Building users requested", building_id=building_id)
    
    # Placeholder implementation
    raise HTTPException(status_code=501, detail="Not implemented yet")