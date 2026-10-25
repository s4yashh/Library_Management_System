# LibraryDesk — Library Management System

A complete, interactive Library Management System web application for the VIT Database Systems Lab Review 3. It integrates an existing Oracle Database implementation ( seven tables, stored procedures, functions, triggers and a cursor ) into a modern administrative dashboard.

## Features

- **Dashboard:** Live statistics from Oracle — titles, copies, issued books, members, overdue issues, fines.
- **Books Management:** Add, edit, delete and filter books by title, category and availability.
- **Members Management:** Register, edit, delete members and view borrowing history.
- **Authors & Categories:** Manage authors and categories with linked book counts.
- **Issue Book:** Transaction form that calls the existing `issue_book` procedure and relies on the stock trigger.
- **Return Book:** Workflow that calls the existing `return_book` procedure and displays any generated fine.
- **Issue History:** Searchable, filterable transaction log.
- **Fine Management:** Mark fines as paid; view paid/unpaid totals.
- **Reports:** 12 database-driven reports with CSV export.
- **Database Logic page:** Explains and demonstrates existing PL/SQL objects.
- **Demo mode:** UI can be tested without a live Oracle connection.

## Architecture

```
Browser (HTML/CSS/JS SPA)
    ↓ HTTP / JSON
Flask Backend (Python)
    ↓ python-oracledb (Thin mode)
Oracle Database
```

Detailed architecture is in [docs/architecture.md](docs/architecture.md).

## Prerequisites

- Python 3.10 or newer
- Oracle Database (local, remote or containerized) with the schema installed
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:s4yashh/Library_Management_System.git
   cd Library_Management_System
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Oracle credentials:
   ```ini
   ORACLE_USER=your_username
   ORACLE_PASSWORD=your_password
   ORACLE_CONNECT_STRING=localhost:1521/XEPDB1
   FLASK_SECRET_KEY=any-random-string
   ```

3. **Optional — Demo mode without Oracle:**
   ```ini
   DEMO_MODE=true
   ```
   When demo mode is active the UI shows a banner and returns sample data.

## Database Setup

Run the following scripts in Oracle SQL Developer or SQL*Plus in order:

1. `sql/schema.sql` — create tables and constraints.
2. `sql/sample_data.sql` — insert sample records.
3. `sql/procedures.sql` — create procedures, functions, triggers and cursor.

> These scripts are safe to re-run only if you want to reset the database, because they recreate objects. For a fresh install they are required; for an existing Review 2 database only verify that the objects match.

## Running the Application

```bash
source venv/bin/activate
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Running Tests

```bash
source venv/bin/activate
DEMO_MODE=true python -m unittest discover -s tests -v
```

To run live Oracle integration tests, set real credentials and run:

```bash
DEMO_MODE=false python -m unittest tests.test_app.LiveOracleTests -v
```

## API Endpoint Summary

| Resource | Endpoints |
|----------|-----------|
| Health | `GET /api/health`, `GET /api/status` |
| Dashboard | `GET /api/dashboard/stats`, `/api/dashboard/recent-issues`, `/api/dashboard/overdue` |
| Books | `GET /api/books`, `GET /api/books/<id>`, `POST /api/books`, `PUT /api/books/<id>`, `DELETE /api/books/<id>` |
| Members | `GET /api/members`, `GET /api/members/<id>`, `POST /api/members`, `PUT /api/members/<id>`, `DELETE /api/members/<id>`, `GET /api/members/<id>/history` |
| Authors | `GET /api/authors`, `POST /api/authors`, `PUT /api/authors/<id>`, `DELETE /api/authors/<id>` |
| Categories | `GET /api/categories`, `POST /api/categories`, `PUT /api/categories/<id>`, `DELETE /api/categories/<id>` |
| Staff | `GET /api/staff` |
| Issues | `GET /api/issues`, `GET /api/issues/<id>`, `POST /api/issues`, `POST /api/issues/<id>/return` |
| Fines | `GET /api/fines`, `GET /api/fines/summary`, `PUT /api/fines/<id>/payment-status` |
| Reports | `GET /api/reports/<report_name>` |
| Database Logic | `GET /api/database-logic/objects`, `POST /api/database-logic/overdue-demonstration` |

## Database Object Integration

| UI Operation | Oracle Object |
|--------------|---------------|
| Issue Book | `issue_book` procedure + `trg_issue_insert` trigger |
| Return Book | `return_book` procedure + `calculate_fine` function + `trg_issue_return` trigger |
| Overdue report/cursor demo | PL/SQL `SYS_REFCURSOR` over the Review 2 overdue query |

Full details are in [docs/database-integration.md](docs/database-integration.md).

## Review 3 Demonstration

Step-by-step demo script and verification queries are in [docs/demo-checklist.md](docs/demo-checklist.md).

The final written report is [docs/review-3-report.md](docs/review-3-report.md) and its PDF copy is [review3.pdf](review3.pdf). It distinguishes expected sample results from live Oracle output. Before presenting, run `python scripts/verify_oracle.py` with your Oracle credentials and capture your own transaction and report results.

## Viva Questions

A list of likely viva questions with answers is in [docs/review-3-viva.md](docs/review-3-viva.md).

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'oracledb'` | Activate venv and run `pip install -r requirements.txt` |
| Oracle connection fails | Verify `.env` values, network, service name/SID and that the listener is running |
| `python-oracledb` install fails | Check Python version compatibility; use Thin mode (`ORACLE_MODE=thin`) |
| Book issue fails with "No copies available" | Return an active copy or increase `total_copies` |
| Foreign-key error on delete | Remove child records (issues/fines) before deleting parents |
| UI shows empty data | Check the browser console for API errors and confirm database status |

## License

This is an academic project for educational purposes.

## Author

s4yashh
