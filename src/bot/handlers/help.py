"""Help command handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ...core.logging import get_logger, log_bot_interaction

logger = get_logger(__name__)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    user = update.effective_user
    chat = update.effective_chat
    
    if not user or not chat:
        return
    
    try:
        log_bot_interaction(
            user_id=user.id,
            username=user.username or "unknown", 
            command="help",
            success=True,
        )
        
        help_text = """
📱 **Neighborhood Sharing Platform Help**

**Main Commands:**
/start - Get started or restart the bot
/menu - Show main menu
/share - Share food with neighbors
/browse - Browse available food
/myposts - View your food posts
/profile - Manage your profile
/help - Show this help message

**How it works:**
1. 🏠 **Register** - Verify your phone and building
2. 🍲 **Share Food** - Post excess food with photos and details
3. ⭐ **Earn Credits** - Get credits when neighbors claim your food
4. 🔍 **Browse & Claim** - Use credits to claim food from others
5. 🤝 **Coordinate** - Chat with neighbors to arrange pickup

**Safety Guidelines:**
• Only share food you would eat yourself
• List all ingredients and allergens
• Follow pickup time windows
• Meet in safe, common areas

**Credit System:**
• Earn 1 credit per successful share
• Spend 1 credit to claim food
• New users get 10 starter credits

**Need Help?**
Contact our support team or check the safety guidelines for food sharing best practices.
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🍲 Share Food", callback_data="help_share"),
                InlineKeyboardButton("🔍 Browse Food", callback_data="help_browse"),
            ],
            [
                InlineKeyboardButton("⭐ Credits", callback_data="help_credits"),
                InlineKeyboardButton("🛡️ Safety", callback_data="help_safety"),
            ],
            [InlineKeyboardButton("📞 Contact Support", callback_data="contact_support")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=chat.id,
            text=help_text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
        
    except Exception as e:
        logger.error(
            "Error in help handler",
            user_id=user.id,
            error=str(e),
            exc_info=True
        )
        
        await context.bot.send_message(
            chat_id=chat.id,
            text="Sorry, I encountered an error. Please try again later.",
        )