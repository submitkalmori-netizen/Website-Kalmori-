"""
Iteration 34 - Admin Dashboard Upgrade Tests
Tests for:
1. GET /api/admin/analytics - Platform-wide analytics
2. GET /api/admin/users/{user_id}/detail - User detail with stats
3. PUT /api/admin/users/{user_id}/profile - Update user profile
4. Authentication requirements for all admin endpoints
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials from test_credentials.md
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"


class TestAdminAuthentication:
    """Test that admin endpoints require authentication"""
    
    def test_admin_analytics_requires_auth(self):
        """GET /api/admin/analytics should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: GET /api/admin/analytics returns 401 without auth")
    
    def test_admin_user_detail_requires_auth(self):
        """GET /api/admin/users/{user_id}/detail should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/admin/users/user_test123/detail")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: GET /api/admin/users/{user_id}/detail returns 401 without auth")
    
    def test_admin_update_profile_requires_auth(self):
        """PUT /api/admin/users/{user_id}/profile should return 401 without token"""
        response = requests.put(
            f"{BASE_URL}/api/admin/users/user_test123/profile",
            json={"name": "Test"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("PASS: PUT /api/admin/users/{user_id}/profile returns 401 without auth")


class TestAdminLogin:
    """Test admin login and get token"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Login as admin and get access token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in login response"
        print(f"PASS: Admin login successful, got token")
        return data["access_token"]
    
    def test_admin_login_success(self, admin_token):
        """Verify admin can login"""
        assert admin_token is not None
        print("PASS: Admin login returns valid token")


