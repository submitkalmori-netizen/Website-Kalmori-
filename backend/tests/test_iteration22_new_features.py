"""
Iteration 22 - Test new features:
1. Beat Catalog Search/Filter with genre, BPM range, key, mood, price range, sort options
2. Social Sharing Deep Links for beats/releases/artists with OG meta data
3. Pre-Save Campaign system with public landing pages, countdown timer, email collection, platform links
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://artist-hub-219.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"

# Existing test campaign ID from main agent
EXISTING_CAMPAIGN_ID = "presave_90e40c235523"


@pytest.fixture(scope="module")
def auth_token():
    """Get admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")


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


class TestBeatSearchFilter:
    """Test beat catalog search and filter functionality"""

    def test_list_beats_basic(self):
        """GET /api/beats - returns beats list"""
        response = requests.get(f"{BASE_URL}/api/beats")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        assert "total" in data
        assert isinstance(data["beats"], list)
        print(f"✓ GET /api/beats returns {data['total']} beats")

    def test_search_by_text(self):
        """GET /api/beats?search=<text> - filters by title/genre/mood/tags"""
        response = requests.get(f"{BASE_URL}/api/beats?search=trap")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        print(f"✓ Search 'trap' returns {data['total']} beats")

    def test_filter_by_genre(self):
        """GET /api/beats?genre=<genre> - filters by genre"""
        response = requests.get(f"{BASE_URL}/api/beats?genre=Hip-Hop")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        print(f"✓ Filter by genre 'Hip-Hop' returns {data['total']} beats")

    def test_filter_by_mood(self):
        """GET /api/beats?mood=<mood> - filters by mood"""
        response = requests.get(f"{BASE_URL}/api/beats?mood=Energetic")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        print(f"✓ Filter by mood 'Energetic' returns {data['total']} beats")

    def test_filter_by_key(self):
        """GET /api/beats?key=<key> - filters by musical key"""
        response = requests.get(f"{BASE_URL}/api/beats?key=Cm")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        print(f"✓ Filter by key 'Cm' returns {data['total']} beats")

    def test_filter_by_bpm_range(self):
        """GET /api/beats?bpm_min=<min>&bpm_max=<max> - filters BPM range"""
        response = requests.get(f"{BASE_URL}/api/beats?bpm_min=100&bpm_max=140")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        # Verify BPM range if beats exist
        for beat in data["beats"]:
            if "bpm" in beat:
                assert 100 <= beat["bpm"] <= 140, f"Beat BPM {beat['bpm']} outside range 100-140"
        print(f"✓ Filter by BPM range 100-140 returns {data['total']} beats")

    def test_sort_by_newest(self):
        """GET /api/beats?sort_by=newest - sorts by newest first"""
        response = requests.get(f"{BASE_URL}/api/beats?sort_by=newest")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        print(f"✓ Sort by newest returns {data['total']} beats")

    def test_sort_by_price_low(self):
        """GET /api/beats?sort_by=price_low - sorts by price low to high"""
        response = requests.get(f"{BASE_URL}/api/beats?sort_by=price_low")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        print(f"✓ Sort by price_low returns {data['total']} beats")

    def test_sort_by_price_high(self):
        """GET /api/beats?sort_by=price_high - sorts by price high to low"""
        response = requests.get(f"{BASE_URL}/api/beats?sort_by=price_high")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        print(f"✓ Sort by price_high returns {data['total']} beats")

    def test_sort_by_bpm_low(self):
        """GET /api/beats?sort_by=bpm_low - sorts by BPM low to high"""
        response = requests.get(f"{BASE_URL}/api/beats?sort_by=bpm_low")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        print(f"✓ Sort by bpm_low returns {data['total']} beats")

    def test_sort_by_bpm_high(self):
        """GET /api/beats?sort_by=bpm_high - sorts by BPM high to low"""
        response = requests.get(f"{BASE_URL}/api/beats?sort_by=bpm_high")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        print(f"✓ Sort by bpm_high returns {data['total']} beats")

    def test_combined_filters(self):
        """GET /api/beats with multiple filters"""
        response = requests.get(f"{BASE_URL}/api/beats?genre=Hip-Hop&bpm_min=80&bpm_max=160&sort_by=newest")
        assert response.status_code == 200
        data = response.json()
        assert "beats" in data
        print(f"✓ Combined filters return {data['total']} beats")


