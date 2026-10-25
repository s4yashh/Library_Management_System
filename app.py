"""LibraryDesk Flask backend for the Library Management System."""

import os
import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

import oracledb
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

import db

load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


def serialize_value(value: Any) -> Any:
    """Convert Oracle/Python values into JSON-serializable forms."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def serialize_rows(cur, rows: list) -> list[dict[str, Any]]:
    """Transform fetched rows into dicts using cursor description."""
    columns = [desc[0].lower() for desc in cur.description] if cur.description else []
    return [dict(zip(columns, (serialize_value(v) for v in row))) for row in rows]


def json_success(data: Any = None, message: str = "Success"):
    payload = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload)


def json_error(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
_PHONE_RE = re.compile(r"^[0-9+\-\s]{7,20}$")


def is_valid_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(email))


def is_valid_phone(phone: str) -> bool:
    return phone == "" or bool(_PHONE_RE.match(phone))


@app.errorhandler(Exception)
def handle_exception(exc):
    app.logger.exception("Unhandled exception")
    return json_error("An unexpected error occurred", 500)


@app.errorhandler(404)
def handle_not_found(exc):
    if request.path.startswith("/api/"):
        return json_error("Endpoint not found", 404)
    return send_from_directory(app.static_folder, "404.html"), 404


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# ---------------------------------------------------------------------------
# Health / status
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    return json_success({"status": "ok", "demo_mode": DEMO_MODE})


@app.route("/api/status", methods=["GET"])
def status():
    status_info = db.db_status()
    status_info["demo_mode"] = DEMO_MODE
    if status_info["connected"]:
        return json_success(status_info)
    return jsonify({"success": False, "error": status_info["message"], "demo_mode": DEMO_MODE}), 503


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route("/api/dashboard/stats", methods=["GET"])
def dashboard_stats():
    if DEMO_MODE:
        from mock_data import DASHBOARD_STATS
        return json_success(DASHBOARD_STATS)

    queries = {
        "total_books": "SELECT COUNT(*) FROM BOOK",
        "total_copies": "SELECT SUM(total_copies) FROM BOOK",
        "available_copies": "SELECT SUM(available_copies) FROM BOOK",
        "issued_transactions": "SELECT COUNT(*) FROM ISSUE WHERE status = 'Issued'",
        "registered_members": "SELECT COUNT(*) FROM MEMBER",
        "overdue_issues": """
            SELECT COUNT(*) FROM ISSUE
            WHERE status = 'Issued' AND due_date < SYSDATE
        """,
        "total_unpaid_fines": "SELECT SUM(amount) FROM FINE WHERE paid_status = 'Unpaid'",
        "total_paid_fines": "SELECT SUM(amount) FROM FINE WHERE paid_status = 'Paid'",
    }

    stats = {}
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            for key, sql in queries.items():
                cur.execute(sql)
                row = cur.fetchone()
                value = row[0]
                stats[key] = serialize_value(value) if value is not None else 0

    return json_success(stats)


@app.route("/api/dashboard/recent-issues", methods=["GET"])
def dashboard_recent_issues():
    if DEMO_MODE:
        from mock_data import RECENT_ISSUES
        return json_success(RECENT_ISSUES)

    sql = """
        SELECT i.issue_id, m.name AS member_name, b.title AS book_title,
               i.issue_date, i.due_date, i.return_date, i.status
        FROM ISSUE i
        JOIN MEMBER m ON m.member_id = i.member_id
        JOIN BOOK b ON b.book_id = i.book_id
        ORDER BY i.issue_id DESC
        FETCH FIRST 10 ROWS ONLY
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return json_success(serialize_rows(cur, rows))


