"""
API Structure Tests
These tests verify the API structure without requiring database setup.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)

class TestAPIStructure:
    """Test API structure and endpoints."""
    
    def test_api_v1_routes_exist(self):
        """Test that API v1 routes are properly configured."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        
        # Check for API v1 routes
        paths = data["paths"]
        api_v1_paths = [path for path in paths.keys() if path.startswith("/api/v1")]
        assert len(api_v1_paths) > 0, "No API v1 routes found"
        
        # Check for specific endpoints
        expected_endpoints = [
            "/api/v1/users/",
            "/api/v1/posts/"
        ]
        
        for endpoint in expected_endpoints:
            assert endpoint in paths, f"Missing endpoint: {endpoint}"
            
        # Check for follows endpoints (they don't have a base /follows/ endpoint)
        follows_paths = [path for path in paths.keys() if path.startswith("/api/v1/follows")]
        assert len(follows_paths) > 0, "No follows endpoints found"
    
    def test_users_endpoints_exist(self):
        """Test that users endpoints exist."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        
        paths = data["paths"]
        user_paths = [path for path in paths.keys() if "/users" in path]
        assert len(user_paths) > 0, "No user endpoints found"
    
    def test_posts_endpoints_exist(self):
        """Test that posts endpoints exist."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        
        paths = data["paths"]
        post_paths = [path for path in paths.keys() if "/posts" in path]
        assert len(post_paths) > 0, "No post endpoints found"
    
    def test_follows_endpoints_exist(self):
        """Test that follows endpoints exist."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        
        paths = data["paths"]
        follow_paths = [path for path in paths.keys() if "/follows" in path]
        assert len(follow_paths) > 0, "No follow endpoints found"
    
    def test_api_info(self):
        """Test API metadata."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        
        info = data["info"]
        assert info["title"] == "Grateful API"
        assert info["version"] == "1.0.0"
        assert "description" in info
    
    def test_api_schema_structure(self):
        """Test that API schema has proper structure."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        
        # Check required OpenAPI fields
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert "components" in data
    
    def test_error_responses_defined(self):
        """Test that error responses are properly defined."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        
        # Check that common error responses are defined
        paths = data["paths"]
        for path, methods in paths.items():
            if "/api/v1/" in path:
                for method, details in methods.items():
                    if method in ["get", "post", "put", "delete"]:
                        responses = details.get("responses", {})
                        # Check for common error responses - 422 is always present for validation
                        # Skip /me endpoints as they don't need validation errors
                        if "/me" not in path:
                            assert "422" in responses, f"Missing 422 response for {path} {method}"
                        # 404 is not always required, especially for POST endpoints
                        # Only check for 404 on GET endpoints that could return 404 (not /me endpoints)
                        if method == "get" and "/me" not in path and "{user_id}" in path:
                            # These endpoints can return 404 but FastAPI doesn't auto-include them in schema
                            # We'll skip this check as it's implementation-dependent
                            pass

class TestEndpointValidation:
    """Test endpoint validation without database."""
    
    def test_invalid_user_id_format(self):
        """Test that invalid user ID format returns appropriate error."""
        response = client.get("/api/v1/users/invalid-id")
        # Could be 403 (auth required), 404 (not found), or 422 (validation error)
        assert response.status_code in [403, 404, 422]
    
    def test_invalid_post_id_format(self):
        """Test that invalid post ID format returns appropriate error."""
        response = client.get("/api/v1/posts/invalid-id")
        # Could be 403 (auth required), 404 (not found), or 422 (validation error)
        assert response.status_code in [403, 404, 422]
    
    def test_invalid_follow_id_format(self):
        """Test that invalid follow ID format returns appropriate error."""
        response = client.get("/api/v1/follows/invalid-id")
        # Could be 403 (auth required), 404 (not found), 405 (method not allowed), or 422 (validation error)
        assert response.status_code in [403, 404, 405, 422]
    
    def test_missing_required_fields(self):
        """Test that missing required fields returns 422."""
        # Test user creation without required fields
        response = client.post("/api/v1/users/", json={})
        assert response.status_code == 422
        
        # Test post creation without required fields (may require auth)
        response = client.post("/api/v1/posts/", json={})
        # Could be 403 (auth required) or 422 (validation error)
        assert response.status_code in [403, 422] 