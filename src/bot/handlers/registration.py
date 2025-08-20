"""User registration conversation handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from ...core.logging import get_logger

logger = get_logger(__name__)

# Conversation states
PHONE_NUMBER, BUILDING_INFO, APARTMENT, CONFIRMATION = range(4)


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the registration process."""
    query = update.callback_query
    user = update.effective_user
    
    if not query or not user:
        return ConversationHandler.END
    
    await query.answer()
    
    text = f"""
📝 **Registration - Step 1/3**

Hi {user.first_name}! To ensure safe food sharing, I need to verify a few details.

**Phone Number Verification**
For safety and coordination, please share your phone number. This helps us:
• Verify you're a real person
• Enable direct contact for pickups
• Send important safety notifications

Your number will only be visible to neighbors you're actively exchanging food with.
    """
    
    # Create keyboard with phone sharing button
    keyboard = [[KeyboardButton("📱 Share My Phone Number", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        one_time_keyboard=True, 
        resize_keyboard=True
    )
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown"
    )
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="👆 Please use the button below to share your phone number:",
        reply_markup=reply_markup
    )
    
    return PHONE_NUMBER


async def receive_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and process phone number."""
    user = update.effective_user
    message = update.message
    
    if not user or not message or not message.contact:
        await message.reply_text("Please use the 'Share My Phone Number' button to continue.")
        return PHONE_NUMBER
    
    contact = message.contact
    phone_number = contact.phone_number
    
    # Store phone number in context
    context.user_data['phone_number'] = phone_number
    
    text = f"""
✅ **Phone Number Received**

Thanks! I've received your phone number: {phone_number}

**Step 2/3 - Building Information**

Now I need to know which building you live in. This ensures you only see food from your neighbors and keeps our community safe.

Please enter your building name or address:
    """
    
    # Remove custom keyboard
    from telegram import ReplyKeyboardRemove
    await message.reply_text(
        text,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    
    return BUILDING_INFO


async def receive_building_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive building information."""
    user = update.effective_user
    message = update.message
    
    if not user or not message or not message.text:
        await message.reply_text("Please enter your building name or address.")
        return BUILDING_INFO
    
    building_info = message.text.strip()
    context.user_data['building_info'] = building_info
    
    text = f"""
🏠 **Building Information Received**

Building: {building_info}

**Step 3/3 - Apartment Details**

Finally, what's your apartment number? This helps neighbors know where to meet for pickups.

Examples: 3B, Apt 205, Unit 15, etc.
    """
    
    await message.reply_text(text, parse_mode="Markdown")
    return APARTMENT


async def receive_apartment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive apartment information."""
    user = update.effective_user
    message = update.message
    
    if not user or not message or not message.text:
        await message.reply_text("Please enter your apartment number.")
        return APARTMENT
    
    apartment = message.text.strip()
    context.user_data['apartment'] = apartment
    
    # Show confirmation
    phone = context.user_data.get('phone_number', 'N/A')
    building = context.user_data.get('building_info', 'N/A')
    
    text = f"""
📋 **Registration Summary**

Please confirm your information:

👤 **Name:** {user.first_name} {user.last_name or ''}
📱 **Phone:** {phone}
🏠 **Building:** {building}  
🏢 **Apartment:** {apartment}

Is this information correct?
    """
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_registration"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_registration"),
        ],
        [InlineKeyboardButton("🔄 Edit Info", callback_data="edit_registration")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return CONFIRMATION


async def confirm_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm and complete registration."""
    query = update.callback_query
    user = update.effective_user
    
    if not query or not user:
        return ConversationHandler.END
    
    await query.answer()
    
    # TODO: Save user information to database
    # For now, just complete the flow
    
    success_text = f"""
🎉 **Registration Complete!**

Welcome to the Neighborhood Sharing Platform, {user.first_name}!

**What's next?**
• You've been given 10 starter credits
• You can now share food and browse available items
• Check out /help for tips on safe food sharing

**Your Benefits:**
⭐ Earn credits when neighbors claim your food
🍲 Use credits to claim food from others
🤝 Build connections with your neighbors
🌱 Reduce food waste together

Ready to start sharing?
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🍲 Share Food", callback_data="main_menu_share"),
            InlineKeyboardButton("🔍 Browse Food", callback_data="main_menu_browse"),
        ],
        [InlineKeyboardButton("📋 Show Menu", callback_data="show_main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        success_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END


async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel registration."""
    query = update.callback_query
    
    if query:
        await query.answer()
        await query.edit_message_text(
            "Registration cancelled. You can start again anytime with /start"
        )
    
    context.user_data.clear()
    return ConversationHandler.END


async def edit_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Edit registration info."""
    query = update.callback_query
    
    if query:
        await query.answer()
        await query.edit_message_text(
            "Registration editing not implemented yet. Please restart with /start"
        )
    
    context.user_data.clear()
    return ConversationHandler.END


# Create conversation handler
registration_conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_registration, pattern="^start_registration$"),
    ],
    states={
        PHONE_NUMBER: [
            MessageHandler(filters.CONTACT, receive_phone_number),
        ],
        BUILDING_INFO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_building_info),
        ],
        APARTMENT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_apartment),
        ],
        CONFIRMATION: [
            CallbackQueryHandler(confirm_registration, pattern="^confirm_registration$"),
            CallbackQueryHandler(cancel_registration, pattern="^cancel_registration$"),
            CallbackQueryHandler(edit_registration, pattern="^edit_registration$"),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_registration),
        CallbackQueryHandler(cancel_registration, pattern="^cancel_registration$"),
    ],
)