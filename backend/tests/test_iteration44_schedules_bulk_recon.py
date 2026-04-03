"""
Iteration 44 - Automated Distributor Report Scheduler & Bulk Reconciliation Tests
Tests:
1. Schedule CRUD (POST, GET, PUT toggle, DELETE)
2. Check Due Schedules (POST /api/admin/schedules/check-due)
3. Bulk Resolve Duplicates (POST /api/admin/royalties/reconciliation/resolve-duplicates)
4. Bulk Assign Unmatched (POST /api/admin/royalties/reconciliation/bulk-assign)
5. Revenue Analytics regression test
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "admin@tunedrop.com"
ADMIN_PASSWORD = "Admin123!"


class TestSchedulerAndBulkReconciliation:
    """Test Schedule CRUD and Bulk Reconciliation features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin and get auth cookie"""
        self.session = requests.Session()
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert login_res.status_code == 200, f"Admin login failed: {login_res.text}"
        self.admin_user = login_res.json().get("user", {})
        print(f"Logged in as admin: {self.admin_user.get('email')}")
        yield
        # Cleanup - no explicit logout needed
    
    # ============= SCHEDULE CRUD TESTS =============
    
    def test_01_get_schedules_list(self):
        """GET /api/admin/schedules returns list of schedules"""
        res = self.session.get(f"{BASE_URL}/api/admin/schedules")
        assert res.status_code == 200, f"Failed to get schedules: {res.text}"
        data = res.json()
        assert "schedules" in data, "Response should have 'schedules' key"
        assert isinstance(data["schedules"], list), "Schedules should be a list"
        print(f"Found {len(data['schedules'])} existing schedules")
        # Check if any schedule has overdue flag
        for sched in data["schedules"]:
            assert "overdue" in sched, "Each schedule should have 'overdue' flag"
            print(f"  - {sched.get('name')}: status={sched.get('status')}, overdue={sched.get('overdue')}")
    
    def test_02_create_schedule_weekly(self):
        """POST /api/admin/schedules creates a new weekly schedule"""
        unique_name = f"Test Weekly Schedule {uuid.uuid4().hex[:6]}"
        res = self.session.post(f"{BASE_URL}/api/admin/schedules", json={
            "name": unique_name,
            "frequency": "weekly",
            "template_id": "",
            "artist_id": "",
            "notes": "Test schedule for iteration 44"
        })
        assert res.status_code == 200, f"Failed to create schedule: {res.text}"
        data = res.json()
        assert data.get("name") == unique_name, "Schedule name should match"
        assert data.get("frequency") == "weekly", "Frequency should be weekly"
        assert data.get("status") == "active", "New schedule should be active"
        assert "id" in data, "Schedule should have an ID"
        assert "next_due" in data, "Schedule should have next_due date"
        print(f"Created schedule: {data.get('id')} - {data.get('name')}")
        # Store for later tests
        self.__class__.created_schedule_id = data.get("id")
    
    def test_03_create_schedule_monthly(self):
        """POST /api/admin/schedules creates a new monthly schedule"""
        unique_name = f"Test Monthly Schedule {uuid.uuid4().hex[:6]}"
        res = self.session.post(f"{BASE_URL}/api/admin/schedules", json={
            "name": unique_name,
            "frequency": "monthly",
            "template_id": "",
            "artist_id": "",
            "notes": "Monthly test schedule"
        })
        assert res.status_code == 200, f"Failed to create monthly schedule: {res.text}"
        data = res.json()
        assert data.get("frequency") == "monthly", "Frequency should be monthly"
        print(f"Created monthly schedule: {data.get('id')}")
        self.__class__.monthly_schedule_id = data.get("id")
    
    def test_04_create_schedule_invalid_frequency(self):
        """POST /api/admin/schedules rejects invalid frequency"""
        res = self.session.post(f"{BASE_URL}/api/admin/schedules", json={
            "name": "Invalid Schedule",
            "frequency": "daily",  # Invalid - only weekly/monthly allowed
            "template_id": "",
            "artist_id": "",
            "notes": ""
        })
        assert res.status_code == 400, f"Should reject invalid frequency: {res.text}"
        assert "weekly" in res.text.lower() or "monthly" in res.text.lower(), "Error should mention valid frequencies"
        print("Correctly rejected invalid frequency")
    
    def test_05_toggle_schedule_pause(self):
        """PUT /api/admin/schedules/{id}/toggle pauses an active schedule"""
        schedule_id = getattr(self.__class__, 'created_schedule_id', None)
        if not schedule_id:
            pytest.skip("No schedule created to toggle")
        
        res = self.session.put(f"{BASE_URL}/api/admin/schedules/{schedule_id}/toggle")
        assert res.status_code == 200, f"Failed to toggle schedule: {res.text}"
        data = res.json()
        assert data.get("status") == "paused", "Schedule should be paused after toggle"
        print(f"Toggled schedule to paused")
    
    def test_06_toggle_schedule_resume(self):
        """PUT /api/admin/schedules/{id}/toggle resumes a paused schedule"""
        schedule_id = getattr(self.__class__, 'created_schedule_id', None)
        if not schedule_id:
            pytest.skip("No schedule created to toggle")
        
        res = self.session.put(f"{BASE_URL}/api/admin/schedules/{schedule_id}/toggle")
        assert res.status_code == 200, f"Failed to toggle schedule: {res.text}"
        data = res.json()
        assert data.get("status") == "active", "Schedule should be active after second toggle"
        print(f"Toggled schedule back to active")
    
    def test_07_toggle_nonexistent_schedule(self):
        """PUT /api/admin/schedules/{id}/toggle returns 404 for nonexistent schedule"""
        res = self.session.put(f"{BASE_URL}/api/admin/schedules/nonexistent_id_12345/toggle")
        assert res.status_code == 404, f"Should return 404 for nonexistent schedule: {res.text}"
        print("Correctly returned 404 for nonexistent schedule")
    
    def test_08_check_due_schedules(self):
        """POST /api/admin/schedules/check-due processes overdue schedules"""
        res = self.session.post(f"{BASE_URL}/api/admin/schedules/check-due")
        assert res.status_code == 200, f"Failed to check due schedules: {res.text}"
        data = res.json()
        assert "reminders_sent" in data, "Response should have reminders_sent count"
        assert "due_schedules" in data, "Response should have due_schedules count"
        print(f"Check due: {data.get('reminders_sent')} reminders sent, {data.get('due_schedules')} due schedules")
    
    def test_09_delete_schedule(self):
        """DELETE /api/admin/schedules/{id} deletes a schedule"""
        schedule_id = getattr(self.__class__, 'monthly_schedule_id', None)
        if not schedule_id:
            pytest.skip("No monthly schedule created to delete")
        
        res = self.session.delete(f"{BASE_URL}/api/admin/schedules/{schedule_id}")
        assert res.status_code == 200, f"Failed to delete schedule: {res.text}"
        data = res.json()
        assert "deleted" in data.get("message", "").lower(), "Response should confirm deletion"
        print(f"Deleted schedule: {schedule_id}")
    
    def test_10_delete_nonexistent_schedule(self):
        """DELETE /api/admin/schedules/{id} returns 404 for nonexistent schedule"""
        res = self.session.delete(f"{BASE_URL}/api/admin/schedules/nonexistent_id_12345")
        assert res.status_code == 404, f"Should return 404 for nonexistent schedule: {res.text}"
        print("Correctly returned 404 for nonexistent schedule deletion")
    
    # ============= BULK RECONCILIATION TESTS =============
    
    def test_11_get_reconciliation_data(self):
        """GET /api/admin/royalties/reconciliation returns reconciliation data"""
        res = self.session.get(f"{BASE_URL}/api/admin/royalties/reconciliation")
        assert res.status_code == 200, f"Failed to get reconciliation: {res.text}"
        data = res.json()
        assert "summary" in data, "Response should have summary"
        assert "duplicates" in data, "Response should have duplicates list"
        assert "discrepancies" in data, "Response should have discrepancies list"
        
        summary = data["summary"]
        assert "total_imports" in summary, "Summary should have total_imports"
        assert "total_entries" in summary, "Summary should have total_entries"
        assert "duplicate_groups" in summary, "Summary should have duplicate_groups"
        assert "unmatched_entries" in summary, "Summary should have unmatched_entries"
        
        print(f"Reconciliation summary: {summary.get('total_entries')} entries, {summary.get('duplicate_groups')} duplicate groups, {summary.get('unmatched_entries')} unmatched")
    
    def test_12_resolve_duplicates_validation_min_entries(self):
        """POST resolve-duplicates requires at least 2 entry IDs"""
        res = self.session.post(f"{BASE_URL}/api/admin/royalties/reconciliation/resolve-duplicates", json={
            "entry_ids": ["single_id"],
            "strategy": "keep_latest"
        })
        assert res.status_code == 400, f"Should reject single entry ID: {res.text}"
        assert "2" in res.text, "Error should mention minimum 2 entries"
        print("Correctly rejected single entry ID")
    
    def test_13_resolve_duplicates_validation_empty_entries(self):
        """POST resolve-duplicates requires entry_ids"""
        res = self.session.post(f"{BASE_URL}/api/admin/royalties/reconciliation/resolve-duplicates", json={
            "entry_ids": [],
            "strategy": "keep_latest"
        })
        assert res.status_code == 400, f"Should reject empty entry IDs: {res.text}"
        print("Correctly rejected empty entry IDs")
    
    def test_14_resolve_duplicates_validation_invalid_strategy(self):
        """POST resolve-duplicates requires valid strategy"""
        res = self.session.post(f"{BASE_URL}/api/admin/royalties/reconciliation/resolve-duplicates", json={
            "entry_ids": ["id1", "id2"],
            "strategy": "invalid_strategy"
        })
        assert res.status_code == 400, f"Should reject invalid strategy: {res.text}"
        assert "keep_latest" in res.text or "keep_highest" in res.text or "delete_all" in res.text, "Error should mention valid strategies"
        print("Correctly rejected invalid strategy")
    
    def test_15_resolve_duplicates_valid_strategies(self):
        """POST resolve-duplicates accepts valid strategies (keep_latest, keep_highest, delete_all)"""
        # Test with non-existent IDs - should still validate strategy
        for strategy in ["keep_latest", "keep_highest", "delete_all"]:
            res = self.session.post(f"{BASE_URL}/api/admin/royalties/reconciliation/resolve-duplicates", json={
                "entry_ids": ["fake_id_1", "fake_id_2"],
                "strategy": strategy
            })
            # Should either succeed (200) or fail because entries not found (not 400 for invalid strategy)
            assert res.status_code in [200, 400], f"Unexpected status for strategy {strategy}: {res.status_code}"
            if res.status_code == 400:
                # If 400, it should be because entries not found, not invalid strategy
                assert "strategy" not in res.text.lower() or "valid" not in res.text.lower(), f"Strategy {strategy} should be valid"
            print(f"Strategy '{strategy}' accepted")
    
    def test_16_bulk_assign_validation_empty_entries(self):
        """POST bulk-assign requires entry_ids"""
        res = self.session.post(f"{BASE_URL}/api/admin/royalties/reconciliation/bulk-assign", json={
            "entry_ids": [],
            "artist_id": "some_artist_id"
        })
        assert res.status_code == 400, f"Should reject empty entry IDs: {res.text}"
        print("Correctly rejected empty entry IDs for bulk assign")
    
    def test_17_bulk_assign_validation_invalid_artist(self):
        """POST bulk-assign requires valid artist_id"""
        res = self.session.post(f"{BASE_URL}/api/admin/royalties/reconciliation/bulk-assign", json={
            "entry_ids": ["id1", "id2"],
            "artist_id": "nonexistent_artist_12345"
        })
        assert res.status_code == 404, f"Should return 404 for invalid artist: {res.text}"
        assert "artist" in res.text.lower() or "not found" in res.text.lower(), "Error should mention artist not found"
        print("Correctly returned 404 for invalid artist")
    
    def test_18_bulk_assign_with_valid_artist(self):
        """POST bulk-assign works with valid artist_id (even if entries don't exist)"""
        # Get admin user ID (which is a valid user)
        admin_id = self.admin_user.get("id")
        if not admin_id:
            pytest.skip("No admin user ID available")
        
        res = self.session.post(f"{BASE_URL}/api/admin/royalties/reconciliation/bulk-assign", json={
            "entry_ids": ["fake_entry_1", "fake_entry_2"],
            "artist_id": admin_id
        })
        # Should succeed (200) even if entries don't exist - just assigns 0
        assert res.status_code == 200, f"Should accept valid artist: {res.text}"
        data = res.json()
        assert "assigned" in data, "Response should have assigned count"
        print(f"Bulk assign with valid artist: {data.get('assigned')} entries assigned")
    
    # ============= REGRESSION TESTS =============
    
    def test_19_revenue_analytics_still_works(self):
        """GET /api/analytics/revenue returns revenue data (regression)"""
        res = self.session.get(f"{BASE_URL}/api/analytics/revenue")
        assert res.status_code == 200, f"Revenue analytics failed: {res.text}"
        data = res.json()
        assert "summary" in data, "Should have summary section"
        assert "kalmori" in data, "Should have kalmori section"
        assert "combined" in data, "Should have combined section"
        print(f"Revenue analytics working: ${data.get('combined', {}).get('total_earnings', 0):.2f} total earnings")
    
    def test_20_distributor_templates_still_work(self):
        """GET /api/admin/distributor-templates returns templates (regression)"""
        res = self.session.get(f"{BASE_URL}/api/admin/distributor-templates")
        assert res.status_code == 200, f"Templates endpoint failed: {res.text}"
        data = res.json()
        assert "templates" in data, "Should have templates list"
        print(f"Templates working: {len(data.get('templates', []))} templates found")
    
    def test_21_royalty_imports_still_work(self):
        """GET /api/admin/royalties/imports returns imports (regression)"""
        res = self.session.get(f"{BASE_URL}/api/admin/royalties/imports")
        assert res.status_code == 200, f"Imports endpoint failed: {res.text}"
        data = res.json()
        assert "imports" in data, "Should have imports list"
        print(f"Imports working: {len(data.get('imports', []))} imports found")
    
    # ============= CLEANUP =============
    
    def test_99_cleanup_test_schedule(self):
        """Cleanup - delete test schedule created during tests"""
        schedule_id = getattr(self.__class__, 'created_schedule_id', None)
        if schedule_id:
            res = self.session.delete(f"{BASE_URL}/api/admin/schedules/{schedule_id}")
            if res.status_code == 200:
                print(f"Cleaned up test schedule: {schedule_id}")
            else:
                print(f"Could not cleanup schedule (may already be deleted): {schedule_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
