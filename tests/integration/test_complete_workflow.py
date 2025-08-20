"""Integration tests for complete user workflows."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock

from src.services.user_service import UserService
from src.services.food_service import FoodService
from src.services.exchange_service import ExchangeService
from src.services.credit_service import CreditService
from src.services.notification_service import NotificationService
from src.models.food import FoodCategory, ServingSize, FoodStatus
from src.models.exchange import ExchangeStatus


class TestCompleteWorkflows:
    """Test complete user workflows end-to-end."""

    @pytest.mark.asyncio
    async def test_complete_food_sharing_workflow(self, test_db, sample_building):
        """Test complete workflow from user registration to exchange completion."""
        # Initialize services
        user_service = UserService(test_db)
        food_service = FoodService(test_db)
        exchange_service = ExchangeService(test_db)
        credit_service = CreditService(test_db)
        
        # Step 1: Create two users (sharer and recipient)
        sharer = await user_service.create_user(
            telegram_id=111222333,
            email="sharer@example.com",
            display_name="Food Sharer",
            phone_number="+1111222333",
            apartment_number="201",
            building_id=sample_building.id
        )
        
        recipient = await user_service.create_user(
            telegram_id=444555666,
            email="recipient@example.com",
            display_name="Food Recipient",
            phone_number="+1444555666",
            apartment_number="202",
            building_id=sample_building.id
        )
        
        # Step 2: Verify both users
        await user_service.verify_user(sharer.telegram_id, sharer.verification_code)
        await user_service.verify_user(recipient.telegram_id, recipient.verification_code)
        
        # Step 3: Initialize credit accounts
        sharer_credits = await credit_service.initialize_user_credits(sharer.id)
        recipient_credits = await credit_service.initialize_user_credits(recipient.id)
        
        assert sharer_credits.balance == 50  # Initial credits
        assert recipient_credits.balance == 50
        
        # Step 4: Sharer creates a food post
        food = await food_service.create_food_post(
            user_id=sharer.id,
            title="Homemade Lasagna",
            description="Fresh lasagna with ricotta and spinach",
            category=FoodCategory.MAIN_COURSE,
            serving_size=ServingSize.SERVES_4_6,
            ingredients="Pasta, ricotta, spinach, tomato sauce",
            allergens="Gluten, Dairy",
            dietary_info="Vegetarian",
            pickup_start=datetime.utcnow() + timedelta(hours=2),
            pickup_end=datetime.utcnow() + timedelta(hours=8),
            pickup_location="Building lobby",
            pickup_instructions="I'll meet you in the lobby",
            credit_value=15
        )
        
        assert food is not None
        assert food.status == FoodStatus.AVAILABLE
        assert food.credit_value == 15
        
        # Step 5: Recipient browses and finds the food
        available_foods = await food_service.browse_available_food(
            user_id=recipient.id,
            limit=10
        )
        
        assert len(available_foods) >= 1
        food_ids = [f.id for f in available_foods]
        assert food.id in food_ids
        
        # Step 6: Recipient claims the food
        exchange = await food_service.claim_food(
            food_id=food.id,
            user_id=recipient.id,
            notes="This looks delicious! I'll be there at 6 PM."
        )
        
        assert exchange is not None
        assert exchange.status == ExchangeStatus.PENDING
        assert exchange.recipient_notes == "This looks delicious! I'll be there at 6 PM."
        
        # Verify food is now claimed
        await test_db.refresh(food)
        assert food.status == FoodStatus.CLAIMED
        assert food.claimed_by_id == recipient.id
        
        # Step 7: Both parties confirm the exchange
        # Sharer confirms
        sharer_confirm = await exchange_service.confirm_exchange(
            exchange_id=exchange.id,
            user_id=sharer.id,
            notes="Perfect! See you at 6 PM in the lobby."
        )
        assert sharer_confirm is True
        
        # Recipient confirms
        recipient_confirm = await exchange_service.confirm_exchange(
            exchange_id=exchange.id,
            user_id=recipient.id,
            notes="Confirmed! Looking forward to it."
        )
        assert recipient_confirm is True
        
        # Exchange should now be confirmed
        await test_db.refresh(exchange)
        assert exchange.status == ExchangeStatus.CONFIRMED
        assert exchange.sharer_confirmed is True
        assert exchange.recipient_confirmed is True
        
        # Step 8: Exchange is completed
        completion = await exchange_service.complete_exchange(
            exchange_id=exchange.id,
            user_id=sharer.id,  # Sharer marks as complete
            rating=5,
            notes="Great interaction! Food was picked up on time."
        )
        assert completion is True
        
        await test_db.refresh(exchange)
        assert exchange.status == ExchangeStatus.COMPLETED
        assert exchange.sharer_rating == 5
        assert exchange.credits_transferred is True
        
        # Step 9: Verify credit transfer
        await test_db.refresh(sharer_credits)
        await test_db.refresh(recipient_credits)
        
        # Sharer should have received credits
        assert sharer_credits.balance == 50 + 15  # Initial + food credits
        assert sharer_credits.lifetime_earned == 50 + 15
        
        # Recipient should have paid credits
        assert recipient_credits.balance == 50 - 15  # Initial - food cost
        assert recipient_credits.lifetime_spent == 15
        
        # Step 10: Verify transaction history
        sharer_transactions = await credit_service.get_user_transactions(sharer.id)
        recipient_transactions = await credit_service.get_user_transactions(recipient.id)
        
        assert len(sharer_transactions) >= 2  # Initial + earned
        assert len(recipient_transactions) >= 2  # Initial + spent

    @pytest.mark.asyncio
    async def test_exchange_cancellation_workflow(self, test_db, sample_building):
        """Test workflow when exchange is cancelled."""
        # Initialize services
        user_service = UserService(test_db)
        food_service = FoodService(test_db)
        exchange_service = ExchangeService(test_db)
        credit_service = CreditService(test_db)
        
        # Create users
        sharer = await user_service.create_user(
            telegram_id=777888999,
            email="sharer2@example.com",
            display_name="Sharer 2",
            phone_number="+1777888999",
            apartment_number="301",
            building_id=sample_building.id
        )
        
        recipient = await user_service.create_user(
            telegram_id=999888777,
            email="recipient2@example.com",
            display_name="Recipient 2",
            phone_number="+1999888777",
            apartment_number="302",
            building_id=sample_building.id
        )
        
        # Verify users and initialize credits
        await user_service.verify_user(sharer.telegram_id, sharer.verification_code)
        await user_service.verify_user(recipient.telegram_id, recipient.verification_code)
        await credit_service.initialize_user_credits(sharer.id)
        await credit_service.initialize_user_credits(recipient.id)
        
        # Create and claim food
        food = await food_service.create_food_post(
            user_id=sharer.id,
            title="Soup to Share",
            description="Homemade vegetable soup",
            category=FoodCategory.APPETIZER,
            serving_size=ServingSize.SERVES_2_4,
            ingredients="Vegetables, broth",
            pickup_start=datetime.utcnow() + timedelta(hours=1),
            pickup_end=datetime.utcnow() + timedelta(hours=6),
            pickup_location="Apartment 301",
            credit_value=8
        )
        
        exchange = await food_service.claim_food(
            food_id=food.id,
            user_id=recipient.id,
            notes="I'd love some soup!"
        )
        
        # Cancel the exchange
        cancellation = await exchange_service.cancel_exchange(
            exchange_id=exchange.id,
            user_id=recipient.id,  # Recipient cancels
            reason="Something came up, sorry!"
        )
        assert cancellation is True
        
        # Verify exchange is cancelled
        await test_db.refresh(exchange)
        assert exchange.status == ExchangeStatus.CANCELLED
        assert exchange.cancelled_by_id == recipient.id
        assert exchange.cancellation_reason == "Something came up, sorry!"
        
        # Food should be available again
        await test_db.refresh(food)
        assert food.status == FoodStatus.AVAILABLE
        assert food.claimed_by_id is None

    @pytest.mark.asyncio
    async def test_multiple_claims_workflow(self, test_db, sample_building):
        """Test workflow with multiple users trying to claim same food."""
        # Initialize services
        user_service = UserService(test_db)
        food_service = FoodService(test_db)
        
        # Create one sharer and two recipients
        sharer = await user_service.create_user(
            telegram_id=123456789,
            email="sharer3@example.com",
            display_name="Popular Sharer",
            phone_number="+1123456789",
            apartment_number="401",
            building_id=sample_building.id
        )
        
        recipient1 = await user_service.create_user(
            telegram_id=234567890,
            email="recipient3@example.com",
            display_name="Quick Recipient",
            phone_number="+1234567890",
            apartment_number="402",
            building_id=sample_building.id
        )
        
        recipient2 = await user_service.create_user(
            telegram_id=345678901,
            email="recipient4@example.com",
            display_name="Slow Recipient",
            phone_number="+1345678901",
            apartment_number="403",
            building_id=sample_building.id
        )
        
        # Verify all users
        await user_service.verify_user(sharer.telegram_id, sharer.verification_code)
        await user_service.verify_user(recipient1.telegram_id, recipient1.verification_code)
        await user_service.verify_user(recipient2.telegram_id, recipient2.verification_code)
        
        # Create popular food item
        food = await food_service.create_food_post(
            user_id=sharer.id,
            title="Amazing Cookies",
            description="Fresh baked chocolate chip cookies",
            category=FoodCategory.DESSERT,
            serving_size=ServingSize.SERVES_4_6,
            ingredients="Flour, chocolate chips, butter, sugar",
            allergens="Gluten, Dairy",
            pickup_start=datetime.utcnow() + timedelta(hours=3),
            pickup_end=datetime.utcnow() + timedelta(hours=9),
            pickup_location="Kitchen window",
            credit_value=12
        )
        
        # First recipient claims successfully
        exchange1 = await food_service.claim_food(
            food_id=food.id,
            user_id=recipient1.id,
            notes="I love cookies!"
        )
        assert exchange1 is not None
        
        # Second recipient tries to claim same food (should fail)
        exchange2 = await food_service.claim_food(
            food_id=food.id,
            user_id=recipient2.id,
            notes="I want cookies too!"
        )
        assert exchange2 is None
        
        # Verify food is claimed by first recipient only
        await test_db.refresh(food)
        assert food.status == FoodStatus.CLAIMED
        assert food.claimed_by_id == recipient1.id

    @pytest.mark.asyncio
    async def test_expired_food_cleanup_workflow(self, test_db, sample_building):
        """Test workflow for expired food cleanup."""
        user_service = UserService(test_db)
        food_service = FoodService(test_db)
        
        # Create user
        user = await user_service.create_user(
            telegram_id=555777999,
            email="expiry_user@example.com",
            display_name="Expiry User",
            phone_number="+1555777999",
            apartment_number="501",
            building_id=sample_building.id
        )
        await user_service.verify_user(user.telegram_id, user.verification_code)
        
        # Create food that will expire soon
        food = await food_service.create_food_post(
            user_id=user.id,
            title="Soon to Expire",
            description="This will expire soon",
            category=FoodCategory.APPETIZER,
            serving_size=ServingSize.SERVES_1_2,
            ingredients="Time-sensitive ingredients",
            pickup_start=datetime.utcnow() - timedelta(hours=2),  # Already started
            pickup_end=datetime.utcnow() - timedelta(hours=1),   # Already ended
            pickup_location="User's door",
            credit_value=5
        )
        
        # Manually set expiry to past
        food.expires_at = datetime.utcnow() - timedelta(minutes=1)
        test_db.add(food)
        await test_db.commit()
        
        # Run cleanup
        expired_count = await food_service.expire_old_posts()
        assert expired_count >= 1
        
        # Verify food is expired
        await test_db.refresh(food)
        assert food.status == FoodStatus.EXPIRED

    @pytest.mark.asyncio
    @patch('src.services.notification_service.NotificationService.send_message')
    async def test_notification_workflow(self, mock_send_message, test_db, sample_building):
        """Test notification workflow throughout exchange."""
        mock_send_message.return_value = True
        
        # Initialize services
        user_service = UserService(test_db)
        food_service = FoodService(test_db)
        notification_service = NotificationService(test_db, bot=AsyncMock())
        
        # Create users
        sharer = await user_service.create_user(
            telegram_id=666777888,
            email="notif_sharer@example.com",
            display_name="Notification Sharer",
            phone_number="+1666777888",
            apartment_number="601",
            building_id=sample_building.id
        )
        
        recipient = await user_service.create_user(
            telegram_id=888777666,
            email="notif_recipient@example.com",
            display_name="Notification Recipient",
            phone_number="+1888777666",
            apartment_number="602",
            building_id=sample_building.id
        )
        
        await user_service.verify_user(sharer.telegram_id, sharer.verification_code)
        await user_service.verify_user(recipient.telegram_id, recipient.verification_code)
        
        # Create food post and send confirmation
        food = await food_service.create_food_post(
            user_id=sharer.id,
            title="Notification Test Food",
            description="Testing notifications",
            category=FoodCategory.MAIN_COURSE,
            serving_size=ServingSize.SERVES_2_4,
            ingredients="Test ingredients",
            pickup_start=datetime.utcnow() + timedelta(hours=2),
            pickup_end=datetime.utcnow() + timedelta(hours=8),
            pickup_location="Test location",
            credit_value=10
        )
        
        # Send food posted confirmation
        confirmation_sent = await notification_service.send_food_posted_confirmation(
            user_id=sharer.id,
            food_id=food.id
        )
        assert confirmation_sent is True
        
        # Claim food and send request notification
        exchange = await food_service.claim_food(
            food_id=food.id,
            user_id=recipient.id,
            notes="Notification test claim"
        )
        
        request_sent = await notification_service.send_food_request_notification(
            sharer_id=sharer.id,
            recipient_id=recipient.id,
            food_id=food.id,
            exchange_id=exchange.id
        )
        assert request_sent is True
        
        # Verify notifications were called
        assert mock_send_message.call_count >= 2