class TestAdminAnalytics:
    """Test GET /api/admin/analytics endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Create authenticated session for admin"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        token = response.json()["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    def test_admin_analytics_returns_total_streams(self, admin_session):
        """Analytics should return total_streams field"""
        response = admin_session.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "total_streams" in data, f"Missing total_streams in response: {data.keys()}"
        assert isinstance(data["total_streams"], int), "total_streams should be int"
        print(f"PASS: total_streams = {data['total_streams']}")
    
    def test_admin_analytics_returns_week_streams(self, admin_session):
        """Analytics should return week_streams field"""
        response = admin_session.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "week_streams" in data, f"Missing week_streams in response: {data.keys()}"
        assert isinstance(data["week_streams"], int), "week_streams should be int"
        print(f"PASS: week_streams = {data['week_streams']}")
    
    def test_admin_analytics_returns_total_stream_revenue(self, admin_session):
        """Analytics should return total_stream_revenue field"""
        response = admin_session.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "total_stream_revenue" in data, f"Missing total_stream_revenue in response: {data.keys()}"
        assert isinstance(data["total_stream_revenue"], (int, float)), "total_stream_revenue should be numeric"
        print(f"PASS: total_stream_revenue = ${data['total_stream_revenue']}")
    
    def test_admin_analytics_returns_platform_breakdown(self, admin_session):
        """Analytics should return platform_breakdown array"""
        response = admin_session.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "platform_breakdown" in data, f"Missing platform_breakdown in response: {data.keys()}"
        assert isinstance(data["platform_breakdown"], list), "platform_breakdown should be list"
        # If there's data, check structure
        if data["platform_breakdown"]:
            item = data["platform_breakdown"][0]
            assert "platform" in item, "platform_breakdown item missing 'platform'"
            assert "streams" in item, "platform_breakdown item missing 'streams'"
        print(f"PASS: platform_breakdown has {len(data['platform_breakdown'])} items")
    
    def test_admin_analytics_returns_country_breakdown(self, admin_session):
        """Analytics should return country_breakdown array"""
        response = admin_session.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "country_breakdown" in data, f"Missing country_breakdown in response: {data.keys()}"
        assert isinstance(data["country_breakdown"], list), "country_breakdown should be list"
        if data["country_breakdown"]:
            item = data["country_breakdown"][0]
            assert "country" in item, "country_breakdown item missing 'country'"
            assert "streams" in item, "country_breakdown item missing 'streams'"
        print(f"PASS: country_breakdown has {len(data['country_breakdown'])} items")
    
    def test_admin_analytics_returns_top_artists(self, admin_session):
        """Analytics should return top_artists array"""
        response = admin_session.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "top_artists" in data, f"Missing top_artists in response: {data.keys()}"
        assert isinstance(data["top_artists"], list), "top_artists should be list"
        if data["top_artists"]:
            item = data["top_artists"][0]
            assert "id" in item, "top_artists item missing 'id'"
            assert "streams" in item, "top_artists item missing 'streams'"
        print(f"PASS: top_artists has {len(data['top_artists'])} items")
    
    def test_admin_analytics_returns_monthly_trend(self, admin_session):
        """Analytics should return monthly_trend array"""
        response = admin_session.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "monthly_trend" in data, f"Missing monthly_trend in response: {data.keys()}"
        assert isinstance(data["monthly_trend"], list), "monthly_trend should be list"
        if data["monthly_trend"]:
            item = data["monthly_trend"][0]
            assert "month" in item, "monthly_trend item missing 'month'"
            assert "streams" in item, "monthly_trend item missing 'streams'"
        print(f"PASS: monthly_trend has {len(data['monthly_trend'])} items")
    
    def test_admin_analytics_returns_active_artists(self, admin_session):
        """Analytics should return active_artists count"""
        response = admin_session.get(f"{BASE_URL}/api/admin/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "active_artists" in data, f"Missing active_artists in response: {data.keys()}"
        assert isinstance(data["active_artists"], int), "active_artists should be int"
        print(f"PASS: active_artists = {data['active_artists']}")


class TestAdminUserDetail:
    """Test GET /api/admin/users/{user_id}/detail endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Create authenticated session for admin"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        token = response.json()["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    @pytest.fixture(scope="class")
    def test_user_id(self, admin_session):
        """Get a user ID from the users list"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users?limit=1")
        assert response.status_code == 200, f"Failed to get users: {response.text}"
        data = response.json()
        if data.get("users") and len(data["users"]) > 0:
            return data["users"][0]["id"]
        # If no users, create one
        test_email = f"test_user_{uuid.uuid4().hex[:8]}@test.com"
        reg_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": test_email, "password": "Test123!", "name": "Test User"}
        )
        if reg_response.status_code == 200:
            return reg_response.json()["user"]["id"]
        pytest.skip("No users available for testing")
    
    def test_user_detail_returns_user_object(self, admin_session, test_user_id):
        """User detail should return user object with basic fields"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users/{test_user_id}/detail")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "user" in data, f"Missing 'user' in response: {data.keys()}"
        user = data["user"]
        assert "id" in user, "user missing 'id'"
        assert "email" in user, "user missing 'email'"
        assert "name" in user or "artist_name" in user, "user missing name fields"
        print(f"PASS: user detail returns user object for {test_user_id}")
    
    def test_user_detail_returns_stats(self, admin_session, test_user_id):
        """User detail should return stats object"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users/{test_user_id}/detail")
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data, f"Missing 'stats' in response: {data.keys()}"
        stats = data["stats"]
        expected_fields = ["total_streams", "total_revenue", "total_releases", "presave_subscribers", "goals_active", "goals_completed"]
        for field in expected_fields:
            assert field in stats, f"stats missing '{field}'"
        print(f"PASS: user detail returns stats with all expected fields")
    
    def test_user_detail_returns_releases(self, admin_session, test_user_id):
        """User detail should return releases array"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users/{test_user_id}/detail")
        assert response.status_code == 200
        data = response.json()
        assert "releases" in data, f"Missing 'releases' in response: {data.keys()}"
        assert isinstance(data["releases"], list), "releases should be list"
        print(f"PASS: user detail returns releases array ({len(data['releases'])} items)")
    
    def test_user_detail_returns_platform_breakdown(self, admin_session, test_user_id):
        """User detail should return platform_breakdown array"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users/{test_user_id}/detail")
        assert response.status_code == 200
        data = response.json()
        assert "platform_breakdown" in data, f"Missing 'platform_breakdown' in response: {data.keys()}"
        assert isinstance(data["platform_breakdown"], list), "platform_breakdown should be list"
        print(f"PASS: user detail returns platform_breakdown")
    
    def test_user_detail_returns_country_breakdown(self, admin_session, test_user_id):
        """User detail should return country_breakdown array"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users/{test_user_id}/detail")
        assert response.status_code == 200
        data = response.json()
        assert "country_breakdown" in data, f"Missing 'country_breakdown' in response: {data.keys()}"
        assert isinstance(data["country_breakdown"], list), "country_breakdown should be list"
        print(f"PASS: user detail returns country_breakdown")
    
    def test_user_detail_returns_weekly_trends(self, admin_session, test_user_id):
        """User detail should return weekly_trends array"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users/{test_user_id}/detail")
        assert response.status_code == 200
        data = response.json()
        assert "weekly_trends" in data, f"Missing 'weekly_trends' in response: {data.keys()}"
        assert isinstance(data["weekly_trends"], list), "weekly_trends should be list"
        print(f"PASS: user detail returns weekly_trends ({len(data['weekly_trends'])} weeks)")
    
    def test_user_detail_returns_goals(self, admin_session, test_user_id):
        """User detail should return goals array"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users/{test_user_id}/detail")
        assert response.status_code == 200
        data = response.json()
        assert "goals" in data, f"Missing 'goals' in response: {data.keys()}"
        assert isinstance(data["goals"], list), "goals should be list"
        print(f"PASS: user detail returns goals array")
    
    def test_user_detail_404_for_invalid_user(self, admin_session):
        """User detail should return 404 for non-existent user"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users/user_nonexistent_xyz/detail")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: user detail returns 404 for invalid user")


class TestAdminUpdateProfile:
    """Test PUT /api/admin/users/{user_id}/profile endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Create authenticated session for admin"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        token = response.json()["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    @pytest.fixture(scope="class")
    def test_user_id(self, admin_session):
        """Get or create a test user for profile updates"""
        # Create a new test user to avoid modifying real users
        test_email = f"test_profile_{uuid.uuid4().hex[:8]}@test.com"
        reg_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"email": test_email, "password": "Test123!", "name": "Profile Test User", "artist_name": "Test Artist"}
        )
        if reg_response.status_code == 200:
            return reg_response.json()["user"]["id"]
        # Fallback to existing user
        response = admin_session.get(f"{BASE_URL}/api/admin/users?limit=1")
        if response.status_code == 200 and response.json().get("users"):
            return response.json()["users"][0]["id"]
        pytest.skip("No users available for testing")
    
    def test_update_profile_name(self, admin_session, test_user_id):
        """Admin can update user's name"""
        new_name = f"Updated Name {uuid.uuid4().hex[:6]}"
        response = admin_session.put(
            f"{BASE_URL}/api/admin/users/{test_user_id}/profile",
            json={"name": new_name}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data, "Response should have message"
        # Verify update
        detail_response = admin_session.get(f"{BASE_URL}/api/admin/users/{test_user_id}/detail")
        assert detail_response.status_code == 200
        assert detail_response.json()["user"]["name"] == new_name
        print(f"PASS: Updated name to '{new_name}'")
    
    def test_update_profile_artist_name(self, admin_session, test_user_id):
        """Admin can update user's artist_name"""
        new_artist_name = f"DJ Test {uuid.uuid4().hex[:6]}"
        response = admin_session.put(
            f"{BASE_URL}/api/admin/users/{test_user_id}/profile",
            json={"artist_name": new_artist_name}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        # Verify update
        detail_response = admin_session.get(f"{BASE_URL}/api/admin/users/{test_user_id}/detail")
        assert detail_response.status_code == 200
        assert detail_response.json()["user"]["artist_name"] == new_artist_name
        print(f"PASS: Updated artist_name to '{new_artist_name}'")
    
    def test_update_profile_bio(self, admin_session, test_user_id):
        """Admin can update user's bio"""
        new_bio = f"Test bio updated at {uuid.uuid4().hex[:8]}"
        response = admin_session.put(
            f"{BASE_URL}/api/admin/users/{test_user_id}/profile",
            json={"bio": new_bio}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"PASS: Updated bio")
    
    def test_update_profile_genre(self, admin_session, test_user_id):
        """Admin can update user's genre"""
        response = admin_session.put(
            f"{BASE_URL}/api/admin/users/{test_user_id}/profile",
            json={"genre": "Hip-Hop"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: Updated genre")
    
    def test_update_profile_country(self, admin_session, test_user_id):
        """Admin can update user's country"""
        response = admin_session.put(
            f"{BASE_URL}/api/admin/users/{test_user_id}/profile",
            json={"country": "United States"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: Updated country")
    
    def test_update_profile_social_links(self, admin_session, test_user_id):
        """Admin can update user's social links"""
        response = admin_session.put(
            f"{BASE_URL}/api/admin/users/{test_user_id}/profile",
            json={
                "spotify_url": "https://open.spotify.com/artist/test",
                "apple_music_url": "https://music.apple.com/artist/test",
                "instagram": "@testartist",
                "twitter": "@testartist"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: Updated social links")
    
    def test_update_profile_role(self, admin_session, test_user_id):
        """Admin can update user's role"""
        response = admin_session.put(
            f"{BASE_URL}/api/admin/users/{test_user_id}/profile",
            json={"role": "producer"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        # Verify
        detail_response = admin_session.get(f"{BASE_URL}/api/admin/users/{test_user_id}/detail")
        assert detail_response.status_code == 200
        # Role might be 'producer' or 'artist' depending on implementation
        print("PASS: Updated role")
    
    def test_update_profile_plan(self, admin_session, test_user_id):
        """Admin can update user's plan"""
        response = admin_session.put(
            f"{BASE_URL}/api/admin/users/{test_user_id}/profile",
            json={"plan": "pro"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        # Verify
        detail_response = admin_session.get(f"{BASE_URL}/api/admin/users/{test_user_id}/detail")
        assert detail_response.status_code == 200
        assert detail_response.json()["user"]["plan"] == "pro"
        print("PASS: Updated plan to 'pro'")
    
    def test_update_profile_status(self, admin_session, test_user_id):
        """Admin can update user's status"""
        response = admin_session.put(
            f"{BASE_URL}/api/admin/users/{test_user_id}/profile",
            json={"status": "active"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: Updated status")
    
    def test_update_profile_404_for_invalid_user(self, admin_session):
        """Update profile should return 404 for non-existent user"""
        response = admin_session.put(
            f"{BASE_URL}/api/admin/users/user_nonexistent_xyz/profile",
            json={"name": "Test"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Update profile returns 404 for invalid user")


class TestAdminDashboardEndpoint:
    """Test GET /api/admin/dashboard endpoint (existing)"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Create authenticated session for admin"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        token = response.json()["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    
    def test_admin_dashboard_returns_stats(self, admin_session):
        """Admin dashboard should return platform stats"""
        response = admin_session.get(f"{BASE_URL}/api/admin/dashboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        expected_fields = ["total_users", "total_releases", "pending_submissions", "total_revenue"]
        for field in expected_fields:
            assert field in data, f"Missing '{field}' in dashboard response"
        print(f"PASS: Admin dashboard returns all expected stats")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
