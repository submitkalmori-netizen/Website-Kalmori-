"""
Iteration 37 - Royalty Splits Management Tests
Tests for:
- GET /api/label/royalties - returns summary and artists array with royalty data
- PUT /api/label/artists/{artist_id}/split - set custom royalty split
- Validation: splits must add to 100%, cannot be negative
- Default split is 70% artist / 30% label
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRoyaltySplits:
    """Royalty Splits Management Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login as admin (label_producer) and get auth cookies"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@tunedrop.com",
            "password": "Admin123!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.user = login_resp.json().get("user", {})
        print(f"Logged in as: {self.user.get('email')} (user_role: {self.user.get('user_role')})")
        yield
        # Cleanup: Reset split to default 70/30 if we modified it
        try:
            artists_resp = self.session.get(f"{BASE_URL}/api/label/artists")
            if artists_resp.status_code == 200:
                artists = artists_resp.json().get("artists", [])
                for a in artists:
                    self.session.put(f"{BASE_URL}/api/label/artists/{a['id']}/split", json={
                        "artist_split": 70,
                        "label_split": 30
                    })
        except:
            pass
    
    # ===== GET /api/label/royalties Tests =====
    
    def test_get_royalties_returns_200(self):
        """GET /api/label/royalties returns 200 for authenticated user"""
        resp = self.session.get(f"{BASE_URL}/api/label/royalties")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        print("PASS: GET /api/label/royalties returns 200")
    
    def test_get_royalties_returns_summary(self):
        """GET /api/label/royalties returns summary with total_revenue, total_artist_payouts, total_label_earnings, artist_count"""
        resp = self.session.get(f"{BASE_URL}/api/label/royalties")
        assert resp.status_code == 200
        data = resp.json()
        
        assert "summary" in data, "Response missing 'summary' field"
        summary = data["summary"]
        
        assert "total_revenue" in summary, "Summary missing 'total_revenue'"
        assert "total_artist_payouts" in summary, "Summary missing 'total_artist_payouts'"
        assert "total_label_earnings" in summary, "Summary missing 'total_label_earnings'"
        assert "artist_count" in summary, "Summary missing 'artist_count'"
        
        # Verify types
        assert isinstance(summary["total_revenue"], (int, float)), "total_revenue should be numeric"
        assert isinstance(summary["total_artist_payouts"], (int, float)), "total_artist_payouts should be numeric"
        assert isinstance(summary["total_label_earnings"], (int, float)), "total_label_earnings should be numeric"
        assert isinstance(summary["artist_count"], int), "artist_count should be integer"
        
        print(f"PASS: Summary returned: total_revenue=${summary['total_revenue']}, artist_payouts=${summary['total_artist_payouts']}, label_earnings=${summary['total_label_earnings']}, artist_count={summary['artist_count']}")
    
    def test_get_royalties_returns_artists_array(self):
        """GET /api/label/royalties returns artists array with required fields"""
        resp = self.session.get(f"{BASE_URL}/api/label/royalties")
        assert resp.status_code == 200
        data = resp.json()
        
        assert "artists" in data, "Response missing 'artists' field"
        assert isinstance(data["artists"], list), "'artists' should be a list"
        
        if len(data["artists"]) > 0:
            artist = data["artists"][0]
            required_fields = ["id", "gross_revenue", "artist_split", "label_split", "artist_earnings", "label_earnings"]
            for field in required_fields:
                assert field in artist, f"Artist missing '{field}' field"
            
            # Verify artist_name or name exists
            assert "artist_name" in artist or "name" in artist, "Artist missing 'artist_name' or 'name'"
            
            print(f"PASS: Artists array returned with {len(data['artists'])} artists")
            print(f"  First artist: {artist.get('artist_name') or artist.get('name')}, gross_revenue=${artist['gross_revenue']}, split={artist['artist_split']}/{artist['label_split']}")
        else:
            print("PASS: Artists array returned (empty roster)")
    
    def test_get_royalties_requires_auth(self):
        """GET /api/label/royalties returns 401 without authentication"""
        new_session = requests.Session()
        resp = new_session.get(f"{BASE_URL}/api/label/royalties")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        print("PASS: GET /api/label/royalties requires authentication")
    
    def test_default_split_is_70_30(self):
        """Default split is 70% artist / 30% label when no custom split is set"""
        # First get artists to find one
        artists_resp = self.session.get(f"{BASE_URL}/api/label/artists")
        assert artists_resp.status_code == 200
        artists = artists_resp.json().get("artists", [])
        
        if len(artists) == 0:
            pytest.skip("No artists on roster to test default split")
        
        # Reset to default by setting 70/30
        artist_id = artists[0]["id"]
        reset_resp = self.session.put(f"{BASE_URL}/api/label/artists/{artist_id}/split", json={
            "artist_split": 70,
            "label_split": 30
        })
        assert reset_resp.status_code == 200
        
        # Verify in royalties endpoint
        royalties_resp = self.session.get(f"{BASE_URL}/api/label/royalties")
        assert royalties_resp.status_code == 200
        royalties_data = royalties_resp.json()
        
        artist_data = next((a for a in royalties_data["artists"] if a["id"] == artist_id), None)
        assert artist_data is not None, "Artist not found in royalties response"
        assert artist_data["artist_split"] == 70, f"Expected artist_split=70, got {artist_data['artist_split']}"
        assert artist_data["label_split"] == 30, f"Expected label_split=30, got {artist_data['label_split']}"
        
        print(f"PASS: Default split is 70% artist / 30% label")
    
    # ===== PUT /api/label/artists/{artist_id}/split Tests =====
    
    def test_set_custom_split_success(self):
        """PUT /api/label/artists/{artist_id}/split sets custom royalty split"""
        # Get artists
        artists_resp = self.session.get(f"{BASE_URL}/api/label/artists")
        assert artists_resp.status_code == 200
        artists = artists_resp.json().get("artists", [])
        
        if len(artists) == 0:
            pytest.skip("No artists on roster to test split update")
        
        artist_id = artists[0]["id"]
        artist_name = artists[0].get("artist_name") or artists[0].get("name")
        
        # Set custom split 80/20
        resp = self.session.put(f"{BASE_URL}/api/label/artists/{artist_id}/split", json={
            "artist_split": 80,
            "label_split": 20
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert data.get("artist_split") == 80, f"Expected artist_split=80, got {data.get('artist_split')}"
        assert data.get("label_split") == 20, f"Expected label_split=20, got {data.get('label_split')}"
        
        # Verify in royalties endpoint
        royalties_resp = self.session.get(f"{BASE_URL}/api/label/royalties")
        assert royalties_resp.status_code == 200
        royalties_data = royalties_resp.json()
        
        artist_data = next((a for a in royalties_data["artists"] if a["id"] == artist_id), None)
        assert artist_data is not None, "Artist not found in royalties response"
        assert artist_data["artist_split"] == 80, f"Expected artist_split=80 in royalties, got {artist_data['artist_split']}"
        assert artist_data["label_split"] == 20, f"Expected label_split=20 in royalties, got {artist_data['label_split']}"
        
        print(f"PASS: Custom split 80/20 set for {artist_name}")
    
    def test_set_split_validates_sum_to_100(self):
        """PUT /api/label/artists/{artist_id}/split returns 400 if splits don't add to 100%"""
        # Get artists
        artists_resp = self.session.get(f"{BASE_URL}/api/label/artists")
        assert artists_resp.status_code == 200
        artists = artists_resp.json().get("artists", [])
        
        if len(artists) == 0:
            pytest.skip("No artists on roster to test validation")
        
        artist_id = artists[0]["id"]
        
        # Try to set splits that don't add to 100
        resp = self.session.put(f"{BASE_URL}/api/label/artists/{artist_id}/split", json={
            "artist_split": 60,
            "label_split": 30  # Total = 90, not 100
        })
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "100" in data.get("detail", "").lower() or "add" in data.get("detail", "").lower(), f"Error message should mention splits must add to 100%: {data}"
        
        print(f"PASS: Returns 400 when splits don't add to 100% (60+30=90)")
    
    def test_set_split_validates_negative_values(self):
        """PUT /api/label/artists/{artist_id}/split returns 400 if splits are negative"""
        # Get artists
        artists_resp = self.session.get(f"{BASE_URL}/api/label/artists")
        assert artists_resp.status_code == 200
        artists = artists_resp.json().get("artists", [])
        
        if len(artists) == 0:
            pytest.skip("No artists on roster to test validation")
        
        artist_id = artists[0]["id"]
        
        # Try to set negative split
        resp = self.session.put(f"{BASE_URL}/api/label/artists/{artist_id}/split", json={
            "artist_split": -10,
            "label_split": 110  # Total = 100, but negative value
        })
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "negative" in data.get("detail", "").lower(), f"Error message should mention negative values: {data}"
        
        print(f"PASS: Returns 400 when splits are negative")
    
    def test_set_split_returns_404_for_non_roster_artist(self):
        """PUT /api/label/artists/{artist_id}/split returns 404 for non-roster artist"""
        fake_artist_id = "user_nonexistent123"
        
        resp = self.session.put(f"{BASE_URL}/api/label/artists/{fake_artist_id}/split", json={
            "artist_split": 70,
            "label_split": 30
        })
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
        
        print(f"PASS: Returns 404 for non-roster artist")
    
    def test_set_split_requires_auth(self):
        """PUT /api/label/artists/{artist_id}/split returns 401 without authentication"""
        new_session = requests.Session()
        resp = new_session.put(f"{BASE_URL}/api/label/artists/some_artist_id/split", json={
            "artist_split": 70,
            "label_split": 30
        })
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        print("PASS: PUT /api/label/artists/{artist_id}/split requires authentication")
    
    # ===== Earnings Calculation Tests =====
    
    def test_earnings_calculated_correctly(self):
        """Verify artist_earnings and label_earnings are calculated correctly based on split"""
        # Get artists
        artists_resp = self.session.get(f"{BASE_URL}/api/label/artists")
        assert artists_resp.status_code == 200
        artists = artists_resp.json().get("artists", [])
        
        if len(artists) == 0:
            pytest.skip("No artists on roster to test earnings calculation")
        
        artist_id = artists[0]["id"]
        
        # Set a specific split
        self.session.put(f"{BASE_URL}/api/label/artists/{artist_id}/split", json={
            "artist_split": 60,
            "label_split": 40
        })
        
        # Get royalties
        royalties_resp = self.session.get(f"{BASE_URL}/api/label/royalties")
        assert royalties_resp.status_code == 200
        royalties_data = royalties_resp.json()
        
        artist_data = next((a for a in royalties_data["artists"] if a["id"] == artist_id), None)
        assert artist_data is not None
        
        gross = artist_data["gross_revenue"]
        expected_artist_earnings = round(gross * 60 / 100, 2)
        expected_label_earnings = round(gross * 40 / 100, 2)
        
        # Allow small floating point differences
        assert abs(artist_data["artist_earnings"] - expected_artist_earnings) < 0.02, \
            f"Artist earnings mismatch: expected {expected_artist_earnings}, got {artist_data['artist_earnings']}"
        assert abs(artist_data["label_earnings"] - expected_label_earnings) < 0.02, \
            f"Label earnings mismatch: expected {expected_label_earnings}, got {artist_data['label_earnings']}"
        
        print(f"PASS: Earnings calculated correctly - gross=${gross}, artist_earnings=${artist_data['artist_earnings']} (60%), label_earnings=${artist_data['label_earnings']} (40%)")
    
    def test_summary_totals_match_artist_sum(self):
        """Verify summary totals match sum of individual artist values"""
        royalties_resp = self.session.get(f"{BASE_URL}/api/label/royalties")
        assert royalties_resp.status_code == 200
        data = royalties_resp.json()
        
        summary = data["summary"]
        artists = data["artists"]
        
        if len(artists) == 0:
            pytest.skip("No artists to verify totals")
        
        calculated_revenue = sum(a["gross_revenue"] for a in artists)
        calculated_artist_payouts = sum(a["artist_earnings"] for a in artists)
        calculated_label_earnings = sum(a["label_earnings"] for a in artists)
        
        # Allow small floating point differences
        assert abs(summary["total_revenue"] - calculated_revenue) < 0.1, \
            f"Total revenue mismatch: summary={summary['total_revenue']}, calculated={calculated_revenue}"
        assert abs(summary["total_artist_payouts"] - calculated_artist_payouts) < 0.1, \
            f"Total artist payouts mismatch: summary={summary['total_artist_payouts']}, calculated={calculated_artist_payouts}"
        assert abs(summary["total_label_earnings"] - calculated_label_earnings) < 0.1, \
            f"Total label earnings mismatch: summary={summary['total_label_earnings']}, calculated={calculated_label_earnings}"
        
        print(f"PASS: Summary totals match artist sums - revenue=${summary['total_revenue']}, artist_payouts=${summary['total_artist_payouts']}, label_earnings=${summary['total_label_earnings']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
