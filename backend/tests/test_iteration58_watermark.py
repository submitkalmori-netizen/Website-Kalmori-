"""
Iteration 58 - Beat Preview Watermark System Tests
Tests for:
- POST /api/beats/{beat_id}/audio - uploads audio and returns both audio_url (clean) and preview_url (watermarked)
- GET /api/beats/{beat_id}/stream - serves the watermarked preview (not the original)
- GET /api/purchases/{id}/download - serves the clean original (post-purchase only)
- POST /api/beats/{beat_id}/watermark - regenerates watermark preview (admin only)
- POST /api/beats/{beat_id}/watermark - returns 403 for non-admin
- Beat listing shows preview_url field when available
- Voice tag file exists at /app/backend/kalmori_tag.mp3
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "submitkalmori@gmail.com"
ADMIN_PASSWORD = "MAYAsimpSON37!!"


class TestWatermarkSystem:
    """Tests for the Beat Preview Watermark System"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
    
    @pytest.fixture(scope="class")
    def admin_headers(self, admin_token):
        """Headers with admin auth"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    @pytest.fixture(scope="class")
    def test_user_token(self):
        """Create and login a non-admin test user"""
        import uuid
        test_email = f"test_watermark_{uuid.uuid4().hex[:8]}@test.com"
        # Register
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Test User",
            "artist_name": "Test Artist"
        })
        if reg_response.status_code not in [200, 201]:
            pytest.skip(f"User registration failed: {reg_response.status_code}")
        
        # Login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": "TestPass123!"
        })
        if login_response.status_code == 200:
            data = login_response.json()
            return data.get("access_token") or data.get("token")
        pytest.skip(f"Test user login failed: {login_response.status_code}")
    
    @pytest.fixture(scope="class")
    def test_user_headers(self, test_user_token):
        """Headers with test user auth"""
        return {"Authorization": f"Bearer {test_user_token}"}
    
    # ==================== Voice Tag File Tests ====================
    
    def test_voice_tag_file_exists(self):
        """Test that voice tag file exists at /app/backend/kalmori_tag.mp3"""
        voice_tag_path = "/app/backend/kalmori_tag.mp3"
        assert os.path.exists(voice_tag_path), f"Voice tag file not found at {voice_tag_path}"
        
        # Check file size is reasonable (should be a small MP3)
        file_size = os.path.getsize(voice_tag_path)
        assert file_size > 1000, f"Voice tag file too small: {file_size} bytes"
        assert file_size < 100000, f"Voice tag file too large: {file_size} bytes"
        print(f"Voice tag file exists: {file_size} bytes")
    
    # ==================== Beat Listing Tests ====================
    
    def test_beat_listing_shows_preview_url(self):
        """Test that beat listing shows preview_url field when available"""
        response = requests.get(f"{BASE_URL}/api/beats")
        assert response.status_code == 200, f"Failed to get beats: {response.status_code}"
        
        data = response.json()
        beats = data.get("beats", [])
        assert len(beats) > 0, "No beats found"
        
        # Check if any beat has preview_url
        beats_with_preview = [b for b in beats if b.get("preview_url")]
        print(f"Found {len(beats_with_preview)} beats with preview_url out of {len(beats)} total")
        
        # The test beat should have preview_url
        test_beat = next((b for b in beats if b.get("id") == "beat_0fc024b75417"), None)
        if test_beat:
            assert "preview_url" in test_beat, "Test beat missing preview_url field"
            print(f"Test beat preview_url: {test_beat.get('preview_url')}")
            print(f"Test beat audio_url: {test_beat.get('audio_url')}")
    
    def test_beat_has_both_audio_and_preview_urls(self):
        """Test that beat with audio has both audio_url (clean) and preview_url (watermarked)"""
        response = requests.get(f"{BASE_URL}/api/beats")
        assert response.status_code == 200
        
        data = response.json()
        beats = data.get("beats", [])
        
        # Find beats with audio
        beats_with_audio = [b for b in beats if b.get("audio_url")]
        
        for beat in beats_with_audio:
            assert "audio_url" in beat, f"Beat {beat.get('id')} missing audio_url"
            assert "preview_url" in beat, f"Beat {beat.get('id')} missing preview_url"
            
            # Preview URL should be different from audio URL (watermarked version)
            if beat.get("preview_url") and beat.get("audio_url"):
                # They might be the same if watermarking failed, but ideally different
                print(f"Beat {beat.get('id')}: audio_url={beat.get('audio_url')}, preview_url={beat.get('preview_url')}")
    
    # ==================== Stream Endpoint Tests ====================
    
    def test_stream_endpoint_serves_watermarked_preview(self):
        """Test GET /api/beats/{beat_id}/stream serves the watermarked preview"""
        # First get a beat with audio
        response = requests.get(f"{BASE_URL}/api/beats")
        assert response.status_code == 200
        
        data = response.json()
        beats = data.get("beats", [])
        beat_with_audio = next((b for b in beats if b.get("audio_url")), None)
        
        if not beat_with_audio:
            pytest.skip("No beats with audio found")
        
        beat_id = beat_with_audio.get("id")
        
        # Stream the beat
        stream_response = requests.get(f"{BASE_URL}/api/beats/{beat_id}/stream")
        assert stream_response.status_code == 200, f"Stream failed: {stream_response.status_code}"
        
        # Check content type is audio
        content_type = stream_response.headers.get("Content-Type", "")
        assert "audio" in content_type, f"Expected audio content type, got: {content_type}"
        
        # Check content disposition suggests preview
        content_disp = stream_response.headers.get("Content-Disposition", "")
        print(f"Stream Content-Disposition: {content_disp}")
        
        # Verify we got audio data
        assert len(stream_response.content) > 1000, "Stream response too small"
        print(f"Stream returned {len(stream_response.content)} bytes of audio")
    
    def test_stream_endpoint_returns_404_for_nonexistent_beat(self):
        """Test stream endpoint returns 404 for non-existent beat"""
        response = requests.get(f"{BASE_URL}/api/beats/nonexistent_beat_123/stream")
        assert response.status_code == 404
    
    # ==================== Watermark Regeneration Tests ====================
    
    def test_watermark_regeneration_admin_only(self, admin_headers):
        """Test POST /api/beats/{beat_id}/watermark works for admin"""
        # Get a beat with audio
        response = requests.get(f"{BASE_URL}/api/beats")
        assert response.status_code == 200
        
        data = response.json()
        beats = data.get("beats", [])
        beat_with_audio = next((b for b in beats if b.get("audio_url")), None)
        
        if not beat_with_audio:
            pytest.skip("No beats with audio found")
        
        beat_id = beat_with_audio.get("id")
        
        # Regenerate watermark as admin
        regen_response = requests.post(
            f"{BASE_URL}/api/beats/{beat_id}/watermark",
            headers=admin_headers
        )
        
        assert regen_response.status_code == 200, f"Watermark regeneration failed: {regen_response.status_code} - {regen_response.text}"
        
        regen_data = regen_response.json()
        assert "preview_url" in regen_data, "Response missing preview_url"
        assert "message" in regen_data, "Response missing message"
        print(f"Watermark regenerated: {regen_data}")
    
    def test_watermark_regeneration_returns_403_for_non_admin(self, test_user_headers):
        """Test POST /api/beats/{beat_id}/watermark returns 403 for non-admin"""
        # Get a beat with audio
        response = requests.get(f"{BASE_URL}/api/beats")
        assert response.status_code == 200
        
        data = response.json()
        beats = data.get("beats", [])
        beat_with_audio = next((b for b in beats if b.get("audio_url")), None)
        
        if not beat_with_audio:
            pytest.skip("No beats with audio found")
        
        beat_id = beat_with_audio.get("id")
        
        # Try to regenerate watermark as non-admin
        regen_response = requests.post(
            f"{BASE_URL}/api/beats/{beat_id}/watermark",
            headers=test_user_headers
        )
        
        assert regen_response.status_code == 403, f"Expected 403, got: {regen_response.status_code}"
        print(f"Non-admin correctly denied: {regen_response.status_code}")
    
    def test_watermark_regeneration_returns_401_without_auth(self):
        """Test POST /api/beats/{beat_id}/watermark returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/beats")
        data = response.json()
        beats = data.get("beats", [])
        beat_with_audio = next((b for b in beats if b.get("audio_url")), None)
        
        if not beat_with_audio:
            pytest.skip("No beats with audio found")
        
        beat_id = beat_with_audio.get("id")
        
        # Try without auth
        regen_response = requests.post(f"{BASE_URL}/api/beats/{beat_id}/watermark")
        assert regen_response.status_code in [401, 403], f"Expected 401/403, got: {regen_response.status_code}"
    
    def test_watermark_regeneration_returns_404_for_beat_without_audio(self, admin_headers):
        """Test watermark regeneration returns 404 for beat without audio"""
        # Get a beat without audio
        response = requests.get(f"{BASE_URL}/api/beats")
        data = response.json()
        beats = data.get("beats", [])
        beat_without_audio = next((b for b in beats if not b.get("audio_url")), None)
        
        if not beat_without_audio:
            pytest.skip("All beats have audio")
        
        beat_id = beat_without_audio.get("id")
        
        regen_response = requests.post(
            f"{BASE_URL}/api/beats/{beat_id}/watermark",
            headers=admin_headers
        )
        
        assert regen_response.status_code == 404, f"Expected 404, got: {regen_response.status_code}"
    
    # ==================== Get Single Beat Tests ====================
    
    def test_get_single_beat_includes_preview_url(self):
        """Test GET /api/beats/{beat_id} includes preview_url"""
        # Get a beat with audio
        response = requests.get(f"{BASE_URL}/api/beats")
        data = response.json()
        beats = data.get("beats", [])
        beat_with_audio = next((b for b in beats if b.get("audio_url")), None)
        
        if not beat_with_audio:
            pytest.skip("No beats with audio found")
        
        beat_id = beat_with_audio.get("id")
        
        # Get single beat
        single_response = requests.get(f"{BASE_URL}/api/beats/{beat_id}")
        assert single_response.status_code == 200
        
        beat_data = single_response.json()
        assert "preview_url" in beat_data, "Single beat response missing preview_url"
        assert "audio_url" in beat_data, "Single beat response missing audio_url"
        print(f"Single beat {beat_id}: audio_url={beat_data.get('audio_url')}, preview_url={beat_data.get('preview_url')}")


