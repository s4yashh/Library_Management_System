# Live Oracle Verification — 26 October 2026

This is an observed snapshot from the local `LIBRARY` schema in `FREEPDB1`. Queries come from [`sql/queries.sql`](../sql/queries.sql). Data can change after later UI transactions.

**Oracle server time:** 2026-10-26 11:30:01

## Table row counts

| Table | Rows |
|---|---:|
| AUTHOR | 10 |
| CATEGORY | 10 |
| BOOK | 10 |
| MEMBER | 10 |
| STAFF | 10 |
| ISSUE | 15 |
| FINE | 10 |

## Review II query outputs

### 1. Books with author and category

**Rows returned:** 10

| TITLE | AUTHOR_NAME | CATEGORY_NAME |
|---|---|---|
| Malgudi Days | R. K. Narayan | Fiction |
| The Alchemist | Paulo Coelho | Fiction |
| Five Point Someone | Chetan Bhagat | Fiction |
| 1984 | George Orwell | Classic |
| Pride and Prejudice | Jane Austen | Classic |
| Harry Potter | J. K. Rowling | Fantasy |
| A Brief History of Time | Stephen Hawking | Science |
| Sapiens | Yuval Noah Harari | History |
| Murder on the Orient Express | Agatha Christie | Mystery |
| Wings of Fire | A. P. J. Abdul Kalam | Biography |

### 2. Available books

**Rows returned:** 10

| TITLE | AVAILABLE_COPIES |
|---|---|
| Malgudi Days | 4 |
| 1984 | 3 |
| Harry Potter | 5 |
| The Alchemist | 4 |
| Wings of Fire | 3 |
| Pride and Prejudice | 3 |
| Sapiens | 4 |
| Five Point Someone | 5 |
| A Brief History of Time | 3 |
| Murder on the Orient Express | 4 |

### 3. Members who borrowed books

**Rows returned:** 10

| NAME |
|---|
| Aditi Sharma |
| Rahul Verma |
| Neha Gupta |
| Arjun Mehta |
| Isha Nair |
| Karan Das |
| Pooja Rao |
| Dev Malhotra |
| Riya Kapoor |
| Manav Jain |

### 4. Issue history

**Rows returned:** 15

| ISSUE_ID | NAME | TITLE | ISSUE_DATE | DUE_DATE | RETURN_DATE | STATUS |
|---|---|---|---|---|---|---|
| 1 | Aditi Sharma | Malgudi Days | 2026-08-01 | 2026-08-08 | 2026-08-11 | Returned |
| 11 | Rahul Verma | Malgudi Days | 2026-09-01 | 2026-09-15 | — | Issued |
| 2 | Rahul Verma | 1984 | 2026-08-02 | 2026-08-09 | 2026-08-12 | Returned |
| 12 | Neha Gupta | 1984 | 2026-09-02 | 2026-09-16 | — | Issued |
| 3 | Neha Gupta | Harry Potter | 2026-08-03 | 2026-08-10 | 2026-08-14 | Returned |
| 13 | Arjun Mehta | Harry Potter | 2026-09-03 | 2026-09-17 | — | Issued |
| 4 | Arjun Mehta | The Alchemist | 2026-08-04 | 2026-08-11 | 2026-08-13 | Returned |
| 14 | Isha Nair | The Alchemist | 2026-09-04 | 2026-09-18 | — | Issued |
| 5 | Isha Nair | Wings of Fire | 2026-08-05 | 2026-08-12 | 2026-08-15 | Returned |
| 15 | Karan Das | Wings of Fire | 2026-09-05 | 2026-09-19 | — | Issued |
| 6 | Karan Das | Pride and Prejudice | 2026-08-06 | 2026-08-13 | 2026-08-16 | Returned |
| 7 | Pooja Rao | Sapiens | 2026-08-07 | 2026-08-14 | 2026-08-18 | Returned |
| 8 | Dev Malhotra | Five Point Someone | 2026-08-08 | 2026-08-15 | 2026-08-18 | Returned |
| 9 | Riya Kapoor | A Brief History of Time | 2026-08-09 | 2026-08-16 | 2026-08-20 | Returned |
| 10 | Manav Jain | Murder on the Orient Express | 2026-08-10 | 2026-08-17 | 2026-08-21 | Returned |

### 5. Book titles per category

**Rows returned:** 10

