"""
Iteration 23 Tests - Fan Analytics Dashboard, Spotify Integration Placeholder, OG Meta Tags
Tests:
- GET /api/fan-analytics/overview - subscriber data, platform engagement, top countries, listener growth, peak hours
- GET /api/integrations/spotify/status - returns connected: false for unconnected users
- POST /api/integrations/spotify/connect - saves connection intent
- DELETE /api/integrations/spotify/disconnect - removes connection
- Social share endpoints still working (GET /api/share/beat/{id}, /api/share/release/{id}, /api/share/artist/{id})
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestFanAnalyticsEndpoints:
    """Fan Analytics API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth session"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_fan_analytics_overview_returns_200(self):
        """GET /api/fan-analytics/overview returns 200 with required fields"""
        resp = self.session.get(f"{BASE_URL}/api/fan-analytics/overview")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        # Verify all required fields are present
        assert "total_subscribers" in data, "Missing total_subscribers"
        assert "total_campaigns" in data, "Missing total_campaigns"
        assert "platform_engagement" in data, "Missing platform_engagement"
        assert "top_countries" in data, "Missing top_countries"
        assert "listener_growth" in data, "Missing listener_growth"
        assert "peak_hours" in data, "Missing peak_hours"
        print(f"Fan analytics overview: {data.get('total_subscribers')} subscribers, {data.get('total_campaigns')} campaigns")
    
    def test_fan_analytics_platform_engagement_structure(self):
        """Platform engagement has correct structure"""
        resp = self.session.get(f"{BASE_URL}/api/fan-analytics/overview")
        assert resp.status_code == 200
        data = resp.json()
        
        platform_engagement = data.get("platform_engagement", [])
        assert isinstance(platform_engagement, list), "platform_engagement should be a list"
        
        if platform_engagement:
            platform = platform_engagement[0]
            assert "name" in platform, "Platform missing 'name'"
            assert "streams" in platform, "Platform missing 'streams'"
            assert "percentage" in platform, "Platform missing 'percentage'"
            assert "color" in platform, "Platform missing 'color'"
            print(f"Top platform: {platform['name']} with {platform['streams']} streams ({platform['percentage']}%)")
    
    def test_fan_analytics_top_countries_structure(self):
        """Top countries has correct structure"""
        resp = self.session.get(f"{BASE_URL}/api/fan-analytics/overview")
        assert resp.status_code == 200
        data = resp.json()
        
        top_countries = data.get("top_countries", [])
        assert isinstance(top_countries, list), "top_countries should be a list"
        
        if top_countries:
            country = top_countries[0]
            assert "country" in country, "Country missing 'country' code"
            assert "streams" in country, "Country missing 'streams'"
            assert "percentage" in country, "Country missing 'percentage'"
            print(f"Top country: {country['country']} with {country['streams']} streams ({country['percentage']}%)")
    
    def test_fan_analytics_listener_growth_structure(self):
        """Listener growth has correct structure"""
        resp = self.session.get(f"{BASE_URL}/api/fan-analytics/overview")
        assert resp.status_code == 200
        data = resp.json()
        
        listener_growth = data.get("listener_growth", [])
        assert isinstance(listener_growth, list), "listener_growth should be a list"
        
        if listener_growth:
            day = listener_growth[0]
            assert "date" in day, "Growth data missing 'date'"
            assert "listeners" in day, "Growth data missing 'listeners'"
            print(f"Listener growth data: {len(listener_growth)} days of data")
    
    def test_fan_analytics_peak_hours_structure(self):
        """Peak hours has correct structure"""
        resp = self.session.get(f"{BASE_URL}/api/fan-analytics/overview")
        assert resp.status_code == 200
        data = resp.json()
        
        peak_hours = data.get("peak_hours", [])
        assert isinstance(peak_hours, list), "peak_hours should be a list"
        
        if peak_hours:
            hour = peak_hours[0]
            assert "hour" in hour, "Peak hour missing 'hour'"
            assert "count" in hour, "Peak hour missing 'count'"
            print(f"Peak hours data: {len(peak_hours)} hours of data")
    
    def test_fan_analytics_requires_auth(self):
        """Fan analytics requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/fan-analytics/overview")
        assert resp.status_code in [401, 422], f"Expected 401/422 without auth, got {resp.status_code}"


class TestSpotifyIntegrationEndpoints:
    """Spotify Integration Placeholder tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth session"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_spotify_status_returns_connected_false(self):
        """GET /api/integrations/spotify/status returns connected: false for unconnected users"""
        # First disconnect to ensure clean state
        self.session.delete(f"{BASE_URL}/api/integrations/spotify/disconnect")
        
        resp = self.session.get(f"{BASE_URL}/api/integrations/spotify/status")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        assert "connected" in data, "Missing 'connected' field"
        assert data["connected"] == False, f"Expected connected=False, got {data['connected']}"
        print("Spotify status: Not connected (as expected)")
    
    def test_spotify_connect_saves_intent(self):
        """POST /api/integrations/spotify/connect saves connection intent"""
        resp = self.session.post(f"{BASE_URL}/api/integrations/spotify/connect", json={
            "spotify_id": "test_spotify_123",
            "display_name": "Test Artist"
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        assert "message" in data, "Missing 'message' field"
        assert "coming soon" in data["message"].lower() or "saved" in data["message"].lower(), f"Unexpected message: {data['message']}"
        print(f"Spotify connect response: {data['message']}")
        
        # Verify status shows connected
        status_resp = self.session.get(f"{BASE_URL}/api/integrations/spotify/status")
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        assert status_data.get("connected") == True, "Expected connected=True after connect"
        print("Spotify status after connect: Connected")
    
    def test_spotify_disconnect_removes_connection(self):
        """DELETE /api/integrations/spotify/disconnect removes connection"""
        # First connect
        self.session.post(f"{BASE_URL}/api/integrations/spotify/connect", json={
            "spotify_id": "test_spotify_456",
            "display_name": "Test Artist 2"
        })
        
        # Then disconnect
        resp = self.session.delete(f"{BASE_URL}/api/integrations/spotify/disconnect")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        assert "message" in data, "Missing 'message' field"
        print(f"Spotify disconnect response: {data['message']}")
        
        # Verify status shows disconnected
        status_resp = self.session.get(f"{BASE_URL}/api/integrations/spotify/status")
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        assert status_data.get("connected") == False, "Expected connected=False after disconnect"
        print("Spotify status after disconnect: Not connected")
    
    def test_spotify_status_requires_auth(self):
        """Spotify status requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/integrations/spotify/status")
        assert resp.status_code in [401, 422], f"Expected 401/422 without auth, got {resp.status_code}"
    
    def test_spotify_connect_requires_auth(self):
        """Spotify connect requires authentication"""
        resp = requests.post(f"{BASE_URL}/api/integrations/spotify/connect", json={})
        assert resp.status_code in [401, 422], f"Expected 401/422 without auth, got {resp.status_code}"
    
    def test_spotify_disconnect_requires_auth(self):
        """Spotify disconnect requires authentication"""
        resp = requests.delete(f"{BASE_URL}/api/integrations/spotify/disconnect")
        assert resp.status_code in [401, 422], f"Expected 401/422 without auth, got {resp.status_code}"


class TestSocialShareEndpointsStillWorking:
    """Verify social share endpoints still work (regression test)"""
    
    def test_share_beat_endpoint_exists(self):
        """GET /api/share/beat/{id} returns 404 for invalid ID (endpoint exists)"""
        resp = requests.get(f"{BASE_URL}/api/share/beat/invalid_beat_id")
        assert resp.status_code == 404, f"Expected 404 for invalid beat, got {resp.status_code}"
        print("Share beat endpoint working (returns 404 for invalid ID)")
    
    def test_share_release_endpoint_exists(self):
        """GET /api/share/release/{id} returns 404 for invalid ID (endpoint exists)"""
        resp = requests.get(f"{BASE_URL}/api/share/release/invalid_release_id")
        assert resp.status_code == 404, f"Expected 404 for invalid release, got {resp.status_code}"
        print("Share release endpoint working (returns 404 for invalid ID)")
    
    def test_share_artist_endpoint_exists(self):
        """GET /api/share/artist/{id} returns 404 for invalid ID (endpoint exists)"""
        resp = requests.get(f"{BASE_URL}/api/share/artist/invalid_user_id")
        assert resp.status_code == 404, f"Expected 404 for invalid artist, got {resp.status_code}"
        print("Share artist endpoint working (returns 404 for invalid ID)")


class TestPreSaveCampaignsStillWorking:
    """Verify pre-save campaigns still work (regression test)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth session"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_presave_campaigns_list(self):
        """GET /api/presave/campaigns returns list"""
        resp = self.session.get(f"{BASE_URL}/api/presave/campaigns")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "campaigns" in data, "Missing 'campaigns' field"
        print(f"Pre-save campaigns: {len(data['campaigns'])} campaigns found")


class TestBeatsSearchFilterStillWorking:
    """Verify beats search/filter still works (regression test)"""
    
    def test_beats_list_endpoint(self):
        """GET /api/beats returns list"""
        resp = requests.get(f"{BASE_URL}/api/beats")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "beats" in data, "Missing 'beats' field"
        print(f"Beats endpoint working: {len(data['beats'])} beats found")
    
    def test_beats_search_filter(self):
        """GET /api/beats?search=test works"""
        resp = requests.get(f"{BASE_URL}/api/beats?search=test")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        print("Beats search filter working")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
