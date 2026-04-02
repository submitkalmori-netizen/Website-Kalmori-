"""
Iteration 15 - Subscription Plan Upgrade/Downgrade Tests
Tests:
- GET /api/subscriptions/plans - returns free/rise/pro plans
- POST /api/subscriptions/upgrade?plan=rise - upgrades user plan (requires auth)
- POST /api/subscriptions/checkout - creates Stripe checkout session for paid plans
- POST /api/subscriptions/checkout with plan=free - downgrades immediately without Stripe
- GET /api/beats - verify beats endpoint for featured beats section
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSubscriptionPlans:
    """Test subscription plan endpoints"""
    
    def test_get_subscription_plans(self):
        """GET /api/subscriptions/plans - returns free/rise/pro plans"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "free" in data, "Missing 'free' plan"
        assert "rise" in data, "Missing 'rise' plan"
        assert "pro" in data, "Missing 'pro' plan"
        
        # Verify free plan structure
        assert data["free"]["name"] == "Free"
        assert data["free"]["price"] == 0
        assert data["free"]["revenue_share"] == 15
        
        # Verify rise plan structure
        assert data["rise"]["name"] == "Rise"
        assert data["rise"]["price"] == 9.99
        assert data["rise"]["revenue_share"] == 0
        
        # Verify pro plan structure
        assert data["pro"]["name"] == "Pro"
        assert data["pro"]["price"] == 19.99
        assert data["pro"]["revenue_share"] == 0
        
        print("✓ GET /api/subscriptions/plans - returns all 3 plans with correct structure")


class TestSubscriptionUpgrade:
    """Test subscription upgrade endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_upgrade_to_rise_plan(self, auth_token):
        """POST /api/subscriptions/upgrade?plan=rise - upgrades user plan"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/upgrade?plan=rise",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data
        assert data["plan"] == "rise"
        
        # Verify plan was updated by checking /auth/me
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["plan"] == "rise", f"Expected plan 'rise', got '{user_data.get('plan')}'"
        
        print("✓ POST /api/subscriptions/upgrade?plan=rise - upgrades user plan successfully")
    
    def test_upgrade_to_pro_plan(self, auth_token):
        """POST /api/subscriptions/upgrade?plan=pro - upgrades user plan"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/upgrade?plan=pro",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["plan"] == "pro"
        
        print("✓ POST /api/subscriptions/upgrade?plan=pro - upgrades user plan successfully")
    
    def test_downgrade_to_free_plan(self, auth_token):
        """POST /api/subscriptions/upgrade?plan=free - downgrades user plan"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/upgrade?plan=free",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["plan"] == "free"
        
        print("✓ POST /api/subscriptions/upgrade?plan=free - downgrades user plan successfully")
    
    def test_upgrade_invalid_plan(self, auth_token):
        """POST /api/subscriptions/upgrade?plan=invalid - returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/upgrade?plan=invalid_plan",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        print("✓ POST /api/subscriptions/upgrade?plan=invalid - returns 400 for invalid plan")
    
    def test_upgrade_without_auth(self):
        """POST /api/subscriptions/upgrade - returns 401 without auth"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/upgrade?plan=rise",
            json={}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        print("✓ POST /api/subscriptions/upgrade - returns 401 without auth")


