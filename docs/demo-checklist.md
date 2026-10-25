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
5. Open `http://127.0.0.1:5000` in a browser.
6. Confirm the database status indicator shows **Oracle connected**.

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
WHERE i.status = 'Issued' AND i.due_date < SYSDATE;
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

## Scenario 2: Issue a Book

**Steps:**
1. Navigate to **Issue Book**.
2. Select a member, a book with available copies, a staff member and a due date.
3. Note the available copy count displayed.
4. Click **Issue Book**.

**Expected:**
- Success toast shows the new Issue ID.
- The book's available copies decrease by 1.
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

## Scenario 3: Return an Overdue Book

**Prerequisite:** An active issue with `due_date < SYSDATE`. The sample data includes issues 11–15 with due dates in September 2026.

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

## Scenario 4: Pay a Fine

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

## Scenario 5: Generate an Overdue Report

**Steps:**
1. Navigate to **Reports**.
2. Click **Overdue Issues**.
3. Review the rows and click **Export CSV**.

**Expected:**
- Report lists active issues where `due_date < SYSDATE`.
- CSV file downloads with correct data.

**Verify in Oracle:**
```sql
SELECT i.issue_id, m.name, b.title, i.due_date
FROM ISSUE i JOIN MEMBER m ON m.member_id = i.member_id
JOIN BOOK b ON b.book_id = i.book_id
WHERE i.status = 'Issued' AND i.due_date < SYSDATE;
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

If you created test members, issues or fines during practice, remove them before the final review:

```sql
-- Delete test fines first (child table)
DELETE FROM FINE WHERE issue_id IN (SELECT issue_id FROM ISSUE WHERE member_id = <test_member_id>);

-- Delete test issues
DELETE FROM ISSUE WHERE member_id = <test_member_id>;

-- Delete test member
DELETE FROM MEMBER WHERE member_id = <test_member_id>;

COMMIT;
```

Always delete child records before parent records to respect foreign keys.