@app.route("/api/dashboard/overdue", methods=["GET"])
def dashboard_overdue():
    if DEMO_MODE:
        from mock_data import OVERDUE_PREVIEW
        return json_success(OVERDUE_PREVIEW)

    sql = """
        SELECT i.issue_id, m.name AS member_name, b.title AS book_title, i.due_date
        FROM ISSUE i
        JOIN MEMBER m ON m.member_id = i.member_id
        JOIN BOOK b ON b.book_id = i.book_id
        WHERE i.status = 'Issued' AND i.due_date < SYSDATE
        ORDER BY i.due_date ASC
        FETCH FIRST 5 ROWS ONLY
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return json_success(serialize_rows(cur, rows))


# ---------------------------------------------------------------------------
# Books
# ---------------------------------------------------------------------------

@app.route("/api/books", methods=["GET"])
def list_books():
    if DEMO_MODE:
        from mock_data import BOOKS
        return json_success(BOOKS)

    search = request.args.get("search", "").strip()
    category_id = request.args.get("category_id", "").strip()
    availability = request.args.get("availability", "").strip()

    sql = """
        SELECT b.book_id, b.title, b.author_id, a.author_name,
               b.category_id, c.category_name, b.price,
               b.total_copies, b.available_copies
        FROM BOOK b
        JOIN AUTHOR a ON a.author_id = b.author_id
        JOIN CATEGORY c ON c.category_id = b.category_id
        WHERE 1=1
    """
    params = {}

    if search:
        sql += " AND LOWER(b.title) LIKE LOWER(:search)"
        params["search"] = f"%{search}%"
    if category_id:
        sql += " AND b.category_id = :category_id"
        params["category_id"] = int(category_id)
    if availability == "available":
        sql += " AND b.available_copies > 0"
    elif availability == "unavailable":
        sql += " AND b.available_copies = 0"

    sql += " ORDER BY b.book_id"

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return json_success(serialize_rows(cur, rows))


@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id: int):
    if DEMO_MODE:
        from mock_data import BOOKS
        book = next((b for b in BOOKS if b["book_id"] == book_id), None)
        if book:
            return json_success(book)
        return json_error("Book not found", 404)

    sql = """
        SELECT b.book_id, b.title, b.author_id, a.author_name,
               b.category_id, c.category_name, b.price,
               b.total_copies, b.available_copies
        FROM BOOK b
        JOIN AUTHOR a ON a.author_id = b.author_id
        JOIN CATEGORY c ON c.category_id = b.category_id
        WHERE b.book_id = :book_id
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"book_id": book_id})
            row = cur.fetchone()
            if not row:
                return json_error("Book not found", 404)
            return json_success(serialize_rows(cur, [row])[0])


@app.route("/api/books", methods=["POST"])
def create_book():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    author_id = data.get("author_id")
    category_id = data.get("category_id")
    price = data.get("price")
    total_copies = data.get("total_copies", 1)

    if not title:
        return json_error("Title is required")
    try:
        author_id = int(author_id)
        category_id = int(category_id)
        price = float(price)
        total_copies = int(total_copies)
    except (TypeError, ValueError):
        return json_error("Invalid numeric values")

    if price <= 0:
        return json_error("Price must be greater than zero")
    if total_copies < 0:
        return json_error("Total copies cannot be negative")

    if DEMO_MODE:
        return json_success({"book_id": 999, "demo": True}, "Book created (demo mode)")

    book_id = db.next_id("BOOK", "book_id")
    sql = """
        INSERT INTO BOOK (book_id, title, author_id, category_id, price, total_copies, available_copies)
        VALUES (:book_id, :title, :author_id, :category_id, :price, :total_copies, :total_copies)
    """
    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, {
                    "book_id": book_id,
                    "title": title,
                    "author_id": author_id,
                    "category_id": category_id,
                    "price": price,
                    "total_copies": total_copies,
                })
            conn.commit()
            return json_success({"book_id": book_id}, "Book added successfully")
        except oracledb.IntegrityError as exc:
            conn.rollback()
            error_obj, = exc.args
            message = str(exc)
            if "FK" in message.upper() or "ORA-02291" in message:
                return json_error("Selected author or category does not exist", 400)
            return json_error("Could not add book: constraint violation", 400)
        except oracledb.Error as exc:
            conn.rollback()
            return json_error(f"Database error: {exc}", 500)


@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id: int):
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    author_id = data.get("author_id")
    category_id = data.get("category_id")
    price = data.get("price")
    total_copies = data.get("total_copies")

    if not title:
        return json_error("Title is required")
    try:
        author_id = int(author_id)
        category_id = int(category_id)
        price = float(price)
        total_copies = int(total_copies)
    except (TypeError, ValueError):
        return json_error("Invalid numeric values")

    if price <= 0:
        return json_error("Price must be greater than zero")
    if total_copies < 0:
        return json_error("Total copies cannot be negative")

    if DEMO_MODE:
        return json_success({"demo": True}, "Book updated (demo mode)")

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT available_copies FROM BOOK WHERE book_id = :book_id", {"book_id": book_id})
            row = cur.fetchone()
            if not row:
                return json_error("Book not found", 404)
            available = row[0]

    if total_copies < available:
        return json_error(
            "Total copies cannot be less than currently available copies "
            f"({available})"
        )

    sql = """
        UPDATE BOOK
        SET title = :title,
            author_id = :author_id,
            category_id = :category_id,
            price = :price,
            total_copies = :total_copies
        WHERE book_id = :book_id
    """
    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, {
                    "title": title,
                    "author_id": author_id,
                    "category_id": category_id,
                    "price": price,
                    "total_copies": total_copies,
                    "book_id": book_id,
                })
            conn.commit()
            return json_success(message="Book updated successfully")
        except oracledb.IntegrityError:
            conn.rollback()
            return json_error("Could not update book: constraint violation", 400)
        except oracledb.Error as exc:
            conn.rollback()
            return json_error(f"Database error: {exc}", 500)


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id: int):
    if DEMO_MODE:
        return json_success({"demo": True}, "Book deleted (demo mode)")

    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM BOOK WHERE book_id = :book_id", {"book_id": book_id})
                if cur.rowcount == 0:
                    return json_error("Book not found", 404)
            conn.commit()
            return json_success(message="Book deleted successfully")
        except oracledb.IntegrityError:
            conn.rollback()
            return json_error(
                "Cannot delete this book because it has existing issue or fine records.",
                409,
            )
        except oracledb.Error as exc:
            conn.rollback()
            return json_error(f"Database error: {exc}", 500)


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------

