"""Credit system endpoints."""

from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...core.database import get_db_session
from ...core.logging import get_logger
from ...models.credit import Credit, CreditTransaction, TransactionType
from ...models.user import User

router = APIRouter()
logger = get_logger(__name__)


class CreditBalanceResponse:
    """Credit balance response schema."""
    balance: int
    lifetime_earned: int
    lifetime_spent: int
    
    def __init__(self, credit: Credit):
        self.balance = credit.balance
        self.lifetime_earned = credit.lifetime_earned
        self.lifetime_spent = credit.lifetime_spent


class CreditTransactionResponse:
    """Credit transaction response schema."""
    id: str
    transaction_type: TransactionType
    amount: int
    balance_before: int
    balance_after: int
    description: Optional[str]
    notes: Optional[str]
    food_id: Optional[str]
    exchange_id: Optional[str]
    created_at: datetime
    
    def __init__(self, transaction: CreditTransaction):
        self.id = transaction.id
        self.transaction_type = transaction.transaction_type
        self.amount = transaction.amount
        self.balance_before = transaction.balance_before
        self.balance_after = transaction.balance_after
        self.description = transaction.description
        self.notes = transaction.notes
        self.food_id = transaction.food_id
        self.exchange_id = transaction.exchange_id
        self.created_at = transaction.created_at


class LeaderboardEntry:
    """Leaderboard entry schema."""
    user_id: str
    user_name: str
    apartment_number: Optional[str]
    balance: int
    lifetime_earned: int
    rank: int
    
    def __init__(self, user: User, credit: Credit, rank: int):
        self.user_id = user.id
        self.user_name = user.display_name
        self.apartment_number = user.apartment_number
        self.balance = credit.balance
        self.lifetime_earned = credit.lifetime_earned
        self.rank = rank


@router.get("/balance")
async def get_credit_balance(
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get user's credit balance."""
    logger.info("Credit balance requested")
    
    try:
        # TODO: Get user ID from JWT token
        # For now, use sample user for testing
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's credit account
        result = await db.execute(
            select(Credit).where(Credit.user_id == user.id)
        )
        credit = result.scalar_one_or_none()
        
        if not credit:
            raise HTTPException(status_code=404, detail="Credit account not found")
        
        response = CreditBalanceResponse(credit)
        
        return {
            "balance": response.balance,
            "lifetime_earned": response.lifetime_earned,
            "lifetime_spent": response.lifetime_spent,
            "updated_at": credit.updated_at.isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting credit balance", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/transactions")
async def list_credit_transactions(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    transaction_type: Optional[TransactionType] = Query(None),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """List user's credit transactions."""
    logger.info(
        "Credit transactions requested",
        limit=limit,
        offset=offset,
        transaction_type=transaction_type
    )
    
    try:
        # TODO: Get user ID from JWT token
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build query
        query = (
            select(CreditTransaction)
            .where(CreditTransaction.user_id == user.id)
        )
        
        # Apply transaction type filter
        if transaction_type:
            query = query.where(CreditTransaction.transaction_type == transaction_type)
        
        # Order by most recent first
        query = query.order_by(desc(CreditTransaction.created_at))
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        transactions = result.scalars().all()
        
        # Convert to response format
        transaction_responses = []
        for transaction in transactions:
            response = CreditTransactionResponse(transaction)
            transaction_responses.append({
                "id": response.id,
                "transaction_type": response.transaction_type,
                "amount": response.amount,
                "balance_before": response.balance_before,
                "balance_after": response.balance_after,
                "description": response.description,
                "notes": response.notes,
                "food_id": response.food_id,
                "exchange_id": response.exchange_id,
                "created_at": response.created_at.isoformat(),
            })
        
        return {
            "transactions": transaction_responses,
            "total_count": len(transaction_responses),
            "page": offset // limit + 1,
            "page_size": limit,
            "has_more": len(transaction_responses) == limit,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error listing credit transactions", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/leaderboard")
async def get_credit_leaderboard(
    building_id: Optional[str] = Query(None),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get credit leaderboard."""
    logger.info("Credit leaderboard requested", building_id=building_id, limit=limit)
    
    try:
        # TODO: Get user's building if not specified
        if not building_id:
            from ...services.user_service import UserService
            user_service = UserService(db)
            user = await user_service.get_by_telegram_id(123456789)
            if user:
                building_id = user.building_id
        
        if not building_id:
            raise HTTPException(status_code=400, detail="Building ID required")
        
        # Get top users by lifetime earned credits in the building
        result = await db.execute(
            select(User, Credit)
            .join(Credit, User.id == Credit.user_id)
            .where(User.building_id == building_id)
            .order_by(desc(Credit.lifetime_earned), desc(Credit.balance))
            .limit(limit)
        )
        
        leaderboard_data = result.all()
        
        # Convert to response format
        leaderboard = []
        for rank, (user, credit) in enumerate(leaderboard_data, 1):
            entry = LeaderboardEntry(user, credit, rank)
            leaderboard.append({
                "rank": entry.rank,
                "user_id": entry.user_id,
                "user_name": entry.user_name,
                "apartment_number": entry.apartment_number,
                "balance": entry.balance,
                "lifetime_earned": entry.lifetime_earned,
            })
        
        return {
            "leaderboard": leaderboard,
            "building_id": building_id,
            "total_users": len(leaderboard),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting credit leaderboard", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats")
async def get_credit_stats(
    period: str = Query("week", regex="^(day|week|month|all)$"),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get user's credit statistics."""
    logger.info("Credit stats requested", period=period)
    
    try:
        # TODO: Get user ID from JWT token
        from ...services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_telegram_id(123456789)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate period start
        now = datetime.utcnow()
        if period == "day":
            start_date = now - timedelta(days=1)
        elif period == "week":
            start_date = now - timedelta(weeks=1)
        elif period == "month":
            start_date = now - timedelta(days=30)
        else:  # all
            start_date = datetime.min
        
        # Get transactions in period
        query = (
            select(CreditTransaction)
            .where(CreditTransaction.user_id == user.id)
            .where(CreditTransaction.created_at >= start_date)
        )
        
        result = await db.execute(query)
        transactions = result.scalars().all()
        
        # Calculate stats
        earned = sum(t.amount for t in transactions if t.amount > 0)
        spent = abs(sum(t.amount for t in transactions if t.amount < 0))
        transaction_count = len(transactions)
        
        # Get current balance
        credit_result = await db.execute(
            select(Credit).where(Credit.user_id == user.id)
        )
        credit = credit_result.scalar_one_or_none()
        current_balance = credit.balance if credit else 0
        
        return {
            "period": period,
            "current_balance": current_balance,
            "earned_in_period": earned,
            "spent_in_period": spent,
            "net_change": earned - spent,
            "transaction_count": transaction_count,
            "start_date": start_date.isoformat() if start_date != datetime.min else None,
            "end_date": now.isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting credit stats", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")