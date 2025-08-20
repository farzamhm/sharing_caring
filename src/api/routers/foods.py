"""Food management endpoints."""

from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db_session
from ...core.logging import get_logger
from ...services.food_service import FoodService
from ...services.photo_service import PhotoService
from ...services.notification_service import NotificationService
from ..schemas.food import (
    FoodCreate,
    FoodUpdate,
    FoodResponse,
    FoodSummary,
    FoodBrowseResponse,
    ClaimFoodRequest,
    ClaimFoodResponse,
    PhotoUploadResponse,
    FoodSearchFilters,
)
from ...models.food import FoodCategory, ServingSize

router = APIRouter()
logger = get_logger(__name__)


def _convert_food_to_response(food) -> FoodResponse:
    """Convert Food model to response schema."""
    # Calculate time remaining
    time_remaining_minutes = None
    if food.expires_at > datetime.utcnow():
        delta = food.expires_at - datetime.utcnow()
        time_remaining_minutes = int(delta.total_seconds() / 60)
    
    # Parse photo URLs
    photo_urls = None
    if food.photo_urls:
        import json
        try:
            photo_urls = json.loads(food.photo_urls)
        except:
            photo_urls = [food.photo_urls]  # Fallback for single URL
    
    return FoodResponse(
        id=food.id,
        title=food.title,
        description=food.description,
        category=food.category,
        serving_size=food.serving_size,
        ingredients=food.ingredients,
        allergens=food.allergens,
        dietary_info=food.dietary_info,
        status=food.status,
        prepared_at=food.prepared_at,
        pickup_start=food.pickup_start,
        pickup_end=food.pickup_end,
        expires_at=food.expires_at,
        pickup_location=food.pickup_location,
        pickup_instructions=food.pickup_instructions,
        photo_urls=photo_urls,
        credit_value=food.credit_value,
        created_at=food.created_at,
        updated_at=food.updated_at,
        sharer_id=food.sharer_id,
        sharer_name=food.sharer.display_name if food.sharer else "Unknown",
        sharer_apartment=food.sharer.apartment_number if food.sharer else None,
        building_id=food.building_id,
        claimed_by_id=food.claimed_by_id,
        claimed_at=food.claimed_at,
        is_available=food.is_available,
        is_expired=food.is_expired,
        time_remaining_minutes=time_remaining_minutes,
        pickup_window_active=food.pickup_window_active,
    )


def _convert_food_to_summary(food) -> FoodSummary:
    """Convert Food model to summary schema."""
    # Calculate time remaining
    time_remaining_minutes = None
    if food.expires_at > datetime.utcnow():
        delta = food.expires_at - datetime.utcnow()
        time_remaining_minutes = int(delta.total_seconds() / 60)
    
    # Parse photo URLs
    photo_urls = None
    if food.photo_urls:
        import json
        try:
            photo_urls = json.loads(food.photo_urls)
        except:
            photo_urls = [food.photo_urls]
    
    return FoodSummary(
        id=food.id,
        title=food.title,
        category=food.category,
        serving_size=food.serving_size,
        status=food.status,
        pickup_start=food.pickup_start,
        pickup_end=food.pickup_end,
        expires_at=food.expires_at,
        photo_urls=photo_urls,
        credit_value=food.credit_value,
        sharer_name=food.sharer.display_name if food.sharer else "Unknown",
        sharer_apartment=food.sharer.apartment_number if food.sharer else None,
        is_available=food.is_available,
        time_remaining_minutes=time_remaining_minutes,
    )


@router.post("/", response_model=FoodResponse)
async def create_food_post(
    food_data: FoodCreate,
    db: AsyncSession = Depends(get_db_session),
) -> FoodResponse:
    """Create a new food post."""
    logger.info("Food post creation requested", title=food_data.title)
    
    try:
        food_service = FoodService(db)
        
        # TODO: Get user ID from JWT token
        # For now, use sample user for testing
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        food = await food_service.create_food_post(
            user_id=user.id,
            title=food_data.title,
            description=food_data.description,
            category=food_data.category,
            serving_size=food_data.serving_size,
            ingredients=food_data.ingredients,
            allergens=food_data.allergens,
            dietary_info=food_data.dietary_info,
            pickup_start=food_data.pickup_start,
            pickup_end=food_data.pickup_end,
            pickup_location=food_data.pickup_location,
            pickup_instructions=food_data.pickup_instructions,
            credit_value=food_data.credit_value,
        )
        
        if not food:
            raise HTTPException(status_code=400, detail="Failed to create food post")
        
        await db.commit()
        
        # Send confirmation notification
        notification_service = NotificationService(db)
        await notification_service.send_food_posted_confirmation(user.id, food.id)
        
        return _convert_food_to_response(food)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating food post", error=str(e), exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/upload-photo", response_model=PhotoUploadResponse)