@app.route("/api/members", methods=["GET"])
def list_members():
    if DEMO_MODE:
        from mock_data import MEMBERS
        return json_success(MEMBERS)

    search = request.args.get("search", "").strip()
    sql = """
        SELECT member_id, name, email, phone, join_date, membership_type
        FROM MEMBER
        WHERE 1=1
    """
    params = {}
    if search:
        sql += """ AND (
            LOWER(name) LIKE LOWER(:search)
            OR LOWER(email) LIKE LOWER(:search)
            OR TO_CHAR(member_id) LIKE :search
        )"""
        params["search"] = f"%{search}%"
    sql += " ORDER BY member_id"

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return json_success(serialize_rows(cur, rows))


@app.route("/api/members/<int:member_id>", methods=["GET"])
def get_member(member_id: int):
    if DEMO_MODE:
        from mock_data import MEMBERS
        member = next((m for m in MEMBERS if m["member_id"] == member_id), None)
        if member:
            return json_success(member)
        return json_error("Member not found", 404)

    sql = """
        SELECT member_id, name, email, phone, join_date, membership_type
        FROM MEMBER WHERE member_id = :member_id
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"member_id": member_id})
            row = cur.fetchone()
            if not row:
                return json_error("Member not found", 404)
            return json_success(serialize_rows(cur, [row])[0])


@app.route("/api/members", methods=["POST"])
def create_member():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    membership_type = data.get("membership_type", "").strip()

    if not name:
        return json_error("Name is required")
    if not email:
        return json_error("Email is required")
    if not is_valid_email(email):
        return json_error("Please enter a valid email address")
    if not is_valid_phone(phone):
        return json_error("Please enter a valid phone number")
    if membership_type not in ("Student", "Faculty", "General"):
        return json_error("Membership type must be Student, Faculty or General")

    if DEMO_MODE:
        return json_success({"member_id": 999, "demo": True}, "Member registered (demo mode)")

    member_id = db.next_id("MEMBER", "member_id")
    sql = """
        INSERT INTO MEMBER (member_id, name, email, phone, membership_type)
        VALUES (:member_id, :name, :email, :phone, :membership_type)
    """
    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, {
                    "member_id": member_id,
                    "name": name,
                    "email": email,
                    "phone": phone or None,
                    "membership_type": membership_type,
                })
            conn.commit()
            return json_success({"member_id": member_id}, "Member registered successfully")
        except oracledb.IntegrityError:
            conn.rollback()
            return json_error("A member with this email already exists", 409)
        except oracledb.Error as exc:
            conn.rollback()
            return json_error(f"Database error: {exc}", 500)


@app.route("/api/members/<int:member_id>", methods=["PUT"])
def update_member(member_id: int):
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    membership_type = data.get("membership_type", "").strip()

    if not name:
        return json_error("Name is required")
    if not email:
        return json_error("Email is required")
    if not is_valid_email(email):
        return json_error("Please enter a valid email address")
    if not is_valid_phone(phone):
        return json_error("Please enter a valid phone number")
    if membership_type not in ("Student", "Faculty", "General"):
        return json_error("Membership type must be Student, Faculty or General")

    if DEMO_MODE:
        return json_success({"demo": True}, "Member updated (demo mode)")

    sql = """
        UPDATE MEMBER
        SET name = :name,
            email = :email,
            phone = :phone,
            membership_type = :membership_type
        WHERE member_id = :member_id
    """
    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, {
                    "name": name,
                    "email": email,
                    "phone": phone or None,
                    "membership_type": membership_type,
                    "member_id": member_id,
                })
                if cur.rowcount == 0:
                    return json_error("Member not found", 404)
            conn.commit()
            return json_success(message="Member updated successfully")
        except oracledb.IntegrityError:
            conn.rollback()
            return json_error("A member with this email already exists", 409)
        except oracledb.Error as exc:
            conn.rollback()
            return json_error(f"Database error: {exc}", 500)


@app.route("/api/members/<int:member_id>", methods=["DELETE"])
def delete_member(member_id: int):
    if DEMO_MODE:
        return json_success({"demo": True}, "Member deleted (demo mode)")

    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM MEMBER WHERE member_id = :member_id", {"member_id": member_id})
                if cur.rowcount == 0:
                    return json_error("Member not found", 404)
            conn.commit()
            return json_success(message="Member deleted successfully")
        except oracledb.IntegrityError:
            conn.rollback()
            return json_error(
                "Cannot delete this member because they have existing issue records.",
                409,
            )
        except oracledb.Error as exc:
            conn.rollback()
            return json_error(f"Database error: {exc}", 500)


@app.route("/api/members/<int:member_id>/history", methods=["GET"])
def member_history(member_id: int):
    if DEMO_MODE:
        from mock_data import ISSUES
        rows = [i for i in ISSUES if i.get("member_id") == member_id]
        return json_success(rows)

    sql = """
        SELECT i.issue_id, b.title AS book_title, i.issue_date,
               i.due_date, i.return_date, i.status
        FROM ISSUE i
        JOIN BOOK b ON b.book_id = i.book_id
        WHERE i.member_id = :member_id
        ORDER BY i.issue_id DESC
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"member_id": member_id})
            rows = cur.fetchall()
            return json_success(serialize_rows(cur, rows))


