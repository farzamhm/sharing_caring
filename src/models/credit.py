"""Credit system models."""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base


class TransactionType(str, Enum):
    """Credit transaction type enumeration."""
    EARNED_SHARING = "earned_sharing"      # Credits earned from sharing food
    SPENT_CLAIMING = "spent_claiming"      # Credits spent claiming food
    BONUS_SIGNUP = "bonus_signup"          # Initial signup bonus
    BONUS_REFERRAL = "bonus_referral"      # Referral bonus
    BONUS_COMMUNITY = "bonus_community"    # Community milestone bonus
    ADJUSTMENT_ADMIN = "adjustment_admin"   # Manual admin adjustment
    REFUND_CANCELLED = "refund_cancelled"  # Refund for cancelled exchange
    PENALTY_VIOLATION = "penalty_violation" # Penalty for rule violation


class Credit(Base):
    """User credit account model."""
    
    __tablename__ = "credits"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    
    # User association (one-to-one)
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
        unique=True
    )
    
    # Balance
    balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lifetime_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lifetime_spent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    user = relationship("User", back_populates="credit_account")
    
    def __repr__(self) -> str:
        return f"<Credit(user_id='{self.user_id}', balance={self.balance})>"
    
    @property
    def can_spend(self, amount: int) -> bool:
        """Check if user can spend specified amount."""
        return self.balance >= amount
    
    def add_credits(self, amount: int) -> bool:
        """Add credits to account."""
        if amount <= 0:
            return False
        
        self.balance += amount
        self.lifetime_earned += amount
        return True
    
    def spend_credits(self, amount: int) -> bool:
        """Spend credits from account."""
        if not self.can_spend(amount):
            return False
        
        self.balance -= amount
        self.lifetime_spent += amount
        return True


class CreditTransaction(Base):
    """Credit transaction history model."""
    
    __tablename__ = "credit_transactions"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    
    # User
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False
    )
    
    # Transaction details
    transaction_type: Mapped[TransactionType] = mapped_column(
        String(50),
        nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # Positive for credit, negative for debit
    balance_before: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Description and context
    description: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Related entities
    food_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("foods.id"),
    )
    exchange_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("exchanges.id"),
    )
    
    # Administrative
    created_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="credit_transactions")
    food = relationship("Food", foreign_keys=[food_id])
    exchange = relationship("Exchange", foreign_keys=[exchange_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self) -> str:
        return f"<CreditTransaction(id='{self.id}', user_id='{self.user_id}', amount={self.amount})>"
    
    @property
    def is_credit(self) -> bool:
        """Check if transaction is a credit (positive amount)."""
        return self.amount > 0
    
    @property
    def is_debit(self) -> bool:
        """Check if transaction is a debit (negative amount)."""
        return self.amount < 0
    
    @classmethod
    def create_transaction(
        cls,
        user_id: str,
        transaction_type: TransactionType,
        amount: int,
        balance_before: int,
        balance_after: int,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        food_id: Optional[str] = None,
        exchange_id: Optional[str] = None,
        created_by_id: Optional[str] = None,
    ) -> "CreditTransaction":
        """Factory method to create a credit transaction."""
        return cls(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            notes=notes,
            food_id=food_id,
            exchange_id=exchange_id,
            created_by_id=created_by_id,
        )