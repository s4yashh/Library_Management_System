# Review 3 Viva Preparation

## Project Introduction

**Project:** Library Management System  
**Student:** s4yashh  
**Institution:** Vellore Institute of Technology (VIT)  
**Course:** BCSE302L – Database Systems Lab  
**Tech Stack:** Oracle Database, Python Flask, python-oracledb, HTML5/CSS3/JS

## Problem Statement

A library needs to track books, authors, categories, members, staff, borrowings and fines. Manual record-keeping causes duplicate members, books issued without available copies, missed overdue books and incorrect fines. This system automates issuing, returning and fine calculation using an Oracle database with SQL and PL/SQL.

## Architecture Explanation

The application has three layers:

1. **Frontend:** Single-page admin dashboard built with vanilla JavaScript. It calls REST APIs and renders tables, forms and reports.
2. **Backend:** Flask server that validates input, manages transactions and talks to Oracle.
3. **Database:** Oracle Database containing seven tables, stored procedures, functions, triggers and a cursor.

## Table Relationships

- **AUTHOR → BOOK:** One author writes many books (1:N).
- **CATEGORY → BOOK:** One category contains many books (1:N).
- **BOOK → ISSUE:** One book can be issued many times (1:N).
- **MEMBER → ISSUE:** One member can have many issue records (1:N).
- **STAFF → ISSUE:** One staff member handles many issues (1:N).
- **ISSUE → FINE:** One issue generates at most one fine (1:0..1), enforced by a UNIQUE FK.

## Primary and Foreign Keys

| Table | Primary Key | Foreign Keys |
|-------|-------------|--------------|
| AUTHOR | author_id | — |
| CATEGORY | category_id | — |
| BOOK | book_id | author_id, category_id |
| MEMBER | member_id | — |
| STAFF | staff_id | — |
| ISSUE | issue_id | book_id, member_id, staff_id |
| FINE | fine_id | issue_id (UNIQUE) |

## Constraints Used

- **NOT NULL:** e.g., `BOOK.title`, `MEMBER.name`, `MEMBER.email`
- **UNIQUE:** `CATEGORY.category_name`, `MEMBER.email`, `FINE.issue_id`
- **CHECK:** `BOOK.price > 0`, `BOOK.total_copies >= 0`, `MEMBER.membership_type IN ('Student','Faculty','General')`
- **DEFAULT:** `MEMBER.join_date DEFAULT SYSDATE`, `FINE.paid_status DEFAULT 'Unpaid'`
- **Foreign Key:** Referential integrity across all related tables.

## SQL Concepts Demonstrated

- **Joins:** INNER JOIN for books with authors/categories, LEFT JOIN for categories with zero books.
- **Grouping and aggregation:** `COUNT`, `SUM`, `GROUP BY`, `HAVING`.
- **Subqueries:** Books above average price, most expensive book.
- **NOT EXISTS:** Members with no borrowing history.
- **Date comparison:** Overdue active issues where `due_date < SYSDATE`.

## Procedures vs Functions

- **Procedure:** Performs an action (e.g., `issue_book` inserts a row, `return_book` updates a row and may insert a fine). It does not have to return a value.
- **Function:** Computes and returns a single value (e.g., `overdue_days`, `calculate_fine`). Functions are called inside procedures.

## Cursor Purpose

The `overdue_cursor` is an explicit cursor that fetches every active issue whose due date has passed. It demonstrates row-by-row processing in PL/SQL and is used to display overdue books to the librarian.

## Trigger Purpose

- `trg_issue_insert` automatically validates stock and decreases `available_copies` when a book is issued.
- `trg_issue_return` automatically restores `available_copies` when an issue changes from `Issued` to `Returned`.

These triggers keep stock consistent without the application manually updating `BOOK`.

## Issue Transaction Workflow

1. Librarian selects member, book, staff and due date in the UI.
2. Backend validates input and generates the next `issue_id`.
3. Backend calls `issue_book(...)`.
4. Oracle inserts into `ISSUE`.
5. `trg_issue_insert` checks `available_copies`; if zero it raises an error, otherwise it decrements by one.
6. Backend commits on success or rolls back on failure.
7. UI refreshes the issue list and book availability.

## Return Transaction Workflow

1. Librarian selects an active issue in the UI.
2. Backend calls `return_book(issue_id)`.
3. Procedure selects the issue `FOR UPDATE` and checks status.
4. If already returned, it raises an error.
5. It calculates `calculate_fine(due_date, SYSDATE)`.
6. It updates `ISSUE` status to `Returned` and sets `return_date`.
7. `trg_issue_return` increments `BOOK.available_copies`.
8. If fine > 0, a `FINE` row is inserted.
9. Backend commits or rolls back.

