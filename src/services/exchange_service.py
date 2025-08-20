"""Exchange coordination service."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.config import get_settings
from ..core.logging import get_logger, log_exchange_event
from ..models.exchange import Exchange, ExchangeStatus
from ..models.food import Food, FoodStatus
from ..models.user import User
from ..models.credit import Credit, CreditTransaction, TransactionType
from .notification_service import NotificationService

settings = get_settings()
logger = get_logger(__name__)


class ExchangeService:
    """Service for exchange coordination operations."""
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.notification_service = NotificationService(db)
    
    async def get_exchange_by_id(self, exchange_id: str) -> Optional[Exchange]:
        """Get exchange by ID."""
        try:
            result = await self.db.execute(
                select(Exchange)
                .options(
                    selectinload(Exchange.sharer),
                    selectinload(Exchange.recipient),
                    selectinload(Exchange.food),
                )
                .where(Exchange.id == exchange_id)
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error("Error getting exchange by ID", exchange_id=exchange_id, error=str(e))
            return None
    
    async def confirm_exchange(
        self,
        exchange_id: str,
        user_id: str,
        notes: Optional[str] = None,
    ) -> bool:
        """Confirm participation in an exchange."""
        try:
            exchange = await self.get_exchange_by_id(exchange_id)
            if not exchange:
                return False
            
            # Check if user is part of the exchange
            if user_id not in [exchange.sharer_id, exchange.recipient_id]:
                logger.error(
                    "User not part of exchange",
                    exchange_id=exchange_id,
                    user_id=user_id,
                )
                return False
            
            # Confirm based on user role
            confirmed = exchange.confirm_by_user(user_id)
            if not confirmed:
                logger.info(
                    "User already confirmed",
                    exchange_id=exchange_id,
                    user_id=user_id,
                )
                return True  # Already confirmed
            
            # If both confirmed, update status
            if exchange.is_confirmed:
                exchange.status = ExchangeStatus.CONFIRMED
                
                # Send notifications
                await self.notification_service.send_exchange_confirmed(
                    exchange_id=exchange_id,
                    sharer_id=exchange.sharer_id,
                    recipient_id=exchange.recipient_id,
                )
            
            await self.db.flush()
            
            log_exchange_event(
                event="exchange_confirmed",
                exchange_id=exchange_id,
                sharer_id=exchange.sharer_id,
                recipient_id=exchange.recipient_id,
                confirmed_by=user_id,
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Error confirming exchange",
                exchange_id=exchange_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            await self.db.rollback()
            return False
    
    async def complete_exchange(
        self,
        exchange_id: str,
        user_id: str,
        rating: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> bool:
        """Complete an exchange and transfer credits."""
        try:
            exchange = await self.get_exchange_by_id(exchange_id)
            if not exchange:
                return False
            
            # Verify user is part of the exchange
            if user_id not in [exchange.sharer_id, exchange.recipient_id]:
                logger.error(
                    "User not part of exchange",
                    exchange_id=exchange_id,
                    user_id=user_id,
                )
                return False
            
            # Check if already completed
            if exchange.status == ExchangeStatus.COMPLETED:
                logger.info(
                    "Exchange already completed",
                    exchange_id=exchange_id,
                )
                return True
            
            # Mark as completed
            success = exchange.complete()
            if not success:
                logger.error(
                    "Exchange not confirmed, cannot complete",
                    exchange_id=exchange_id,
                    status=exchange.status,
                )
                return False
            
            # Add rating if provided
            if rating:
                if user_id == exchange.recipient_id:
                    exchange.recipient_rating = rating
                    if notes:
                        exchange.recipient_notes = notes
                elif user_id == exchange.sharer_id:
                    exchange.sharer_rating = rating
                    if notes:
                        exchange.sharer_notes = notes
            
            # Transfer credits
            await self._transfer_credits(exchange)
            
            # Update food status
            result = await self.db.execute(
                select(Food).where(Food.id == exchange.food_id)
            )
            food = result.scalar_one_or_none()
            if food:
                food.status = FoodStatus.COMPLETED
            
            await self.db.flush()
            
            # Send notifications
            await self.notification_service.send_exchange_completed(
                exchange_id=exchange_id,
                sharer_id=exchange.sharer_id,
                recipient_id=exchange.recipient_id,
            )
            
            log_exchange_event(
                event="exchange_completed",
                exchange_id=exchange_id,
                sharer_id=exchange.sharer_id,
                recipient_id=exchange.recipient_id,
                completed_by=user_id,
                rating=rating,
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Error completing exchange",
                exchange_id=exchange_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            await self.db.rollback()
            return False
    
    async def cancel_exchange(
        self,
        exchange_id: str,
        user_id: str,
        reason: str,
    ) -> bool:
        """Cancel an exchange."""
        try:
            exchange = await self.get_exchange_by_id(exchange_id)
            if not exchange:
                return False
            
            # Cancel the exchange
            success = exchange.cancel_by_user(user_id, reason)
            if not success:
                logger.error(
                    "Cannot cancel exchange",
                    exchange_id=exchange_id,
                    user_id=user_id,
                    status=exchange.status,
                )
                return False
            
            # Reset food status if needed
            if exchange.status == ExchangeStatus.CANCELLED:
                result = await self.db.execute(
                    select(Food).where(Food.id == exchange.food_id)
                )
                food = result.scalar_one_or_none()
                if food and food.status == FoodStatus.CLAIMED:
                    food.status = FoodStatus.AVAILABLE
                    food.claimed_by_id = None
                    food.claimed_at = None
            
            await self.db.flush()
            
            # Send notifications
            other_user_id = (
                exchange.recipient_id
                if user_id == exchange.sharer_id
                else exchange.sharer_id
            )
            await self.notification_service.send_exchange_cancelled(
                exchange_id=exchange_id,
                cancelled_by=user_id,
                other_user_id=other_user_id,
                reason=reason,
            )
            
            log_exchange_event(
                event="exchange_cancelled",
                exchange_id=exchange_id,
                sharer_id=exchange.sharer_id,
                recipient_id=exchange.recipient_id,
                cancelled_by=user_id,
                reason=reason,
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Error cancelling exchange",
                exchange_id=exchange_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            await self.db.rollback()
            return False
    
    async def mark_no_show(
        self,
        exchange_id: str,
        user_id: str,
        no_show_user_id: str,
        notes: Optional[str] = None,
    ) -> bool:
        """Mark an exchange as no-show."""
        try:
            exchange = await self.get_exchange_by_id(exchange_id)
            if not exchange:
                return False
            
            # Verify reporting user is part of the exchange
            if user_id not in [exchange.sharer_id, exchange.recipient_id]:
                logger.error(
                    "User not part of exchange",
                    exchange_id=exchange_id,
                    user_id=user_id,
                )
                return False
            
            # Update status
            exchange.status = ExchangeStatus.NO_SHOW
            exchange.completed_at = datetime.utcnow()
            
            # Add notes
            if notes:
                if user_id == exchange.sharer_id:
                    exchange.sharer_notes = notes
                else:
                    exchange.recipient_notes = notes
            
            # Return credits to appropriate party
            if no_show_user_id == exchange.recipient_id:
                # Recipient didn't show, no credits transferred
                pass
            else:
                # Sharer didn't show, refund recipient's credits
                await self._refund_credits(exchange)
            
            await self.db.flush()
            
            log_exchange_event(
                event="exchange_no_show",
                exchange_id=exchange_id,
                sharer_id=exchange.sharer_id,
                recipient_id=exchange.recipient_id,
                reported_by=user_id,
                no_show_user=no_show_user_id,
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Error marking no-show",
                exchange_id=exchange_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            await self.db.rollback()
            return False
    
    async def get_user_exchanges(
        self,
        user_id: str,
        role: Optional[str] = None,  # 'sharer', 'recipient', or None for both
        status: Optional[ExchangeStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Exchange]:
        """Get user's exchanges."""
        try:
            query = select(Exchange).options(
                selectinload(Exchange.sharer),
                selectinload(Exchange.recipient),
                selectinload(Exchange.food),
            )
            
            # Filter by role
            if role == "sharer":
                query = query.where(Exchange.sharer_id == user_id)
            elif role == "recipient":
                query = query.where(Exchange.recipient_id == user_id)
            else:
                query = query.where(
                    or_(
                        Exchange.sharer_id == user_id,
                        Exchange.recipient_id == user_id,
                    )
                )
            
            # Filter by status
            if status:
                query = query.where(Exchange.status == status)
            
            # Order by most recent first
            query = query.order_by(Exchange.created_at.desc())
            
            # Apply pagination
            query = query.limit(limit).offset(offset)
            
            result = await self.db.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(
                "Error getting user exchanges",
                user_id=user_id,
                role=role,
                status=status,
                error=str(e),
                exc_info=True,
            )
            return []
    
    async def get_active_exchanges(
        self,
        user_id: str,
    ) -> List[Exchange]:
        """Get user's active exchanges (pending/confirmed)."""
        try:
            result = await self.db.execute(
                select(Exchange)
                .options(
                    selectinload(Exchange.sharer),
                    selectinload(Exchange.recipient),
                    selectinload(Exchange.food),
                )
                .where(
                    or_(
                        Exchange.sharer_id == user_id,
                        Exchange.recipient_id == user_id,
                    )
                )
                .where(
                    Exchange.status.in_([
                        ExchangeStatus.PENDING,
                        ExchangeStatus.CONFIRMED,
                        ExchangeStatus.IN_PROGRESS,
                    ])
                )
                .order_by(Exchange.scheduled_pickup_at)
            )
            
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(
                "Error getting active exchanges",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            return []
    
    async def _transfer_credits(self, exchange: Exchange) -> bool:
        """Transfer credits from recipient to sharer."""
        try:
            if exchange.credits_transferred:
                logger.info(
                    "Credits already transferred",
                    exchange_id=exchange.id,
                )
                return True
            
            # Get credit accounts
            recipient_credit_result = await self.db.execute(
                select(Credit).where(Credit.user_id == exchange.recipient_id)
            )
            recipient_credit = recipient_credit_result.scalar_one_or_none()
            
            sharer_credit_result = await self.db.execute(
                select(Credit).where(Credit.user_id == exchange.sharer_id)
            )
            sharer_credit = sharer_credit_result.scalar_one_or_none()
            
            if not recipient_credit or not sharer_credit:
                logger.error(
                    "Credit accounts not found",
                    recipient_id=exchange.recipient_id,
                    sharer_id=exchange.sharer_id,
                )
                return False
            
            # Transfer credits
            amount = exchange.credit_amount
            
            # Deduct from recipient
            if not recipient_credit.spend_credits(amount):
                logger.error(
                    "Insufficient credits",
                    user_id=exchange.recipient_id,
                    required=amount,
                    available=recipient_credit.balance,
                )
                return False
            
            # Add to sharer
            sharer_credit.add_credits(amount)
            
            # Create transaction records
            recipient_transaction = CreditTransaction.create_transaction(
                user_id=exchange.recipient_id,
                transaction_type=TransactionType.SPENT_CLAIMING,
                amount=-amount,
                balance_before=recipient_credit.balance + amount,
                balance_after=recipient_credit.balance,
                description=f"Claimed food from exchange",
                exchange_id=exchange.id,
                food_id=exchange.food_id,
            )
            
            sharer_transaction = CreditTransaction.create_transaction(
                user_id=exchange.sharer_id,
                transaction_type=TransactionType.EARNED_SHARING,
                amount=amount,
                balance_before=sharer_credit.balance - amount,
                balance_after=sharer_credit.balance,
                description=f"Earned from sharing food",
                exchange_id=exchange.id,
                food_id=exchange.food_id,
            )
            
            self.db.add(recipient_transaction)
            self.db.add(sharer_transaction)
            
            # Mark as transferred
            exchange.credits_transferred = True
            exchange.credits_transferred_at = datetime.utcnow()
            
            logger.info(
                "Credits transferred",
                exchange_id=exchange.id,
                amount=amount,
                from_user=exchange.recipient_id,
                to_user=exchange.sharer_id,
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Error transferring credits",
                exchange_id=exchange.id,
                error=str(e),
                exc_info=True,
            )
            return False
    
    async def _refund_credits(self, exchange: Exchange) -> bool:
        """Refund credits to recipient if exchange is cancelled."""
        try:
            # Only refund if credits were reserved but not transferred
            if exchange.credits_transferred:
                logger.info(
                    "Credits already transferred, no refund",
                    exchange_id=exchange.id,
                )
                return False
            
            # For now, credits are only deducted on completion,
            # so no refund needed for cancellations
            
            logger.info(
                "No credits to refund (not yet transferred)",
                exchange_id=exchange.id,
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Error refunding credits",
                exchange_id=exchange.id,
                error=str(e),
                exc_info=True,
            )
            return False
    
    async def expire_old_exchanges(self) -> int:
        """Expire pending exchanges that weren't confirmed (background task)."""
        try:
            # Expire unconfirmed exchanges after 30 minutes
            expiry_time = datetime.utcnow() - timedelta(minutes=30)
            
            result = await self.db.execute(
                select(Exchange)
                .where(Exchange.status == ExchangeStatus.PENDING)
                .where(Exchange.created_at <= expiry_time)
            )
            expired_exchanges = result.scalars().all()
            
            count = 0
            for exchange in expired_exchanges:
                exchange.status = ExchangeStatus.CANCELLED
                exchange.cancelled_at = datetime.utcnow()
                exchange.cancellation_reason = "Expired - not confirmed in time"
                
                # Reset food status
                food_result = await self.db.execute(
                    select(Food).where(Food.id == exchange.food_id)
                )
                food = food_result.scalar_one_or_none()
                if food and food.status == FoodStatus.CLAIMED:
                    food.status = FoodStatus.AVAILABLE
                    food.claimed_by_id = None
                    food.claimed_at = None
                
                count += 1
            
            if count > 0:
                await self.db.flush()
                logger.info(f"Expired {count} unconfirmed exchanges")
            
            return count
            
        except Exception as e:
            logger.error("Error expiring old exchanges", error=str(e), exc_info=True)
            await self.db.rollback()
            return 0