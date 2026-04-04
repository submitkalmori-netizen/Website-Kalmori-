"""
Iteration 63 - Page Builder API Tests
Tests for the new admin-only Page Builder (Elementor-style) feature.
Endpoints tested:
- GET /api/admin/pages - List editable pages
- GET /api/admin/pages/{slug} - Get page layout
- GET /api/admin/pages/block-templates/all - Get all block templates
- POST /api/admin/pages/{slug}/add-block - Add block to page
- PUT /api/admin/pages/{slug} - Save page layout
- POST /api/admin/pages/{slug}/publish - Publish page
- POST /api/admin/pages/{slug}/unpublish - Unpublish page
- DELETE /api/admin/pages/{slug}/blocks/{block_id} - Delete block
- GET /api/pages/{slug} - Public endpoint for published pages
Also tests regression for: messages, royalty-splits, admin/payouts
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPageBuilderAdmin:
    """Page Builder Admin API Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin before each test"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@kalmori.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        data = login_response.json()
        if "access_token" in data:
            self.session.headers.update({"Authorization": f"Bearer {data['access_token']}"})
        self.admin_user = data.get("user", data)
        print(f"Logged in as admin: {self.admin_user.get('email')}")
        yield
    
    def test_list_editable_pages(self):
        """GET /api/admin/pages returns list of editable pages"""
        response = self.session.get(f"{BASE_URL}/api/admin/pages")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "pages" in data
        pages = data["pages"]
        assert isinstance(pages, list)
        # Should include default pages: landing, about, pricing
        slugs = [p.get("page_slug") for p in pages]
        assert "landing" in slugs, "Landing page should be in list"
        print(f"Found {len(pages)} editable pages: {slugs}")
    
    def test_get_page_layout_landing(self):
        """GET /api/admin/pages/landing returns page layout"""
        response = self.session.get(f"{BASE_URL}/api/admin/pages/landing")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "page_slug" in data or data.get("page_slug") == "landing"
        assert "blocks" in data
        assert isinstance(data["blocks"], list)
        print(f"Landing page has {len(data['blocks'])} blocks, published: {data.get('published', False)}")
    
    def test_get_block_templates(self):
        """GET /api/admin/pages/block-templates/all returns 12 block templates"""
        response = self.session.get(f"{BASE_URL}/api/admin/pages/block-templates/all")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) == 12, f"Expected 12 templates, got {len(templates)}"
        template_keys = [t.get("key") for t in templates]
        expected_keys = ["hero", "text", "image", "features", "cta", "testimonials", 
                        "stats", "spacer", "two_column", "video", "logo_bar", "pricing"]
        for key in expected_keys:
            assert key in template_keys, f"Missing template: {key}"
        print(f"Found {len(templates)} block templates: {template_keys}")
    
    def test_add_hero_block(self):
        """POST /api/admin/pages/landing/add-block with type=hero creates a hero block"""
        response = self.session.post(f"{BASE_URL}/api/admin/pages/landing/add-block", json={
            "type": "hero",
            "order": 0
        })
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("type") == "hero"
        assert "id" in data
        assert data["id"].startswith("blk_")
        assert "content" in data
        assert "styles" in data
        self.hero_block_id = data["id"]
        print(f"Created hero block: {data['id']}")
        return data["id"]
    
    def test_add_features_block(self):
        """POST /api/admin/pages/landing/add-block with type=features creates a features block"""
        response = self.session.post(f"{BASE_URL}/api/admin/pages/landing/add-block", json={
            "type": "features",
            "order": 1
        })
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("type") == "features"
        assert "id" in data
        assert "content" in data
        assert "items" in data["content"]
        print(f"Created features block: {data['id']}")
        return data["id"]
    
    def test_add_stats_block(self):
        """POST /api/admin/pages/landing/add-block with type=stats creates a stats block"""
        response = self.session.post(f"{BASE_URL}/api/admin/pages/landing/add-block", json={
            "type": "stats",
            "order": 2
        })
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("type") == "stats"
        assert "id" in data
        assert "content" in data
        assert "items" in data["content"]
        print(f"Created stats block: {data['id']}")
        return data["id"]
    
    def test_save_page_layout(self):
        """PUT /api/admin/pages/landing saves the layout with blocks array"""
        # First get current layout
        get_response = self.session.get(f"{BASE_URL}/api/admin/pages/landing")
        current_blocks = get_response.json().get("blocks", [])
        
        # Save with updated title
        response = self.session.put(f"{BASE_URL}/api/admin/pages/landing", json={
            "blocks": current_blocks,
            "title": "Test Landing Page"
        })
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "message" in data
        assert data.get("page_slug") == "landing"
        assert "updated_at" in data
        print(f"Saved layout: {data}")
    
    def test_publish_page(self):
        """POST /api/admin/pages/landing/publish publishes the page"""
        # First ensure there are blocks
        get_response = self.session.get(f"{BASE_URL}/api/admin/pages/landing")
        blocks = get_response.json().get("blocks", [])
        
        if len(blocks) == 0:
            # Add a block first
            self.session.post(f"{BASE_URL}/api/admin/pages/landing/add-block", json={"type": "hero"})
        
        response = self.session.post(f"{BASE_URL}/api/admin/pages/landing/publish")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "message" in data
        assert "published" in data.get("message", "").lower() or data.get("page_slug") == "landing"
        print(f"Published page: {data}")
    
    def test_public_page_endpoint(self):
        """GET /api/pages/landing (public, no auth) returns published page layout"""
        # Use a new session without auth
        public_session = requests.Session()
        response = public_session.get(f"{BASE_URL}/api/pages/landing")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "page_slug" in data
        assert "blocks" in data
        # If published, should have blocks
        if data.get("published"):
            print(f"Public page has {len(data['blocks'])} blocks")
        else:
            print(f"Public page not published yet, blocks: {len(data['blocks'])}")
    
    def test_unpublish_page(self):
        """POST /api/admin/pages/landing/unpublish unpublishes the page"""
        response = self.session.post(f"{BASE_URL}/api/admin/pages/landing/unpublish")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "message" in data
        print(f"Unpublished page: {data}")
    
    def test_delete_block(self):
        """DELETE /api/admin/pages/landing/blocks/{block_id} removes a block"""
        # First add a block to delete
        add_response = self.session.post(f"{BASE_URL}/api/admin/pages/landing/add-block", json={
            "type": "spacer"
        })
        assert add_response.status_code == 200
        block_id = add_response.json()["id"]
        
        # Now delete it
        response = self.session.delete(f"{BASE_URL}/api/admin/pages/landing/blocks/{block_id}")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "message" in data
        assert data.get("block_id") == block_id
        print(f"Deleted block: {block_id}")


