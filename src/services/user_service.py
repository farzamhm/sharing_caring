"""User management service."""

import random
import string
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.config import get_settings
from ..core.logging import get_logger
from ..models.user import User, UserStatus
from ..models.building import Building
from ..models.credit import Credit, CreditTransaction, TransactionType
from ..services.sms_service import SMSService

settings = get_settings()
logger = get_logger(__name__)


class UserService:
    """Service for user management operations."""
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.sms_service = SMSService()
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        try:
            result = await self.db.execute(
                select(User)
                .options(selectinload(User.building), selectinload(User.credit_account))
                .where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error getting user by telegram ID", telegram_id=telegram_id, error=str(e))
            return None
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            result = await self.db.execute(
                select(User)
                .options(selectinload(User.building), selectinload(User.credit_account))
                .where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error getting user by ID", user_id=user_id, error=str(e))
            return None
    
    async def create_user(
        self,
        telegram_id: int,
        telegram_username: Optional[str],
        first_name: str,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        building_id: Optional[str] = None,
        apartment_number: Optional[str] = None,
    ) -> Optional[User]:
        """Create a new user."""
        try:
            # Check if user already exists
            existing_user = await self.get_by_telegram_id(telegram_id)
            if existing_user:
                logger.info("User already exists", telegram_id=telegram_id, user_id=existing_user.id)
                return existing_user
            
            # Create new user
            user = User(
                telegram_id=telegram_id,
                telegram_username=telegram_username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                building_id=building_id,
                apartment_number=apartment_number,
                status=UserStatus.PENDING,
            )
            
            self.db.add(user)
            await self.db.flush()  # Get the ID
            
            # Create credit account with initial balance
            credit_account = Credit(
                user_id=user.id,
                balance=settings.credit_initial_balance,
                lifetime_earned=settings.credit_initial_balance,
            )
            
            self.db.add(credit_account)
            await self.db.flush()
            
            # Create initial credit transaction
            transaction = CreditTransaction.create_transaction(
                user_id=user.id,
                transaction_type=TransactionType.BONUS_SIGNUP,
                amount=settings.credit_initial_balance,
                balance_before=0,
                balance_after=settings.credit_initial_balance,
                description=f"Welcome bonus: {settings.credit_initial_balance} credits",
                notes="Initial signup bonus for new users",
            )
            
            self.db.add(transaction)
            
            logger.info("Created new user", user_id=user.id, telegram_id=telegram_id)
            return user
            
        except Exception as e:
            logger.error("Error creating user", telegram_id=telegram_id, error=str(e), exc_info=True)
            await self.db.rollback()
            return None
    
    async def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user information."""
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return None
            
            # Update allowed fields
            allowed_fields = {
                'first_name', 'last_name', 'preferred_name', 'phone_number',
                'apartment_number', 'bio', 'dietary_restrictions', 'allergens',
                'notifications_enabled', 'sharing_enabled', 'building_id'
            }
            
            for key, value in kwargs.items():
                if key in allowed_fields and hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            
            logger.info("Updated user", user_id=user_id, updated_fields=list(kwargs.keys()))
            return user
            
        except Exception as e:
            logger.error("Error updating user", user_id=user_id, error=str(e), exc_info=True)
            return None
    
    async def request_phone_verification(self, user_id: str, phone_number: str) -> bool:
        """Request phone number verification."""
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            # Generate verification code
            verification_code = ''.join(random.choices(string.digits, k=6))
            
            # Set verification code and expiry
            user.phone_number = phone_number
            user.verification_code = verification_code
            user.verification_expires_at = datetime.utcnow() + timedelta(minutes=10)
            
            # Send SMS (if SMS service is configured)
            if settings.twilio_account_sid and settings.twilio_auth_token:
                success = await self.sms_service.send_verification_code(
                    phone_number, verification_code
                )
                if not success:
                    logger.error("Failed to send SMS", user_id=user_id, phone_number=phone_number)
                    return False
            else:
                logger.info(
                    "SMS not configured, verification code generated",
                    user_id=user_id,
                    code=verification_code  # Only log in development
                )
            
            logger.info("Phone verification requested", user_id=user_id, phone_number=phone_number)
            return True
            
        except Exception as e:
            logger.error("Error requesting phone verification", user_id=user_id, error=str(e))
            return False
    
    async def verify_phone_code(self, user_id: str, code: str) -> bool:
        """Verify phone verification code."""
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            # Check if code matches and hasn't expired
            if (
                user.verification_code == code
                and user.verification_expires_at
                and datetime.utcnow() < user.verification_expires_at
            ):
                user.is_phone_verified = True
                user.verification_code = None
                user.verification_expires_at = None
                
                # Update status if building is also set
                if user.building_id:
                    user.status = UserStatus.VERIFIED
                
                logger.info("Phone verification successful", user_id=user_id)
                return True
            else:
                logger.info("Phone verification failed", user_id=user_id, provided_code=code)
                return False
                
        except Exception as e:
            logger.error("Error verifying phone code", user_id=user_id, error=str(e))
            return False
    
    async def assign_to_building(self, user_id: str, building_id: str) -> bool:
        """Assign user to a building."""
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            # Verify building exists and has capacity
            result = await self.db.execute(
                select(Building).where(Building.id == building_id)
            )
            building = result.scalar_one_or_none()
            
            if not building or not building.has_capacity:
                logger.error("Building not found or at capacity", building_id=building_id)
                return False
            
            user.building_id = building_id
            
            # Update status if phone is also verified
            if user.is_phone_verified:
                user.status = UserStatus.VERIFIED
            
            logger.info("User assigned to building", user_id=user_id, building_id=building_id)
            return True
            
        except Exception as e:
            logger.error("Error assigning user to building", user_id=user_id, error=str(e))
            return False
    
    async def get_building_users(self, building_id: str, limit: int = 50) -> List[User]:
        """Get users in a building."""
        try:
            result = await self.db.execute(
                select(User)
                .where(User.building_id == building_id)
                .where(User.status == UserStatus.VERIFIED)
                .limit(limit)
            )
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error("Error getting building users", building_id=building_id, error=str(e))
            return []
    
    async def update_last_active(self, user_id: str) -> None:
        """Update user's last active timestamp."""
        try:
            user = await self.get_by_id(user_id)
            if user:
                user.last_active_at = datetime.utcnow()
                
        except Exception as e:
            logger.error("Error updating last active", user_id=user_id, error=str(e))