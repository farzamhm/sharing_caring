"""Telegram webhook endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request
from telegram import Update

from ...core.config import get_settings
from ...core.logging import get_logger

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)


@router.post("/telegram")
async def telegram_webhook(request: Request) -> dict:
    """Handle Telegram webhook updates."""
    try:
        # Verify webhook secret if configured
        if settings.telegram_webhook_secret:
            secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if secret_header != settings.telegram_webhook_secret:
                logger.warning("Invalid webhook secret received")
                raise HTTPException(status_code=403, detail="Invalid webhook secret")
        
        # Parse update data
        update_data = await request.json()
        update = Update.de_json(update_data, None)
        
        if not update:
            logger.warning("Invalid update received", update_data=update_data)
            raise HTTPException(status_code=400, detail="Invalid update")
        
        # TODO: Process update with bot dispatcher
        # This will be implemented when we create the bot module
        logger.info(
            "Received Telegram update",
            update_id=update.update_id,
            user_id=update.effective_user.id if update.effective_user else None,
            chat_id=update.effective_chat.id if update.effective_chat else None,
        )
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error("Error processing webhook", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/telegram/info")
async def webhook_info() -> dict:
    """Get webhook configuration info."""
    return {
        "webhook_url": settings.telegram_webhook_url,
        "secret_configured": bool(settings.telegram_webhook_secret),
    }