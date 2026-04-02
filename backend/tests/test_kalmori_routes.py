"""
Test suite for Kalmori Routes - CMS, Cart, Credits, Social, Testimonials, Theme, etc.
Tests all endpoints merged from user's GitHub repository.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://artist-hub-219.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"
ADMIN_USER_ID = "user_ff17829e7621"


class TestHealthAndInfo:
    """Health check and info endpoints"""
    
    def test_health_endpoint(self):
        """GET /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        print("✓ Health endpoint working")
    
    def test_kalmori_info(self):
        """GET /api/kalmori-info returns version info"""
        response = requests.get(f"{BASE_URL}/api/kalmori-info")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "message" in data
        print(f"✓ Kalmori info: version {data['version']}")


class TestAuthentication:
    """Authentication endpoints"""
    
    def test_login_success(self):
        """POST /api/auth/login with valid credentials returns user data"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == ADMIN_EMAIL
        assert data["role"] == "admin"
        assert "id" in data
        print(f"✓ Login successful for {ADMIN_EMAIL}")
        return response.cookies
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login with invalid credentials returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": "wrongpassword"}
        )
        assert response.status_code == 401
        print("✓ Invalid login rejected correctly")
    
    def test_auth_me_with_cookie(self):
        """GET /api/auth/me with cookie returns user info"""
        # First login to get cookie
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        cookies = login_response.cookies
        
        # Then check /auth/me
        response = requests.get(f"{BASE_URL}/api/auth/me", cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == ADMIN_EMAIL
        print("✓ Auth me endpoint working with cookie")


class TestCMSPublicEndpoints:
    """CMS public endpoints - slides, pricing, legal, pages"""
    
    def test_cms_slides(self):
        """GET /api/cms/slides returns slides array"""
        response = requests.get(f"{BASE_URL}/api/cms/slides")
        assert response.status_code == 200
        data = response.json()
        assert "slides" in data
        assert isinstance(data["slides"], list)
        assert len(data["slides"]) >= 1
        print(f"✓ CMS slides: {len(data['slides'])} slides returned")
    
    def test_cms_pricing(self):
        """GET /api/cms/pricing returns plans array"""
        response = requests.get(f"{BASE_URL}/api/cms/pricing")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert isinstance(data["plans"], list)
        assert len(data["plans"]) >= 1
        # Verify plan structure
        plan = data["plans"][0]
        assert "id" in plan
        assert "name" in plan
        assert "price" in plan
        print(f"✓ CMS pricing: {len(data['plans'])} plans returned")
    
    def test_cms_legal_terms(self):
        """GET /api/cms/legal/terms returns terms content"""
        response = requests.get(f"{BASE_URL}/api/cms/legal/terms")
        assert response.status_code == 200
        data = response.json()
        assert data["page_id"] == "terms"
        assert "title" in data
        assert "content" in data
        assert len(data["content"]) > 0
        print("✓ CMS legal terms returned")
    
    def test_cms_legal_privacy(self):
        """GET /api/cms/legal/privacy returns privacy content"""
        response = requests.get(f"{BASE_URL}/api/cms/legal/privacy")
        assert response.status_code == 200
        data = response.json()
        assert data["page_id"] == "privacy"
        assert "title" in data
        assert "content" in data
        print("✓ CMS legal privacy returned")
    
    def test_cms_pages_list(self):
        """GET /api/cms/pages returns pages list"""
        response = requests.get(f"{BASE_URL}/api/cms/pages")
        assert response.status_code == 200
        data = response.json()
        assert "pages" in data
        assert isinstance(data["pages"], list)
        page_ids = [p["id"] for p in data["pages"]]
        assert "homepage" in page_ids
        assert "pricing" in page_ids
        print(f"✓ CMS pages: {len(data['pages'])} pages listed")
    
    def test_cms_page_homepage(self):
        """GET /api/cms/page/homepage returns homepage sections"""
        response = requests.get(f"{BASE_URL}/api/cms/page/homepage")
        assert response.status_code == 200
        data = response.json()
        assert "sections" in data
        assert isinstance(data["sections"], list)
        assert "page_name" in data
        print(f"✓ CMS homepage: {len(data['sections'])} sections")
    
    def test_cms_instrumentals(self):
        """GET /api/cms/instrumentals returns instrumentals content"""
        response = requests.get(f"{BASE_URL}/api/cms/instrumentals")
        assert response.status_code == 200
        data = response.json()
        assert "heroTitle" in data
        assert "licenseTiers" in data
        assert isinstance(data["licenseTiers"], list)
        print(f"✓ CMS instrumentals: {len(data['licenseTiers'])} license tiers")


class TestPublicReleases:
    """Public releases endpoint"""
    
    def test_public_releases(self):
        """GET /api/public-releases returns array"""
        response = requests.get(f"{BASE_URL}/api/public-releases")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Public releases: {len(data)} releases")


class TestTestimonials:
    """Testimonials endpoint"""
    
    def test_testimonials(self):
        """GET /api/testimonials returns array"""
        response = requests.get(f"{BASE_URL}/api/testimonials")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Testimonials: {len(data)} testimonials")


class TestOrderEndpoints:
    """Promotion and instrumental order endpoints"""
    
    def test_promotion_order(self):
        """POST /api/orders/promotion-service creates promotion order"""
        response = requests.post(
            f"{BASE_URL}/api/orders/promotion-service",
            json={
                "artist_name": "TEST_Artist",
                "email": "test@example.com",
                "song_title": "Test Song",
                "services": ["playlist_pitching"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "order_id" in data
        assert data["message"] == "Order submitted successfully"
        print(f"✓ Promotion order created: {data['order_id']}")
    
    def test_instrumental_request(self):
        """POST /api/orders/instrumental-request creates instrumental request"""
        response = requests.post(
            f"{BASE_URL}/api/orders/instrumental-request",
            json={
                "artist_name": "TEST_Artist",
                "email": "test@example.com",
                "genre": "Hip-Hop",
                "license_type": "basic_lease"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert data["message"] == "Request submitted successfully"
        print(f"✓ Instrumental request created: {data['request_id']}")


class TestAuthenticatedEndpoints:
    """Endpoints requiring authentication"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get session cookies"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        self.cookies = login_response.cookies
    
    def test_cart(self):
        """GET /api/cart returns cart with item_count"""
        response = requests.get(f"{BASE_URL}/api/cart", cookies=self.cookies)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "item_count" in data
        assert "subtotal" in data
        print(f"✓ Cart: {data['item_count']} items, ${data['subtotal']} subtotal")
    
    def test_credits(self):
        """GET /api/credits returns credits object"""
        response = requests.get(f"{BASE_URL}/api/credits", cookies=self.cookies)
        assert response.status_code == 200
        data = response.json()
        assert "credits" in data
        print(f"✓ Credits: {data['credits']} credits")
    
    def test_payment_methods(self):
        """GET /api/payment-methods returns array"""
        response = requests.get(f"{BASE_URL}/api/payment-methods", cookies=self.cookies)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Payment methods: {len(data)} methods")
    
    def test_theme(self):
        """GET /api/theme returns theme settings"""
        response = requests.get(f"{BASE_URL}/api/theme", cookies=self.cookies)
        assert response.status_code == 200
        data = response.json()
        assert "theme" in data
        assert "primary_color" in data["theme"]
        print(f"✓ Theme: primary_color={data['theme']['primary_color']}")
    
    def test_analytics_chart_data(self):
        """GET /api/analytics/chart-data?days=3 returns data points"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/chart-data?days=3",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert "date" in data[0]
        assert "plays" in data[0]
        print(f"✓ Analytics chart data: {len(data)} data points")
    
    def test_analytics_platform_breakdown(self):
        """GET /api/analytics/platform-breakdown returns platform list"""
        response = requests.get(
            f"{BASE_URL}/api/analytics/platform-breakdown",
            cookies=self.cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "name" in data[0]
        assert "percentage" in data[0]
        print(f"✓ Analytics platform breakdown: {len(data)} platforms")
    
    def test_kalmori_wallet(self):
        """GET /api/kalmori-wallet returns wallet with credits"""
        response = requests.get(f"{BASE_URL}/api/kalmori-wallet", cookies=self.cookies)
        assert response.status_code == 200
        data = response.json()
        assert "available_balance" in data
        assert "credits" in data
        print(f"✓ Kalmori wallet: ${data['available_balance']} available, {data['credits']} credits")


class TestSocialEndpoints:
    """Social/follower endpoints"""
    
    def test_follower_count(self):
        """GET /api/artists/{user_id}/follower-count returns follower_count"""
        response = requests.get(f"{BASE_URL}/api/artists/{ADMIN_USER_ID}/follower-count")
        assert response.status_code == 200
        data = response.json()
        assert "follower_count" in data
        print(f"✓ Follower count for admin: {data['follower_count']}")


class TestAdminCMSEndpoints:
    """Admin CMS endpoints with admin_key"""
    
    def test_admin_cms_all_pages(self):
        """GET /api/admin/cms/all-pages?admin_key=Admin123! returns pages list"""
        response = requests.get(
            f"{BASE_URL}/api/admin/cms/all-pages?admin_key={ADMIN_PASSWORD}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "pages" in data
        assert isinstance(data["pages"], list)
        page_ids = [p["id"] for p in data["pages"]]
        assert "homepage" in page_ids
        print(f"✓ Admin CMS all pages: {len(data['pages'])} pages")
    
    def test_admin_cms_invalid_key(self):
        """GET /api/admin/cms/all-pages with invalid key returns 403"""
        response = requests.get(
            f"{BASE_URL}/api/admin/cms/all-pages?admin_key=wrongkey"
        )
        assert response.status_code == 403
        print("✓ Admin CMS rejects invalid admin key")


class TestRecaptchaPage:
    """reCAPTCHA page endpoint"""
    
    def test_recaptcha_page(self):
        """GET /api/recaptcha-page returns HTML page"""
        response = requests.get(f"{BASE_URL}/api/recaptcha-page")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "reCAPTCHA" in response.text
        print("✓ reCAPTCHA page returns HTML")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
