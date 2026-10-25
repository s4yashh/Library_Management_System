-- Library Management System - sample data
-- Insert order: AUTHOR, CATEGORY, STAFF, BOOK, MEMBER, ISSUE, FINE

INSERT ALL
INTO AUTHOR VALUES (1, 'R. K. Narayan', 'India')
INTO AUTHOR VALUES (2, 'George Orwell', 'United Kingdom')
INTO AUTHOR VALUES (3, 'J. K. Rowling', 'United Kingdom')
INTO AUTHOR VALUES (4, 'Paulo Coelho', 'Brazil')
INTO AUTHOR VALUES (5, 'A. P. J. Abdul Kalam', 'India')
INTO AUTHOR VALUES (6, 'Jane Austen', 'United Kingdom')
INTO AUTHOR VALUES (7, 'Yuval Noah Harari', 'Israel')
INTO AUTHOR VALUES (8, 'Chetan Bhagat', 'India')
INTO AUTHOR VALUES (9, 'Stephen Hawking', 'United Kingdom')
INTO AUTHOR VALUES (10, 'Agatha Christie', 'United Kingdom')
SELECT 1 FROM DUAL;

INSERT ALL
INTO CATEGORY VALUES (1, 'Fiction')
INTO CATEGORY VALUES (2, 'Classic')
INTO CATEGORY VALUES (3, 'Fantasy')
INTO CATEGORY VALUES (4, 'Self-Help')
INTO CATEGORY VALUES (5, 'Science')
INTO CATEGORY VALUES (6, 'History')
INTO CATEGORY VALUES (7, 'Mystery')
INTO CATEGORY VALUES (8, 'Biography')
INTO CATEGORY VALUES (9, 'Technology')
INTO CATEGORY VALUES (10, 'Education')
SELECT 1 FROM DUAL;

INSERT ALL
INTO STAFF VALUES (1, 'Aarav Sharma', 'Librarian', 'aarav@library.edu')
INTO STAFF VALUES (2, 'Diya Verma', 'Assistant', 'diya@library.edu')
INTO STAFF VALUES (3, 'Rohan Gupta', 'Librarian', 'rohan@library.edu')
INTO STAFF VALUES (4, 'Meera Nair', 'Assistant', 'meera@library.edu')
INTO STAFF VALUES (5, 'Kabir Singh', 'Administrator', 'kabir@library.edu')
INTO STAFF VALUES (6, 'Ananya Rao', 'Assistant', 'ananya@library.edu')
INTO STAFF VALUES (7, 'Ishaan Das', 'Librarian', 'ishaan@library.edu')
INTO STAFF VALUES (8, 'Sara Khan', 'Assistant', 'sara@library.edu')
INTO STAFF VALUES (9, 'Vivaan Joshi', 'Administrator', 'vivaan@library.edu')
INTO STAFF VALUES (10, 'Priya Iyer', 'Librarian', 'priya@library.edu')
SELECT 1 FROM DUAL;

INSERT ALL
INTO BOOK VALUES (1, 'Malgudi Days', 1, 1, 299, 5, 4)
INTO BOOK VALUES (2, '1984', 2, 2, 399, 4, 3)
INTO BOOK VALUES (3, 'Harry Potter', 3, 3, 499, 6, 5)
INTO BOOK VALUES (4, 'The Alchemist', 4, 1, 350, 5, 4)
INTO BOOK VALUES (5, 'Wings of Fire', 5, 8, 275, 4, 3)
INTO BOOK VALUES (6, 'Pride and Prejudice', 6, 2, 320, 3, 3)
INTO BOOK VALUES (7, 'Sapiens', 7, 6, 599, 4, 4)
INTO BOOK VALUES (8, 'Five Point Someone', 8, 1, 250, 5, 5)
INTO BOOK VALUES (9, 'A Brief History of Time', 9, 5, 450, 3, 3)
INTO BOOK VALUES (10, 'Murder on the Orient Express', 10, 7, 375, 4, 4)
SELECT 1 FROM DUAL;

