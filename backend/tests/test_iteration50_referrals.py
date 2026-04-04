"""
Iteration 50 - Referral Program Testing
Tests:
1. Admin login with new credentials (admin@kalmori.com / MAYAsimpSON37!!)
2. Referral endpoints: /api/referral/my-link, /api/referral/stats, /api/referral/validate
3. Admin referral overview: /api/admin/referral/overview
4. Verify old promo code LAUNCH50 was wiped (should return 404)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# New admin credentials (old admin@tunedrop.com no longer exists)
ADMIN_EMAIL = "admin@kalmori.com"
ADMIN_PASSWORD = "MAYAsimpSON37!!"


class TestAdminLogin:
    """Test admin login with new credentials"""
    
    def test_admin_login_success(self):
        """POST /api/auth/login with admin@kalmori.com returns access_token and role=admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert "user" in data, "No user in response"
        assert data["user"]["role"] == "admin", f"Expected role=admin, got {data['user']['role']}"
        assert data["user"]["email"] == ADMIN_EMAIL, f"Email mismatch"
        print(f"✓ Admin login successful: {data['user']['email']} (role={data['user']['role']})")
    
    def test_old_admin_no_longer_exists(self):
        """Verify old admin@tunedrop.com account no longer exists"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 401, f"Old admin should not exist, got {response.status_code}"
        print("✓ Old admin@tunedrop.com account no longer exists (as expected)")


class TestReferralEndpoints:
    """Test referral endpoints for authenticated users"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["access_token"]
    
    def test_get_referral_link(self, admin_token):
        """GET /api/referral/my-link returns referral_code for authenticated user"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/referral/my-link", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "referral_code" in data, "No referral_code in response"
        assert len(data["referral_code"]) > 0, "Referral code is empty"
        # Referral code format: KAL + last 6 chars of user ID in uppercase
        assert data["referral_code"].startswith("KAL"), f"Referral code should start with KAL, got {data['referral_code']}"
        print(f"✓ Referral link endpoint works. Code: {data['referral_code']}")
        return data["referral_code"]
    
    def test_get_referral_stats(self, admin_token):
        """GET /api/referral/stats returns stats object with total_referrals"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/referral/stats", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "total_referrals" in data, "No total_referrals in response"
        assert "successful_referrals" in data, "No successful_referrals in response"
        assert "rewards_earned" in data, "No rewards_earned in response"
        print(f"✓ Referral stats: total={data['total_referrals']}, successful={data['successful_referrals']}, rewards={data['rewards_earned']}")
    
    def test_validate_referral_code_valid(self, admin_token):
        """POST /api/referral/validate with valid code returns referrer info"""
        # First get the admin's referral code
        headers = {"Authorization": f"Bearer {admin_token}"}
        link_response = requests.get(f"{BASE_URL}/api/referral/my-link", headers=headers)
        code = link_response.json().get("referral_code")
        
        # Validate the code (no auth required for validation)
        response = requests.post(f"{BASE_URL}/api/referral/validate", json={"code": code})
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "valid" in data, "No valid field in response"
        assert data["valid"] == True, "Code should be valid"
        assert "referrer_name" in data, "No referrer_name in response"
        print(f"✓ Valid referral code validation works. Referrer: {data.get('referrer_name')}")
    
    def test_validate_referral_code_invalid(self):
        """POST /api/referral/validate with invalid code returns 404"""
        response = requests.post(f"{BASE_URL}/api/referral/validate", json={"code": "INVALID123"})
        assert response.status_code == 404, f"Expected 404 for invalid code, got {response.status_code}"
        print("✓ Invalid referral code returns 404 as expected")
    
    def test_referral_endpoints_require_auth(self):
        """Referral my-link and stats endpoints require authentication"""
        # my-link without auth
        response = requests.get(f"{BASE_URL}/api/referral/my-link")
        assert response.status_code == 401, f"my-link should require auth, got {response.status_code}"
        
        # stats without auth
        response = requests.get(f"{BASE_URL}/api/referral/stats")
        assert response.status_code == 401, f"stats should require auth, got {response.status_code}"
        print("✓ Referral endpoints properly require authentication")


class TestAdminReferralOverview:
    """Test admin referral overview endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["access_token"]
    
    def test_admin_referral_overview(self, admin_token):
        """GET /api/admin/referral/overview returns total_referrals and top_referrers (admin only)"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/referral/overview", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "total_referrals" in data, "No total_referrals in response"
        assert "total_referrers" in data, "No total_referrers in response"
        assert "top_referrers" in data, "No top_referrers in response"
        assert "recent_signups" in data, "No recent_signups in response"
        print(f"✓ Admin referral overview: total_referrals={data['total_referrals']}, total_referrers={data['total_referrers']}")
    
    def test_admin_referral_overview_requires_admin(self):
        """GET /api/admin/referral/overview returns 403 for non-admin"""
        # Without auth
        response = requests.get(f"{BASE_URL}/api/admin/referral/overview")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Admin referral overview properly requires admin role")


class TestDatabaseWipe:
    """Verify database was wiped - old data should not exist"""
    
    def test_promo_code_launch50_wiped(self):
        """Verify LAUNCH50 promo code was wiped (should return 404)"""
        response = requests.post(f"{BASE_URL}/api/promo-codes/validate", json={
            "code": "LAUNCH50",
            "plan": "rise"
        })
        # Should return 404 since DB was wiped
        assert response.status_code == 404, f"LAUNCH50 should be wiped, got {response.status_code}: {response.text}"
        print("✓ LAUNCH50 promo code was wiped (returns 404 as expected)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
