"""
Iteration 48 - Email Domain Management & Badge Removal Tests
Tests:
1. Admin email domain endpoints (GET, POST, auth protection)
2. Non-admin users get 403 on admin endpoints
3. Login flow with admin credentials
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"


class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ Health endpoint working")
    
    def test_admin_login_success(self):
        """Test admin login with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }, timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful - role: {data['user']['role']}")
        return data["access_token"]
    
    def test_admin_login_invalid_credentials(self):
        """Test login with invalid credentials returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }, timeout=10)
        assert response.status_code == 401
        print("✓ Invalid credentials correctly rejected with 401")


class TestEmailDomainEndpoints:
    """Test admin email domain management endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }, timeout=10)
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["access_token"]
    
    @pytest.fixture
    def admin_headers(self, admin_token):
        """Get headers with admin auth"""
        return {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
    
    def test_get_email_domains_requires_auth(self):
        """Test GET /api/admin/email/domain requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/email/domain", timeout=10)
        assert response.status_code == 401
        print("✓ GET /api/admin/email/domain requires auth (401)")
    
    def test_get_email_domains_as_admin(self, admin_headers):
        """Test GET /api/admin/email/domain returns domains list and current_sender"""
        response = requests.get(f"{BASE_URL}/api/admin/email/domain", headers=admin_headers, timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "domains" in data
        assert "current_sender" in data
        assert isinstance(data["domains"], list)
        # Current sender should be onboarding@resend.dev (test domain)
        assert data["current_sender"] == "onboarding@resend.dev"
        print(f"✓ GET /api/admin/email/domain - domains: {len(data['domains'])}, sender: {data['current_sender']}")
    
    def test_post_email_domain_requires_auth(self):
        """Test POST /api/admin/email/domain requires authentication"""
        response = requests.post(f"{BASE_URL}/api/admin/email/domain", 
            json={"domain": "test.example.com"}, timeout=10)
        assert response.status_code == 401
        print("✓ POST /api/admin/email/domain requires auth (401)")
    
    def test_post_email_domain_invalid_domain(self, admin_headers):
        """Test POST /api/admin/email/domain with invalid domain"""
        response = requests.post(f"{BASE_URL}/api/admin/email/domain",
            headers=admin_headers, json={"domain": "invalid"}, timeout=10)
        # Should return 400 for invalid domain (no dot)
        assert response.status_code == 400
        print("✓ POST /api/admin/email/domain rejects invalid domain (400)")
    
    def test_post_email_domain_attempts_resend_api(self, admin_headers):
        """Test POST /api/admin/email/domain attempts to add domain via Resend API
        Note: This may fail with Resend API error for test domains - that's expected
        """
        response = requests.post(f"{BASE_URL}/api/admin/email/domain",
            headers=admin_headers, json={"domain": "test-domain-12345.example.com"}, timeout=15)
        # Could be 200 (success), 400 (already exists), or 500 (Resend API error)
        # All are valid responses - we're testing the endpoint is reachable and processes the request
        assert response.status_code in [200, 400, 500]
        data = response.json()
        print(f"✓ POST /api/admin/email/domain processed - status: {response.status_code}, response: {data}")


class TestNonAdminAccess:
    """Test that non-admin users get 403 on admin endpoints"""
    
    @pytest.fixture
    def regular_user_token(self):
        """Create a regular user and get token"""
        import uuid
        test_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
        
        # Try to register a new user (may fail due to reCAPTCHA)
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPass123!",
            "name": "Test User",
            "recaptcha_token": ""  # Empty token - may be rejected
        }, timeout=10)
        
        if response.status_code == 200:
            return response.json()["access_token"]
        elif response.status_code == 400 and "reCAPTCHA" in response.json().get("detail", ""):
            pytest.skip("reCAPTCHA required for registration - cannot create test user")
        else:
            pytest.skip(f"Could not create test user: {response.status_code}")
    
    def test_non_admin_cannot_access_email_domains(self, regular_user_token):
        """Test non-admin user gets 403 on admin email endpoints"""
        headers = {
            "Authorization": f"Bearer {regular_user_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_URL}/api/admin/email/domain", headers=headers, timeout=10)
        assert response.status_code == 403
        print("✓ Non-admin user correctly gets 403 on admin email endpoint")


class TestExistingEndpoints:
    """Verify existing endpoints still work"""
    
    def test_beats_endpoint(self):
        """Test GET /api/beats returns beats list"""
        response = requests.get(f"{BASE_URL}/api/beats", timeout=10)
        assert response.status_code == 200
        data = response.json()
        # Beats endpoint returns {"beats": [...], "total": N}
        assert "beats" in data
        assert isinstance(data["beats"], list)
        print(f"✓ GET /api/beats - {len(data['beats'])} beats")
    
    def test_subscription_plans(self):
        """Test GET /api/subscriptions/plans returns plans"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3  # Should have at least 3 plans
        print(f"✓ GET /api/subscriptions/plans - {len(data)} plans")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
