"""Food management service."""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.config import get_settings
from ..core.logging import get_logger, log_food_action
from ..models.food import Food, FoodStatus, FoodCategory, ServingSize
from ..models.user import User
from ..models.building import Building
from ..models.exchange import Exchange, ExchangeStatus
from ..models.credit import Credit, CreditTransaction, TransactionType

settings = get_settings()
logger = get_logger(__name__)


class FoodService:
    """Service for food management operations."""
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
    
    async def create_food_post(
        self,
        user_id: str,
        title: str,
        description: str,
        category: FoodCategory,
        serving_size: ServingSize,
        ingredients: Optional[str] = None,
        allergens: Optional[str] = None,
        dietary_info: Optional[str] = None,
        pickup_start: Optional[datetime] = None,
        pickup_end: Optional[datetime] = None,
        pickup_location: Optional[str] = None,
        pickup_instructions: Optional[str] = None,
        photo_urls: Optional[List[str]] = None,
        credit_value: int = 1,
    ) -> Optional[Food]:
        """Create a new food post."""
        try:
            # Get user and validate
            from sqlalchemy import select
            result = await self.db.execute(
                select(User).options(selectinload(User.building)).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error("User not found", user_id=user_id)
                return None
            
            if not user.can_share:
                logger.error("User cannot share food", user_id=user_id)
                return None
            
            if not user.building_id:
                logger.error("User has no building assigned", user_id=user_id)
                return None
            
            # Set default times if not provided
            now = datetime.utcnow()
            if not pickup_start:
                pickup_start = now + timedelta(minutes=30)
            if not pickup_end:
                pickup_end = pickup_start + timedelta(hours=2)
            
            # Calculate expiration (default 4 hours from now)
            expires_at = now + timedelta(hours=settings.food_post_expiry_hours)
            
            # Create food post
            food = Food(
                title=title,
                description=description,
                category=category,
                serving_size=serving_size,
                ingredients=ingredients,
                allergens=allergens,
                dietary_info=dietary_info,
                prepared_at=now,
                pickup_start=pickup_start,
                pickup_end=pickup_end,
                expires_at=expires_at,
                pickup_location=pickup_location or user.apartment_number,
                pickup_instructions=pickup_instructions,
                photo_urls=json.dumps(photo_urls) if photo_urls else None,
                status=FoodStatus.AVAILABLE,
                credit_value=credit_value,
                sharer_id=user_id,
                building_id=user.building_id,
            )
            
            self.db.add(food)
            await self.db.flush()
            
            log_food_action(
                action="food_posted",
                user_id=user.id,
                food_id=food.id,
                category=category,
                serving_size=serving_size,
            )
            
            logger.info(
                "Food post created",
                food_id=food.id,
                user_id=user_id,
                title=title,
                category=category,
            )
            
            return food
            
        except Exception as e:
            logger.error(
                "Error creating food post",
                user_id=user_id,
                title=title,
                error=str(e),
                exc_info=True,
            )
            await self.db.rollback()
            return None
    
    async def get_food_by_id(self, food_id: str) -> Optional[Food]:
        """Get food post by ID."""
        try:
            result = await self.db.execute(
                select(Food)
                .options(
                    selectinload(Food.sharer),
                    selectinload(Food.claimed_by),
                    selectinload(Food.building),
                )
                .where(Food.id == food_id)
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error("Error getting food by ID", food_id=food_id, error=str(e))
            return None
    
    async def browse_available_food(
        self,
        user_id: str,
        building_id: Optional[str] = None,
        category: Optional[FoodCategory] = None,
        dietary_info: Optional[str] = None,
        exclude_allergens: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Food]:
        """Browse available food with filters."""
        try:
            # Get user's building if not specified
            if not building_id:
                result = await self.db.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                if user:
                    building_id = user.building_id
            
            # Build query
            query = (
                select(Food)
                .options(
                    selectinload(Food.sharer),
                    selectinload(Food.building),
                )
                .where(Food.status == FoodStatus.AVAILABLE)
                .where(Food.expires_at > datetime.utcnow())
                .where(Food.sharer_id != user_id)  # Don't show own posts
            )
            
            # Apply filters
            if building_id:
                query = query.where(Food.building_id == building_id)
            
            if category:
                query = query.where(Food.category == category)
            
            if dietary_info:
                query = query.where(
                    or_(
                        Food.dietary_info.ilike(f"%{dietary_info}%"),
                        Food.dietary_info == dietary_info,
                    )
                )
            
            if exclude_allergens:
                for allergen in exclude_allergens:
                    query = query.where(
                        or_(
                            Food.allergens.is_(None),
                            ~Food.allergens.ilike(f"%{allergen}%"),
                        )
                    )
            
            # Order by pickup time (soonest first)
            query = query.order_by(Food.pickup_start)
            
            # Apply pagination
            query = query.limit(limit).offset(offset)
            
            result = await self.db.execute(query)
            foods = list(result.scalars().all())
            
            log_food_action(
                action="browse_food",
                user_id=user_id,
                building_id=building_id,
                filters={
                    "category": category,
                    "dietary_info": dietary_info,
                    "exclude_allergens": exclude_allergens,
                },
                results_count=len(foods),
            )
            
            return foods
            
        except Exception as e:
            logger.error(
                "Error browsing food",
                user_id=user_id,
                building_id=building_id,
                error=str(e),
                exc_info=True,
            )
            return []
    
    async def claim_food(
        self,
        food_id: str,
        user_id: str,
        notes: Optional[str] = None,
    ) -> Optional[Exchange]:
        """Claim a food post."""
        try:
            # Get food post
            food = await self.get_food_by_id(food_id)
            if not food:
                logger.error("Food not found", food_id=food_id)
                return None
            
            # Validate claim
            if not food.can_be_claimed_by(user_id):
                logger.error(
                    "Food cannot be claimed",
                    food_id=food_id,
                    user_id=user_id,
                    status=food.status,
                )
                return None
            
            # Check user has enough credits
            result = await self.db.execute(
                select(Credit).where(Credit.user_id == user_id)
            )
            user_credit = result.scalar_one_or_none()
            
            if not user_credit or not user_credit.can_spend(food.credit_value):
                logger.error(
                    "Insufficient credits",
                    user_id=user_id,
                    required=food.credit_value,
                    available=user_credit.balance if user_credit else 0,
                )
                return None
            
            # Create exchange
            exchange = Exchange(
                sharer_id=food.sharer_id,
                recipient_id=user_id,
                food_id=food_id,
                status=ExchangeStatus.PENDING,
                pickup_location=food.pickup_location,
                pickup_instructions=food.pickup_instructions,
                scheduled_pickup_at=food.pickup_start,
                credit_amount=food.credit_value,
                recipient_notes=notes,
            )
            
            self.db.add(exchange)
            
            # Update food status
            food.status = FoodStatus.CLAIMED
            food.claimed_by_id = user_id
            food.claimed_at = datetime.utcnow()
            
            # Reserve credits (not transferred yet)
            # Credits are transferred when exchange is completed
            
            await self.db.flush()
            
            log_food_action(
                action="food_claimed",
                user_id=user_id,
                food_id=food_id,
                exchange_id=exchange.id,
            )
            
            logger.info(
                "Food claimed",
                food_id=food_id,
                user_id=user_id,
                exchange_id=exchange.id,
            )
            
            return exchange
            
        except Exception as e:
            logger.error(
                "Error claiming food",
                food_id=food_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            await self.db.rollback()
            return None
    
    async def unclaim_food(
        self,
        food_id: str,
        user_id: str,
        reason: Optional[str] = None,
    ) -> bool:
        """Unclaim a previously claimed food post."""
        try:
            # Get food post
            food = await self.get_food_by_id(food_id)
            if not food:
                return False
            
            # Verify user is the one who claimed it
            if food.claimed_by_id != user_id:
                logger.error(
                    "User did not claim this food",
                    food_id=food_id,
                    user_id=user_id,
                    claimed_by=food.claimed_by_id,
                )
                return False
            
            # Get the exchange
            result = await self.db.execute(
                select(Exchange)
                .where(Exchange.food_id == food_id)
                .where(Exchange.recipient_id == user_id)
                .where(Exchange.status.in_([ExchangeStatus.PENDING, ExchangeStatus.CONFIRMED]))
            )
            exchange = result.scalar_one_or_none()
            
            if exchange:
                # Cancel the exchange
                exchange.status = ExchangeStatus.CANCELLED
                exchange.cancelled_at = datetime.utcnow()
                exchange.cancelled_by_id = user_id
                exchange.cancellation_reason = reason or "Recipient cancelled"
            
            # Reset food status
            food.status = FoodStatus.AVAILABLE
            food.claimed_by_id = None
            food.claimed_at = None
            
            await self.db.flush()
            
            log_food_action(
                action="food_unclaimed",
                user_id=user_id,
                food_id=food_id,
                reason=reason,
            )
            
            logger.info(
                "Food unclaimed",
                food_id=food_id,
                user_id=user_id,
                reason=reason,
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Error unclaiming food",
                food_id=food_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            await self.db.rollback()
            return False
    
    async def get_user_posts(
        self,
        user_id: str,
        include_expired: bool = False,
        limit: int = 20,
    ) -> List[Food]:
        """Get user's food posts."""
        try:
            query = (
                select(Food)
                .options(
                    selectinload(Food.claimed_by),
                    selectinload(Food.exchanges),
                )
                .where(Food.sharer_id == user_id)
            )
            
            if not include_expired:
                query = query.where(Food.expires_at > datetime.utcnow())
            
            query = query.order_by(Food.created_at.desc()).limit(limit)
            
            result = await self.db.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(
                "Error getting user posts",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            return []
    
    async def update_food_post(
        self,
        food_id: str,
        user_id: str,
        **kwargs,
    ) -> Optional[Food]:
        """Update a food post."""
        try:
            food = await self.get_food_by_id(food_id)
            if not food:
                return None
            
            # Verify ownership
            if food.sharer_id != user_id:
                logger.error(
                    "User does not own this food post",
                    food_id=food_id,
                    user_id=user_id,
                    owner_id=food.sharer_id,
                )
                return None
            
            # Don't allow updates if already claimed
            if food.status != FoodStatus.AVAILABLE:
                logger.error(
                    "Cannot update claimed/completed food",
                    food_id=food_id,
                    status=food.status,
                )
                return None
            
            # Update allowed fields
            allowed_fields = {
                "description",
                "ingredients",
                "allergens",
                "dietary_info",
                "pickup_start",
                "pickup_end",
                "pickup_location",
                "pickup_instructions",
                "serving_size",
            }
            
            for key, value in kwargs.items():
                if key in allowed_fields and hasattr(food, key):
                    setattr(food, key, value)
            
            food.updated_at = datetime.utcnow()
            
            await self.db.flush()
            
            log_food_action(
                action="food_updated",
                user_id=user_id,
                food_id=food_id,
                updated_fields=list(kwargs.keys()),
            )
            
            logger.info(
                "Food post updated",
                food_id=food_id,
                user_id=user_id,
                updated_fields=list(kwargs.keys()),
            )
            
            return food
            
        except Exception as e:
            logger.error(
                "Error updating food post",
                food_id=food_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            await self.db.rollback()
            return None
    
    async def expire_food_post(
        self,
        food_id: str,
        user_id: str,
        reason: Optional[str] = None,
    ) -> bool:
        """Manually expire a food post."""
        try:
            food = await self.get_food_by_id(food_id)
            if not food:
                return False
            
            # Verify ownership
            if food.sharer_id != user_id:
                logger.error(
                    "User does not own this food post",
                    food_id=food_id,
                    user_id=user_id,
                    owner_id=food.sharer_id,
                )
                return False
            
            # Update status
            food.status = FoodStatus.EXPIRED
            food.expires_at = datetime.utcnow()
            
            # Cancel any pending exchanges
            result = await self.db.execute(
                select(Exchange)
                .where(Exchange.food_id == food_id)
                .where(Exchange.status.in_([ExchangeStatus.PENDING, ExchangeStatus.CONFIRMED]))
            )
            exchanges = result.scalars().all()
            
            for exchange in exchanges:
                exchange.status = ExchangeStatus.CANCELLED
                exchange.cancelled_at = datetime.utcnow()
                exchange.cancelled_by_id = user_id
                exchange.cancellation_reason = reason or "Food expired by sharer"
            
            await self.db.flush()
            
            log_food_action(
                action="food_expired",
                user_id=user_id,
                food_id=food_id,
                reason=reason,
            )
            
            logger.info(
                "Food post expired",
                food_id=food_id,
                user_id=user_id,
                reason=reason,
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Error expiring food post",
                food_id=food_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            await self.db.rollback()
            return False
    
    async def expire_old_posts(self) -> int:
        """Expire all old food posts (background task)."""
        try:
            now = datetime.utcnow()
            
            # Find expired posts
            result = await self.db.execute(
                select(Food)
                .where(Food.status == FoodStatus.AVAILABLE)
                .where(Food.expires_at <= now)
            )
            expired_foods = result.scalars().all()
            
            count = 0
            for food in expired_foods:
                food.status = FoodStatus.EXPIRED
                count += 1
            
            if count > 0:
                await self.db.flush()
                logger.info(f"Expired {count} old food posts")
            
            return count
            
        except Exception as e:
            logger.error("Error expiring old posts", error=str(e), exc_info=True)
            await self.db.rollback()
            return 0
    
    async def get_food_stats(self, building_id: Optional[str] = None) -> Dict[str, Any]:
        """Get food sharing statistics."""
        try:
            # Base query
            query = select(Food)
            if building_id:
                query = query.where(Food.building_id == building_id)
            
            # Total posts
            total_result = await self.db.execute(
                select(func.count(Food.id)).select_from(query.subquery())
            )
            total_posts = total_result.scalar() or 0
            
            # Available posts
            available_result = await self.db.execute(
                select(func.count(Food.id))
                .where(Food.status == FoodStatus.AVAILABLE)
                .where(Food.expires_at > datetime.utcnow())
            )
            available_posts = available_result.scalar() or 0
            
            # Completed exchanges
            completed_result = await self.db.execute(
                select(func.count(Food.id))
                .where(Food.status == FoodStatus.COMPLETED)
            )
            completed_posts = completed_result.scalar() or 0
            
            # Category breakdown
            category_result = await self.db.execute(
                select(Food.category, func.count(Food.id))
                .group_by(Food.category)
            )
            category_breakdown = {
                category: count for category, count in category_result.all()
            }
            
            return {
                "total_posts": total_posts,
                "available_posts": available_posts,
                "completed_posts": completed_posts,
                "success_rate": (completed_posts / total_posts * 100) if total_posts > 0 else 0,
                "category_breakdown": category_breakdown,
            }
            
        except Exception as e:
            logger.error(
                "Error getting food stats",
                building_id=building_id,
                error=str(e),
                exc_info=True,
            )
            return {}