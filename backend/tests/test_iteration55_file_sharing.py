"""
Iteration 55 - File/Audio Sharing in In-App Messaging
Tests for:
- POST /api/messages/{convo_id}/upload - upload files to chat
- GET /api/messages/file/{path} - download chat files
- GET /api/messages/{convo_id} - messages with file attachments
- Privacy: non-participants cannot access files or upload
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestFileSharing:
    """File/Audio sharing in messaging tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session and login"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "submitkalmori@gmail.com",
            "password": "MAYAsimpSON37!!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        data = login_resp.json()
        self.token = data.get("access_token")
        self.user = data.get("user")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        print(f"Logged in as: {self.user.get('email')}")
        
    def test_01_login_works(self):
        """Test login with submitkalmori@gmail.com"""
        # Already logged in via fixture
        assert self.token is not None
        assert self.user.get("email") == "submitkalmori@gmail.com"
        print("PASS: Login with submitkalmori@gmail.com works")
        
    def test_02_get_conversations(self):
        """Get conversations list"""
        resp = self.session.get(f"{BASE_URL}/api/messages/conversations")
        assert resp.status_code == 200, f"Failed to get conversations: {resp.text}"
        convos = resp.json()
        assert isinstance(convos, list), "Conversations should be a list"
        print(f"PASS: Got {len(convos)} conversations")
        # Store first conversation for later tests
        if convos:
            self.__class__.test_convo_id = convos[0]["id"]
            print(f"Using conversation: {self.__class__.test_convo_id}")
        else:
            pytest.skip("No conversations available for testing")
            
    def test_03_upload_text_file(self):
        """Upload a text file to chat"""
        if not hasattr(self.__class__, 'test_convo_id'):
            pytest.skip("No conversation available")
        convo_id = self.__class__.test_convo_id
        
        # Create a test file
        file_content = b"This is a test stem file for collaboration.\nVersion 2.0"
        files = {'file': ('test_stem_v2.txt', file_content, 'text/plain')}
        
        # Remove Content-Type header for multipart upload
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = requests.post(
            f"{BASE_URL}/api/messages/{convo_id}/upload",
            files=files,
            headers=headers
        )
        assert resp.status_code == 200, f"Upload failed: {resp.text}"
        data = resp.json()
        
        # Verify response includes required fields
        assert "file_url" in data, "Response should include file_url"
        assert "file_name" in data, "Response should include file_name"
        assert "file_type" in data, "Response should include file_type"
        assert "file_size" in data, "Response should include file_size"
        
        assert data["file_name"] == "test_stem_v2.txt"
        assert data["file_type"] == "file"  # text files are 'file' type
        assert data["file_size"] == len(file_content)
        
        self.__class__.uploaded_file_url = data["file_url"]
        self.__class__.uploaded_msg_id = data["id"]
        print(f"PASS: Uploaded text file - file_url: {data['file_url']}, file_type: {data['file_type']}, file_size: {data['file_size']}")
        
    def test_04_upload_audio_file(self):
        """Upload an audio file - should have file_type='audio'"""
        if not hasattr(self.__class__, 'test_convo_id'):
            pytest.skip("No conversation available")
        convo_id = self.__class__.test_convo_id
        
        # Create a fake audio file (just bytes with audio mime type)
        audio_content = b"RIFF" + b"\x00" * 100  # Minimal WAV-like header
        files = {'file': ('beat_draft.wav', audio_content, 'audio/wav')}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = requests.post(
            f"{BASE_URL}/api/messages/{convo_id}/upload",
            files=files,
            headers=headers
        )
        assert resp.status_code == 200, f"Audio upload failed: {resp.text}"
        data = resp.json()
        
        assert data["file_type"] == "audio", f"Audio file should have file_type='audio', got: {data['file_type']}"
        assert data["file_name"] == "beat_draft.wav"
        print(f"PASS: Audio file uploaded with file_type='audio'")
        
    def test_05_upload_image_file(self):
        """Upload an image file - should have file_type='image'"""
        if not hasattr(self.__class__, 'test_convo_id'):
            pytest.skip("No conversation available")
        convo_id = self.__class__.test_convo_id
        
        # Create a minimal PNG-like file
        image_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
        files = {'file': ('cover_art.png', image_content, 'image/png')}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = requests.post(
            f"{BASE_URL}/api/messages/{convo_id}/upload",
            files=files,
            headers=headers
        )
        assert resp.status_code == 200, f"Image upload failed: {resp.text}"
        data = resp.json()
        
        assert data["file_type"] == "image", f"Image file should have file_type='image', got: {data['file_type']}"
        assert data["file_name"] == "cover_art.png"
        print(f"PASS: Image file uploaded with file_type='image'")
        
    def test_06_download_uploaded_file(self):
        """Download a previously uploaded file"""
        if not hasattr(self.__class__, 'uploaded_file_url'):
            pytest.skip("No file uploaded to download")
        
        file_path = self.__class__.uploaded_file_url
        resp = self.session.get(f"{BASE_URL}/api/messages/file/{file_path}")
        assert resp.status_code == 200, f"Download failed: {resp.text}"
        print(f"PASS: Downloaded file successfully, content length: {len(resp.content)}")
        
    def test_07_messages_include_file_fields(self):
        """GET /api/messages/{convo_id} - messages with file attachments include file fields"""
        if not hasattr(self.__class__, 'test_convo_id'):
            pytest.skip("No conversation available")
        convo_id = self.__class__.test_convo_id
        
        resp = self.session.get(f"{BASE_URL}/api/messages/{convo_id}")
        assert resp.status_code == 200, f"Failed to get messages: {resp.text}"
        messages = resp.json()
        
        # Find messages with file attachments
        file_messages = [m for m in messages if m.get("file_url")]
        assert len(file_messages) > 0, "Should have at least one file message"
        
        for msg in file_messages:
            assert "file_url" in msg, "File message should have file_url"
            assert "file_name" in msg, "File message should have file_name"
            assert "file_type" in msg, "File message should have file_type"
            assert "file_size" in msg, "File message should have file_size"
            print(f"  File message: {msg['file_name']} ({msg['file_type']}, {msg['file_size']} bytes)")
        
        print(f"PASS: Found {len(file_messages)} file messages with all required fields")
        
    def test_08_upload_returns_404_for_non_participant(self):
        """Upload returns 404 for non-participant"""
        # Create a new user who is not part of any conversation
        unique_email = f"test_nonparticipant_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "name": "Non Participant",
            "artist_name": "Non Participant"
        })
        assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
        new_token = reg_resp.json().get("access_token")
        
        # Try to upload to admin's conversation
        if not hasattr(self.__class__, 'test_convo_id'):
            pytest.skip("No conversation available")
        convo_id = self.__class__.test_convo_id
        
        file_content = b"Unauthorized file"
        files = {'file': ('unauthorized.txt', file_content, 'text/plain')}
        headers = {"Authorization": f"Bearer {new_token}"}
        
        resp = requests.post(
            f"{BASE_URL}/api/messages/{convo_id}/upload",
            files=files,
            headers=headers
        )
        assert resp.status_code == 404, f"Expected 404 for non-participant, got: {resp.status_code}"
        print("PASS: Upload returns 404 for non-participant")
        
    def test_09_download_returns_403_for_non_participant(self):
        """Download returns 403 for non-participant"""
        if not hasattr(self.__class__, 'uploaded_file_url'):
            pytest.skip("No file uploaded to test")
        
        # Create another new user
        unique_email = f"test_nonparticipant2_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "name": "Non Participant 2",
            "artist_name": "Non Participant 2"
        })
        assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
        new_token = reg_resp.json().get("access_token")
        
        file_path = self.__class__.uploaded_file_url
        headers = {"Authorization": f"Bearer {new_token}"}
        resp = requests.get(f"{BASE_URL}/api/messages/file/{file_path}", headers=headers)
        assert resp.status_code == 403, f"Expected 403 for non-participant download, got: {resp.status_code}"
        print("PASS: Download returns 403 for non-participant")
        
    def test_10_messages_privacy(self):
        """User cannot access other users' conversations"""
        # Create a new user
        unique_email = f"test_privacy_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPass123!",
            "name": "Privacy Test",
            "artist_name": "Privacy Test"
        })
        assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
        new_token = reg_resp.json().get("access_token")
        
        if not hasattr(self.__class__, 'test_convo_id'):
            pytest.skip("No conversation available")
        convo_id = self.__class__.test_convo_id
        
        # Try to access admin's conversation messages
        headers = {"Authorization": f"Bearer {new_token}"}
        resp = requests.get(f"{BASE_URL}/api/messages/{convo_id}", headers=headers)
        assert resp.status_code == 404, f"Expected 404 for non-participant accessing messages, got: {resp.status_code}"
        print("PASS: User cannot access other users' conversations (404)")
        
    def test_11_text_messages_still_work(self):
        """Text messages still work (type + send)"""
        if not hasattr(self.__class__, 'test_convo_id'):
            pytest.skip("No conversation available")
        convo_id = self.__class__.test_convo_id
        
        test_text = f"Test message from iteration 55 - {uuid.uuid4().hex[:8]}"
        resp = self.session.post(
            f"{BASE_URL}/api/messages/{convo_id}",
            json={"text": test_text}
        )
        assert resp.status_code == 200, f"Failed to send text message: {resp.text}"
        data = resp.json()
        assert data.get("text") == test_text
        assert data.get("file_url") is None or data.get("file_url") == ""
        print(f"PASS: Text message sent successfully: {test_text[:30]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
