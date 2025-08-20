"""Profile and settings handlers."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
)

from ...core.logging import get_logger

logger = get_logger(__name__)


async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /profile command."""
    user = update.effective_user
    chat = update.effective_chat
    
    if not user or not chat:
        return
    
    try:
        # TODO: Get user data from database
        text = f"""
👤 **Your Profile**

**Name:** {user.first_name} {user.last_name or ''}
**Username:** @{user.username or 'Not set'}
**Building:** Sample Apartment Complex
**Apartment:** 3B
**Phone:** +1-xxx-xxx-xxxx (verified ✅)

**Account Stats:**
⭐ Credits: 15
🍲 Food shared: 8 items  
🔍 Food claimed: 5 items
🏆 Community rank: #12

**Dietary Info:**
🥗 Restrictions: Vegetarian
⚠️ Allergies: Nuts

Want to update your profile?
        """
        
        keyboard = [
            [
                InlineKeyboardButton("✏️ Edit Profile", callback_data="edit_profile"),
                InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications"),
            ],
            [
                InlineKeyboardButton("🛡️ Privacy", callback_data="settings_privacy"),
                InlineKeyboardButton("🏆 Leaderboard", callback_data="view_leaderboard"),
            ],
            [InlineKeyboardButton("📋 Back to Menu", callback_data="show_main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=chat.id,
            text=text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
        
    except Exception as e:
        logger.error("Error in profile handler", user_id=user.id, error=str(e), exc_info=True)


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle settings callbacks."""
    query = update.callback_query
    user = update.effective_user
    
    if not query or not user:
        return
    
    await query.answer()
    
    try:
        callback_data = query.data
        
        if "notifications" in callback_data:
            await _handle_notification_settings(query, context)
        elif "privacy" in callback_data:
            await _handle_privacy_settings(query, context)
        else:
            await query.edit_message_text("Settings - Coming soon!")
            
    except Exception as e:
        logger.error("Error in settings callback", user_id=user.id, error=str(e), exc_info=True)


async def _handle_notification_settings(query, context):
    """Handle notification settings."""
    text = """
🔔 **Notification Settings**

Control what notifications you receive:

✅ New food available (ON)
✅ Food claimed (ON) 
✅ Exchange confirmations (ON)
❌ Daily summaries (OFF)
✅ Safety alerts (ON)

**Quiet Hours:** 10 PM - 8 AM
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🔕 Toggle All", callback_data="toggle_all_notifications"),
        ],
        [
            InlineKeyboardButton("⏰ Quiet Hours", callback_data="set_quiet_hours"),
            InlineKeyboardButton("📧 Email Settings", callback_data="email_settings"),
        ],
        [InlineKeyboardButton("← Back", callback_data="show_profile")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def _handle_privacy_settings(query, context):
    """Handle privacy settings."""
    text = """
🛡️ **Privacy Settings**

Control what information other users can see:

✅ Name and apartment (Visible to neighbors)
✅ Food posts (Public in building)
❌ Phone number (Only during active exchanges)
✅ Dietary restrictions (Helps with food matching)

**Profile Visibility:** Building residents only
    """
    
    keyboard = [
        [
            InlineKeyboardButton("👁️ Profile Visibility", callback_data="profile_visibility"),
            InlineKeyboardButton("📱 Phone Privacy", callback_data="phone_privacy"),
        ],
        [InlineKeyboardButton("← Back", callback_data="show_profile")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")


# Placeholder conversation handler for profile editing
profile_conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(lambda u, c: c, pattern="^edit_profile$"),
    ],
    states={},
    fallbacks=[],
)