"""
Iteration 46 - Subscription Tier System Tests
Tests for:
- GET /api/subscriptions/plans - Returns all 3 plans with correct revenue_share
- GET /api/subscriptions/my-plan - Returns current plan info with locked_features list
- SUBSCRIPTION_PLANS has max_releases field (free=1, others=-1)
- check_feature_access raises 403 for locked features
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"


class TestSubscriptionPlans:
    """Test /api/subscriptions/plans endpoint"""
    
    def test_get_plans_returns_all_three_plans(self):
        """GET /api/subscriptions/plans returns all 3 plans"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "free" in data, "Missing 'free' plan"
        assert "rise" in data, "Missing 'rise' plan"
        assert "pro" in data, "Missing 'pro' plan"
        print(f"✓ All 3 plans returned: free, rise, pro")
    
    def test_free_plan_has_correct_revenue_share(self):
        """Free plan has revenue_share = 20"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        free_plan = data.get("free", {})
        assert free_plan.get("revenue_share") == 20, f"Expected revenue_share=20, got {free_plan.get('revenue_share')}"
        print(f"✓ Free plan revenue_share = 20")
    
    def test_rise_plan_has_correct_revenue_share(self):
        """Rise plan has revenue_share = 10"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        rise_plan = data.get("rise", {})
        assert rise_plan.get("revenue_share") == 10, f"Expected revenue_share=10, got {rise_plan.get('revenue_share')}"
        print(f"✓ Rise plan revenue_share = 10")
    
    def test_pro_plan_has_correct_revenue_share(self):
        """Pro plan has revenue_share = 0 (keep 100%)"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        pro_plan = data.get("pro", {})
        assert pro_plan.get("revenue_share") == 0, f"Expected revenue_share=0, got {pro_plan.get('revenue_share')}"
        print(f"✓ Pro plan revenue_share = 0 (keep 100%)")
    
    def test_free_plan_has_correct_price(self):
        """Free plan has price = 0"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        free_plan = data.get("free", {})
        assert free_plan.get("price") == 0, f"Expected price=0, got {free_plan.get('price')}"
        print(f"✓ Free plan price = $0")
    
    def test_rise_plan_has_correct_price(self):
        """Rise plan has price = 9.99"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        rise_plan = data.get("rise", {})
        assert rise_plan.get("price") == 9.99, f"Expected price=9.99, got {rise_plan.get('price')}"
        print(f"✓ Rise plan price = $9.99/mo")
    
    def test_pro_plan_has_correct_price(self):
        """Pro plan has price = 19.99"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        pro_plan = data.get("pro", {})
        assert pro_plan.get("price") == 19.99, f"Expected price=19.99, got {pro_plan.get('price')}"
        print(f"✓ Pro plan price = $19.99/mo")
    
    def test_free_plan_has_max_releases_1(self):
        """Free plan has max_releases = 1"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        free_plan = data.get("free", {})
        assert free_plan.get("max_releases") == 1, f"Expected max_releases=1, got {free_plan.get('max_releases')}"
        print(f"✓ Free plan max_releases = 1")
    
    def test_rise_plan_has_unlimited_releases(self):
        """Rise plan has max_releases = -1 (unlimited)"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        rise_plan = data.get("rise", {})
        assert rise_plan.get("max_releases") == -1, f"Expected max_releases=-1, got {rise_plan.get('max_releases')}"
        print(f"✓ Rise plan max_releases = -1 (unlimited)")
    
    def test_pro_plan_has_unlimited_releases(self):
        """Pro plan has max_releases = -1 (unlimited)"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        pro_plan = data.get("pro", {})
        assert pro_plan.get("max_releases") == -1, f"Expected max_releases=-1, got {pro_plan.get('max_releases')}"
        print(f"✓ Pro plan max_releases = -1 (unlimited)")
    
    def test_free_plan_has_locked_features(self):
        """Free plan has locked features list"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        free_plan = data.get("free", {})
        locked = free_plan.get("locked", [])
        assert len(locked) > 0, "Free plan should have locked features"
        assert "ai_strategy" in locked, "ai_strategy should be locked for free plan"
        assert "collaborations" in locked, "collaborations should be locked for free plan"
        print(f"✓ Free plan has {len(locked)} locked features: {locked}")
    
    def test_pro_plan_has_no_locked_features(self):
        """Pro plan has empty locked features list"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200
        
        data = response.json()
        pro_plan = data.get("pro", {})
        locked = pro_plan.get("locked", [])
        assert len(locked) == 0, f"Pro plan should have no locked features, got {locked}"
        print(f"✓ Pro plan has no locked features")


class TestMyPlan:
    """Test /api/subscriptions/my-plan endpoint"""
    
    @pytest.fixture
    def auth_session(self):
        """Login and return authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return session
    
    def test_my_plan_requires_auth(self):
        """GET /api/subscriptions/my-plan requires authentication"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/my-plan")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ /api/subscriptions/my-plan requires authentication")
    
    def test_my_plan_returns_current_plan(self, auth_session):
        """GET /api/subscriptions/my-plan returns current plan info"""
        response = auth_session.get(f"{BASE_URL}/api/subscriptions/my-plan")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "plan" in data, "Response should contain 'plan'"
        assert "name" in data, "Response should contain 'name'"
        assert "revenue_share" in data, "Response should contain 'revenue_share'"
        assert "locked_features" in data, "Response should contain 'locked_features'"
        print(f"✓ /api/subscriptions/my-plan returns plan info: {data['plan']} ({data['name']})")
    
    def test_my_plan_returns_max_releases(self, auth_session):
        """GET /api/subscriptions/my-plan returns max_releases field"""
        response = auth_session.get(f"{BASE_URL}/api/subscriptions/my-plan")
        assert response.status_code == 200
        
        data = response.json()
        assert "max_releases" in data, "Response should contain 'max_releases'"
        print(f"✓ /api/subscriptions/my-plan returns max_releases: {data['max_releases']}")
    
    def test_admin_user_is_on_pro_plan(self, auth_session):
        """Admin user should be on pro plan"""
        response = auth_session.get(f"{BASE_URL}/api/subscriptions/my-plan")
        assert response.status_code == 200
        
        data = response.json()
        # Admin should be on pro plan based on context
        assert data["plan"] == "pro", f"Expected admin to be on 'pro' plan, got '{data['plan']}'"
        assert data["revenue_share"] == 0, f"Pro plan should have 0 revenue share"
        assert len(data.get("locked_features", [])) == 0, "Pro plan should have no locked features"
        print(f"✓ Admin user is on Pro plan with 0% revenue share and no locked features")


class TestFeatureAccess:
    """Test feature access control based on plan"""
    
    @pytest.fixture
    def auth_session(self):
        """Login and return authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return session
    
    def test_pro_user_can_access_ai_strategy(self, auth_session):
        """Pro user can access AI strategy endpoint"""
        # Try to access AI strategy endpoint (should work for pro user)
        response = auth_session.get(f"{BASE_URL}/api/ai/release-strategy")
        # Should not return 403 for pro user
        assert response.status_code != 403, f"Pro user should have access to AI strategy"
        print(f"✓ Pro user can access AI strategy (status: {response.status_code})")
    
    def test_pro_user_can_access_leaderboard(self, auth_session):
        """Pro user can access leaderboard endpoint"""
        response = auth_session.get(f"{BASE_URL}/api/analytics/leaderboard")
        assert response.status_code == 200, f"Pro user should have access to leaderboard"
        print(f"✓ Pro user can access leaderboard")
    
    def test_pro_user_can_access_goals(self, auth_session):
        """Pro user can access goals endpoint"""
        response = auth_session.get(f"{BASE_URL}/api/goals")
        assert response.status_code == 200, f"Pro user should have access to goals"
        print(f"✓ Pro user can access goals")


