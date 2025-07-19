import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.post import Post, PostType
from app.schemas.post import PostCreate

pytestmark = pytest.mark.posts

class TestPostEndpoints:
    """Test post-related endpoints."""
    
    def test_create_post_success(self, async_client: TestClient, test_user: User):
        """Test successful post creation."""
        post_data = {
            "content": "I'm grateful for this beautiful day!",
            "post_type": "daily",
            "title": "Daily Gratitude",
            "location": "Home"
        }
        
        # Mock authentication header
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = async_client.post("/api/v1/posts/", json=post_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == post_data["content"]
        assert data["post_type"] == post_data["post_type"]
        assert data["title"] == post_data["title"]
        assert data["location"] == post_data["location"]
        assert "id" in data
        assert data["author_id"] == test_user.id

    def test_create_post_unauthorized(self, async_client: TestClient):
        """Test post creation without authentication."""
        post_data = {
            "content": "I'm grateful for this beautiful day!",
            "post_type": "daily"
        }
        
        response = async_client.post("/api/v1/posts/", json=post_data)
        
        assert response.status_code == 401

    def test_create_post_invalid_content(self, async_client: TestClient, test_user: User):
        """Test post creation with invalid content."""
        post_data = {
            "content": "",  # Empty content
            "post_type": "daily"
        }
        
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = async_client.post("/api/v1/posts/", json=post_data, headers=headers)
        
        assert response.status_code == 422

    def test_create_post_invalid_type(self, async_client: TestClient, test_user: User):
        """Test post creation with invalid post type."""
        post_data = {
            "content": "I'm grateful for this beautiful day!",
            "post_type": "invalid_type"
        }
        
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = async_client.post("/api/v1/posts/", json=post_data, headers=headers)
        
        assert response.status_code == 422

    def test_get_post_success(self, async_client: TestClient, test_post: Post):
        """Test getting a specific post."""
        response = async_client.get(f"/api/v1/posts/{test_post.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_post.id
        assert data["content"] == test_post.content
        assert data["post_type"] == test_post.post_type
        assert "author" in data
        assert "likes_count" in data
        assert "comments_count" in data

    def test_get_post_not_found(self, async_client: TestClient):
        """Test getting non-existent post."""
        response = async_client.get("/api/v1/posts/non-existent-id")
        
        assert response.status_code == 404
        assert "Post not found" in response.json()["detail"]

    def test_get_posts_list(self, async_client: TestClient, test_post: Post):
        """Test getting list of posts."""
        response = async_client.get("/api/v1/posts/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_posts_by_type(self, async_client: TestClient, test_post: Post):
        """Test getting posts by type."""
        response = async_client.get(f"/api/v1/posts/?post_type={test_post.post_type}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert all(post["post_type"] == test_post.post_type for post in data)

    def test_search_posts(self, async_client: TestClient, test_post: Post):
        """Test searching posts."""
        search_term = "gratitude"
        response = async_client.get(f"/api/v1/posts/?q={search_term}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_update_post_success(self, async_client: TestClient, test_post: Post, test_user: User):
        """Test successful post update."""
        update_data = {
            "content": "Updated gratitude content",
            "title": "Updated Title"
        }
        
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = async_client.put(f"/api/v1/posts/{test_post.id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == update_data["content"]
        assert data["title"] == update_data["title"]

    def test_update_post_unauthorized(self, async_client: TestClient, test_post: Post):
        """Test post update without authentication."""
        update_data = {"content": "Updated content"}
        
        response = async_client.put(f"/api/v1/posts/{test_post.id}", json=update_data)
        
        assert response.status_code == 401

    def test_update_post_not_owner(self, async_client: TestClient, test_post: Post, test_user2: User):
        """Test post update by non-owner."""
        update_data = {"content": "Updated content"}
        
        headers = {"Authorization": f"Bearer test-token-{test_user2.id}"}
        response = async_client.put(f"/api/v1/posts/{test_post.id}", json=update_data, headers=headers)
        
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]

    def test_delete_post_success(self, async_client: TestClient, test_post: Post, test_user: User):
        """Test successful post deletion."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = async_client.delete(f"/api/v1/posts/{test_post.id}", headers=headers)
        
        assert response.status_code == 204

    def test_delete_post_unauthorized(self, async_client: TestClient, test_post: Post):
        """Test post deletion without authentication."""
        response = async_client.delete(f"/api/v1/posts/{test_post.id}")
        
        assert response.status_code == 401

    def test_delete_post_not_owner(self, async_client: TestClient, test_post: Post, test_user2: User):
        """Test post deletion by non-owner."""
        headers = {"Authorization": f"Bearer test-token-{test_user2.id}"}
        response = async_client.delete(f"/api/v1/posts/{test_post.id}", headers=headers)
        
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]

class TestPostInteractions:
    """Test post interaction endpoints."""
    
    def test_like_post_success(self, async_client: TestClient, test_post: Post, test_user: User):
        """Test successful post like."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = async_client.post(f"/api/v1/posts/{test_post.id}/like", headers=headers)
        
        assert response.status_code == 201
        assert "Post liked successfully" in response.json()["message"]

    def test_like_post_unauthorized(self, async_client: TestClient, test_post: Post):
        """Test post like without authentication."""
        response = async_client.post(f"/api/v1/posts/{test_post.id}/like")
        
        assert response.status_code == 401

    def test_like_post_not_found(self, async_client: TestClient, test_user: User):
        """Test liking non-existent post."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = async_client.post("/api/v1/posts/non-existent-id/like", headers=headers)
        
        assert response.status_code == 404

    def test_unlike_post_success(self, async_client: TestClient, test_post: Post, test_user: User):
        """Test successful post unlike."""
        # First like the post
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        async_client.post(f"/api/v1/posts/{test_post.id}/like", headers=headers)
        
        # Then unlike it
        response = async_client.delete(f"/api/v1/posts/{test_post.id}/like", headers=headers)
        
        assert response.status_code == 204

    def test_create_comment_success(self, async_client: TestClient, test_post: Post, test_user: User):
        """Test successful comment creation."""
        comment_data = {
            "content": "Great post! I'm grateful too!",
            "post_id": test_post.id
        }
        
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        response = async_client.post(f"/api/v1/posts/{test_post.id}/comments", json=comment_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == comment_data["content"]
        assert data["post_id"] == test_post.id
        assert data["author_id"] == test_user.id

    def test_create_comment_unauthorized(self, async_client: TestClient, test_post: Post):
        """Test comment creation without authentication."""
        comment_data = {
            "content": "Great post!",
            "post_id": test_post.id
        }
        
        response = async_client.post(f"/api/v1/posts/{test_post.id}/comments", json=comment_data)
        
        assert response.status_code == 401

    def test_get_post_comments(self, async_client: TestClient, test_post: Post):
        """Test getting post comments."""
        response = async_client.get(f"/api/v1/posts/{test_post.id}/comments")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestPostPagination:
    """Test post pagination."""
    
    def test_posts_pagination(self, async_client: TestClient):
        """Test posts pagination."""
        response = async_client.get("/api/v1/posts/?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_comments_pagination(self, async_client: TestClient, test_post: Post):
        """Test comments pagination."""
        response = async_client.get(f"/api/v1/posts/{test_post.id}/comments?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5 