"""
Iteration 66 - Page Builder Seeding & User Cleanup Tests
Tests:
1. Page builder seed endpoints (seed-all-pages, seed-defaults for each page)
2. GET page layouts return correct block counts
3. DELETE non-admin users cleanup endpoint
4. All endpoints require admin auth
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "submitkalmori@gmail.com"
ADMIN_PASSWORD = "Admin123!"
SECONDARY_ADMIN_EMAIL = "admin@kalmori.com"

class TestPageBuilderSeeding:
    """Test page builder seeding endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if login_response.status_code != 200:
            # Try secondary admin
            login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
                "email": SECONDARY_ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
        
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        self.admin_token = login_response.json().get("token")
        if self.admin_token:
            self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
        yield
        self.session.close()
    
    # ===== AUTH REQUIRED TESTS =====
    
    def test_seed_all_pages_requires_auth(self):
        """POST /api/admin/seed-all-pages requires admin auth"""
        no_auth_session = requests.Session()
        response = no_auth_session.post(f"{BASE_URL}/api/admin/seed-all-pages")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ seed-all-pages requires auth")
    
    def test_seed_defaults_requires_auth(self):
        """POST /api/admin/pages/{slug}/seed-defaults requires admin auth"""
        no_auth_session = requests.Session()
        response = no_auth_session.post(f"{BASE_URL}/api/admin/pages/landing/seed-defaults")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ seed-defaults requires auth")
    
    def test_get_page_layout_requires_auth(self):
        """GET /api/admin/pages/{slug} requires admin auth"""
        no_auth_session = requests.Session()
        response = no_auth_session.get(f"{BASE_URL}/api/admin/pages/landing")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ get page layout requires auth")
    
    def test_user_cleanup_requires_auth(self):
        """DELETE /api/admin/users/cleanup/non-admin requires admin auth"""
        no_auth_session = requests.Session()
        response = no_auth_session.delete(f"{BASE_URL}/api/admin/users/cleanup/non-admin")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ user cleanup requires auth")
    
    # ===== SEED ALL PAGES =====
    
    def test_seed_all_pages(self):
        """POST /api/admin/seed-all-pages seeds Landing (14), About (5), Pricing (4)"""
        response = self.session.post(f"{BASE_URL}/api/admin/seed-all-pages")
        assert response.status_code == 200, f"seed-all-pages failed: {response.text}"
        
        data = response.json()
        assert "pages" in data, "Response should have 'pages' field"
        assert "message" in data, "Response should have 'message' field"
        
        pages = {p["slug"]: p["blocks"] for p in data["pages"]}
        
        # Verify block counts
        assert pages.get("landing") == 14, f"Landing should have 14 blocks, got {pages.get('landing')}"
        assert pages.get("about") == 5, f"About should have 5 blocks, got {pages.get('about')}"
        assert pages.get("pricing") == 4, f"Pricing should have 4 blocks, got {pages.get('pricing')}"
        
        print(f"✓ seed-all-pages: Landing={pages.get('landing')}, About={pages.get('about')}, Pricing={pages.get('pricing')}")
    
    # ===== SEED INDIVIDUAL PAGES =====
    
    def test_seed_landing_page(self):
        """POST /api/admin/pages/landing/seed-defaults seeds 14 blocks"""
        response = self.session.post(f"{BASE_URL}/api/admin/pages/landing/seed-defaults")
        assert response.status_code == 200, f"seed landing failed: {response.text}"
        
        data = response.json()
        assert data.get("block_count") == 14, f"Landing should have 14 blocks, got {data.get('block_count')}"
        assert data.get("page_slug") == "landing"
        print(f"✓ seed-defaults landing: {data.get('block_count')} blocks")
    
    def test_seed_about_page(self):
        """POST /api/admin/pages/about/seed-defaults seeds 5 blocks"""
        response = self.session.post(f"{BASE_URL}/api/admin/pages/about/seed-defaults")
        assert response.status_code == 200, f"seed about failed: {response.text}"
        
        data = response.json()
        assert data.get("block_count") == 5, f"About should have 5 blocks, got {data.get('block_count')}"
        assert data.get("page_slug") == "about"
        print(f"✓ seed-defaults about: {data.get('block_count')} blocks")
    
    def test_seed_pricing_page(self):
        """POST /api/admin/pages/pricing/seed-defaults seeds 4 blocks"""
        response = self.session.post(f"{BASE_URL}/api/admin/pages/pricing/seed-defaults")
        assert response.status_code == 200, f"seed pricing failed: {response.text}"
        
        data = response.json()
        assert data.get("block_count") == 4, f"Pricing should have 4 blocks, got {data.get('block_count')}"
        assert data.get("page_slug") == "pricing"
        print(f"✓ seed-defaults pricing: {data.get('block_count')} blocks")
    
    def test_seed_invalid_page_returns_400(self):
        """POST /api/admin/pages/invalid/seed-defaults returns 400"""
        response = self.session.post(f"{BASE_URL}/api/admin/pages/invalid-page/seed-defaults")
        assert response.status_code == 400, f"Expected 400 for invalid page, got {response.status_code}"
        print("✓ seed-defaults invalid page returns 400")
    
    # ===== GET PAGE LAYOUTS =====
    
    def test_get_landing_page_layout(self):
        """GET /api/admin/pages/landing returns 14 blocks with correct content"""
        response = self.session.get(f"{BASE_URL}/api/admin/pages/landing")
        assert response.status_code == 200, f"get landing failed: {response.text}"
        
        data = response.json()
        blocks = data.get("blocks", [])
        assert len(blocks) == 14, f"Landing should have 14 blocks, got {len(blocks)}"
        
        # Verify first block is hero with G.O.A.T content
        hero_block = blocks[0]
        assert hero_block.get("type") == "hero", f"First block should be hero, got {hero_block.get('type')}"
        assert "G.O.A.T" in hero_block.get("content", {}).get("title", ""), "Hero should have G.O.A.T in title"
        
        # Verify block types present
        block_types = [b.get("type") for b in blocks]
        assert "hero" in block_types
        assert "features" in block_types
        assert "pricing" in block_types
        assert "cta" in block_types
        
        print(f"✓ GET landing: {len(blocks)} blocks, hero title contains 'G.O.A.T'")
    
    def test_get_about_page_layout(self):
        """GET /api/admin/pages/about returns 5 blocks"""
        response = self.session.get(f"{BASE_URL}/api/admin/pages/about")
        assert response.status_code == 200, f"get about failed: {response.text}"
        
        data = response.json()
        blocks = data.get("blocks", [])
        assert len(blocks) == 5, f"About should have 5 blocks, got {len(blocks)}"
        
        # Verify first block is hero with About Kalmori content
        hero_block = blocks[0]
        assert hero_block.get("type") == "hero", f"First block should be hero, got {hero_block.get('type')}"
        assert "About Kalmori" in hero_block.get("content", {}).get("title", ""), "Hero should have 'About Kalmori' in title"
        
        print(f"✓ GET about: {len(blocks)} blocks")
    
    def test_get_pricing_page_layout(self):
        """GET /api/admin/pages/pricing returns 4 blocks"""
        response = self.session.get(f"{BASE_URL}/api/admin/pages/pricing")
        assert response.status_code == 200, f"get pricing failed: {response.text}"
        
        data = response.json()
        blocks = data.get("blocks", [])
        assert len(blocks) == 4, f"Pricing should have 4 blocks, got {len(blocks)}"
        
        # Verify first block is hero with pricing content
        hero_block = blocks[0]
        assert hero_block.get("type") == "hero", f"First block should be hero, got {hero_block.get('type')}"
        assert "Pricing" in hero_block.get("content", {}).get("title", ""), "Hero should have 'Pricing' in title"
        
        print(f"✓ GET pricing: {len(blocks)} blocks")
    
    # ===== LANDING PAGE CONTENT VERIFICATION =====
    
    def test_landing_page_has_correct_block_content(self):
        """Verify landing page blocks have correct Kalmori content"""
        response = self.session.get(f"{BASE_URL}/api/admin/pages/landing")
        assert response.status_code == 200
        
        blocks = response.json().get("blocks", [])
        
        # Check for specific content
        all_content = str(blocks)
        
        # Hero content
        assert "G.O.A.T" in all_content, "Should have G.O.A.T hero content"
        assert "DISTRIBUTE MY MUSIC ONLINE" in all_content, "Should have CTA button text"
        
        # Features content
        assert "AI Release Strategy" in all_content, "Should have AI Release Strategy feature"
        assert "Real-Time Analytics" in all_content, "Should have Real-Time Analytics feature"
        
        # Pricing content
        assert "FREE" in all_content or "Free" in all_content, "Should have Free plan"
        assert "SINGLE" in all_content or "Rise" in all_content, "Should have Single/Rise plan"
        
        # Stats content
        assert "150+" in all_content, "Should have 150+ platforms stat"
        assert "100%" in all_content, "Should have 100% royalties stat"
        
        print("✓ Landing page has correct Kalmori content")
    
    # ===== USER CLEANUP =====
    
    def test_user_cleanup_non_admin(self):
        """DELETE /api/admin/users/cleanup/non-admin removes non-admin users"""
        response = self.session.delete(f"{BASE_URL}/api/admin/users/cleanup/non-admin")
        assert response.status_code == 200, f"user cleanup failed: {response.text}"
        
        data = response.json()
        assert "deleted_count" in data, "Response should have 'deleted_count'"
        assert "message" in data, "Response should have 'message'"
        
        print(f"✓ User cleanup: deleted {data.get('deleted_count')} non-admin users")
    
    def test_verify_only_admins_remain(self):
        """Verify only admin users remain after cleanup"""
        # First run cleanup
        self.session.delete(f"{BASE_URL}/api/admin/users/cleanup/non-admin")
        
        # Get all users
        response = self.session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 200, f"get users failed: {response.text}"
        
        data = response.json()
        users = data.get("users", [])
        
        # All remaining users should be admins
        for user in users:
            assert user.get("role") == "admin", f"Non-admin user found: {user.get('email')}"
        
        # Verify expected admin emails
        admin_emails = [u.get("email") for u in users]
        assert ADMIN_EMAIL in admin_emails or SECONDARY_ADMIN_EMAIL in admin_emails, "At least one admin should exist"
        
        print(f"✓ Only {len(users)} admin users remain: {admin_emails}")
    
    # ===== BLOCK OPERATIONS =====
    
    def test_add_block_to_page(self):
        """POST /api/admin/pages/{slug}/add-block adds a new block"""
        response = self.session.post(f"{BASE_URL}/api/admin/pages/landing/add-block", json={
            "type": "text",
            "order": 99
        })
        assert response.status_code == 200, f"add block failed: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should have block 'id'"
        assert data.get("type") == "text", "Block type should be 'text'"
        
        # Clean up - delete the added block
        block_id = data.get("id")
        self.session.delete(f"{BASE_URL}/api/admin/pages/landing/blocks/{block_id}")
        
        print(f"✓ Add block: created block {block_id}")
    
    def test_delete_block_from_page(self):
        """DELETE /api/admin/pages/{slug}/blocks/{block_id} deletes a block"""
        # First add a block
        add_response = self.session.post(f"{BASE_URL}/api/admin/pages/landing/add-block", json={
            "type": "spacer",
            "order": 99
        })
        assert add_response.status_code == 200
        block_id = add_response.json().get("id")
        
        # Delete the block
        delete_response = self.session.delete(f"{BASE_URL}/api/admin/pages/landing/blocks/{block_id}")
        assert delete_response.status_code == 200, f"delete block failed: {delete_response.text}"
        
        data = delete_response.json()
        assert "message" in data
        
        print(f"✓ Delete block: removed block {block_id}")
    
    def test_save_page_layout(self):
        """PUT /api/admin/pages/{slug} saves page layout"""
        # Get current layout
        get_response = self.session.get(f"{BASE_URL}/api/admin/pages/landing")
        current_blocks = get_response.json().get("blocks", [])
        
        # Save with same blocks
        save_response = self.session.put(f"{BASE_URL}/api/admin/pages/landing", json={
            "blocks": current_blocks,
            "title": "Landing Page"
        })
        assert save_response.status_code == 200, f"save layout failed: {save_response.text}"
        
        data = save_response.json()
        assert "message" in data
        assert data.get("page_slug") == "landing"
        
        print("✓ Save page layout works")


