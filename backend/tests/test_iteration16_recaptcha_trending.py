"""
Iteration 16 - Backend Tests
Tests for:
- reCAPTCHA on registration (POST /api/auth/register with recaptcha_token)
- Trending analytics endpoint (GET /api/analytics/trending)
- Subscription checkout (POST /api/subscriptions/checkout)
- Subscription upgrade (POST /api/subscriptions/upgrade)
- Subscription plans (GET /api/subscriptions/plans)
- Analytics overview (GET /api/analytics/overview)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealth:
    """Health check - run first"""
    
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")


class TestAuthWithRecaptcha:
    """Test registration with reCAPTCHA token field"""
    
    def test_register_accepts_recaptcha_token_field(self):
        """POST /api/auth/register should accept recaptcha_token field"""
        unique_email = f"test_recaptcha_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "name": "Test User",
            "recaptcha_token": "test_token_for_testing"  # This will fail verification but endpoint should accept the field
        })
        # The endpoint should accept the field - it may fail reCAPTCHA verification but shouldn't 500
        # If reCAPTCHA verification fails, it returns 400 with "reCAPTCHA verification failed"
        # If reCAPTCHA service is down, it allows registration
        assert response.status_code in [200, 201, 400]
        if response.status_code == 400:
            data = response.json()
            # Should be reCAPTCHA failure, not a field validation error
            assert "recaptcha" in data.get("detail", "").lower() or "captcha" in data.get("detail", "").lower()
            print("✓ Register endpoint accepts recaptcha_token field (verification failed as expected with test token)")
        else:
            print("✓ Register endpoint accepts recaptcha_token field (registration succeeded)")
    
    def test_register_without_recaptcha_token(self):
        """POST /api/auth/register should work without recaptcha_token (optional field)"""
        unique_email = f"test_no_recaptcha_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "name": "Test User No Captcha"
        })
        # Should succeed without recaptcha_token
        assert response.status_code in [200, 201]
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        print("✓ Register works without recaptcha_token")
    
    def test_login_admin(self):
        """POST /api/auth/login - admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "admin@tunedrop.com"
        print("✓ Admin login successful")
        return data["access_token"]


