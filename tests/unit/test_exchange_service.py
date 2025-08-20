"""Unit tests for ExchangeService."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from src.services.exchange_service import ExchangeService
from src.models.exchange import Exchange, ExchangeStatus


class TestExchangeService:
    """Test cases for ExchangeService."""

    @pytest.mark.asyncio
    async def test_get_exchange_by_id(self, test_db, sample_exchange):
        """Test getting exchange by ID."""
        service = ExchangeService(test_db)
        
        # Existing exchange
        exchange = await service.get_exchange_by_id(sample_exchange.id)
        assert exchange is not None
        assert exchange.id == sample_exchange.id
        
        # Non-existing exchange
        exchange = await service.get_exchange_by_id("non-existent-id")
        assert exchange is None

    @pytest.mark.asyncio
    async def test_get_user_exchanges(self, test_db, sample_exchange, sample_user):
        """Test getting user's exchanges."""
        service = ExchangeService(test_db)
        
        exchanges = await service.get_user_exchanges(
            user_id=sample_user.id,
            limit=10
        )
        
        assert len(exchanges) >= 1
        exchange_ids = [e.id for e in exchanges]
        assert sample_exchange.id in exchange_ids

    @pytest.mark.asyncio
    async def test_get_user_exchanges_by_role(self, test_db, sample_exchange, sample_user, sample_user2):
        """Test getting exchanges filtered by user role."""
        service = ExchangeService(test_db)
        
        # Get exchanges where user is sharer
        sharer_exchanges = await service.get_user_exchanges(
            user_id=sample_user.id,
            role="sharer"
        )
        
        assert len(sharer_exchanges) >= 1
        assert all(e.sharer_id == sample_user.id for e in sharer_exchanges)
        
        # Get exchanges where user is recipient
        recipient_exchanges = await service.get_user_exchanges(
            user_id=sample_user2.id,
            role="recipient"
        )
        
        assert len(recipient_exchanges) >= 1
        assert all(e.recipient_id == sample_user2.id for e in recipient_exchanges)

    @pytest.mark.asyncio
    async def test_get_active_exchanges(self, test_db, sample_exchange, sample_user):
        """Test getting active exchanges."""
        service = ExchangeService(test_db)
        
        # Sample exchange should be active (PENDING status)
        active_exchanges = await service.get_active_exchanges(sample_user.id)
        
        assert len(active_exchanges) >= 1
        exchange_ids = [e.id for e in active_exchanges]
        assert sample_exchange.id in exchange_ids

    @pytest.mark.asyncio
    async def test_confirm_exchange_sharer(self, test_db, sample_exchange, sample_user):
        """Test sharer confirming an exchange."""
        service = ExchangeService(test_db)
        
        # Sharer confirms
        success = await service.confirm_exchange(
            exchange_id=sample_exchange.id,
            user_id=sample_user.id,  # Sharer
            notes="Ready for pickup!"
        )
        
        assert success is True
        
        # Check exchange state
        await test_db.refresh(sample_exchange)
        assert sample_exchange.sharer_confirmed is True
        assert sample_exchange.sharer_notes == "Ready for pickup!"
        assert sample_exchange.sharer_confirmed_at is not None
        assert sample_exchange.status == ExchangeStatus.PENDING  # Still pending recipient

    @pytest.mark.asyncio
    async def test_confirm_exchange_recipient(self, test_db, sample_exchange, sample_user2):
        """Test recipient confirming an exchange."""
        service = ExchangeService(test_db)
        
        # Recipient confirms
        success = await service.confirm_exchange(
            exchange_id=sample_exchange.id,
            user_id=sample_user2.id,  # Recipient
            notes="Will pick up at 3pm"
        )
        
        assert success is True
        
        # Check exchange state
        await test_db.refresh(sample_exchange)
        assert sample_exchange.recipient_confirmed is True
        assert sample_exchange.recipient_notes == "Will pick up at 3pm"
        assert sample_exchange.recipient_confirmed_at is not None
        assert sample_exchange.status == ExchangeStatus.PENDING  # Still pending sharer

    @pytest.mark.asyncio
    async def test_confirm_exchange_both_parties(self, test_db, sample_exchange, sample_user, sample_user2):
        """Test exchange becomes confirmed when both parties confirm."""
        service = ExchangeService(test_db)
        
        # Both parties confirm
        await service.confirm_exchange(sample_exchange.id, sample_user.id, "Sharer ready")
        await service.confirm_exchange(sample_exchange.id, sample_user2.id, "Recipient ready")
        
        # Should now be CONFIRMED
        await test_db.refresh(sample_exchange)
        assert sample_exchange.status == ExchangeStatus.CONFIRMED
        assert sample_exchange.sharer_confirmed is True
        assert sample_exchange.recipient_confirmed is True

    @pytest.mark.asyncio
    async def test_confirm_exchange_unauthorized(self, test_db, sample_exchange, sample_building):
        """Test that unauthorized users cannot confirm exchange."""
        service = ExchangeService(test_db)
        
        # Create third user not involved in exchange
        from src.services.user_service import UserService
        user_service = UserService(test_db)
        user3 = await user_service.create_user(
            telegram_id=777888999,
            email="user3@example.com",
            display_name="User 3",
            phone_number="+1777888999",
            apartment_number="103",
            building_id=sample_building.id
        )
        
        # Third user tries to confirm
        success = await service.confirm_exchange(
            exchange_id=sample_exchange.id,
            user_id=user3.id,
            notes="Unauthorized confirmation"
        )
        
        assert success is False

    @pytest.mark.asyncio
    async def test_complete_exchange(self, test_db, sample_exchange, sample_user, sample_user2, sample_credit_account):
        """Test completing an exchange."""
        service = ExchangeService(test_db)
        
        # First confirm the exchange from both sides
        await service.confirm_exchange(sample_exchange.id, sample_user.id, "Ready")
        await service.confirm_exchange(sample_exchange.id, sample_user2.id, "Ready")
        
        # Complete the exchange
        success = await service.complete_exchange(
            exchange_id=sample_exchange.id,
            user_id=sample_user.id,  # Sharer completes
            rating=5,
            notes="Great pickup!"
        )
        
        assert success is True
        
        # Check exchange state
        await test_db.refresh(sample_exchange)
        assert sample_exchange.status == ExchangeStatus.COMPLETED
        assert sample_exchange.sharer_rating == 5
        assert sample_exchange.sharer_notes == "Great pickup!"
        assert sample_exchange.completed_at is not None
        assert sample_exchange.actual_pickup_at is not None

    @pytest.mark.asyncio
    async def test_complete_unconfirmed_exchange_fails(self, test_db, sample_exchange, sample_user):
        """Test that unconfirmed exchange cannot be completed."""
        service = ExchangeService(test_db)
        
        # Try to complete without confirmation
        success = await service.complete_exchange(
            exchange_id=sample_exchange.id,
            user_id=sample_user.id,
            rating=5
        )
        
        assert success is False

    @pytest.mark.asyncio
    async def test_cancel_exchange(self, test_db, sample_exchange, sample_user):
        """Test cancelling an exchange."""
        service = ExchangeService(test_db)
        
        success = await service.cancel_exchange(
            exchange_id=sample_exchange.id,
            user_id=sample_user.id,
            reason="Emergency came up"
        )
        
        assert success is True
        
        # Check exchange state
        await test_db.refresh(sample_exchange)
        assert sample_exchange.status == ExchangeStatus.CANCELLED
        assert sample_exchange.cancelled_by_id == sample_user.id
        assert sample_exchange.cancellation_reason == "Emergency came up"
        assert sample_exchange.cancelled_at is not None

    @pytest.mark.asyncio
    async def test_cancel_completed_exchange_fails(self, test_db, sample_exchange, sample_user, sample_user2, sample_credit_account):
        """Test that completed exchange cannot be cancelled."""
        service = ExchangeService(test_db)
        
        # First complete the exchange
        await service.confirm_exchange(sample_exchange.id, sample_user.id, "Ready")
        await service.confirm_exchange(sample_exchange.id, sample_user2.id, "Ready")
        await service.complete_exchange(sample_exchange.id, sample_user.id, rating=5)
        
        # Try to cancel
        success = await service.cancel_exchange(
            exchange_id=sample_exchange.id,
            user_id=sample_user.id,
            reason="Changed mind"
        )
        
        assert success is False

    @pytest.mark.asyncio
    async def test_mark_no_show(self, test_db, sample_exchange, sample_user, sample_user2):
        """Test marking a no-show for an exchange."""
        service = ExchangeService(test_db)
        
        # First confirm the exchange
        await service.confirm_exchange(sample_exchange.id, sample_user.id, "Ready")
        await service.confirm_exchange(sample_exchange.id, sample_user2.id, "Ready")
        
        # Mark no-show
        success = await service.mark_no_show(
            exchange_id=sample_exchange.id,
            user_id=sample_user.id,  # Sharer reporting
            no_show_user_id=sample_user2.id,  # Recipient didn't show
            notes="Waited 30 minutes, recipient never showed"
        )
        
        assert success is True
        
        # Exchange should be cancelled due to no-show
        await test_db.refresh(sample_exchange)
        assert sample_exchange.status == ExchangeStatus.CANCELLED
        assert "no-show" in sample_exchange.cancellation_reason.lower()

    @pytest.mark.asyncio
    async def test_mark_no_show_unauthorized(self, test_db, sample_exchange, sample_building):
        """Test that unauthorized users cannot mark no-show."""
        service = ExchangeService(test_db)
        
        # Create third user not involved in exchange
        from src.services.user_service import UserService
        user_service = UserService(test_db)
        user3 = await user_service.create_user(
            telegram_id=555666777,
            email="user3@example.com",
            display_name="User 3",
            phone_number="+1555666777",
            apartment_number="103",
            building_id=sample_building.id
        )
        
        # Third user tries to mark no-show
        success = await service.mark_no_show(
            exchange_id=sample_exchange.id,
            user_id=user3.id,
            no_show_user_id=sample_user.id,
            notes="Unauthorized no-show report"
        )
        
        assert success is False

    @pytest.mark.asyncio
    async def test_get_exchange_history(self, test_db, sample_exchange, sample_user, sample_user2):
        """Test getting exchange history for a user."""
        service = ExchangeService(test_db)
        
        # Complete the exchange first
        await service.confirm_exchange(sample_exchange.id, sample_user.id, "Ready")
        await service.confirm_exchange(sample_exchange.id, sample_user2.id, "Ready")
        await service.complete_exchange(sample_exchange.id, sample_user.id, rating=5)
        
        # Get history
        history = await service.get_exchange_history(
            user_id=sample_user.id,
            limit=10
        )
        
        assert len(history) >= 1
        exchange_ids = [e.id for e in history]
        assert sample_exchange.id in exchange_ids
        
        # Should only include completed/cancelled exchanges
        for exchange in history:
            assert exchange.status in [ExchangeStatus.COMPLETED, ExchangeStatus.CANCELLED]

    @pytest.mark.asyncio
    async def test_get_overdue_exchanges(self, test_db, sample_user, sample_user2, sample_building, sample_food_post):
        """Test getting overdue exchanges."""
        service = ExchangeService(test_db)
        
        # Create overdue exchange
        overdue_exchange = Exchange(
            food_id=sample_food_post.id,
            sharer_id=sample_user.id,
            recipient_id=sample_user2.id,
            status=ExchangeStatus.CONFIRMED,
            credit_amount=10,
            pickup_location="Test location",
            scheduled_pickup_at=datetime.utcnow() - timedelta(hours=2)  # 2 hours overdue
        )
        test_db.add(overdue_exchange)
        await test_db.commit()
        
        # Get overdue exchanges
        overdue = await service.get_overdue_exchanges()
        
        assert len(overdue) >= 1
        overdue_ids = [e.id for e in overdue]
        assert overdue_exchange.id in overdue_ids