| CATEGORY_NAME | TOTAL |
|---|---|
| Fiction | 3 |
| Classic | 2 |
| Fantasy | 1 |
| Biography | 1 |
| History | 1 |
| Science | 1 |
| Mystery | 1 |
| Self-Help | 0 |
| Education | 0 |
| Technology | 0 |

### 6. Borrow count per member

**Rows returned:** 10

| NAME | BORROWED |
|---|---|
| Aditi Sharma | 1 |
| Rahul Verma | 2 |
| Neha Gupta | 2 |
| Arjun Mehta | 2 |
| Isha Nair | 2 |
| Karan Das | 2 |
| Pooja Rao | 1 |
| Dev Malhotra | 1 |
| Riya Kapoor | 1 |
| Manav Jain | 1 |

### 7. Members with no borrowing history

**Rows returned:** 0

No rows in this snapshot.

### 8. Books above average price

**Rows returned:** 4

| TITLE | PRICE |
|---|---|
| 1984 | 399.0 |
| Harry Potter | 499.0 |
| Sapiens | 599.0 |
| A Brief History of Time | 450.0 |

### 9. Overdue active issues

**Rows returned:** 5

| ISSUE_ID | NAME | TITLE | DUE_DATE |
|---|---|---|---|
| 11 | Rahul Verma | Malgudi Days | 2026-09-15 |
| 12 | Neha Gupta | 1984 | 2026-09-16 |
| 13 | Arjun Mehta | Harry Potter | 2026-09-17 |
| 14 | Isha Nair | The Alchemist | 2026-09-18 |
| 15 | Karan Das | Wings of Fire | 2026-09-19 |

### 10. Total fines by payment status

**Rows returned:** 2

| PAID_STATUS | TOTAL_FINE |
|---|---|
| Unpaid | 110 |
| Paid | 55 |

### 11. Unpaid fines

**Rows returned:** 6

| NAME | TITLE | AMOUNT |
|---|---|---|
| Aditi Sharma | Malgudi Days | 15.0 |
| Neha Gupta | Harry Potter | 20.0 |
| Isha Nair | Wings of Fire | 15.0 |
| Pooja Rao | Sapiens | 20.0 |
| Riya Kapoor | A Brief History of Time | 20.0 |
| Manav Jain | Murder on the Orient Express | 20.0 |

### 12. Authors with multiple books

**Rows returned:** 0

No rows in this snapshot.

### 13. Most expensive book

**Rows returned:** 1

| TITLE | PRICE |
|---|---|
| Sapiens | 599.0 |

### 14. Issues handled per staff member

**Rows returned:** 10

| NAME | HANDLED |
|---|---|
| Aarav Sharma | 2 |
| Diya Verma | 2 |
| Rohan Gupta | 2 |
| Meera Nair | 2 |
| Kabir Singh | 2 |
| Ananya Rao | 1 |
| Ishaan Das | 1 |
| Sara Khan | 1 |
| Vivaan Joshi | 1 |
| Priya Iyer | 1 |

### 15. Books with copies currently issued

**Rows returned:** 5

| TITLE | TOTAL_COPIES | AVAILABLE_COPIES |
|---|---|---|
| Malgudi Days | 5 | 4 |
| 1984 | 4 | 3 |
| Harry Potter | 6 | 5 |
| The Alchemist | 5 | 4 |
| Wings of Fire | 4 | 3 |

## Reversible integrated transaction demonstration

These operations ran against the real Oracle procedures, functions, triggers and tables in one transaction. The transaction was rolled back after verification, so the original sample data remains intact.

| Step | Observed result |
|---|---|
| Register member (INSERT) | MEMBER 11: Review 3 Test Member, Student |
| Issue book through `issue_book` and `trg_issue_insert` | ISSUE 16 became Issued; BOOK 1 available copies 4 → 3 |
| Overdue PL/SQL cursor | Included ISSUE 16 with due date 2026-10-25 |
| Return through `return_book`, `calculate_fine`, `overdue_days`, `trg_issue_return` | ISSUE 16 became Returned; return date set; available copies 3 → 4; fine ₹5.0 Unpaid |
| Mark existing fine paid (UPDATE) | FINE 1 became Paid inside the transaction |
| Roll back test transaction | Test member and issue absent; FINE 1 remained Unpaid; BOOK 1 available copies remained 4 |
Additional DML check: inserted then deleted an unreferenced test MEMBER 11; DELETE affected 1 row and the row count was 0. The enclosing transaction was rolled back.
