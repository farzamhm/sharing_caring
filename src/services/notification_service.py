"""Notification service for Telegram messaging."""

from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Bot
from telegram.error import TelegramError

from ..core.config import get_settings
from ..core.logging import get_logger
from ..models.user import User
from ..models.food import Food
from ..models.exchange import Exchange

settings = get_settings()
logger = get_logger(__name__)


class NotificationService:
    """Service for sending notifications via Telegram."""
    
    def __init__(self, db: AsyncSession, bot: Optional[Bot] = None) -> None:
        self.db = db
        self._bot = bot
    
    @property
    def bot(self) -> Optional[Bot]:
        """Get or create bot instance."""
        if not self._bot and settings.telegram_bot_token:
            try:
                self._bot = Bot(token=settings.telegram_bot_token)
            except Exception as e:
                logger.error("Failed to initialize bot", error=str(e))
        return self._bot
    
    async def send_message(
        self,
        telegram_id: int,
        text: str,
        parse_mode: str = "Markdown",
        reply_markup: Optional[Any] = None,
    ) -> bool:
        """Send a message to a user via Telegram."""
        if not self.bot:
            logger.error("Bot not initialized")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=telegram_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
            
            logger.info(
                "Notification sent",
                telegram_id=telegram_id,
                message_preview=text[:50],
            )
            return True
            
        except TelegramError as e:
            logger.error(
                "Failed to send notification",
                telegram_id=telegram_id,
                error=str(e),
            )
            return False
        except Exception as e:
            logger.error(
                "Unexpected error sending notification",
                telegram_id=telegram_id,
                error=str(e),
                exc_info=True,
            )
            return False
    
    async def send_food_posted_confirmation(
        self,
        user_id: str,
        food_id: str,
    ) -> bool:
        """Send confirmation when food is successfully posted."""
        try:
            # Get user and food details
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            food_result = await self.db.execute(
                select(Food).where(Food.id == food_id)
            )
            food = food_result.scalar_one_or_none()
            
            if not user or not food:
                return False
            
            message = f"""
✅ **Food Posted Successfully!**

🍲 **{food.title}**
📍 Pickup: {food.pickup_location}
⏰ Time: {food.pickup_start.strftime('%I:%M %p')} - {food.pickup_end.strftime('%I:%M %p')}
⭐ Credits: {food.credit_value}

Your food is now visible to neighbors in your building. You'll be notified when someone requests it.

Use /myposts to manage your active posts.
            """.strip()
            
            return await self.send_message(user.telegram_id, message)
            
        except Exception as e:
            logger.error(
                "Error sending food posted confirmation",
                user_id=user_id,
                food_id=food_id,
                error=str(e),
            )
            return False
    
    async def send_food_request_notification(
        self,
        sharer_id: str,
        recipient_id: str,
        food_id: str,
        exchange_id: str,
    ) -> bool:
        """Notify sharer when someone requests their food."""
        try:
            # Get all details
            sharer_result = await self.db.execute(
                select(User).where(User.id == sharer_id)
            )
            sharer = sharer_result.scalar_one_or_none()
            
            recipient_result = await self.db.execute(
                select(User).where(User.id == recipient_id)
            )
            recipient = recipient_result.scalar_one_or_none()
            
            food_result = await self.db.execute(
                select(Food).where(Food.id == food_id)
            )
            food = food_result.scalar_one_or_none()
            
            if not all([sharer, recipient, food]):
                return False
            
            message = f"""
🔔 **New Food Request!**

{recipient.display_name} (Apt {recipient.apartment_number}) wants to claim:
**{food.title}**

📍 Pickup: {food.pickup_location}
⏰ Time: {food.pickup_start.strftime('%I:%M %p')}

Please confirm this exchange within 30 minutes.

Reply with:
/confirm_{exchange_id[:8]} - Confirm exchange
/decline_{exchange_id[:8]} - Decline request
            """.strip()
            
            return await self.send_message(sharer.telegram_id, message)
            
        except Exception as e:
            logger.error(
                "Error sending food request notification",
                sharer_id=sharer_id,
                recipient_id=recipient_id,
                error=str(e),
            )
            return False
    
    async def send_request_confirmation(
        self,
        recipient_id: str,
        food_id: str,
        exchange_id: str,
    ) -> bool:
        """Send confirmation to recipient after requesting food."""
        try:
            recipient_result = await self.db.execute(
                select(User).where(User.id == recipient_id)
            )
            recipient = recipient_result.scalar_one_or_none()
            
            food_result = await self.db.execute(
                select(Food).where(Food.id == food_id)
            )
            food = food_result.scalar_one_or_none()
            
            if not recipient or not food:
                return False
            
            message = f"""
✅ **Food Request Sent!**

You've requested:
**{food.title}**

📍 Pickup: {food.pickup_location}
⏰ Time: {food.pickup_start.strftime('%I:%M %p')} - {food.pickup_end.strftime('%I:%M %p')}

The sharer will be notified. You'll receive a confirmation once they approve.

⚠️ This request will expire in 30 minutes if not confirmed.

To cancel: /cancel_{exchange_id[:8]}
            """.strip()
            
            return await self.send_message(recipient.telegram_id, message)
            
        except Exception as e:
            logger.error(
                "Error sending request confirmation",
                recipient_id=recipient_id,
                food_id=food_id,
                error=str(e),
            )
            return False
    
    async def send_exchange_confirmed(
        self,
        exchange_id: str,
        sharer_id: str,
        recipient_id: str,
    ) -> bool:
        """Notify both parties when exchange is confirmed."""
        try:
            # Get exchange details
            exchange_result = await self.db.execute(
                select(Exchange).where(Exchange.id == exchange_id)
            )
            exchange = exchange_result.scalar_one_or_none()
            
            if not exchange:
                return False
            
            # Get user details
            sharer_result = await self.db.execute(
                select(User).where(User.id == sharer_id)
            )
            sharer = sharer_result.scalar_one_or_none()
            
            recipient_result = await self.db.execute(
                select(User).where(User.id == recipient_id)
            )
            recipient = recipient_result.scalar_one_or_none()
            
            if not sharer or not recipient:
                return False
            
            # Message to sharer
            sharer_message = f"""
✅ **Exchange Confirmed!**

{recipient.display_name} will pick up the food.

📍 Pickup: {exchange.pickup_location}
⏰ Time: {exchange.scheduled_pickup_at.strftime('%I:%M %p')}
📱 Contact: @{recipient.telegram_username or 'Not available'}

Mark complete after handoff: /complete_{exchange_id[:8]}
            """.strip()
            
            # Message to recipient
            recipient_message = f"""
✅ **Exchange Confirmed!**

Your pickup is confirmed with {sharer.display_name}.

📍 Pickup: {exchange.pickup_location}
⏰ Time: {exchange.scheduled_pickup_at.strftime('%I:%M %p')}
📱 Contact: @{sharer.telegram_username or 'Not available'}

⭐ {exchange.credit_amount} credit(s) will be deducted after completion.

Mark complete after pickup: /complete_{exchange_id[:8]}
            """.strip()
            
            # Send both notifications
            sharer_sent = await self.send_message(sharer.telegram_id, sharer_message)
            recipient_sent = await self.send_message(recipient.telegram_id, recipient_message)
            
            return sharer_sent and recipient_sent
            
        except Exception as e:
            logger.error(
                "Error sending exchange confirmed notifications",
                exchange_id=exchange_id,
                error=str(e),
            )
            return False
    
    async def send_exchange_completed(
        self,
        exchange_id: str,
        sharer_id: str,
        recipient_id: str,
    ) -> bool:
        """Notify both parties when exchange is completed."""
        try:
            # Get users
            sharer_result = await self.db.execute(
                select(User).where(User.id == sharer_id)
            )
            sharer = sharer_result.scalar_one_or_none()
            
            recipient_result = await self.db.execute(
                select(User).where(User.id == recipient_id)
            )
            recipient = recipient_result.scalar_one_or_none()
            
            exchange_result = await self.db.execute(
                select(Exchange).where(Exchange.id == exchange_id)
            )
            exchange = exchange_result.scalar_one_or_none()
            
            if not all([sharer, recipient, exchange]):
                return False
            
            # Message to sharer
            sharer_message = f"""
🎉 **Exchange Complete!**

Thank you for sharing with {recipient.display_name}!
⭐ You earned {exchange.credit_amount} credit(s).

Please rate this exchange: /rate_{exchange_id[:8]}
            """.strip()
            
            # Message to recipient
            recipient_message = f"""
🎉 **Exchange Complete!**

Hope you enjoyed the food from {sharer.display_name}!
⭐ {exchange.credit_amount} credit(s) have been deducted.

Please rate this exchange: /rate_{exchange_id[:8]}
            """.strip()
            
            # Send both notifications
            sharer_sent = await self.send_message(sharer.telegram_id, sharer_message)
            recipient_sent = await self.send_message(recipient.telegram_id, recipient_message)
            
            return sharer_sent and recipient_sent
            
        except Exception as e:
            logger.error(
                "Error sending exchange completed notifications",
                exchange_id=exchange_id,
                error=str(e),
            )
            return False
    
    async def send_exchange_cancelled(
        self,
        exchange_id: str,
        cancelled_by: str,
        other_user_id: str,
        reason: str,
    ) -> bool:
        """Notify when exchange is cancelled."""
        try:
            # Get users
            cancelled_by_result = await self.db.execute(
                select(User).where(User.id == cancelled_by)
            )
            cancelled_by_user = cancelled_by_result.scalar_one_or_none()
            
            other_user_result = await self.db.execute(
                select(User).where(User.id == other_user_id)
            )
            other_user = other_user_result.scalar_one_or_none()
            
            if not cancelled_by_user or not other_user:
                return False
            
            message = f"""
❌ **Exchange Cancelled**

{cancelled_by_user.display_name} has cancelled the exchange.

Reason: {reason}

The food is now available for others to claim.
            """.strip()
            
            return await self.send_message(other_user.telegram_id, message)
            
        except Exception as e:
            logger.error(
                "Error sending exchange cancelled notification",
                exchange_id=exchange_id,
                cancelled_by=cancelled_by,
                error=str(e),
            )
            return False
    
    async def send_food_expiring_soon(
        self,
        user_id: str,
        food_id: str,
        minutes_until_expiry: int,
    ) -> bool:
        """Notify sharer when their food is about to expire."""
        try:
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            food_result = await self.db.execute(
                select(Food).where(Food.id == food_id)
            )
            food = food_result.scalar_one_or_none()
            
            if not user or not food:
                return False
            
            message = f"""
⏰ **Food Expiring Soon!**

Your post "{food.title}" will expire in {minutes_until_expiry} minutes.

No one has claimed it yet. Consider:
• Extending the pickup time
• Sharing in a community group
• Consuming it yourself

To extend: /extend_{food_id[:8]}
To cancel: /expire_{food_id[:8]}
            """.strip()
            
            return await self.send_message(user.telegram_id, message)
            
        except Exception as e:
            logger.error(
                "Error sending food expiring notification",
                user_id=user_id,
                food_id=food_id,
                error=str(e),
            )
            return False
    
    async def send_daily_summary(
        self,
        user_id: str,
        stats: Dict[str, Any],
    ) -> bool:
        """Send daily activity summary to user."""
        try:
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return False
            
            message = f"""
📊 **Your Daily Summary**

**Today's Activity:**
🍲 Food shared: {stats.get('food_shared', 0)}
🔍 Food claimed: {stats.get('food_claimed', 0)}
⭐ Credits earned: {stats.get('credits_earned', 0)}
💰 Credit balance: {stats.get('credit_balance', 0)}

**Community Impact:**
🌱 Food saved from waste: {stats.get('food_saved', 0)} items
👥 Neighbors helped: {stats.get('neighbors_helped', 0)}

Keep up the great work building our community!

Browse available food: /browse
Share something new: /share
            """.strip()
            
            return await self.send_message(user.telegram_id, message)
            
        except Exception as e:
            logger.error(
                "Error sending daily summary",
                user_id=user_id,
                error=str(e),
            )
            return False

    async def send_admin_notification(
        self,
        user_id: str,
        message: str,
    ) -> bool:
        """Send admin notification to user."""
        try:
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return False
            
            admin_message = f"""
🛡️ **Admin Message**

{message}

If you have questions, please contact support.
            """.strip()
            
            return await self.send_message(user.telegram_id, admin_message)
            
        except Exception as e:
            logger.error(
                "Error sending admin notification",
                user_id=user_id,
                error=str(e),
            )
            return False