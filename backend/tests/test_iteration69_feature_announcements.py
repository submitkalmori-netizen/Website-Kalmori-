"""
Iteration 69 - Testing Feature Announcements and Analytics Cleanup
Tests:
1. Analytics endpoints return real data only (zeros when no stream data)
2. CSV import is admin-only (403 for non-admin)
3. Admin Feature Announcements CRUD (GET, POST, DELETE)
4. Frontend: Admin Feature Announcements page loads and works
5. Frontend: Import CSV button visibility based on user role
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@kalmori.com"
ADMIN_PASSWORD = "Admin123!"
SECONDARY_ADMIN_EMAIL = "submitkalmori@gmail.com"


class TestAnalyticsRealDataOnly:
    """Verify analytics endpoints return real data only (zeros when no stream data)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a fresh test user for each test"""
        self.session = requests.Session()
        self.test_email = f"test_analytics_{uuid.uuid4().hex[:8]}@test.com"
        self.test_password = "TestPass123!"
        
        # Register a new test user
        reg_resp = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "name": "Test Analytics User",
            "artist_name": "Test Artist"
        })
        assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
        self.test_user = reg_resp.json().get("user", {})
        yield
        # Cleanup not needed - test user will be cleaned up by admin cleanup endpoint if needed
    
    def test_analytics_overview_returns_zeros_for_new_user(self):
        """GET /api/analytics/overview should return zeros when no stream data exists"""
        resp = self.session.get(f"{BASE_URL}/api/analytics/overview")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        # Verify zeros for new user with no stream data
        assert data.get("total_streams", -1) == 0, f"Expected total_streams=0, got {data.get('total_streams')}"
        assert data.get("total_earnings", -1) == 0 or data.get("total_earnings", -1) == 0.0, f"Expected total_earnings=0, got {data.get('total_earnings')}"
        assert data.get("total_downloads", -1) == 0, f"Expected total_downloads=0, got {data.get('total_downloads')}"
        
        # Verify empty breakdowns
        assert data.get("streams_by_store", {}) == {} or len(data.get("streams_by_store", {})) == 0
        assert data.get("streams_by_country", {}) == {} or len(data.get("streams_by_country", {})) == 0
        assert data.get("daily_streams", []) == [] or len(data.get("daily_streams", [])) == 0
        print("PASS: Analytics overview returns zeros for new user")
    
    def test_analytics_trending_returns_empty_for_new_user(self):
        """GET /api/analytics/trending should return empty trending array when no stream data"""
        resp = self.session.get(f"{BASE_URL}/api/analytics/trending")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        # Trending should be empty or have zero-stream items
        trending = data.get("trending", [])
        for item in trending:
            assert item.get("total_streams", -1) == 0, f"Expected total_streams=0 in trending item, got {item.get('total_streams')}"
        print(f"PASS: Analytics trending returns {len(trending)} items (all with 0 streams)")
    
    def test_analytics_leaderboard_returns_zero_active_releases(self):
        """GET /api/analytics/leaderboard should return 0 active_releases when no stream data"""
        resp = self.session.get(f"{BASE_URL}/api/analytics/leaderboard")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        assert data.get("active_releases", -1) == 0, f"Expected active_releases=0, got {data.get('active_releases')}"
        print("PASS: Analytics leaderboard returns active_releases=0 for new user")
    
    def test_analytics_revenue_returns_zeros(self):
        """GET /api/analytics/revenue should return 0 streams and 0 revenue when no stream data"""
        resp = self.session.get(f"{BASE_URL}/api/analytics/revenue")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        # Revenue endpoint uses nested 'combined' structure
        combined = data.get("combined", {})
        total_streams = combined.get("total_streams", data.get("total_streams", -1))
        total_gross = combined.get("total_gross", data.get("total_gross_revenue", -1))
        total_net = combined.get("total_net", data.get("total_net_revenue", -1))
        
        assert total_streams == 0, f"Expected total_streams=0, got {total_streams}"
        assert total_gross == 0 or total_gross == 0.0, f"Expected total_gross=0, got {total_gross}"
        assert total_net == 0 or total_net == 0.0, f"Expected total_net=0, got {total_net}"
        print("PASS: Analytics revenue returns zeros for new user")


class TestCSVImportAdminOnly:
    """Verify CSV import endpoint is admin-only"""
    
    def test_csv_import_returns_403_for_non_admin(self):
        """POST /api/analytics/import with non-admin should return 403"""
        session = requests.Session()
        
        # Register a non-admin user
        test_email = f"test_nonadmin_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Non Admin User",
            "artist_name": "Non Admin Artist"
        })
        assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
        
        # Try to import CSV as non-admin
        csv_content = "artist,track,platform,streams,revenue\nTest Artist,Test Track,Spotify,100,0.40"
        files = {"file": ("test.csv", csv_content, "text/csv")}
        resp = session.post(f"{BASE_URL}/api/analytics/import", files=files)
        
        assert resp.status_code == 403, f"Expected 403 for non-admin, got {resp.status_code}: {resp.text}"
        assert "admin" in resp.text.lower(), f"Expected admin-related error message, got: {resp.text}"
        print("PASS: CSV import returns 403 for non-admin user")
    
    def test_csv_import_succeeds_for_admin(self):
        """POST /api/analytics/import with admin should succeed"""
        session = requests.Session()
        
        # Login as admin
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        
        # Import CSV as admin
        csv_content = "artist,track,platform,streams,revenue,country,period\nTest Artist,Test Track,Spotify,100,0.40,US,2024-01"
        files = {"file": ("test.csv", csv_content, "text/csv")}
        resp = session.post(f"{BASE_URL}/api/analytics/import", files=files)
        
        assert resp.status_code == 200, f"Expected 200 for admin, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "imported" in data.get("message", "").lower() or data.get("total_rows", 0) > 0
        print(f"PASS: CSV import succeeds for admin - {data.get('message', 'imported')}")


class TestFeatureAnnouncementsCRUD:
    """Test Admin Feature Announcements CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin for all tests"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        yield
    
    def test_list_feature_announcements(self):
        """GET /api/admin/feature-announcements should return list of announcements"""
        resp = self.session.get(f"{BASE_URL}/api/admin/feature-announcements")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        # Should return a list (could be empty)
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"PASS: GET feature-announcements returns list with {len(data)} items")
    
    def test_create_feature_announcement(self):
        """POST /api/admin/feature-announcements should create a new announcement"""
        announcement_data = {
            "title": f"Test Feature {uuid.uuid4().hex[:6]}",
            "description": "This is a test feature announcement for iteration 69 testing",
            "min_plan": "free",
            "category": "general",
            "icon": "Lightning",
            "color": "#7C4DFF"
        }
        
        resp = self.session.post(f"{BASE_URL}/api/admin/feature-announcements", json=announcement_data)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        # Verify response contains announcement and notification count
        assert "announcement" in data, f"Expected 'announcement' in response, got: {data.keys()}"
        assert "notified" in data, f"Expected 'notified' in response, got: {data.keys()}"
        
        announcement = data["announcement"]
        assert announcement.get("title") == announcement_data["title"]
        assert announcement.get("description") == announcement_data["description"]
        assert announcement.get("min_plan") == announcement_data["min_plan"]
        assert announcement.get("id") is not None
        
        # Store for cleanup
        self.created_announcement_id = announcement["id"]
        print(f"PASS: Created feature announcement '{announcement['title']}' - {data['notified']} users notified")
        
        # Cleanup - delete the announcement
        del_resp = self.session.delete(f"{BASE_URL}/api/admin/feature-announcements/{self.created_announcement_id}")
        assert del_resp.status_code == 200, f"Cleanup failed: {del_resp.text}"
    
    def test_create_announcement_with_different_plans(self):
        """Test creating announcements with different min_plan values"""
        for plan in ["free", "rise", "pro"]:
            announcement_data = {
                "title": f"Test {plan.upper()} Feature {uuid.uuid4().hex[:4]}",
                "description": f"Feature for {plan} plan and above",
                "min_plan": plan,
                "category": "distribution",
                "icon": "Rocket",
                "color": "#E040FB"
            }
            
            resp = self.session.post(f"{BASE_URL}/api/admin/feature-announcements", json=announcement_data)
            assert resp.status_code == 200, f"Failed to create {plan} announcement: {resp.text}"
            data = resp.json()
            
            assert data["announcement"]["min_plan"] == plan
            print(f"PASS: Created {plan} plan announcement")
            
            # Cleanup
            self.session.delete(f"{BASE_URL}/api/admin/feature-announcements/{data['announcement']['id']}")
    
    def test_delete_feature_announcement(self):
        """DELETE /api/admin/feature-announcements/{id} should delete an announcement"""
        # First create an announcement
        announcement_data = {
            "title": f"To Delete {uuid.uuid4().hex[:6]}",
            "description": "This announcement will be deleted",
            "min_plan": "free",
            "category": "general",
            "icon": "Trash",
            "color": "#FF3B30"
        }
        
        create_resp = self.session.post(f"{BASE_URL}/api/admin/feature-announcements", json=announcement_data)
        assert create_resp.status_code == 200
        announcement_id = create_resp.json()["announcement"]["id"]
        
        # Delete the announcement
        del_resp = self.session.delete(f"{BASE_URL}/api/admin/feature-announcements/{announcement_id}")
        assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"
        
        # Verify it's deleted by listing
        list_resp = self.session.get(f"{BASE_URL}/api/admin/feature-announcements")
        announcements = list_resp.json()
        assert not any(a["id"] == announcement_id for a in announcements), "Announcement should be deleted"
        print("PASS: Feature announcement deleted successfully")
    
    def test_delete_nonexistent_announcement_returns_404(self):
        """DELETE /api/admin/feature-announcements/{id} with invalid ID should return 404"""
        resp = self.session.delete(f"{BASE_URL}/api/admin/feature-announcements/nonexistent_id_12345")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
        print("PASS: Delete nonexistent announcement returns 404")


