# LibraryDesk Architecture

## Overview

LibraryDesk is a single-page web application that demonstrates end-to-end database transactions for a Library Management System. It connects an Oracle Database (created for DBMS Lab Reviews 1 and 2) to a modern administrative UI through a Flask REST API.

## High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
│  SPA built with HTML5, CSS3 and vanilla JavaScript           │
│  - Sidebar navigation, tables, forms, modals, toasts         │
│  - Fetch API calls to /api/*                                 │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP / JSON
┌───────────────────────▼─────────────────────────────────────┐
│                     Flask Backend                            │
│  - app.py: API routes, validation, transaction boundaries    │
│  - db.py: Oracle connection pool helper                      │
│  - mock_data.py: demo-mode fallback data                     │
└───────────────────────┬─────────────────────────────────────┘
                        │ python-oracledb (Thin mode)
┌───────────────────────▼─────────────────────────────────────┐
│                   Oracle Database                            │
│  - 7 tables: AUTHOR, CATEGORY, BOOK, MEMBER, STAFF, ISSUE,   │
│    FINE                                                      │
│  - Stored procedures: issue_book, return_book                │
│  - Functions: overdue_days, calculate_fine                   │
│  - Triggers: trg_issue_insert, trg_issue_return              │
└─────────────────────────────────────────────────────────────┘
```

## Frontend Architecture

### Files

- `static/index.html` — application shell with sidebar, topbar, modal and toast containers.
- `static/css/styles.css` — design system (colors, typography, cards, tables, forms, responsive breakpoints).
- `static/js/api.js` — thin Fetch wrapper for every backend endpoint.
- `static/js/components.js` — reusable helpers for tables, forms, modals, toasts, CSV export, formatting.
- `static/js/pages.js` — page renderers: Dashboard, Books, Members, Authors, Categories, Issue, Return, Issues, Fines, Reports, Database Logic.
- `static/js/app.js` — router, sidebar state, database status indicator.

### Routing

Navigation is hash-based (`#/books`, `#/members`). `app.js` reads `window.location.hash`, updates the active sidebar item, and calls the matching renderer from `Pages`. Each renderer asynchronously fetches data and returns HTML into `#content`.

### State Management

There is no global state framework. Each page stores lightweight filters in its own object (e.g., `Pages.books.filters`). Shared selections (such as the book chosen in the Issue form) are temporarily stored in `pageState`.

## Backend Architecture

### Files

- `app.py` — Flask application with all REST endpoints, request validation, error handling and JSON serialization.
- `db.py` — Oracle connection pool initialisation and context-managed connection helper.
- `mock_data.py` — static sample data returned when `DEMO_MODE=true`.

### Request Flow

1. Browser sends a request to `/api/<resource>`.
2. Flask route validates the input and returns a 400 error if invalid.
3. If `DEMO_MODE` is enabled, the route returns the corresponding mock data.
4. Otherwise `db.get_connection()` acquires an Oracle connection from the pool.
5. The route executes parameterised SQL or calls a stored procedure/function.
6. On success the transaction is committed; on failure it is rolled back.
7. Results are serialised (dates → ISO strings, Decimals → floats) and returned as JSON.

### Transaction Flow

#### Issue Book

```
POST /api/issues
  ↓ validate input
  ↓ generate issue_id = MAX(issue_id)+1
  ↓ call issue_book(issue_id, book_id, member_id, staff_id, due_date)
  ↓ Oracle INSERT INTO ISSUE
  ↓ TRIGGER trg_issue_insert:
       SELECT available_copies FROM BOOK FOR UPDATE
       IF available_copies <= 0 THEN raise error
       UPDATE BOOK SET available_copies = available_copies - 1
  ↓ COMMIT
```

The application never decrements `available_copies` itself; the trigger owns stock management.

#### Return Book

```
POST /api/issues/<id>/return
  ↓ call return_book(issue_id)
  ↓ Oracle SELECT due_date, status FROM ISSUE WHERE issue_id = ... FOR UPDATE
       IF status = 'Returned' THEN raise error
  ↓ v_fine := calculate_fine(due_date, SYSDATE)
  ↓ UPDATE ISSUE SET return_date = SYSDATE, status = 'Returned'
  ↓ TRIGGER trg_issue_return:
       IF old.status='Issued' AND new.status='Returned'
       THEN UPDATE BOOK SET available_copies = available_copies + 1
  ↓ IF v_fine > 0 THEN INSERT INTO FINE(...)
  ↓ COMMIT
```

#### Fine Payment

```
PUT /api/fines/<id>/payment-status
  ↓ validate paid_status in ('Paid','Unpaid')
  ↓ UPDATE FINE SET paid_status = :paid_status WHERE fine_id = :fine_id
  ↓ COMMIT
```

The amount is not recalculated.

## Oracle Connection Flow

1. Environment variables are read at startup:
   - `ORACLE_USER`
   - `ORACLE_PASSWORD`
   - `ORACLE_CONNECT_STRING` (e.g., `localhost:1521/XEPDB1`)
   - `ORACLE_MODE` (`thin` or `thick`)
2. `db._init_pool()` creates an `oracledb` connection pool.
3. Each route uses `with db.get_connection() as conn:` to acquire and release a connection.
4. Explicit `conn.commit()` or `conn.rollback()` manages transaction boundaries.

## Demo Mode

When `DEMO_MODE=true` (environment variable) the backend bypasses Oracle and returns sample data from `mock_data.py`. This lets the UI be demonstrated and tested without a live database. The frontend shows a clearly labelled demo banner.

## Security Notes

- Parameterised queries and stored procedure calls prevent SQL injection.
- Stack traces and credentials are never returned to the client.
- There is no generic SQL execution endpoint.
- Write operations are validated server-side; the frontend validation is for UX only.
- The application binds to `127.0.0.1` by default for localhost demonstrations.