## Fine Calculation

`calculate_fine` uses `overdue_days(due_date, return_date) * 5`. Each late calendar day costs INR 5. If the book is returned on or before the due date, the fine is zero.

## Commit and Rollback

The backend explicitly calls `conn.commit()` only after all dependent operations succeed. If any step raises an Oracle error, `conn.rollback()` is called so that partially completed issue/return/fine updates are not saved.

## Database Connectivity

The backend uses `python-oracledb` in Thin mode by default. Connection details come from environment variables (`ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_CONNECT_STRING`). Connections are acquired from a pool and released automatically using a context manager.

## Likely Viva Questions and Answers

1. **Q: How many tables does your project have?**  
   A: Seven: AUTHOR, CATEGORY, BOOK, MEMBER, STAFF, ISSUE and FINE.

2. **Q: Why is the ISSUE table needed?**  
   A: It resolves the many-to-many relationship between BOOK and MEMBER over time and stores borrowing dates and status.

3. **Q: What is the relationship between ISSUE and FINE?**  
   A: One-to-zero-or-one. A fine is created only for late returns, and `FINE.issue_id` is UNIQUE.

4. **Q: Which constraints did you use?**  
   A: PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE, CHECK and DEFAULT.

5. **Q: How do you prevent a book from being issued when no copies are available?**  
   A: The trigger `trg_issue_insert` checks `available_copies` and raises an application error if it is zero.

6. **Q: How is the available copy count updated?**  
   A: Automatically by triggers — decreased on issue, increased on return.

7. **Q: What happens if a returned book is returned again?**  
   A: The `return_book` procedure checks the status and raises `Book already returned`.

8. **Q: How is the fine amount calculated?**  
   A: `calculate_fine` returns `overdue_days * 5`, i.e., INR 5 per late day.

9. **Q: What is the difference between a procedure and a function?**  
   A: A procedure performs actions and may not return a value; a function returns a single value.

10. **Q: Why did you use a cursor?**  
    A: To process multiple overdue issue rows one by one and demonstrate explicit cursor handling in PL/SQL.

11. **Q: What is the role of the backend?**  
    A: It validates requests, calls Oracle procedures/queries, manages transactions and returns JSON to the frontend.

12. **Q: How does the frontend talk to the backend?**  
    A: Through the Fetch API over HTTP to `/api/*` endpoints.

13. **Q: What happens if the Oracle database is not reachable?**  
    A: The status indicator turns red and APIs return errors. If `DEMO_MODE=true`, sample data is shown with a demo banner.

14. **Q: How do you prevent SQL injection?**  
    A: All queries use bound parameters and stored procedure calls; no user input is concatenated into SQL.

15. **Q: What is the purpose of `SELECT ... FOR UPDATE` in `return_book`?**  
    A: It locks the issue row until the return transaction completes, preventing concurrent updates.

16. **Q: What is a UNIQUE foreign key?**  
    A: In `FINE`, `issue_id` is both a foreign key to `ISSUE` and UNIQUE, ensuring one fine per issue.

17. **Q: How do you handle a failed transaction?**  
    A: The backend catches the Oracle error, calls `conn.rollback()`, and returns a friendly error message.

18. **Q: What reports can the system generate?**  
    A: Available books, books by category, current issues, overdue issues, issue history, borrowing count per member, inactive members, fine summary, unpaid fines, staff activity, books with issued copies, and books with authors/categories.

19. **Q: What is the difference between total copies and available copies?**  
    A: Total copies is the physical stock; available copies is the stock not currently issued.

20. **Q: Why use environment variables for database credentials?**  
    A: To keep secrets out of source code and allow different configurations for development, demo and lab machines.

21. **Q: What is the ID generation strategy?**  
    A: `NVL(MAX(id), 0) + 1` per table, matching the existing Review 2 procedures. It is simple but not concurrency-safe.

22. **Q: How do you format dates and currency?**  
    A: Dates are shown in `DD MMM YYYY` format; currency is shown as Indian Rupees with two decimal places.

23. **Q: What is the `status` endpoint used for?**  
    A: It reports whether Oracle is connected, shows the server date, and indicates demo mode.

24. **Q: Can a member be deleted if they have issue records?**  
    A: No. The foreign key constraint prevents deletion; the UI shows an understandable error.
