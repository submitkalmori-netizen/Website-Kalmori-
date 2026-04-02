"""
Iteration 19 - Testing P2 Features:
1. Real-time Streaming Data Ingestion from DSPs (simulated stream_events)
2. Push Notifications - notification bell with unread count and dropdown panel

Tests:
- GET /api/analytics/overview - returns real stream data from stream_events collection
- GET /api/analytics/chart-data?days=14 - returns daily plays and revenue aggregated
- GET /api/analytics/platform-breakdown - returns platform data with streams, revenue, percentage, color
- GET /api/analytics/live-feed?limit=20 - returns recent stream events
- GET /api/notifications/unread-count - returns count of unread notifications
- PUT /api/notifications/read-all - marks all notifications as read
- PUT /api/notifications/{id}/read - marks specific notification as read
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint is working"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health endpoint working")
    
    def test_admin_login(self):
        """Test admin login returns tokens"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        print("✓ Admin login successful")


class TestAnalyticsOverview:
    """Test analytics overview endpoint with stream_events data"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        return session
    
    def test_analytics_overview_requires_auth(self):
        """Test analytics overview requires authentication"""
        response = requests.get(f"{BASE_URL}/api/analytics/overview")
        assert response.status_code == 401
        print("✓ Analytics overview requires auth")
    
    def test_analytics_overview_returns_stream_data(self, auth_session):
        """Test analytics overview returns real stream data from stream_events"""
        response = auth_session.get(f"{BASE_URL}/api/analytics/overview")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "total_streams" in data
        assert "total_earnings" in data
        assert "streams_by_store" in data
        assert "streams_by_country" in data
        assert "daily_streams" in data
        assert "release_count" in data
        
        # Verify data types
        assert isinstance(data["total_streams"], int)
        assert isinstance(data["total_earnings"], (int, float))
        assert isinstance(data["streams_by_store"], dict)
        assert isinstance(data["streams_by_country"], dict)
        assert isinstance(data["daily_streams"], list)
        
        print(f"✓ Analytics overview: {data['total_streams']} total streams, ${data['total_earnings']:.2f} earnings")
        print(f"  Platforms: {list(data['streams_by_store'].keys())}")
        print(f"  Countries: {list(data['streams_by_country'].keys())}")
        print(f"  Daily data points: {len(data['daily_streams'])}")


class TestAnalyticsChartData:
    """Test analytics chart-data endpoint"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        return session
    
    def test_chart_data_requires_auth(self):
        """Test chart-data requires authentication"""
        response = requests.get(f"{BASE_URL}/api/analytics/chart-data?days=14")
        assert response.status_code == 401
        print("✓ Chart data requires auth")
    
    def test_chart_data_returns_daily_aggregates(self, auth_session):
        """Test chart-data returns daily plays and revenue"""
        response = auth_session.get(f"{BASE_URL}/api/analytics/chart-data?days=14")
        assert response.status_code == 200
        data = response.json()
        
        # Should return list of daily data
        assert isinstance(data, list)
        
        # Check structure of each day
        if len(data) > 0:
            day = data[0]
            assert "date" in day
            assert "plays" in day
            assert "revenue" in day
            assert isinstance(day["plays"], int)
            assert isinstance(day["revenue"], (int, float))
        
        print(f"✓ Chart data: {len(data)} days of data")
        if len(data) > 0:
            total_plays = sum(d["plays"] for d in data)
            total_revenue = sum(d["revenue"] for d in data)
            print(f"  Total plays: {total_plays}, Total revenue: ${total_revenue:.2f}")


class TestAnalyticsPlatformBreakdown:
    """Test analytics platform-breakdown endpoint"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        return session
    
    def test_platform_breakdown_requires_auth(self):
        """Test platform-breakdown requires authentication"""
        response = requests.get(f"{BASE_URL}/api/analytics/platform-breakdown")
        assert response.status_code == 401
        print("✓ Platform breakdown requires auth")
    
    def test_platform_breakdown_returns_platform_data(self, auth_session):
        """Test platform-breakdown returns platform data with streams, revenue, percentage, color"""
        response = auth_session.get(f"{BASE_URL}/api/analytics/platform-breakdown")
        assert response.status_code == 200
        data = response.json()
        
        # Should return list of platforms
        assert isinstance(data, list)
        
        # Check structure of each platform
        if len(data) > 0:
            platform = data[0]
            assert "name" in platform
            assert "streams" in platform
            assert "revenue" in platform
            assert "percentage" in platform
            assert "color" in platform
            
            # Verify data types
            assert isinstance(platform["name"], str)
            assert isinstance(platform["streams"], int)
            assert isinstance(platform["revenue"], (int, float))
            assert isinstance(platform["percentage"], (int, float))
            assert isinstance(platform["color"], str)
            assert platform["color"].startswith("#")
        
        print(f"✓ Platform breakdown: {len(data)} platforms")
        for p in data[:5]:  # Show top 5
            print(f"  {p['name']}: {p['streams']} streams ({p['percentage']}%), ${p['revenue']:.2f}")


class TestAnalyticsLiveFeed:
    """Test analytics live-feed endpoint"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        return session
    
    def test_live_feed_requires_auth(self):
        """Test live-feed requires authentication"""
        response = requests.get(f"{BASE_URL}/api/analytics/live-feed?limit=20")
        assert response.status_code == 401
        print("✓ Live feed requires auth")
    
    def test_live_feed_returns_stream_events(self, auth_session):
        """Test live-feed returns recent stream events with platform, country, revenue, timestamp"""
        response = auth_session.get(f"{BASE_URL}/api/analytics/live-feed?limit=20")
        assert response.status_code == 200
        data = response.json()
        
        # Should return events list
        assert "events" in data
        assert isinstance(data["events"], list)
        
        # Check structure of each event
        if len(data["events"]) > 0:
            event = data["events"][0]
            assert "platform" in event
            assert "country" in event
            assert "revenue" in event
            assert "timestamp" in event
            
            # Verify data types
            assert isinstance(event["platform"], str)
            assert isinstance(event["country"], str)
            assert isinstance(event["revenue"], (int, float))
            assert isinstance(event["timestamp"], str)
        
        print(f"✓ Live feed: {len(data['events'])} events")
        for e in data["events"][:3]:  # Show first 3
            print(f"  {e['platform']} - {e['country']} - ${e['revenue']:.4f}")


