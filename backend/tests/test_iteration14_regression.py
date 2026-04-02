"""
Iteration 14 - Regression Test Suite
Tests all major endpoints after backend modularization (server.py refactored from 1686 to 772 lines).
Verifies core.py shared models/helpers work correctly.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"


class TestHealthCheck:
    """Health endpoint - basic connectivity test"""
    
    def test_health_check(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        print("✓ Health check passed")


class TestAuthEndpoints:
    """Authentication endpoints - register, login, me"""
    
    def test_admin_login_success(self):
        """POST /api/auth/login - admin login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful: {data['user']['email']}")
        return data["access_token"]
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login - invalid credentials returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid login correctly returns 401")
    
    def test_register_new_user(self):
        """POST /api/auth/register - creates user with all fields"""
        import uuid
        unique_email = f"test_reg_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "name": "Test User",
            "artist_name": "Test Artist",
            "legal_name": "Test Legal Name",
            "country": "US",
            "state": "CA",
            "town": "Los Angeles",
            "post_code": "90001",
            "phone_number": "+1234567890"
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == unique_email
        assert data["user"]["name"] == "Test User"
        assert data["user"]["artist_name"] == "Test Artist"
        assert data["user"]["country"] == "US"
        print(f"✓ User registration successful: {unique_email}")
        return data
    
    def test_get_me_authenticated(self):
        """GET /api/auth/me - returns current user"""
        # First login
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = login_resp.json()["access_token"]
        
        # Get current user
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200, f"Get me failed: {response.text}"
        data = response.json()
        assert data["email"] == ADMIN_EMAIL
        assert data["role"] == "admin"
        print(f"✓ GET /api/auth/me returned: {data['email']}")
    
    def test_get_me_unauthenticated(self):
        """GET /api/auth/me - returns 401 without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✓ GET /api/auth/me correctly returns 401 without auth")


class TestBeatsEndpoints:
    """Beats CRUD - public list, admin create/delete"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_list_beats_public(self):
        """GET /api/beats - list beats (public)"""
        response = requests.get(f"{BASE_URL}/api/beats")
        assert response.status_code == 200, f"List beats failed: {response.text}"
        data = response.json()
        assert "beats" in data
        assert isinstance(data["beats"], list)
        print(f"✓ GET /api/beats returned {len(data['beats'])} beats")
    
    def test_list_beats_filter_genre(self):
        """GET /api/beats?genre=Trap - filters by genre"""
        response = requests.get(f"{BASE_URL}/api/beats?genre=Trap")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        print(f"✓ GET /api/beats?genre=Trap returned {len(data['beats'])} beats")
    
    def test_admin_create_beat(self, admin_token):
        """POST /api/beats - admin create beat"""
        import uuid
        response = requests.post(f"{BASE_URL}/api/beats", json={
            "title": f"TEST_Regression_{uuid.uuid4().hex[:6]}",
            "genre": "Hip-Hop/Rap",
            "bpm": 95,
            "key": "Am",
            "mood": "Dark",
            "price_basic": 29.99,
            "price_premium": 79.99,
            "price_unlimited": 149.99,
            "price_exclusive": 499.99
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200, f"Create beat failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["genre"] == "Hip-Hop/Rap"
        print(f"✓ POST /api/beats created beat: {data['id']}")
        return data["id"]
    
    def test_admin_delete_beat(self, admin_token):
        """DELETE /api/beats/{id} - admin delete beat"""
        # First create a beat
        import uuid
        create_resp = requests.post(f"{BASE_URL}/api/beats", json={
            "title": f"TEST_ToDelete_{uuid.uuid4().hex[:6]}",
            "genre": "Trap",
            "bpm": 140,
            "key": "Cm",
            "mood": "Dark"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        beat_id = create_resp.json()["id"]
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/beats/{beat_id}", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"Delete beat failed: {response.text}"
        print(f"✓ DELETE /api/beats/{beat_id} successful")
    
    def test_create_beat_without_auth(self):
        """POST /api/beats without auth returns 401"""
        response = requests.post(f"{BASE_URL}/api/beats", json={
            "title": "Unauthorized Beat",
            "genre": "Trap"
        })
        assert response.status_code == 401
        print("✓ POST /api/beats without auth correctly returns 401")


class TestReleasesEndpoints:
    """Releases CRUD - create, list"""
    
    @pytest.fixture
    def user_token(self):
        # Register a new user for release tests
        import uuid
        email = f"test_release_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": "TestPass123!",
            "name": "Release Tester"
        })
        return response.json()["access_token"]
    
    def test_create_release(self, user_token):
        """POST /api/releases - create release"""
        response = requests.post(f"{BASE_URL}/api/releases", json={
            "title": "TEST_Regression_Release",
            "release_type": "single",
            "genre": "Hip-Hop",
            "release_date": "2026-02-01",
            "description": "Test release for regression testing"
        }, headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200, f"Create release failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert "upc" in data
        assert data["title"] == "TEST_Regression_Release"
        assert data["status"] == "draft"
        print(f"✓ POST /api/releases created: {data['id']} with UPC: {data['upc']}")
    
    def test_list_releases(self, user_token):
        """GET /api/releases - list user releases"""
        response = requests.get(f"{BASE_URL}/api/releases", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert response.status_code == 200, f"List releases failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/releases returned {len(data)} releases")
    
    def test_releases_without_auth(self):
        """GET /api/releases without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/releases")
        assert response.status_code == 401
        print("✓ GET /api/releases without auth correctly returns 401")


class TestDistributionEndpoints:
    """Distribution stores endpoint"""
    
    def test_get_distribution_stores(self):
        """GET /api/distributions/stores - returns DSP stores"""
        response = requests.get(f"{BASE_URL}/api/distributions/stores")
        assert response.status_code == 200, f"Get stores failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Check expected stores
        store_ids = [s["store_id"] for s in data]
        assert "spotify" in store_ids
        assert "apple_music" in store_ids
        print(f"✓ GET /api/distributions/stores returned {len(data)} stores: {store_ids}")


class TestPaymentsEndpoints:
    """Payments checkout endpoint"""
    
    @pytest.fixture
    def user_with_release(self):
        import uuid
        email = f"test_payment_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": "TestPass123!",
            "name": "Payment Tester"
        })
        token = reg_resp.json()["access_token"]
        
        # Create a release
        rel_resp = requests.post(f"{BASE_URL}/api/releases", json={
            "title": "TEST_Payment_Release",
            "release_type": "single",
            "genre": "Pop",
            "release_date": "2026-03-01"
        }, headers={"Authorization": f"Bearer {token}"})
        release_id = rel_resp.json()["id"]
        
        return {"token": token, "release_id": release_id}
    
    def test_create_checkout(self, user_with_release):
        """POST /api/payments/checkout - creates Stripe checkout (free tier)"""
        response = requests.post(f"{BASE_URL}/api/payments/checkout", json={
            "release_id": user_with_release["release_id"],
            "origin_url": "https://artist-hub-219.preview.emergentagent.com"
        }, headers={"Authorization": f"Bearer {user_with_release['token']}"})
        assert response.status_code == 200, f"Checkout failed: {response.text}"
        data = response.json()
        # Free tier users get free tier activated
        assert "message" in data or "checkout_url" in data
        print(f"✓ POST /api/payments/checkout response: {data}")


class TestWalletEndpoints:
    """Wallet endpoint"""
    
    @pytest.fixture
    def user_token(self):
        import uuid
        email = f"test_wallet_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": "TestPass123!",
            "name": "Wallet Tester"
        })
        return response.json()["access_token"]
    
    def test_get_wallet(self, user_token):
        """GET /api/wallet - returns wallet"""
        response = requests.get(f"{BASE_URL}/api/wallet", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert response.status_code == 200, f"Get wallet failed: {response.text}"
        data = response.json()
        assert "balance" in data
        assert "pending_balance" in data
        assert "currency" in data
        assert data["currency"] == "USD"
        print(f"✓ GET /api/wallet returned balance: ${data['balance']}")


class TestAnalyticsEndpoints:
    """Analytics overview endpoint"""
    
    @pytest.fixture
    def user_token(self):
        import uuid
        email = f"test_analytics_{uuid.uuid4().hex[:8]}@test.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": "TestPass123!",
            "name": "Analytics Tester"
        })
        return response.json()["access_token"]
    
    def test_get_analytics_overview(self, user_token):
        """GET /api/analytics/overview - returns analytics"""
        response = requests.get(f"{BASE_URL}/api/analytics/overview", headers={
            "Authorization": f"Bearer {user_token}"
        })
        assert response.status_code == 200, f"Get analytics failed: {response.text}"
        data = response.json()
        assert "total_streams" in data
        assert "total_downloads" in data
        assert "total_earnings" in data
        assert "streams_by_store" in data
        assert "streams_by_country" in data
        print(f"✓ GET /api/analytics/overview returned: streams={data['total_streams']}, earnings=${data['total_earnings']}")


class TestSubscriptionEndpoints:
    """Subscription plans endpoint"""
    
    def test_get_subscription_plans(self):
        """GET /api/subscriptions/plans - returns plans"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/plans")
        assert response.status_code == 200, f"Get plans failed: {response.text}"
        data = response.json()
        assert "free" in data
        assert "rise" in data
        assert "pro" in data
        assert data["free"]["price"] == 0
        assert data["rise"]["price"] == 9.99
        assert data["pro"]["price"] == 19.99
        print(f"✓ GET /api/subscriptions/plans returned: {list(data.keys())}")


class TestAdminEndpoints:
    """Admin dashboard and users endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json()["access_token"]
    
    def test_admin_dashboard(self, admin_token):
        """GET /api/admin/dashboard - admin stats"""
        response = requests.get(f"{BASE_URL}/api/admin/dashboard", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"Admin dashboard failed: {response.text}"
        data = response.json()
        assert "total_users" in data
        assert "total_releases" in data
        assert "total_tracks" in data
        assert "pending_submissions" in data
        print(f"✓ GET /api/admin/dashboard: users={data['total_users']}, releases={data['total_releases']}")
    
    def test_admin_list_users(self, admin_token):
        """GET /api/admin/users - list users"""
        response = requests.get(f"{BASE_URL}/api/admin/users", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"Admin users failed: {response.text}"
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert isinstance(data["users"], list)
        print(f"✓ GET /api/admin/users returned {len(data['users'])} users (total: {data['total']})")
    
    def test_admin_dashboard_without_auth(self):
        """GET /api/admin/dashboard without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/admin/dashboard")
        assert response.status_code == 401
        print("✓ GET /api/admin/dashboard without auth correctly returns 401")
    
    def test_admin_dashboard_non_admin(self):
        """GET /api/admin/dashboard as non-admin returns 403"""
        import uuid
        email = f"test_nonadmin_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": "TestPass123!",
            "name": "Non Admin"
        })
        token = reg_resp.json()["access_token"]
        
        response = requests.get(f"{BASE_URL}/api/admin/dashboard", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 403
        print("✓ GET /api/admin/dashboard as non-admin correctly returns 403")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
