"""Food model and related schemas."""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base


class FoodCategory(str, Enum):
    """Food category enumeration based on safety risk levels."""
    BAKED_GOODS = "baked_goods"
    COOKED_VEGETABLES = "cooked_vegetables"
    PRESERVED_FOODS = "preserved_foods"
    COOKED_GRAINS = "cooked_grains"
    COOKED_PROTEINS = "cooked_proteins"
    DAIRY_BASED = "dairy_based"
    OTHER = "other"


class FoodStatus(str, Enum):
    """Food post status enumeration."""
    AVAILABLE = "available"
    CLAIMED = "claimed"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ServingSize(str, Enum):
    """Serving size enumeration."""
    INDIVIDUAL = "individual"  # 1 serving
    SMALL = "small"           # 2-3 servings  
    MEDIUM = "medium"         # 4-6 servings
    LARGE = "large"           # 7+ servings


class Food(Base):
    """Food model."""
    
    __tablename__ = "foods"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    
    # Basic info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[FoodCategory] = mapped_column(
        String(50),
        nullable=False
    )
    serving_size: Mapped[ServingSize] = mapped_column(
        String(20),
        default=ServingSize.INDIVIDUAL,
        nullable=False
    )
    
    # Safety info
    ingredients: Mapped[Optional[str]] = mapped_column(Text)
    allergens: Mapped[Optional[str]] = mapped_column(Text)
    dietary_info: Mapped[Optional[str]] = mapped_column(Text)  # vegan, gluten-free, etc.
    
    # Timing
    prepared_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    pickup_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    pickup_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Location and pickup
    pickup_location: Mapped[Optional[str]] = mapped_column(String(255))
    pickup_instructions: Mapped[Optional[str]] = mapped_column(Text)
    
    # Photos (store file paths)
    photo_urls: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of URLs
    
    # Status
    status: Mapped[FoodStatus] = mapped_column(
        String(20),
        default=FoodStatus.AVAILABLE,
        nullable=False
    )
    claimed_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
    )
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Credits
    credit_value: Mapped[int] = mapped_column(Integer, default=1)
    
    # Relationships
    sharer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False
    )
    building_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("buildings.id"),
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    sharer = relationship("User", foreign_keys=[sharer_id], back_populates="shared_foods")
    claimed_by = relationship("User", foreign_keys=[claimed_by_id])
    building = relationship("Building")
    exchanges: Mapped[List["Exchange"]] = relationship("Exchange", back_populates="food")
    
    def __repr__(self) -> str:
        return f"<Food(id='{self.id}', title='{self.title}', status='{self.status}')>"
    
    @property
    def is_available(self) -> bool:
        """Check if food is available for claiming."""
        return (
            self.status == FoodStatus.AVAILABLE
            and datetime.utcnow() < self.expires_at
            and datetime.utcnow() >= self.pickup_start
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if food has expired."""
        return datetime.utcnow() >= self.expires_at
    
    @property
    def time_until_pickup(self) -> Optional[timedelta]:
        """Get time until pickup window opens."""
        now = datetime.utcnow()
        if now < self.pickup_start:
            return self.pickup_start - now
        return None
    
    @property
    def time_remaining(self) -> Optional[timedelta]:
        """Get time remaining before expiration."""
        now = datetime.utcnow()
        if now < self.expires_at:
            return self.expires_at - now
        return None
    
    @property
    def pickup_window_active(self) -> bool:
        """Check if currently in pickup window."""
        now = datetime.utcnow()
        return self.pickup_start <= now <= self.pickup_end
    
    def can_be_claimed_by(self, user_id: str) -> bool:
        """Check if food can be claimed by a specific user."""
        return (
            self.is_available
            and self.sharer_id != user_id  # Can't claim your own food
            and self.claimed_by_id is None
        )