"""
Iteration 9 Tests - New Endpoints from GitHub api.ts Port
Tests for: /api/stats, /api/genres, /api/transactions, /api/payment-methods/{id}/set-default,
/api/analytics/streaming/{userId}, /api/artists/{id}/followers, /api/artists/{id}/following,
/api/withdrawals (POST and GET)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestNewEndpointsIteration9:
    """Test new endpoints added in iteration 9"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login and get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        login_data = login_response.json()
        self.token = login_data.get("access_token")
        self.user = login_data.get("user", {})
        self.user_id = self.user.get("id")
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}
        
    # ==================== GET /api/stats ====================
    
    def test_get_stats_returns_expected_fields(self):
        """GET /api/stats should return stats with all expected fields"""
        response = self.session.get(
            f"{BASE_URL}/api/stats",
            headers=self.auth_headers
        )
        assert response.status_code == 200, f"Stats failed: {response.text}"
        data = response.json()
        
        # Verify all expected fields exist
        assert "total_releases" in data, "Missing total_releases"
        assert "total_tracks" in data, "Missing total_tracks"
        assert "total_earnings" in data, "Missing total_earnings"
        assert "total_streams" in data, "Missing total_streams"
        assert "total_downloads" in data, "Missing total_downloads"
        assert "follower_count" in data, "Missing follower_count"
        
        # Verify types
        assert isinstance(data["total_releases"], int)
        assert isinstance(data["total_tracks"], int)
        assert isinstance(data["total_earnings"], (int, float))
        assert isinstance(data["total_streams"], int)
        assert isinstance(data["total_downloads"], int)
        assert isinstance(data["follower_count"], int)
        print(f"Stats response: {data}")
        
    def test_get_stats_requires_auth(self):
        """GET /api/stats should require authentication"""
        clean = requests.Session()
        response = clean.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 401, f"Stats should require auth, got {response.status_code}"
        
    # ==================== GET /api/genres ====================
    
    def test_get_genres_returns_array(self):
        """GET /api/genres should return array of genre strings"""
        response = self.session.get(f"{BASE_URL}/api/genres")
        assert response.status_code == 200, f"Genres failed: {response.text}"
        data = response.json()
        
        # Verify it's a list
        assert isinstance(data, list), "Genres should be a list"
        assert len(data) > 0, "Genres list should not be empty"
        
        # Verify all items are strings
        for genre in data:
            assert isinstance(genre, str), f"Genre should be string: {genre}"
        
        # Verify some expected genres exist
        expected_genres = ["Hip-Hop/Rap", "R&B/Soul", "Pop", "Rock", "Electronic"]
        for expected in expected_genres:
            assert expected in data, f"Missing expected genre: {expected}"
        
        print(f"Genres count: {len(data)}, Sample: {data[:5]}")
        
    def test_get_genres_is_public(self):
        """GET /api/genres should be public (no auth required)"""
        # Already tested above without auth headers
        response = requests.get(f"{BASE_URL}/api/genres")
        assert response.status_code == 200
        
    # ==================== GET /api/transactions ====================
    
    def test_get_transactions_returns_array(self):
        """GET /api/transactions should return array of transactions"""
        response = self.session.get(
            f"{BASE_URL}/api/transactions",
            headers=self.auth_headers
        )
        assert response.status_code == 200, f"Transactions failed: {response.text}"
        data = response.json()
        
        # Verify it's a list
        assert isinstance(data, list), "Transactions should be a list"
        print(f"Transactions count: {len(data)}")
        
    def test_get_transactions_requires_auth(self):
        """GET /api/transactions should require authentication"""
        clean = requests.Session()
        response = clean.get(f"{BASE_URL}/api/transactions")
        assert response.status_code == 401, f"Transactions should require auth, got {response.status_code}"
        
    # ==================== PUT /api/payment-methods/{id}/set-default ====================
    
    def test_set_default_payment_method_flow(self):
        """Test full flow: create payment method, set as default, verify"""
        # First, create a payment method
        create_response = self.session.post(
            f"{BASE_URL}/api/payment-methods",
            headers=self.auth_headers,
            json={
                "method_type": "paypal",
                "paypal_email": "test_iteration9@example.com"
            }
        )
        assert create_response.status_code == 200, f"Create payment method failed: {create_response.text}"
        method = create_response.json()
        method_id = method.get("id")
        assert method_id, "Payment method should have ID"
        
        # Set as default
        set_default_response = self.session.put(
            f"{BASE_URL}/api/payment-methods/{method_id}/set-default",
            headers=self.auth_headers
        )
        assert set_default_response.status_code == 200, f"Set default failed: {set_default_response.text}"
        result = set_default_response.json()
        assert "message" in result, "Should return message"
        
        # Verify it's now default
        list_response = self.session.get(
            f"{BASE_URL}/api/payment-methods",
            headers=self.auth_headers
        )
        assert list_response.status_code == 200
        methods = list_response.json()
        
        # Find our method and verify it's default
        our_method = next((m for m in methods if m["id"] == method_id), None)
        assert our_method, "Our payment method should exist"
        assert our_method.get("is_default") == True, "Method should be default"
        
        # Cleanup: delete the test payment method
        self.session.delete(
            f"{BASE_URL}/api/payment-methods/{method_id}",
            headers=self.auth_headers
        )
        print(f"Set default payment method test passed for method {method_id}")
        
    def test_set_default_payment_method_not_found(self):
        """PUT /api/payment-methods/{id}/set-default should return 404 for invalid ID"""
        response = self.session.put(
            f"{BASE_URL}/api/payment-methods/invalid-id-12345/set-default",
            headers=self.auth_headers
        )
        assert response.status_code == 404, f"Should return 404: {response.text}"
        
    def test_set_default_payment_method_requires_auth(self):
        """PUT /api/payment-methods/{id}/set-default should require auth"""
        clean = requests.Session()
        response = clean.put(f"{BASE_URL}/api/payment-methods/some-id/set-default")
        assert response.status_code == 401, f"Should require auth, got {response.status_code}"
        
    # ==================== GET /api/analytics/streaming/{userId} ====================
    
    def test_get_streaming_analytics_returns_expected_structure(self):
        """GET /api/analytics/streaming/{userId} should return streaming analytics"""
        response = self.session.get(
            f"{BASE_URL}/api/analytics/streaming/{self.user_id}",
            headers=self.auth_headers
        )
        assert response.status_code == 200, f"Streaming analytics failed: {response.text}"
        data = response.json()
        
        # Verify expected fields
        assert "total_streams" in data, "Missing total_streams"
        assert "total_revenue" in data, "Missing total_revenue"
        assert "platforms" in data, "Missing platforms"
        assert "top_tracks" in data, "Missing top_tracks"
        assert "monthly_data" in data, "Missing monthly_data"
        
        # Verify platforms structure
        assert isinstance(data["platforms"], list), "Platforms should be list"
        if len(data["platforms"]) > 0:
            platform = data["platforms"][0]
            assert "name" in platform, "Platform should have name"
            assert "streams" in platform, "Platform should have streams"
            assert "revenue" in platform, "Platform should have revenue"
            assert "color" in platform, "Platform should have color"
        
        print(f"Streaming analytics: total_streams={data['total_streams']}, platforms={len(data['platforms'])}")
        
    def test_get_streaming_analytics_requires_auth(self):
        """GET /api/analytics/streaming/{userId} should require auth"""
        clean = requests.Session()
        response = clean.get(f"{BASE_URL}/api/analytics/streaming/{self.user_id}")
        assert response.status_code == 401, f"Should require auth, got {response.status_code}"
        
    # ==================== GET /api/artists/{id}/followers ====================
    
    def test_get_followers_list_returns_array(self):
        """GET /api/artists/{id}/followers should return followers list"""
        response = self.session.get(f"{BASE_URL}/api/artists/{self.user_id}/followers")
        assert response.status_code == 200, f"Followers list failed: {response.text}"
        data = response.json()
        
        # Verify it's a list
        assert isinstance(data, list), "Followers should be a list"
        
        # If there are followers, verify structure
        if len(data) > 0:
            follower = data[0]
            assert "id" in follower, "Follower should have id"
            # name and artist_name may be empty strings
            assert "name" in follower or "artist_name" in follower, "Follower should have name or artist_name"
        
        print(f"Followers count: {len(data)}")
        
    def test_get_followers_list_is_public(self):
        """GET /api/artists/{id}/followers should be public"""
        response = requests.get(f"{BASE_URL}/api/artists/{self.user_id}/followers")
        assert response.status_code == 200
        
    # ==================== GET /api/artists/{id}/following ====================
    
    def test_get_following_list_returns_array(self):
        """GET /api/artists/{id}/following should return following list"""
        response = self.session.get(f"{BASE_URL}/api/artists/{self.user_id}/following")
        assert response.status_code == 200, f"Following list failed: {response.text}"
        data = response.json()
        
        # Verify it's a list
        assert isinstance(data, list), "Following should be a list"
        
        # If there are following, verify structure
        if len(data) > 0:
            following = data[0]
            assert "id" in following, "Following should have id"
        
        print(f"Following count: {len(data)}")
        
    def test_get_following_list_is_public(self):
        """GET /api/artists/{id}/following should be public"""
        response = requests.get(f"{BASE_URL}/api/artists/{self.user_id}/following")
        assert response.status_code == 200
        
    # ==================== POST /api/withdrawals ====================
    
    def test_post_withdrawals_requires_payment_method(self):
        """POST /api/withdrawals should require payment_method_id"""
        response = self.session.post(
            f"{BASE_URL}/api/withdrawals",
            headers=self.auth_headers,
            json={"amount": 50}
        )
        assert response.status_code == 400, f"Should require payment method: {response.text}"
        
    def test_post_withdrawals_validates_minimum_amount(self):
        """POST /api/withdrawals should validate minimum $10"""
        # First create a payment method
        create_response = self.session.post(
            f"{BASE_URL}/api/payment-methods",
            headers=self.auth_headers,
            json={
                "method_type": "paypal",
                "paypal_email": "withdrawal_test@example.com"
            }
        )
        method_id = create_response.json().get("id")
        
        # Try withdrawal with amount < $10
        response = self.session.post(
            f"{BASE_URL}/api/withdrawals",
            headers=self.auth_headers,
            json={"amount": 5, "payment_method_id": method_id}
        )
        assert response.status_code == 400, f"Should reject amount < $10: {response.text}"
        detail = response.json().get("detail", "")
        assert "Minimum" in detail or "Insufficient" in detail, f"Should mention minimum or insufficient, got: {detail}"
        
        # Cleanup
        self.session.delete(
            f"{BASE_URL}/api/payment-methods/{method_id}",
            headers=self.auth_headers
        )
        
    def test_post_withdrawals_requires_auth(self):
        """POST /api/withdrawals should require auth"""
        clean = requests.Session()
        clean.headers.update({"Content-Type": "application/json"})
        response = clean.post(
            f"{BASE_URL}/api/withdrawals",
            json={"amount": 50, "payment_method_id": "some-id"}
        )
        assert response.status_code == 401, f"Should require auth, got {response.status_code}"
        
    # ==================== GET /api/withdrawals ====================
    
    def test_get_withdrawals_returns_array(self):
        """GET /api/withdrawals should return withdrawals list"""
        response = self.session.get(
            f"{BASE_URL}/api/withdrawals",
            headers=self.auth_headers
        )
        assert response.status_code == 200, f"Withdrawals list failed: {response.text}"
        data = response.json()
        
        # Verify it's a list
        assert isinstance(data, list), "Withdrawals should be a list"
        
        # If there are withdrawals, verify structure
        if len(data) > 0:
            withdrawal = data[0]
            assert "id" in withdrawal, "Withdrawal should have id"
            assert "amount" in withdrawal, "Withdrawal should have amount"
            assert "status" in withdrawal, "Withdrawal should have status"
        
        print(f"Withdrawals count: {len(data)}")
        
    def test_get_withdrawals_requires_auth(self):
        """GET /api/withdrawals should require auth"""
        clean = requests.Session()
        response = clean.get(f"{BASE_URL}/api/withdrawals")
        assert response.status_code == 401, f"Should require auth, got {response.status_code}"


