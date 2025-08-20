"""Exchange management endpoints."""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db_session
from ...core.logging import get_logger
from ...services.exchange_service import ExchangeService
from ..schemas.exchange import (
    ExchangeResponse,
    ExchangeSummary,
    ExchangeConfirmRequest,
    ExchangeCompleteRequest,
    ExchangeCancelRequest,
    ExchangeNoShowRequest,
)
from ...models.exchange import ExchangeStatus

router = APIRouter()
logger = get_logger(__name__)


def _convert_exchange_to_response(exchange, current_user_id: str) -> ExchangeResponse:
    """Convert Exchange model to response schema."""
    # Get photo URL from food
    food_photo_url = None
    if exchange.food and exchange.food.photo_urls:
        import json
        try:
            photo_urls = json.loads(exchange.food.photo_urls)
            food_photo_url = photo_urls[0] if photo_urls else None
        except:
            food_photo_url = exchange.food.photo_urls
    
    return ExchangeResponse(
        id=exchange.id,
        status=exchange.status,
        credit_amount=exchange.credit_amount,
        credits_transferred=exchange.credits_transferred,
        sharer_id=exchange.sharer_id,
        recipient_id=exchange.recipient_id,
        sharer_name=exchange.sharer.display_name if exchange.sharer else "Unknown",
        recipient_name=exchange.recipient.display_name if exchange.recipient else "Unknown",
        food_id=exchange.food_id,
        food_title=exchange.food.title if exchange.food else "Unknown",
        food_photo_url=food_photo_url,
        pickup_location=exchange.pickup_location,
        pickup_instructions=exchange.pickup_instructions,
        scheduled_pickup_at=exchange.scheduled_pickup_at,
        notes=exchange.sharer_notes if current_user_id == exchange.sharer_id else exchange.recipient_notes,
        sharer_confirmed=exchange.sharer_confirmed,
        recipient_confirmed=exchange.recipient_confirmed,
        sharer_confirmed_at=exchange.sharer_confirmed_at,
        recipient_confirmed_at=exchange.recipient_confirmed_at,
        actual_pickup_at=exchange.actual_pickup_at,
        completed_at=exchange.completed_at,
        cancelled_at=exchange.cancelled_at,
        sharer_rating=exchange.sharer_rating,
        recipient_rating=exchange.recipient_rating,
        sharer_notes=exchange.sharer_notes,
        recipient_notes=exchange.recipient_notes,
        cancelled_by_id=exchange.cancelled_by_id,
        cancellation_reason=exchange.cancellation_reason,
        created_at=exchange.created_at,
        updated_at=exchange.updated_at,
        is_confirmed=exchange.is_confirmed,
        is_active=exchange.is_active,
        is_completed=exchange.is_completed,
        is_cancelled=exchange.is_cancelled,
    )


def _convert_exchange_to_summary(exchange, current_user_id: str) -> ExchangeSummary:
    """Convert Exchange model to summary schema."""
    # Determine the other user
    is_sharer = current_user_id == exchange.sharer_id
    other_user = exchange.recipient if is_sharer else exchange.sharer
    other_user_name = other_user.display_name if other_user else "Unknown"
    other_user_apartment = other_user.apartment_number if other_user else None
    
    # Get photo URL
    food_photo_url = None
    if exchange.food and exchange.food.photo_urls:
        import json
        try:
            photo_urls = json.loads(exchange.food.photo_urls)
            food_photo_url = photo_urls[0] if photo_urls else None
        except:
            food_photo_url = exchange.food.photo_urls
    
    # Check if overdue
    is_overdue = (
        exchange.status == ExchangeStatus.CONFIRMED 
        and exchange.scheduled_pickup_at 
        and exchange.scheduled_pickup_at < datetime.utcnow()
    )
    
    return ExchangeSummary(
        id=exchange.id,
        status=exchange.status,
        food_title=exchange.food.title if exchange.food else "Unknown",
        food_photo_url=food_photo_url,
        other_user_name=other_user_name,
        other_user_apartment=other_user_apartment,
        pickup_location=exchange.pickup_location,
        scheduled_pickup_at=exchange.scheduled_pickup_at,
        credit_amount=exchange.credit_amount,
        created_at=exchange.created_at,
        needs_confirmation=exchange.status == ExchangeStatus.PENDING,
        is_overdue=is_overdue,
    )


