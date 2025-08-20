"""Exchange model and related schemas."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base


class ExchangeStatus(str, Enum):
    """Exchange status enumeration."""
    PENDING = "pending"        # Exchange created, waiting for confirmation
    CONFIRMED = "confirmed"    # Both parties confirmed
    IN_PROGRESS = "in_progress"  # Pickup is happening
    COMPLETED = "completed"    # Successfully completed
    CANCELLED = "cancelled"    # Cancelled by either party
    FAILED = "failed"         # Failed for some reason
    NO_SHOW = "no_show"       # Recipient didn't show up


class Exchange(Base):
    """Exchange model representing a food sharing transaction."""
    
    __tablename__ = "exchanges"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    
    # Participants
    sharer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False
    )
    recipient_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Food item
    food_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("foods.id"),
        nullable=False
    )
    
    # Exchange details
    status: Mapped[ExchangeStatus] = mapped_column(
        String(20),
        default=ExchangeStatus.PENDING,
        nullable=False
    )
    
    # Confirmation tracking
    sharer_confirmed: Mapped[bool] = mapped_column(default=False)
    recipient_confirmed: Mapped[bool] = mapped_column(default=False)
    sharer_confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    recipient_confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Pickup details
    pickup_location: Mapped[Optional[str]] = mapped_column(String(255))
    pickup_instructions: Mapped[Optional[str]] = mapped_column(Text)
    scheduled_pickup_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_pickup_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Credits
    credit_amount: Mapped[int] = mapped_column(Integer, default=1)
    credits_transferred: Mapped[bool] = mapped_column(default=False)
    credits_transferred_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Feedback and notes
    sharer_notes: Mapped[Optional[str]] = mapped_column(Text)
    recipient_notes: Mapped[Optional[str]] = mapped_column(Text)
    sharer_rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5
    recipient_rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5
    
    # Completion tracking
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cancelled_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
    )
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text)
    
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
    sharer = relationship("User", foreign_keys=[sharer_id], back_populates="given_exchanges")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_exchanges")
    food = relationship("Food", back_populates="exchanges")
    cancelled_by = relationship("User", foreign_keys=[cancelled_by_id])
    
    def __repr__(self) -> str:
        return f"<Exchange(id='{self.id}', food_id='{self.food_id}', status='{self.status}')>"
    
    @property
    def is_confirmed(self) -> bool:
        """Check if exchange is confirmed by both parties."""
        return self.sharer_confirmed and self.recipient_confirmed
    
    @property
    def is_active(self) -> bool:
        """Check if exchange is in an active state."""
        return self.status in [
            ExchangeStatus.PENDING,
            ExchangeStatus.CONFIRMED,
            ExchangeStatus.IN_PROGRESS,
        ]
    
    @property
    def is_completed(self) -> bool:
        """Check if exchange is completed successfully."""
        return self.status == ExchangeStatus.COMPLETED
    
    @property
    def is_cancelled(self) -> bool:
        """Check if exchange is cancelled."""
        return self.status in [ExchangeStatus.CANCELLED, ExchangeStatus.FAILED, ExchangeStatus.NO_SHOW]
    
    @property
    def can_be_cancelled_by(self, user_id: str) -> bool:
        """Check if exchange can be cancelled by a specific user."""
        return (
            self.is_active
            and (self.sharer_id == user_id or self.recipient_id == user_id)
        )
    
    def confirm_by_user(self, user_id: str) -> bool:
        """Confirm exchange by a specific user."""
        now = datetime.utcnow()
        
        if user_id == self.sharer_id and not self.sharer_confirmed:
            self.sharer_confirmed = True
            self.sharer_confirmed_at = now
            return True
        elif user_id == self.recipient_id and not self.recipient_confirmed:
            self.recipient_confirmed = True
            self.recipient_confirmed_at = now
            return True
        
        return False
    
    def cancel_by_user(self, user_id: str, reason: str) -> bool:
        """Cancel exchange by a specific user."""
        if not self.can_be_cancelled_by(user_id):
            return False
        
        self.status = ExchangeStatus.CANCELLED
        self.cancelled_by_id = user_id
        self.cancelled_at = datetime.utcnow()
        self.cancellation_reason = reason
        return True
    
    def complete(self) -> bool:
        """Mark exchange as completed."""
        if not self.is_confirmed:
            return False
        
        self.status = ExchangeStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.actual_pickup_at = datetime.utcnow()
        return True