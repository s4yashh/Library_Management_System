# Review 3 Demonstration Checklist

## Pre-Demo Preparation

1. Ensure Oracle is running and the schema from `sql/schema.sql`, sample data from `sql/sample_data.sql` and procedures/triggers from `sql/procedures.sql` are installed.
2. Copy `.env.example` to `.env` and fill in real Oracle credentials.
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Start the backend:
   ```bash
   python app.py
   ```
5. Open the port configured by `FLASK_PORT` in `.env` (on this machine, `http://127.0.0.1:5001`).
6. Run `python scripts/verify_oracle.py` and confirm the database status indicator shows **Oracle connected**.

## Sample Records to Verify

Run these queries in SQL Developer or SQL*Plus to confirm the starting state:

```sql
-- Total titles and copies
SELECT COUNT(*) AS total_titles, SUM(total_copies) AS total_copies, SUM(available_copies) AS available_copies FROM BOOK;

-- Active issues
SELECT issue_id, book_id, member_id, due_date, status FROM ISSUE WHERE status = 'Issued';

-- Unpaid fines
SELECT fine_id, issue_id, amount, paid_status FROM FINE WHERE paid_status = 'Unpaid';

-- Overdue active issues
SELECT i.issue_id, m.name, b.title, i.due_date
FROM ISSUE i JOIN MEMBER m ON m.member_id = i.member_id
JOIN BOOK b ON b.book_id = i.book_id
WHERE i.status = 'Issued' AND TRUNC(i.due_date) < TRUNC(SYSDATE);
```

## Scenario 1: Register a Member

**Steps:**
1. Navigate to **Members** → click **Register Member**.
2. Enter name, email, phone and select membership type (Student/Faculty/General).
3. Click **Register Member**.

**Expected:**
- Success toast appears.
- New member appears in the members table.

**Verify in Oracle:**
```sql
SELECT * FROM MEMBER WHERE email = '<entered_email>';
```

**Cleanup (optional):**
```sql
DELETE FROM MEMBER WHERE email = '<entered_email>';
COMMIT;
```

## Scenario 2: Add a Catalog Book

**Steps:**
1. Navigate to **Books** → **Add Book**.
2. Choose an existing author and category. Enter a distinctive demo title, price ₹250 and total copies 2.
3. Save the book and note its generated Book ID.

**Expected:** The new title appears with total copies 2 and available copies 2. It also appears in **Available Books** and raises its category's book count.

**Verify in Oracle:**
```sql
SELECT book_id, title, author_id, category_id, total_copies, available_copies
FROM BOOK WHERE book_id = <book_id>;
```

**Viva talking points:** `BOOK.author_id` and `BOOK.category_id` are foreign keys. The database checks positive price and valid copy counts.

## Scenario 3: Issue a Book

**Steps:**
1. Navigate to **Issue Book**.
2. Select the new member, the new two-copy book, a staff member and a due date today or later.
3. Note the available copy count displayed.
4. Click **Issue Book**.

**Expected:**
- Success toast shows the new Issue ID.
- The new book's available copies decrease from 2 to 1.
- A new row appears in Issue History with status **Issued**.

**Verify in Oracle:**
```sql
-- Replace <book_id> and <issue_id>
SELECT available_copies FROM BOOK WHERE book_id = <book_id>;
SELECT * FROM ISSUE WHERE issue_id = <issue_id>;
```

**Viva talking points:**
- Explain that the backend calls the `issue_book` procedure.
- Explain that `trg_issue_insert` validates stock and decrements `available_copies` automatically.
- The application does not decrement the count itself.

## Scenario 4: Return an Overdue Book

**Prerequisite:** An active issue with a due date before today. At the 26 October 2026 snapshot, sample issues 11–15 were overdue. The new issue from Scenario 3 has a future due date, so choose an older sample issue here.

**Steps:**
1. Navigate to **Return Book**.
2. Find an overdue active issue (look for past due date).
3. Click **Return** and confirm.

**Expected:**
- Success toast appears.
- Issue status changes to **Returned** and return date is set.
- The book's available copies increase by 1.
- A fine row is created with amount `overdue_days * 5`.

**Verify in Oracle:**
```sql
SELECT status, return_date FROM ISSUE WHERE issue_id = <issue_id>;
SELECT available_copies FROM BOOK WHERE book_id = <book_id>;
SELECT * FROM FINE WHERE issue_id = <issue_id>;
```

**Viva talking points:**
- Explain `return_book`, `calculate_fine` and `trg_issue_return`.
- Explain why the trigger only fires on `Issued → Returned` transition.
- Show that no fine is created if the book is returned on time.

## Scenario 5: Pay a Fine

**Prerequisite:** At least one unpaid fine (created in Scenario 3 or from sample data).

**Steps:**
1. Navigate to **Fine Management**.
2. Locate an unpaid fine.
3. Click **Mark Paid** and confirm.

**Expected:**
- The fine status changes to **Paid**.
- Total Paid increases and Total Unpaid decreases.

**Verify in Oracle:**
```sql
SELECT paid_status FROM FINE WHERE fine_id = <fine_id>;
SELECT paid_status, SUM(amount) FROM FINE GROUP BY paid_status;
```

**Viva talking point:**
- This is a payment-status update only; no real payment gateway is involved.

## Separate Read-Only Demonstration: Generate an Overdue Report

**Steps:**
1. Navigate to **Reports**.
2. Click **Overdue Issues**.
3. Review the rows and click **Export CSV**.

**Expected:**
- Report lists active issues where `TRUNC(due_date) < TRUNC(SYSDATE)`.
- CSV file downloads with correct data.

**Verify in Oracle:**
```sql
SELECT i.issue_id, m.name, b.title, i.due_date
FROM ISSUE i JOIN MEMBER m ON m.member_id = i.member_id
JOIN BOOK b ON b.book_id = i.book_id
WHERE i.status = 'Issued' AND TRUNC(i.due_date) < TRUNC(SYSDATE);
```

**Viva talking points:**
- Explain the JOINs and the date comparison.
- Explain how the same logic is implemented in the `overdue_cursor` PL/SQL block.

## Additional Demonstrations

### Database Logic Page
1. Navigate to **Database Logic**.
2. Read through the procedure/function/trigger cards.
3. Click **Run Overdue Cursor Demo**.
4. Compare output with the Overdue Issues report.

### Reports Page
Demonstrate at least three reports:
- Available Books
- Books by Category
- Staff Activity

## Recovery Steps if Demo Fails

| Problem | Recovery |
|---------|----------|
| Oracle not connected | Check `.env` credentials; ensure Oracle service is running; refresh status with topbar refresh button. |
| No overdue issues | Insert an active issue with a past due date directly in Oracle or use sample data. |
| Book has no available copies | Return an active copy first, or update `available_copies` in Oracle. |
| Procedure/trigger error | Run `sql/procedures.sql` to recreate them; verify no compile errors. |
| Duplicate email error | Use a unique email for new member registration. |
| UI shows old data | Click the refresh button in the topbar or navigate away and back. |

## Post-Demo Cleanup

Keep issued and returned transactions as history, or reset the whole database from the setup scripts before the final review. Deleting an `ISSUE` directly does not fire either stock trigger and can leave `BOOK.available_copies` inconsistent. A member with no issue history can be deleted safely:

```sql
DELETE FROM MEMBER
WHERE member_id = <test_member_id>
  AND NOT EXISTS (SELECT 1 FROM ISSUE WHERE member_id = <test_member_id>);

COMMIT;
```

Foreign keys prevent deletion of members with issue history.
