"""Unit tests for UserService."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from src.services.user_service import UserService
from src.models.user import User
from src.models.building import Building


class TestUserService:
    """Test cases for UserService."""

    @pytest.mark.asyncio
    async def test_create_user(self, test_db, sample_building):
        """Test user creation."""
        service = UserService(test_db)
        
        user_data = {
            "telegram_id": 555666777,
            "email": "newuser@example.com",
            "display_name": "New User",
            "phone_number": "+1555666777",
            "apartment_number": "205",
            "building_id": sample_building.id
        }
        
        user = await service.create_user(**user_data)
        
        assert user is not None
        assert user.telegram_id == 555666777
        assert user.email == "newuser@example.com"
        assert user.display_name == "New User"
        assert user.apartment_number == "205"
        assert user.building_id == sample_building.id
        assert user.is_verified is False
        assert user.verification_code is not None
        assert len(user.verification_code) == 6
        assert user.verification_code_expires_at > datetime.utcnow()

    @pytest.mark.asyncio
    async def test_create_duplicate_telegram_id(self, test_db, sample_user, sample_building):
        """Test that creating user with duplicate telegram_id fails."""
        service = UserService(test_db)
        
        user_data = {
            "telegram_id": sample_user.telegram_id,  # Duplicate
            "email": "different@example.com",
            "display_name": "Different User",
            "phone_number": "+1999888777",
            "apartment_number": "999",
            "building_id": sample_building.id
        }
        
        user = await service.create_user(**user_data)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_telegram_id(self, test_db, sample_user):
        """Test getting user by telegram ID."""
        service = UserService(test_db)
        
        # Existing user
        user = await service.get_by_telegram_id(sample_user.telegram_id)
        assert user is not None
        assert user.id == sample_user.id
        
        # Non-existing user
        user = await service.get_by_telegram_id(999999999)
        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_email(self, test_db, sample_user):
        """Test getting user by email."""
        service = UserService(test_db)
        
        # Existing user
        user = await service.get_by_email(sample_user.email)
        assert user is not None
        assert user.id == sample_user.id
        
        # Non-existing user
        user = await service.get_by_email("nonexistent@example.com")
        assert user is None

    @pytest.mark.asyncio
    async def test_verify_user_valid_code(self, test_db, sample_building):
        """Test user verification with valid code."""
        service = UserService(test_db)
        
        # Create unverified user
        user = await service.create_user(
            telegram_id=777888999,
            email="verify@example.com",
            display_name="Verify User",
            phone_number="+1777888999",
            apartment_number="301",
            building_id=sample_building.id
        )
        
        assert not user.is_verified
        verification_code = user.verification_code
        
        # Verify user
        success = await service.verify_user(user.telegram_id, verification_code)
        
        assert success is True
        
        # Refresh user from database
        await test_db.refresh(user)
        assert user.is_verified is True
        assert user.verification_code is None
        assert user.verification_code_expires_at is None

    @pytest.mark.asyncio
    async def test_verify_user_invalid_code(self, test_db, sample_building):
        """Test user verification with invalid code."""
        service = UserService(test_db)
        
        # Create unverified user
        user = await service.create_user(
            telegram_id=888999000,
            email="verify2@example.com",
            display_name="Verify User 2",
            phone_number="+1888999000",
            apartment_number="302",
            building_id=sample_building.id
        )
        
        # Try to verify with wrong code
        success = await service.verify_user(user.telegram_id, "000000")
        
        assert success is False
        
        # User should still be unverified
        await test_db.refresh(user)
        assert user.is_verified is False

    @pytest.mark.asyncio
    async def test_verify_user_expired_code(self, test_db, sample_building):
        """Test user verification with expired code."""
        service = UserService(test_db)
        
        # Create user with expired verification
        user = User(
            telegram_id=111222333,
            email="expired@example.com",
            display_name="Expired User",
            phone_number="+1111222333",
            apartment_number="401",
            building_id=sample_building.id,
            verification_code="123456",
            verification_code_expires_at=datetime.utcnow() - timedelta(hours=1)  # Expired
        )
        test_db.add(user)
        await test_db.commit()
        
        # Try to verify with expired code
        success = await service.verify_user(user.telegram_id, "123456")
        
        assert success is False

    @pytest.mark.asyncio
    async def test_regenerate_verification_code(self, test_db, sample_building):
        """Test regenerating verification code."""
        service = UserService(test_db)
        
        # Create unverified user
        user = await service.create_user(
            telegram_id=444555666,
            email="regen@example.com",
            display_name="Regen User",
            phone_number="+1444555666",
            apartment_number="501",
            building_id=sample_building.id
        )
        
        original_code = user.verification_code
        original_expires = user.verification_code_expires_at
        
        # Regenerate code
        new_user = await service.regenerate_verification_code(user.telegram_id)
        
        assert new_user is not None
        assert new_user.verification_code != original_code
        assert new_user.verification_code_expires_at > original_expires

    @pytest.mark.asyncio
    async def test_update_profile(self, test_db, sample_user):
        """Test updating user profile."""
        service = UserService(test_db)
        
        updated_user = await service.update_profile(
            user_id=sample_user.id,
            display_name="Updated Name",
            apartment_number="999"
        )
        
        assert updated_user is not None
        assert updated_user.display_name == "Updated Name"
        assert updated_user.apartment_number == "999"
        assert updated_user.email == sample_user.email  # Unchanged

    @pytest.mark.asyncio
    async def test_update_last_active(self, test_db, sample_user):
        """Test updating user last active timestamp."""
        service = UserService(test_db)
        
        original_last_active = sample_user.last_active_at
        
        await service.update_last_active(sample_user.id)
        
        # Refresh user from database
        await test_db.refresh(sample_user)
        
        # Should be updated (allowing for small time differences)
        if original_last_active:
            assert sample_user.last_active_at > original_last_active
        else:
            assert sample_user.last_active_at is not None

    @pytest.mark.asyncio
    async def test_get_building_users(self, test_db, sample_building, sample_user, sample_user2):
        """Test getting all users in a building."""
        service = UserService(test_db)
        
        users = await service.get_building_users(sample_building.id)
        
        assert len(users) >= 2  # At least our two sample users
        user_ids = [user.id for user in users]
        assert sample_user.id in user_ids
        assert sample_user2.id in user_ids

    @pytest.mark.asyncio
    async def test_delete_user(self, test_db, sample_building):
        """Test deleting a user."""
        service = UserService(test_db)
        
        # Create user to delete
        user = await service.create_user(
            telegram_id=999888777,
            email="delete@example.com",
            display_name="Delete User",
            phone_number="+1999888777",
            apartment_number="999",
            building_id=sample_building.id
        )
        
        user_id = user.id
        
        # Delete user
        success = await service.delete_user(user_id)
        assert success is True
        
        # User should not be found
        deleted_user = await service.get_by_telegram_id(999888777)
        assert deleted_user is None