class TestSubscriptionUpgrade:
    """Test subscription upgrade endpoint"""
    
    @pytest.fixture
    def auth_session(self):
        """Login and return authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return session
    
    def test_upgrade_requires_auth(self):
        """POST /api/subscriptions/upgrade requires authentication"""
        response = requests.post(f"{BASE_URL}/api/subscriptions/upgrade?plan=pro")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ /api/subscriptions/upgrade requires authentication")
    
    def test_upgrade_rejects_invalid_plan(self, auth_session):
        """POST /api/subscriptions/upgrade rejects invalid plan"""
        response = auth_session.post(f"{BASE_URL}/api/subscriptions/upgrade?plan=invalid_plan")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"✓ /api/subscriptions/upgrade rejects invalid plan")
    
    def test_upgrade_accepts_valid_plan(self, auth_session):
        """POST /api/subscriptions/upgrade accepts valid plan"""
        # Upgrade to pro (admin is already pro, but this should still work)
        response = auth_session.post(f"{BASE_URL}/api/subscriptions/upgrade?plan=pro")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should contain 'message'"
        assert data["plan"] == "pro", f"Expected plan='pro', got '{data['plan']}'"
        print(f"✓ /api/subscriptions/upgrade accepts valid plan: {data['message']}")


class TestSubscriptionCheckout:
    """Test subscription checkout endpoint"""
    
    @pytest.fixture
    def auth_session(self):
        """Login and return authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return session
    
    def test_checkout_requires_auth(self):
        """POST /api/subscriptions/checkout requires authentication"""
        response = requests.post(f"{BASE_URL}/api/subscriptions/checkout", json={
            "plan": "pro",
            "origin_url": "https://example.com"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ /api/subscriptions/checkout requires authentication")
    
    def test_checkout_rejects_invalid_plan(self, auth_session):
        """POST /api/subscriptions/checkout rejects invalid plan"""
        response = auth_session.post(f"{BASE_URL}/api/subscriptions/checkout", json={
            "plan": "invalid_plan",
            "origin_url": "https://example.com"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"✓ /api/subscriptions/checkout rejects invalid plan")
    
    def test_checkout_free_plan_returns_no_url(self, auth_session):
        """POST /api/subscriptions/checkout for free plan returns no checkout URL"""
        response = auth_session.post(f"{BASE_URL}/api/subscriptions/checkout", json={
            "plan": "free",
            "origin_url": "https://example.com"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("redirect_url") is None, "Free plan should not have checkout URL"
        print(f"✓ Free plan checkout returns no URL (direct downgrade)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
