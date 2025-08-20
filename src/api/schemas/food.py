"""Food schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from ...models.food import FoodCategory, FoodStatus, ServingSize


class FoodBase(BaseModel):
    """Base food schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: FoodCategory
    serving_size: ServingSize = Field(default=ServingSize.INDIVIDUAL)
    ingredients: Optional[str] = Field(None, max_length=1000)
    allergens: Optional[str] = Field(None, max_length=500)
    dietary_info: Optional[str] = Field(None, max_length=500)
    pickup_location: Optional[str] = Field(None, max_length=255)
    pickup_instructions: Optional[str] = Field(None, max_length=1000)


class FoodCreate(FoodBase):
    """Schema for creating a food post."""
    pickup_start: Optional[datetime] = None
    pickup_end: Optional[datetime] = None
    credit_value: int = Field(default=1, ge=1, le=5)


class FoodUpdate(BaseModel):
    """Schema for updating a food post."""
    description: Optional[str] = Field(None, max_length=1000)
    ingredients: Optional[str] = Field(None, max_length=1000)
    allergens: Optional[str] = Field(None, max_length=500)
    dietary_info: Optional[str] = Field(None, max_length=500)
    pickup_start: Optional[datetime] = None
    pickup_end: Optional[datetime] = None
    pickup_location: Optional[str] = Field(None, max_length=255)
    pickup_instructions: Optional[str] = Field(None, max_length=1000)
    serving_size: Optional[ServingSize] = None


class FoodResponse(FoodBase):
    """Schema for food API responses."""
    id: str
    status: FoodStatus
    prepared_at: datetime
    pickup_start: datetime
    pickup_end: datetime
    expires_at: datetime
    photo_urls: Optional[List[str]] = None
    credit_value: int
    created_at: datetime
    updated_at: datetime
    
    # Sharer information
    sharer_id: str
    sharer_name: str
    sharer_apartment: Optional[str] = None
    
    # Building information
    building_id: str
    
    # Claiming information
    claimed_by_id: Optional[str] = None
    claimed_at: Optional[datetime] = None
    
    # Computed properties
    is_available: bool
    is_expired: bool
    time_remaining_minutes: Optional[int] = None
    pickup_window_active: bool
    
    class Config:
        from_attributes = True


class FoodSummary(BaseModel):
    """Summary schema for food listings."""
    id: str
    title: str
    category: FoodCategory
    serving_size: ServingSize
    status: FoodStatus
    pickup_start: datetime
    pickup_end: datetime
    expires_at: datetime
    photo_urls: Optional[List[str]] = None
    credit_value: int
    
    # Sharer info
    sharer_name: str
    sharer_apartment: Optional[str] = None
    
    # Quick status checks
    is_available: bool
    time_remaining_minutes: Optional[int] = None
    
    class Config:
        from_attributes = True


class ClaimFoodRequest(BaseModel):
    """Schema for claiming food."""
    notes: Optional[str] = Field(None, max_length=500)


class ClaimFoodResponse(BaseModel):
    """Schema for claim response."""
    success: bool
    message: str
    exchange_id: Optional[str] = None
    pickup_details: Optional[dict] = None


class FoodSearchFilters(BaseModel):
    """Schema for food search filters."""
    category: Optional[FoodCategory] = None
    dietary_info: Optional[str] = None
    exclude_allergens: Optional[List[str]] = None
    available_now: bool = False
    max_distance: Optional[int] = None  # Future: distance in meters


class FoodBrowseResponse(BaseModel):
    """Schema for browse response."""
    foods: List[FoodSummary]
    total_count: int
    page: int
    page_size: int
    has_more: bool


class PhotoUploadResponse(BaseModel):
    """Schema for photo upload response."""
    success: bool
    message: str
    original_url: Optional[str] = None
    thumbnail_url: Optional[str] = None