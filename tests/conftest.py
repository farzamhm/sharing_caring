"""Pytest configuration and shared fixtures."""

import asyncio
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base, get_db_session
from src.core.config import get_settings
from src.models.user import User
from src.models.building import Building
from src.models.food import Food, FoodCategory, FoodStatus, ServingSize
from src.models.exchange import Exchange, ExchangeStatus
from src.models.credit import Credit, CreditTransaction, TransactionType


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create async engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
def mock_settings():
    """Mock application settings."""
    settings = MagicMock()
    settings.database_url = TEST_DATABASE_URL
    settings.redis_url = "redis://localhost:6379/15"  # Test Redis DB
    settings.telegram_bot_token = "test_bot_token"
    settings.environment = "test"
    settings.debug = True
    settings.log_level = "DEBUG"
    return settings


@pytest_asyncio.fixture
async def sample_building(test_db: AsyncSession) -> Building:
    """Create a sample building for testing."""
    building = Building(
        name="Test Apartment Complex",
        address="123 Test Street, Test City",
        postal_code="12345",
        country="TestCountry",
        timezone="UTC"
    )
    test_db.add(building)
    await test_db.commit()
    await test_db.refresh(building)
    return building


@pytest_asyncio.fixture
async def sample_user(test_db: AsyncSession, sample_building: Building) -> User:
    """Create a sample user for testing."""
    user = User(
        telegram_id=123456789,
        email="test@example.com",
        display_name="Test User",
        phone_number="+1234567890",
        apartment_number="101",
        building_id=sample_building.id,
        is_verified=True,
        verification_code="123456",
        verification_code_expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_user2(test_db: AsyncSession, sample_building: Building) -> User:
    """Create a second sample user for testing exchanges."""
    user = User(
        telegram_id=987654321,
        email="test2@example.com",
        display_name="Test User 2",
        phone_number="+1987654321",
        apartment_number="102",
        building_id=sample_building.id,
        is_verified=True,
        verification_code="654321",
        verification_code_expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_credit_account(test_db: AsyncSession, sample_user: User) -> Credit:
    """Create a sample credit account for testing."""
    credit = Credit(
        user_id=sample_user.id,
        balance=100,
        lifetime_earned=150,
        lifetime_spent=50
    )
    test_db.add(credit)
    await test_db.commit()
    await test_db.refresh(credit)
    return credit


@pytest_asyncio.fixture
async def sample_food_post(test_db: AsyncSession, sample_user: User, sample_building: Building) -> Food:
    """Create a sample food post for testing."""
    food = Food(
        title="Homemade Pasta",
        description="Fresh pasta with tomato sauce",
        category=FoodCategory.MAIN_COURSE,
        serving_size=ServingSize.SERVES_2_4,
        ingredients="Pasta, tomatoes, basil, garlic",
        allergens="Gluten, Eggs",
        dietary_info="Vegetarian",
        status=FoodStatus.AVAILABLE,
        prepared_at=datetime.utcnow() - timedelta(hours=1),
        pickup_start=datetime.utcnow() + timedelta(hours=1),
        pickup_end=datetime.utcnow() + timedelta(hours=6),
        expires_at=datetime.utcnow() + timedelta(hours=12),
        pickup_location="Apartment 101 lobby",
        pickup_instructions="Ring buzzer and I'll come down",
        credit_value=10,
        sharer_id=sample_user.id,
        building_id=sample_building.id
    )
    test_db.add(food)
    await test_db.commit()
    await test_db.refresh(food)
    return food


@pytest_asyncio.fixture
async def sample_exchange(
    test_db: AsyncSession,
    sample_food_post: Food,
    sample_user: User,
    sample_user2: User
) -> Exchange:
    """Create a sample exchange for testing."""
    exchange = Exchange(
        food_id=sample_food_post.id,
        sharer_id=sample_user.id,
        recipient_id=sample_user2.id,
        status=ExchangeStatus.PENDING,
        credit_amount=sample_food_post.credit_value,
        pickup_location=sample_food_post.pickup_location,
        pickup_instructions=sample_food_post.pickup_instructions,
        scheduled_pickup_at=sample_food_post.pickup_start + timedelta(hours=1)
    )
    test_db.add(exchange)
    await test_db.commit()
    await test_db.refresh(exchange)
    return exchange


@pytest.fixture
def mock_telegram_bot():
    """Mock Telegram bot for testing notifications."""
    bot = AsyncMock()
    bot.send_message = AsyncMock(return_value=True)
    return bot


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.exists = AsyncMock(return_value=0)
    return redis


@pytest_asyncio.fixture
async def credit_transaction(
    test_db: AsyncSession,
    sample_user: User,
    sample_food_post: Food
) -> CreditTransaction:
    """Create a sample credit transaction for testing."""
    transaction = CreditTransaction(
        user_id=sample_user.id,
        transaction_type=TransactionType.EARNED,
        amount=10,
        balance_before=90,
        balance_after=100,
        description="Food sharing reward",
        food_id=sample_food_post.id
    )
    test_db.add(transaction)
    await test_db.commit()
    await test_db.refresh(transaction)
    return transaction


# Helper functions for tests

def assert_datetime_close(dt1: datetime, dt2: datetime, tolerance_seconds: int = 5):
    """Assert that two datetimes are close within tolerance."""
    diff = abs((dt1 - dt2).total_seconds())
    assert diff <= tolerance_seconds, f"Datetimes differ by {diff} seconds, expected <= {tolerance_seconds}"


def create_test_food_data(**overrides):
    """Create test food post data with optional overrides."""
    default_data = {
        "title": "Test Food",
        "description": "A test food item",
        "category": FoodCategory.MAIN_COURSE,
        "serving_size": ServingSize.SERVES_2_4,
        "ingredients": "Test ingredients",
        "pickup_start": datetime.utcnow() + timedelta(hours=1),
        "pickup_end": datetime.utcnow() + timedelta(hours=6),
        "pickup_location": "Test location",
        "credit_value": 10
    }
    default_data.update(overrides)
    return default_data