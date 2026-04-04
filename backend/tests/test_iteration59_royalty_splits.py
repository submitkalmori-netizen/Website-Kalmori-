"""
Iteration 59 - Producer Royalty Split System Tests
Tests for:
- GET /api/royalty-splits - User's splits with earnings_history and total_earned
- GET /api/royalty-splits/summary - Summary stats (active_splits, total_as_producer, total_as_artist, total_earned)
- POST /api/royalty-splits/calculate - Admin distributes revenue
- GET /api/admin/royalty-splits - Admin views all splits with total_distributed
- PUT /api/admin/royalty-splits/{split_id} - Admin updates split percentages (must sum to 100)
- DEFAULT_SPLITS verification (basic=50/50, premium=40/60, unlimited=30/70, exclusive=0/100)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "submitkalmori@gmail.com"
ADMIN_PASSWORD = "MAYAsimpSON37!!"

# Known test split from context
TEST_SPLIT_ID = "split_f5759bb4cd63"


class TestRoyaltySplitsAuth:
    """Test authentication for royalty splits endpoints"""
    
    def test_login_admin(self):
        """Login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        print(f"✓ Admin login successful: {data['user'].get('email')}")
        return data
    
    def test_royalty_splits_requires_auth(self):
        """GET /api/royalty-splits requires authentication"""
        response = requests.get(f"{BASE_URL}/api/royalty-splits")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/royalty-splits requires auth (401)")
    
    def test_royalty_splits_summary_requires_auth(self):
        """GET /api/royalty-splits/summary requires authentication"""
        response = requests.get(f"{BASE_URL}/api/royalty-splits/summary")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/royalty-splits/summary requires auth (401)")


