import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.post import Post
from app.schemas.user import UserCreate

pytestmark = pytest.mark.users

class TestUserEndpoints:
    """Test user-related endpoints."""
    
    def test_create_user_success(self, async_client: TestClient, db_session: AsyncSession):
        """Test successful user creation."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "bio": "A test user"
        }
        
        response = async_client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert data["bio"] == user_data["bio"]
        assert "id" in data
        assert data["is_verified"] is False
        assert data["is_active"] is True

    def test_create_user_duplicate_email(self, async_client: TestClient, test_user: User):
        """Test user creation with duplicate email."""
        user_data = {
            "email": test_user.email,
            "username": "differentuser",
            "full_name": "Different User"
        }
        
        response = async_client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_create_user_duplicate_username(self, async_client: TestClient, test_user: User):
        """Test user creation with duplicate username."""
        user_data = {
            "email": "different@example.com",
            "username": test_user.username,
            "full_name": "Different User"
        }
        
        response = async_client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    def test_create_user_invalid_email(self, async_client: TestClient):
        """Test user creation with invalid email."""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "full_name": "Test User"
        }
        
        response = async_client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 422

    def test_create_user_invalid_username(self, async_client: TestClient):
        """Test user creation with invalid username."""
        user_data = {
            "email": "test@example.com",
            "username": "a",  # Too short
            "full_name": "Test User"
        }
        
        response = async_client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 422

    def test_get_user_profile_success(self, async_client: TestClient, test_user: User):
        """Test getting user profile."""
        response = async_client.get(f"/api/v1/users/{test_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "posts_count" in data
        assert "followers_count" in data
        assert "following_count" in data

    def test_get_user_profile_not_found(self, async_client: TestClient):
        """Test getting non-existent user profile."""
        response = async_client.get("/api/v1/users/non-existent-id")
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_search_users_success(self, async_client: TestClient, test_user: User):
        """Test user search."""
        response = async_client.get(f"/api/v1/users/search/?q={test_user.username}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any(user["username"] == test_user.username for user in data)

    def test_search_users_empty_query(self, async_client: TestClient):
        """Test user search with empty query."""
        response = async_client.get("/api/v1/users/search/?q=")
        
        assert response.status_code == 422

    def test_get_user_posts_success(self, async_client: TestClient, test_user: User, test_post: Post):
        """Test getting user posts."""
        response = async_client.get(f"/api/v1/users/{test_user.id}/posts")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any(post["author"]["id"] == test_user.id for post in data)

    def test_get_user_posts_not_found(self, async_client: TestClient):
        """Test getting posts for non-existent user."""
        response = async_client.get("/api/v1/users/non-existent-id/posts")
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_get_user_followers_success(self, async_client: TestClient, test_user: User):
        """Test getting user followers."""
        response = async_client.get(f"/api/v1/users/{test_user.id}/followers")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_user_following_success(self, async_client: TestClient, test_user: User):
        """Test getting users that a user is following."""
        response = async_client.get(f"/api/v1/users/{test_user.id}/following")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestUserValidation:
    """Test user validation scenarios."""
    
    def test_username_pattern_validation(self, async_client: TestClient):
        """Test username pattern validation."""
        user_data = {
            "email": "test@example.com",
            "username": "invalid-username!",  # Invalid characters
            "full_name": "Test User"
        }
        
        response = async_client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 422

    def test_username_length_validation(self, async_client: TestClient):
        """Test username length validation."""
        user_data = {
            "email": "test@example.com",
            "username": "ab",  # Too short
            "full_name": "Test User"
        }
        
        response = async_client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 422

    def test_email_validation(self, async_client: TestClient):
        """Test email format validation."""
        user_data = {
            "email": "not-an-email",
            "username": "testuser",
            "full_name": "Test User"
        }
        
        response = async_client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 422

class TestUserPagination:
    """Test user pagination."""
    
    def test_search_users_pagination(self, async_client: TestClient):
        """Test user search pagination."""
        response = async_client.get("/api/v1/users/search/?q=test&skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_user_posts_pagination(self, async_client: TestClient, test_user: User):
        """Test user posts pagination."""
        response = async_client.get(f"/api/v1/users/{test_user.id}/posts?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_user_followers_pagination(self, async_client: TestClient, test_user: User):
        """Test user followers pagination."""
        response = async_client.get(f"/api/v1/users/{test_user.id}/followers?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5 