class TestSubscriptionCheckout:
    """Test subscription checkout endpoint (Stripe integration)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_checkout_rise_plan(self, auth_token):
        """POST /api/subscriptions/checkout - creates Stripe checkout for rise plan"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "plan": "rise",
                "origin_url": "https://artist-hub-219.preview.emergentagent.com"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "checkout_url" in data, "Missing checkout_url in response"
        assert "session_id" in data, "Missing session_id in response"
        assert data["checkout_url"].startswith("https://checkout.stripe.com"), f"Invalid checkout URL: {data['checkout_url']}"
        
        print(f"✓ POST /api/subscriptions/checkout (rise) - creates Stripe checkout URL")
    
    def test_checkout_pro_plan(self, auth_token):
        """POST /api/subscriptions/checkout - creates Stripe checkout for pro plan"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "plan": "pro",
                "origin_url": "https://artist-hub-219.preview.emergentagent.com"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "checkout_url" in data
        assert "session_id" in data
        
        print(f"✓ POST /api/subscriptions/checkout (pro) - creates Stripe checkout URL")
    
    def test_checkout_free_plan_instant_downgrade(self, auth_token):
        """POST /api/subscriptions/checkout with plan=free - downgrades immediately without Stripe"""
        # First upgrade to rise so we can test downgrade
        requests.post(
            f"{BASE_URL}/api/subscriptions/upgrade?plan=rise",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={}
        )
        
        # Now test free plan checkout (should downgrade immediately)
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "plan": "free",
                "origin_url": "https://artist-hub-219.preview.emergentagent.com"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Missing message in response"
        assert "Downgraded" in data["message"] or "Free" in data["message"], f"Unexpected message: {data['message']}"
        # Free plan should NOT have checkout_url (instant downgrade)
        assert data.get("redirect_url") is None, "Free plan should not have redirect_url"
        
        # Verify plan was updated
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["plan"] == "free", f"Expected plan 'free', got '{user_data.get('plan')}'"
        
        print("✓ POST /api/subscriptions/checkout (free) - instant downgrade without Stripe")
    
    def test_checkout_invalid_plan(self, auth_token):
        """POST /api/subscriptions/checkout with invalid plan - returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "plan": "invalid_plan",
                "origin_url": "https://artist-hub-219.preview.emergentagent.com"
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        print("✓ POST /api/subscriptions/checkout (invalid) - returns 400")
    
    def test_checkout_without_auth(self):
        """POST /api/subscriptions/checkout - returns 401 without auth"""
        response = requests.post(
            f"{BASE_URL}/api/subscriptions/checkout",
            json={
                "plan": "rise",
                "origin_url": "https://artist-hub-219.preview.emergentagent.com"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        print("✓ POST /api/subscriptions/checkout - returns 401 without auth")


class TestBeatsForFeaturedSection:
    """Test beats endpoint for featured beats section on landing page"""
    
    def test_get_beats_public(self):
        """GET /api/beats - returns beats (public, no auth required)"""
        response = requests.get(f"{BASE_URL}/api/beats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "beats" in data, "Missing 'beats' key in response"
        assert isinstance(data["beats"], list), "beats should be a list"
        
        if len(data["beats"]) > 0:
            beat = data["beats"][0]
            assert "id" in beat, "Beat missing 'id'"
            assert "title" in beat, "Beat missing 'title'"
            assert "genre" in beat, "Beat missing 'genre'"
            assert "bpm" in beat, "Beat missing 'bpm'"
            assert "key" in beat, "Beat missing 'key'"
            assert "prices" in beat, "Beat missing 'prices'"
        
        print(f"✓ GET /api/beats - returns {len(data['beats'])} beats")
    
    def test_get_beats_with_limit(self):
        """GET /api/beats?limit=4 - returns limited beats for featured section"""
        response = requests.get(f"{BASE_URL}/api/beats?limit=4")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "beats" in data
        assert len(data["beats"]) <= 4, f"Expected max 4 beats, got {len(data['beats'])}"
        
        print(f"✓ GET /api/beats?limit=4 - returns {len(data['beats'])} beats (max 4)")


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_check(self):
        """GET /api/health - returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ GET /api/health - healthy")
    
    def test_admin_login(self):
        """POST /api/auth/login - admin login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "admin@tunedrop.com"
        assert data["user"]["role"] == "admin"
        
        print("✓ POST /api/auth/login - admin login successful")


# Cleanup: Reset admin to pro plan after tests
class TestCleanup:
    """Cleanup test data"""
    
    def test_reset_admin_to_pro(self):
        """Reset admin user to pro plan after tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            requests.post(
                f"{BASE_URL}/api/subscriptions/upgrade?plan=pro",
                headers={"Authorization": f"Bearer {token}"},
                json={}
            )
            print("✓ Cleanup: Admin user reset to pro plan")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
