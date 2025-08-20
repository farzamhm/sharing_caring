"""Building model and related schemas."""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base


class BuildingType(str, Enum):
    """Building type enumeration."""
    APARTMENT = "apartment"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    HOUSE = "house"
    OTHER = "other"


class BuildingStatus(str, Enum):
    """Building status enumeration."""
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class Building(Base):
    """Building model."""
    
    __tablename__ = "buildings"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    
    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(10), nullable=False)
    country: Mapped[str] = mapped_column(String(50), default="US", nullable=False)
    
    # Building details
    building_type: Mapped[BuildingType] = mapped_column(
        String(20),
        default=BuildingType.APARTMENT,
        nullable=False
    )
    total_units: Mapped[Optional[int]] = mapped_column(Integer)
    floors: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Contact and management
    manager_name: Mapped[Optional[str]] = mapped_column(String(255))
    manager_email: Mapped[Optional[str]] = mapped_column(String(255))
    manager_phone: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Platform settings
    status: Mapped[BuildingStatus] = mapped_column(
        String(20),
        default=BuildingStatus.PENDING,
        nullable=False
    )
    max_users: Mapped[int] = mapped_column(Integer, default=100)
    is_pilot: Mapped[bool] = mapped_column(Boolean, default=False)
    pilot_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    pilot_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Rules and guidelines
    sharing_rules: Mapped[Optional[str]] = mapped_column(Text)
    pickup_locations: Mapped[Optional[str]] = mapped_column(Text)
    quiet_hours: Mapped[Optional[str]] = mapped_column(String(100))
    
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
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="building",
    )
    
    def __repr__(self) -> str:
        return f"<Building(id='{self.id}', name='{self.name}', address='{self.address}')>"
    
    @property
    def full_address(self) -> str:
        """Get full formatted address."""
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"
    
    @property
    def is_active(self) -> bool:
        """Check if building is active."""
        return self.status == BuildingStatus.ACTIVE
    
    @property
    def current_user_count(self) -> int:
        """Get current number of users (loaded via relationship)."""
        return len(self.users) if self.users else 0
    
    @property
    def has_capacity(self) -> bool:
        """Check if building has capacity for more users."""
        return self.current_user_count < self.max_users
    
    @property
    def is_pilot_active(self) -> bool:
        """Check if pilot program is currently active."""
        if not self.is_pilot:
            return False
        
        now = datetime.utcnow()
        if self.pilot_start_date and now < self.pilot_start_date:
            return False
        
        if self.pilot_end_date and now > self.pilot_end_date:
            return False
        
        return True