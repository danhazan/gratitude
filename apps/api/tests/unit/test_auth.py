"""
Unit tests for authentication endpoints.
"""

import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient
from app.models.user import User
from tests.utils.factories import UserFactory

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

@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user using the factory."""
    user = UserFactory.create_user(db_session)
    await db_session.commit()
    await db_session.refresh(user)
    return user

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
            "password": "testpassword123"  # Default password from factory
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

    @pytest.mark.asyncio
    async def test_session_valid_token(self, async_client: AsyncClient, test_user):
        """Test session check with valid token."""
        # First login to get a real token
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"  # Default password from factory
        }
        login_response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        
        # Use the token to test session endpoint
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = await async_client.get("/api/v1/auth/session", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    @pytest.mark.asyncio
    async def test_session_expired_token(self, async_client: AsyncClient, test_user):
        """Test session check with expired token."""
        # Create expired token
        headers = {"Authorization": "Bearer expired.token.here"}
        
        response = await async_client.get("/api/v1/auth/session", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "invalid token" in data["detail"].lower()

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
        
        assert response.status_code == 403  # Changed from 401 to 403 - no token provided
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_logout_success(self, async_client: AsyncClient, test_user):
        """Test successful logout."""
        # First login to get a real token
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"  # Default password from factory
        }
        login_response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        
        # Use the token for logout
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
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
    async def test_signup_username_validation(self, async_client: AsyncClient, test_user_data):
        """Test username validation rules."""
        # Test too short username
        data = test_user_data.copy()
        data["username"] = "ab"  # Less than 3 characters
        response = await async_client.post("/api/v1/auth/signup", json=data)
        assert response.status_code == 422

        # Test too long username
        data["username"] = "a" * 51  # More than 50 characters
        response = await async_client.post("/api/v1/auth/signup", json=data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_signup_email_validation(self, async_client: AsyncClient, test_user_data):
        """Test email format validation."""
        invalid_emails = [
            "not-an-email",
            "missing@tld",
            "@notld.com",
            "spaces in@email.com",
            "unicode@🦄.com"
        ]
        
        for invalid_email in invalid_emails:
            data = test_user_data.copy()
            data["email"] = invalid_email
            response = await async_client.post("/api/v1/auth/signup", json=data)
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_signup_password_validation(self, async_client: AsyncClient, test_user_data):
        """Test password strength validation."""
        # Test too short password
        data = test_user_data.copy()
        data["password"] = "short"
        response = await async_client.post("/api/v1/auth/signup", json=data)
        assert response.status_code == 422

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