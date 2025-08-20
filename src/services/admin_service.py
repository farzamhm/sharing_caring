"""Admin service for platform monitoring and management."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.logging import get_logger
from ..models.user import User
from ..models.building import Building
from ..models.food import Food, FoodStatus
from ..models.exchange import Exchange, ExchangeStatus
from ..models.credit import Credit, CreditTransaction, TransactionType

logger = get_logger(__name__)


class AdminService:
    """Service for admin dashboard functionality."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_platform_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get platform-wide statistics."""
        logger.info("Getting platform stats", days=days)
        
        try:
            # Date range for stats
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Total users
            total_users_result = await self.db.execute(select(func.count(User.id)))
            total_users = total_users_result.scalar()
            
            # Active users (posted or claimed food in period)
            active_users_query = select(func.count(func.distinct(User.id))).select_from(
                User
            ).join(Food, or_(
                Food.sharer_id == User.id,
                Food.claimed_by_id == User.id
            )).where(Food.created_at >= start_date)
            
            active_users_result = await self.db.execute(active_users_query)
            active_users = active_users_result.scalar() or 0
            
            # Total buildings
            total_buildings_result = await self.db.execute(select(func.count(Building.id)))
            total_buildings = total_buildings_result.scalar()
            
            # Food posts stats
            total_food_posts_result = await self.db.execute(select(func.count(Food.id)))
            total_food_posts = total_food_posts_result.scalar()
            
            recent_food_posts_result = await self.db.execute(
                select(func.count(Food.id)).where(Food.created_at >= start_date)
            )
            recent_food_posts = recent_food_posts_result.scalar()
            
            # Active food posts
            active_food_posts_result = await self.db.execute(
                select(func.count(Food.id)).where(Food.status == FoodStatus.AVAILABLE)
            )
            active_food_posts = active_food_posts_result.scalar()
            
            # Exchange stats
            total_exchanges_result = await self.db.execute(select(func.count(Exchange.id)))
            total_exchanges = total_exchanges_result.scalar()
            
            completed_exchanges_result = await self.db.execute(
                select(func.count(Exchange.id)).where(
                    and_(
                        Exchange.status == ExchangeStatus.COMPLETED,
                        Exchange.completed_at >= start_date
                    )
                )
            )
            completed_exchanges = completed_exchanges_result.scalar()
            
            # Credit stats
            total_credits_result = await self.db.execute(
                select(func.sum(Credit.balance))
            )
            total_credits_in_circulation = total_credits_result.scalar() or 0
            
            total_transactions_result = await self.db.execute(
                select(func.count(CreditTransaction.id)).where(
                    CreditTransaction.created_at >= start_date
                )
            )
            recent_transactions = total_transactions_result.scalar()
            
            return {
                "period_days": days,
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "activation_rate": round((active_users / total_users * 100) if total_users > 0 else 0, 1)
                },
                "buildings": {
                    "total": total_buildings
                },
                "food_posts": {
                    "total": total_food_posts,
                    "recent": recent_food_posts,
                    "active": active_food_posts
                },
                "exchanges": {
                    "total": total_exchanges,
                    "completed_recent": completed_exchanges,
                    "success_rate": round((completed_exchanges / recent_food_posts * 100) if recent_food_posts > 0 else 0, 1)
                },
                "credits": {
                    "total_in_circulation": total_credits_in_circulation,
                    "recent_transactions": recent_transactions
                },
                "updated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error("Error getting platform stats", error=str(e), exc_info=True)
            raise

    async def get_building_stats(self, building_id: str, days: int = 30) -> Dict[str, Any]:
        """Get statistics for a specific building."""
        logger.info("Getting building stats", building_id=building_id, days=days)
        
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Building info
            building_result = await self.db.execute(
                select(Building).where(Building.id == building_id)
            )
            building = building_result.scalar_one_or_none()
            
            if not building:
                return None
            
            # Users in building
            total_users_result = await self.db.execute(
                select(func.count(User.id)).where(User.building_id == building_id)
            )
            total_users = total_users_result.scalar()
            
            # Active users
            active_users_result = await self.db.execute(
                select(func.count(func.distinct(User.id))).select_from(User)
                .join(Food, Food.sharer_id == User.id)
                .where(
                    and_(
                        User.building_id == building_id,
                        Food.created_at >= start_date
                    )
                )
            )
            active_users = active_users_result.scalar() or 0
            
            # Food posts in building
            food_posts_result = await self.db.execute(
                select(func.count(Food.id)).where(
                    and_(
                        Food.building_id == building_id,
                        Food.created_at >= start_date
                    )
                )
            )
            food_posts = food_posts_result.scalar()
            
            # Completed exchanges
            completed_exchanges_result = await self.db.execute(
                select(func.count(Exchange.id))
                .select_from(Exchange)
                .join(Food, Food.id == Exchange.food_id)
                .where(
                    and_(
                        Food.building_id == building_id,
                        Exchange.status == ExchangeStatus.COMPLETED,
                        Exchange.completed_at >= start_date
                    )
                )
            )
            completed_exchanges = completed_exchanges_result.scalar()
            
            # Top sharers
            top_sharers_result = await self.db.execute(
                select(User.id, User.display_name, User.apartment_number, func.count(Food.id).label("food_count"))
                .select_from(User)
                .join(Food, Food.sharer_id == User.id)
                .where(
                    and_(
                        User.building_id == building_id,
                        Food.created_at >= start_date
                    )
                )
                .group_by(User.id, User.display_name, User.apartment_number)
                .order_by(desc("food_count"))
                .limit(5)
            )
            top_sharers = [
                {
                    "user_id": row.id,
                    "name": row.display_name,
                    "apartment": row.apartment_number,
                    "posts_count": row.food_count
                }
                for row in top_sharers_result.all()
            ]
            
            return {
                "building": {
                    "id": building.id,
                    "name": building.name,
                    "address": building.address
                },
                "period_days": days,
                "users": {
                    "total": total_users,
                    "active": active_users
                },
                "activity": {
                    "food_posts": food_posts,
                    "completed_exchanges": completed_exchanges
                },
                "top_sharers": top_sharers,
                "updated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error("Error getting building stats", building_id=building_id, error=str(e), exc_info=True)
            raise

    async def get_user_activity(self, user_id: str) -> Dict[str, Any]:
        """Get detailed activity for a specific user."""
        logger.info("Getting user activity", user_id=user_id)
        
        try:
            # User info
            user_result = await self.db.execute(
                select(User).options(selectinload(User.building))
                .where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return None
            
            # Credit info
            credit_result = await self.db.execute(
                select(Credit).where(Credit.user_id == user_id)
            )
            credit = credit_result.scalar_one_or_none()
            
            # Food posts
            food_posts_result = await self.db.execute(
                select(Food).where(Food.sharer_id == user_id)
                .order_by(desc(Food.created_at))
                .limit(10)
            )
            food_posts = food_posts_result.scalars().all()
            
            # Exchanges as sharer
            sharer_exchanges_result = await self.db.execute(
                select(Exchange).options(
                    selectinload(Exchange.food),
                    selectinload(Exchange.recipient)
                ).where(Exchange.sharer_id == user_id)
                .order_by(desc(Exchange.created_at))
                .limit(10)
            )
            sharer_exchanges = sharer_exchanges_result.scalars().all()
            
            # Exchanges as recipient
            recipient_exchanges_result = await self.db.execute(
                select(Exchange).options(
                    selectinload(Exchange.food),
                    selectinload(Exchange.sharer)
                ).where(Exchange.recipient_id == user_id)
                .order_by(desc(Exchange.created_at))
                .limit(10)
            )
            recipient_exchanges = recipient_exchanges_result.scalars().all()
            
            # Recent transactions
            transactions_result = await self.db.execute(
                select(CreditTransaction)
                .where(CreditTransaction.user_id == user_id)
                .order_by(desc(CreditTransaction.created_at))
                .limit(10)
            )
            transactions = transactions_result.scalars().all()
            
            return {
                "user": {
                    "id": user.id,
                    "name": user.display_name,
                    "email": user.email,
                    "phone": user.phone_number,
                    "apartment": user.apartment_number,
                    "building": {
                        "id": user.building.id,
                        "name": user.building.name
                    } if user.building else None,
                    "verified": user.is_verified,
                    "created_at": user.created_at,
                    "last_active": user.last_active_at
                },
                "credits": {
                    "balance": credit.balance if credit else 0,
                    "lifetime_earned": credit.lifetime_earned if credit else 0,
                    "lifetime_spent": credit.lifetime_spent if credit else 0
                },
                "activity": {
                    "food_posts_count": len(food_posts),
                    "exchanges_as_sharer": len(sharer_exchanges),
                    "exchanges_as_recipient": len(recipient_exchanges)
                },
                "recent_food_posts": [
                    {
                        "id": food.id,
                        "title": food.title,
                        "status": food.status,
                        "created_at": food.created_at
                    }
                    for food in food_posts
                ],
                "recent_transactions": [
                    {
                        "id": txn.id,
                        "type": txn.transaction_type,
                        "amount": txn.amount,
                        "description": txn.description,
                        "created_at": txn.created_at
                    }
                    for txn in transactions
                ]
            }
            
        except Exception as e:
            logger.error("Error getting user activity", user_id=user_id, error=str(e), exc_info=True)
            raise

    async def get_problematic_exchanges(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get exchanges that may need admin attention."""
        logger.info("Getting problematic exchanges", days=days)
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Overdue exchanges (confirmed but past pickup time)
            overdue_result = await self.db.execute(
                select(Exchange).options(
                    selectinload(Exchange.food),
                    selectinload(Exchange.sharer),
                    selectinload(Exchange.recipient)
                ).where(
                    and_(
                        Exchange.status == ExchangeStatus.CONFIRMED,
                        Exchange.scheduled_pickup_at < datetime.utcnow(),
                        Exchange.scheduled_pickup_at > cutoff_date
                    )
                )
            )
            
            # Long pending exchanges
            long_pending_result = await self.db.execute(
                select(Exchange).options(
                    selectinload(Exchange.food),
                    selectinload(Exchange.sharer),
                    selectinload(Exchange.recipient)
                ).where(
                    and_(
                        Exchange.status == ExchangeStatus.PENDING,
                        Exchange.created_at < datetime.utcnow() - timedelta(hours=24)
                    )
                )
            )
            
            problematic = []
            
            for exchange in overdue_result.scalars().all():
                hours_overdue = (datetime.utcnow() - exchange.scheduled_pickup_at).total_seconds() / 3600
                problematic.append({
                    "id": exchange.id,
                    "type": "overdue",
                    "severity": "high" if hours_overdue > 24 else "medium",
                    "description": f"Exchange overdue by {int(hours_overdue)} hours",
                    "food_title": exchange.food.title if exchange.food else "Unknown",
                    "sharer_name": exchange.sharer.display_name if exchange.sharer else "Unknown",
                    "recipient_name": exchange.recipient.display_name if exchange.recipient else "Unknown",
                    "scheduled_pickup": exchange.scheduled_pickup_at,
                    "created_at": exchange.created_at
                })
            
            for exchange in long_pending_result.scalars().all():
                hours_pending = (datetime.utcnow() - exchange.created_at).total_seconds() / 3600
                problematic.append({
                    "id": exchange.id,
                    "type": "long_pending",
                    "severity": "medium",
                    "description": f"Exchange pending for {int(hours_pending)} hours",
                    "food_title": exchange.food.title if exchange.food else "Unknown",
                    "sharer_name": exchange.sharer.display_name if exchange.sharer else "Unknown",
                    "recipient_name": exchange.recipient.display_name if exchange.recipient else "Unknown",
                    "created_at": exchange.created_at
                })
            
            # Sort by severity and creation time
            severity_order = {"high": 0, "medium": 1, "low": 2}
            problematic.sort(key=lambda x: (severity_order[x["severity"]], x["created_at"]))
            
            return problematic
            
        except Exception as e:
            logger.error("Error getting problematic exchanges", error=str(e), exc_info=True)
            raise

    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health indicators."""
        logger.info("Getting system health")
        
        try:
            now = datetime.utcnow()
            
            # Database connectivity (this call itself tests it)
            db_healthy = True
            
            # Recent activity (food posts in last hour)
            recent_posts_result = await self.db.execute(
                select(func.count(Food.id))
                .where(Food.created_at > now - timedelta(hours=1))
            )
            recent_posts = recent_posts_result.scalar()
            
            # Failed exchanges (cancelled in last 24h)
            failed_exchanges_result = await self.db.execute(
                select(func.count(Exchange.id))
                .where(
                    and_(
                        Exchange.status == ExchangeStatus.CANCELLED,
                        Exchange.cancelled_at > now - timedelta(hours=24)
                    )
                )
            )
            failed_exchanges = failed_exchanges_result.scalar()
            
            # Determine overall health
            health_score = 100
            issues = []
            
            if recent_posts == 0:
                health_score -= 20
                issues.append("No recent food posts (last hour)")
            
            if failed_exchanges > 5:  # Arbitrary threshold
                health_score -= 30
                issues.append(f"High number of failed exchanges: {failed_exchanges}")
            
            health_status = "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "unhealthy"
            
            return {
                "status": health_status,
                "score": health_score,
                "database_connected": db_healthy,
                "recent_activity": {
                    "posts_last_hour": recent_posts,
                    "failed_exchanges_24h": failed_exchanges
                },
                "issues": issues,
                "checked_at": now
            }
            
        except Exception as e:
            logger.error("Error getting system health", error=str(e), exc_info=True)
            return {
                "status": "unhealthy",
                "score": 0,
                "database_connected": False,
                "issues": [f"Database error: {str(e)}"],
                "checked_at": now
            }