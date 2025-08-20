#!/usr/bin/env python3
"""Telegram bot runner."""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bot.main import bot_instance
from src.core.config import get_settings
from src.core.logging import configure_logging, get_logger

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


async def main():
    """Run the bot."""
    try:
        logger.info("🤖 Starting Neighborhood Sharing Platform Bot...")
        logger.info(f"Environment: {settings.environment}")
        logger.info("=" * 50)
        
        if settings.telegram_webhook_url:
            logger.info("Starting bot in webhook mode", webhook_url=settings.telegram_webhook_url)
            await bot_instance.start_webhook(
                webhook_url=settings.telegram_webhook_url,
                port=8443
            )
        else:
            logger.info("Starting bot in polling mode")
            await bot_instance.start_polling()
        
        # Keep the bot running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error("Bot error", error=str(e), exc_info=True)
    finally:
        await bot_instance.stop()


if __name__ == "__main__":
    if not settings.telegram_bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN is required")
        sys.exit(1)
    
    asyncio.run(main())