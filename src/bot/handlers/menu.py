"""Main menu handlers."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ...core.logging import get_logger, log_bot_interaction

logger = get_logger(__name__)


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /menu command."""
    user = update.effective_user
    chat = update.effective_chat
    
    if not user or not chat:
        return
    
    try:
        log_bot_interaction(
            user_id=user.id,
            username=user.username or "unknown",
            command="menu", 
            success=True,
        )
        
        # TODO: Check user registration status
        # For now, assume user is registered
        
        menu_text = f"""
🏠 **Neighborhood Sharing Platform**

Hello {user.first_name}! What would you like to do today?

**Food Sharing:**
🍲 Share food with your neighbors
🔍 Browse available food in your building
📋 Manage your food posts

**Your Account:**
👤 View and edit your profile  
⭐ Check your credit balance
📊 View sharing history

Choose an option below:
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🍲 Share Food", callback_data="main_menu_share"),
                InlineKeyboardButton("🔍 Browse Food", callback_data="main_menu_browse"),
            ],
            [
                InlineKeyboardButton("📋 My Posts", callback_data="main_menu_myposts"),
                InlineKeyboardButton("⭐ My Credits", callback_data="main_menu_credits"),
            ],
            [
                InlineKeyboardButton("👤 Profile", callback_data="main_menu_profile"),
                InlineKeyboardButton("📊 History", callback_data="main_menu_history"),
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data="main_menu_help"),
                InlineKeyboardButton("⚙️ Settings", callback_data="main_menu_settings"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=chat.id,
            text=menu_text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
        
    except Exception as e:
        logger.error(
            "Error in menu handler",
            user_id=user.id,
            error=str(e),
            exc_info=True
        )


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu button callbacks."""
    query = update.callback_query
    user = update.effective_user
    
    if not query or not user:
        return
    
    await query.answer()
    
    try:
        callback_data = query.data
        action = callback_data.replace("main_menu_", "")
        
        if action == "share":
            await _handle_share_action(query, context)
        elif action == "browse":
            await _handle_browse_action(query, context)
        elif action == "myposts":
            await _handle_myposts_action(query, context)
        elif action == "credits":
            await _handle_credits_action(query, context)
        elif action == "profile":
            await _handle_profile_action(query, context)
        elif action == "history":
            await _handle_history_action(query, context)
        elif action == "help":
            await _handle_help_action(query, context)
        elif action == "settings":
            await _handle_settings_action(query, context)
        else:
            await query.edit_message_text("Unknown action. Please try again.")
    
    except Exception as e:
        logger.error(
            "Error in main menu callback",
            user_id=user.id,
            error=str(e),
            exc_info=True
        )


async def _handle_share_action(query, context):
    """Handle share food action."""
    text = """
🍲 **Share Food**

Ready to share some delicious food with your neighbors?

I'll guide you through posting your food item step by step:
1. 📸 Upload a photo
2. 📝 Add description and ingredients  
3. ⏰ Set pickup time
4. 📍 Choose pickup location
5. ⚠️ List any allergens

Let's start! What would you like to share today?
    """
    
    keyboard = [
        [InlineKeyboardButton("📸 Start Sharing", callback_data="start_food_share")],
        [InlineKeyboardButton("← Back to Menu", callback_data="back_to_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def _handle_browse_action(query, context):
    """Handle browse food action.""" 
    text = """
🔍 **Browse Available Food**

Looking for something tasty? Here's what's available in your building:

Loading available food items...
    """
    
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_food_list")],
        [InlineKeyboardButton("← Back to Menu", callback_data="back_to_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def _handle_myposts_action(query, context):
    """Handle my posts action."""
    # TODO: Implement my posts view
    await query.edit_message_text("📋 My Posts - Coming soon!")


async def _handle_credits_action(query, context):
    """Handle credits action."""
    # TODO: Implement credits view
    await query.edit_message_text("⭐ Credits - Coming soon!")


async def _handle_profile_action(query, context):
    """Handle profile action."""
    # TODO: Implement profile view
    await query.edit_message_text("👤 Profile - Coming soon!")


async def _handle_history_action(query, context):
    """Handle history action."""
    # TODO: Implement history view
    await query.edit_message_text("📊 History - Coming soon!")


async def _handle_help_action(query, context):
    """Handle help action."""
    # TODO: Implement help view
    await query.edit_message_text("❓ Help - Coming soon!")


async def _handle_settings_action(query, context):
    """Handle settings action."""
    # TODO: Implement settings view
    await query.edit_message_text("⚙️ Settings - Coming soon!")