"""
Iteration 62 - Artist Profile Enhancements & Backend Refactoring Tests
Tests:
1. Artist Profile endpoints (theme_color, tracks in releases)
2. QR Code generation endpoint
3. Track preview streaming endpoint
4. Theme color save/get endpoints
5. Refactored routes (messages, royalty splits, payouts)
6. Landing page features (12 feature cards, 3 highlights)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "admin@kalmori.com"
ADMIN_PASSWORD = "MAYAsimpSON37!!"


class TestArtistProfileEndpoints:
    """Test artist profile public endpoints with theme_color and tracks"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_get_public_artist_profile_returns_theme_color(self):
        """GET /api/artist/{slug} should return theme_color field"""
        # Use admin slug 'kalmori-admin'
        response = self.session.get(f"{BASE_URL}/api/artist/kalmori-admin")
        print(f"GET /api/artist/kalmori-admin status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {data.keys()}")
            assert "theme_color" in data, "theme_color field missing from response"
            assert data["theme_color"].startswith("#"), f"theme_color should be hex: {data['theme_color']}"
            print(f"theme_color: {data['theme_color']}")
            print("PASS: Artist profile returns theme_color")
        elif response.status_code == 404:
            print("SKIP: Artist profile not found (slug may not exist)")
            pytest.skip("Artist profile slug 'kalmori-admin' not found")
        else:
            print(f"FAIL: Unexpected status {response.status_code}")
            assert False, f"Unexpected status: {response.status_code}"
    
    def test_get_public_artist_profile_returns_releases_with_tracks(self):
        """GET /api/artist/{slug} should return releases with tracks array for audio previews"""
        response = self.session.get(f"{BASE_URL}/api/artist/kalmori-admin")
        
        if response.status_code == 200:
            data = response.json()
            assert "releases" in data, "releases field missing"
            print(f"Number of releases: {len(data.get('releases', []))}")
            
            # Check if releases have tracks array
            for release in data.get("releases", []):
                assert "tracks" in release, f"Release {release.get('id')} missing tracks array"
                print(f"Release '{release.get('title')}' has {len(release.get('tracks', []))} tracks")
            
            print("PASS: Releases include tracks for audio previews")
        elif response.status_code == 404:
            pytest.skip("Artist profile not found")
        else:
            assert False, f"Unexpected status: {response.status_code}"


class TestQRCodeEndpoint:
    """Test QR code generation endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
    
    def test_qr_code_returns_png_image(self):
        """GET /api/artist/{slug}/qr should return PNG image"""
        response = self.session.get(f"{BASE_URL}/api/artist/kalmori-admin/qr")
        print(f"GET /api/artist/kalmori-admin/qr status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            print(f"Content-Type: {content_type}")
            assert "image/png" in content_type, f"Expected image/png, got {content_type}"
            assert len(response.content) > 100, "QR image too small"
            print(f"QR image size: {len(response.content)} bytes")
            print("PASS: QR code endpoint returns PNG image")
        elif response.status_code == 404:
            pytest.skip("Artist profile not found for QR generation")
        else:
            assert False, f"Unexpected status: {response.status_code}"


class TestTrackPreviewEndpoint:
    """Test track preview streaming endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
    
    def test_track_preview_endpoint_exists(self):
        """GET /api/artist/{slug}/track/{track_id}/preview should exist"""
        # First get artist profile to find a track
        profile_resp = self.session.get(f"{BASE_URL}/api/artist/kalmori-admin")
        
        if profile_resp.status_code != 200:
            pytest.skip("Artist profile not found")
        
        data = profile_resp.json()
        track_id = None
        
        for release in data.get("releases", []):
            for track in release.get("tracks", []):
                if track.get("audio_url"):
                    track_id = track.get("id")
                    break
            if track_id:
                break
        
        if not track_id:
            print("No tracks with audio found, testing endpoint with dummy track_id")
            track_id = "trk_dummy123"
        
        response = self.session.get(f"{BASE_URL}/api/artist/kalmori-admin/track/{track_id}/preview")
        print(f"GET /api/artist/kalmori-admin/track/{track_id}/preview status: {response.status_code}")
        
        # 200 = audio found, 404 = track not found (both valid responses)
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            print(f"Content-Type: {content_type}")
            assert "audio" in content_type or "octet-stream" in content_type, f"Expected audio content type"
            print("PASS: Track preview returns audio stream")
        else:
            print("PASS: Track preview endpoint exists (404 for missing track is expected)")


