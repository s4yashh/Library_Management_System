# Database Integration Guide

## Existing Schema

The Oracle schema was created during Review 2 and contains seven related tables.

### Tables

| Table | Purpose | Key Constraints |
|-------|---------|-----------------|
| `AUTHOR` | Writers of books | `author_id` PK; `author_name` NOT NULL |
| `CATEGORY` | Book genres/subjects | `category_id` PK; `category_name` UNIQUE, NOT NULL |
| `BOOK` | Book titles and copy counts | `book_id` PK; FKs to AUTHOR and CATEGORY; CHECK price > 0; CHECK available_copies <= total_copies |
| `MEMBER` | Library borrowers | `member_id` PK; `email` UNIQUE, NOT NULL; CHECK membership_type IN ('Student','Faculty','General') |
| `STAFF` | Library employees | `staff_id` PK; `email` UNIQUE |
| `ISSUE` | Borrowing transactions | `issue_id` PK; FKs to BOOK, MEMBER, STAFF; CHECK status IN ('Issued','Returned') |
| `FINE` | Late-return fines | `fine_id` PK; FK to ISSUE (UNIQUE); CHECK paid_status IN ('Paid','Unpaid') |

### Referential Integrity

```
BOOK.author_id      → AUTHOR.author_id
BOOK.category_id    → CATEGORY.category_id
ISSUE.book_id       → BOOK.book_id
ISSUE.member_id     → MEMBER.member_id
ISSUE.staff_id      → STAFF.staff_id
FINE.issue_id       → ISSUE.issue_id
```

## Existing PL/SQL Objects

### Procedures

#### `issue_book(p_issue_id, p_book_id, p_member_id, p_staff_id, p_due_date)`

- **Purpose:** Insert a new ISSUE row.
- **Tables affected:** `ISSUE` (insert), `BOOK` (updated by trigger).
- **Invoked by:** `POST /api/issues`.
- **Expected result:** A new active issue is created and the trigger decrements `BOOK.available_copies`.

#### `return_book(p_issue_id)`

- **Purpose:** Mark an active issue as returned and create a fine if overdue.
- **Tables affected:** `ISSUE` (update), `BOOK` (updated by trigger), `FINE` (conditional insert).
- **Invoked by:** `POST /api/issues/<id>/return`.
- **Expected result:** Issue status becomes `Returned`, return_date is set, available copy is restored, and a fine row is inserted only when `calculate_fine` > 0.

### Functions

#### `overdue_days(p_due_date, p_return_date)`

- **Purpose:** Returns `GREATEST(TRUNC(p_return_date) - TRUNC(p_due_date), 0)`.
- **Invoked by:** `calculate_fine`.

#### `calculate_fine(p_due_date, p_return_date)`

- **Purpose:** Returns `overdue_days(...) * 5` (INR 5 per overdue day).
- **Invoked by:** `return_book` procedure.
- **UI exposure:** Fine amount is displayed on the Fines page and in the return success message.

### Triggers

#### `trg_issue_insert`

- **Type:** `BEFORE INSERT ON ISSUE FOR EACH ROW`
- **Purpose:** Reject an issue if the selected book has no available copies; otherwise decrement `available_copies`.
- **UI operation:** Issue Book form.

#### `trg_issue_return`

- **Type:** `BEFORE UPDATE OF status ON ISSUE FOR EACH ROW`
- **Purpose:** When `status` changes from `Issued` to `Returned`, increment `BOOK.available_copies`.
- **UI operation:** Return Book workflow.

### Cursor

#### `overdue_cursor`

- **Form:** Anonymous PL/SQL block in `sql/procedures.sql`.
- **Purpose:** Iterate over active issues where `due_date < SYSDATE` and print member, book and due date.
- **Demonstration:** Database Logic page runs equivalent SQL and displays the rows the cursor would process.

## SQL Queries Used by Reports

| Report | Endpoint | SQL Concepts |
|--------|----------|--------------|
| Available books | `/api/reports/available-books` | Simple SELECT with WHERE |
| Books by category | `/api/reports/books-by-category` | LEFT JOIN, GROUP BY, aggregation |
| Current issues | `/api/reports/current-issues` | JOINs, WHERE |
| Overdue issues | `/api/reports/overdue` | JOINs, date comparison |
| Complete issue history | `/api/reports/issue-history` | JOINs |
| Borrowing count per member | `/api/reports/borrowing-count` | LEFT JOIN, GROUP BY |
| Inactive members | `/api/reports/inactive-members` | NOT EXISTS subquery |
| Fine summary | `/api/reports/fine-summary` | GROUP BY, aggregation |
| Unpaid fines | `/api/reports/unpaid-fines` | Multi-table JOIN, WHERE |
| Staff activity | `/api/reports/staff-activity` | LEFT JOIN, GROUP BY |
| Books with issued copies | `/api/reports/issued-books` | Computed column |
| Books, authors and categories | `/api/reports/books-authors-categories` | Multi-table JOIN |

## ID Generation Strategy

The existing schema uses `NUMBER` primary keys without sequences or identity columns. For new rows created through the UI, the application generates IDs with:

```sql
SELECT NVL(MAX(<id_column>), 0) + 1 FROM <table>
```

This matches the existing Review 2 implementation (e.g., `SELECT NVL(MAX(fine_id), 0) + 1 FROM FINE` inside `return_book`). It is simple and sufficient for a lab demonstration, but it is not safe under high concurrency.

## Known Limitations

1. **Concurrency:** The `MAX(id)+1` strategy can produce duplicate IDs if two inserts happen simultaneously. For a production system, switch to Oracle `SEQUENCE` or `IDENTITY` columns.
2. **Trigger race condition:** `trg_issue_insert` does a `SELECT ... INTO` without `FOR UPDATE`, so two simultaneous issues of the last copy could both pass the check before either updates the count. A production fix would use `SELECT ... FOR UPDATE` on `BOOK` inside the trigger.
3. **No user authentication:** The application is designed for a trusted localhost demonstration. Adding real authentication would require password hashing and session management.
4. **Demo mode writes are not persisted:** When `DEMO_MODE=true`, POST/PUT/DELETE operations return simulated success messages but do not change the mock data.

## UI Operation → Database Object Mapping

| UI Operation | Backend Route | Database Object(s) |
|--------------|---------------|-------------------|
| Register member | `POST /api/members` | `INSERT INTO MEMBER` |
| Add book | `POST /api/books` | `INSERT INTO BOOK` |
| Issue book | `POST /api/issues` | `issue_book` procedure, `trg_issue_insert` |
| Return book | `POST /api/issues/<id>/return` | `return_book` procedure, `calculate_fine`, `trg_issue_return` |
| Pay fine | `PUT /api/fines/<id>/payment-status` | `UPDATE FINE` |
| Overdue report | `POST /api/database-logic/overdue-demonstration` | `overdue_cursor` equivalent query |
