import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.post import Post
from app.schemas.user import UserCreate

pytestmark = pytest.mark.users

class TestUserEndpoints:
    """Test user-related endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, async_client, db_session):
        import uuid
        unique = uuid.uuid4().hex[:8]
        user_data = {
            "email": f"newuser_{unique}@example.com",
            "username": f"newuser_{unique}",
            "full_name": "New User",
            "bio": "A test user",
            "password": "testpassword"
        }
        response = await async_client.post("/api/v1/users/", json=user_data)
        if response.status_code != 201:
            print("Response status:", response.status_code)
            print("Response body:", response.text)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert data["bio"] == user_data["bio"]
        assert "id" in data
        assert data["is_verified"] is False
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, async_client, test_user):
        user_data = {
            "email": test_user.email,
            "username": "differentuser",
            "full_name": "Different User",
            "password": "testpassword"
        }
        response = await async_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, async_client, test_user):
        user_data = {
            "email": "different@example.com",
            "username": test_user.username,
            "full_name": "Different User",
            "password": "testpassword"
        }
        response = await async_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_user_invalid_email(self, async_client):
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "full_name": "Test User",
            "password": "testpassword"
        }
        response = await async_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_user_invalid_username(self, async_client):
        user_data = {
            "email": "test@example.com",
            "username": "a",  # Too short
            "full_name": "Test User",
            "password": "testpassword"
        }
        response = await async_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, async_client, test_user):
        response = await async_client.get(f"/api/v1/users/{test_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "posts_count" in data
        assert "followers_count" in data
        assert "following_count" in data

    @pytest.mark.asyncio
    async def test_get_user_profile_not_found(self, async_client):
        response = await async_client.get("/api/v1/users/non-existent-id")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_search_users_success(self, async_client, test_user):
        response = await async_client.get(f"/api/v1/users/search/?q={test_user.username}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any(user["username"] == test_user.username for user in data)

    @pytest.mark.asyncio
    async def test_search_users_empty_query(self, async_client):
        response = await async_client.get("/api/v1/users/search/?q=")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_user_posts_success(self, async_client, test_user, test_post):
        response = await async_client.get(f"/api/v1/users/{test_user.id}/posts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any(post["author"]["id"] == test_user.id for post in data)

    @pytest.mark.asyncio
    async def test_get_user_posts_not_found(self, async_client):
        response = await async_client.get("/api/v1/users/non-existent-id/posts")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_user_followers_success(self, async_client, test_user):
        response = await async_client.get(f"/api/v1/users/{test_user.id}/followers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_user_following_success(self, async_client, test_user):
        response = await async_client.get(f"/api/v1/users/{test_user.id}/following")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_update_user_profile(self, async_client, test_user):
        # Ensure test_user has a password set for token auth if required
        token = f"test-token-{test_user.id}"
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {
            "username": "updateduser",
            "full_name": "Updated User",
            "bio": "Updated bio",
            "avatar_url": "https://example.com/avatar.png"
        }
        response = await async_client.put("/api/v1/users/me", json=update_data, headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["username"] == update_data["username"]
        assert data["full_name"] == update_data["full_name"]
        assert data["bio"] == update_data["bio"]
        assert data["avatar_url"] == update_data["avatar_url"]

class TestUserValidation:
    """Test user validation logic."""

    @pytest.mark.asyncio
    async def test_username_pattern_validation(self, async_client):
        user_data = {
            "email": "test@example.com",
            "username": "invalid-username!",  # Invalid characters
            "full_name": "Test User",
            "password": "testpassword"
        }
        response = await async_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_username_length_validation(self, async_client):
        user_data = {
            "email": "test@example.com",
            "username": "ab",  # Too short
            "full_name": "Test User",
            "password": "testpassword"
        }
        response = await async_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_email_validation(self, async_client):
        user_data = {
            "email": "not-an-email",
            "username": "testuser",
            "full_name": "Test User",
            "password": "testpassword"
        }
        response = await async_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 422

class TestUserPagination:
    """Test user pagination endpoints."""

    @pytest.mark.asyncio
    async def test_search_users_pagination(self, async_client):
        response = await async_client.get("/api/v1/users/search/?q=test&skip=0&limit=5")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_user_posts_pagination(self, async_client, test_user):
        response = await async_client.get(f"/api/v1/users/{test_user.id}/posts?skip=0&limit=5")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_user_followers_pagination(self, async_client, test_user):
        response = await async_client.get(f"/api/v1/users/{test_user.id}/followers?skip=0&limit=5")
        assert response.status_code == 200 