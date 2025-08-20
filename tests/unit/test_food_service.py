"""Unit tests for FoodService."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.services.food_service import FoodService
from src.models.food import Food, FoodStatus, FoodCategory, ServingSize


class TestFoodService:
    """Test cases for FoodService."""

    @pytest.mark.asyncio
    async def test_create_food_post(self, test_db, sample_user, sample_building):
        """Test creating a food post."""
        service = FoodService(test_db)
        
        food = await service.create_food_post(
            user_id=sample_user.id,
            title="Test Pizza",
            description="Homemade pizza with fresh ingredients",
            category=FoodCategory.MAIN_COURSE,
            serving_size=ServingSize.SERVES_2_4,
            ingredients="Dough, tomatoes, cheese, basil",
            allergens="Gluten, Dairy",
            dietary_info="Vegetarian",
            pickup_start=datetime.utcnow() + timedelta(hours=2),
            pickup_end=datetime.utcnow() + timedelta(hours=8),
            pickup_location="Building lobby",
            pickup_instructions="Call when you arrive",
            credit_value=15
        )
        
        assert food is not None
        assert food.title == "Test Pizza"
        assert food.sharer_id == sample_user.id
        assert food.building_id == sample_building.id
        assert food.status == FoodStatus.AVAILABLE
        assert food.credit_value == 15
        assert food.expires_at > datetime.utcnow()

    @pytest.mark.asyncio
    async def test_get_food_by_id(self, test_db, sample_food_post):
        """Test getting food by ID."""
        service = FoodService(test_db)
        
        # Existing food
        food = await service.get_food_by_id(sample_food_post.id)
        assert food is not None
        assert food.id == sample_food_post.id
        
        # Non-existing food
        food = await service.get_food_by_id("non-existent-id")
        assert food is None

    @pytest.mark.asyncio
    async def test_browse_available_food(self, test_db, sample_user, sample_user2, sample_building):
        """Test browsing available food with filters."""
        service = FoodService(test_db)
        
        # Create multiple food posts
        food1 = await service.create_food_post(
            user_id=sample_user.id,
            title="Vegetarian Pasta",
            description="Fresh pasta",
            category=FoodCategory.MAIN_COURSE,
            serving_size=ServingSize.SERVES_2_4,
            dietary_info="Vegetarian",
            allergens="Gluten",
            pickup_start=datetime.utcnow() + timedelta(hours=1),
            pickup_end=datetime.utcnow() + timedelta(hours=6),
            pickup_location="Apt 101",
            credit_value=10
        )
        
        food2 = await service.create_food_post(
            user_id=sample_user2.id,
            title="Vegan Salad",
            description="Fresh salad",
            category=FoodCategory.APPETIZER,
            serving_size=ServingSize.SERVES_1_2,
            dietary_info="Vegan",
            pickup_start=datetime.utcnow() + timedelta(hours=1),
            pickup_end=datetime.utcnow() + timedelta(hours=6),
            pickup_location="Apt 102",
            credit_value=5
        )
        
        # Browse all available (should exclude user's own posts)
        foods = await service.browse_available_food(
            user_id=sample_user.id,
            limit=10
        )
        
        assert len(foods) >= 1
        food_ids = [f.id for f in foods]
        assert food1.id not in food_ids  # User's own post excluded
        assert food2.id in food_ids  # Other user's post included

    @pytest.mark.asyncio
    async def test_browse_with_category_filter(self, test_db, sample_user, sample_user2):
        """Test browsing with category filter."""
        service = FoodService(test_db)
        
        # Create food posts with different categories
        main_course = await service.create_food_post(
            user_id=sample_user2.id,
            title="Main Course",
            description="Main dish",
            category=FoodCategory.MAIN_COURSE,
            serving_size=ServingSize.SERVES_2_4,
            pickup_start=datetime.utcnow() + timedelta(hours=1),
            pickup_end=datetime.utcnow() + timedelta(hours=6),
            pickup_location="Apt 102",
            credit_value=10
        )
        
        dessert = await service.create_food_post(
            user_id=sample_user2.id,
            title="Dessert",
            description="Sweet treat",
            category=FoodCategory.DESSERT,
            serving_size=ServingSize.SERVES_1_2,
            pickup_start=datetime.utcnow() + timedelta(hours=1),
            pickup_end=datetime.utcnow() + timedelta(hours=6),
            pickup_location="Apt 102",
            credit_value=5
        )
        
        # Filter by main course
        foods = await service.browse_available_food(
            user_id=sample_user.id,
            category=FoodCategory.MAIN_COURSE
        )
        
        assert len(foods) >= 1
        assert all(f.category == FoodCategory.MAIN_COURSE for f in foods)

    @pytest.mark.asyncio
    async def test_browse_exclude_allergens(self, test_db, sample_user, sample_user2):
        """Test browsing with allergen exclusion."""
        service = FoodService(test_db)
        
        # Create food with gluten
        gluten_food = await service.create_food_post(
            user_id=sample_user2.id,
            title="Wheat Pasta",
            description="Contains gluten",
            category=FoodCategory.MAIN_COURSE,
            serving_size=ServingSize.SERVES_2_4,
            allergens="Gluten, Eggs",
            pickup_start=datetime.utcnow() + timedelta(hours=1),
            pickup_end=datetime.utcnow() + timedelta(hours=6),
            pickup_location="Apt 102",
            credit_value=10
        )
        
        # Create food without gluten
        no_gluten_food = await service.create_food_post(
            user_id=sample_user2.id,
            title="Rice Bowl",
            description="Gluten-free",
            category=FoodCategory.MAIN_COURSE,
            serving_size=ServingSize.SERVES_1_2,
            allergens="None",
            pickup_start=datetime.utcnow() + timedelta(hours=1),
            pickup_end=datetime.utcnow() + timedelta(hours=6),
            pickup_location="Apt 102",
            credit_value=8
        )
        
        # Exclude gluten
        foods = await service.browse_available_food(
            user_id=sample_user.id,
            exclude_allergens=["Gluten"]
        )
        
        # Should only get non-gluten food
        food_ids = [f.id for f in foods]
        assert gluten_food.id not in food_ids
        assert no_gluten_food.id in food_ids

    @pytest.mark.asyncio
    async def test_claim_food(self, test_db, sample_food_post, sample_user2):
        """Test claiming a food post."""
        service = FoodService(test_db)
        
        exchange = await service.claim_food(
            food_id=sample_food_post.id,
            user_id=sample_user2.id,
            notes="Looking forward to trying this!"
        )
        
        assert exchange is not None
        assert exchange.food_id == sample_food_post.id
        assert exchange.recipient_id == sample_user2.id
        assert exchange.sharer_id == sample_food_post.sharer_id
        assert exchange.recipient_notes == "Looking forward to trying this!"
        
        # Food should now be claimed
        await test_db.refresh(sample_food_post)
        assert sample_food_post.status == FoodStatus.CLAIMED
        assert sample_food_post.claimed_by_id == sample_user2.id

    @pytest.mark.asyncio
    async def test_claim_own_food_fails(self, test_db, sample_food_post, sample_user):
        """Test that users cannot claim their own food."""
        service = FoodService(test_db)
        
        exchange = await service.claim_food(
            food_id=sample_food_post.id,
            user_id=sample_user.id,  # Same user who posted
            notes="Trying to claim own food"
        )
        
        assert exchange is None

    @pytest.mark.asyncio
    async def test_claim_already_claimed_food_fails(self, test_db, sample_food_post, sample_user2, sample_building):
        """Test that already claimed food cannot be claimed again."""
        service = FoodService(test_db)
        
        # First claim
        exchange1 = await service.claim_food(
            food_id=sample_food_post.id,
            user_id=sample_user2.id
        )
        assert exchange1 is not None
        
        # Create another user to try second claim
        from src.services.user_service import UserService
        user_service = UserService(test_db)
        user3 = await user_service.create_user(
            telegram_id=333444555,
            email="user3@example.com",
            display_name="User 3",
            phone_number="+1333444555",
            apartment_number="103",
            building_id=sample_building.id
        )
        
        # Second claim should fail
        exchange2 = await service.claim_food(
            food_id=sample_food_post.id,
            user_id=user3.id
        )
        assert exchange2 is None

    @pytest.mark.asyncio
    async def test_unclaim_food(self, test_db, sample_food_post, sample_user2):
        """Test unclaiming a food post."""
        service = FoodService(test_db)
        
        # First claim the food
        exchange = await service.claim_food(
            food_id=sample_food_post.id,
            user_id=sample_user2.id
        )
        assert exchange is not None
        
        # Now unclaim it
        success = await service.unclaim_food(
            food_id=sample_food_post.id,
            user_id=sample_user2.id,
            reason="Changed my mind"
        )
        
        assert success is True
        
        # Food should be available again
        await test_db.refresh(sample_food_post)
        assert sample_food_post.status == FoodStatus.AVAILABLE
        assert sample_food_post.claimed_by_id is None

    @pytest.mark.asyncio
    async def test_update_food_post(self, test_db, sample_food_post, sample_user):
        """Test updating a food post."""
        service = FoodService(test_db)
        
        updated_food = await service.update_food_post(
            food_id=sample_food_post.id,
            user_id=sample_user.id,
            title="Updated Title",
            description="Updated description",
            credit_value=20
        )
        
        assert updated_food is not None
        assert updated_food.title == "Updated Title"
        assert updated_food.description == "Updated description"
        assert updated_food.credit_value == 20

    @pytest.mark.asyncio
    async def test_update_food_post_unauthorized(self, test_db, sample_food_post, sample_user2):
        """Test that only the sharer can update their food post."""
        service = FoodService(test_db)
        
        updated_food = await service.update_food_post(
            food_id=sample_food_post.id,
            user_id=sample_user2.id,  # Different user
            title="Unauthorized Update"
        )
        
        assert updated_food is None

    @pytest.mark.asyncio
    async def test_expire_food_post(self, test_db, sample_food_post, sample_user):
        """Test manually expiring a food post."""
        service = FoodService(test_db)
        
        success = await service.expire_food_post(
            food_id=sample_food_post.id,
            user_id=sample_user.id,
            reason="No longer available"
        )
        
        assert success is True
        
        # Food should be expired
        await test_db.refresh(sample_food_post)
        assert sample_food_post.status == FoodStatus.EXPIRED

    @pytest.mark.asyncio
    async def test_get_user_posts(self, test_db, sample_user, sample_food_post):
        """Test getting user's food posts."""
        service = FoodService(test_db)
        
        # Create another food post
        food2 = await service.create_food_post(
            user_id=sample_user.id,
            title="Second Food",
            description="Another food item",
            category=FoodCategory.APPETIZER,
            serving_size=ServingSize.SERVES_1_2,
            pickup_start=datetime.utcnow() + timedelta(hours=1),
            pickup_end=datetime.utcnow() + timedelta(hours=6),
            pickup_location="Apt 101",
            credit_value=8
        )
        
        # Get user posts
        posts = await service.get_user_posts(
            user_id=sample_user.id,
            include_expired=False
        )
        
        assert len(posts) >= 2
        post_ids = [p.id for p in posts]
        assert sample_food_post.id in post_ids
        assert food2.id in post_ids

    @pytest.mark.asyncio
    async def test_expire_old_posts(self, test_db, sample_user, sample_building):
        """Test expiring old food posts."""
        service = FoodService(test_db)
        
        # Create an expired food post
        expired_food = Food(
            title="Expired Food",
            description="This should be expired",
            category=FoodCategory.MAIN_COURSE,
            serving_size=ServingSize.SERVES_2_4,
            status=FoodStatus.AVAILABLE,
            prepared_at=datetime.utcnow() - timedelta(hours=25),
            pickup_start=datetime.utcnow() - timedelta(hours=2),
            pickup_end=datetime.utcnow() - timedelta(hours=1),
            expires_at=datetime.utcnow() - timedelta(hours=1),  # Already expired
            pickup_location="Apt 101",
            credit_value=5,
            sharer_id=sample_user.id,
            building_id=sample_building.id
        )
        test_db.add(expired_food)
        await test_db.commit()
        
        # Run expiration
        expired_count = await service.expire_old_posts()
        
        assert expired_count >= 1
        
        # Check that the food is now expired
        await test_db.refresh(expired_food)
        assert expired_food.status == FoodStatus.EXPIRED