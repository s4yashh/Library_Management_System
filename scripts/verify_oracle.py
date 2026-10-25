"""Verify Oracle connectivity and required database objects."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

import db

REQUIRED_TABLES = ["AUTHOR", "CATEGORY", "BOOK", "MEMBER", "STAFF", "ISSUE", "FINE"]
REQUIRED_PROCEDURES = ["ISSUE_BOOK", "RETURN_BOOK"]
REQUIRED_FUNCTIONS = ["OVERDUE_DAYS", "CALCULATE_FINE"]
REQUIRED_TRIGGERS = ["TRG_ISSUE_INSERT", "TRG_ISSUE_RETURN"]


def check_table(conn, table_name):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM user_tables WHERE table_name = :name",
            {"name": table_name.upper()},
        )
        return cur.fetchone()[0] > 0


def check_object(conn, object_name, object_type):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM user_objects
            WHERE object_name = :name AND object_type = :type
            """,
            {"name": object_name.upper(), "type": object_type.upper()},
        )
        return cur.fetchone()[0] > 0


def main():
    status = db.db_status()
    if not status["connected"]:
        print(f"ERROR: Could not connect to Oracle: {status['message']}")
        sys.exit(1)

    print(f"Connected to Oracle. Server date: {status.get('server_date')}")

    with db.get_connection() as conn:
        missing = []

        for table in REQUIRED_TABLES:
            if not check_table(conn, table):
                missing.append(f"Table {table}")
            else:
                print(f"OK: Table {table}")

        for proc in REQUIRED_PROCEDURES:
            if not check_object(conn, proc, "PROCEDURE"):
                missing.append(f"Procedure {proc}")
            else:
                print(f"OK: Procedure {proc}")

        for func in REQUIRED_FUNCTIONS:
            if not check_object(conn, func, "FUNCTION"):
                missing.append(f"Function {func}")
            else:
                print(f"OK: Function {func}")

        for trig in REQUIRED_TRIGGERS:
            if not check_object(conn, trig, "TRIGGER"):
                missing.append(f"Trigger {trig}")
            else:
                print(f"OK: Trigger {trig}")

    if missing:
        print("\nMISSING OBJECTS:")
        for item in missing:
            print(f"  - {item}")
        print("\nRun sql/schema.sql and sql/procedures.sql to create missing objects.")
        sys.exit(1)

    print("\nAll required objects are present.")


if __name__ == "__main__":
    main()