class TestFeatureAnnouncementsNonAdmin:
    """Test that non-admin users cannot access feature announcements endpoints"""
    
    def test_non_admin_cannot_list_announcements(self):
        """Non-admin should get 403 when listing feature announcements"""
        session = requests.Session()
        
        # Register a non-admin user
        test_email = f"test_nonadmin_ann_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Non Admin User"
        })
        assert reg_resp.status_code == 200
        
        # Try to list announcements
        resp = session.get(f"{BASE_URL}/api/admin/feature-announcements")
        assert resp.status_code == 403, f"Expected 403 for non-admin, got {resp.status_code}"
        print("PASS: Non-admin cannot list feature announcements (403)")
    
    def test_non_admin_cannot_create_announcement(self):
        """Non-admin should get 403 when creating feature announcement"""
        session = requests.Session()
        
        # Register a non-admin user
        test_email = f"test_nonadmin_create_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Non Admin User"
        })
        assert reg_resp.status_code == 200
        
        # Try to create announcement
        resp = session.post(f"{BASE_URL}/api/admin/feature-announcements", json={
            "title": "Unauthorized Announcement",
            "description": "This should fail",
            "min_plan": "free",
            "category": "general",
            "icon": "Lightning",
            "color": "#7C4DFF"
        })
        assert resp.status_code == 403, f"Expected 403 for non-admin, got {resp.status_code}"
        print("PASS: Non-admin cannot create feature announcement (403)")


class TestAdminLogin:
    """Verify admin login works for both admin accounts"""
    
    def test_admin_login_primary(self):
        """Admin login works for admin@kalmori.com"""
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200, f"Admin login failed: {resp.text}"
        data = resp.json()
        assert data.get("user", {}).get("role") == "admin", f"Expected admin role, got: {data.get('user', {}).get('role')}"
        print("PASS: Admin login works for admin@kalmori.com")
    
    def test_admin_login_secondary(self):
        """Admin login works for submitkalmori@gmail.com"""
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": SECONDARY_ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200, f"Secondary admin login failed: {resp.text}"
        data = resp.json()
        assert data.get("user", {}).get("role") == "admin", f"Expected admin role, got: {data.get('user', {}).get('role')}"
        print("PASS: Admin login works for submitkalmori@gmail.com")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
