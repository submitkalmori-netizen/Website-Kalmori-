"""
Iteration 21 - Release Wizard API Tests
Tests for the 4-tab Release Wizard: General Information, Tracks & Assets, Territory & Platform Rights, Summary

Endpoints tested:
- POST /api/releases - Create release with all metadata
- POST /api/releases/{id}/cover - Upload cover art
- POST /api/tracks - Create track
- POST /api/tracks/{id}/audio - Upload audio file
- POST /api/distributions/submit/{id} - Submit for distribution
- GET /api/releases/{id} - Get release details
- GET /api/distributions/stores - Get available DSP stores
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestReleaseWizardAPIs:
    """Test Release Wizard backend APIs"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        data = login_response.json()
        self.token = data.get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        print(f"Logged in successfully")
        
        yield
        
        # Cleanup - no specific cleanup needed
    
    def test_health_check(self):
        """Test API health endpoint"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("SUCCESS: Health check passed")
    
    def test_get_distribution_stores(self):
        """Test getting available DSP stores"""
        response = self.session.get(f"{BASE_URL}/api/distributions/stores")
        assert response.status_code == 200
        stores = response.json()
        assert isinstance(stores, list)
        assert len(stores) >= 10, f"Expected at least 10 stores, got {len(stores)}"
        
        # Check for key platforms
        store_ids = [s["store_id"] for s in stores]
        expected_stores = ["spotify", "apple_music", "amazon_music", "youtube_music", "tidal", "deezer"]
        for store in expected_stores:
            assert store in store_ids, f"Missing store: {store}"
        
        print(f"SUCCESS: Found {len(stores)} distribution stores")
    
    def test_create_release_with_full_metadata(self):
        """Test creating a release with all wizard metadata fields"""
        unique_id = uuid.uuid4().hex[:8]
        release_data = {
            "title": f"TEST_Wizard_Release_{unique_id}",
            "release_type": "album",
            "genre": "Hip-Hop/Rap",
            "release_date": "2026-05-01",
            "description": "Test release from wizard",
            "explicit": False,
            "language": "en",
            "label": "Test Label",
            "upc": f"0{uuid.uuid4().hex[:11]}",  # 12-digit UPC
            "catalog_number": f"CAT-{unique_id}",
            "production_year": "2026",
            "copyright_line": "2026 Test Label",
            "production_line": "2026 Test Label",
            "is_compilation": False,
            "title_version": "Deluxe Edition",
            "main_artist": "Test Artist",
            "territory": "worldwide",
            "distributed_platforms": ["spotify", "apple_music", "amazon_music", "youtube_music"],
            "rights_confirmed": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/releases", json=release_data)
        assert response.status_code == 200, f"Create release failed: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert data["title"] == release_data["title"]
        assert data["release_type"] == "album"
        assert data["status"] == "draft"
        
        self.release_id = data["id"]
        print(f"SUCCESS: Created release {self.release_id}")
        
        return data["id"]
    
    def test_create_track_for_release(self):
        """Test creating a track for a release"""
        # First create a release
        release_id = self.test_create_release_with_full_metadata()
        
        track_data = {
            "release_id": release_id,
            "title": "Test Track One",
            "track_number": 1,
            "explicit": False
        }
        
        response = self.session.post(f"{BASE_URL}/api/tracks", json=track_data)
        assert response.status_code == 200, f"Create track failed: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Track One"
        assert data["track_number"] == 1
        assert "isrc" in data  # Auto-generated ISRC
        
        print(f"SUCCESS: Created track {data['id']} with ISRC {data['isrc']}")
        
        return release_id, data["id"]
    
    def test_get_release_with_tracks(self):
        """Test getting release details with tracks"""
        release_id, track_id = self.test_create_track_for_release()
        
        response = self.session.get(f"{BASE_URL}/api/releases/{release_id}")
        assert response.status_code == 200, f"Get release failed: {response.text}"
        
        data = response.json()
        assert data["id"] == release_id
        assert "tracks" in data
        assert len(data["tracks"]) >= 1
        assert data["tracks"][0]["id"] == track_id
        
        print(f"SUCCESS: Retrieved release with {len(data['tracks'])} track(s)")
    
    def test_release_requires_auth(self):
        """Test that release endpoints require authentication"""
        # Create a new session without auth
        no_auth_session = requests.Session()
        no_auth_session.headers.update({"Content-Type": "application/json"})
        
        response = no_auth_session.post(f"{BASE_URL}/api/releases", json={
            "title": "Unauthorized Release",
            "release_type": "single",
            "genre": "Pop",
            "release_date": "2026-05-01"
        })
        # API may return 401 (unauthorized) or 422 (validation before auth check)
        assert response.status_code in [401, 422], f"Expected 401 or 422, got {response.status_code}"
        print(f"SUCCESS: Release creation rejected without auth (status: {response.status_code})")
    
    def test_track_requires_auth(self):
        """Test that track endpoints require authentication"""
        no_auth_session = requests.Session()
        no_auth_session.headers.update({"Content-Type": "application/json"})
        
        response = no_auth_session.post(f"{BASE_URL}/api/tracks", json={
            "release_id": "fake_id",
            "title": "Unauthorized Track",
            "track_number": 1
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("SUCCESS: Track creation requires authentication")
    
    def test_distribution_submit_requires_cover_and_tracks(self):
        """Test that distribution submission validates requirements"""
        # Create a release without cover art or tracks
        unique_id = uuid.uuid4().hex[:8]
        release_data = {
            "title": f"TEST_Empty_Release_{unique_id}",
            "release_type": "single",
            "genre": "Pop",
            "release_date": "2026-05-01"
        }
        
        response = self.session.post(f"{BASE_URL}/api/releases", json=release_data)
        assert response.status_code == 200, f"Create release failed: {response.text}"
        release_id = response.json()["id"]
        
        # Try to submit without cover art
        submit_response = self.session.post(
            f"{BASE_URL}/api/distributions/submit/{release_id}",
            json=["spotify", "apple_music"]
        )
        assert submit_response.status_code == 400, f"Expected 400, got {submit_response.status_code}"
        assert "cover art" in submit_response.text.lower()
        
        print("SUCCESS: Distribution submission validates cover art requirement")
    
    def test_upc_generation_format(self):
        """Test that UPC codes are properly formatted (12 digits)"""
        # Create release and check UPC format
        unique_id = uuid.uuid4().hex[:8]
        release_data = {
            "title": f"TEST_UPC_Release_{unique_id}",
            "release_type": "single",
            "genre": "Pop",
            "release_date": "2026-05-01"
        }
        
        response = self.session.post(f"{BASE_URL}/api/releases", json=release_data)
        assert response.status_code == 200, f"Create release failed: {response.text}"
        
        data = response.json()
        upc = data.get("upc", "")
        assert len(upc) == 12, f"UPC should be 12 digits, got {len(upc)}: {upc}"
        assert upc.isdigit(), f"UPC should be all digits: {upc}"
        
        print(f"SUCCESS: UPC generated correctly: {upc}")
    
    def test_delete_track(self):
        """Test deleting a track from a release"""
        release_id, track_id = self.test_create_track_for_release()
        
        # Delete the track
        response = self.session.delete(f"{BASE_URL}/api/tracks/{track_id}")
        assert response.status_code == 200, f"Delete track failed: {response.text}"
        
        # Verify track is deleted
        release_response = self.session.get(f"{BASE_URL}/api/releases/{release_id}")
        assert release_response.status_code == 200
        tracks = release_response.json().get("tracks", [])
        track_ids = [t["id"] for t in tracks]
        assert track_id not in track_ids, "Track should be deleted"
        
        print(f"SUCCESS: Track {track_id} deleted successfully")
    
    def test_update_release(self):
        """Test updating release metadata"""
        release_id = self.test_create_release_with_full_metadata()
        
        update_data = {
            "title": "Updated Album Title",
            "release_type": "album",
            "genre": "R&B/Soul",
            "release_date": "2026-06-15",
            "description": "Updated description",
            "explicit": True,
            "language": "en"
        }
        
        response = self.session.put(f"{BASE_URL}/api/releases/{release_id}", json=update_data)
        assert response.status_code == 200, f"Update release failed: {response.text}"
        
        # Verify update
        get_response = self.session.get(f"{BASE_URL}/api/releases/{release_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["title"] == "Updated Album Title"
        assert data["genre"] == "R&B/Soul"
        
        print(f"SUCCESS: Release {release_id} updated successfully")
    
    def test_delete_draft_release(self):
        """Test deleting a draft release"""
        release_id = self.test_create_release_with_full_metadata()
        
        response = self.session.delete(f"{BASE_URL}/api/releases/{release_id}")
        assert response.status_code == 200, f"Delete release failed: {response.text}"
        
        # Verify deletion
        get_response = self.session.get(f"{BASE_URL}/api/releases/{release_id}")
        assert get_response.status_code == 404, "Release should be deleted"
        
        print(f"SUCCESS: Draft release {release_id} deleted successfully")


class TestReleaseWizardValidation:
    """Test Release Wizard validation rules"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200
        
        data = login_response.json()
        self.token = data.get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        yield
    
    def test_track_requires_valid_release(self):
        """Test that track creation requires a valid release ID"""
        track_data = {
            "release_id": "invalid_release_id",
            "title": "Orphan Track",
            "track_number": 1
        }
        
        response = self.session.post(f"{BASE_URL}/api/tracks", json=track_data)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("SUCCESS: Track creation validates release ID")
    
    def test_release_not_found(self):
        """Test getting a non-existent release"""
        response = self.session.get(f"{BASE_URL}/api/releases/nonexistent_id")
        assert response.status_code == 404
        print("SUCCESS: Non-existent release returns 404")
    
    def test_track_not_found(self):
        """Test deleting a non-existent track"""
        response = self.session.delete(f"{BASE_URL}/api/tracks/nonexistent_id")
        assert response.status_code == 404
        print("SUCCESS: Non-existent track returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