@router.get("/", response_model=List[ExchangeSummary])
async def list_exchanges(
    status: Optional[ExchangeStatus] = Query(None),
    role: Optional[str] = Query(None, regex="^(sharer|recipient)$"),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session),
) -> List[ExchangeSummary]:
    """List user's exchanges."""
    logger.info("Exchange list requested", status=status, role=role, limit=limit, offset=offset)
    
    try:
        exchange_service = ExchangeService(db)
        
        # TODO: Get user ID from JWT token
        # For now, use sample user for testing
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        exchanges = await exchange_service.get_user_exchanges(
            user_id=user.id,
            role=role,
            status=status,
            limit=limit,
            offset=offset,
        )
        
        return [_convert_exchange_to_summary(exchange, user.id) for exchange in exchanges]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error listing exchanges", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/active", response_model=List[ExchangeSummary])
async def list_active_exchanges(
    db: AsyncSession = Depends(get_db_session),
) -> List[ExchangeSummary]:
    """List user's active exchanges (pending/confirmed)."""
    logger.info("Active exchanges requested")
    
    try:
        exchange_service = ExchangeService(db)
        
        # TODO: Get user ID from JWT token
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        exchanges = await exchange_service.get_active_exchanges(user.id)
        
        return [_convert_exchange_to_summary(exchange, user.id) for exchange in exchanges]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting active exchanges", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{exchange_id}", response_model=ExchangeResponse)
async def get_exchange(
    exchange_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> ExchangeResponse:
    """Get exchange by ID."""
    logger.info("Exchange details requested", exchange_id=exchange_id)
    
    try:
        exchange_service = ExchangeService(db)
        exchange = await exchange_service.get_exchange_by_id(exchange_id)
        
        if not exchange:
            raise HTTPException(status_code=404, detail="Exchange not found")
        
        # TODO: Get user ID from JWT token
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify user is part of this exchange
        if user.id not in [exchange.sharer_id, exchange.recipient_id]:
            raise HTTPException(status_code=403, detail="Not authorized to view this exchange")
        
        return _convert_exchange_to_response(exchange, user.id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting exchange", exchange_id=exchange_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{exchange_id}/confirm", response_model=dict)
async def confirm_exchange(
    exchange_id: str,
    confirm_request: ExchangeConfirmRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Confirm an exchange."""
    logger.info("Exchange confirmation requested", exchange_id=exchange_id)
    
    try:
        exchange_service = ExchangeService(db)
        
        # TODO: Get user ID from JWT token
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = await exchange_service.confirm_exchange(
            exchange_id=exchange_id,
            user_id=user.id,
            notes=confirm_request.notes,
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to confirm exchange")
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Exchange confirmed successfully",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error confirming exchange", exchange_id=exchange_id, error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{exchange_id}/complete", response_model=dict)
async def complete_exchange(
    exchange_id: str,
    complete_request: ExchangeCompleteRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Mark exchange as completed."""
    logger.info("Exchange completion requested", exchange_id=exchange_id)
    
    try:
        exchange_service = ExchangeService(db)
        
        # TODO: Get user ID from JWT token
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = await exchange_service.complete_exchange(
            exchange_id=exchange_id,
            user_id=user.id,
            rating=complete_request.rating,
            notes=complete_request.notes,
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to complete exchange")
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Exchange completed successfully",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error completing exchange", exchange_id=exchange_id, error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{exchange_id}/cancel", response_model=dict)
async def cancel_exchange(
    exchange_id: str,
    cancel_request: ExchangeCancelRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Cancel an exchange."""
    logger.info("Exchange cancellation requested", exchange_id=exchange_id)
    
    try:
        exchange_service = ExchangeService(db)
        
        # TODO: Get user ID from JWT token
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = await exchange_service.cancel_exchange(
            exchange_id=exchange_id,
            user_id=user.id,
            reason=cancel_request.reason,
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to cancel exchange")
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Exchange cancelled successfully",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error cancelling exchange", exchange_id=exchange_id, error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{exchange_id}/no-show", response_model=dict)
async def report_no_show(
    exchange_id: str,
    no_show_request: ExchangeNoShowRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Report a no-show for an exchange."""
    logger.info("No-show report requested", exchange_id=exchange_id)
    
    try:
        exchange_service = ExchangeService(db)
        
        # TODO: Get user ID from JWT token
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = await exchange_service.mark_no_show(
            exchange_id=exchange_id,
            user_id=user.id,
            no_show_user_id=no_show_request.no_show_user_id,
            notes=no_show_request.notes,
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to report no-show")
        
        await db.commit()
        
        return {
            "success": True,
            "message": "No-show reported successfully",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error reporting no-show", exchange_id=exchange_id, error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")