INSERT ALL
INTO MEMBER VALUES (1, 'Aditi Sharma', 'aditi@example.com', '9000000001', DATE '2026-01-10', 'Student')
INTO MEMBER VALUES (2, 'Rahul Verma', 'rahul@example.com', '9000000002', DATE '2026-01-12', 'Student')
INTO MEMBER VALUES (3, 'Neha Gupta', 'neha@example.com', '9000000003', DATE '2026-01-15', 'Faculty')
INTO MEMBER VALUES (4, 'Arjun Mehta', 'arjun@example.com', '9000000004', DATE '2026-01-18', 'General')
INTO MEMBER VALUES (5, 'Isha Nair', 'isha@example.com', '9000000005', DATE '2026-02-01', 'Student')
INTO MEMBER VALUES (6, 'Karan Das', 'karan@example.com', '9000000006', DATE '2026-02-05', 'Faculty')
INTO MEMBER VALUES (7, 'Pooja Rao', 'pooja@example.com', '9000000007', DATE '2026-02-10', 'Student')
INTO MEMBER VALUES (8, 'Dev Malhotra', 'dev@example.com', '9000000008', DATE '2026-02-15', 'General')
INTO MEMBER VALUES (9, 'Riya Kapoor', 'riya@example.com', '9000000009', DATE '2026-03-01', 'Student')
INTO MEMBER VALUES (10, 'Manav Jain', 'manav@example.com', '9000000010', DATE '2026-03-05', 'Faculty')
SELECT 1 FROM DUAL;

-- Ten returned issues with corresponding fines
INSERT ALL
INTO ISSUE VALUES (1, 1, 1, 1, DATE '2026-08-01', DATE '2026-08-08', DATE '2026-08-11', 'Returned')
INTO ISSUE VALUES (2, 2, 2, 2, DATE '2026-08-02', DATE '2026-08-09', DATE '2026-08-12', 'Returned')
INTO ISSUE VALUES (3, 3, 3, 3, DATE '2026-08-03', DATE '2026-08-10', DATE '2026-08-14', 'Returned')
INTO ISSUE VALUES (4, 4, 4, 4, DATE '2026-08-04', DATE '2026-08-11', DATE '2026-08-13', 'Returned')
INTO ISSUE VALUES (5, 5, 5, 5, DATE '2026-08-05', DATE '2026-08-12', DATE '2026-08-15', 'Returned')
INTO ISSUE VALUES (6, 6, 6, 6, DATE '2026-08-06', DATE '2026-08-13', DATE '2026-08-16', 'Returned')
INTO ISSUE VALUES (7, 7, 7, 7, DATE '2026-08-07', DATE '2026-08-14', DATE '2026-08-18', 'Returned')
INTO ISSUE VALUES (8, 8, 8, 8, DATE '2026-08-08', DATE '2026-08-15', DATE '2026-08-18', 'Returned')
INTO ISSUE VALUES (9, 9, 9, 9, DATE '2026-08-09', DATE '2026-08-16', DATE '2026-08-20', 'Returned')
INTO ISSUE VALUES (10, 10, 10, 10, DATE '2026-08-10', DATE '2026-08-17', DATE '2026-08-21', 'Returned')
-- Five active issues with past due dates so overdue reports return rows
INTO ISSUE VALUES (11, 1, 2, 1, DATE '2026-09-01', DATE '2026-09-15', NULL, 'Issued')
INTO ISSUE VALUES (12, 2, 3, 2, DATE '2026-09-02', DATE '2026-09-16', NULL, 'Issued')
INTO ISSUE VALUES (13, 3, 4, 3, DATE '2026-09-03', DATE '2026-09-17', NULL, 'Issued')
INTO ISSUE VALUES (14, 4, 5, 4, DATE '2026-09-04', DATE '2026-09-18', NULL, 'Issued')
INTO ISSUE VALUES (15, 5, 6, 5, DATE '2026-09-05', DATE '2026-09-19', NULL, 'Issued')
SELECT 1 FROM DUAL;

-- Sample fines for the returned issues
INSERT ALL
INTO FINE VALUES (1, 1, 15, 'Unpaid')
INTO FINE VALUES (2, 2, 15, 'Paid')
INTO FINE VALUES (3, 3, 20, 'Unpaid')
INTO FINE VALUES (4, 4, 10, 'Paid')
INTO FINE VALUES (5, 5, 15, 'Unpaid')
INTO FINE VALUES (6, 6, 15, 'Paid')
INTO FINE VALUES (7, 7, 20, 'Unpaid')
INTO FINE VALUES (8, 8, 15, 'Paid')
INTO FINE VALUES (9, 9, 20, 'Unpaid')
INTO FINE VALUES (10, 10, 20, 'Unpaid')
SELECT 1 FROM DUAL;

COMMIT;
