"""
Iteration 10 Backend Tests - New Features
Tests: AI Features, PayPal, Email/Password Reset, Spotify Canvas, YouTube Content ID, Analytics
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://artist-hub-219.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"

class TestHealthAndPublic:
    """Public endpoint tests"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")
    
    def test_spotify_canvas_specs_public(self):
        """Test Spotify Canvas specs endpoint (public)"""
        response = requests.get(f"{BASE_URL}/api/spotify-canvas/specs")
        assert response.status_code == 200
        data = response.json()
        assert "specs" in data
        assert "tips" in data
        assert data["specs"]["format"] == "MP4 (H.264)"
        assert data["specs"]["aspect_ratio"] == "9:16 (vertical)"
        print("✓ Spotify Canvas specs endpoint works")
    
    def test_paypal_config_public(self):
        """Test PayPal config endpoint (public)"""
        response = requests.get(f"{BASE_URL}/api/payments/paypal/config")
        assert response.status_code == 200
        data = response.json()
        assert "client_id" in data
        assert "mode" in data
        assert "enabled" in data
        print(f"✓ PayPal config: mode={data['mode']}, enabled={data['enabled']}")


class TestAuthAndPasswordReset:
    """Authentication and password reset tests"""
    
    def test_login_success(self):
        """Test successful login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        print("✓ Login successful")
        return data["access_token"]
    
    def test_forgot_password_endpoint(self):
        """Test forgot password endpoint"""
        response = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": ADMIN_EMAIL
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        # Should always return success message (security - don't reveal if email exists)
        assert "reset link" in data["message"].lower() or "email" in data["message"].lower()
        print("✓ Forgot password endpoint works")
    
    def test_forgot_password_nonexistent_email(self):
        """Test forgot password with non-existent email (should still return 200)"""
        response = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": "nonexistent@example.com"
        })
        # Should return 200 for security (don't reveal if email exists)
        assert response.status_code == 200
        print("✓ Forgot password handles non-existent email securely")
    
    def test_verify_reset_token_invalid(self):
        """Test verify reset token with invalid token"""
        response = requests.get(f"{BASE_URL}/api/auth/verify-reset-token?token=invalid_token_123")
        assert response.status_code == 400
        print("✓ Invalid reset token rejected correctly")
    
    def test_reset_password_invalid_token(self):
        """Test reset password with invalid token"""
        response = requests.post(f"{BASE_URL}/api/auth/reset-password", json={
            "token": "invalid_token_123",
            "new_password": "NewPassword123!"
        })
        assert response.status_code == 400
        print("✓ Reset password with invalid token rejected")


class TestAIFeatures:
    """AI Features tests (metadata, descriptions, analytics insights)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for authenticated tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_ai_metadata_suggestions(self):
        """Test AI metadata suggestions endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/ai/metadata-suggestions",
            json={"title": "Summer Vibes", "genre": "Pop", "mood": "Happy"},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        # Should return suggestions (either from AI or fallback)
        assert "suggested_genres" in data or "raw_response" in data
        print(f"✓ AI metadata suggestions returned: {list(data.keys())}")
    
    def test_ai_generate_description(self):
        """Test AI description generation endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/ai/generate-description",
            json={
                "title": "Midnight Dreams",
                "artist_name": "Test Artist",
                "genre": "R&B",
                "track_count": 1
            },
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "description" in data
        assert len(data["description"]) > 0
        print(f"✓ AI description generated: {data['description'][:50]}...")
    
    def test_ai_analytics_insights(self):
        """Test AI analytics insights endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/ai/analytics-insights",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data
        assert len(data["insights"]) > 0
        print(f"✓ AI analytics insights returned: {data['insights'][:100]}...")


class TestPayPalIntegration:
    """PayPal integration tests (sandbox simulation)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_paypal_create_order(self):
        """Test PayPal create order (sandbox simulation)"""
        response = requests.post(
            f"{BASE_URL}/api/payments/paypal/create-order",
            json={
                "amount": 29.99,
                "currency": "USD",
                "description": "Test subscription",
                "order_type": "subscription"
            },
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "order_id" in data
        assert "internal_order_id" in data
        assert "status" in data
        # In sandbox mode without API keys, should be simulated
        if data.get("simulated"):
            print(f"✓ PayPal order created (SIMULATED): {data['order_id']}")
        else:
            print(f"✓ PayPal order created: {data['order_id']}")
        return data


class TestSpotifyCanvas:
    """Spotify Canvas management tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token and user releases"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get user releases
        releases_resp = requests.get(f"{BASE_URL}/api/releases", headers=self.headers)
        self.releases = releases_resp.json() if releases_resp.status_code == 200 else []
    
    def test_get_canvas_specs(self):
        """Test getting canvas specifications"""
        response = requests.get(f"{BASE_URL}/api/spotify-canvas/specs")
        assert response.status_code == 200
        data = response.json()
        assert "specs" in data
        assert data["specs"]["duration"] == "3-8 seconds"
        print("✓ Canvas specs retrieved")
    
    def test_get_user_canvases(self):
        """Test getting user's canvases"""
        response = requests.get(
            f"{BASE_URL}/api/spotify-canvas",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ User canvases retrieved: {len(data)} canvases")
    
    def test_create_canvas_requires_release(self):
        """Test creating canvas requires valid release"""
        response = requests.post(
            f"{BASE_URL}/api/spotify-canvas",
            json={"release_id": "invalid_release_id"},
            headers=self.headers
        )
        assert response.status_code == 404
        print("✓ Canvas creation requires valid release")
    
    def test_create_canvas_with_valid_release(self):
        """Test creating canvas with valid release"""
        if not self.releases:
            pytest.skip("No releases available for testing")
        
        release_id = self.releases[0]["id"]
        response = requests.post(
            f"{BASE_URL}/api/spotify-canvas",
            json={"release_id": release_id},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "draft"
        print(f"✓ Canvas created for release: {release_id}")
        return data["id"]


class TestYouTubeContentID:
    """YouTube Content ID management tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token and user releases"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get user releases
        releases_resp = requests.get(f"{BASE_URL}/api/releases", headers=self.headers)
        self.releases = releases_resp.json() if releases_resp.status_code == 200 else []
    
    def test_get_content_id_registrations(self):
        """Test getting Content ID registrations"""
        response = requests.get(
            f"{BASE_URL}/api/youtube-content-id",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Content ID registrations retrieved: {len(data)} registrations")
    
    def test_register_content_id_requires_release(self):
        """Test Content ID registration requires valid release"""
        response = requests.post(
            f"{BASE_URL}/api/youtube-content-id",
            json={"release_id": "invalid_release_id"},
            headers=self.headers
        )
        assert response.status_code == 404
        print("✓ Content ID registration requires valid release")
    
    def test_register_content_id_with_valid_release(self):
        """Test Content ID registration with valid release"""
        if not self.releases:
            pytest.skip("No releases available for testing")
        
        # Find a release not already registered
        existing_resp = requests.get(f"{BASE_URL}/api/youtube-content-id", headers=self.headers)
        existing_ids = [r["release_id"] for r in existing_resp.json()] if existing_resp.status_code == 200 else []
        
        available_release = None
        for release in self.releases:
            if release["id"] not in existing_ids:
                available_release = release
                break
        
        if not available_release:
            pytest.skip("All releases already registered for Content ID")
        
        response = requests.post(
            f"{BASE_URL}/api/youtube-content-id",
            json={
                "release_id": available_release["id"],
                "ownership_type": "composition_and_recording"
            },
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "asset_id" in data
        assert data["status"] == "pending"
        print(f"✓ Content ID registered: Asset ID {data['asset_id']}")


class TestAdvancedAnalytics:
    """Advanced Analytics tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_analytics_overview(self):
        """Test analytics overview endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/overview",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_streams" in data
        assert "total_earnings" in data
        assert "streams_by_store" in data
        assert "streams_by_country" in data
        print(f"✓ Analytics overview: {data['total_streams']} streams, ${data['total_earnings']} earnings")
    
    def test_analytics_chart_data(self):
        """Test analytics chart data endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/chart-data?days=14",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 14
        if data:
            assert "date" in data[0]
            assert "plays" in data[0] or "streams" in data[0]
        print(f"✓ Chart data retrieved: {len(data)} days")
    
    def test_analytics_platform_breakdown(self):
        """Test platform breakdown endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/platform-breakdown",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        platform_names = [p["name"] for p in data]
        assert "Spotify" in platform_names
        assert "Apple Music" in platform_names
        print(f"✓ Platform breakdown: {len(data)} platforms")


class TestAuthenticatedEndpointsRequireAuth:
    """Test that authenticated endpoints require authentication"""
    
    def test_ai_metadata_requires_auth(self):
        """Test AI metadata requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/ai/metadata-suggestions",
            json={"title": "Test", "genre": "Pop"}
        )
        assert response.status_code == 401
        print("✓ AI metadata requires auth")
    
    def test_ai_description_requires_auth(self):
        """Test AI description requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/ai/generate-description",
            json={"title": "Test", "artist_name": "Test", "genre": "Pop"}
        )
        assert response.status_code == 401
        print("✓ AI description requires auth")
    
    def test_ai_insights_requires_auth(self):
        """Test AI insights requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ai/analytics-insights")
        assert response.status_code == 401
        print("✓ AI insights requires auth")
    
    def test_paypal_create_order_requires_auth(self):
        """Test PayPal create order requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/payments/paypal/create-order",
            json={"amount": 10, "currency": "USD"}
        )
        assert response.status_code == 401
        print("✓ PayPal create order requires auth")
    
    def test_spotify_canvas_list_requires_auth(self):
        """Test Spotify Canvas list requires authentication"""
        response = requests.get(f"{BASE_URL}/api/spotify-canvas")
        assert response.status_code == 401
        print("✓ Spotify Canvas list requires auth")
    
    def test_content_id_list_requires_auth(self):
        """Test Content ID list requires authentication"""
        response = requests.get(f"{BASE_URL}/api/youtube-content-id")
        assert response.status_code == 401
        print("✓ Content ID list requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
