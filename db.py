"""Oracle database connection helper for the Library Management System."""

import os
from contextlib import contextmanager
from typing import Any, Optional

import oracledb
from dotenv import load_dotenv

load_dotenv()

ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_CONNECT_STRING = os.getenv("ORACLE_CONNECT_STRING", "localhost:1521/XEPDB1")
ORACLE_MODE = os.getenv("ORACLE_MODE", "thin").lower()

_pool: Optional[oracledb.ConnectionPool] = None
_last_error: Optional[str] = None


def _init_pool() -> Optional[oracledb.ConnectionPool]:
    """Create a connection pool using environment variables."""
    global _pool, _last_error
    if _pool is not None:
        return _pool

    if not ORACLE_USER or not ORACLE_PASSWORD or not ORACLE_CONNECT_STRING:
        _last_error = "Oracle credentials are not configured. Set ORACLE_USER, ORACLE_PASSWORD and ORACLE_CONNECT_STRING."
        return None

    try:
        if ORACLE_MODE == "thick":
            oracledb.init_oracle_client()

        _pool = oracledb.create_pool(
            user=ORACLE_USER,
            password=ORACLE_PASSWORD,
            dsn=ORACLE_CONNECT_STRING,
            min=1,
            max=5,
            increment=1,
        )
        _last_error = None
        return _pool
    except oracledb.Error as exc:
        _last_error = f"Oracle connection error: {exc}"
        return None
    except Exception as exc:
        _last_error = f"Unexpected error while creating pool: {exc}"
        return None


@contextmanager
def get_connection():
    """Yield a managed Oracle connection with automatic cleanup."""
    pool = _init_pool()
    if pool is None:
        raise ConnectionError(_last_error or "Oracle pool not available")

    conn = None
    try:
        conn = pool.acquire()
        yield conn
    finally:
        if conn is not None:
            try:
                conn.close()
            except oracledb.Error:
                pass


def db_status() -> dict[str, Any]:
    """Return the current database connection status."""
    pool = _init_pool()
    if pool is None:
        return {
            "connected": False,
            "message": _last_error or "Oracle pool not available",
        }
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT SYSDATE FROM DUAL")
                row = cur.fetchone()
                return {
                    "connected": True,
                    "message": "Connected to Oracle",
                    "server_date": row[0].isoformat() if row and row[0] else None,
                }
    except Exception as exc:
        return {"connected": False, "message": str(exc)}


def next_id(table_name: str, id_column: str) -> int:
    """Return the next monotonic ID for a table using MAX(id)+1.

    Note: This strategy is simple and matches the existing schema, but it is
    not safe under high concurrency. For a production system with many
    concurrent inserts, use an Oracle SEQUENCE or IDENTITY column.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT NVL(MAX({id_column}), 0) + 1 FROM {table_name}",
            )
            row = cur.fetchone()
            return int(row[0]) if row else 1
