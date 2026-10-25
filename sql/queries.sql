-- Library Management System - 15 representative SQL queries

-- 1. Books with author and category
SELECT b.title, a.author_name, c.category_name
FROM BOOK b
JOIN AUTHOR a ON a.author_id = b.author_id
JOIN CATEGORY c ON c.category_id = b.category_id;

-- 2. Available books
SELECT title, available_copies
FROM BOOK
WHERE available_copies > 0;

-- 3. Members who borrowed books
SELECT DISTINCT m.name
FROM MEMBER m
JOIN ISSUE i ON i.member_id = m.member_id;

-- 4. Issue history
SELECT i.issue_id, m.name, b.title, i.issue_date,
       i.due_date, i.return_date, i.status
FROM ISSUE i
JOIN MEMBER m ON m.member_id = i.member_id
JOIN BOOK b ON b.book_id = i.book_id;

-- 5. Book titles per category
SELECT c.category_name, COUNT(b.book_id) total
FROM CATEGORY c
LEFT JOIN BOOK b ON b.category_id = c.category_id
GROUP BY c.category_name;

-- 6. Borrow count per member
SELECT m.name, COUNT(i.issue_id) borrowed
FROM MEMBER m
LEFT JOIN ISSUE i ON i.member_id = m.member_id
GROUP BY m.name;

-- 7. Members with no borrowing history
SELECT name
FROM MEMBER m
WHERE NOT EXISTS (
    SELECT 1
    FROM ISSUE i
    WHERE i.member_id = m.member_id
);

-- 8. Books above average price
SELECT title, price
FROM BOOK
WHERE price > (
    SELECT AVG(price)
    FROM BOOK
);

-- 9. Overdue active issues
SELECT i.issue_id, m.name, b.title, i.due_date
FROM ISSUE i
JOIN MEMBER m ON m.member_id = i.member_id
JOIN BOOK b ON b.book_id = i.book_id
WHERE i.status = 'Issued'
  AND TRUNC(i.due_date) < TRUNC(SYSDATE);

-- 10. Total fines by payment status
SELECT paid_status, SUM(amount) total_fine
FROM FINE
GROUP BY paid_status;

-- 11. Unpaid fines
SELECT m.name, b.title, f.amount
FROM FINE f
JOIN ISSUE i ON i.issue_id = f.issue_id
JOIN MEMBER m ON m.member_id = i.member_id
JOIN BOOK b ON b.book_id = i.book_id
WHERE f.paid_status = 'Unpaid';

-- 12. Authors with multiple books
SELECT a.author_name, COUNT(*) total
FROM AUTHOR a
JOIN BOOK b ON b.author_id = a.author_id
GROUP BY a.author_name
HAVING COUNT(*) > 1;

-- 13. Most expensive book
SELECT title, price
FROM BOOK
WHERE price = (
    SELECT MAX(price)
    FROM BOOK
);

-- 14. Issues handled per staff member
SELECT s.name, COUNT(i.issue_id) handled
FROM STAFF s
LEFT JOIN ISSUE i ON i.staff_id = s.staff_id
GROUP BY s.name;

-- 15. Books with copies currently issued
SELECT title, total_copies, available_copies
FROM BOOK
WHERE available_copies < total_copies;
