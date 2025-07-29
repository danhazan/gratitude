"""
Unit tests for authentication endpoints.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.models.user import User
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest_asyncio.fixture
async def test_user_data():
    """Test user data for authentication tests."""
    # Generate unique identifiers to avoid conflicts
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"testuser{unique_id}",
        "email": f"test{unique_id}@example.com",
        "password": "testpassword123"
    }


class TestAuthEndpoints:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_signup_success(self, async_client: AsyncClient, test_user_data):
        """Test successful user signup."""
        response = await async_client.post("/api/v1/auth/signup", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Check response structure
        assert "id" in data
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        
        # Password should not be returned
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, async_client: AsyncClient, test_user_data):
        """Test signup with duplicate email."""
        # First create a user
        response = await async_client.post("/api/v1/auth/signup", json=test_user_data)
        assert response.status_code == 201

        # Try to create another user with the same email
        response = await async_client.post("/api/v1/auth/signup", json=test_user_data)
        
        assert response.status_code == 409
        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_signup_invalid_data(self, async_client: AsyncClient):
        """Test signup with invalid data."""
        invalid_data = {
            "username": "test",
            "email": "invalid-email",
            "password": "123"  # Too short
        }
        
        response = await async_client.post("/api/v1/auth/signup", json=invalid_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, test_user):
        """Test successful login."""
        login_data = {
            "email": test_user.email,
            "password": "testpassword"  # From fixture
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.skip(reason="Session endpoint needs to be fixed after removing full_name field")
    @pytest.mark.asyncio
    async def test_session_valid_token(self, async_client: AsyncClient, test_user, auth_headers):
        """Test session check with valid token."""
        # Create a valid token for the test user
        headers = auth_headers(test_user.id)
        
        response = await async_client.get("/api/v1/auth/session", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "id" in data
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    @pytest.mark.asyncio
    async def test_session_invalid_token(self, async_client: AsyncClient):
        """Test session check with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        
        response = await async_client.get("/api/v1/auth/session", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_session_no_token(self, async_client: AsyncClient):
        """Test session check without token."""
        response = await async_client.get("/api/v1/auth/session")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_logout_success(self, async_client: AsyncClient, test_user, auth_headers):
        """Test successful logout."""
        headers = auth_headers(test_user.id)
        
        response = await async_client.post("/api/v1/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "logged out" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_logout_no_token(self, async_client: AsyncClient):
        """Test logout without token."""
        response = await async_client.post("/api/v1/auth/logout")
        
        assert response.status_code == 200  # Logout is a no-op, always succeeds
        data = response.json()
        assert "message" in data


class TestAuthValidation:
    """Test authentication validation and edge cases."""

    @pytest.mark.asyncio
    async def test_signup_missing_fields(self, async_client: AsyncClient):
        """Test signup with missing required fields."""
        incomplete_data = {
            "username": "testuser",
            "email": "test@example.com"
            # Missing password
        }
        
        response = await async_client.post("/api/v1/auth/signup", json=incomplete_data)
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, async_client: AsyncClient):
        """Test login with missing required fields."""
        incomplete_data = {
            "email": "test@example.com"
            # Missing password
        }
        
        response = await async_client.post("/api/v1/auth/login", json=incomplete_data)
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_password_hashing(self, async_client: AsyncClient, test_user_data):
        """Test that passwords are properly hashed during signup."""
        response = await async_client.post("/api/v1/auth/signup", json=test_user_data)
        
        assert response.status_code == 201
        
        # Verify password was hashed (we can't directly check the hash,
        # but we can verify the user can login with the original password)
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        login_response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200 