"""Exchange schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ...models.exchange import ExchangeStatus


class ExchangeBase(BaseModel):
    """Base exchange schema."""
    pickup_location: Optional[str] = Field(None, max_length=255)
    pickup_instructions: Optional[str] = Field(None, max_length=1000)
    scheduled_pickup_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)


class ExchangeConfirmRequest(BaseModel):
    """Schema for confirming an exchange."""
    notes: Optional[str] = Field(None, max_length=500)


class ExchangeCompleteRequest(BaseModel):
    """Schema for completing an exchange."""
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=500)


class ExchangeCancelRequest(BaseModel):
    """Schema for cancelling an exchange."""
    reason: str = Field(..., min_length=1, max_length=500)


class ExchangeNoShowRequest(BaseModel):
    """Schema for reporting no-show."""
    no_show_user_id: str
    notes: Optional[str] = Field(None, max_length=500)


class ExchangeResponse(ExchangeBase):
    """Schema for exchange API responses."""
    id: str
    status: ExchangeStatus
    credit_amount: int
    credits_transferred: bool
    
    # Participants
    sharer_id: str
    recipient_id: str
    sharer_name: str
    recipient_name: str
    
    # Food details
    food_id: str
    food_title: str
    food_photo_url: Optional[str] = None
    
    # Confirmation status
    sharer_confirmed: bool
    recipient_confirmed: bool
    sharer_confirmed_at: Optional[datetime] = None
    recipient_confirmed_at: Optional[datetime] = None
    
    # Timing
    actual_pickup_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Feedback
    sharer_rating: Optional[int] = None
    recipient_rating: Optional[int] = None
    sharer_notes: Optional[str] = None
    recipient_notes: Optional[str] = None
    
    # Cancellation
    cancelled_by_id: Optional[str] = None
    cancellation_reason: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_confirmed: bool
    is_active: bool
    is_completed: bool
    is_cancelled: bool
    
    class Config:
        from_attributes = True


class ExchangeSummary(BaseModel):
    """Summary schema for exchange listings."""
    id: str
    status: ExchangeStatus
    food_title: str
    food_photo_url: Optional[str] = None
    other_user_name: str  # The other party in the exchange
    other_user_apartment: Optional[str] = None
    pickup_location: Optional[str] = None
    scheduled_pickup_at: Optional[datetime] = None
    credit_amount: int
    created_at: datetime
    
    # Quick status
    needs_confirmation: bool
    is_overdue: bool
    
    class Config:
        from_attributes = True