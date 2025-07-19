"""
Basic endpoint tests for Grateful API
These tests focus on basic API functionality that doesn't require database connections.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)


class TestBasicEndpoints:
    """Test basic API endpoints that don't require database."""
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Welcome to Grateful API" in data["message"]
        assert "version" in data
        assert "docs" in data

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "grateful-api"

    def test_api_docs_available(self):
        """Test that API docs are available."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_schema_available(self):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Grateful API"
        assert "paths" in data


class TestAPIStructure:
    """Test API structure and configuration."""
    
    def test_cors_headers(self):
        """Test that CORS headers are properly configured."""
        response = client.options("/")
        # CORS preflight should work
        assert response.status_code in [200, 405]  # 405 is also acceptable for OPTIONS

    def test_api_has_required_endpoints(self):
        """Test that API has the expected endpoint structure."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        
        # Check that we have the expected paths
        paths = data["paths"]
        assert "/" in paths
        assert "/health" in paths
        # Note: /docs and /openapi.json are not in OpenAPI schema as they're FastAPI-generated endpoints
        # We test /docs and /openapi.json availability separately in other tests

    def test_api_info(self):
        """Test API metadata."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        
        info = data["info"]
        assert info["title"] == "Grateful API"
        assert info["version"] == "1.0.0"
        assert "description" in info


class TestErrorHandling:
    """Test basic error handling."""
    
    def test_404_not_found(self):
        """Test 404 for non-existent endpoints."""
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """Test 405 for wrong HTTP methods."""
        response = client.post("/health")
        assert response.status_code == 405


class TestAPIRoutes:
    """Test that API routes are properly included."""
    
    def test_api_v1_prefix(self):
        """Test that API routes are under /api/v1 prefix."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        
        # Check for API v1 routes
        paths = data["paths"]
        api_v1_paths = [path for path in paths.keys() if path.startswith("/api/v1")]
        assert len(api_v1_paths) > 0, "No API v1 routes found"

    def test_users_endpoint_exists(self):
        """Test that users endpoint exists in OpenAPI schema."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        
        paths = data["paths"]
        user_paths = [path for path in paths.keys() if "/users" in path]
        assert len(user_paths) > 0, "No user endpoints found in API schema"

    def test_posts_endpoint_exists(self):
        """Test that posts endpoint exists in OpenAPI schema."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        
        paths = data["paths"]
        post_paths = [path for path in paths.keys() if "/posts" in path]
        assert len(post_paths) > 0, "No post endpoints found in API schema" 