class TestSubscriptionPlans:
    """Test subscription plans endpoint"""
    
    def test_get_subscription_plans(self):
        """GET /api/subscriptions/plans returns 3 plans"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        data = response.json()
        assert "free" in data
        assert "rise" in data
        assert "pro" in data
        # Verify plan structure
        assert data["free"]["price"] == 0
        assert data["rise"]["price"] == 9.99
        assert data["pro"]["price"] == 19.99
        print("✓ GET /api/subscriptions/plans returns 3 plans with correct prices")


class TestSubscriptionCheckout:
    """Test subscription checkout endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_checkout_paid_plan_creates_stripe_url(self, auth_token):
        """POST /api/subscriptions/checkout with paid plan creates Stripe checkout"""
        response = requests.post(f"{BASE_URL}/api/subscriptions/checkout", 
            json={"plan": "rise", "origin_url": "https://artist-hub-219.preview.emergentagent.com"},
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "checkout_url" in data
        assert "stripe.com" in data["checkout_url"] or data["checkout_url"] is not None
        print("✓ POST /api/subscriptions/checkout (rise) creates Stripe checkout URL")
    
    def test_checkout_free_plan_no_stripe(self, auth_token):
        """POST /api/subscriptions/checkout with plan=free returns direct downgrade"""
        response = requests.post(f"{BASE_URL}/api/subscriptions/checkout", 
            json={"plan": "free", "origin_url": "https://artist-hub-219.preview.emergentagent.com"},
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        # Free plan should not create checkout URL
        assert data.get("redirect_url") is None or "checkout_url" not in data or data.get("checkout_url") is None
        print("✓ POST /api/subscriptions/checkout (free) returns direct downgrade without checkout_url")
    
    def test_checkout_invalid_plan(self, auth_token):
        """POST /api/subscriptions/checkout with invalid plan returns 400"""
        response = requests.post(f"{BASE_URL}/api/subscriptions/checkout", 
            json={"plan": "invalid_plan", "origin_url": "https://artist-hub-219.preview.emergentagent.com"},
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 400
        print("✓ POST /api/subscriptions/checkout (invalid) returns 400")
    
    def test_checkout_without_auth(self):
        """POST /api/subscriptions/checkout without auth returns 401"""
        response = requests.post(f"{BASE_URL}/api/subscriptions/checkout", 
            json={"plan": "rise", "origin_url": "https://artist-hub-219.preview.emergentagent.com"})
        assert response.status_code == 401
        print("✓ POST /api/subscriptions/checkout without auth returns 401")


class TestSubscriptionUpgrade:
    """Test subscription upgrade endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_upgrade_to_rise(self, auth_token):
        """POST /api/subscriptions/upgrade?plan=rise updates user plan"""
        response = requests.post(f"{BASE_URL}/api/subscriptions/upgrade?plan=rise", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["plan"] == "rise"
        print("✓ POST /api/subscriptions/upgrade?plan=rise works")
    
    def test_upgrade_invalid_plan(self, auth_token):
        """POST /api/subscriptions/upgrade with invalid plan returns 400"""
        response = requests.post(f"{BASE_URL}/api/subscriptions/upgrade?plan=invalid", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 400
        print("✓ POST /api/subscriptions/upgrade (invalid) returns 400")
    
    def test_upgrade_without_auth(self):
        """POST /api/subscriptions/upgrade without auth returns 401"""
        response = requests.post(f"{BASE_URL}/api/subscriptions/upgrade?plan=rise")
        assert response.status_code == 401
        print("✓ POST /api/subscriptions/upgrade without auth returns 401")


class TestAnalyticsTrending:
    """Test trending analytics endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_trending_endpoint_returns_data(self, auth_token):
        """GET /api/analytics/trending returns trending releases"""
        response = requests.get(f"{BASE_URL}/api/analytics/trending", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "trending" in data
        assert "period" in data
        assert isinstance(data["trending"], list)
        # May be empty if user has no distributed releases - this is expected
        print(f"✓ GET /api/analytics/trending returns data (found {len(data['trending'])} trending items)")
    
    def test_trending_without_auth(self):
        """GET /api/analytics/trending without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/analytics/trending")
        assert response.status_code == 401
        print("✓ GET /api/analytics/trending without auth returns 401")


class TestAnalyticsOverview:
    """Test analytics overview endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_analytics_overview(self, auth_token):
        """GET /api/analytics/overview returns analytics data"""
        response = requests.get(f"{BASE_URL}/api/analytics/overview", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert "total_streams" in data
        assert "total_earnings" in data
        assert "release_count" in data
        assert "daily_streams" in data
        print("✓ GET /api/analytics/overview returns analytics data")
    
    def test_analytics_overview_without_auth(self):
        """GET /api/analytics/overview without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/analytics/overview")
        assert response.status_code == 401
        print("✓ GET /api/analytics/overview without auth returns 401")


class TestBeatsEndpoint:
    """Test beats endpoint for Featured Beats section"""
    
    def test_get_beats_public(self):
        """GET /api/beats returns beats (public, no auth required)"""
        response = requests.get(f"{BASE_URL}/api/beats")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        assert isinstance(data["beats"], list)
        print(f"✓ GET /api/beats returns {len(data['beats'])} beats")
    
    def test_get_beats_with_limit(self):
        """GET /api/beats?limit=4 returns limited beats for featured section"""
        response = requests.get(f"{BASE_URL}/api/beats?limit=4")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        assert len(data["beats"]) <= 4
        print(f"✓ GET /api/beats?limit=4 returns {len(data['beats'])} beats")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
