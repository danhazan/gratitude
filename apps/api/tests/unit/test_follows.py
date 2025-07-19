import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.interaction import Follow

pytestmark = pytest.mark.interactions

class TestFollowEndpoints:
    """Test follow-related endpoints."""
    
    @pytest.mark.asyncio
    async def test_follow_user_success(self, async_client: AsyncClient, test_user: User, test_user2: User):
        """Test successful user follow."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = await async_client.post(f"/api/v1/follows/{test_user2.id}", headers=headers)
        
        assert response.status_code == 201
        assert "User followed successfully" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_follow_user_unauthorized(self, async_client: AsyncClient, test_user2: User):
        """Test user follow without authentication."""
        response = await async_client.post(f"/api/v1/follows/{test_user2.id}")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_follow_user_not_found(self, async_client: AsyncClient, test_user: User):
        """Test following non-existent user."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = await async_client.post("/api/v1/follows/non-existent-id", headers=headers)
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_follow_self(self, async_client: AsyncClient, test_user: User):
        """Test following yourself."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = await async_client.post(f"/api/v1/follows/{test_user.id}", headers=headers)
        
        assert response.status_code == 400
        assert "Cannot follow yourself" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_follow_already_following(self, async_client: AsyncClient, test_user: User, test_user2: User):
        """Test following a user you already follow."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        
        # First follow
        response1 = await async_client.post(f"/api/v1/follows/{test_user2.id}", headers=headers)
        assert response1.status_code == 201
        
        # Try to follow again
        response2 = await async_client.post(f"/api/v1/follows/{test_user2.id}", headers=headers)
        assert response2.status_code == 400
        assert "Already following this user" in response2.json()["detail"]

    @pytest.mark.asyncio
    async def test_unfollow_user_success(self, async_client: AsyncClient, test_user: User, test_user2: User):
        """Test successful user unfollow."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        
        # First follow
        await async_client.post(f"/api/v1/follows/{test_user2.id}", headers=headers)
        
        # Then unfollow
        response = await async_client.delete(f"/api/v1/follows/{test_user2.id}", headers=headers)
        
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_unfollow_user_unauthorized(self, async_client: AsyncClient, test_user2: User):
        """Test user unfollow without authentication."""
        response = await async_client.delete(f"/api/v1/follows/{test_user2.id}")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_unfollow_user_not_found(self, async_client: AsyncClient, test_user: User):
        """Test unfollowing non-existent user."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = await async_client.delete("/api/v1/follows/non-existent-id", headers=headers)
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_unfollow_not_following(self, async_client: AsyncClient, test_user: User, test_user2: User):
        """Test unfollowing a user you don't follow."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = await async_client.delete(f"/api/v1/follows/{test_user2.id}", headers=headers)
        
        assert response.status_code == 400
        assert "Not following this user" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_my_followers(self, async_client: AsyncClient, test_user: User, test_user2: User):
        """Test getting current user's followers."""
        # Make test_user2 follow test_user
        headers = {"Authorization": f"Bearer test-token-{test_user2.id}"}
        await async_client.post(f"/api/v1/follows/{test_user.id}", headers=headers)
        
        # Get test_user's followers
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = await async_client.get("/api/v1/follows/me/followers", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_get_my_following(self, async_client: AsyncClient, test_user: User, test_user2: User):
        """Test getting users that current user is following."""
        # Make test_user follow test_user2
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        await async_client.post(f"/api/v1/follows/{test_user2.id}", headers=headers)
        
        # Get test_user's following
        response = await async_client.get("/api/v1/follows/me/following", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_check_if_following_true(self, async_client: AsyncClient, test_user: User, test_user2: User):
        """Test checking if following a user (true case)."""
        # Make test_user follow test_user2
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        await async_client.post(f"/api/v1/follows/{test_user2.id}", headers=headers)
        
        # Check if following
        response = await async_client.get(f"/api/v1/follows/{test_user2.id}/is-following", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_following"] is True

    @pytest.mark.asyncio
    async def test_check_if_following_false(self, async_client: AsyncClient, test_user: User, test_user2: User):
        """Test checking if following a user (false case)."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = await async_client.get(f"/api/v1/follows/{test_user2.id}/is-following", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_following"] is False

    @pytest.mark.asyncio
    async def test_check_if_following_not_found(self, async_client: AsyncClient, test_user: User):
        """Test checking if following non-existent user."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = await async_client.get("/api/v1/follows/non-existent-id/is-following", headers=headers)
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

class TestFollowPagination:
    """Test follow pagination."""
    
    @pytest.mark.asyncio
    async def test_followers_pagination(self, async_client: AsyncClient, test_user: User):
        """Test followers pagination."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = await async_client.get("/api/v1/follows/me/followers?skip=0&limit=5", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    @pytest.mark.asyncio
    async def test_following_pagination(self, async_client: AsyncClient, test_user: User):
        """Test following pagination."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = await async_client.get("/api/v1/follows/me/following?skip=0&limit=5", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

class TestFollowValidation:
    """Test follow validation scenarios."""
    
    @pytest.mark.asyncio
    async def test_follow_invalid_user_id(self, async_client: AsyncClient, test_user: User):
        """Test following with invalid user ID format."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = await async_client.post("/api/v1/follows/invalid-id", headers=headers)
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_unfollow_invalid_user_id(self, async_client: AsyncClient, test_user: User):
        """Test unfollowing with invalid user ID format."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = await async_client.delete("/api/v1/follows/invalid-id", headers=headers)
        
        assert response.status_code == 404 