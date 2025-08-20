"""User model and related schemas."""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base


class UserStatus(str, Enum):
    """User status enumeration."""
    PENDING = "pending"
    VERIFIED = "verified" 
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    
    # Telegram info
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    telegram_username: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Personal info
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    preferred_name: Mapped[Optional[str]] = mapped_column(String(100))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Verification
    is_phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_code: Mapped[Optional[str]] = mapped_column(String(10))
    verification_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Building association
    building_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("buildings.id"),
    )
    apartment_number: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Profile
    status: Mapped[UserStatus] = mapped_column(
        String(20), 
        default=UserStatus.PENDING,
        nullable=False
    )
    bio: Mapped[Optional[str]] = mapped_column(Text)
    dietary_restrictions: Mapped[Optional[str]] = mapped_column(Text)
    allergens: Mapped[Optional[str]] = mapped_column(Text)
    
    # Settings
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sharing_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
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
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    building = relationship("Building", back_populates="users")
    shared_foods: Mapped[List["Food"]] = relationship(
        "Food",
        foreign_keys="Food.sharer_id",
        back_populates="sharer",
    )
    received_exchanges: Mapped[List["Exchange"]] = relationship(
        "Exchange",
        foreign_keys="Exchange.recipient_id", 
        back_populates="recipient",
    )
    given_exchanges: Mapped[List["Exchange"]] = relationship(
        "Exchange",
        foreign_keys="Exchange.sharer_id",
        back_populates="sharer",
    )
    credit_account = relationship(
        "Credit",
        back_populates="user",
        uselist=False,
    )
    credit_transactions: Mapped[List["CreditTransaction"]] = relationship(
        "CreditTransaction",
        back_populates="user",
    )
    
    def __repr__(self) -> str:
        return f"<User(id='{self.id}', telegram_id={self.telegram_id}, name='{self.first_name}')>"
    
    @property
    def display_name(self) -> str:
        """Get user's display name."""
        if self.preferred_name:
            return self.preferred_name
        elif self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.first_name
    
    @property
    def is_verified(self) -> bool:
        """Check if user is verified."""
        return self.status == UserStatus.VERIFIED and self.is_phone_verified
    
    @property
    def can_share(self) -> bool:
        """Check if user can share food."""
        return (
            self.is_verified 
            and self.sharing_enabled 
            and self.status == UserStatus.VERIFIED
        )