"""
Iteration 60 - Admin Payout Dashboard Tests
Tests for batch-processing and exporting payout reports, tracking payment history with status management.

Endpoints tested:
- GET /api/admin/payouts - List all withdrawals with user details
- GET /api/admin/payouts?status=pending - Filter by status
- GET /api/admin/payouts/summary - Counts and amounts for each status
- PUT /api/admin/payouts/{id} - Update payout status
- POST /api/admin/payouts/batch - Batch update multiple payouts
- GET /api/admin/payouts/export - Export CSV file
- All endpoints return 403 for non-admin users
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "submitkalmori@gmail.com"
ADMIN_PASSWORD = "MAYAsimpSON37!!"


class TestAdminPayoutDashboard:
    """Admin Payout Dashboard endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with admin login"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        login_data = login_response.json()
        self.admin_token = login_data.get("access_token")
        self.admin_user = login_data.get("user")
        
        # Set auth header
        if self.admin_token:
            self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
        
        yield
        
        # Cleanup
        self.session.close()
    
    def test_01_admin_login_success(self):
        """Test admin login with submitkalmori@gmail.com / MAYAsimpSON37!!"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL.lower()
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful: {data['user']['email']}")
    
    def test_02_get_all_payouts(self):
        """Test GET /api/admin/payouts returns all withdrawals with user_name, user_email"""
        response = self.session.get(f"{BASE_URL}/api/admin/payouts")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "withdrawals" in data
        withdrawals = data["withdrawals"]
        assert isinstance(withdrawals, list)
        print(f"✓ GET /api/admin/payouts returned {len(withdrawals)} withdrawals")
        
        # Verify structure if there are withdrawals
        if withdrawals:
            w = withdrawals[0]
            assert "id" in w
            assert "user_name" in w
            assert "user_email" in w
            assert "amount" in w
            assert "status" in w
            print(f"  First withdrawal: {w['id']} - {w['user_name']} - ${w['amount']} - {w['status']}")
    
    def test_03_get_pending_payouts(self):
        """Test GET /api/admin/payouts?status=pending returns only pending withdrawals"""
        response = self.session.get(f"{BASE_URL}/api/admin/payouts?status=pending")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        withdrawals = data.get("withdrawals", [])
        
        # All returned should be pending
        for w in withdrawals:
            assert w.get("status") == "pending", f"Expected pending, got {w.get('status')}"
        
        print(f"✓ GET /api/admin/payouts?status=pending returned {len(withdrawals)} pending payouts")
    
    def test_04_get_payouts_summary(self):
        """Test GET /api/admin/payouts/summary returns counts and amounts for each status"""
        response = self.session.get(f"{BASE_URL}/api/admin/payouts/summary")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify all required fields
        assert "pending_count" in data
        assert "pending_amount" in data
        assert "processing_count" in data
        assert "processing_amount" in data
        assert "completed_count" in data
        assert "completed_amount" in data
        assert "failed_count" in data
        assert "total_user_balances" in data
        
        print(f"✓ GET /api/admin/payouts/summary:")
        print(f"  Pending: {data['pending_count']} (${data['pending_amount']})")
        print(f"  Processing: {data['processing_count']} (${data['processing_amount']})")
        print(f"  Completed: {data['completed_count']} (${data['completed_amount']})")
        print(f"  Failed: {data['failed_count']}")
        print(f"  Total User Balances: ${data['total_user_balances']}")
    
    def test_05_update_payout_to_processing(self):
        """Test PUT /api/admin/payouts/{id} updates payout status to 'processing'"""
        # First get a pending payout
        response = self.session.get(f"{BASE_URL}/api/admin/payouts?status=pending")
        assert response.status_code == 200
        withdrawals = response.json().get("withdrawals", [])
        
        if not withdrawals:
            pytest.skip("No pending payouts to test status update")
        
        payout_id = withdrawals[0]["id"]
        
        # Update to processing
        update_response = self.session.put(f"{BASE_URL}/api/admin/payouts/{payout_id}", json={
            "status": "processing"
        })
        assert update_response.status_code == 200, f"Failed: {update_response.text}"
        data = update_response.json()
        assert "message" in data
        assert "processing" in data["message"].lower()
        print(f"✓ PUT /api/admin/payouts/{payout_id} updated to processing")
        
        # Verify the update
        verify_response = self.session.get(f"{BASE_URL}/api/admin/payouts?status=processing")
        assert verify_response.status_code == 200
        processing_payouts = verify_response.json().get("withdrawals", [])
        payout_ids = [p["id"] for p in processing_payouts]
        assert payout_id in payout_ids, "Payout not found in processing list"
        print(f"  Verified: payout {payout_id} is now in processing status")
    
    def test_06_update_payout_to_completed(self):
        """Test PUT /api/admin/payouts/{id} updates payout status to 'completed' and sets paid_at"""
        # Get a processing payout
        response = self.session.get(f"{BASE_URL}/api/admin/payouts?status=processing")
        assert response.status_code == 200
        withdrawals = response.json().get("withdrawals", [])
        
        if not withdrawals:
            pytest.skip("No processing payouts to test completion")
        
        payout_id = withdrawals[0]["id"]
        
        # Update to completed
        update_response = self.session.put(f"{BASE_URL}/api/admin/payouts/{payout_id}", json={
            "status": "completed",
            "transaction_ref": "TEST_TXN_123"
        })
        assert update_response.status_code == 200, f"Failed: {update_response.text}"
        data = update_response.json()
        assert "completed" in data["message"].lower()
        print(f"✓ PUT /api/admin/payouts/{payout_id} updated to completed")
        
        # Verify paid_at is set
        verify_response = self.session.get(f"{BASE_URL}/api/admin/payouts?status=completed")
        assert verify_response.status_code == 200
        completed_payouts = verify_response.json().get("withdrawals", [])
        completed_payout = next((p for p in completed_payouts if p["id"] == payout_id), None)
        assert completed_payout is not None, "Completed payout not found"
        assert completed_payout.get("paid_at") is not None, "paid_at should be set"
        print(f"  Verified: payout {payout_id} has paid_at: {completed_payout.get('paid_at')}")
    
    def test_07_update_nonexistent_payout_returns_404(self):
        """Test PUT /api/admin/payouts/{id} returns 404 for non-existent ID"""
        fake_id = f"wd_nonexistent_{uuid.uuid4().hex[:8]}"
        response = self.session.put(f"{BASE_URL}/api/admin/payouts/{fake_id}", json={
            "status": "processing"
        })
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ PUT /api/admin/payouts/{fake_id} correctly returned 404")
    
    def test_08_batch_update_payouts(self):
        """Test POST /api/admin/payouts/batch batch-updates multiple payouts"""
        # Get pending payouts
        response = self.session.get(f"{BASE_URL}/api/admin/payouts?status=pending")
        assert response.status_code == 200
        withdrawals = response.json().get("withdrawals", [])
        
        if len(withdrawals) < 1:
            pytest.skip("Not enough pending payouts for batch test")
        
        # Take up to 2 payouts for batch update
        payout_ids = [w["id"] for w in withdrawals[:2]]
        
        # Batch update to processing
        batch_response = self.session.post(f"{BASE_URL}/api/admin/payouts/batch", json={
            "withdrawal_ids": payout_ids,
            "status": "processing"
        })
        assert batch_response.status_code == 200, f"Failed: {batch_response.text}"
        data = batch_response.json()
        assert "updated" in data
        assert data["updated"] >= 1
        print(f"✓ POST /api/admin/payouts/batch updated {data['updated']} payouts to processing")
    
    def test_09_export_csv(self):
        """Test GET /api/admin/payouts/export returns CSV file (Content-Type: text/csv)"""
        response = self.session.get(f"{BASE_URL}/api/admin/payouts/export?status=all")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "text/csv" in content_type, f"Expected text/csv, got {content_type}"
        
        # Check content disposition
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp
        assert ".csv" in content_disp
        
        # Verify CSV content
        csv_content = response.text
        assert "ID" in csv_content
        assert "User" in csv_content
        assert "Email" in csv_content
        assert "Amount" in csv_content
        assert "Status" in csv_content
        
        print(f"✓ GET /api/admin/payouts/export returned CSV file")
        print(f"  Content-Type: {content_type}")
        print(f"  Content-Disposition: {content_disp}")
        print(f"  CSV preview (first 200 chars): {csv_content[:200]}...")


class TestNonAdminAccess:
    """Test that non-admin users get 403 on all admin payout endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with non-admin user"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Create a test non-admin user
        test_email = f"test_nonadmin_{uuid.uuid4().hex[:8]}@test.com"
        test_password = "TestPass123!"
        
        # Register
        register_response = self.session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": test_password,
            "name": "Test Non-Admin",
            "artist_name": "Test Artist"
        })
        
        if register_response.status_code == 200:
            data = register_response.json()
            self.token = data.get("access_token")
            if self.token:
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            # Try login if already exists
            login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
                "email": test_email,
                "password": test_password
            })
            if login_response.status_code == 200:
                data = login_response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        yield
        self.session.close()
    
    def test_10_nonadmin_get_payouts_returns_403(self):
        """Test GET /api/admin/payouts returns 403 for non-admin users"""
        response = self.session.get(f"{BASE_URL}/api/admin/payouts")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ GET /api/admin/payouts returns 403 for non-admin")
    
    def test_11_nonadmin_get_summary_returns_403(self):
        """Test GET /api/admin/payouts/summary returns 403 for non-admin users"""
        response = self.session.get(f"{BASE_URL}/api/admin/payouts/summary")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ GET /api/admin/payouts/summary returns 403 for non-admin")
    
    def test_12_nonadmin_update_payout_returns_403(self):
        """Test PUT /api/admin/payouts/{id} returns 403 for non-admin users"""
        response = self.session.put(f"{BASE_URL}/api/admin/payouts/wd_test123", json={
            "status": "processing"
        })
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ PUT /api/admin/payouts/{id} returns 403 for non-admin")
    
    def test_13_nonadmin_batch_returns_403(self):
        """Test POST /api/admin/payouts/batch returns 403 for non-admin users"""
        response = self.session.post(f"{BASE_URL}/api/admin/payouts/batch", json={
            "withdrawal_ids": ["wd_test123"],
            "status": "processing"
        })
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ POST /api/admin/payouts/batch returns 403 for non-admin")
    
    def test_14_nonadmin_export_returns_403(self):
        """Test GET /api/admin/payouts/export returns 403 for non-admin users"""
        response = self.session.get(f"{BASE_URL}/api/admin/payouts/export")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ GET /api/admin/payouts/export returns 403 for non-admin")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
