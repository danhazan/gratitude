import pytest
# pytest.skip("Disabled due to known issues. See TEST_STATUS.md for details.", allow_module_level=True)
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.post import Post

pytestmark = pytest.mark.integration

class TestCompleteWorkflow:
    """Test complete API workflow scenarios."""
    
    @pytest.mark.asyncio
    async def test_complete_user_workflow(self, async_client: AsyncClient, db_session: AsyncSession):
        """Test complete user workflow: create, update, search, profile."""
        # 1. Create a user
        user_data = {
            "email": "workflow@example.com",
            "username": "workflowuser",
            "full_name": "Workflow User",
            "bio": "Testing the complete workflow"
        }
        
        response = await async_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        user = response.json()
        user_id = user["id"]
        
        # 2. Get user profile
        response = await async_client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        profile = response.json()
        assert profile["username"] == user_data["username"]
        assert profile["posts_count"] == 0
        assert profile["followers_count"] == 0
        assert profile["following_count"] == 0
        
        # 3. Search for the user
        response = await async_client.get(f"/api/v1/users/search/?q={user_data['username']}")
        assert response.status_code == 200
        search_results = response.json()
        assert len(search_results) > 0
        assert any(u["username"] == user_data["username"] for u in search_results)

    @pytest.mark.asyncio
    async def test_complete_post_workflow(self, async_client: AsyncClient, test_user: User):
        """Test complete post workflow: create, like, comment, update, delete."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        
        # 1. Create a post
        post_data = {
            "content": "I'm grateful for this amazing workflow test!",
            "post_type": "daily",
            "title": "Workflow Test Post"
        }
        
        response = await async_client.post("/api/v1/posts/", json=post_data, headers=headers)
        assert response.status_code == 201
        post = response.json()
        post_id = post["id"]
        
        # 2. Get the post
        response = await async_client.get(f"/api/v1/posts/{post_id}")
        assert response.status_code == 200
        retrieved_post = response.json()
        assert retrieved_post["content"] == post_data["content"]
        assert retrieved_post["likes_count"] == 0
        assert retrieved_post["comments_count"] == 0
        
        # 3. Like the post
        response = await async_client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
        assert response.status_code == 201
        
        # 4. Comment on the post
        comment_data = {
            "content": "Great post! I'm grateful too!",
            "post_id": post_id
        }
        
        response = await async_client.post(f"/api/v1/posts/{post_id}/comments", json=comment_data, headers=headers)
        assert response.status_code == 201
        
        # 5. Get post comments
        response = await async_client.get(f"/api/v1/posts/{post_id}/comments")
        assert response.status_code == 200
        comments = response.json()
        assert len(comments) > 0
        
        # 6. Update the post
        update_data = {
            "content": "Updated: I'm grateful for this amazing workflow test!",
            "title": "Updated Workflow Test Post"
        }
        
        response = await async_client.put(f"/api/v1/posts/{post_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        updated_post = response.json()
        assert updated_post["content"] == update_data["content"]
        assert updated_post["title"] == update_data["title"]
        
        # 7. Delete the post
        response = await async_client.delete(f"/api/v1/posts/{post_id}", headers=headers)
        assert response.status_code == 204
        
        # 8. Verify post is deleted
        response = await async_client.get(f"/api/v1/posts/{post_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_complete_follow_workflow(self, async_client: AsyncClient, test_user: User, test_user2: User):
        """Test complete follow workflow: follow, check status, get lists, unfollow."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        
        # 1. Check initial following status
        response = await async_client.get(f"/api/v1/follows/{test_user2.id}/is-following", headers=headers)
        assert response.status_code == 200
        assert response.json()["is_following"] is False
        
        # 2. Follow the user
        response = await async_client.post(f"/api/v1/follows/{test_user2.id}", headers=headers)
        assert response.status_code == 201
        
        # 3. Check following status again
        response = await async_client.get(f"/api/v1/follows/{test_user2.id}/is-following", headers=headers)
        assert response.status_code == 200
        assert response.json()["is_following"] is True
        
        # 4. Get following list
        response = await async_client.get("/api/v1/follows/me/following", headers=headers)
        assert response.status_code == 200
        following = response.json()
        assert len(following) > 0
        assert any(u["id"] == test_user2.id for u in following)
        
        # 5. Get followers list for test_user2
        headers2 = {"Authorization": f"Bearer test-token-{test_user2.id}"}
        response = await async_client.get("/api/v1/follows/me/followers", headers=headers2)
        assert response.status_code == 200
        followers = response.json()
        assert len(followers) > 0
        assert any(u["id"] == test_user.id for u in followers)
        
        # 6. Unfollow the user
        response = await async_client.delete(f"/api/v1/follows/{test_user2.id}", headers=headers)
        assert response.status_code == 204
        
        # 7. Check following status after unfollow
        response = await async_client.get(f"/api/v1/follows/{test_user2.id}/is-following", headers=headers)
        assert response.status_code == 200
        assert response.json()["is_following"] is False

    @pytest.mark.asyncio
    async def test_feed_workflow(self, async_client: AsyncClient, test_user: User, test_user2: User):
        """Test feed workflow: create posts, follow users, check feed."""
        headers1 = {"Authorization": f"Bearer test-token-{test_user.id}"}
        headers2 = {"Authorization": f"Bearer test-token-{test_user2.id}"}
        
        # 1. Create posts for both users
        post1_data = {"content": "User 1's gratitude post", "post_type": "daily"}
        post2_data = {"content": "User 2's gratitude post", "post_type": "daily"}
        
        response1 = await async_client.post("/api/v1/posts/", json=post1_data, headers=headers1)
        response2 = await async_client.post("/api/v1/posts/", json=post2_data, headers=headers2)
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        # 2. User 1 follows User 2
        response = await async_client.post(f"/api/v1/follows/{test_user2.id}", headers=headers1)
        assert response.status_code == 201
        
        # 3. Check User 1's feed (should include both users' posts)
        response = await async_client.get("/api/v1/posts/feed", headers=headers1)
        assert response.status_code == 200
        feed = response.json()
        assert len(feed) >= 2
        
        # 4. Check User 2's feed (should only include User 2's posts)
        response = await async_client.get("/api/v1/posts/feed", headers=headers2)
        assert response.status_code == 200
        feed2 = response.json()
        assert len(feed2) >= 1

    @pytest.mark.asyncio
    async def test_search_and_filter_workflow(self, async_client: AsyncClient, test_user: User):
        """Test search and filter workflow: create posts, search, filter by type."""
        headers = {"Authorization": f"Bearer test-token-{test_user.id}"}
        
        # 1. Create different types of posts
        posts_data = [
            {"content": "Daily gratitude post", "post_type": "daily"},
            {"content": "Photo gratitude post", "post_type": "photo"},
            {"content": "Spontaneous gratitude post", "post_type": "spontaneous"}
        ]
        
        for post_data in posts_data:
            response = await async_client.post("/api/v1/posts/", json=post_data, headers=headers)
            assert response.status_code == 201
        
        # 2. Search for posts
        response = await async_client.get("/api/v1/posts/?q=gratitude")
        assert response.status_code == 200
        search_results = response.json()
        assert len(search_results) >= 3
        
        # 3. Filter by post type
        response = await async_client.get("/api/v1/posts/?post_type=daily")
        assert response.status_code == 200
        daily_posts = response.json()
        assert all(post["post_type"] == "daily" for post in daily_posts)
        
        # 4. Filter by another post type
        response = await async_client.get("/api/v1/posts/?post_type=photo")
        assert response.status_code == 200
        photo_posts = response.json()
        assert all(post["post_type"] == "photo" for post in photo_posts)

    @pytest.mark.asyncio
    async def test_notification_api(self, async_client: AsyncClient, test_user: User, create_test_token):
        """Test notification API: create and fetch notifications."""
        token = create_test_token(test_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        # 1. Create a notification
        notification_data = {
            "user_id": test_user.id,
            "type": "test",
            "priority": "normal",
            "title": "Test Notification",
            "message": "This is a test notification.",
            "data": {"foo": "bar"},
            "channel": "in_app"
        }
        response = await async_client.post("/api/v1/notifications/", json=notification_data, headers=headers)
        assert response.status_code == 201
        notif = response.json()
        assert notif["title"] == notification_data["title"]
        assert notif["message"] == notification_data["message"]
        # 2. Fetch notifications for the user
        response = await async_client.get("/api/v1/notifications/", headers=headers)
        assert response.status_code == 200
        notifications = response.json()
        assert any(n["title"] == notification_data["title"] for n in notifications)

class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_authentication_errors(self, async_client: AsyncClient):
        """Test various authentication error scenarios."""
        # Test protected endpoints without authentication
        endpoints = [
            ("POST", "/api/v1/posts/", {"content": "test", "post_type": "daily"}),
            ("GET", "/api/v1/posts/feed", None),
            ("POST", "/api/v1/follows/test-id", None),
        ]
        
        for method, endpoint, data in endpoints:
            if method == "POST":
                response = await async_client.post(endpoint, json=data)
            elif method == "GET":
                response = await async_client.get(endpoint)
            
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_validation_errors(self, async_client: AsyncClient):
        """Test various validation error scenarios."""
        # Test invalid user creation
        invalid_user_data = {
            "email": "invalid-email",
            "username": "a",  # Too short
            "full_name": "Test User"
        }
        
        response = await async_client.post("/api/v1/users/", json=invalid_user_data)
        assert response.status_code == 422
        
        # Test invalid post creation
        invalid_post_data = {
            "content": "",  # Empty content
            "post_type": "invalid_type"
        }
        
        response = await async_client.post("/api/v1/posts/", json=invalid_post_data)
        assert response.status_code == 401  # Unauthorized, but would be 422 if authenticated

    @pytest.mark.asyncio
    async def test_not_found_errors(self, async_client: AsyncClient):
        """Test various not found error scenarios."""
        # Test non-existent user
        response = await async_client.get("/api/v1/users/non-existent-id")
        assert response.status_code == 404
        
        # Test non-existent post
        response = await async_client.get("/api/v1/posts/non-existent-id")
        assert response.status_code == 404
        
        # Test non-existent user posts
        response = await async_client.get("/api/v1/users/non-existent-id/posts")
        assert response.status_code == 404 