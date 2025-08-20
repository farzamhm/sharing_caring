"""Integration tests for API endpoints."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.api.main import app
from src.core.database import get_db_session


class TestAPIEndpoints:
    """Integration tests for API endpoints."""

    @pytest.fixture
    def client(self, test_db):
        """Create test client with database override."""
        def get_test_db():
            yield test_db
        
        app.dependency_overrides[get_db_session] = get_test_db
        
        with TestClient(app) as client:
            yield client
        
        app.dependency_overrides.clear()

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Neighborhood Sharing Platform API"
        assert data["version"] == "0.1.0"

    def test_create_food_post(self, client, sample_user):
        """Test creating a food post via API."""
        food_data = {
            "title": "API Test Food",
            "description": "Testing food creation via API",
            "category": "main_course",
            "serving_size": "serves_2_4",
            "ingredients": "Test ingredients",
            "pickup_start": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            "pickup_end": (datetime.utcnow() + timedelta(hours=8)).isoformat(),
            "pickup_location": "Test location",
            "credit_value": 12
        }
        
        response = client.post("/foods/", json=food_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "API Test Food"
        assert data["credit_value"] == 12
        assert data["status"] == "available"
        assert data["sharer_id"] == sample_user.id

    def test_browse_foods(self, client, sample_food_post):
        """Test browsing foods via API."""
        response = client.get("/foods/browse")
        assert response.status_code == 200
        
        data = response.json()
        assert "foods" in data
        assert "total_count" in data
        assert "page" in data
        
        # Should have at least our sample food
        assert data["total_count"] >= 1

    def test_browse_foods_with_filters(self, client):
        """Test browsing foods with category filter."""
        response = client.get("/foods/browse?category=main_course&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page_size"] == 5

    def test_get_food_by_id(self, client, sample_food_post):
        """Test getting specific food post."""
        response = client.get(f"/foods/{sample_food_post.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == sample_food_post.id
        assert data["title"] == sample_food_post.title

    def test_get_nonexistent_food(self, client):
        """Test getting non-existent food returns 404."""
        response = client.get("/foods/nonexistent-id")
        assert response.status_code == 404

    def test_claim_food(self, client, sample_food_post, sample_user2):
        """Test claiming a food post."""
        claim_data = {
            "notes": "Looking forward to this!"
        }
        
        response = client.post(f"/foods/{sample_food_post.id}/claim", json=claim_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "exchange_id" in data
        assert "pickup_details" in data

    def test_list_exchanges(self, client, sample_exchange):
        """Test listing exchanges."""
        response = client.get("/exchanges/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Should have at least our sample exchange
        assert len(data) >= 1

    def test_get_exchange_details(self, client, sample_exchange):
        """Test getting exchange details."""
        response = client.get(f"/exchanges/{sample_exchange.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == sample_exchange.id
        assert data["status"] == "pending"

    def test_confirm_exchange(self, client, sample_exchange, sample_user):
        """Test confirming an exchange."""
        confirm_data = {
            "notes": "Ready for pickup!"
        }
        
        response = client.post(f"/exchanges/{sample_exchange.id}/confirm", json=confirm_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True

    def test_get_credit_balance(self, client, sample_credit_account):
        """Test getting credit balance."""
        response = client.get("/credits/balance")
        assert response.status_code == 200
        
        data = response.json()
        assert "balance" in data
        assert "lifetime_earned" in data
        assert "lifetime_spent" in data

    def test_get_credit_transactions(self, client, credit_transaction):
        """Test getting credit transactions."""
        response = client.get("/credits/transactions")
        assert response.status_code == 200
        
        data = response.json()
        assert "transactions" in data
        assert "total_count" in data
        assert len(data["transactions"]) >= 1

    def test_get_credit_leaderboard(self, client, sample_credit_account):
        """Test getting credit leaderboard."""
        response = client.get("/credits/leaderboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "leaderboard" in data
        assert "building_id" in data

    def test_admin_dashboard_html(self, client):
        """Test admin dashboard HTML endpoint."""
        response = client.get("/admin/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_admin_platform_stats(self, client):
        """Test admin platform stats."""
        response = client.get("/admin/stats/platform")
        assert response.status_code == 200
        
        data = response.json()
        assert "users" in data
        assert "food_posts" in data
        assert "exchanges" in data
        assert "credits" in data

    def test_admin_system_health(self, client):
        """Test admin system health check."""
        response = client.get("/admin/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "score" in data
        assert "database_connected" in data

    def test_admin_dashboard_summary(self, client):
        """Test admin dashboard summary."""
        response = client.get("/admin/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "overview" in data
        assert "health" in data
        assert "alerts" in data

    def test_file_upload_validation(self, client):
        """Test file upload validation."""
        # Test with non-image file
        response = client.post(
            "/foods/upload-photo?user_id=test-user&food_id=test-food",
            files={"file": ("test.txt", "not an image", "text/plain")}
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "must be an image" in data["detail"].lower()

    def test_pagination_parameters(self, client):
        """Test API endpoints handle pagination correctly."""
        # Test with limit and offset
        response = client.get("/foods/browse?limit=5&offset=0")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page_size"] == 5
        assert data["page"] == 1

    def test_invalid_json_handling(self, client):
        """Test API handles invalid JSON gracefully."""
        response = client.post(
            "/foods/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Unprocessable Entity

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/foods/")
        # CORS headers should be present due to middleware
        assert "access-control-allow-origin" in response.headers

    @pytest.mark.asyncio
    async def test_async_client_operations(self, test_db, sample_user, sample_building):
        """Test async operations using httpx AsyncClient."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Override dependency
            app.dependency_overrides[get_db_session] = lambda: test_db
            
            # Test creating food post
            food_data = {
                "title": "Async Test Food",
                "description": "Testing async operations",
                "category": "appetizer",
                "serving_size": "serves_1_2",
                "ingredients": "Async ingredients",
                "pickup_start": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                "pickup_end": (datetime.utcnow() + timedelta(hours=5)).isoformat(),
                "pickup_location": "Async location",
                "credit_value": 8
            }
            
            response = await ac.post("/foods/", json=food_data)
            assert response.status_code == 200
            
            # Test browsing
            response = await ac.get("/foods/browse")
            assert response.status_code == 200
            
            app.dependency_overrides.clear()

    def test_error_handling_in_endpoints(self, client):
        """Test error handling in API endpoints."""
        # Test with invalid food ID format
        response = client.get("/foods/invalid-uuid-format")
        # Should handle gracefully and return appropriate error

        # Test with invalid exchange action
        response = client.post(
            "/admin/exchanges/test-id/intervene?action=invalid&reason=test",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Validation error