class TestFrontendApiServiceMethods:
    """Test that frontend api.js methods work correctly with backend"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login and get auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200
        login_data = login_response.json()
        self.token = login_data.get("access_token")
        self.user = login_data.get("user", {})
        self.user_id = self.user.get("id")
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}
        
    def test_api_getStats_method(self):
        """Test api.getStats() method from api.js"""
        response = self.session.get(
            f"{BASE_URL}/api/stats",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # Matches api.js getStats() expected response
        required_fields = ["total_releases", "total_tracks", "total_earnings", 
                          "total_streams", "total_downloads", "follower_count"]
        for field in required_fields:
            assert field in data, f"api.getStats() missing {field}"
            
    def test_api_getGenres_method(self):
        """Test api.getGenres() method from api.js"""
        response = self.session.get(f"{BASE_URL}/api/genres")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
    def test_api_getTransactions_method(self):
        """Test api.getTransactions() method from api.js"""
        response = self.session.get(
            f"{BASE_URL}/api/transactions",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_api_setDefaultPaymentMethod_method(self):
        """Test api.setDefaultPaymentMethod(id) method from api.js"""
        # Create a payment method first
        create_response = self.session.post(
            f"{BASE_URL}/api/payment-methods",
            headers=self.auth_headers,
            json={"method_type": "paypal", "paypal_email": "api_test@example.com"}
        )
        method_id = create_response.json().get("id")
        
        # Test setDefaultPaymentMethod
        response = self.session.put(
            f"{BASE_URL}/api/payment-methods/{method_id}/set-default",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/payment-methods/{method_id}", headers=self.auth_headers)
        
    def test_api_getStreamingAnalytics_method(self):
        """Test api.getStreamingAnalytics(userId) method from api.js"""
        response = self.session.get(
            f"{BASE_URL}/api/analytics/streaming/{self.user_id}",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "platforms" in data
        
    def test_api_getFollowers_method(self):
        """Test api.getFollowers(artistId) method from api.js"""
        response = self.session.get(f"{BASE_URL}/api/artists/{self.user_id}/followers")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        
    def test_api_getFollowing_method(self):
        """Test api.getFollowing(artistId) method from api.js"""
        response = self.session.get(f"{BASE_URL}/api/artists/{self.user_id}/following")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        
    def test_api_getWithdrawals_method(self):
        """Test api.getWithdrawals() method from api.js"""
        response = self.session.get(
            f"{BASE_URL}/api/withdrawals",
            headers=self.auth_headers
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
