"""Database boundary tests for Review 3 transactions (no Oracle server needed)."""

import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import oracledb

import app as flask_app


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.demo_patch = patch.object(flask_app, "DEMO_MODE", False)
        self.demo_patch.start()
        self.addCleanup(self.demo_patch.stop)
        self.client = flask_app.app.test_client()

    def connection(self, cursor):
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor
        manager = patch.object(flask_app.db, "get_connection")
        get_connection = manager.start()
        self.addCleanup(manager.stop)
        get_connection.return_value.__enter__.return_value = conn
        return conn

    def test_issue_passes_date_to_procedure_and_commits(self):
        cur = MagicMock()
        conn = self.connection(cur)
        due = date.today() + timedelta(days=7)
        with patch.object(flask_app.db, "next_id", return_value=16):
            response = self.client.post("/api/issues", json={
                "book_id": 1, "member_id": 2, "staff_id": 1,
                "due_date": due.isoformat(),
            })
        self.assertEqual(response.status_code, 200)
        cur.callproc.assert_called_once_with("issue_book", [16, 1, 2, 1, due])
        conn.commit.assert_called_once()

    def test_issue_without_stock_rolls_back(self):
        cur = MagicMock()
        conn = self.connection(cur)
        cur.callproc.side_effect = oracledb.DatabaseError("ORA-20005: No copies available")
        with patch.object(flask_app.db, "next_id", return_value=16):
            response = self.client.post("/api/issues", json={
                "book_id": 1, "member_id": 2, "staff_id": 1,
                "due_date": (date.today() + timedelta(days=7)).isoformat(),
            })
        self.assertEqual(response.status_code, 409)
        conn.rollback.assert_called_once()
        conn.commit.assert_not_called()

    def test_return_serializes_issue_and_fine_separately(self):
        cur = MagicMock()
        conn = self.connection(cur)
        issued = date.today() - timedelta(days=20)
        due = date.today() - timedelta(days=6)
        returned = date.today()

        def execute(sql, params):
            if "FROM ISSUE WHERE" in sql:
                cur.description = [(name,) for name in (
                    "ISSUE_ID", "BOOK_ID", "MEMBER_ID", "STAFF_ID",
                    "ISSUE_DATE", "DUE_DATE", "RETURN_DATE", "STATUS")]
                cur.fetchone.return_value = (11, 1, 2, 1, issued, due, returned, "Returned")
            elif "FROM FINE WHERE" in sql:
                cur.description = [(name,) for name in (
                    "FINE_ID", "ISSUE_ID", "AMOUNT", "PAID_STATUS")]
                cur.fetchone.return_value = (11, 11, 30, "Unpaid")

        cur.execute.side_effect = execute
        response = self.client.post("/api/issues/11/return")
        self.assertEqual(response.status_code, 200)
        result = response.get_json()["data"]
        self.assertEqual(result["issue"]["status"], "Returned")
        self.assertEqual(result["issue"]["book_id"], 1)
        self.assertEqual(result["fine"]["amount"], 30)
        conn.commit.assert_called_once()

    def test_double_return_rolls_back(self):
        cur = MagicMock()
        conn = self.connection(cur)
        cur.callproc.side_effect = oracledb.DatabaseError("ORA-20003: Book already returned")
        response = self.client.post("/api/issues/11/return")
        self.assertEqual(response.status_code, 409)
        conn.rollback.assert_called_once()

    def test_missing_issue_is_404(self):
        cur = MagicMock()
        conn = self.connection(cur)
        cur.callproc.side_effect = oracledb.DatabaseError("ORA-20004: Issue ID not found")
        response = self.client.post("/api/issues/999/return")
        self.assertEqual(response.status_code, 404)
        conn.rollback.assert_called_once()

    def test_book_stock_change_preserves_issued_count(self):
        cur = MagicMock()
        conn = self.connection(cur)
        cur.fetchone.return_value = (5, 3)  # 2 currently issued
        response = self.client.put("/api/books/1", json={
            "title": "Malgudi Days", "author_id": 1,
            "category_id": 1, "price": 299, "total_copies": 7,
        })
        self.assertEqual(response.status_code, 200)
        update_args = cur.execute.call_args_list[-1].args[1]
        self.assertEqual(update_args["available_copies"], 5)
        conn.commit.assert_called_once()

    def test_book_stock_cannot_drop_below_issued_count(self):
        cur = MagicMock()
        conn = self.connection(cur)
        cur.fetchone.return_value = (5, 3)
        response = self.client.put("/api/books/1", json={
            "title": "Malgudi Days", "author_id": 1,
            "category_id": 1, "price": 299, "total_copies": 1,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(cur.execute.call_count, 1)
        conn.rollback.assert_called_once()

    def test_overdue_demo_fetches_plsql_cursor(self):
        cur = MagicMock()
        self.connection(cur)
        rows_cursor = MagicMock()
        rows_cursor.description = [(name,) for name in (
            "ISSUE_ID", "MEMBER_NAME", "BOOK_TITLE", "DUE_DATE")]
        rows_cursor.fetchall.return_value = [(11, "Aditi", "Malgudi Days", date(2026, 9, 15))]
        cur.var.return_value.getvalue.return_value = rows_cursor
        response = self.client.post("/api/database-logic/overdue-demonstration")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"][0]["issue_id"], 11)
        self.assertIn("OPEN overdue_cursor FOR", cur.execute.call_args.args[0])
        self.assertIn("TRUNC(i.due_date) < TRUNC(SYSDATE)", cur.execute.call_args.args[0])
        rows_cursor.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
