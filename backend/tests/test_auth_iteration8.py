"""
Iteration 8 - Auth Flow Tests
Testing the new dual auth (cookie + Bearer token) implementation:
- POST /api/auth/login returns {access_token, refresh_token, user}
- POST /api/auth/register with new fields returns {access_token, refresh_token, user}
- GET /api/auth/me works with Bearer token
- GET /api/auth/me works with cookies (backward compatibility)
- Authenticated endpoints work with Bearer token
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://artist-hub-219.preview.emergentagent.com')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"

# Generate unique test user for registration tests
TEST_USER_EMAIL = f"test_auth_{uuid.uuid4().hex[:8]}@test.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_NAME = "Test Auth User"


class TestAuthLoginResponse:
    """Test that login returns the new {access_token, refresh_token, user} format"""
    
    def test_login_returns_access_token(self):
        """POST /api/auth/login should return access_token in response body"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        
        # Verify new response format
        assert "access_token" in data, "Response missing access_token"
        assert "refresh_token" in data, "Response missing refresh_token"
        assert "user" in data, "Response missing user object"
        
        # Verify token is a non-empty string
        assert isinstance(data["access_token"], str), "access_token should be string"
        assert len(data["access_token"]) > 0, "access_token should not be empty"
        
        # Verify user object has expected fields
        user = data["user"]
        assert "id" in user, "User missing id"
        assert "email" in user, "User missing email"
        assert user["email"] == ADMIN_EMAIL.lower(), f"Email mismatch: {user['email']}"
        
        print(f"✓ Login returns access_token, refresh_token, and user object")
    
    def test_login_also_sets_cookies(self):
        """POST /api/auth/login should also set httpOnly cookies for backward compatibility"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200
        
        # Check cookies are set
        cookies = response.cookies
        assert "access_token" in cookies or len(cookies) > 0, "Cookies should be set"
        
        print(f"✓ Login also sets cookies for backward compatibility")


class TestAuthRegisterResponse:
    """Test that register returns the new format with new fields"""
    
    def test_register_returns_access_token(self):
        """POST /api/auth/register should return {access_token, refresh_token, user}"""
        unique_email = f"test_reg_{uuid.uuid4().hex[:8]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME,
            "artist_name": "Test Artist",
            "user_role": "artist",
            "country": "US",
            "state": "CA",
            "town": "Los Angeles",
            "post_code": "90001"
        })
        
        assert response.status_code == 200, f"Register failed: {response.text}"
        data = response.json()
        
        # Verify new response format
        assert "access_token" in data, "Response missing access_token"
        assert "refresh_token" in data, "Response missing refresh_token"
        assert "user" in data, "Response missing user object"
        
        # Verify user has new fields
        user = data["user"]
        assert user["email"] == unique_email.lower()
        assert "country" in user or user.get("country") == "US", "User should have country field"
        
        print(f"✓ Register returns access_token, refresh_token, and user with new fields")
    
    def test_register_with_new_fields(self):
        """POST /api/auth/register should accept new fields (user_role, country, state, town, post_code)"""
        unique_email = f"test_fields_{uuid.uuid4().hex[:8]}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": TEST_USER_PASSWORD,
            "name": "Field Test User",
            "artist_name": "Field Artist",
            "user_role": "producer",
            "legal_name": "Legal Name Test",
            "country": "UK",
            "state": "London",
            "town": "Westminster",
            "post_code": "SW1A 1AA",
            "phone_number": "+44123456789"
        })
        
        assert response.status_code == 200, f"Register with new fields failed: {response.text}"
        data = response.json()
        
        user = data["user"]
        # Verify new fields are stored
        assert user.get("country") == "UK", f"Country not stored: {user.get('country')}"
        assert user.get("state") == "London", f"State not stored: {user.get('state')}"
        assert user.get("town") == "Westminster", f"Town not stored: {user.get('town')}"
        assert user.get("post_code") == "SW1A 1AA", f"Post code not stored: {user.get('post_code')}"
        
        print(f"✓ Register accepts and stores new fields (country, state, town, post_code)")


class TestAuthMeWithBearerToken:
    """Test GET /api/auth/me works with Bearer token from login response"""
    
    def test_auth_me_with_bearer_token(self):
        """GET /api/auth/me should work with Bearer token in Authorization header"""
        # First login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Use Bearer token to call /auth/me
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert me_response.status_code == 200, f"Auth/me with Bearer failed: {me_response.text}"
        user = me_response.json()
        
        assert user["email"] == ADMIN_EMAIL.lower()
        assert "id" in user
        assert "password_hash" not in user, "password_hash should not be returned"
        
        print(f"✓ GET /api/auth/me works with Bearer token")
    
    def test_auth_me_with_cookies(self):
        """GET /api/auth/me should work with cookies (backward compatibility)"""
        session = requests.Session()
        
        # Login to set cookies
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200
        
        # Use session (with cookies) to call /auth/me
        me_response = session.get(f"{BASE_URL}/api/auth/me")
        
        assert me_response.status_code == 200, f"Auth/me with cookies failed: {me_response.text}"
        user = me_response.json()
        
        assert user["email"] == ADMIN_EMAIL.lower()
        
        print(f"✓ GET /api/auth/me works with cookies (backward compatibility)")


class TestAuthenticatedEndpointsWithBearerToken:
    """Test that authenticated endpoints work with Bearer token"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get Bearer token for tests"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_cart_with_bearer_token(self):
        """GET /api/cart should work with Bearer token"""
        response = requests.get(f"{BASE_URL}/api/cart", headers=self.headers)
        
        assert response.status_code == 200, f"Cart failed: {response.text}"
        data = response.json()
        assert "items" in data or "item_count" in data
        
        print(f"✓ GET /api/cart works with Bearer token")
    
    def test_theme_with_bearer_token(self):
        """GET /api/theme should work with Bearer token"""
        response = requests.get(f"{BASE_URL}/api/theme", headers=self.headers)
        
        assert response.status_code == 200, f"Theme failed: {response.text}"
        
        print(f"✓ GET /api/theme works with Bearer token")
    
    def test_credits_with_bearer_token(self):
        """GET /api/credits should work with Bearer token"""
        response = requests.get(f"{BASE_URL}/api/credits", headers=self.headers)
        
        assert response.status_code == 200, f"Credits failed: {response.text}"
        data = response.json()
        assert "credits" in data
        
        print(f"✓ GET /api/credits works with Bearer token")
    
    def test_payment_methods_with_bearer_token(self):
        """GET /api/payment-methods should work with Bearer token"""
        response = requests.get(f"{BASE_URL}/api/payment-methods", headers=self.headers)
        
        assert response.status_code == 200, f"Payment methods failed: {response.text}"
        # Should return array
        assert isinstance(response.json(), list)
        
        print(f"✓ GET /api/payment-methods works with Bearer token")
    
    def test_analytics_chart_data_with_bearer_token(self):
        """GET /api/analytics/chart-data should work with Bearer token"""
        response = requests.get(f"{BASE_URL}/api/analytics/chart-data?days=7", headers=self.headers)
        
        assert response.status_code == 200, f"Analytics chart-data failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 7
        
        print(f"✓ GET /api/analytics/chart-data works with Bearer token")


class TestPublicEndpoints:
    """Test that public endpoints still work without auth"""
    
    def test_cms_slides_public(self):
        """GET /api/cms/slides should work without auth"""
        response = requests.get(f"{BASE_URL}/api/cms/slides")
        
        assert response.status_code == 200
        data = response.json()
        assert "slides" in data
        
        print(f"✓ GET /api/cms/slides works (public endpoint)")
    
    def test_health_public(self):
        """GET /api/health should work without auth"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        
        print(f"✓ GET /api/health works (public endpoint)")


class TestInvalidAuth:
    """Test error handling for invalid auth"""
    
    def test_invalid_credentials(self):
        """POST /api/auth/login with invalid credentials should return 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        
        print(f"✓ Invalid credentials return 401")
    
    def test_invalid_bearer_token(self):
        """GET /api/auth/me with invalid Bearer token should return 401"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401
        
        print(f"✓ Invalid Bearer token returns 401")
    
    def test_missing_auth(self):
        """GET /api/auth/me without auth should return 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        
        assert response.status_code == 401
        
        print(f"✓ Missing auth returns 401")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
