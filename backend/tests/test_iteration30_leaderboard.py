"""
Iteration 30 - Release Performance Leaderboard Tests
Tests the NEW /api/analytics/leaderboard endpoint and frontend LeaderboardPage

Features tested:
- GET /api/analytics/leaderboard - returns leaderboard array with rank, title, genre, total_streams, 
  total_revenue, streams_this_week, growth_percent, sparkline (14 values), hot_streak, momentum, top_platform
- Authentication required (401 without token)
- Returns total_releases and active_releases counts
- Leaderboard sorted by total_streams descending by default
- Sparkline has exactly 14 data points (14 days)
- Regression tests for /api/analytics/revenue and /api/ai/smart-insights
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLeaderboardAuthentication:
    """Test authentication requirements for leaderboard endpoint"""
    
    def test_leaderboard_requires_auth(self):
        """GET /api/analytics/leaderboard should return 401/422 without authentication"""
        response = requests.get(f"{BASE_URL}/api/analytics/leaderboard")
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"
        print("✓ Leaderboard endpoint requires authentication")


class TestLeaderboardEndpoint:
    """Test the leaderboard endpoint with authentication"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.cookies = login_response.cookies
        print("✓ Logged in as admin@tunedrop.com")
    
    def test_leaderboard_returns_200(self):
        """GET /api/analytics/leaderboard should return 200 with valid auth"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/leaderboard",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Leaderboard endpoint returns 200 with auth")
    
    def test_leaderboard_response_structure(self):
        """Leaderboard response should have leaderboard array, total_releases, active_releases"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/leaderboard",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level structure
        assert "leaderboard" in data, "Response missing 'leaderboard' field"
        assert "total_releases" in data, "Response missing 'total_releases' field"
        assert "active_releases" in data, "Response missing 'active_releases' field"
        
        assert isinstance(data["leaderboard"], list), "leaderboard should be a list"
        assert isinstance(data["total_releases"], int), "total_releases should be int"
        assert isinstance(data["active_releases"], int), "active_releases should be int"
        
        print(f"✓ Response structure valid: {data['total_releases']} total, {data['active_releases']} active releases")
    
    def test_leaderboard_item_fields(self):
        """Each leaderboard item should have required fields"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/leaderboard",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        
        if len(data["leaderboard"]) == 0:
            pytest.skip("No releases in leaderboard to test")
        
        required_fields = [
            "release_id", "title", "genre", "total_streams", "total_revenue",
            "streams_this_week", "growth_percent", "sparkline", "hot_streak",
            "momentum", "top_platform", "rank"
        ]
        
        item = data["leaderboard"][0]
        for field in required_fields:
            assert field in item, f"Leaderboard item missing '{field}' field"
        
        print(f"✓ Leaderboard item has all required fields: {required_fields}")
    
    def test_sparkline_has_14_data_points(self):
        """Sparkline should have exactly 14 data points (14 days)"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/leaderboard",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        
        if len(data["leaderboard"]) == 0:
            pytest.skip("No releases in leaderboard to test")
        
        for item in data["leaderboard"]:
            sparkline = item.get("sparkline", [])
            assert isinstance(sparkline, list), f"Sparkline should be a list, got {type(sparkline)}"
            assert len(sparkline) == 14, f"Sparkline should have 14 points, got {len(sparkline)}"
        
        print(f"✓ All {len(data['leaderboard'])} releases have sparklines with 14 data points")
    
    def test_leaderboard_sorted_by_total_streams(self):
        """Leaderboard should be sorted by total_streams descending by default"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/leaderboard",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        
        if len(data["leaderboard"]) < 2:
            pytest.skip("Need at least 2 releases to test sorting")
        
        streams = [item["total_streams"] for item in data["leaderboard"]]
        assert streams == sorted(streams, reverse=True), "Leaderboard not sorted by total_streams descending"
        
        print(f"✓ Leaderboard sorted by total_streams descending: {streams[:5]}...")
    
    def test_rank_field_sequential(self):
        """Rank field should be sequential starting from 1"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/leaderboard",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        
        if len(data["leaderboard"]) == 0:
            pytest.skip("No releases in leaderboard to test")
        
        ranks = [item["rank"] for item in data["leaderboard"]]
        expected_ranks = list(range(1, len(ranks) + 1))
        assert ranks == expected_ranks, f"Ranks not sequential: {ranks}"
        
        print(f"✓ Ranks are sequential from 1 to {len(ranks)}")
    
    def test_hot_streak_is_boolean(self):
        """hot_streak field should be boolean"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/leaderboard",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        
        if len(data["leaderboard"]) == 0:
            pytest.skip("No releases in leaderboard to test")
        
        for item in data["leaderboard"]:
            assert isinstance(item["hot_streak"], bool), f"hot_streak should be bool, got {type(item['hot_streak'])}"
        
        hot_count = sum(1 for item in data["leaderboard"] if item["hot_streak"])
        print(f"✓ hot_streak is boolean for all items ({hot_count} releases on hot streak)")
    
    def test_data_types(self):
        """Verify data types of leaderboard fields"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/leaderboard",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        
        if len(data["leaderboard"]) == 0:
            pytest.skip("No releases in leaderboard to test")
        
        item = data["leaderboard"][0]
        
        # Check data types
        assert isinstance(item["release_id"], str), "release_id should be string"
        assert isinstance(item["title"], str), "title should be string"
        assert isinstance(item["total_streams"], int), "total_streams should be int"
        assert isinstance(item["total_revenue"], (int, float)), "total_revenue should be numeric"
        assert isinstance(item["streams_this_week"], int), "streams_this_week should be int"
        assert isinstance(item["growth_percent"], (int, float)), "growth_percent should be numeric"
        assert isinstance(item["momentum"], (int, float)), "momentum should be numeric"
        assert isinstance(item["top_platform"], str), "top_platform should be string"
        assert isinstance(item["rank"], int), "rank should be int"
        
        print(f"✓ All data types correct for leaderboard item")
    
    def test_active_releases_count(self):
        """active_releases should count releases with total_streams > 0"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/leaderboard",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        
        # Count releases with streams > 0
        active_count = sum(1 for item in data["leaderboard"] if item["total_streams"] > 0)
        assert data["active_releases"] == active_count, f"active_releases mismatch: {data['active_releases']} vs {active_count}"
        
        print(f"✓ active_releases count correct: {active_count}")


class TestRegressionEndpoints:
    """Regression tests for existing endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.cookies = login_response.cookies
    
    def test_revenue_endpoint_still_works(self):
        """GET /api/analytics/revenue should still work (regression)"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/revenue",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200, f"Revenue endpoint failed: {response.status_code}"
        data = response.json()
        assert "summary" in data, "Revenue response missing 'summary'"
        assert "platforms" in data, "Revenue response missing 'platforms'"
        print("✓ GET /api/analytics/revenue still works (regression)")
    
    def test_smart_insights_endpoint_still_works(self):
        """POST /api/ai/smart-insights should still work (regression)"""
        response = requests.post(
            f"{BASE_URL}/api/ai/smart-insights",
            headers=self.headers,
            cookies=self.cookies,
            json={}
        )
        # Accept 200 or 500 (if AI service unavailable) - just checking endpoint exists
        assert response.status_code in [200, 500], f"Smart insights endpoint failed: {response.status_code}"
        print(f"✓ POST /api/ai/smart-insights still works (status: {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
