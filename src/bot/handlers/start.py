"""Start command handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ...core.logging import get_logger, log_bot_interaction

logger = get_logger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    chat = update.effective_chat
    
    if not user or not chat:
        return
    
    try:
        # Log the interaction
        log_bot_interaction(
            user_id=user.id,
            username=user.username or "unknown",
            command="start",
            success=True,
        )
        
        # Check if user is already registered
        # TODO: Check user registration status from database
        
        welcome_text = f"""
🏠 **Welcome to Neighborhood Sharing Platform!**

Hi {user.first_name}! I'm here to help you share and discover food with your neighbors.

**What you can do:**
🍲 Share extra food with neighbors
🔍 Browse available food in your building
⭐ Earn credits for sharing
💬 Coordinate pickups easily

To get started, let's set up your profile. I'll need to verify your phone number and building information.

Ready to begin?
        """
        
        # Create inline keyboard
        keyboard = [
            [InlineKeyboardButton("📝 Get Started", callback_data="start_registration")],
            [InlineKeyboardButton("❓ Learn More", callback_data="learn_more")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=chat.id,
            text=welcome_text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
        
    except Exception as e:
        logger.error(
            "Error in start handler",
            user_id=user.id,
            error=str(e),
            exc_info=True
        )
        
        await context.bot.send_message(
            chat_id=chat.id,
            text="Sorry, I encountered an error. Please try again later.",
        )