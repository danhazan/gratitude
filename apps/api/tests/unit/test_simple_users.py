"""
Simple user tests using synchronous TestClient
These tests avoid database operations and focus on API structure.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)

class TestSimpleUserEndpoints:
    """Test user endpoints using synchronous client."""
    
    def test_user_endpoints_exist(self):
        """Test that user endpoints are accessible."""
        # Test that the endpoint exists (may require auth)
        response = client.get("/api/v1/users/me")
        # Could be 403 (auth required) or 401 (unauthorized)
        assert response.status_code in [401, 403]
    
    def test_user_profile_endpoint_structure(self):
        """Test user profile endpoint structure."""
        # Test with invalid user ID format
        response = client.get("/api/v1/users/invalid-id")
        # Could be 403 (auth required), 404 (not found), or 422 (validation error)
        assert response.status_code in [403, 404, 422]
    
    def test_user_update_validation(self):
        """Test user update validation."""
        # Test with invalid data (may require auth)
        response = client.put("/api/v1/users/me", json={
            "email": "invalid-email"
        })
        # Could be 401 (unauthorized), 403 (forbidden), or 422 (validation error)
        assert response.status_code in [401, 403, 422]
    
    def test_user_endpoints_require_auth(self):
        """Test that protected user endpoints require authentication."""
        # Test endpoints that should require authentication
        protected_endpoints = [
            "/api/v1/users/me"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            # Should return 401 (unauthorized) or 403 (forbidden)
            assert response.status_code in [401, 403], f"Endpoint {endpoint} should require auth"
    
    def test_user_validation_rules(self):
        """Test user validation rules."""
        # Test username pattern validation
        response = client.post("/api/v1/users/", json={
            "email": "test@example.com",
            "username": "invalid-username!",  # Invalid characters
            "full_name": "Test User"
        })
        assert response.status_code == 422
        
        # Test username length validation
        response = client.post("/api/v1/users/", json={
            "email": "test@example.com",
            "username": "a",  # Too short
            "full_name": "Test User"
        })
        assert response.status_code == 422
        
        # Test email validation
        response = client.post("/api/v1/users/", json={
            "email": "invalid-email",
            "username": "testuser",
            "full_name": "Test User"
        })
        assert response.status_code == 422
    
    def test_user_create_validation(self):
        """Test user creation validation without database."""
        # Test with missing required fields
        response = client.post("/api/v1/users/", json={})
        assert response.status_code == 422
        
        # Test with invalid email format
        response = client.post("/api/v1/users/", json={
            "email": "invalid-email",
            "username": "testuser",
            "full_name": "Test User"
        })
        assert response.status_code == 422
    
    def test_user_endpoint_methods(self):
        """Test that user endpoints support correct HTTP methods."""
        # Test GET method on user endpoints
        response = client.get("/api/v1/users/me")
        assert response.status_code in [401, 403]
        
        # Test PUT method on user endpoints
        response = client.put("/api/v1/users/me", json={})
        assert response.status_code in [401, 403, 422]
        
        # Test POST method on user creation
        response = client.post("/api/v1/users/", json={})
        assert response.status_code == 422
    
    def test_user_schema_structure(self):
        """Test user schema structure validation."""
        # Test with valid data structure but missing required fields
        response = client.post("/api/v1/users/", json={
            "email": "test@example.com",
            # Missing username and full_name
        })
        assert response.status_code == 422 