# ---------------------------------------------------------------------------
# Authors
# ---------------------------------------------------------------------------

@app.route("/api/authors", methods=["GET"])
def list_authors():
    if DEMO_MODE:
        from mock_data import AUTHORS
        return json_success(AUTHORS)

    sql = """
        SELECT a.author_id, a.author_name, a.country,
               COUNT(b.book_id) AS book_count
        FROM AUTHOR a
        LEFT JOIN BOOK b ON b.author_id = a.author_id
        GROUP BY a.author_id, a.author_name, a.country
        ORDER BY a.author_id
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return json_success(serialize_rows(cur, rows))


@app.route("/api/authors", methods=["POST"])
def create_author():
    data = request.get_json(silent=True) or {}
    author_name = data.get("author_name", "").strip()
    country = data.get("country", "India").strip()

    if not author_name:
        return json_error("Author name is required")

    if DEMO_MODE:
        return json_success({"author_id": 999, "demo": True}, "Author added (demo mode)")

    author_id = db.next_id("AUTHOR", "author_id")
    sql = "INSERT INTO AUTHOR (author_id, author_name, country) VALUES (:author_id, :author_name, :country)"
    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, {
                    "author_id": author_id,
                    "author_name": author_name,
                    "country": country or "India",
                })
            conn.commit()
            return json_success({"author_id": author_id}, "Author added successfully")
        except oracledb.Error as exc:
            conn.rollback()
            return json_error(f"Database error: {exc}", 500)


@app.route("/api/authors/<int:author_id>", methods=["PUT"])
def update_author(author_id: int):
    data = request.get_json(silent=True) or {}
    author_name = data.get("author_name", "").strip()
    country = data.get("country", "India").strip()

    if not author_name:
        return json_error("Author name is required")

    if DEMO_MODE:
        return json_success({"demo": True}, "Author updated (demo mode)")

    sql = """
        UPDATE AUTHOR
        SET author_name = :author_name, country = :country
        WHERE author_id = :author_id
    """
    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, {
                    "author_name": author_name,
                    "country": country or "India",
                    "author_id": author_id,
                })
                if cur.rowcount == 0:
                    return json_error("Author not found", 404)
            conn.commit()
            return json_success(message="Author updated successfully")
        except oracledb.Error as exc:
            conn.rollback()
            return json_error(f"Database error: {exc}", 500)


@app.route("/api/authors/<int:author_id>", methods=["DELETE"])
def delete_author(author_id: int):
    if DEMO_MODE:
        return json_success({"demo": True}, "Author deleted (demo mode)")

    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM AUTHOR WHERE author_id = :author_id", {"author_id": author_id})
                if cur.rowcount == 0:
                    return json_error("Author not found", 404)
            conn.commit()
            return json_success(message="Author deleted successfully")
        except oracledb.IntegrityError:
            conn.rollback()
            return json_error(
                "Cannot delete this author because books are linked to them.",
                409,
            )
        except oracledb.Error as exc:
            conn.rollback()
            return json_error(f"Database error: {exc}", 500)


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@app.route("/api/categories", methods=["GET"])
def list_categories():
    if DEMO_MODE:
        from mock_data import CATEGORIES
        return json_success(CATEGORIES)

    sql = """
        SELECT c.category_id, c.category_name,
               COUNT(b.book_id) AS book_count,
               NVL(SUM(b.available_copies), 0) AS available_copies
        FROM CATEGORY c
        LEFT JOIN BOOK b ON b.category_id = c.category_id
        GROUP BY c.category_id, c.category_name
        ORDER BY c.category_id
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return json_success(serialize_rows(cur, rows))


