"""Building management service."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.logging import get_logger
from ..models.building import Building, BuildingStatus

logger = get_logger(__name__)


class BuildingService:
    """Service for building management operations."""
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
    
    async def get_by_id(self, building_id: str) -> Optional[Building]:
        """Get building by ID."""
        try:
            result = await self.db.execute(
                select(Building)
                .options(selectinload(Building.users))
                .where(Building.id == building_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error getting building by ID", building_id=building_id, error=str(e))
            return None
    
    async def get_active_buildings(self, limit: int = 50) -> List[Building]:
        """Get all active buildings."""
        try:
            result = await self.db.execute(
                select(Building)
                .where(Building.status == BuildingStatus.ACTIVE)
                .limit(limit)
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error("Error getting active buildings", error=str(e))
            return []
    
    async def search_buildings(self, query: str, limit: int = 10) -> List[Building]:
        """Search buildings by name or address."""
        try:
            search_term = f"%{query.lower()}%"
            result = await self.db.execute(
                select(Building)
                .where(Building.status == BuildingStatus.ACTIVE)
                .where(
                    Building.name.ilike(search_term)
                    | Building.address.ilike(search_term)
                    | Building.city.ilike(search_term)
                )
                .limit(limit)
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error("Error searching buildings", query=query, error=str(e))
            return []
    
    async def create_building(
        self,
        name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        **kwargs
    ) -> Optional[Building]:
        """Create a new building."""
        try:
            building = Building(
                name=name,
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                **kwargs
            )
            
            self.db.add(building)
            await self.db.flush()  # Get the ID
            
            logger.info("Created new building", building_id=building.id, name=name)
            return building
            
        except Exception as e:
            logger.error("Error creating building", name=name, error=str(e), exc_info=True)
            await self.db.rollback()
            return None
    
    async def update_building(self, building_id: str, **kwargs) -> Optional[Building]:
        """Update building information."""
        try:
            building = await self.get_by_id(building_id)
            if not building:
                return None
            
            # Update allowed fields
            allowed_fields = {
                'name', 'address', 'city', 'state', 'zip_code', 'building_type',
                'total_units', 'floors', 'manager_name', 'manager_email',
                'manager_phone', 'max_users', 'sharing_rules', 'pickup_locations',
                'quiet_hours'
            }
            
            for key, value in kwargs.items():
                if key in allowed_fields and hasattr(building, key):
                    setattr(building, key, value)
            
            logger.info("Updated building", building_id=building_id, updated_fields=list(kwargs.keys()))
            return building
            
        except Exception as e:
            logger.error("Error updating building", building_id=building_id, error=str(e))
            return None
    
    async def get_building_stats(self, building_id: str) -> dict:
        """Get building statistics."""
        try:
            building = await self.get_by_id(building_id)
            if not building:
                return {}
            
            # TODO: Add more detailed stats (active food posts, exchanges, etc.)
            stats = {
                'total_users': building.current_user_count,
                'max_users': building.max_users,
                'capacity_percentage': (building.current_user_count / building.max_users * 100) if building.max_users > 0 else 0,
                'is_at_capacity': not building.has_capacity,
                'is_pilot': building.is_pilot,
                'pilot_active': building.is_pilot_active if building.is_pilot else None,
            }
            
            return stats
            
        except Exception as e:
            logger.error("Error getting building stats", building_id=building_id, error=str(e))
            return {}