"""
Iteration 28 - Weekly Digest Email Feature Tests
Tests for:
- POST /api/digest/send - sends weekly digest email
- POST /api/digest/preview - returns HTML preview
- GET /api/digest/history - returns sent digest history
- GET /api/settings/notification-preferences - includes email_weekly_digest
- PUT /api/settings/notification-preferences - can toggle email_weekly_digest
- Regression: POST /api/ai/smart-insights, POST /api/ai/release-strategy, POST /api/ai/strategies/export-pdf
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"


@pytest.fixture(scope="module")
def auth_session():
    """Create authenticated session for tests"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    # Login
    login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if login_resp.status_code != 200:
        pytest.skip(f"Login failed: {login_resp.status_code} - {login_resp.text}")
    
    return session


class TestDigestSend:
    """Tests for POST /api/digest/send endpoint"""
    
    def test_digest_send_requires_auth(self):
        """Digest send should require authentication"""
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/digest/send", json={})
        assert resp.status_code in [401, 422], f"Expected 401/422, got {resp.status_code}"
        print("PASS: POST /api/digest/send requires authentication")
    
    def test_digest_send_returns_stats(self, auth_session):
        """Digest send should return streaming stats"""
        resp = auth_session.post(f"{BASE_URL}/api/digest/send", json={})
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        
        # Check message field
        assert "message" in data, "Response should have 'message' field"
        
        # Check stats field
        assert "stats" in data, "Response should have 'stats' field"
        stats = data["stats"]
        
        # Verify stats structure
        assert "streams_this_week" in stats, "Stats should have 'streams_this_week'"
        assert "streams_last_week" in stats, "Stats should have 'streams_last_week'"
        assert "growth" in stats, "Stats should have 'growth'"
        assert "top_countries" in stats, "Stats should have 'top_countries'"
        assert "insights_included" in stats, "Stats should have 'insights_included'"
        
        # Verify types
        assert isinstance(stats["streams_this_week"], int), "streams_this_week should be int"
        assert isinstance(stats["streams_last_week"], int), "streams_last_week should be int"
        assert isinstance(stats["growth"], (int, float)), "growth should be numeric"
        
        print(f"PASS: POST /api/digest/send returns stats: {stats}")


class TestDigestPreview:
    """Tests for POST /api/digest/preview endpoint"""
    
    def test_digest_preview_requires_auth(self):
        """Digest preview should require authentication"""
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/digest/preview", json={})
        assert resp.status_code in [401, 422], f"Expected 401/422, got {resp.status_code}"
        print("PASS: POST /api/digest/preview requires authentication")
    
    def test_digest_preview_returns_html(self, auth_session):
        """Digest preview should return HTML content"""
        resp = auth_session.post(f"{BASE_URL}/api/digest/preview", json={})
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        
        # Check html field
        assert "html" in data, "Response should have 'html' field"
        html = data["html"]
        
        # Verify HTML contains expected content
        assert "KALMORI" in html, "HTML should contain 'KALMORI' branding"
        assert "Weekly" in html or "weekly" in html.lower(), "HTML should contain 'Weekly'"
        
        # Check for streaming stats in HTML
        assert "streams" in html.lower() or "stream" in html.lower(), "HTML should mention streams"
        
        # Check stats field
        assert "stats" in data, "Response should have 'stats' field"
        
        print(f"PASS: POST /api/digest/preview returns HTML ({len(html)} chars)")
    
    def test_digest_preview_html_structure(self, auth_session):
        """Digest preview HTML should have proper structure"""
        resp = auth_session.post(f"{BASE_URL}/api/digest/preview", json={})
        assert resp.status_code == 200
        
        html = resp.json()["html"]
        
        # Check for key sections
        assert "This Week" in html or "this week" in html.lower(), "HTML should have 'This Week' section"
        assert "Last Week" in html or "last week" in html.lower(), "HTML should have 'Last Week' section"
        assert "Growth" in html or "growth" in html.lower(), "HTML should have 'Growth' section"
        
        # Check for gradient header (KALMORI branding)
        assert "gradient" in html.lower(), "HTML should have gradient styling"
        
        print("PASS: Digest preview HTML has proper structure")