@app.route("/api/categories", methods=["POST"])
def create_category():
    data = request.get_json(silent=True) or {}
    category_name = data.get("category_name", "").strip()

    if not category_name:
        return json_error("Category name is required")

    if DEMO_MODE:
        return json_success({"category_id": 999, "demo": True}, "Category added (demo mode)")

    category_id = db.next_id("CATEGORY", "category_id")
    sql = "INSERT INTO CATEGORY (category_id, category_name) VALUES (:category_id, :category_name)"
    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, {"category_id": category_id, "category_name": category_name})
            conn.commit()
            return json_success({"category_id": category_id}, "Category added successfully")
        except oracledb.IntegrityError:
            conn.rollback()
            return json_error("A category with this name already exists", 409)
        except oracledb.Error as exc:
            conn.rollback()
            return json_error(f"Database error: {exc}", 500)


@app.route("/api/categories/<int:category_id>", methods=["PUT"])
def update_category(category_id: int):
    data = request.get_json(silent=True) or {}
    category_name = data.get("category_name", "").strip()

    if not category_name:
        return json_error("Category name is required")

    if DEMO_MODE:
        return json_success({"demo": True}, "Category updated (demo mode)")

    sql = "UPDATE CATEGORY SET category_name = :category_name WHERE category_id = :category_id"
    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, {"category_name": category_name, "category_id": category_id})
                if cur.rowcount == 0:
                    return json_error("Category not found", 404)
            conn.commit()
            return json_success(message="Category updated successfully")
        except oracledb.IntegrityError:
            conn.rollback()
            return json_error("A category with this name already exists", 409)
        except oracledb.Error as exc:
            conn.rollback()
            return json_error(f"Database error: {exc}", 500)


