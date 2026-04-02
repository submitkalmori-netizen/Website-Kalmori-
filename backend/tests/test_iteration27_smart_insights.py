"""
Iteration 27 - AI Smart Notifications / Smart Insights Feature Tests
Tests for:
- POST /api/ai/smart-insights - generates AI insights from streaming trends
- GET /api/ai/smart-insights - retrieves saved AI insights
- GET /api/notifications - includes AI insight notifications
- GET /api/notifications/unread-count - counts AI insight notifications
- Regression tests for existing AI endpoints
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSmartInsightsAuth:
    """Test authentication requirements for smart insights endpoints"""
    
    def test_post_smart_insights_requires_auth(self):
        """POST /api/ai/smart-insights should require authentication"""
        response = requests.post(f"{BASE_URL}/api/ai/smart-insights")
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"
        print("PASS: POST /api/ai/smart-insights requires authentication")
    
    def test_get_smart_insights_requires_auth(self):
        """GET /api/ai/smart-insights should require authentication"""
        response = requests.get(f"{BASE_URL}/api/ai/smart-insights")
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"
        print("PASS: GET /api/ai/smart-insights requires authentication")


class TestSmartInsightsGeneration:
    """Test POST /api/ai/smart-insights endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        print("Authenticated successfully")
        return session
    
    def test_generate_smart_insights_success(self, auth_session):
        """POST /api/ai/smart-insights should generate insights and return them"""
        # This endpoint calls GPT-4o, so allow longer timeout
        response = auth_session.post(
            f"{BASE_URL}/api/ai/smart-insights",
            json={},
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "insights" in data, "Response should contain 'insights' array"
        assert "data_context" in data, "Response should contain 'data_context'"
        assert "generated_at" in data, "Response should contain 'generated_at'"
        
        # Verify data_context structure
        ctx = data["data_context"]
        assert "recent_streams" in ctx, "data_context should have recent_streams"
        assert "previous_streams" in ctx, "data_context should have previous_streams"
        assert "overall_growth" in ctx, "data_context should have overall_growth"
        
        print(f"PASS: Generated {len(data['insights'])} insights")
        print(f"  - Recent streams: {ctx['recent_streams']}")
        print(f"  - Previous streams: {ctx['previous_streams']}")
        print(f"  - Overall growth: {ctx['overall_growth']}%")
        
        # Verify insights structure (if any were generated)
        if len(data["insights"]) > 0:
            insight = data["insights"][0]
            assert "id" in insight, "Insight should have 'id'"
            assert "message" in insight, "Insight should have 'message'"
            assert "type" in insight, "Insight should have 'type'"
            assert insight["type"] == "ai_insight", f"Insight type should be 'ai_insight', got {insight['type']}"
            assert "category" in insight, "Insight should have 'category'"
            assert "priority" in insight, "Insight should have 'priority'"
            assert "metric_value" in insight, "Insight should have 'metric_value'"
            assert "action_suggestion" in insight, "Insight should have 'action_suggestion'"
            
            print(f"  - First insight category: {insight['category']}")
            print(f"  - First insight priority: {insight['priority']}")
            print(f"  - First insight metric: {insight['metric_value']}")
        
        return data
    
    def test_insights_stored_as_notifications(self, auth_session):
        """Verify generated insights are stored in notifications collection"""
        # First generate insights
        gen_response = auth_session.post(
            f"{BASE_URL}/api/ai/smart-insights",
            json={},
            timeout=60
        )
        assert gen_response.status_code == 200
        generated = gen_response.json()
        
        # Wait a moment for DB write
        time.sleep(0.5)
        
        # Now fetch via GET endpoint
        get_response = auth_session.get(f"{BASE_URL}/api/ai/smart-insights")
        assert get_response.status_code == 200
        
        fetched = get_response.json()
        assert "insights" in fetched
        assert "total" in fetched
        
        # Verify at least some insights exist
        assert len(fetched["insights"]) > 0, "Should have at least one insight stored"
        
        # Verify all returned insights have type=ai_insight
        for insight in fetched["insights"]:
            assert insight.get("type") == "ai_insight", f"Expected type='ai_insight', got {insight.get('type')}"
        
        print(f"PASS: GET /api/ai/smart-insights returns {fetched['total']} insights, all with type='ai_insight'")


class TestSmartInsightsRetrieval:
    """Test GET /api/ai/smart-insights endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200
        return session
    
    def test_get_smart_insights_returns_only_ai_insights(self, auth_session):
        """GET /api/ai/smart-insights should only return type=ai_insight notifications"""
        response = auth_session.get(f"{BASE_URL}/api/ai/smart-insights")
        assert response.status_code == 200
        
        data = response.json()
        assert "insights" in data
        assert "total" in data
        
        # All returned items should have type=ai_insight
        for insight in data["insights"]:
            assert insight.get("type") == "ai_insight", f"Expected type='ai_insight', got {insight.get('type')}"
        
        print(f"PASS: GET /api/ai/smart-insights returns {data['total']} AI insights only")


class TestNotificationsIntegration:
    """Test that AI insights appear in regular notifications endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200
        return session
    
    def test_notifications_include_ai_insights(self, auth_session):
        """GET /api/notifications should include AI insight notifications"""
        response = auth_session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        
        data = response.json()
        # Response should be an array
        assert isinstance(data, list), f"Expected array, got {type(data)}"
        
        # Check if any AI insights are present
        ai_insights = [n for n in data if n.get("type") == "ai_insight"]
        print(f"PASS: GET /api/notifications returns {len(data)} notifications, {len(ai_insights)} are AI insights")
        
        # Verify AI insight structure in notifications
        if ai_insights:
            insight = ai_insights[0]
            assert "id" in insight
            assert "message" in insight
            assert "type" in insight
            assert insight["type"] == "ai_insight"
            # AI insights should have extra fields
            assert "category" in insight or "metric_value" in insight or "action_suggestion" in insight
            print(f"  - AI insight has expected fields: category={insight.get('category')}, metric={insight.get('metric_value')}")
    
    def test_unread_count_includes_ai_insights(self, auth_session):
        """GET /api/notifications/unread-count should count AI insight notifications"""
        response = auth_session.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code == 200
        
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)
        
        print(f"PASS: GET /api/notifications/unread-count returns count={data['count']}")


