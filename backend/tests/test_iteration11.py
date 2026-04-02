"""
Iteration 11 Backend Tests
Tests for:
- Object Storage: POST /api/releases/{id}/cover - upload cover art
- Object Storage: POST /api/tracks/{id}/audio - upload audio file
- Stripe: POST /api/payments/checkout - creates Stripe checkout session
- Stripe: GET /api/payments/status/{session_id} - checks payment status
- POST /api/releases - create release
- GET /api/releases - list releases
"""
import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@tunedrop.com"
TEST_PASSWORD = "Admin123!"


class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health endpoint working")
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        print(f"✓ Login successful for {TEST_EMAIL}")
        return data["access_token"]


class TestReleasesCRUD:
    """Test release creation and listing"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    def test_create_release(self, auth_token):
        """POST /api/releases - create release"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "title": "TEST_Iteration11_Release",
            "release_type": "single",
            "genre": "Pop",
            "release_date": "2026-02-01",
            "description": "Test release for iteration 11",
            "explicit": False,
            "language": "en"
        }
        response = requests.post(f"{BASE_URL}/api/releases", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == payload["title"]
        assert data["status"] == "draft"
        assert "upc" in data
        print(f"✓ Release created: {data['id']}")
        return data["id"]
    
    def test_list_releases(self, auth_token):
        """GET /api/releases - list releases"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/releases", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Listed {len(data)} releases")


class TestObjectStorage:
    """Test Object Storage endpoints for cover art and audio uploads"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    @pytest.fixture
    def test_release(self, auth_token):
        """Create a test release for upload tests"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "title": "TEST_Upload_Release",
            "release_type": "single",
            "genre": "Electronic",
            "release_date": "2026-02-15",
            "explicit": False,
            "language": "en"
        }
        response = requests.post(f"{BASE_URL}/api/releases", json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        pytest.skip("Failed to create test release")
    
    def test_upload_cover_art(self, auth_token, test_release):
        """POST /api/releases/{id}/cover - upload cover art"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        release_id = test_release["id"]
        
        # Create a simple test image (1x1 pixel PNG)
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
            0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
            0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND chunk
            0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        
        files = {"file": ("test_cover.png", io.BytesIO(png_data), "image/png")}
        response = requests.post(
            f"{BASE_URL}/api/releases/{release_id}/cover",
            headers=headers,
            files=files
        )
        assert response.status_code == 200
        data = response.json()
        assert "cover_art_url" in data
        print(f"✓ Cover art uploaded: {data['cover_art_url']}")
    
    def test_upload_audio_requires_track(self, auth_token):
        """POST /api/tracks/{id}/audio - requires valid track"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Try to upload to non-existent track
        wav_header = bytes([
            0x52, 0x49, 0x46, 0x46,  # RIFF
            0x24, 0x00, 0x00, 0x00,  # File size
            0x57, 0x41, 0x56, 0x45,  # WAVE
            0x66, 0x6D, 0x74, 0x20,  # fmt
            0x10, 0x00, 0x00, 0x00,  # Subchunk1Size
            0x01, 0x00, 0x02, 0x00,  # AudioFormat, NumChannels
            0x44, 0xAC, 0x00, 0x00,  # SampleRate (44100)
            0x10, 0xB1, 0x02, 0x00,  # ByteRate
            0x04, 0x00, 0x10, 0x00,  # BlockAlign, BitsPerSample
            0x64, 0x61, 0x74, 0x61,  # data
            0x00, 0x00, 0x00, 0x00   # Subchunk2Size
        ])
        
        files = {"file": ("test.wav", io.BytesIO(wav_header), "audio/wav")}
        response = requests.post(
            f"{BASE_URL}/api/tracks/nonexistent_track/audio",
            headers=headers,
            files=files
        )
        assert response.status_code == 404
        print("✓ Audio upload correctly rejects non-existent track")


class TestStripePayments:
    """Test Stripe payment endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    @pytest.fixture
    def test_release(self, auth_token):
        """Create a test release for payment tests"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {
            "title": "TEST_Payment_Release",
            "release_type": "single",
            "genre": "Rock",
            "release_date": "2026-03-01",
            "explicit": False,
            "language": "en"
        }
        response = requests.post(f"{BASE_URL}/api/releases", json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        pytest.skip("Failed to create test release")
    
    def test_create_checkout_session(self, auth_token, test_release):
        """POST /api/payments/checkout - creates Stripe checkout session"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        release_id = test_release["id"]
        
        payload = {
            "release_id": release_id,
            "origin_url": "https://artist-hub-219.preview.emergentagent.com"
        }
        response = requests.post(f"{BASE_URL}/api/payments/checkout", json=payload, headers=headers)
        
        # Admin user is on 'pro' plan, so checkout should work
        # Free plan users get free_tier activation instead
        if response.status_code == 200:
            data = response.json()
            # Either checkout_url (paid plan) or message (free tier)
            if "checkout_url" in data:
                assert "session_id" in data
                print(f"✓ Stripe checkout session created: {data['session_id']}")
                return data["session_id"]
            elif "message" in data:
                assert data["message"] == "Free tier activated"
                print("✓ Free tier activated (no payment needed)")
        else:
            # Log the error for debugging
            print(f"Checkout response: {response.status_code} - {response.text}")
            assert response.status_code == 200
    
    def test_check_payment_status_invalid_session(self, auth_token):
        """GET /api/payments/status/{session_id} - checks payment status"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test with invalid session ID
        response = requests.get(
            f"{BASE_URL}/api/payments/status/invalid_session_id",
            headers=headers
        )
        # Should return error for invalid session
        assert response.status_code in [400, 404, 500]
        print("✓ Payment status correctly handles invalid session")


class TestAuthenticationRequired:
    """Test that endpoints require authentication"""
    
    def test_releases_requires_auth(self):
        """GET /api/releases requires authentication"""
        response = requests.get(f"{BASE_URL}/api/releases")
        assert response.status_code == 401
        print("✓ Releases endpoint requires authentication")
    
    def test_checkout_requires_auth(self):
        """POST /api/payments/checkout requires authentication"""
        response = requests.post(f"{BASE_URL}/api/payments/checkout", json={
            "release_id": "test",
            "origin_url": "https://example.com"
        })
        assert response.status_code == 401
        print("✓ Checkout endpoint requires authentication")
    
    def test_cover_upload_requires_auth(self):
        """POST /api/releases/{id}/cover requires authentication"""
        # Create a minimal file to avoid 422 validation error
        files = {"file": ("test.png", b"fake_image_data", "image/png")}
        response = requests.post(f"{BASE_URL}/api/releases/test/cover", files=files)
        assert response.status_code == 401
        print("✓ Cover upload endpoint requires authentication")


# Cleanup fixture
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """Cleanup test data after all tests"""
    yield
    # Note: In production, we'd delete TEST_ prefixed releases
    # For now, we leave them as they don't affect functionality


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
