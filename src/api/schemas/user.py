"""User schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from phonenumbers import NumberParseException, parse as parse_phone

from ...models.user import UserStatus


class UserBase(BaseModel):
    """Base user schema."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    preferred_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = Field(None, max_length=1000)
    dietary_restrictions: Optional[str] = Field(None, max_length=500)
    allergens: Optional[str] = Field(None, max_length=500)
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is None:
            return v
        
        try:
            parsed = parse_phone(v, "US")  # Default to US
            if not parsed.is_valid():
                raise ValueError("Invalid phone number")
            return f"+{parsed.country_code}{parsed.national_number}"
        except NumberParseException:
            raise ValueError("Invalid phone number format")


class UserCreate(UserBase):
    """Schema for creating a user."""
    telegram_id: int = Field(..., gt=0)
    telegram_username: Optional[str] = Field(None, max_length=255)
    apartment_number: Optional[str] = Field(None, max_length=20)
    building_id: Optional[str] = Field(None)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    preferred_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    apartment_number: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = Field(None, max_length=1000)
    dietary_restrictions: Optional[str] = Field(None, max_length=500)
    allergens: Optional[str] = Field(None, max_length=500)
    notifications_enabled: Optional[bool] = None
    sharing_enabled: Optional[bool] = None
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is None:
            return v
        
        try:
            parsed = parse_phone(v, "US")
            if not parsed.is_valid():
                raise ValueError("Invalid phone number")
            return f"+{parsed.country_code}{parsed.national_number}"
        except NumberParseException:
            raise ValueError("Invalid phone number format")


class UserResponse(UserBase):
    """Schema for user API responses."""
    id: str
    telegram_id: int
    telegram_username: Optional[str] = None
    apartment_number: Optional[str] = None
    building_id: Optional[str] = None
    status: UserStatus
    is_phone_verified: bool
    notifications_enabled: bool
    sharing_enabled: bool
    created_at: datetime
    updated_at: datetime
    last_active_at: Optional[datetime] = None
    
    # Computed fields
    display_name: str
    is_verified: bool
    can_share: bool
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Public user profile schema."""
    id: str
    display_name: str
    apartment_number: Optional[str] = None
    bio: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PhoneVerificationRequest(BaseModel):
    """Schema for phone verification request."""
    phone_number: str = Field(..., max_length=20)
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number format."""
        try:
            parsed = parse_phone(v, "US")
            if not parsed.is_valid():
                raise ValueError("Invalid phone number")
            return f"+{parsed.country_code}{parsed.national_number}"
        except NumberParseException:
            raise ValueError("Invalid phone number format")


class PhoneVerificationConfirm(BaseModel):
    """Schema for phone verification confirmation."""
    phone_number: str = Field(..., max_length=20)
    verification_code: str = Field(..., min_length=4, max_length=10)
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number format."""
        try:
            parsed = parse_phone(v, "US")
            if not parsed.is_valid():
                raise ValueError("Invalid phone number")
            return f"+{parsed.country_code}{parsed.national_number}"
        except NumberParseException:
            raise ValueError("Invalid phone number format")