class TestDigestHistory:
    """Tests for GET /api/digest/history endpoint"""
    
    def test_digest_history_requires_auth(self):
        """Digest history should require authentication"""
        session = requests.Session()
        resp = session.get(f"{BASE_URL}/api/digest/history")
        assert resp.status_code in [401, 422], f"Expected 401/422, got {resp.status_code}"
        print("PASS: GET /api/digest/history requires authentication")
    
    def test_digest_history_returns_list(self, auth_session):
        """Digest history should return list of sent digests"""
        resp = auth_session.get(f"{BASE_URL}/api/digest/history")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        
        # Check structure
        assert "history" in data, "Response should have 'history' field"
        assert "total" in data, "Response should have 'total' field"
        
        # History should be a list
        assert isinstance(data["history"], list), "history should be a list"
        
        # If we have history entries, verify structure
        if len(data["history"]) > 0:
            entry = data["history"][0]
            assert "id" in entry, "History entry should have 'id'"
            assert "user_id" in entry, "History entry should have 'user_id'"
            assert "sent_at" in entry, "History entry should have 'sent_at'"
            assert "streams_this_week" in entry, "History entry should have 'streams_this_week'"
            print(f"PASS: GET /api/digest/history returns {len(data['history'])} entries")
        else:
            print("PASS: GET /api/digest/history returns empty list (no digests sent yet)")


class TestNotificationPreferences:
    """Tests for notification preferences with email_weekly_digest"""
    
    def test_get_notification_prefs_includes_weekly_digest(self, auth_session):
        """GET notification-preferences should include email_weekly_digest"""
        resp = auth_session.get(f"{BASE_URL}/api/settings/notification-preferences")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        
        # Check email_weekly_digest field exists
        assert "email_weekly_digest" in data, "Preferences should include 'email_weekly_digest'"
        assert isinstance(data["email_weekly_digest"], bool), "email_weekly_digest should be boolean"
        
        print(f"PASS: GET notification-preferences includes email_weekly_digest={data['email_weekly_digest']}")
    
    def test_toggle_weekly_digest_preference(self, auth_session):
        """PUT notification-preferences should toggle email_weekly_digest"""
        # Get current value
        get_resp = auth_session.get(f"{BASE_URL}/api/settings/notification-preferences")
        assert get_resp.status_code == 200
        current_value = get_resp.json().get("email_weekly_digest", True)
        
        # Toggle to opposite value
        new_value = not current_value
        put_resp = auth_session.put(f"{BASE_URL}/api/settings/notification-preferences", json={
            "email_weekly_digest": new_value
        })
        assert put_resp.status_code == 200, f"Expected 200, got {put_resp.status_code}: {put_resp.text}"
        
        # Verify change
        verify_resp = auth_session.get(f"{BASE_URL}/api/settings/notification-preferences")
        assert verify_resp.status_code == 200
        assert verify_resp.json()["email_weekly_digest"] == new_value, "Preference should be updated"
        
        # Restore original value
        auth_session.put(f"{BASE_URL}/api/settings/notification-preferences", json={
            "email_weekly_digest": current_value
        })
        
        print(f"PASS: PUT notification-preferences can toggle email_weekly_digest ({current_value} -> {new_value})")


class TestRegressionAIEndpoints:
    """Regression tests for existing AI endpoints"""
    
    def test_smart_insights_still_works(self, auth_session):
        """POST /api/ai/smart-insights should still work"""
        resp = auth_session.post(f"{BASE_URL}/api/ai/smart-insights", json={})
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "insights" in data, "Response should have 'insights' field"
        
        print(f"PASS: POST /api/ai/smart-insights still works ({len(data.get('insights', []))} insights)")
    
    def test_release_strategy_still_works(self, auth_session):
        """POST /api/ai/release-strategy should still work"""
        resp = auth_session.post(f"{BASE_URL}/api/ai/release-strategy", json={
            "release_title": "Test Release",
            "genre": "Pop"
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "strategy" in data, "Response should have 'strategy' field"
        
        print("PASS: POST /api/ai/release-strategy still works")
    
    def test_export_pdf_still_works(self, auth_session):
        """POST /api/ai/strategies/export-pdf should still work"""
        # First generate a strategy
        strategy_resp = auth_session.post(f"{BASE_URL}/api/ai/release-strategy", json={
            "release_title": "PDF Test",
            "genre": "Hip-Hop"
        })
        
        if strategy_resp.status_code != 200:
            pytest.skip("Could not generate strategy for PDF test")
        
        strategy_data = strategy_resp.json()
        
        # Export as PDF
        pdf_resp = auth_session.post(f"{BASE_URL}/api/ai/strategies/export-pdf", json={
            "strategy": strategy_data.get("strategy", {}),
            "data_summary": strategy_data.get("data_summary", {}),
            "release_title": "PDF Test",
            "genre": "Hip-Hop",
            "label": "Test Export"
        })
        
        assert pdf_resp.status_code == 200, f"Expected 200, got {pdf_resp.status_code}"
        assert pdf_resp.headers.get("content-type") == "application/pdf", "Response should be PDF"
        
        print("PASS: POST /api/ai/strategies/export-pdf still works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