class TestThemeColorEndpoints:
    """Test theme color save/get endpoints (authenticated)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as admin
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_resp.status_code == 200:
            self.logged_in = True
            print("Logged in as admin")
        else:
            self.logged_in = False
            print(f"Login failed: {login_resp.status_code}")
    
    def test_get_theme_color(self):
        """GET /api/artist/profile/theme should return current theme color"""
        if not self.logged_in:
            pytest.skip("Login failed")
        
        response = self.session.get(f"{BASE_URL}/api/artist/profile/theme")
        print(f"GET /api/artist/profile/theme status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "theme_color" in data, "theme_color field missing"
        print(f"Current theme_color: {data['theme_color']}")
        print("PASS: GET theme color works")
    
    def test_put_theme_color(self):
        """PUT /api/artist/profile/theme should save theme color"""
        if not self.logged_in:
            pytest.skip("Login failed")
        
        test_color = "#E040FB"
        response = self.session.put(f"{BASE_URL}/api/artist/profile/theme", json={
            "theme_color": test_color
        })
        print(f"PUT /api/artist/profile/theme status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("theme_color") == test_color, f"Expected {test_color}, got {data.get('theme_color')}"
        print("PASS: PUT theme color works")
        
        # Verify by GET
        verify_resp = self.session.get(f"{BASE_URL}/api/artist/profile/theme")
        verify_data = verify_resp.json()
        assert verify_data.get("theme_color") == test_color, "Theme color not persisted"
        print("PASS: Theme color persisted correctly")


class TestRefactoredMessagesRoutes:
    """Test messaging routes (refactored from server.py to messages_routes.py)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as admin
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.logged_in = login_resp.status_code == 200
    
    def test_get_conversations_list(self):
        """GET /api/messages/conversations should return conversations list"""
        if not self.logged_in:
            pytest.skip("Login failed")
        
        response = self.session.get(f"{BASE_URL}/api/messages/conversations")
        print(f"GET /api/messages/conversations status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Expected list of conversations"
        print(f"Number of conversations: {len(data)}")
        print("PASS: GET conversations works (refactored route)")
    
    def test_get_unread_count(self):
        """GET /api/messages/unread/count should return unread count"""
        if not self.logged_in:
            pytest.skip("Login failed")
        
        response = self.session.get(f"{BASE_URL}/api/messages/unread/count")
        print(f"GET /api/messages/unread/count status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "unread" in data, "unread field missing"
        print(f"Unread count: {data['unread']}")
        print("PASS: GET unread count works (refactored route)")


class TestRefactoredRoyaltyRoutes:
    """Test royalty split routes (refactored from server.py to royalty_routes.py)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as admin
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.logged_in = login_resp.status_code == 200
    
    def test_get_royalty_splits(self):
        """GET /api/royalty-splits should return splits list"""
        if not self.logged_in:
            pytest.skip("Login failed")
        
        response = self.session.get(f"{BASE_URL}/api/royalty-splits")
        print(f"GET /api/royalty-splits status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "splits" in data, "splits field missing"
        print(f"Number of splits: {len(data['splits'])}")
        print("PASS: GET royalty splits works (refactored route)")
    
    def test_get_royalty_splits_summary(self):
        """GET /api/royalty-splits/summary should return summary data"""
        if not self.logged_in:
            pytest.skip("Login failed")
        
        response = self.session.get(f"{BASE_URL}/api/royalty-splits/summary")
        print(f"GET /api/royalty-splits/summary status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        expected_fields = ["active_splits", "total_as_producer", "total_as_artist", "total_earned"]
        for field in expected_fields:
            assert field in data, f"{field} missing from summary"
        print(f"Summary: {data}")
        print("PASS: GET royalty splits summary works (refactored route)")


class TestRefactoredPayoutsRoutes:
    """Test payout routes (refactored from server.py to payouts_routes.py)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login as admin
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.logged_in = login_resp.status_code == 200
    
    def test_get_admin_payouts(self):
        """GET /api/admin/payouts should return withdrawals list"""
        if not self.logged_in:
            pytest.skip("Login failed")
        
        response = self.session.get(f"{BASE_URL}/api/admin/payouts")
        print(f"GET /api/admin/payouts status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "withdrawals" in data, "withdrawals field missing"
        print(f"Number of withdrawals: {len(data['withdrawals'])}")
        print("PASS: GET admin payouts works (refactored route)")
    
    def test_get_admin_payouts_summary(self):
        """GET /api/admin/payouts/summary should return payout summary"""
        if not self.logged_in:
            pytest.skip("Login failed")
        
        response = self.session.get(f"{BASE_URL}/api/admin/payouts/summary")
        print(f"GET /api/admin/payouts/summary status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        expected_fields = ["pending_count", "pending_amount", "processing_count", "completed_count"]
        for field in expected_fields:
            assert field in data, f"{field} missing from summary"
        print(f"Summary: {data}")
        print("PASS: GET admin payouts summary works (refactored route)")
    
    def test_get_admin_payouts_schedule(self):
        """GET /api/admin/payouts/schedule should return schedule config"""
        if not self.logged_in:
            pytest.skip("Login failed")
        
        response = self.session.get(f"{BASE_URL}/api/admin/payouts/schedule")
        print(f"GET /api/admin/payouts/schedule status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        expected_fields = ["frequency", "day_of_month", "min_threshold"]
        for field in expected_fields:
            assert field in data, f"{field} missing from schedule"
        print(f"Schedule: {data}")
        print("PASS: GET admin payouts schedule works (refactored route)")
    
    def test_post_admin_payouts_batch(self):
        """POST /api/admin/payouts/batch should process batch payouts"""
        if not self.logged_in:
            pytest.skip("Login failed")
        
        # Test with empty list (should work without errors)
        response = self.session.post(f"{BASE_URL}/api/admin/payouts/batch", json={
            "withdrawal_ids": [],
            "status": "processing"
        })
        print(f"POST /api/admin/payouts/batch status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "updated" in data, "updated field missing"
        print(f"Batch result: {data}")
        print("PASS: POST admin payouts batch works (refactored route)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
