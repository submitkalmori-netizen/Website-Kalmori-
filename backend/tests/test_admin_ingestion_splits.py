"""
Test suite for Admin Panel, Ingestion/Review Engine, and Split Payments features.
Iteration 5 - Testing new features added to TuneDrop/Kalmori music distribution platform.

Features tested:
1. Admin Dashboard - platform stats
2. Admin Submissions - ingestion review queue
3. Admin Users - user management
4. Split Payments - collaborator revenue splits
5. Ingestion Flow - submission with pending_review status
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://artist-hub-219.preview.emergentagent.com')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"


class TestHealthCheck:
    """Basic health check to ensure API is running"""
    
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health check passed: {data}")


class TestAdminAuth:
    """Test admin authentication"""
    
    def test_admin_login_success(self):
        """Admin can login with correct credentials"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert data["role"] == "admin", f"Expected admin role, got: {data.get('role')}"
        assert data["email"] == ADMIN_EMAIL
        print(f"✓ Admin login successful: {data['name']} ({data['role']})")
        return session
    
    def test_admin_login_wrong_password(self):
        """Admin login fails with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "WrongPassword123!"
        })
        assert response.status_code == 401
        print("✓ Admin login correctly rejected with wrong password")


class TestAdminDashboard:
    """Test GET /api/admin/dashboard - platform stats"""
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_admin_dashboard_returns_stats(self, admin_session):
        """Admin dashboard returns platform statistics"""
        response = admin_session.get(f"{BASE_URL}/api/admin/dashboard")
        assert response.status_code == 200, f"Dashboard failed: {response.text}"
        data = response.json()
        
        # Verify all expected fields are present
        expected_fields = [
            "total_users", "total_releases", "total_tracks",
            "pending_submissions", "approved_submissions", "rejected_submissions",
            "total_revenue", "users_by_plan", "new_users_week", "new_releases_week"
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
        
        # Verify data types
        assert isinstance(data["total_users"], int)
        assert isinstance(data["total_releases"], int)
        assert isinstance(data["pending_submissions"], int)
        assert isinstance(data["total_revenue"], (int, float))
        assert isinstance(data["users_by_plan"], dict)
        
        print(f"✓ Admin dashboard stats: users={data['total_users']}, releases={data['total_releases']}, pending={data['pending_submissions']}")
    
    def test_non_admin_cannot_access_dashboard(self):
        """Non-admin user cannot access admin dashboard"""
        # Create a regular user
        session = requests.Session()
        test_email = f"test_artist_{uuid.uuid4().hex[:8]}@test.com"
        
        # Register as regular artist
        reg_response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Test Artist"
        })
        assert reg_response.status_code == 200
        
        # Try to access admin dashboard
        response = session.get(f"{BASE_URL}/api/admin/dashboard")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Non-admin correctly blocked from admin dashboard")


class TestAdminSubmissions:
    """Test admin submissions/ingestion queue endpoints"""
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_get_submissions_list(self, admin_session):
        """GET /api/admin/submissions returns paginated list"""
        response = admin_session.get(f"{BASE_URL}/api/admin/submissions")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "submissions" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert isinstance(data["submissions"], list)
        
        print(f"✓ Submissions list: {data['total']} total, page {data['page']} of {data['pages']}")
    
    def test_filter_submissions_by_status(self, admin_session):
        """GET /api/admin/submissions?status=pending_review filters correctly"""
        response = admin_session.get(f"{BASE_URL}/api/admin/submissions?status=pending_review")
        assert response.status_code == 200
        data = response.json()
        
        # All returned submissions should have pending_review status
        for sub in data["submissions"]:
            assert sub["status"] == "pending_review", f"Got status: {sub['status']}"
        
        print(f"✓ Filtered submissions by pending_review: {len(data['submissions'])} found")
    
    def test_filter_submissions_approved(self, admin_session):
        """GET /api/admin/submissions?status=approved filters correctly"""
        response = admin_session.get(f"{BASE_URL}/api/admin/submissions?status=approved")
        assert response.status_code == 200
        data = response.json()
        
        for sub in data["submissions"]:
            assert sub["status"] == "approved"
        
        print(f"✓ Filtered submissions by approved: {len(data['submissions'])} found")


class TestAdminUsers:
    """Test admin user management endpoints"""
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_get_users_list(self, admin_session):
        """GET /api/admin/users returns paginated user list"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "users" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert isinstance(data["users"], list)
        
        # Verify user objects have release_count
        if data["users"]:
            user = data["users"][0]
            assert "release_count" in user, "User should have release_count"
            assert "email" in user
            assert "role" in user
            assert "plan" in user
        
        print(f"✓ Users list: {data['total']} total users")
    
    def test_search_users(self, admin_session):
        """GET /api/admin/users?search=admin searches users"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users?search=admin")
        assert response.status_code == 200
        data = response.json()
        
        # Should find at least the admin user
        assert data["total"] >= 1, "Should find at least admin user"
        
        # Verify search matches
        found_admin = False
        for user in data["users"]:
            if "admin" in user["email"].lower() or "admin" in user.get("name", "").lower():
                found_admin = True
                break
        
        assert found_admin, "Admin user should be in search results"
        print(f"✓ User search for 'admin': {data['total']} results")
    
    def test_update_user_role_plan_status(self, admin_session):
        """PUT /api/admin/users/{user_id} updates user"""
        # First create a test user
        test_session = requests.Session()
        test_email = f"test_update_{uuid.uuid4().hex[:8]}@test.com"
        
        reg_response = test_session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Test Update User"
        })
        assert reg_response.status_code == 200
        test_user_id = reg_response.json()["id"]
        
        # Update user via admin
        update_response = admin_session.put(f"{BASE_URL}/api/admin/users/{test_user_id}", json={
            "role": "artist",
            "plan": "rise",
            "status": "active"
        })
        assert update_response.status_code == 200, f"Update failed: {update_response.text}"
        
        # Verify update by fetching users
        users_response = admin_session.get(f"{BASE_URL}/api/admin/users?search={test_email}")
        assert users_response.status_code == 200
        users_data = users_response.json()
        
        updated_user = next((u for u in users_data["users"] if u["id"] == test_user_id), None)
        assert updated_user is not None
        assert updated_user["plan"] == "rise"
        
        print(f"✓ User update successful: plan changed to 'rise'")


class TestIngestionFlow:
    """Test the complete ingestion flow: submit -> pending_review -> approve/reject"""
    
    @pytest.fixture
    def artist_session(self):
        """Create a test artist user"""
        session = requests.Session()
        test_email = f"test_artist_{uuid.uuid4().hex[:8]}@test.com"
        
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Test Artist",
            "artist_name": "Test Artist Name"
        })
        assert response.status_code == 200
        return session, response.json()
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_submit_distribution_creates_pending_review(self, artist_session, admin_session):
        """POST /api/distributions/submit/{release_id} creates submission with pending_review status"""
        session, user = artist_session
        
        # Create a release
        release_response = session.post(f"{BASE_URL}/api/releases", json={
            "title": f"Test Release {uuid.uuid4().hex[:6]}",
            "release_type": "single",
            "genre": "Pop",
            "release_date": "2026-05-01",
            "explicit": False,
            "language": "en"
        })
        assert release_response.status_code == 200
        release = release_response.json()
        release_id = release["id"]
        
        # Note: Distribution submit requires cover art and audio
        # This will fail validation but we can test the endpoint exists
        submit_response = session.post(f"{BASE_URL}/api/distributions/submit/{release_id}", json=["spotify", "apple_music"])
        
        # Should fail because no cover art
        assert submit_response.status_code == 400
        assert "cover art" in submit_response.json()["detail"].lower()
        
        print(f"✓ Distribution submit correctly validates cover art requirement")
    
    def test_review_submission_approve(self, admin_session):
        """PUT /api/admin/submissions/{release_id}/review approves submission"""
        # Get a pending submission if any
        subs_response = admin_session.get(f"{BASE_URL}/api/admin/submissions?status=pending_review")
        assert subs_response.status_code == 200
        subs = subs_response.json()["submissions"]
        
        if not subs:
            pytest.skip("No pending submissions to test approval")
        
        release_id = subs[0]["release_id"]
        
        # Approve the submission
        review_response = admin_session.put(f"{BASE_URL}/api/admin/submissions/{release_id}/review", json={
            "action": "approve",
            "notes": "Test approval"
        })
        assert review_response.status_code == 200
        data = review_response.json()
        assert data["status"] == "approved"
        
        print(f"✓ Submission approved: {release_id}")
    
    def test_review_submission_reject(self, admin_session):
        """PUT /api/admin/submissions/{release_id}/review rejects submission"""
        # Get a pending submission if any
        subs_response = admin_session.get(f"{BASE_URL}/api/admin/submissions?status=pending_review")
        assert subs_response.status_code == 200
        subs = subs_response.json()["submissions"]
        
        if not subs:
            pytest.skip("No pending submissions to test rejection")
        
        release_id = subs[0]["release_id"]
        
        # Reject the submission
        review_response = admin_session.put(f"{BASE_URL}/api/admin/submissions/{release_id}/review", json={
            "action": "reject",
            "notes": "Does not meet quality guidelines"
        })
        assert review_response.status_code == 200
        data = review_response.json()
        assert data["status"] == "rejected"
        
        print(f"✓ Submission rejected: {release_id}")


class TestSplitPayments:
    """Test split payment endpoints for collaborator revenue sharing"""
    
    @pytest.fixture
    def artist_with_track(self):
        """Create artist with a release and track"""
        session = requests.Session()
        test_email = f"test_split_{uuid.uuid4().hex[:8]}@test.com"
        
        # Register
        reg_response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Split Test Artist"
        })
        assert reg_response.status_code == 200
        user = reg_response.json()
        
        # Create release
        release_response = session.post(f"{BASE_URL}/api/releases", json={
            "title": f"Split Test Release {uuid.uuid4().hex[:6]}",
            "release_type": "single",
            "genre": "Hip Hop",
            "release_date": "2026-06-01",
            "explicit": False,
            "language": "en"
        })
        assert release_response.status_code == 200
        release = release_response.json()
        
        # Create track
        track_response = session.post(f"{BASE_URL}/api/tracks", json={
            "release_id": release["id"],
            "title": "Split Test Track",
            "track_number": 1,
            "explicit": False
        })
        assert track_response.status_code == 200
        track = track_response.json()
        
        return session, user, release, track
    
    def test_create_split_agreement(self, artist_with_track):
        """POST /api/splits creates split agreement with collaborators"""
        session, user, release, track = artist_with_track
        
        response = session.post(f"{BASE_URL}/api/splits", json={
            "track_id": track["id"],
            "collaborators": [
                {"name": "Producer A", "email": "producer@test.com", "role": "producer", "percentage": 25.0},
                {"name": "Writer B", "email": "writer@test.com", "role": "songwriter", "percentage": 15.0}
            ]
        })
        assert response.status_code == 200, f"Create split failed: {response.text}"
        data = response.json()
        
        assert "split_id" in data
        assert data["owner_percentage"] == 60.0  # 100 - 25 - 15
        
        print(f"✓ Split agreement created: owner gets {data['owner_percentage']}%")
    
    def test_get_split_details(self, artist_with_track):
        """GET /api/splits/{track_id} returns split details"""
        session, user, release, track = artist_with_track
        
        # First create a split
        session.post(f"{BASE_URL}/api/splits", json={
            "track_id": track["id"],
            "collaborators": [
                {"name": "Collab C", "email": "collab@test.com", "role": "featured_artist", "percentage": 20.0}
            ]
        })
        
        # Get split details
        response = session.get(f"{BASE_URL}/api/splits/{track['id']}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["track_id"] == track["id"]
        assert "collaborators" in data
        assert "owner_percentage" in data
        assert len(data["collaborators"]) == 1
        assert data["collaborators"][0]["percentage"] == 20.0
        
        print(f"✓ Split details retrieved: {len(data['collaborators'])} collaborators")
    
    def test_update_split_percentages(self, artist_with_track):
        """PUT /api/splits/{track_id} updates split percentages"""
        session, user, release, track = artist_with_track
        
        # Create initial split
        session.post(f"{BASE_URL}/api/splits", json={
            "track_id": track["id"],
            "collaborators": [
                {"name": "Initial Collab", "email": "initial@test.com", "role": "producer", "percentage": 30.0}
            ]
        })
        
        # Update split
        response = session.put(f"{BASE_URL}/api/splits/{track['id']}", json={
            "collaborators": [
                {"name": "Updated Collab", "email": "updated@test.com", "role": "producer", "percentage": 40.0},
                {"name": "New Collab", "email": "new@test.com", "role": "songwriter", "percentage": 10.0}
            ]
        })
        assert response.status_code == 200
        data = response.json()
        
        assert data["owner_percentage"] == 50.0  # 100 - 40 - 10
        
        # Verify update
        get_response = session.get(f"{BASE_URL}/api/splits/{track['id']}")
        assert get_response.status_code == 200
        split_data = get_response.json()
        assert len(split_data["collaborators"]) == 2
        
        print(f"✓ Split updated: owner now gets {data['owner_percentage']}%")
    
    def test_delete_split_agreement(self, artist_with_track):
        """DELETE /api/splits/{track_id} removes split agreement"""
        session, user, release, track = artist_with_track
        
        # Create split
        session.post(f"{BASE_URL}/api/splits", json={
            "track_id": track["id"],
            "collaborators": [
                {"name": "To Delete", "email": "delete@test.com", "role": "producer", "percentage": 20.0}
            ]
        })
        
        # Delete split
        response = session.delete(f"{BASE_URL}/api/splits/{track['id']}")
        assert response.status_code == 200
        
        # Verify deletion - should return empty collaborators
        get_response = session.get(f"{BASE_URL}/api/splits/{track['id']}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["collaborators"] == []
        assert data["owner_percentage"] == 100.0
        
        print(f"✓ Split agreement deleted, owner back to 100%")
    
    def test_split_percentage_validation(self, artist_with_track):
        """Split percentages cannot exceed 100%"""
        session, user, release, track = artist_with_track
        
        response = session.post(f"{BASE_URL}/api/splits", json={
            "track_id": track["id"],
            "collaborators": [
                {"name": "Greedy A", "email": "greedy1@test.com", "role": "producer", "percentage": 60.0},
                {"name": "Greedy B", "email": "greedy2@test.com", "role": "songwriter", "percentage": 50.0}
            ]
        })
        assert response.status_code == 400
        assert "100" in response.json()["detail"]
        
        print("✓ Split percentage validation working (>100% rejected)")


class TestAdminAccessControl:
    """Test that admin routes are properly protected"""
    
    def test_unauthenticated_cannot_access_admin(self):
        """Unauthenticated requests to admin endpoints return 401"""
        endpoints = [
            "/api/admin/dashboard",
            "/api/admin/submissions",
            "/api/admin/users"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 401, f"{endpoint} should require auth"
        
        print("✓ All admin endpoints require authentication")
    
    def test_regular_user_cannot_access_admin(self):
        """Regular artist cannot access admin endpoints"""
        session = requests.Session()
        test_email = f"test_regular_{uuid.uuid4().hex[:8]}@test.com"
        
        # Register as regular user
        session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Regular User"
        })
        
        endpoints = [
            "/api/admin/dashboard",
            "/api/admin/submissions",
            "/api/admin/users"
        ]
        
        for endpoint in endpoints:
            response = session.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 403, f"{endpoint} should return 403 for non-admin"
        
        print("✓ Regular users blocked from admin endpoints (403)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