@app.route("/api/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id: int):
    if DEMO_MODE:
        return json_success({"demo": True}, "Category deleted (demo mode)")

    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM CATEGORY WHERE category_id = :category_id", {"category_id": category_id})
                if cur.rowcount == 0:
                    return json_error("Category not found", 404)
            conn.commit()
            return json_success(message="Category deleted successfully")
        except oracledb.IntegrityError:
            conn.rollback()
            return json_error(
                "Cannot delete this category because books are linked to it.",
                409,
            )
        except oracledb.Error as exc:
            conn.rollback()
            return json_error(f"Database error: {exc}", 500)


# ---------------------------------------------------------------------------
# Staff
# ---------------------------------------------------------------------------

@app.route("/api/staff", methods=["GET"])
def list_staff():
    if DEMO_MODE:
        from mock_data import STAFF
        return json_success(STAFF)

    sql = "SELECT staff_id, name, role, email FROM STAFF ORDER BY staff_id"
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return json_success(serialize_rows(cur, rows))


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------

@app.route("/api/issues", methods=["GET"])
def list_issues():
    if DEMO_MODE:
        from mock_data import ISSUES
        return json_success(ISSUES)

    status_filter = request.args.get("status", "").strip()
    overdue = request.args.get("overdue", "").strip()
    search = request.args.get("search", "").strip()

    sql = """
        SELECT i.issue_id, i.book_id, b.title AS book_title,
               i.member_id, m.name AS member_name,
               i.staff_id, s.name AS staff_name,
               i.issue_date, i.due_date, i.return_date, i.status
        FROM ISSUE i
        JOIN BOOK b ON b.book_id = i.book_id
        JOIN MEMBER m ON m.member_id = i.member_id
        LEFT JOIN STAFF s ON s.staff_id = i.staff_id
        WHERE 1=1
    """
    params = {}

    if status_filter in ("Issued", "Returned"):
        sql += " AND i.status = :status"
        params["status"] = status_filter
    if overdue == "true":
        sql += " AND i.status = 'Issued' AND i.due_date < SYSDATE"
    if search:
        sql += """ AND (
            LOWER(b.title) LIKE LOWER(:search)
            OR LOWER(m.name) LIKE LOWER(:search)
            OR TO_CHAR(i.issue_id) LIKE :search
        )"""
        params["search"] = f"%{search}%"

    sql += " ORDER BY i.issue_id DESC"

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return json_success(serialize_rows(cur, rows))


@app.route("/api/issues/<int:issue_id>", methods=["GET"])
def get_issue(issue_id: int):
    if DEMO_MODE:
        from mock_data import ISSUES
        issue = next((i for i in ISSUES if i["issue_id"] == issue_id), None)
        if issue:
            return json_success(issue)
        return json_error("Issue not found", 404)

    sql = """
        SELECT i.issue_id, i.book_id, b.title AS book_title,
               i.member_id, m.name AS member_name,
               i.staff_id, s.name AS staff_name,
               i.issue_date, i.due_date, i.return_date, i.status
        FROM ISSUE i
        JOIN BOOK b ON b.book_id = i.book_id
        JOIN MEMBER m ON m.member_id = i.member_id
        LEFT JOIN STAFF s ON s.staff_id = i.staff_id
        WHERE i.issue_id = :issue_id
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"issue_id": issue_id})
            row = cur.fetchone()
            if not row:
                return json_error("Issue not found", 404)
            return json_success(serialize_rows(cur, [row])[0])


@app.route("/api/issues", methods=["POST"])
def create_issue():
    data = request.get_json(silent=True) or {}
    book_id = data.get("book_id")
    member_id = data.get("member_id")
    staff_id = data.get("staff_id")
    due_date = data.get("due_date", "").strip()

    if not book_id or not member_id or not staff_id or not due_date:
        return json_error("Book, member, staff and due date are required")

    try:
        book_id = int(book_id)
        member_id = int(member_id)
        staff_id = int(staff_id)
        parsed_due = datetime.fromisoformat(due_date).date()
    except (TypeError, ValueError):
        return json_error("Invalid numeric values or due date format")

    if parsed_due < date.today():
        return json_error("Due date must be today or later")

    if DEMO_MODE:
        return json_success({"issue_id": 999, "demo": True}, "Book issued (demo mode)")

    issue_id = db.next_id("ISSUE", "issue_id")

    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.callproc("issue_book", [issue_id, book_id, member_id, staff_id, due_date])
            conn.commit()
            return json_success({"issue_id": issue_id}, "Book issued successfully")
        except oracledb.DatabaseError as exc:
            conn.rollback()
            error_obj, = exc.args
            message = error_obj.message if hasattr(error_obj, "message") else str(exc)
            if "-20005" in message or "No copies available" in message:
                return json_error("No copies of this book are available", 409)
            if "ORA-02291" in message:
                return json_error("Selected book, member or staff does not exist", 400)
            return json_error(f"Could not issue book: {message}", 500)


@app.route("/api/issues/<int:issue_id>/return", methods=["POST"])
def return_issue(issue_id: int):
    if DEMO_MODE:
        return json_success({
            "issue_id": issue_id,
            "return_date": datetime.now().isoformat(),
            "fine_amount": 25,
            "demo": True,
        }, "Book returned (demo mode)")

    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.callproc("return_book", [issue_id])
            conn.commit()

            # Fetch the updated issue and any fine created for this issue.
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT issue_id, book_id, member_id, staff_id,
                           issue_date, due_date, return_date, status
                    FROM ISSUE WHERE issue_id = :issue_id
                """, {"issue_id": issue_id})
                issue_row = cur.fetchone()

                cur.execute("""
                    SELECT fine_id, amount, paid_status
                    FROM FINE WHERE issue_id = :issue_id
                """, {"issue_id": issue_id})
                fine_row = cur.fetchone()

            result = {
                "issue": serialize_rows(cur, [issue_row])[0] if issue_row else None,
                "fine": serialize_rows(cur, [fine_row])[0] if fine_row else None,
            }
            return json_success(result, "Book returned successfully")
        except oracledb.DatabaseError as exc:
            conn.rollback()
            error_obj, = exc.args
            message = error_obj.message if hasattr(error_obj, "message") else str(exc)
            if "-20003" in message or "already returned" in message:
                return json_error("This book has already been returned", 409)
            if "-20004" in message or "not found" in message:
                return json_error("Issue ID not found", 404)
            return json_error(f"Could not return book: {message}", 500)


# ---------------------------------------------------------------------------
# Fines
# ---------------------------------------------------------------------------

