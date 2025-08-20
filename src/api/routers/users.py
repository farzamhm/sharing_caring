"""User management endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db_session
from ...core.logging import get_logger
from ...services.user_service import UserService
from ...services.building_service import BuildingService
from ..schemas.user import (
    PhoneVerificationConfirm,
    PhoneVerificationRequest,
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """Create a new user."""
    logger.info("User creation requested", telegram_id=user_data.telegram_id)
    
    try:
        user_service = UserService(db)
        
        # Check if building exists if provided
        if user_data.building_id:
            building_service = BuildingService(db)
            building = await building_service.get_by_id(user_data.building_id)
            if not building:
                raise HTTPException(status_code=404, detail="Building not found")
            if not building.has_capacity:
                raise HTTPException(status_code=400, detail="Building is at capacity")
        
        user = await user_service.create_user(
            telegram_id=user_data.telegram_id,
            telegram_username=user_data.telegram_username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phone_number,
            building_id=user_data.building_id,
            apartment_number=user_data.apartment_number,
        )
        
        if not user:
            raise HTTPException(status_code=400, detail="Failed to create user")
        
        await db.commit()
        
        # Convert to response model
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating user", telegram_id=user_data.telegram_id, error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """Get current user profile."""
    # TODO: Get current user from JWT token
    # For now, return sample user for testing
    logger.info("Current user profile requested")
    
    try:
        user_service = UserService(db)
        # Get sample user for testing (telegram_id: 123456789)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting current user", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """Update current user profile."""
    logger.info("User profile update requested")
    
    try:
        user_service = UserService(db)
        # TODO: Get user ID from JWT token
        # For now, use sample user for testing
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user with provided data
        update_data = user_update.dict(exclude_unset=True)
        updated_user = await user_service.update_user(user.id, **update_data)
        
        if not updated_user:
            raise HTTPException(status_code=400, detail="Failed to update user")
        
        await db.commit()
        
        return UserResponse.from_orm(updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating user", error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """Get user by ID."""
    logger.info("User profile requested", user_id=user_id)
    
    try:
        user_service = UserService(db)
        user = await user_service.get_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting user", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/verify-phone")
async def request_phone_verification(
    verification_request: PhoneVerificationRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Request phone number verification."""
    logger.info(
        "Phone verification requested",
        phone_number=verification_request.phone_number
    )
    
    try:
        user_service = UserService(db)
        # TODO: Get user ID from JWT token
        # For now, use sample user for testing
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = await user_service.request_phone_verification(
            user.id,
            verification_request.phone_number
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to send verification code")
        
        await db.commit()
        
        return {
            "message": "Verification code sent",
            "phone_number": verification_request.phone_number,
            "expires_in_minutes": 10,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error requesting phone verification",
            phone_number=verification_request.phone_number,
            error=str(e)
        )
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/verify-phone/confirm")
async def confirm_phone_verification(
    verification_confirm: PhoneVerificationConfirm,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Confirm phone number verification."""
    logger.info(
        "Phone verification confirmation",
        phone_number=verification_confirm.phone_number
    )
    
    try:
        user_service = UserService(db)
        # TODO: Get user ID from JWT token
        # For now, use sample user for testing
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = await user_service.verify_phone_code(
            user.id,
            verification_confirm.verification_code
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid or expired verification code")
        
        await db.commit()
        
        return {
            "message": "Phone number verified successfully",
            "phone_number": verification_confirm.phone_number,
            "is_verified": True,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error confirming phone verification",
            phone_number=verification_confirm.phone_number,
            error=str(e)
        )
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")