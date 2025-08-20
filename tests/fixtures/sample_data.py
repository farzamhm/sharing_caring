"""Sample data generation for testing."""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import random

from src.models.food import FoodCategory, ServingSize
from src.models.exchange import ExchangeStatus


class SampleDataGenerator:
    """Generate sample data for testing."""

    FOOD_TITLES = [
        "Homemade Pasta", "Fresh Salad", "Chocolate Cake", "Vegetable Soup",
        "Grilled Chicken", "Rice Bowl", "Apple Pie", "Sandwich Platter",
        "Fruit Smoothie", "Baked Bread", "Pizza Slices", "Curry Dish"
    ]
    
    FOOD_DESCRIPTIONS = [
        "Delicious homemade meal", "Fresh and healthy",
        "Made with love", "Perfect for sharing",
        "Great for lunch or dinner", "Nutritious and tasty"
    ]
    
    INGREDIENTS = [
        "Tomatoes, basil, garlic", "Mixed vegetables", "Flour, eggs, sugar",
        "Rice, vegetables, spices", "Chicken, herbs, olive oil", "Fresh fruits"
    ]
    
    ALLERGENS = ["None", "Gluten", "Dairy", "Nuts", "Eggs", "Gluten, Dairy"]
    
    DIETARY_INFO = ["Vegetarian", "Vegan", "Gluten-free", "High protein", "Low carb", ""]
    
    LOCATIONS = [
        "Building lobby", "Apartment door", "Kitchen window",
        "Balcony", "Mail room", "Parking garage"
    ]
    
    PICKUP_INSTRUCTIONS = [
        "Ring the doorbell", "Text when you arrive", "I'll meet you downstairs",
        "Leave by the door", "Call when you're here", "Knock on the door"
    ]

    @classmethod
    def generate_food_data(cls, **overrides) -> Dict[str, Any]:
        """Generate sample food post data."""
        now = datetime.utcnow()
        
        data = {
            "title": random.choice(cls.FOOD_TITLES),
            "description": random.choice(cls.FOOD_DESCRIPTIONS),
            "category": random.choice(list(FoodCategory)),
            "serving_size": random.choice(list(ServingSize)),
            "ingredients": random.choice(cls.INGREDIENTS),
            "allergens": random.choice(cls.ALLERGENS),
            "dietary_info": random.choice(cls.DIETARY_INFO),
            "pickup_start": now + timedelta(hours=random.randint(1, 4)),
            "pickup_end": now + timedelta(hours=random.randint(5, 12)),
            "pickup_location": random.choice(cls.LOCATIONS),
            "pickup_instructions": random.choice(cls.PICKUP_INSTRUCTIONS),
            "credit_value": random.randint(5, 25)
        }
        
        # Apply overrides
        data.update(overrides)
        
        # Ensure pickup_end is after pickup_start
        if data["pickup_end"] <= data["pickup_start"]:
            data["pickup_end"] = data["pickup_start"] + timedelta(hours=4)
        
        return data

    @classmethod
    def generate_user_data(cls, telegram_id: int, **overrides) -> Dict[str, Any]:
        """Generate sample user data."""
        data = {
            "telegram_id": telegram_id,
            "email": f"user{telegram_id}@example.com",
            "display_name": f"Test User {telegram_id}",
            "phone_number": f"+1{telegram_id}",
            "apartment_number": str(random.randint(100, 999))
        }
        
        data.update(overrides)
        return data

    @classmethod
    def generate_building_data(cls, **overrides) -> Dict[str, Any]:
        """Generate sample building data."""
        data = {
            "name": f"Test Building {random.randint(1, 100)}",
            "address": f"{random.randint(100, 999)} Test Street",
            "postal_code": f"{random.randint(10000, 99999)}",
            "country": "TestCountry",
            "timezone": "UTC"
        }
        
        data.update(overrides)
        return data

    @classmethod
    def generate_exchange_notes(cls) -> List[str]:
        """Generate sample exchange notes."""
        return [
            "Looking forward to this!",
            "Thanks for sharing!",
            "I'll be there on time",
            "Great! See you soon",
            "Perfect timing",
            "This looks delicious"
        ]

    @classmethod
    def generate_cancellation_reasons(cls) -> List[str]:
        """Generate sample cancellation reasons."""
        return [
            "Emergency came up",
            "Changed my mind",
            "No longer available",
            "Schedule conflict",
            "Found another option",
            "Family emergency"
        ]

    @classmethod
    def create_test_scenario_data(cls, scenario: str) -> Dict[str, Any]:
        """Create data for specific test scenarios."""
        scenarios = {
            "quick_pickup": {
                "pickup_start": datetime.utcnow() + timedelta(minutes=30),
                "pickup_end": datetime.utcnow() + timedelta(hours=2),
                "title": "Quick Pickup Food",
                "credit_value": 8
            },
            "expensive_item": {
                "title": "Gourmet Meal",
                "description": "High-quality gourmet meal",
                "credit_value": 30,
                "category": FoodCategory.MAIN_COURSE,
                "serving_size": ServingSize.SERVES_4_6
            },
            "dietary_restricted": {
                "title": "Vegan Gluten-Free Meal",
                "dietary_info": "Vegan, Gluten-free",
                "allergens": "None",
                "ingredients": "Quinoa, vegetables, herbs"
            },
            "large_serving": {
                "title": "Family Feast",
                "serving_size": ServingSize.SERVES_6_PLUS,
                "credit_value": 25,
                "description": "Enough food for the whole family"
            }
        }
        
        base_data = cls.generate_food_data()
        scenario_data = scenarios.get(scenario, {})
        base_data.update(scenario_data)
        
        return base_data


def create_mock_telegram_message(text: str, user_id: int = 123456789) -> Dict[str, Any]:
    """Create a mock Telegram message for testing."""
    return {
        "message_id": random.randint(1000, 9999),
        "from": {
            "id": user_id,
            "is_bot": False,
            "first_name": "Test",
            "last_name": "User",
            "username": f"testuser{user_id}"
        },
        "chat": {
            "id": user_id,
            "first_name": "Test",
            "last_name": "User",
            "username": f"testuser{user_id}",
            "type": "private"
        },
        "date": int(datetime.utcnow().timestamp()),
        "text": text
    }


def create_test_photo_data() -> bytes:
    """Create mock photo data for testing."""
    # Simple 1x1 pixel PNG
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'