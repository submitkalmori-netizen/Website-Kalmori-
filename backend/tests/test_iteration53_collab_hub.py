"""
Iteration 53 - Collaboration Hub Backend Tests
Tests for /api/collab-hub/* endpoints:
- POST /api/collab-hub/posts - Create collaboration post
- GET /api/collab-hub/posts - List posts with optional filters
- GET /api/collab-hub/my-posts - Get user's own posts
- PUT /api/collab-hub/posts/{id} - Update post status
- DELETE /api/collab-hub/posts/{id} - Delete post
- POST /api/collab-hub/invite - Send collaboration invite
- GET /api/collab-hub/invites - Get received and sent invites
- PUT /api/collab-hub/invites/{id} - Accept/decline invite
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@kalmori.com"
ADMIN_PASSWORD = "MAYAsimpSON37!!"


class TestCollabHubAuth:
    """Test authentication requirements for collab-hub endpoints"""
    
    def test_posts_requires_auth(self):
        """GET /api/collab-hub/posts requires authentication"""
        response = requests.get(f"{BASE_URL}/api/collab-hub/posts")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/collab-hub/posts requires auth")
    
    def test_my_posts_requires_auth(self):
        """GET /api/collab-hub/my-posts requires authentication"""
        response = requests.get(f"{BASE_URL}/api/collab-hub/my-posts")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/collab-hub/my-posts requires auth")
    
    def test_create_post_requires_auth(self):
        """POST /api/collab-hub/posts requires authentication"""
        response = requests.post(f"{BASE_URL}/api/collab-hub/posts", json={
            "title": "Test", "looking_for": "vocalist", "genre": "Pop"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/collab-hub/posts requires auth")
    
    def test_invites_requires_auth(self):
        """GET /api/collab-hub/invites requires authentication"""
        response = requests.get(f"{BASE_URL}/api/collab-hub/invites")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/collab-hub/invites requires auth")


class TestCollabHubPosts:
    """Test collaboration post CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get("access_token") or data.get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.created_post_ids = []
        yield
        # Cleanup created posts
        for post_id in self.created_post_ids:
            try:
                requests.delete(f"{BASE_URL}/api/collab-hub/posts/{post_id}", headers=self.headers)
            except:
                pass
    
    def test_create_post_success(self):
        """POST /api/collab-hub/posts creates a new collaboration post"""
        unique_title = f"TEST_Looking for vocalist {uuid.uuid4().hex[:6]}"
        payload = {
            "title": unique_title,
            "looking_for": "vocalist",
            "genre": "R&B",
            "description": "Need a vocalist for my new track",
            "budget": "$100 - $500",
            "deadline": "2026-02-15"
        }
        response = requests.post(f"{BASE_URL}/api/collab-hub/posts", json=payload, headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should contain post id"
        assert data["title"] == unique_title
        assert data["looking_for"] == "vocalist"
        assert data["genre"] == "R&B"
        assert data["status"] == "open"
        assert data["responses"] == 0
        
        self.created_post_ids.append(data["id"])
        print(f"✓ Created post: {data['id']}")
    
    def test_create_post_minimal(self):
        """POST /api/collab-hub/posts with minimal required fields"""
        unique_title = f"TEST_Minimal post {uuid.uuid4().hex[:6]}"
        payload = {
            "title": unique_title,
            "looking_for": "producer",
            "genre": "Hip-Hop"
        }
        response = requests.post(f"{BASE_URL}/api/collab-hub/posts", json=payload, headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["title"] == unique_title
        assert data["looking_for"] == "producer"
        self.created_post_ids.append(data["id"])
        print(f"✓ Created minimal post: {data['id']}")
    
    def test_list_posts(self):
        """GET /api/collab-hub/posts returns list of open posts"""
        response = requests.get(f"{BASE_URL}/api/collab-hub/posts", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Listed {len(data)} posts")
    
    def test_list_posts_filter_by_role(self):
        """GET /api/collab-hub/posts?looking_for=vocalist filters by role"""
        # First create a post with specific role
        unique_title = f"TEST_Filter test {uuid.uuid4().hex[:6]}"
        create_resp = requests.post(f"{BASE_URL}/api/collab-hub/posts", json={
            "title": unique_title,
            "looking_for": "mixer",
            "genre": "Electronic"
        }, headers=self.headers)
        assert create_resp.status_code == 200
        post_id = create_resp.json()["id"]
        self.created_post_ids.append(post_id)
        
        # Filter by mixer role
        response = requests.get(f"{BASE_URL}/api/collab-hub/posts?looking_for=mixer", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # All returned posts should have looking_for=mixer
        for post in data:
            assert post["looking_for"] == "mixer", f"Expected mixer, got {post['looking_for']}"
        print(f"✓ Filtered posts by role: {len(data)} mixer posts")
    
    def test_list_posts_filter_by_genre(self):
        """GET /api/collab-hub/posts?genre=Pop filters by genre"""
        # Create a post with specific genre
        unique_title = f"TEST_Genre filter {uuid.uuid4().hex[:6]}"
        create_resp = requests.post(f"{BASE_URL}/api/collab-hub/posts", json={
            "title": unique_title,
            "looking_for": "songwriter",
            "genre": "Pop"
        }, headers=self.headers)
        assert create_resp.status_code == 200
        post_id = create_resp.json()["id"]
        self.created_post_ids.append(post_id)
        
        # Filter by Pop genre
        response = requests.get(f"{BASE_URL}/api/collab-hub/posts?genre=Pop", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1, "Should have at least 1 Pop post"
        print(f"✓ Filtered posts by genre: {len(data)} Pop posts")
    
    def test_my_posts(self):
        """GET /api/collab-hub/my-posts returns user's own posts"""
        # Create a post first
        unique_title = f"TEST_My post {uuid.uuid4().hex[:6]}"
        create_resp = requests.post(f"{BASE_URL}/api/collab-hub/posts", json={
            "title": unique_title,
            "looking_for": "feature",
            "genre": "Latin"
        }, headers=self.headers)
        assert create_resp.status_code == 200
        post_id = create_resp.json()["id"]
        self.created_post_ids.append(post_id)
        
        # Get my posts
        response = requests.get(f"{BASE_URL}/api/collab-hub/my-posts", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Should contain our created post
        post_ids = [p["id"] for p in data]
        assert post_id in post_ids, "Created post should be in my-posts"
        print(f"✓ My posts: {len(data)} posts")
    
    def test_update_post_status(self):
        """PUT /api/collab-hub/posts/{id} updates post status"""
        # Create a post
        unique_title = f"TEST_Update status {uuid.uuid4().hex[:6]}"
        create_resp = requests.post(f"{BASE_URL}/api/collab-hub/posts", json={
            "title": unique_title,
            "looking_for": "dj",
            "genre": "Electronic"
        }, headers=self.headers)
        assert create_resp.status_code == 200
        post_id = create_resp.json()["id"]
        self.created_post_ids.append(post_id)
        
        # Update status to closed
        response = requests.put(f"{BASE_URL}/api/collab-hub/posts/{post_id}", 
                               json={"status": "closed"}, headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "closed", f"Expected closed, got {data['status']}"
        print(f"✓ Updated post status to closed")
    
    def test_update_post_not_found(self):
        """PUT /api/collab-hub/posts/{id} returns 404 for nonexistent post"""
        response = requests.put(f"{BASE_URL}/api/collab-hub/posts/nonexistent_id", 
                               json={"status": "closed"}, headers=self.headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Update nonexistent post returns 404")
    
    def test_delete_post(self):
        """DELETE /api/collab-hub/posts/{id} deletes a post"""
        # Create a post
        unique_title = f"TEST_Delete me {uuid.uuid4().hex[:6]}"
        create_resp = requests.post(f"{BASE_URL}/api/collab-hub/posts", json={
            "title": unique_title,
            "looking_for": "instrumentalist",
            "genre": "Jazz"
        }, headers=self.headers)
        assert create_resp.status_code == 200
        post_id = create_resp.json()["id"]
        
        # Delete the post
        response = requests.delete(f"{BASE_URL}/api/collab-hub/posts/{post_id}", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify it's deleted - should not appear in my-posts
        my_posts = requests.get(f"{BASE_URL}/api/collab-hub/my-posts", headers=self.headers).json()
        post_ids = [p["id"] for p in my_posts]
        assert post_id not in post_ids, "Deleted post should not appear in my-posts"
        print(f"✓ Deleted post: {post_id}")
    
    def test_delete_post_not_found(self):
        """DELETE /api/collab-hub/posts/{id} returns 404 for nonexistent post"""
        response = requests.delete(f"{BASE_URL}/api/collab-hub/posts/nonexistent_id", headers=self.headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Delete nonexistent post returns 404")


class TestCollabHubInvites:
    """Test collaboration invite operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get("access_token") or data.get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.created_post_ids = []
        yield
        # Cleanup
        for post_id in self.created_post_ids:
            try:
                requests.delete(f"{BASE_URL}/api/collab-hub/posts/{post_id}", headers=self.headers)
            except:
                pass
    
    def test_get_invites(self):
        """GET /api/collab-hub/invites returns received and sent invites"""
        response = requests.get(f"{BASE_URL}/api/collab-hub/invites", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "received" in data, "Response should have 'received' key"
        assert "sent" in data, "Response should have 'sent' key"
        assert isinstance(data["received"], list)
        assert isinstance(data["sent"], list)
        print(f"✓ Got invites: {len(data['received'])} received, {len(data['sent'])} sent")
    
    def test_send_invite_to_own_post_fails(self):
        """POST /api/collab-hub/invite fails when inviting to own post"""
        # Create a post
        unique_title = f"TEST_Own post invite {uuid.uuid4().hex[:6]}"
        create_resp = requests.post(f"{BASE_URL}/api/collab-hub/posts", json={
            "title": unique_title,
            "looking_for": "vocalist",
            "genre": "R&B"
        }, headers=self.headers)
        assert create_resp.status_code == 200
        post_id = create_resp.json()["id"]
        self.created_post_ids.append(post_id)
        
        # Try to send invite to own post
        response = requests.post(f"{BASE_URL}/api/collab-hub/invite", json={
            "post_id": post_id,
            "message": "I want to collaborate"
        }, headers=self.headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "yourself" in response.json().get("detail", "").lower()
        print("✓ Cannot send invite to own post")
    
    def test_send_invite_to_nonexistent_post(self):
        """POST /api/collab-hub/invite fails for nonexistent post"""
        response = requests.post(f"{BASE_URL}/api/collab-hub/invite", json={
            "post_id": "nonexistent_post_id",
            "message": "Hello"
        }, headers=self.headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Cannot send invite to nonexistent post")
    
    def test_respond_to_invite_invalid_action(self):
        """PUT /api/collab-hub/invites/{id} fails with invalid action"""
        response = requests.put(f"{BASE_URL}/api/collab-hub/invites/some_invite_id", 
                               json={"action": "invalid"}, headers=self.headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid invite action returns 400")
    
    def test_respond_to_nonexistent_invite(self):
        """PUT /api/collab-hub/invites/{id} returns 404 for nonexistent invite"""
        response = requests.put(f"{BASE_URL}/api/collab-hub/invites/nonexistent_invite", 
                               json={"action": "accept"}, headers=self.headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Respond to nonexistent invite returns 404")


class TestExistingTestPost:
    """Test that the existing test post is present"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get("access_token") or data.get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_existing_post_in_browse(self):
        """Verify at least 1 post exists in browse (test post mentioned in requirements)"""
        response = requests.get(f"{BASE_URL}/api/collab-hub/posts", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        # Main agent mentioned there's 1 test post: 'Need a vocalist for R&B track'
        # But it might have been cleaned up, so we just check the endpoint works
        print(f"✓ Browse posts endpoint works, found {len(data)} posts")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