class TestSocialSharing:
    """Test social sharing endpoints for beats, releases, and artists"""

    def test_share_beat_endpoint(self, auth_session):
        """GET /api/share/beat/{beat_id} - returns OG meta data for beat"""
        # First get a beat ID
        beats_response = requests.get(f"{BASE_URL}/api/beats")
        if beats_response.status_code == 200 and beats_response.json().get("beats"):
            beat_id = beats_response.json()["beats"][0]["id"]
            response = requests.get(f"{BASE_URL}/api/share/beat/{beat_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["type"] == "beat"
            assert "og_title" in data
            assert "og_description" in data
            assert "title" in data
            print(f"✓ GET /api/share/beat/{beat_id} returns OG meta data")
        else:
            pytest.skip("No beats available to test share endpoint")

    def test_share_beat_not_found(self):
        """GET /api/share/beat/{invalid_id} - returns 404"""
        response = requests.get(f"{BASE_URL}/api/share/beat/nonexistent_beat_id")
        assert response.status_code == 404
        print("✓ GET /api/share/beat/invalid returns 404")

    def test_share_release_endpoint(self, auth_session):
        """GET /api/share/release/{release_id} - returns OG meta data for release"""
        # First get a release ID
        releases_response = auth_session.get(f"{BASE_URL}/api/releases")
        if releases_response.status_code == 200:
            releases = releases_response.json()
            if isinstance(releases, list) and len(releases) > 0:
                release_id = releases[0]["id"]
                response = requests.get(f"{BASE_URL}/api/share/release/{release_id}")
                assert response.status_code == 200
                data = response.json()
                assert data["type"] == "release"
                assert "og_title" in data
                assert "og_description" in data
                print(f"✓ GET /api/share/release/{release_id} returns OG meta data")
            else:
                pytest.skip("No releases available to test share endpoint")
        else:
            pytest.skip("Could not fetch releases")

    def test_share_release_not_found(self):
        """GET /api/share/release/{invalid_id} - returns 404"""
        response = requests.get(f"{BASE_URL}/api/share/release/nonexistent_release_id")
        assert response.status_code == 404
        print("✓ GET /api/share/release/invalid returns 404")

    def test_share_artist_endpoint(self, auth_session):
        """GET /api/share/artist/{user_id} - returns OG meta data for artist"""
        # Get current user ID
        me_response = auth_session.get(f"{BASE_URL}/api/auth/me")
        if me_response.status_code == 200:
            user_id = me_response.json()["id"]
            response = requests.get(f"{BASE_URL}/api/share/artist/{user_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["type"] == "artist"
            assert "og_title" in data
            assert "og_description" in data
            assert "artist_name" in data
            print(f"✓ GET /api/share/artist/{user_id} returns OG meta data")
        else:
            pytest.skip("Could not get current user")

    def test_share_artist_not_found(self):
        """GET /api/share/artist/{invalid_id} - returns 404"""
        response = requests.get(f"{BASE_URL}/api/share/artist/nonexistent_user_id")
        assert response.status_code == 404
        print("✓ GET /api/share/artist/invalid returns 404")


class TestPreSaveCampaigns:
    """Test pre-save campaign CRUD and public endpoints"""

    def test_get_existing_campaign_public(self):
        """GET /api/presave/{campaign_id} - public endpoint for landing page"""
        response = requests.get(f"{BASE_URL}/api/presave/{EXISTING_CAMPAIGN_ID}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "title" in data
        assert "release_date" in data
        # Should not include subscribers list (privacy)
        assert "subscribers" not in data
        print(f"✓ GET /api/presave/{EXISTING_CAMPAIGN_ID} returns campaign data (public)")

    def test_get_campaign_not_found(self):
        """GET /api/presave/{invalid_id} - returns 404"""
        response = requests.get(f"{BASE_URL}/api/presave/nonexistent_campaign")
        assert response.status_code == 404
        print("✓ GET /api/presave/invalid returns 404")

    def test_list_my_campaigns(self, auth_session):
        """GET /api/presave/campaigns - lists user's pre-save campaigns"""
        response = auth_session.get(f"{BASE_URL}/api/presave/campaigns")
        assert response.status_code == 200
        data = response.json()
        assert "campaigns" in data
        assert isinstance(data["campaigns"], list)
        print(f"✓ GET /api/presave/campaigns returns {len(data['campaigns'])} campaigns")

    def test_create_presave_campaign(self, auth_session):
        """POST /api/presave/campaigns - creates pre-save campaign"""
        # First get a release to link
        releases_response = auth_session.get(f"{BASE_URL}/api/releases")
        if releases_response.status_code != 200:
            pytest.skip("Could not fetch releases")
        
        releases = releases_response.json()
        if not isinstance(releases, list) or len(releases) == 0:
            pytest.skip("No releases available to create campaign")
        
        release_id = releases[0]["id"]
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        campaign_data = {
            "release_id": release_id,
            "title": "TEST_Pre-Save Campaign",
            "description": "Test campaign for iteration 22",
            "release_date": future_date,
            "spotify_url": "https://open.spotify.com/test",
            "apple_music_url": "https://music.apple.com/test",
            "youtube_url": "https://youtube.com/test"
        }
        
        response = auth_session.post(f"{BASE_URL}/api/presave/campaigns", json=campaign_data)
        assert response.status_code == 200
        data = response.json()
        assert "campaign" in data
        assert data["campaign"]["title"] == "TEST_Pre-Save Campaign"
        assert data["campaign"]["spotify_url"] == "https://open.spotify.com/test"
        
        # Store campaign ID for cleanup
        TestPreSaveCampaigns.created_campaign_id = data["campaign"]["id"]
        print(f"✓ POST /api/presave/campaigns creates campaign: {data['campaign']['id']}")

    def test_subscribe_to_campaign(self):
        """POST /api/presave/{campaign_id}/subscribe - subscribes with email"""
        test_email = f"test_{datetime.now().timestamp()}@example.com"
        response = requests.post(
            f"{BASE_URL}/api/presave/{EXISTING_CAMPAIGN_ID}/subscribe",
            json={"email": test_email, "name": "Test Subscriber"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ POST /api/presave/{EXISTING_CAMPAIGN_ID}/subscribe works with email")

    def test_subscribe_duplicate_email(self):
        """POST /api/presave/{campaign_id}/subscribe - rejects duplicate email"""
        # First subscribe
        test_email = f"duplicate_{datetime.now().timestamp()}@example.com"
        requests.post(
            f"{BASE_URL}/api/presave/{EXISTING_CAMPAIGN_ID}/subscribe",
            json={"email": test_email}
        )
        # Try to subscribe again
        response = requests.post(
            f"{BASE_URL}/api/presave/{EXISTING_CAMPAIGN_ID}/subscribe",
            json={"email": test_email}
        )
        assert response.status_code == 400
        print("✓ Duplicate email subscription returns 400")

    def test_subscribe_missing_email(self):
        """POST /api/presave/{campaign_id}/subscribe - requires email"""
        response = requests.post(
            f"{BASE_URL}/api/presave/{EXISTING_CAMPAIGN_ID}/subscribe",
            json={"name": "No Email"}
        )
        assert response.status_code == 400
        print("✓ Subscribe without email returns 400")

    def test_delete_campaign(self, auth_session):
        """DELETE /api/presave/campaigns/{campaign_id} - deletes campaign"""
        if hasattr(TestPreSaveCampaigns, 'created_campaign_id'):
            campaign_id = TestPreSaveCampaigns.created_campaign_id
            response = auth_session.delete(f"{BASE_URL}/api/presave/campaigns/{campaign_id}")
            assert response.status_code == 200
            print(f"✓ DELETE /api/presave/campaigns/{campaign_id} deletes campaign")
        else:
            pytest.skip("No test campaign to delete")

    def test_create_campaign_invalid_release(self, auth_session):
        """POST /api/presave/campaigns - returns 404 for invalid release"""
        campaign_data = {
            "release_id": "nonexistent_release",
            "title": "Invalid Campaign",
            "release_date": "2026-12-31"
        }
        response = auth_session.post(f"{BASE_URL}/api/presave/campaigns", json=campaign_data)
        assert response.status_code == 404
        print("✓ Create campaign with invalid release returns 404")


class TestPreSaveCampaignRequiresAuth:
    """Test that campaign management requires authentication"""

    def test_list_campaigns_requires_auth(self):
        """GET /api/presave/campaigns requires auth"""
        response = requests.get(f"{BASE_URL}/api/presave/campaigns")
        assert response.status_code in [401, 422]
        print("✓ GET /api/presave/campaigns requires auth")

    def test_create_campaign_requires_auth(self):
        """POST /api/presave/campaigns requires auth"""
        response = requests.post(f"{BASE_URL}/api/presave/campaigns", json={
            "release_id": "test",
            "title": "Test",
            "release_date": "2026-12-31"
        })
        assert response.status_code in [401, 422]
        print("✓ POST /api/presave/campaigns requires auth")

    def test_delete_campaign_requires_auth(self):
        """DELETE /api/presave/campaigns/{id} requires auth"""
        response = requests.delete(f"{BASE_URL}/api/presave/campaigns/test_id")
        assert response.status_code in [401, 422]
        print("✓ DELETE /api/presave/campaigns requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