async def upload_food_photo(
    file: UploadFile = File(...),
    user_id: str = Query(...),  # TODO: Get from JWT
    food_id: str = Query(...),
    db: AsyncSession = Depends(get_db_session),
) -> PhotoUploadResponse:
    """Upload photo for a food post."""
    logger.info("Photo upload requested", food_id=food_id, filename=file.filename)
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (max 10MB)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        # Save photo
        photo_service = PhotoService()
        result = await photo_service.save_photo(
            photo_data=content,
            user_id=user_id,
            food_id=food_id,
            content_type=file.content_type,
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to save photo")
        
        original_url, thumbnail_url = result
        
        return PhotoUploadResponse(
            success=True,
            message="Photo uploaded successfully",
            original_url=original_url,
            thumbnail_url=thumbnail_url,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error uploading photo", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/browse", response_model=FoodBrowseResponse)
async def browse_available_foods(
    category: Optional[FoodCategory] = Query(None),
    dietary_info: Optional[str] = Query(None),
    exclude_allergens: Optional[str] = Query(None),  # Comma-separated list
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session),
) -> FoodBrowseResponse:
    """Browse available food posts with filters."""
    logger.info(
        "Food browse requested",
        category=category,
        dietary_info=dietary_info,
        exclude_allergens=exclude_allergens,
        limit=limit,
        offset=offset,
    )
    
    try:
        food_service = FoodService(db)
        
        # TODO: Get user ID from JWT token
        # For now, use sample user for testing
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Parse exclude allergens
        exclude_allergens_list = None
        if exclude_allergens:
            exclude_allergens_list = [a.strip() for a in exclude_allergens.split(",")]
        
        foods = await food_service.browse_available_food(
            user_id=user.id,
            category=category,
            dietary_info=dietary_info,
            exclude_allergens=exclude_allergens_list,
            limit=limit,
            offset=offset,
        )
        
        # Convert to summaries
        food_summaries = [_convert_food_to_summary(food) for food in foods]
        
        return FoodBrowseResponse(
            foods=food_summaries,
            total_count=len(food_summaries),  # TODO: Get actual count
            page=offset // limit + 1,
            page_size=limit,
            has_more=len(food_summaries) == limit,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error browsing foods", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{food_id}", response_model=FoodResponse)
async def get_food_post(
    food_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> FoodResponse:
    """Get food post by ID."""
    logger.info("Food post requested", food_id=food_id)
    
    try:
        food_service = FoodService(db)
        food = await food_service.get_food_by_id(food_id)
        
        if not food:
            raise HTTPException(status_code=404, detail="Food post not found")
        
        return _convert_food_to_response(food)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting food post", food_id=food_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{food_id}", response_model=FoodResponse)
async def update_food_post(
    food_id: str,
    food_update: FoodUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> FoodResponse:
    """Update food post."""
    logger.info("Food post update requested", food_id=food_id)
    
    try:
        food_service = FoodService(db)
        
        # TODO: Get user ID from JWT token
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update with provided data
        update_data = food_update.dict(exclude_unset=True)
        updated_food = await food_service.update_food_post(
            food_id=food_id,
            user_id=user.id,
            **update_data
        )
        
        if not updated_food:
            raise HTTPException(status_code=400, detail="Failed to update food post")
        
        await db.commit()
        
        return _convert_food_to_response(updated_food)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating food post", food_id=food_id, error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{food_id}/claim", response_model=ClaimFoodResponse)
async def claim_food(
    food_id: str,
    claim_request: ClaimFoodRequest,
    db: AsyncSession = Depends(get_db_session),
) -> ClaimFoodResponse:
    """Claim a food post."""
    logger.info("Food claim requested", food_id=food_id)
    
    try:
        food_service = FoodService(db)
        
        # TODO: Get user ID from JWT token
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        exchange = await food_service.claim_food(
            food_id=food_id,
            user_id=user.id,
            notes=claim_request.notes,
        )
        
        if not exchange:
            raise HTTPException(status_code=400, detail="Failed to claim food")
        
        await db.commit()
        
        # Send notifications
        notification_service = NotificationService(db)
        await notification_service.send_food_request_notification(
            sharer_id=exchange.sharer_id,
            recipient_id=exchange.recipient_id,
            food_id=food_id,
            exchange_id=exchange.id,
        )
        await notification_service.send_request_confirmation(
            recipient_id=exchange.recipient_id,
            food_id=food_id,
            exchange_id=exchange.id,
        )
        
        return ClaimFoodResponse(
            success=True,
            message="Food claimed successfully",
            exchange_id=exchange.id,
            pickup_details={
                "location": exchange.pickup_location,
                "instructions": exchange.pickup_instructions,
                "scheduled_time": exchange.scheduled_pickup_at.isoformat(),
            },
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error claiming food", food_id=food_id, error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{food_id}/claim", response_model=dict)
async def unclaim_food(
    food_id: str,
    reason: str = Query("Changed mind"),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Unclaim a food post."""
    logger.info("Food unclaim requested", food_id=food_id)
    
    try:
        food_service = FoodService(db)
        
        # TODO: Get user ID from JWT token
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = await food_service.unclaim_food(
            food_id=food_id,
            user_id=user.id,
            reason=reason,
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to unclaim food")
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Food unclaimed successfully",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error unclaiming food", food_id=food_id, error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{food_id}/expire", response_model=dict)
async def expire_food_post(
    food_id: str,
    reason: str = Query("No longer available"),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Manually expire a food post."""
    logger.info("Food expiration requested", food_id=food_id)
    
    try:
        food_service = FoodService(db)
        
        # TODO: Get user ID from JWT token
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = await food_service.expire_food_post(
            food_id=food_id,
            user_id=user.id,
            reason=reason,
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to expire food post")
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Food post expired successfully",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error expiring food post", food_id=food_id, error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user/posts", response_model=List[FoodResponse])
async def get_user_food_posts(
    include_expired: bool = Query(False),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db_session),
) -> List[FoodResponse]:
    """Get current user's food posts."""
    logger.info("User food posts requested", include_expired=include_expired)
    
    try:
        food_service = FoodService(db)
        
        # TODO: Get user ID from JWT token
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        foods = await food_service.get_user_posts(
            user_id=user.id,
            include_expired=include_expired,
            limit=limit,
        )
        
        return [_convert_food_to_response(food) for food in foods]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting user food posts", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")