import requests
import sys
import json
from datetime import datetime

class TuneDropAPITester:
    def __init__(self, base_url="https://artist-hub-219.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def run_test(self, name, method, endpoint, expected_status, data=None, auth_required=True):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(response_data) <= 5:
                        print(f"   Response: {response_data}")
                except:
                    pass
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response text: {response.text[:200]}")

            return success, response.json() if response.content else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health check"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200,
            auth_required=False
        )
        return success

    def test_register(self, name="Test User", email=None, password="TestPass123!"):
        """Test user registration"""
        if not email:
            timestamp = datetime.now().strftime('%H%M%S')
            email = f"test_user_{timestamp}@example.com"
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "name": name,
                "artist_name": f"{name} Artist",
                "email": email,
                "password": password
            },
            auth_required=False
        )
        
        if success and 'id' in response:
            self.user_id = response['id']
            print(f"   Created user: {email}")
        
        return success, response

    def test_login(self, email, password):
        """Test user login"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={"email": email, "password": password},
            auth_required=False
        )
        
        # For cookie-based auth, we need to extract from cookies
        if success:
            print("   Login successful - using cookie-based auth")
        
        return success, response

    def test_admin_login(self):
        """Test admin login with credentials from test_credentials.md"""
        return self.test_login("admin@tunedrop.com", "Admin123!")

    def test_get_me(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success, response

    def test_create_release(self):
        """Test creating a new release"""
        success, response = self.run_test(
            "Create Release",
            "POST",
            "releases",
            200,
            data={
                "title": "Test Release",
                "release_type": "single",
                "genre": "Pop",
                "release_date": "2024-12-31",
                "description": "A test release for API testing",
                "explicit": False,
                "language": "en"
            }
        )
        return success, response

    def test_get_releases(self):
        """Test getting user's releases"""
        success, response = self.run_test(
            "Get Releases",
            "GET",
            "releases",
            200
        )
        return success, response

    def test_analytics_overview(self):
        """Test analytics overview endpoint"""
        success, response = self.run_test(
            "Analytics Overview",
            "GET",
            "analytics/overview",
            200
        )
        return success, response

    def test_wallet(self):
        """Test wallet endpoint"""
        success, response = self.run_test(
            "Get Wallet",
            "GET",
            "wallet",
            200
        )
        return success, response

    def test_subscription_plans(self):
        """Test subscription plans endpoint"""
        success, response = self.run_test(
            "Get Subscription Plans",
            "GET",
            "subscriptions/plans",
            200,
            auth_required=False
        )
        return success, response

    def test_distribution_stores(self):
        """Test distribution stores endpoint"""
        success, response = self.run_test(
            "Get Distribution Stores",
            "GET",
            "distributions/stores",
            200,
            auth_required=False
        )
        return success, response

def main():
    print("🎵 TuneDrop API Testing Suite")
    print("=" * 50)
    
    tester = TuneDropAPITester()
    
    # Test 1: Health Check
    if not tester.test_health_check():
        print("❌ Health check failed - API may be down")
        return 1

    # Test 2: Public endpoints
    tester.test_subscription_plans()
    tester.test_distribution_stores()

    # Test 3: Admin Login
    admin_success, admin_response = tester.test_admin_login()
    if not admin_success:
        print("❌ Admin login failed - cannot test authenticated endpoints")
        return 1

    # Test 4: Get current user info
    tester.test_get_me()

    # Test 5: Create and manage releases
    release_success, release_response = tester.test_create_release()
    if release_success:
        tester.test_get_releases()

    # Test 6: Analytics and wallet
    tester.test_analytics_overview()
    tester.test_wallet()

    # Test 7: User registration (create new user)
    reg_success, reg_response = tester.test_register()
    if reg_success:
        # Test login with new user
        new_email = reg_response.get('email')
        if new_email:
            tester.test_login(new_email, "TestPass123!")

    # Print results
    print(f"\n📊 Test Results")
    print("=" * 30)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Backend API tests mostly successful")
        return 0
    else:
        print("❌ Backend API tests have significant failures")
        return 1

if __name__ == "__main__":
    sys.exit(main())