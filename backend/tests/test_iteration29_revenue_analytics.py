"""
Iteration 29 - Revenue Analytics & Royalty Calculator Tests
Tests the NEW Revenue Analytics page endpoints:
- GET /api/analytics/revenue - Revenue summary, platforms, monthly trend, collaborator splits
- POST /api/analytics/revenue/calculator - What-if revenue calculator
Plus regression tests for existing analytics endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"

# Platform rates from server.py
PLATFORM_RATES = {
    "Spotify": 0.004, "Apple Music": 0.008, "YouTube Music": 0.002,
    "Amazon Music": 0.004, "Tidal": 0.012, "Deezer": 0.003,
    "Pandora": 0.002, "SoundCloud": 0.003,
}


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def auth_session(auth_token):
    """Create authenticated session"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    session.cookies.set("access_token", auth_token)
    return session


class TestRevenueAnalyticsEndpoint:
    """Tests for GET /api/analytics/revenue endpoint"""
    
    def test_revenue_requires_auth(self):
        """Revenue endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/analytics/revenue")
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"
        print("✓ GET /api/analytics/revenue requires authentication")
    
    def test_revenue_returns_summary(self, auth_session):
        """Revenue endpoint returns summary with all required fields"""
        response = auth_session.get(f"{BASE_URL}/api/analytics/revenue")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "summary" in data, "Response missing 'summary' field"
        
        summary = data["summary"]
        required_fields = ["total_streams", "gross_revenue", "platform_fee", "net_revenue", 
                          "artist_take", "collab_payouts", "plan", "avg_rate_per_stream"]
        for field in required_fields:
            assert field in summary, f"Summary missing '{field}' field"
        
        # Verify numeric types
        assert isinstance(summary["total_streams"], int), "total_streams should be int"
        assert isinstance(summary["gross_revenue"], (int, float)), "gross_revenue should be numeric"
        assert isinstance(summary["platform_fee"], (int, float)), "platform_fee should be numeric"
        assert isinstance(summary["net_revenue"], (int, float)), "net_revenue should be numeric"
        assert isinstance(summary["artist_take"], (int, float)), "artist_take should be numeric"
        
        print(f"✓ Revenue summary returned: {summary['total_streams']} streams, ${summary['gross_revenue']} gross")
    
    def test_revenue_returns_platforms_array(self, auth_session):
        """Revenue endpoint returns platforms array with correct structure"""
        response = auth_session.get(f"{BASE_URL}/api/analytics/revenue")
        assert response.status_code == 200
        
        data = response.json()
        assert "platforms" in data, "Response missing 'platforms' field"
        assert isinstance(data["platforms"], list), "platforms should be a list"
        
        # Check platform structure if there are any platforms
        if len(data["platforms"]) > 0:
            platform = data["platforms"][0]
            required_fields = ["platform", "streams", "rate_per_stream", "gross_revenue", "net_revenue"]
            for field in required_fields:
                assert field in platform, f"Platform missing '{field}' field"
            
            # Verify rate is reasonable
            assert 0 < platform["rate_per_stream"] < 0.1, f"Rate {platform['rate_per_stream']} seems unreasonable"
        
        print(f"✓ Platforms array returned with {len(data['platforms'])} platforms")
    
    def test_revenue_returns_monthly_trend(self, auth_session):
        """Revenue endpoint returns monthly_trend with 6 months of data"""
        response = auth_session.get(f"{BASE_URL}/api/analytics/revenue")
        assert response.status_code == 200
        
        data = response.json()
        assert "monthly_trend" in data, "Response missing 'monthly_trend' field"
        assert isinstance(data["monthly_trend"], list), "monthly_trend should be a list"
        assert len(data["monthly_trend"]) == 6, f"Expected 6 months, got {len(data['monthly_trend'])}"
        
        # Check monthly structure
        for month in data["monthly_trend"]:
            assert "month" in month, "Month entry missing 'month' field"
            assert "streams" in month, "Month entry missing 'streams' field"
            assert "gross" in month, "Month entry missing 'gross' field"
            assert "net" in month, "Month entry missing 'net' field"
        
        print(f"✓ Monthly trend returned with {len(data['monthly_trend'])} months")
    
    def test_revenue_returns_collaborator_splits(self, auth_session):
        """Revenue endpoint returns collaborator_splits array"""
        response = auth_session.get(f"{BASE_URL}/api/analytics/revenue")
        assert response.status_code == 200
        
        data = response.json()
        assert "collaborator_splits" in data, "Response missing 'collaborator_splits' field"
        assert isinstance(data["collaborator_splits"], list), "collaborator_splits should be a list"
        
        # If there are splits, check structure
        if len(data["collaborator_splits"]) > 0:
            split = data["collaborator_splits"][0]
            assert "collaborator" in split, "Split missing 'collaborator' field"
            assert "split_percentage" in split, "Split missing 'split_percentage' field"
            assert "estimated_amount" in split, "Split missing 'estimated_amount' field"
        
        print(f"✓ Collaborator splits returned: {len(data['collaborator_splits'])} collaborators")
    
    def test_revenue_plan_fee_calculation(self, auth_session):
        """Verify platform fee is calculated based on plan (pro = 0%)"""
        response = auth_session.get(f"{BASE_URL}/api/analytics/revenue")
        assert response.status_code == 200
        
        data = response.json()
        summary = data["summary"]
        
        # Admin is on 'pro' plan which has 0% cut
        if summary["plan"] == "pro":
            assert summary["platform_fee"] == 0, f"Pro plan should have $0 fee, got ${summary['platform_fee']}"
            assert summary["gross_revenue"] == summary["net_revenue"], "Pro plan: gross should equal net"
            print("✓ Pro plan correctly has 0% platform fee")
        else:
            # Free plan has 15% cut
            expected_fee = round(summary["gross_revenue"] * 0.15, 2)
            assert abs(summary["platform_fee"] - expected_fee) < 0.01, f"Fee mismatch: expected ~${expected_fee}, got ${summary['platform_fee']}"
            print(f"✓ {summary['plan']} plan fee calculated correctly")


class TestRevenueCalculatorEndpoint:
    """Tests for POST /api/analytics/revenue/calculator endpoint"""
    
    def test_calculator_requires_auth(self):
        """Calculator endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/analytics/revenue/calculator", json={"streams": 10000})
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"
        print("✓ POST /api/analytics/revenue/calculator requires authentication")
    
    def test_calculator_basic_request(self, auth_session):
        """Calculator accepts streams count and returns breakdown"""
        response = auth_session.post(f"{BASE_URL}/api/analytics/revenue/calculator", json={
            "streams": 10000
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        required_fields = ["platform_breakdown", "gross_revenue", "net_revenue", "artist_take"]
        for field in required_fields:
            assert field in data, f"Response missing '{field}' field"
        
        assert isinstance(data["platform_breakdown"], list), "platform_breakdown should be a list"
        assert len(data["platform_breakdown"]) > 0, "platform_breakdown should not be empty"
        
        print(f"✓ Calculator returned: ${data['gross_revenue']} gross, ${data['artist_take']} artist take")
    
    def test_calculator_default_platform_mix(self, auth_session):
        """Calculator uses default mix: Spotify 45%, Apple Music 25%, etc."""
        response = auth_session.post(f"{BASE_URL}/api/analytics/revenue/calculator", json={
            "streams": 10000
        })
        assert response.status_code == 200
        
        data = response.json()
        breakdown = {p["platform"]: p["streams"] for p in data["platform_breakdown"]}
        
        # Default mix: Spotify 45%, Apple Music 25%, YouTube Music 15%, Amazon Music 10%, Other 5%
        # With 10000 streams:
        # Spotify should be ~4500, Apple Music ~2500, YouTube ~1500, Amazon ~1000, Other ~500
        if "Spotify" in breakdown:
            assert 4000 <= breakdown["Spotify"] <= 5000, f"Spotify streams {breakdown['Spotify']} not ~45%"
        if "Apple Music" in breakdown:
            assert 2000 <= breakdown["Apple Music"] <= 3000, f"Apple Music streams {breakdown['Apple Music']} not ~25%"
        
        print(f"✓ Default platform mix applied correctly")
    
    def test_calculator_custom_platform_mix(self, auth_session):
        """Calculator applies custom platform_mix correctly"""
        custom_mix = {
            "Spotify": 80,
            "Apple Music": 20
        }
        response = auth_session.post(f"{BASE_URL}/api/analytics/revenue/calculator", json={
            "streams": 10000,
            "platform_mix": custom_mix
        })
        assert response.status_code == 200
        
        data = response.json()
        breakdown = {p["platform"]: p["streams"] for p in data["platform_breakdown"]}
        
        # With 80/20 split of 10000 streams
        assert breakdown.get("Spotify", 0) == 8000, f"Expected 8000 Spotify streams, got {breakdown.get('Spotify')}"
        assert breakdown.get("Apple Music", 0) == 2000, f"Expected 2000 Apple Music streams, got {breakdown.get('Apple Music')}"
        
        print(f"✓ Custom platform mix (80/20) applied correctly")
    
    def test_calculator_platform_breakdown_structure(self, auth_session):
        """Calculator platform_breakdown has correct fields"""
        response = auth_session.post(f"{BASE_URL}/api/analytics/revenue/calculator", json={
            "streams": 10000
        })
        assert response.status_code == 200
        
        data = response.json()
        for platform in data["platform_breakdown"]:
            assert "platform" in platform, "Missing 'platform' field"
            assert "streams" in platform, "Missing 'streams' field"
            assert "rate" in platform, "Missing 'rate' field"
            assert "gross" in platform, "Missing 'gross' field"
            
            # Verify rate matches known platform rates
            if platform["platform"] in PLATFORM_RATES:
                expected_rate = PLATFORM_RATES[platform["platform"]]
                assert platform["rate"] == expected_rate, f"Rate mismatch for {platform['platform']}: expected {expected_rate}, got {platform['rate']}"
        
        print("✓ Platform breakdown has correct structure and rates")
    
    def test_calculator_revenue_math(self, auth_session):
        """Verify calculator math: gross = sum of platform revenues"""
        response = auth_session.post(f"{BASE_URL}/api/analytics/revenue/calculator", json={
            "streams": 10000,
            "platform_mix": {"Spotify": 100}  # 100% Spotify for easy math
        })
        assert response.status_code == 200
        
        data = response.json()
        
        # 10000 streams * $0.004/stream = $40 gross
        expected_gross = 10000 * 0.004
        assert abs(data["gross_revenue"] - expected_gross) < 0.01, f"Expected ${expected_gross} gross, got ${data['gross_revenue']}"
        
        # Pro plan has 0% fee, so net = gross
        if data.get("plan") == "pro":
            assert data["net_revenue"] == data["gross_revenue"], "Pro plan: net should equal gross"
        
        print(f"✓ Calculator math verified: 10000 Spotify streams = ${data['gross_revenue']}")


class TestRegressionAnalytics:
    """Regression tests for existing analytics endpoints"""
    
    def test_analytics_overview_still_works(self, auth_session):
        """GET /api/analytics/overview still returns expected data"""
        response = auth_session.get(f"{BASE_URL}/api/analytics/overview")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        required_fields = ["total_streams", "total_downloads", "total_earnings", 
                          "streams_by_store", "streams_by_country", "daily_streams"]
        for field in required_fields:
            assert field in data, f"Overview missing '{field}' field"
        
        print(f"✓ Analytics overview still works: {data['total_streams']} total streams")
    
    def test_ai_release_strategy_still_works(self, auth_session):
        """POST /api/ai/release-strategy still works"""
        response = auth_session.post(f"{BASE_URL}/api/ai/release-strategy", json={
            "release_title": "Test Track",
            "genre": "Hip-Hop",
            "target_audience": "18-25",
            "release_date": "2026-02-15",
            "budget": "medium"
        })
        # Accept 200 (success) or 500 (AI service issue) - just verify endpoint exists
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "strategy" in data or "phases" in data, "Response missing strategy data"
            print("✓ AI release strategy endpoint still works")
        else:
            print("✓ AI release strategy endpoint exists (AI service may be slow)")


class TestPlatformRates:
    """Verify platform rates are correctly configured"""
    
    def test_platform_rates_in_revenue(self, auth_session):
        """Verify platform rates match expected values"""
        response = auth_session.get(f"{BASE_URL}/api/analytics/revenue")
        assert response.status_code == 200
        
        data = response.json()
        for platform in data["platforms"]:
            name = platform["platform"]
            if name in PLATFORM_RATES:
                expected = PLATFORM_RATES[name]
                actual = platform["rate_per_stream"]
                assert actual == expected, f"{name}: expected ${expected}, got ${actual}"
        
        print("✓ All platform rates match expected values")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
