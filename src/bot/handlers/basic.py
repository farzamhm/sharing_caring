"""Basic message handlers."""

from telegram import Update
from telegram.ext import ContextTypes

from ...core.logging import get_logger

logger = get_logger(__name__)


async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    
    if not user or not chat or not message:
        return
    
    try:
        # For now, provide helpful guidance
        response = """
I'm not sure what you mean. Here are some things you can do:

🍲 /share - Share food with neighbors
🔍 /browse - Look for available food  
📋 /menu - Show main menu
❓ /help - Get help and see all commands

Or use the menu buttons to navigate!
        """
        
        await message.reply_text(response)
        
    except Exception as e:
        logger.error(
            "Error in echo handler",
            user_id=user.id,
            error=str(e),
            exc_info=True
        )


async def unknown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    
    if not user or not chat or not message:
        return
    
    try:
        response = """
❓ Unknown command. Here are the available commands:

**Main Commands:**
/start - Get started
/menu - Show main menu  
/share - Share food
/browse - Browse available food
/myposts - Your posts
/profile - Your profile
/help - Full help

Type /help for more details!
        """
        
        await message.reply_text(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(
            "Error in unknown handler",
            user_id=user.id,
            error=str(e),
            exc_info=True
        )