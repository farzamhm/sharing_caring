"""Main Telegram bot implementation."""

from typing import Optional

from telegram import Bot, Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters

from ..core.config import get_settings
from ..core.logging import configure_logging, get_logger
from .handlers import (
    command_handlers,
    conversation_handlers, 
    message_handlers,
    callback_query_handlers,
)
from .handlers.start import start_handler
from .handlers.help import help_handler
from .handlers.registration import registration_conversation
from .handlers.food import food_conversation
from .handlers.profile import profile_conversation

settings = get_settings()
logger = get_logger(__name__)


class SharingBot:
    """Main bot class."""
    
    def __init__(self) -> None:
        self.bot: Optional[Bot] = None
        self.application: Optional[Application] = None
    
    async def setup(self) -> None:
        """Set up the bot application."""
        logger.info("Setting up Telegram bot...")
        
        # Create application
        self.application = (
            ApplicationBuilder()
            .token(settings.telegram_bot_token)
            .build()
        )
        
        self.bot = self.application.bot
        
        # Add handlers
        await self._add_handlers()
        
        logger.info("Bot setup completed", bot_username=self.bot.username)
    
    async def _add_handlers(self) -> None:
        """Add all command and message handlers."""
        if not self.application:
            return
        
        # Add conversation handlers first (they have priority)
        self.application.add_handler(registration_conversation)
        self.application.add_handler(food_conversation)
        self.application.add_handler(profile_conversation)
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", start_handler))
        self.application.add_handler(CommandHandler("help", help_handler))
        
        # Add command handlers from handlers module
        for pattern, handler in command_handlers.items():
            self.application.add_handler(CommandHandler(pattern, handler))
        
        # Add callback query handlers
        for pattern, handler in callback_query_handlers.items():
            from telegram.ext import CallbackQueryHandler
            self.application.add_handler(CallbackQueryHandler(handler, pattern=pattern))
        
        # Add message handlers (catch-all, so add last)
        for filter_type, handler in message_handlers.items():
            self.application.add_handler(MessageHandler(filter_type, handler))
        
        logger.info("Added all bot handlers")
    
    async def start_polling(self) -> None:
        """Start bot with polling."""
        if not self.application:
            await self.setup()
        
        logger.info("Starting bot polling...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
    
    async def start_webhook(self, webhook_url: str, port: int = 8443) -> None:
        """Start bot with webhook."""
        if not self.application:
            await self.setup()
        
        logger.info("Starting bot webhook", webhook_url=webhook_url, port=port)
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="webhook/telegram",
            webhook_url=webhook_url,
            secret_token=settings.telegram_webhook_secret,
        )
    
    async def stop(self) -> None:
        """Stop the bot."""
        if self.application:
            logger.info("Stopping bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
    
    async def process_update(self, update: Update) -> None:
        """Process a single update (for webhook mode)."""
        if self.application:
            await self.application.process_update(update)


# Global bot instance
bot_instance = SharingBot()


async def get_bot() -> SharingBot:
    """Get the bot instance."""
    return bot_instance