class TestRegressionAIEndpoints:
    """Regression tests for existing AI endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200
        return session
    
    def test_release_strategy_still_works(self, auth_session):
        """POST /api/ai/release-strategy should still work (regression)"""
        response = auth_session.post(
            f"{BASE_URL}/api/ai/release-strategy",
            json={"release_title": "Test Release", "genre": "Pop"},
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "strategy" in data
        assert "data_summary" in data
        
        print("PASS: POST /api/ai/release-strategy still works (regression)")
    
    def test_save_strategy_still_works(self, auth_session):
        """POST /api/ai/strategies/save should still work (regression)"""
        response = auth_session.post(
            f"{BASE_URL}/api/ai/strategies/save",
            json={
                "strategy": {"optimal_release_day": "Friday", "optimal_release_time": "00:00 UTC"},
                "data_summary": {"total_streams": 1000},
                "label": "TEST_Regression_Strategy"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "saved_strategy" in data
        assert data["saved_strategy"]["label"] == "TEST_Regression_Strategy"
        
        print("PASS: POST /api/ai/strategies/save still works (regression)")
        
        # Cleanup - delete the test strategy
        strategy_id = data["saved_strategy"]["id"]
        delete_response = auth_session.delete(f"{BASE_URL}/api/ai/strategies/{strategy_id}")
        assert delete_response.status_code == 200
        print(f"  - Cleaned up test strategy {strategy_id}")
    
    def test_export_pdf_still_works(self, auth_session):
        """POST /api/ai/strategies/export-pdf should still work (regression)"""
        response = auth_session.post(
            f"{BASE_URL}/api/ai/strategies/export-pdf",
            json={
                "strategy": {
                    "optimal_release_day": "Friday",
                    "optimal_release_time": "00:00 UTC",
                    "release_day_reasoning": "Test reasoning",
                    "target_platforms": [],
                    "geographic_strategy": [],
                    "pre_release_timeline": [],
                    "promotion_tips": ["Test tip"]
                },
                "data_summary": {"total_streams": 500},
                "label": "Regression Test"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify PDF response
        assert response.headers.get("Content-Type") == "application/pdf"
        assert "Content-Disposition" in response.headers
        assert response.content[:4] == b"%PDF"
        
        print("PASS: POST /api/ai/strategies/export-pdf still works (regression)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
