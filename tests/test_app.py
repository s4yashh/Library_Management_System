"""Automated tests for the LibraryDesk Flask backend.

Tests marked with @unittest.mock live tests rely on a real Oracle connection.
Set ORACLE_USER, ORACLE_PASSWORD and ORACLE_CONNECT_STRING in your environment
before running them. By default only the demo-mode tests run.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("DEMO_MODE", "true")
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret")

import app as flask_app


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = flask_app.app
        self.client = self.app.test_client()


class HealthTests(BaseTestCase):
    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "ok")

    def test_status_reports_demo_mode(self):
        res = self.client.get("/api/status")
        self.assertIn(res.status_code, [200, 503])
        data = res.get_json()
        self.assertTrue("demo_mode" in data.get("data", {}) or "demo_mode" in data)


class DashboardTests(BaseTestCase):
    def test_dashboard_stats(self):
        res = self.client.get("/api/dashboard/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("total_books", data["data"])
        self.assertIn("available_copies", data["data"])

    def test_recent_issues(self):
        res = self.client.get("/api/dashboard/recent-issues")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)

    def test_overdue_preview(self):
        res = self.client.get("/api/dashboard/overdue")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)


class BookTests(BaseTestCase):
    def test_list_books(self):
        res = self.client.get("/api/books")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)
        if data["data"]:
            self.assertIn("title", data["data"][0])

    def test_get_book(self):
        res = self.client.get("/api/books/1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["book_id"], 1)

    def test_get_book_not_found(self):
        res = self.client.get("/api/books/99999")
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        self.assertFalse(data["success"])

    def test_create_book_validation(self):
        res = self.client.post("/api/books", json={"title": "", "price": -5})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])


class MemberTests(BaseTestCase):
    def test_list_members(self):
        res = self.client.get("/api/members")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)

    def test_get_member(self):
        res = self.client.get("/api/members/1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["member_id"], 1)

    def test_create_member_validation(self):
        res = self.client.post("/api/members", json={
            "name": "",
            "email": "not-an-email",
            "membership_type": "Invalid",
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])

    def test_create_member_success_demo(self):
        res = self.client.post("/api/members", json={
            "name": "Demo User",
            "email": "demo_user_test@example.com",
            "phone": "9000000099",
            "membership_type": "Student",
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])


class AuthorCategoryTests(BaseTestCase):
    def test_list_authors(self):
        res = self.client.get("/api/authors")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)

    def test_list_categories(self):
        res = self.client.get("/api/categories")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)


class StaffTests(BaseTestCase):
    def test_list_staff(self):
        res = self.client.get("/api/staff")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)


class IssueTests(BaseTestCase):
    def test_list_issues(self):
        res = self.client.get("/api/issues")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)

    def test_create_issue_validation(self):
        res = self.client.post("/api/issues", json={})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])

    def test_return_invalid_issue(self):
        res = self.client.post("/api/issues/99999/return")
        self.assertEqual(res.status_code, 404)

    def test_demo_return_shows_calculated_fine(self):
        res = self.client.post("/api/issues/11/return")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertEqual(data["issue"]["status"], "Returned")
        self.assertGreater(data["fine"]["amount"], 0)


class FineTests(BaseTestCase):
    def test_list_fines(self):
        res = self.client.get("/api/fines")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)

    def test_fines_summary(self):
        res = self.client.get("/api/fines/summary")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("Paid", data["data"])
        self.assertIn("Unpaid", data["data"])

    def test_update_payment_validation(self):
        res = self.client.put("/api/fines/1/payment-status", json={"paid_status": "Maybe"})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])


class ReportTests(BaseTestCase):
    def test_available_books_report(self):
        res = self.client.get("/api/reports/available-books")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)

    def test_overdue_report(self):
        res = self.client.get("/api/reports/overdue")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)

    def test_invalid_report(self):
        res = self.client.get("/api/reports/nonexistent")
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        self.assertFalse(data["success"])


class DatabaseLogicTests(BaseTestCase):
    def test_objects_endpoint(self):
        res = self.client.get("/api/database-logic/objects")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)
        names = {obj["name"] for obj in data["data"]}
        self.assertIn("issue_book", names)
        self.assertIn("return_book", names)
        self.assertIn("calculate_fine", names)
        self.assertIn("trg_issue_insert", names)
        self.assertIn("trg_issue_return", names)

    def test_overdue_demonstration(self):
        res = self.client.post("/api/database-logic/overdue-demonstration")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)


class LiveOracleTests(unittest.TestCase):
    """Run only when explicitly enabled with RUN_LIVE_ORACLE_TESTS=true."""

    def setUp(self):
        self.demo_patch = patch.object(flask_app, "DEMO_MODE", False)
        self.demo_patch.start()
        self.addCleanup(self.demo_patch.stop)
        self.app = flask_app.app
        self.client = self.app.test_client()

    @unittest.skipUnless(
        os.getenv("RUN_LIVE_ORACLE_TESTS", "").lower() == "true"
        and os.getenv("ORACLE_USER") and os.getenv("ORACLE_PASSWORD") and os.getenv("ORACLE_CONNECT_STRING"),
        "Live Oracle tests are not enabled or credentials are missing"
    )
    def test_live_oracle_status(self):
        res = self.client.get("/api/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["data"]["connected"])

    @unittest.skipUnless(
        os.getenv("RUN_LIVE_ORACLE_TESTS", "").lower() == "true"
        and os.getenv("ORACLE_USER") and os.getenv("ORACLE_PASSWORD") and os.getenv("ORACLE_CONNECT_STRING"),
        "Live Oracle tests are not enabled or credentials are missing"
    )
    def test_live_books_list(self):
        res = self.client.get("/api/books")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["data"], list)


class RollbackTests(unittest.TestCase):
    """Verify that the backend handles Oracle errors without exposing internals."""

    def test_oracle_error_returns_json(self):
        app = flask_app.app
        client = app.test_client()
        with patch("app.db.get_connection") as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = Exception("Simulated Oracle failure")
            mock_connection = MagicMock()
            mock_connection.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
            mock_connection.cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_conn.return_value.__enter__ = MagicMock(return_value=mock_connection)
            mock_conn.return_value.__exit__ = MagicMock(return_value=False)
            with patch.object(flask_app, "DEMO_MODE", False):
                res = client.get("/api/books")
            self.assertEqual(res.status_code, 500)
            data = res.get_json()
            self.assertFalse(data["success"])


if __name__ == "__main__":
    unittest.main()
