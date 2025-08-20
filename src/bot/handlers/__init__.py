"""Bot handlers module."""

from typing import Dict, Any
from telegram.ext import filters

# Import handlers
from .basic import echo_handler, unknown_handler
from .menu import menu_handler, main_menu_callback
from .food import (
    share_food_handler,
    browse_food_handler, 
    my_posts_handler,
    claim_food_callback,
)
from .profile import profile_handler, settings_callback

# Command handlers mapping
command_handlers: Dict[str, Any] = {
    "menu": menu_handler,
    "share": share_food_handler,
    "browse": browse_food_handler,
    "myposts": my_posts_handler,
    "profile": profile_handler,
}

# Callback query handlers mapping
callback_query_handlers: Dict[str, Any] = {
    "^main_menu": main_menu_callback,
    "^claim_food": claim_food_callback,
    "^settings": settings_callback,
}

# Message handlers mapping
message_handlers: Dict[Any, Any] = {
    filters.TEXT & ~filters.COMMAND: echo_handler,
    filters.COMMAND: unknown_handler,
}

__all__ = [
    "command_handlers",
    "callback_query_handlers", 
    "message_handlers",
]