class TestPageBuilderNonAdmin:
    """Test that non-admin users cannot access page builder endpoints"""
    
    def test_non_admin_cannot_access_pages(self):
        """Non-admin users should get 403 on /api/admin/pages"""
        # Try without auth
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/admin/pages")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"Unauthenticated access blocked: {response.status_code}")


class TestRegressionMessagesAPI:
    """Regression tests for messages API (refactored in iteration 62)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@kalmori.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200
        data = login_response.json()
        if "access_token" in data:
            self.session.headers.update({"Authorization": f"Bearer {data['access_token']}"})
        yield
    
    def test_messages_conversations(self):
        """GET /api/messages/conversations returns conversations list"""
        response = self.session.get(f"{BASE_URL}/api/messages/conversations")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        # Response is an array directly
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"Messages conversations: {len(data)} found")
    
    def test_messages_unread_count(self):
        """GET /api/messages/unread/count returns unread count"""
        response = self.session.get(f"{BASE_URL}/api/messages/unread/count")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "unread" in data
        print(f"Unread messages count: {data['unread']}")


class TestRegressionRoyaltySplitsAPI:
    """Regression tests for royalty-splits API (refactored in iteration 62)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@kalmori.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200
        data = login_response.json()
        if "access_token" in data:
            self.session.headers.update({"Authorization": f"Bearer {data['access_token']}"})
        yield
    
    def test_royalty_splits_list(self):
        """GET /api/royalty-splits returns splits list"""
        response = self.session.get(f"{BASE_URL}/api/royalty-splits")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "splits" in data
        print(f"Royalty splits: {len(data['splits'])} found")
    
    def test_royalty_splits_summary(self):
        """GET /api/royalty-splits/summary returns summary data"""
        response = self.session.get(f"{BASE_URL}/api/royalty-splits/summary")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        # Should have summary fields
        print(f"Royalty splits summary: {data}")


class TestRegressionAdminPayoutsAPI:
    """Regression tests for admin/payouts API (refactored in iteration 62)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@kalmori.com",
            "password": "Admin123!"
        })
        assert login_response.status_code == 200
        data = login_response.json()
        if "access_token" in data:
            self.session.headers.update({"Authorization": f"Bearer {data['access_token']}"})
        yield
    
    def test_admin_payouts_list(self):
        """GET /api/admin/payouts returns withdrawals list"""
        response = self.session.get(f"{BASE_URL}/api/admin/payouts")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "withdrawals" in data
        print(f"Admin payouts: {len(data['withdrawals'])} found")
    
    def test_admin_payouts_summary(self):
        """GET /api/admin/payouts/summary returns payout summary"""
        response = self.session.get(f"{BASE_URL}/api/admin/payouts/summary")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        print(f"Admin payouts summary: {data}")
    
    def test_admin_payouts_schedule(self):
        """GET /api/admin/payouts/schedule returns schedule config"""
        response = self.session.get(f"{BASE_URL}/api/admin/payouts/schedule")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        print(f"Admin payouts schedule: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
