"""Admin dashboard endpoints."""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db_session
from ...core.logging import get_logger
from ...services.admin_service import AdminService

router = APIRouter()
logger = get_logger(__name__)


@router.get("/stats/platform")
async def get_platform_stats(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get platform-wide statistics."""
    logger.info("Platform stats requested", days=days)
    
    try:
        admin_service = AdminService(db)
        stats = await admin_service.get_platform_stats(days=days)
        return stats
        
    except Exception as e:
        logger.error("Error getting platform stats", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/building/{building_id}")
async def get_building_stats(
    building_id: str,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get statistics for a specific building."""
    logger.info("Building stats requested", building_id=building_id, days=days)
    
    try:
        admin_service = AdminService(db)
        stats = await admin_service.get_building_stats(building_id=building_id, days=days)
        
        if not stats:
            raise HTTPException(status_code=404, detail="Building not found")
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting building stats", building_id=building_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/users/{user_id}/activity")
async def get_user_activity(
    user_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get detailed activity for a specific user."""
    logger.info("User activity requested", user_id=user_id)
    
    try:
        admin_service = AdminService(db)
        activity = await admin_service.get_user_activity(user_id=user_id)
        
        if not activity:
            raise HTTPException(status_code=404, detail="User not found")
        
        return activity
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting user activity", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/exchanges/problematic")
async def get_problematic_exchanges(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get exchanges that may need admin attention."""
    logger.info("Problematic exchanges requested", days=days)
    
    try:
        admin_service = AdminService(db)
        exchanges = await admin_service.get_problematic_exchanges(days=days)
        
        return {
            "exchanges": exchanges,
            "total_count": len(exchanges),
            "period_days": days,
            "checked_at": datetime.utcnow(),
        }
        
    except Exception as e:
        logger.error("Error getting problematic exchanges", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def get_system_health(
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get system health indicators."""
    logger.info("System health check requested")
    
    try:
        admin_service = AdminService(db)
        health = await admin_service.get_system_health()
        return health
        
    except Exception as e:
        logger.error("Error getting system health", error=str(e), exc_info=True)
        # Return unhealthy status instead of error
        return {
            "status": "unhealthy",
            "score": 0,
            "database_connected": False,
            "issues": [f"Health check failed: {str(e)}"],
            "checked_at": datetime.utcnow()
        }


@router.post("/exchanges/{exchange_id}/intervene")
async def admin_intervene_exchange(
    exchange_id: str,
    action: str = Query(..., regex="^(cancel|complete|reset)$"),
    reason: str = Query(..., min_length=1, max_length=500),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Admin intervention for problematic exchanges."""
    logger.info("Admin intervention requested", exchange_id=exchange_id, action=action)
    
    try:
        # Import services
        from ...services.exchange_service import ExchangeService
        from ...services.notification_service import NotificationService
        
        exchange_service = ExchangeService(db)
        notification_service = NotificationService(db)
        
        # Get exchange
        exchange = await exchange_service.get_exchange_by_id(exchange_id)
        if not exchange:
            raise HTTPException(status_code=404, detail="Exchange not found")
        
        success = False
        message = ""
        
        if action == "cancel":
            success = await exchange_service.cancel_exchange(
                exchange_id=exchange_id,
                user_id="admin",  # Special admin user ID
                reason=f"Admin intervention: {reason}"
            )
            message = "Exchange cancelled by admin"
            
        elif action == "complete":
            success = await exchange_service.complete_exchange(
                exchange_id=exchange_id,
                user_id="admin",
                rating=None,
                notes=f"Admin intervention: {reason}"
            )
            message = "Exchange completed by admin"
            
        elif action == "reset":
            # Reset exchange to pending status
            from ...models.exchange import ExchangeStatus
            exchange.status = ExchangeStatus.PENDING
            exchange.sharer_confirmed = False
            exchange.recipient_confirmed = False
            exchange.sharer_confirmed_at = None
            exchange.recipient_confirmed_at = None
            success = True
            message = "Exchange reset to pending status"
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Failed to {action} exchange")
        
        await db.commit()
        
        # Notify participants
        await notification_service.send_admin_notification(
            user_id=exchange.sharer_id,
            message=f"Admin has {action}ed your exchange: {reason}"
        )
        await notification_service.send_admin_notification(
            user_id=exchange.recipient_id,
            message=f"Admin has {action}ed your exchange: {reason}"
        )
        
        return {
            "success": True,
            "message": message,
            "action": action,
            "exchange_id": exchange_id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in admin intervention", exchange_id=exchange_id, error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/dashboard")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get summary data for admin dashboard."""
    logger.info("Dashboard summary requested")
    
    try:
        admin_service = AdminService(db)
        
        # Get key metrics
        platform_stats = await admin_service.get_platform_stats(days=7)
        system_health = await admin_service.get_system_health()
        problematic_exchanges = await admin_service.get_problematic_exchanges(days=3)
        
        # Summary counters
        active_users = platform_stats["users"]["active"]
        recent_posts = platform_stats["food_posts"]["recent"]
        success_rate = platform_stats["exchanges"]["success_rate"]
        issues_count = len(problematic_exchanges)
        
        return {
            "overview": {
                "active_users_7d": active_users,
                "food_posts_7d": recent_posts,
                "exchange_success_rate": success_rate,
                "issues_requiring_attention": issues_count,
            },
            "health": {
                "status": system_health["status"],
                "score": system_health["score"],
            },
            "alerts": problematic_exchanges[:5],  # Top 5 most urgent
            "generated_at": datetime.utcnow(),
        }
        
    except Exception as e:
        logger.error("Error getting dashboard summary", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard_html():
    """Serve the admin dashboard HTML interface."""
    import os
    
    # Read the HTML template
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "templates",
        "admin_dashboard.html"
    )
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Admin Dashboard Template Not Found</h1><p>Please check template file exists.</p>",
            status_code=404
        )