@app.route("/api/fines", methods=["GET"])
def list_fines():
    if DEMO_MODE:
        from mock_data import FINES
        return json_success(FINES)

    status_filter = request.args.get("status", "").strip()
    sql = """
        SELECT f.fine_id, f.issue_id, f.amount, f.paid_status,
               m.name AS member_name, b.title AS book_title
        FROM FINE f
        JOIN ISSUE i ON i.issue_id = f.issue_id
        JOIN MEMBER m ON m.member_id = i.member_id
        JOIN BOOK b ON b.book_id = i.book_id
        WHERE 1=1
    """
    params = {}
    if status_filter in ("Paid", "Unpaid"):
        sql += " AND f.paid_status = :status"
        params["status"] = status_filter
    sql += " ORDER BY f.fine_id"

    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return json_success(serialize_rows(cur, rows))


@app.route("/api/fines/summary", methods=["GET"])
def fines_summary():
    if DEMO_MODE:
        from mock_data import FINE_SUMMARY
        return json_success(FINE_SUMMARY)

    sql = """
        SELECT paid_status, SUM(amount) AS total
        FROM FINE
        GROUP BY paid_status
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            result = {"Paid": 0, "Unpaid": 0}
            for row in rows:
                result[row[0]] = serialize_value(row[1])
            return json_success(result)


@app.route("/api/fines/<int:fine_id>/payment-status", methods=["PUT"])
def update_fine_payment(fine_id: int):
    data = request.get_json(silent=True) or {}
    paid_status = data.get("paid_status", "").strip()

    if paid_status not in ("Paid", "Unpaid"):
        return json_error("Payment status must be Paid or Unpaid")

    if DEMO_MODE:
        return json_success({"demo": True}, "Fine payment status updated (demo mode)")

    sql = "UPDATE FINE SET paid_status = :paid_status WHERE fine_id = :fine_id"
    with db.get_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, {"paid_status": paid_status, "fine_id": fine_id})
                if cur.rowcount == 0:
                    return json_error("Fine not found", 404)
            conn.commit()
            return json_success(message="Fine payment status updated")
        except oracledb.Error as exc:
            conn.rollback()
            return json_error(f"Database error: {exc}", 500)


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

REPORTS = {
    "available-books": """
        SELECT title, available_copies
        FROM BOOK
        WHERE available_copies > 0
    """,
    "books-by-category": """
        SELECT c.category_name, COUNT(b.book_id) AS total_titles,
               NVL(SUM(b.total_copies), 0) AS total_copies,
               NVL(SUM(b.available_copies), 0) AS available_copies
        FROM CATEGORY c
        LEFT JOIN BOOK b ON b.category_id = c.category_id
        GROUP BY c.category_name
    """,
    "current-issues": """
        SELECT i.issue_id, m.name AS member_name, b.title AS book_title,
               i.issue_date, i.due_date, s.name AS staff_name
        FROM ISSUE i
        JOIN MEMBER m ON m.member_id = i.member_id
        JOIN BOOK b ON b.book_id = i.book_id
        LEFT JOIN STAFF s ON s.staff_id = i.staff_id
        WHERE i.status = 'Issued'
    """,
    "overdue": """
        SELECT i.issue_id, m.name AS member_name, b.title AS book_title,
               i.due_date, TRUNC(SYSDATE) - TRUNC(i.due_date) AS overdue_days
        FROM ISSUE i
        JOIN MEMBER m ON m.member_id = i.member_id
        JOIN BOOK b ON b.book_id = i.book_id
        WHERE i.status = 'Issued' AND i.due_date < SYSDATE
    """,
    "issue-history": """
        SELECT i.issue_id, m.name AS member_name, b.title AS book_title,
               i.issue_date, i.due_date, i.return_date, i.status
        FROM ISSUE i
        JOIN MEMBER m ON m.member_id = i.member_id
        JOIN BOOK b ON b.book_id = i.book_id
    """,
    "borrowing-count": """
        SELECT m.member_id, m.name, COUNT(i.issue_id) AS borrow_count
        FROM MEMBER m
        LEFT JOIN ISSUE i ON i.member_id = m.member_id
        GROUP BY m.member_id, m.name
    """,
    "inactive-members": """
        SELECT m.member_id, m.name, m.email
        FROM MEMBER m
        WHERE NOT EXISTS (
            SELECT 1 FROM ISSUE i WHERE i.member_id = m.member_id
        )
    """,
    "fine-summary": """
        SELECT paid_status, SUM(amount) AS total, COUNT(*) AS count
        FROM FINE
        GROUP BY paid_status
    """,
    "unpaid-fines": """
        SELECT f.fine_id, m.name AS member_name, b.title AS book_title, f.amount
        FROM FINE f
        JOIN ISSUE i ON i.issue_id = f.issue_id
        JOIN MEMBER m ON m.member_id = i.member_id
        JOIN BOOK b ON b.book_id = i.book_id
        WHERE f.paid_status = 'Unpaid'
    """,
    "staff-activity": """
        SELECT s.staff_id, s.name, COUNT(i.issue_id) AS issues_handled
        FROM STAFF s
        LEFT JOIN ISSUE i ON i.staff_id = s.staff_id
        GROUP BY s.staff_id, s.name
    """,
    "issued-books": """
        SELECT title, total_copies, available_copies,
               total_copies - available_copies AS issued_copies
        FROM BOOK
        WHERE available_copies < total_copies
    """,
    "books-authors-categories": """
        SELECT b.title, a.author_name, c.category_name, b.price
        FROM BOOK b
        JOIN AUTHOR a ON a.author_id = b.author_id
        JOIN CATEGORY c ON c.category_id = b.category_id
    """,
}


@app.route("/api/reports/<report_name>", methods=["GET"])
def report(report_name: str):
    if report_name not in REPORTS:
        return json_error("Report not found", 404)

    if DEMO_MODE:
        from mock_data import REPORT_DATA
        return json_success(REPORT_DATA.get(report_name, []))

    sql = REPORTS[report_name]
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            return json_success(serialize_rows(cur, rows))


# ---------------------------------------------------------------------------
# Database logic demonstration
# ---------------------------------------------------------------------------

@app.route("/api/database-logic/objects", methods=["GET"])
def database_logic_objects():
    objects = [
        {
            "type": "procedure",
            "name": "issue_book",
            "purpose": "Insert a new ISSUE row. The trigger trg_issue_insert validates stock and decrements available_copies.",
            "tables": ["ISSUE", "BOOK"],
            "invoked_by": "Issue Book form",
        },
        {
            "type": "procedure",
            "name": "return_book",
            "purpose": "Mark an active issue as Returned. The trigger trg_issue_return restores one available copy. A fine is created when overdue.",
            "tables": ["ISSUE", "BOOK", "FINE"],
            "invoked_by": "Return Book workflow",
        },
        {
            "type": "function",
            "name": "overdue_days",
            "purpose": "Return the number of late calendar days between due date and return date.",
            "tables": [],
            "invoked_by": "calculate_fine",
        },
        {
            "type": "function",
            "name": "calculate_fine",
            "purpose": "Calculate fine amount at INR 5 per overdue day.",
            "tables": [],
            "invoked_by": "return_book procedure",
        },
        {
            "type": "trigger",
            "name": "trg_issue_insert",
            "purpose": "Before inserting an ISSUE row, reject the insert if no copies are available and decrement BOOK.available_copies.",
            "tables": ["ISSUE", "BOOK"],
            "invoked_by": "INSERT on ISSUE",
        },
        {
            "type": "trigger",
            "name": "trg_issue_return",
            "purpose": "When an ISSUE status changes from Issued to Returned, increment BOOK.available_copies by one.",
            "tables": ["ISSUE", "BOOK"],
            "invoked_by": "UPDATE of status on ISSUE",
        },
        {
            "type": "cursor",
            "name": "overdue_cursor",
            "purpose": "Anonymous PL/SQL cursor that iterates over currently issued, overdue transactions.",
            "tables": ["ISSUE", "MEMBER", "BOOK"],
            "invoked_by": "PL/SQL Demonstration page",
        },
    ]
    return json_success(objects)


@app.route("/api/database-logic/overdue-demonstration", methods=["POST"])
def overdue_demonstration():
    """Run the existing overdue_cursor logic and return the rows it would print."""
    if DEMO_MODE:
        from mock_data import OVERDUE_DEMO_ROWS
        return json_success(OVERDUE_DEMO_ROWS)

    plsql = """
        DECLARE
            CURSOR overdue_cursor IS
                SELECT i.issue_id, m.name, b.title, i.due_date
                FROM ISSUE i
                JOIN MEMBER m ON m.member_id = i.member_id
                JOIN BOOK b ON b.book_id = i.book_id
                WHERE i.status = 'Issued'
                  AND i.due_date < SYSDATE;
        BEGIN
            OPEN overdue_cursor;
        END;
    """
    query = """
        SELECT i.issue_id, m.name AS member_name, b.title AS book_title, i.due_date
        FROM ISSUE i
        JOIN MEMBER m ON m.member_id = i.member_id
        JOIN BOOK b ON b.book_id = i.book_id
        WHERE i.status = 'Issued'
          AND i.due_date < SYSDATE
    """
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(plsql)
            cur.execute(query)
            rows = cur.fetchall()
            return json_success(serialize_rows(cur, rows))


# ---------------------------------------------------------------------------
# Static SPA fallback
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>", methods=["GET"])
def static_files(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(host=host, port=port, debug=debug)