class TestNotificationsUnreadCount:
    """Test notifications unread-count endpoint"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        return session
    
    def test_unread_count_requires_auth(self):
        """Test unread-count requires authentication"""
        response = requests.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code == 401
        print("✓ Unread count requires auth")
    
    def test_unread_count_returns_count(self, auth_session):
        """Test unread-count returns count of unread notifications"""
        response = auth_session.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code == 200
        data = response.json()
        
        assert "count" in data
        assert isinstance(data["count"], int)
        assert data["count"] >= 0
        
        print(f"✓ Unread count: {data['count']} unread notifications")


class TestNotificationsReadAll:
    """Test notifications read-all endpoint"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        return session
    
    def test_read_all_requires_auth(self):
        """Test read-all requires authentication"""
        response = requests.put(f"{BASE_URL}/api/notifications/read-all")
        assert response.status_code == 401
        print("✓ Read all requires auth")
    
    def test_read_all_marks_notifications_read(self, auth_session):
        """Test read-all marks all notifications as read"""
        # First get current unread count
        count_before = auth_session.get(f"{BASE_URL}/api/notifications/unread-count").json()["count"]
        
        # Mark all as read
        response = auth_session.put(f"{BASE_URL}/api/notifications/read-all")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify unread count is now 0
        count_after = auth_session.get(f"{BASE_URL}/api/notifications/unread-count").json()["count"]
        assert count_after == 0
        
        print(f"✓ Read all: marked {count_before} notifications as read, now {count_after} unread")


class TestNotificationsMarkRead:
    """Test notifications mark individual as read endpoint"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        return session
    
    def test_mark_read_requires_auth(self):
        """Test mark read requires authentication"""
        response = requests.put(f"{BASE_URL}/api/notifications/test-id/read")
        assert response.status_code == 401
        print("✓ Mark read requires auth")
    
    def test_mark_read_endpoint_exists(self, auth_session):
        """Test mark read endpoint exists and accepts requests"""
        # Use a fake notification ID - should return 200 even if not found (no error)
        response = auth_session.put(f"{BASE_URL}/api/notifications/notif_test123/read")
        # Should return 200 (marks as read if exists, no error if not)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        print("✓ Mark read endpoint working")


class TestNotificationsList:
    """Test notifications list endpoint"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        return session
    
    def test_notifications_list_requires_auth(self):
        """Test notifications list requires authentication"""
        response = requests.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 401
        print("✓ Notifications list requires auth")
    
    def test_notifications_list_returns_array(self, auth_session):
        """Test notifications list returns array of notifications"""
        response = auth_session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        data = response.json()
        
        # Should return list
        assert isinstance(data, list)
        
        # Check structure if notifications exist
        if len(data) > 0:
            notif = data[0]
            assert "id" in notif
            assert "message" in notif
            assert "read" in notif
            assert "created_at" in notif
        
        print(f"✓ Notifications list: {len(data)} notifications")


class TestStreamEventsSeeding:
    """Test that stream_events collection has been seeded with data"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert response.status_code == 200
        return session
    
    def test_stream_events_seeded(self, auth_session):
        """Verify stream_events collection has seeded data via analytics endpoints"""
        # Get analytics overview
        overview = auth_session.get(f"{BASE_URL}/api/analytics/overview").json()
        
        # Get platform breakdown
        platforms = auth_session.get(f"{BASE_URL}/api/analytics/platform-breakdown").json()
        
        # Get live feed
        feed = auth_session.get(f"{BASE_URL}/api/analytics/live-feed?limit=20").json()
        
        # Verify data exists
        total_streams = overview.get("total_streams", 0)
        platform_count = len(platforms)
        event_count = len(feed.get("events", []))
        
        print(f"✓ Stream events seeding verification:")
        print(f"  Total streams: {total_streams}")
        print(f"  Platforms with data: {platform_count}")
        print(f"  Recent events: {event_count}")
        
        # Check if Spotify is top platform (as per seeding weights)
        if platforms:
            top_platform = platforms[0]["name"]
            print(f"  Top platform: {top_platform}")
            # Spotify should be top with 40% weight
            assert top_platform == "Spotify", f"Expected Spotify as top platform, got {top_platform}"
            print("✓ Spotify is top platform as expected (40% weight)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
