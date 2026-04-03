"""
Iteration 36 - Label Dashboard Tests
Tests for Label/Producer dashboard endpoints:
- GET /api/label/dashboard - Label overview stats
- GET /api/label/artists - List artists on roster
- POST /api/label/artists/invite - Add artist by email
- DELETE /api/label/artists/{artist_id} - Remove artist from roster
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"


class TestLabelDashboard:
    """Tests for Label Dashboard endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin (label_producer) before each test"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        self.token = login_resp.json().get("access_token")
        self.user = login_resp.json().get("user")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        yield
        self.session.close()
    
    # ============= GET /api/label/dashboard =============
    def test_label_dashboard_returns_200(self):
        """GET /api/label/dashboard returns 200 for authenticated user"""
        resp = self.session.get(f"{BASE_URL}/api/label/dashboard")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        print("✓ GET /api/label/dashboard returns 200")
    
    def test_label_dashboard_structure(self):
        """GET /api/label/dashboard returns correct data structure"""
        resp = self.session.get(f"{BASE_URL}/api/label/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify all required fields exist
        required_fields = [
            "total_artists", "total_streams", "total_revenue", "total_releases",
            "week_streams", "platform_breakdown", "country_breakdown", 
            "top_artists", "recent_releases"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Verify data types
        assert isinstance(data["total_artists"], int), "total_artists should be int"
        assert isinstance(data["total_streams"], int), "total_streams should be int"
        assert isinstance(data["total_revenue"], (int, float)), "total_revenue should be numeric"
        assert isinstance(data["total_releases"], int), "total_releases should be int"
        assert isinstance(data["week_streams"], int), "week_streams should be int"
        assert isinstance(data["platform_breakdown"], list), "platform_breakdown should be list"
        assert isinstance(data["country_breakdown"], list), "country_breakdown should be list"
        assert isinstance(data["top_artists"], list), "top_artists should be list"
        assert isinstance(data["recent_releases"], list), "recent_releases should be list"
        
        print(f"✓ Dashboard structure verified: {len(required_fields)} fields present")
        print(f"  - total_artists: {data['total_artists']}")
        print(f"  - total_streams: {data['total_streams']}")
        print(f"  - total_revenue: ${data['total_revenue']}")
        print(f"  - total_releases: {data['total_releases']}")
    
    def test_label_dashboard_requires_auth(self):
        """GET /api/label/dashboard requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/label/dashboard")
        assert resp.status_code == 401, f"Expected 401 without auth, got {resp.status_code}"
        print("✓ GET /api/label/dashboard requires authentication (401)")
    
    # ============= GET /api/label/artists =============
    def test_label_artists_returns_200(self):
        """GET /api/label/artists returns 200 for authenticated user"""
        resp = self.session.get(f"{BASE_URL}/api/label/artists")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        print("✓ GET /api/label/artists returns 200")
    
    def test_label_artists_structure(self):
        """GET /api/label/artists returns correct data structure"""
        resp = self.session.get(f"{BASE_URL}/api/label/artists")
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify response structure
        assert "artists" in data, "Response should have 'artists' field"
        assert "total" in data, "Response should have 'total' field"
        assert isinstance(data["artists"], list), "artists should be list"
        assert isinstance(data["total"], int), "total should be int"
        
        # If there are artists, verify their structure
        if data["artists"]:
            artist = data["artists"][0]
            expected_fields = ["id", "name", "artist_name", "email", "plan", "streams", "revenue", "releases", "added_at"]
            for field in expected_fields:
                assert field in artist, f"Artist missing field: {field}"
            
            print(f"✓ Artist structure verified with fields: {list(artist.keys())}")
        
        print(f"✓ GET /api/label/artists returns {data['total']} artists")
    
    def test_label_artists_requires_auth(self):
        """GET /api/label/artists requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/label/artists")
        assert resp.status_code == 401, f"Expected 401 without auth, got {resp.status_code}"
        print("✓ GET /api/label/artists requires authentication (401)")
    
    # ============= POST /api/label/artists/invite =============
    def test_invite_artist_nonexistent_email_returns_404(self):
        """POST /api/label/artists/invite returns 404 for non-existent email"""
        resp = self.session.post(f"{BASE_URL}/api/label/artists/invite", json={
            "email": f"nonexistent_{int(time.time())}@test.com"
        })
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "detail" in data, "Response should have error detail"
        print(f"✓ POST /api/label/artists/invite returns 404 for non-existent email: {data['detail']}")
    
    def test_invite_artist_duplicate_returns_409(self):
        """POST /api/label/artists/invite returns 409 for duplicate artist"""
        # First, get existing artists to find one already on roster
        artists_resp = self.session.get(f"{BASE_URL}/api/label/artists")
        assert artists_resp.status_code == 200
        artists = artists_resp.json().get("artists", [])
        
        if artists:
            # Try to add an artist that's already on the roster
            existing_email = artists[0].get("email")
            resp = self.session.post(f"{BASE_URL}/api/label/artists/invite", json={
                "email": existing_email
            })
            assert resp.status_code == 409, f"Expected 409 for duplicate, got {resp.status_code}: {resp.text}"
            data = resp.json()
            assert "detail" in data, "Response should have error detail"
            print(f"✓ POST /api/label/artists/invite returns 409 for duplicate: {data['detail']}")
        else:
            pytest.skip("No artists on roster to test duplicate invite")
    
    def test_invite_artist_requires_auth(self):
        """POST /api/label/artists/invite requires authentication"""
        resp = requests.post(f"{BASE_URL}/api/label/artists/invite", json={
            "email": "test@test.com"
        })
        assert resp.status_code == 401, f"Expected 401 without auth, got {resp.status_code}"
        print("✓ POST /api/label/artists/invite requires authentication (401)")
    
    def test_invite_self_returns_400(self):
        """POST /api/label/artists/invite returns 400 when trying to add self"""
        resp = self.session.post(f"{BASE_URL}/api/label/artists/invite", json={
            "email": ADMIN_EMAIL
        })
        assert resp.status_code == 400, f"Expected 400 for self-invite, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "detail" in data, "Response should have error detail"
        print(f"✓ POST /api/label/artists/invite returns 400 for self-invite: {data['detail']}")
    
    # ============= DELETE /api/label/artists/{artist_id} =============
    def test_remove_artist_nonexistent_returns_404(self):
        """DELETE /api/label/artists/{artist_id} returns 404 for non-existent roster entry"""
        fake_artist_id = f"user_nonexistent_{int(time.time())}"
        resp = self.session.delete(f"{BASE_URL}/api/label/artists/{fake_artist_id}")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "detail" in data, "Response should have error detail"
        print(f"✓ DELETE /api/label/artists returns 404 for non-existent: {data['detail']}")
    
    def test_remove_artist_requires_auth(self):
        """DELETE /api/label/artists/{artist_id} requires authentication"""
        resp = requests.delete(f"{BASE_URL}/api/label/artists/some_artist_id")
        assert resp.status_code == 401, f"Expected 401 without auth, got {resp.status_code}"
        print("✓ DELETE /api/label/artists requires authentication (401)")


class TestLabelDashboardIntegration:
    """Integration tests for full invite/remove flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin before each test"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200
        self.token = login_resp.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        yield
        self.session.close()
    
    def test_full_invite_and_remove_flow(self):
        """Test complete flow: find user -> invite -> verify -> remove -> verify"""
        # First, get list of all users to find one to invite
        # We need to find a user that's NOT already on the roster
        
        # Get current roster
        roster_resp = self.session.get(f"{BASE_URL}/api/label/artists")
        assert roster_resp.status_code == 200
        current_roster = roster_resp.json().get("artists", [])
        current_artist_ids = {a["id"] for a in current_roster}
        
        # Get all users (admin endpoint)
        users_resp = self.session.get(f"{BASE_URL}/api/admin/users")
        if users_resp.status_code != 200:
            pytest.skip("Cannot access admin users endpoint")
        
        all_users = users_resp.json().get("users", [])
        
        # Find a user not on roster and not the admin
        test_user = None
        for u in all_users:
            if u["id"] not in current_artist_ids and u["email"] != ADMIN_EMAIL:
                test_user = u
                break
        
        if not test_user:
            pytest.skip("No available users to test invite flow")
        
        print(f"Testing with user: {test_user['email']}")
        
        # Step 1: Invite the user
        invite_resp = self.session.post(f"{BASE_URL}/api/label/artists/invite", json={
            "email": test_user["email"]
        })
        assert invite_resp.status_code == 200, f"Invite failed: {invite_resp.text}"
        invite_data = invite_resp.json()
        assert "message" in invite_data
        assert "artist_id" in invite_data
        print(f"✓ Invited artist: {invite_data['message']}")
        
        # Step 2: Verify artist is on roster
        roster_resp = self.session.get(f"{BASE_URL}/api/label/artists")
        assert roster_resp.status_code == 200
        updated_roster = roster_resp.json().get("artists", [])
        artist_ids = [a["id"] for a in updated_roster]
        assert test_user["id"] in artist_ids, "Invited artist should be on roster"
        print(f"✓ Verified artist is on roster")
        
        # Step 3: Verify dashboard shows updated count
        dashboard_resp = self.session.get(f"{BASE_URL}/api/label/dashboard")
        assert dashboard_resp.status_code == 200
        dashboard_data = dashboard_resp.json()
        assert dashboard_data["total_artists"] >= 1, "Dashboard should show at least 1 artist"
        print(f"✓ Dashboard shows {dashboard_data['total_artists']} artists")
        
        # Step 4: Remove the artist
        remove_resp = self.session.delete(f"{BASE_URL}/api/label/artists/{test_user['id']}")
        assert remove_resp.status_code == 200, f"Remove failed: {remove_resp.text}"
        remove_data = remove_resp.json()
        assert "message" in remove_data
        print(f"✓ Removed artist: {remove_data['message']}")
        
        # Step 5: Verify artist is no longer on roster
        roster_resp = self.session.get(f"{BASE_URL}/api/label/artists")
        assert roster_resp.status_code == 200
        final_roster = roster_resp.json().get("artists", [])
        final_artist_ids = [a["id"] for a in final_roster]
        assert test_user["id"] not in final_artist_ids, "Removed artist should not be on roster"
        print(f"✓ Verified artist removed from roster")
        
        print("✓ Full invite/remove flow completed successfully")


class TestLabelDashboardDataValidation:
    """Tests for data validation in Label Dashboard"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin before each test"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200
        self.token = login_resp.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        yield
        self.session.close()
    
    def test_platform_breakdown_structure(self):
        """Verify platform_breakdown items have correct structure"""
        resp = self.session.get(f"{BASE_URL}/api/label/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        
        if data["platform_breakdown"]:
            for item in data["platform_breakdown"]:
                assert "platform" in item, "platform_breakdown item should have 'platform'"
                assert "streams" in item, "platform_breakdown item should have 'streams'"
                assert isinstance(item["streams"], int), "streams should be int"
            print(f"✓ platform_breakdown structure verified ({len(data['platform_breakdown'])} platforms)")
        else:
            print("✓ platform_breakdown is empty (no data yet)")
    
    def test_country_breakdown_structure(self):
        """Verify country_breakdown items have correct structure"""
        resp = self.session.get(f"{BASE_URL}/api/label/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        
        if data["country_breakdown"]:
            for item in data["country_breakdown"]:
                assert "country" in item, "country_breakdown item should have 'country'"
                assert "streams" in item, "country_breakdown item should have 'streams'"
                assert isinstance(item["streams"], int), "streams should be int"
            print(f"✓ country_breakdown structure verified ({len(data['country_breakdown'])} countries)")
        else:
            print("✓ country_breakdown is empty (no data yet)")
    
    def test_top_artists_structure(self):
        """Verify top_artists items have correct structure"""
        resp = self.session.get(f"{BASE_URL}/api/label/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        
        if data["top_artists"]:
            for artist in data["top_artists"]:
                assert "id" in artist, "top_artists item should have 'id'"
                assert "streams" in artist, "top_artists item should have 'streams'"
                assert "revenue" in artist, "top_artists item should have 'revenue'"
                assert "releases" in artist, "top_artists item should have 'releases'"
            print(f"✓ top_artists structure verified ({len(data['top_artists'])} artists)")
        else:
            print("✓ top_artists is empty (no data yet)")
    
    def test_recent_releases_structure(self):
        """Verify recent_releases items have correct structure"""
        resp = self.session.get(f"{BASE_URL}/api/label/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        
        if data["recent_releases"]:
            for release in data["recent_releases"]:
                assert "id" in release, "recent_releases item should have 'id'"
                assert "title" in release, "recent_releases item should have 'title'"
                assert "artist_name" in release, "recent_releases item should have 'artist_name'"
                assert "status" in release, "recent_releases item should have 'status'"
            print(f"✓ recent_releases structure verified ({len(data['recent_releases'])} releases)")
        else:
            print("✓ recent_releases is empty (no data yet)")
    
    def test_artist_stats_in_roster(self):
        """Verify artist stats (streams, revenue, releases) are returned correctly"""
        resp = self.session.get(f"{BASE_URL}/api/label/artists")
        assert resp.status_code == 200
        data = resp.json()
        
        if data["artists"]:
            for artist in data["artists"]:
                assert isinstance(artist.get("streams", 0), int), "streams should be int"
                assert isinstance(artist.get("revenue", 0), (int, float)), "revenue should be numeric"
                assert isinstance(artist.get("releases", 0), int), "releases should be int"
            print(f"✓ Artist stats verified for {len(data['artists'])} artists")
        else:
            print("✓ No artists on roster to verify stats")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
