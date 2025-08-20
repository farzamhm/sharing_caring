#!/usr/bin/env python3
"""Initialize the database with initial data."""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import get_db
from src.core.config import get_settings
from src.models.building import Building, BuildingType, BuildingStatus
from src.models.user import User, UserStatus
from src.models.credit import Credit
from src.core.logging import configure_logging, get_logger

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


async def create_sample_building() -> str:
    """Create a sample building for development."""
    async with get_db() as db:
        # Check if sample building already exists
        from sqlalchemy import select
        result = await db.execute(
            select(Building).where(Building.name == "Sample Apartment Complex")
        )
        existing_building = result.scalar_one_or_none()
        
        if existing_building:
            logger.info("Sample building already exists", building_id=existing_building.id)
            return existing_building.id
        
        # Create new sample building
        building = Building(
            name="Sample Apartment Complex",
            address="123 Main Street",
            city="San Francisco",
            state="CA", 
            zip_code="94102",
            building_type=BuildingType.APARTMENT,
            total_units=50,
            floors=5,
            manager_name="Jane Smith",
            manager_email="manager@sample-building.com",
            manager_phone="+1-415-555-0123",
            status=BuildingStatus.ACTIVE,
            max_users=100,
            is_pilot=True,
            sharing_rules="Please be courteous and follow food safety guidelines.",
            pickup_locations="Lobby, Apartment doors",
            quiet_hours="10 PM - 8 AM"
        )
        
        db.add(building)
        await db.flush()  # Get the ID
        
        logger.info("Created sample building", building_id=building.id)
        return building.id


async def create_sample_user(building_id: str) -> str:
    """Create a sample user for development."""
    async with get_db() as db:
        # Check if sample user already exists
        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.telegram_id == 123456789)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            logger.info("Sample user already exists", user_id=existing_user.id)
            return existing_user.id
        
        # Create new sample user
        user = User(
            telegram_id=123456789,
            telegram_username="sample_user",
            first_name="John",
            last_name="Doe",
            preferred_name="John",
            phone_number="+1-415-555-0100",
            is_phone_verified=True,
            building_id=building_id,
            apartment_number="3B",
            status=UserStatus.VERIFIED,
            bio="Love sharing homemade meals with neighbors!",
            dietary_restrictions="Vegetarian",
            allergens="Nuts",
        )
        
        db.add(user)
        await db.flush()  # Get the ID
        
        # Create credit account
        credit_account = Credit(
            user_id=user.id,
            balance=settings.credit_initial_balance,
            lifetime_earned=settings.credit_initial_balance,
        )
        
        db.add(credit_account)
        
        logger.info("Created sample user", user_id=user.id)
        return user.id


async def init_development_data():
    """Initialize development data."""
    try:
        logger.info("Initializing development data...")
        
        # Create sample building
        building_id = await create_sample_building()
        
        # Create sample user
        user_id = await create_sample_user(building_id)
        
        logger.info(
            "Development data initialized successfully",
            building_id=building_id,
            user_id=user_id
        )
        
    except Exception as e:
        logger.error("Failed to initialize development data", error=str(e), exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(init_development_data())