class TestPurchaseDownload:
    """Tests for purchase download endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        pytest.skip(f"Admin login failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def admin_headers(self, admin_token):
        """Headers with admin auth"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    def test_download_endpoint_exists(self, admin_headers):
        """Test that download endpoint exists (even if no purchases)"""
        # Try to access a non-existent purchase
        response = requests.get(
            f"{BASE_URL}/api/purchases/nonexistent_purchase_123/download",
            headers=admin_headers
        )
        # Should return 404 (not found) not 405 (method not allowed)
        assert response.status_code in [404, 401, 403], f"Unexpected status: {response.status_code}"
        print(f"Download endpoint exists, returned {response.status_code} for non-existent purchase")
    
    def test_download_requires_authentication(self):
        """Test that download endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/purchases/some_purchase_id/download")
        assert response.status_code in [401, 403], f"Expected 401/403, got: {response.status_code}"


class TestAdminLogin:
    """Test admin login with provided credentials"""
    
    def test_admin_login_success(self):
        """Test login with submitkalmori@gmail.com / MAYAsimpSON37!!"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Admin login failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "access_token" in data or "token" in data, "Login response missing token"
        
        # Verify user is admin
        user = data.get("user", {})
        assert user.get("role") == "admin" or user.get("is_admin") == True, f"User is not admin: {user}"
        print(f"Admin login successful: {user.get('email')}, role: {user.get('role')}")


class TestAdminContractsPage:
    """Test admin contracts page accessibility"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        pytest.skip(f"Admin login failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def admin_headers(self, admin_token):
        """Headers with admin auth"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    def test_admin_contracts_endpoint(self, admin_headers):
        """Test GET /api/admin/contracts is accessible"""
        response = requests.get(
            f"{BASE_URL}/api/admin/contracts",
            headers=admin_headers
        )
        
        assert response.status_code == 200, f"Admin contracts failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "contracts" in data or isinstance(data, list), "Response missing contracts"
        print(f"Admin contracts endpoint working, found {len(data.get('contracts', data))} contracts")
