"""Structured logging configuration."""

import logging
import sys
from typing import Any, Dict

import structlog

from .config import get_settings

settings = get_settings()


def configure_logging() -> None:
    """Configure structured logging."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if settings.debug else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger."""
    return structlog.get_logger(name)


class LoggingMixin:
    """Mixin class for adding structured logging to classes."""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def log_error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    user_id: str = None,
    **kwargs: Any
) -> None:
    """Log API request."""
    logger = get_logger("api")
    logger.info(
        "API request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration * 1000, 2),
        user_id=user_id,
        **kwargs
    )


def log_bot_interaction(
    user_id: int,
    username: str,
    command: str,
    success: bool,
    **kwargs: Any
) -> None:
    """Log bot interaction."""
    logger = get_logger("bot")
    logger.info(
        "Bot interaction",
        user_id=user_id,
        username=username,
        command=command,
        success=success,
        **kwargs
    )


def log_food_action(
    action: str,
    user_id: int,
    food_id: str = None,
    **kwargs: Any
) -> None:
    """Log food-related action."""
    logger = get_logger("food")
    logger.info(
        "Food action",
        action=action,
        user_id=user_id,
        food_id=food_id,
        **kwargs
    )


def log_exchange_event(
    event: str,
    exchange_id: str,
    sharer_id: int,
    recipient_id: int,
    **kwargs: Any
) -> None:
    """Log exchange event."""
    logger = get_logger("exchange")
    logger.info(
        "Exchange event",
        event=event,
        exchange_id=exchange_id,
        sharer_id=sharer_id,
        recipient_id=recipient_id,
        **kwargs
    )