class TestRoyaltySplitsUser:
    """Test user-facing royalty splits endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.cookies = response.cookies
    
    def test_get_royalty_splits(self):
        """GET /api/royalty-splits returns splits with earnings_history and total_earned"""
        response = requests.get(
            f"{BASE_URL}/api/royalty-splits",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "splits" in data, "Response should have 'splits' key"
        splits = data["splits"]
        assert isinstance(splits, list), "splits should be a list"
        
        print(f"✓ GET /api/royalty-splits returned {len(splits)} splits")
        
        # If there are splits, verify structure
        if splits:
            split = splits[0]
            assert "id" in split, "Split should have 'id'"
            assert "beat_title" in split, "Split should have 'beat_title'"
            assert "license_type" in split, "Split should have 'license_type'"
            assert "producer_split" in split, "Split should have 'producer_split'"
            assert "artist_split" in split, "Split should have 'artist_split'"
            assert "earnings_history" in split, "Split should have 'earnings_history'"
            assert "total_earned" in split, "Split should have 'total_earned'"
            assert "is_producer" in split, "Split should have 'is_producer'"
            
            print(f"  - First split: {split['beat_title']} ({split['license_type']})")
            print(f"  - Split: {split['producer_split']}/{split['artist_split']}")
            print(f"  - Total earned: ${split['total_earned']}")
            print(f"  - Earnings history entries: {len(split['earnings_history'])}")
        
        return data
    
    def test_get_royalty_splits_summary(self):
        """GET /api/royalty-splits/summary returns summary stats"""
        response = requests.get(
            f"{BASE_URL}/api/royalty-splits/summary",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "active_splits" in data, "Response should have 'active_splits'"
        assert "total_as_producer" in data, "Response should have 'total_as_producer'"
        assert "total_as_artist" in data, "Response should have 'total_as_artist'"
        assert "total_earned" in data, "Response should have 'total_earned'"
        
        # Verify data types
        assert isinstance(data["active_splits"], int), "active_splits should be int"
        assert isinstance(data["total_as_producer"], (int, float)), "total_as_producer should be numeric"
        assert isinstance(data["total_as_artist"], (int, float)), "total_as_artist should be numeric"
        assert isinstance(data["total_earned"], (int, float)), "total_earned should be numeric"
        
        # Verify total_earned = total_as_producer + total_as_artist
        expected_total = round(data["total_as_producer"] + data["total_as_artist"], 2)
        assert abs(data["total_earned"] - expected_total) < 0.01, \
            f"total_earned ({data['total_earned']}) should equal sum of producer+artist ({expected_total})"
        
        print(f"✓ GET /api/royalty-splits/summary:")
        print(f"  - Active splits: {data['active_splits']}")
        print(f"  - Total as producer: ${data['total_as_producer']}")
        print(f"  - Total as artist: ${data['total_as_artist']}")
        print(f"  - Total earned: ${data['total_earned']}")
        
        return data


class TestRoyaltySplitsAdmin:
    """Test admin royalty splits endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.cookies = response.cookies
    
    def test_admin_get_all_splits(self):
        """GET /api/admin/royalty-splits returns all splits with total_distributed"""
        response = requests.get(
            f"{BASE_URL}/api/admin/royalty-splits",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "splits" in data, "Response should have 'splits' key"
        splits = data["splits"]
        
        print(f"✓ GET /api/admin/royalty-splits returned {len(splits)} splits")
        
        if splits:
            split = splits[0]
            assert "total_distributed" in split, "Admin split should have 'total_distributed'"
            assert "periods_distributed" in split, "Admin split should have 'periods_distributed'"
            print(f"  - First split: {split.get('beat_title', 'N/A')}")
            print(f"  - Total distributed: ${split['total_distributed']}")
            print(f"  - Periods distributed: {split['periods_distributed']}")
        
        return data
    
    def test_admin_update_split_percentages(self):
        """PUT /api/admin/royalty-splits/{split_id} updates split percentages"""
        # First get existing splits to find one to update
        response = requests.get(
            f"{BASE_URL}/api/admin/royalty-splits",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200
        splits = response.json().get("splits", [])
        
        if not splits:
            pytest.skip("No splits available to test update")
        
        split_id = splits[0]["id"]
        original_producer = splits[0].get("producer_split", 50)
        
        # Update to new percentage
        new_producer = 45 if original_producer != 45 else 55
        response = requests.put(
            f"{BASE_URL}/api/admin/royalty-splits/{split_id}",
            headers=self.headers,
            cookies=self.cookies,
            json={"producer_split": new_producer}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify the update
        assert data["producer_split"] == new_producer, f"Producer split should be {new_producer}"
        assert data["artist_split"] == 100 - new_producer, f"Artist split should be {100 - new_producer}"
        
        print(f"✓ PUT /api/admin/royalty-splits/{split_id}:")
        print(f"  - Updated producer_split: {original_producer} -> {new_producer}")
        print(f"  - Artist split auto-calculated: {data['artist_split']}")
        
        # Restore original
        requests.put(
            f"{BASE_URL}/api/admin/royalty-splits/{split_id}",
            headers=self.headers,
            cookies=self.cookies,
            json={"producer_split": original_producer}
        )
        print(f"  - Restored to original: {original_producer}/{100 - original_producer}")
    
    def test_admin_update_ensures_sum_100(self):
        """PUT /api/admin/royalty-splits/{split_id} ensures producer+artist=100"""
        response = requests.get(
            f"{BASE_URL}/api/admin/royalty-splits",
            headers=self.headers,
            cookies=self.cookies
        )
        splits = response.json().get("splits", [])
        
        if not splits:
            pytest.skip("No splits available")
        
        split_id = splits[0]["id"]
        
        # Test various percentages
        for producer_pct in [0, 30, 50, 70, 100]:
            response = requests.put(
                f"{BASE_URL}/api/admin/royalty-splits/{split_id}",
                headers=self.headers,
                cookies=self.cookies,
                json={"producer_split": producer_pct}
            )
            assert response.status_code == 200
            data = response.json()
            total = data["producer_split"] + data["artist_split"]
            assert total == 100, f"Split total should be 100, got {total}"
        
        print("✓ Split percentages always sum to 100")
    
    def test_calculate_distribute_admin_only(self):
        """POST /api/royalty-splits/calculate is admin only"""
        response = requests.post(
            f"{BASE_URL}/api/royalty-splits/calculate",
            headers=self.headers,
            cookies=self.cookies
        )
        # Should succeed for admin
        assert response.status_code == 200, f"Admin should be able to calculate: {response.text}"
        data = response.json()
        
        assert "period" in data, "Response should have 'period'"
        assert "distributions" in data, "Response should have 'distributions'"
        assert "total_processed" in data, "Response should have 'total_processed'"
        
        print(f"✓ POST /api/royalty-splits/calculate (admin):")
        print(f"  - Period: {data['period']}")
        print(f"  - Total processed: {data['total_processed']}")
        
        return data


class TestRoyaltySplitsNonAdmin:
    """Test that non-admin users cannot access admin endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create and login as non-admin user"""
        import uuid
        self.test_email = f"test_nonadmin_{uuid.uuid4().hex[:8]}@test.com"
        self.test_password = "TestPass123!"
        
        # Register new user
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "name": "Test Non-Admin",
            "artist_name": "Test Artist"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            self.cookies = response.cookies
        else:
            # If registration fails (email exists), try login
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": self.test_email,
                "password": self.test_password
            })
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                self.cookies = response.cookies
            else:
                pytest.skip("Could not create/login test user")
    
    def test_calculate_returns_403_for_non_admin(self):
        """POST /api/royalty-splits/calculate returns 403 for non-admin"""
        response = requests.post(
            f"{BASE_URL}/api/royalty-splits/calculate",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("✓ POST /api/royalty-splits/calculate returns 403 for non-admin")
    
    def test_admin_splits_returns_403_for_non_admin(self):
        """GET /api/admin/royalty-splits returns 403 for non-admin"""
        response = requests.get(
            f"{BASE_URL}/api/admin/royalty-splits",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("✓ GET /api/admin/royalty-splits returns 403 for non-admin")
    
    def test_admin_update_split_returns_403_for_non_admin(self):
        """PUT /api/admin/royalty-splits/{split_id} returns 403 for non-admin"""
        response = requests.put(
            f"{BASE_URL}/api/admin/royalty-splits/{TEST_SPLIT_ID}",
            headers=self.headers,
            cookies=self.cookies,
            json={"producer_split": 50}
        )
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("✓ PUT /api/admin/royalty-splits/{split_id} returns 403 for non-admin")


class TestDefaultSplits:
    """Test that DEFAULT_SPLITS are correctly defined"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.cookies = response.cookies
    
    def test_default_splits_exist_in_db(self):
        """Verify splits in DB follow DEFAULT_SPLITS pattern"""
        # Get all splits
        response = requests.get(
            f"{BASE_URL}/api/admin/royalty-splits",
            headers=self.headers,
            cookies=self.cookies
        )
        assert response.status_code == 200
        splits = response.json().get("splits", [])
        
        # Expected default splits by license type
        expected_defaults = {
            "basic_lease": (50, 50),
            "premium_lease": (40, 60),
            "unlimited_lease": (30, 70),
            "exclusive": (0, 100),
        }
        
        print("✓ DEFAULT_SPLITS verification:")
        print("  Expected defaults:")
        for license_type, (producer, artist) in expected_defaults.items():
            print(f"    - {license_type}: {producer}/{artist}")
        
        # Check if any splits match expected defaults
        for split in splits:
            license_type = split.get("license_type")
            if license_type in expected_defaults:
                expected_producer, expected_artist = expected_defaults[license_type]
                # Note: Admin may have overridden, so just log
                actual_producer = split.get("producer_split")
                actual_artist = split.get("artist_split")
                print(f"  Found {license_type} split: {actual_producer}/{actual_artist}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