class TestPageBuilderBlockCounts:
    """Verify exact block counts for each page"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if login_response.status_code != 200:
            login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
                "email": SECONDARY_ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
        
        assert login_response.status_code == 200
        self.admin_token = login_response.json().get("token")
        if self.admin_token:
            self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
        yield
        self.session.close()
    
    def test_landing_has_14_blocks(self):
        """Landing page should have exactly 14 blocks"""
        # Seed first to ensure correct state
        self.session.post(f"{BASE_URL}/api/admin/pages/landing/seed-defaults")
        
        response = self.session.get(f"{BASE_URL}/api/admin/pages/landing")
        assert response.status_code == 200
        
        blocks = response.json().get("blocks", [])
        assert len(blocks) == 14, f"Expected 14 blocks, got {len(blocks)}"
        print(f"✓ Landing has exactly 14 blocks")
    
    def test_about_has_5_blocks(self):
        """About page should have exactly 5 blocks"""
        # Seed first
        self.session.post(f"{BASE_URL}/api/admin/pages/about/seed-defaults")
        
        response = self.session.get(f"{BASE_URL}/api/admin/pages/about")
        assert response.status_code == 200
        
        blocks = response.json().get("blocks", [])
        assert len(blocks) == 5, f"Expected 5 blocks, got {len(blocks)}"
        print(f"✓ About has exactly 5 blocks")
    
    def test_pricing_has_4_blocks(self):
        """Pricing page should have exactly 4 blocks"""
        # Seed first
        self.session.post(f"{BASE_URL}/api/admin/pages/pricing/seed-defaults")
        
        response = self.session.get(f"{BASE_URL}/api/admin/pages/pricing")
        assert response.status_code == 200
        
        blocks = response.json().get("blocks", [])
        assert len(blocks) == 4, f"Expected 4 blocks, got {len(blocks)}"
        print(f"✓ Pricing has exactly 4 blocks")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
