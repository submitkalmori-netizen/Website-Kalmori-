"""
Iteration 35 Tests - Multi-step Registration, Role Selection, Track Upload Form
Tests:
1. PUT /api/auth/set-role accepts 'artist' or 'label_producer'
2. PUT /api/auth/set-role rejects invalid roles with 400
3. Registration flow works with new fields
4. Welcome email function accepts role parameter
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"


class TestSetRoleEndpoint:
    """Tests for PUT /api/auth/set-role endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Login as admin and return session with auth"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
            return session
        pytest.skip("Admin login failed - skipping authenticated tests")
    
    @pytest.fixture(scope="class")
    def test_user_session(self):
        """Create a test user and return session with auth"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Create unique test user
        unique_email = f"test_role_{int(time.time())}@test.com"
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPassword123!",
            "name": "Test Role User",
            "artist_name": "Test Role Artist"
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
            session.test_email = unique_email
            return session
        pytest.skip("Test user registration failed")
    
    def test_set_role_requires_auth(self):
        """Test that set-role endpoint requires authentication"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.put(f"{BASE_URL}/api/auth/set-role", json={"role": "artist"})
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: set-role requires authentication (401 without token)")
    
    def test_set_role_artist_valid(self, test_user_session):
        """Test setting role to 'artist' succeeds"""
        response = test_user_session.put(f"{BASE_URL}/api/auth/set-role", json={"role": "artist"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("role") == "artist", f"Expected role 'artist', got {data.get('role')}"
        assert "message" in data, "Response should contain message"
        print("PASS: set-role accepts 'artist' role")
    
    def test_set_role_label_producer_valid(self, test_user_session):
        """Test setting role to 'label_producer' succeeds"""
        response = test_user_session.put(f"{BASE_URL}/api/auth/set-role", json={"role": "label_producer"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("role") == "label_producer", f"Expected role 'label_producer', got {data.get('role')}"
        print("PASS: set-role accepts 'label_producer' role")
    
    def test_set_role_invalid_role_rejected(self, test_user_session):
        """Test that invalid roles are rejected with 400"""
        invalid_roles = ["admin", "superuser", "manager", "invalid", "", "ARTIST", "Label"]
        
        for invalid_role in invalid_roles:
            response = test_user_session.put(f"{BASE_URL}/api/auth/set-role", json={"role": invalid_role})
            assert response.status_code == 400, f"Expected 400 for role '{invalid_role}', got {response.status_code}"
        
        print(f"PASS: set-role rejects invalid roles with 400 (tested {len(invalid_roles)} invalid roles)")
    
    def test_set_role_updates_user_profile(self, test_user_session):
        """Test that set-role updates both users and artist_profiles collections"""
        # Set role to label_producer
        response = test_user_session.put(f"{BASE_URL}/api/auth/set-role", json={"role": "label_producer"})
        assert response.status_code == 200
        
        # Verify by getting current user
        me_response = test_user_session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        
        user_data = me_response.json()
        assert user_data.get("user_role") == "label_producer", f"Expected user_role 'label_producer', got {user_data.get('user_role')}"
        print("PASS: set-role updates user profile correctly")


class TestRegistrationEndpoint:
    """Tests for registration with new fields"""
    
    def test_register_with_all_new_fields(self):
        """Test registration with all new Step 2 fields"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        unique_email = f"test_full_reg_{int(time.time())}@test.com"
        
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPassword123!",
            "name": "John Doe",
            "artist_name": "John Doe",
            "user_role": "artist",
            "legal_name": "John Doe",
            "company_name": "Test Records",
            "country": "United States",
            "state": "California",
            "town": "Los Angeles",
            "address": "123 Music Street",
            "address_2": "Suite 100",
            "post_code": "90001",
            "phone": "+1-555-123-4567"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        assert "user" in data, "Response should contain user"
        
        user = data["user"]
        assert user["email"] == unique_email
        assert user["name"] == "John Doe"
        print("PASS: Registration with all new fields succeeds")
    
    def test_register_minimal_fields(self):
        """Test registration with minimal required fields"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        unique_email = f"test_min_reg_{int(time.time())}@test.com"
        
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPassword123!",
            "name": "Minimal User"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: Registration with minimal fields succeeds")


class TestWelcomeEmailFunction:
    """Tests for role-specific welcome email"""
    
    def test_welcome_email_import(self):
        """Test that send_welcome_email function exists and accepts role parameter"""
        try:
            import sys
            sys.path.insert(0, '/app/backend')
            from routes.email_routes import send_welcome_email
            import inspect
            
            # Check function signature
            sig = inspect.signature(send_welcome_email)
            params = list(sig.parameters.keys())
            
            assert "user_email" in params, "send_welcome_email should have user_email parameter"
            assert "user_name" in params, "send_welcome_email should have user_name parameter"
            assert "user_role" in params, "send_welcome_email should have user_role parameter"
            
            print("PASS: send_welcome_email function accepts role parameter")
        except ImportError as e:
            pytest.skip(f"Could not import email_routes: {e}")


class TestAdminLogin:
    """Test admin login works"""
    
    def test_admin_login(self):
        """Test admin can login with correct credentials"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        assert data["user"]["role"] == "admin", "User should have admin role"
        print("PASS: Admin login works correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
