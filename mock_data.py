"""Static demo data used when DEMO_MODE=true.

This module lets the LibraryDesk UI be tested without a live Oracle connection.
All responses carry a `demo: true` flag from the backend to make the demo state
explicit to the user.
"""

AUTHORS = [
    {"author_id": 1, "author_name": "R. K. Narayan", "country": "India", "book_count": 1},
    {"author_id": 2, "author_name": "George Orwell", "country": "United Kingdom", "book_count": 1},
    {"author_id": 3, "author_name": "J. K. Rowling", "country": "United Kingdom", "book_count": 1},
    {"author_id": 4, "author_name": "Paulo Coelho", "country": "Brazil", "book_count": 1},
    {"author_id": 5, "author_name": "A. P. J. Abdul Kalam", "country": "India", "book_count": 1},
    {"author_id": 6, "author_name": "Jane Austen", "country": "United Kingdom", "book_count": 1},
    {"author_id": 7, "author_name": "Yuval Noah Harari", "country": "Israel", "book_count": 1},
    {"author_id": 8, "author_name": "Chetan Bhagat", "country": "India", "book_count": 1},
    {"author_id": 9, "author_name": "Stephen Hawking", "country": "United Kingdom", "book_count": 1},
    {"author_id": 10, "author_name": "Agatha Christie", "country": "United Kingdom", "book_count": 1},
]

CATEGORIES = [
    {"category_id": 1, "category_name": "Fiction", "book_count": 3, "available_copies": 13},
    {"category_id": 2, "category_name": "Classic", "book_count": 2, "available_copies": 6},
    {"category_id": 3, "category_name": "Fantasy", "book_count": 1, "available_copies": 5},
    {"category_id": 4, "category_name": "Self-Help", "book_count": 0, "available_copies": 0},
    {"category_id": 5, "category_name": "Science", "book_count": 1, "available_copies": 3},
    {"category_id": 6, "category_name": "History", "book_count": 1, "available_copies": 4},
    {"category_id": 7, "category_name": "Mystery", "book_count": 1, "available_copies": 4},
    {"category_id": 8, "category_name": "Biography", "book_count": 1, "available_copies": 3},
    {"category_id": 9, "category_name": "Technology", "book_count": 0, "available_copies": 0},
    {"category_id": 10, "category_name": "Education", "book_count": 0, "available_copies": 0},
]

BOOKS = [
    {"book_id": 1, "title": "Malgudi Days", "author_id": 1, "author_name": "R. K. Narayan", "category_id": 1, "category_name": "Fiction", "price": 299.0, "total_copies": 5, "available_copies": 4},
    {"book_id": 2, "title": "1984", "author_id": 2, "author_name": "George Orwell", "category_id": 2, "category_name": "Classic", "price": 399.0, "total_copies": 4, "available_copies": 3},
    {"book_id": 3, "title": "Harry Potter", "author_id": 3, "author_name": "J. K. Rowling", "category_id": 3, "category_name": "Fantasy", "price": 499.0, "total_copies": 6, "available_copies": 5},
    {"book_id": 4, "title": "The Alchemist", "author_id": 4, "author_name": "Paulo Coelho", "category_id": 1, "category_name": "Fiction", "price": 350.0, "total_copies": 5, "available_copies": 4},
    {"book_id": 5, "title": "Wings of Fire", "author_id": 5, "author_name": "A. P. J. Abdul Kalam", "category_id": 8, "category_name": "Biography", "price": 275.0, "total_copies": 4, "available_copies": 3},
    {"book_id": 6, "title": "Pride and Prejudice", "author_id": 6, "author_name": "Jane Austen", "category_id": 2, "category_name": "Classic", "price": 320.0, "total_copies": 3, "available_copies": 3},
    {"book_id": 7, "title": "Sapiens", "author_id": 7, "author_name": "Yuval Noah Harari", "category_id": 6, "category_name": "History", "price": 599.0, "total_copies": 4, "available_copies": 4},
    {"book_id": 8, "title": "Five Point Someone", "author_id": 8, "author_name": "Chetan Bhagat", "category_id": 1, "category_name": "Fiction", "price": 250.0, "total_copies": 5, "available_copies": 5},
    {"book_id": 9, "title": "A Brief History of Time", "author_id": 9, "author_name": "Stephen Hawking", "category_id": 5, "category_name": "Science", "price": 450.0, "total_copies": 3, "available_copies": 3},
    {"book_id": 10, "title": "Murder on the Orient Express", "author_id": 10, "author_name": "Agatha Christie", "category_id": 7, "category_name": "Mystery", "price": 375.0, "total_copies": 4, "available_copies": 4},
]

MEMBERS = [
    {"member_id": 1, "name": "Aditi Sharma", "email": "aditi@example.com", "phone": "9000000001", "join_date": "2026-01-10", "membership_type": "Student"},
    {"member_id": 2, "name": "Rahul Verma", "email": "rahul@example.com", "phone": "9000000002", "join_date": "2026-01-12", "membership_type": "Student"},
    {"member_id": 3, "name": "Neha Gupta", "email": "neha@example.com", "phone": "9000000003", "join_date": "2026-01-15", "membership_type": "Faculty"},
    {"member_id": 4, "name": "Arjun Mehta", "email": "arjun@example.com", "phone": "9000000004", "join_date": "2026-01-18", "membership_type": "General"},
    {"member_id": 5, "name": "Isha Nair", "email": "isha@example.com", "phone": "9000000005", "join_date": "2026-02-01", "membership_type": "Student"},
    {"member_id": 6, "name": "Karan Das", "email": "karan@example.com", "phone": "9000000006", "join_date": "2026-02-05", "membership_type": "Faculty"},
    {"member_id": 7, "name": "Pooja Rao", "email": "pooja@example.com", "phone": "9000000007", "join_date": "2026-02-10", "membership_type": "Student"},
    {"member_id": 8, "name": "Dev Malhotra", "email": "dev@example.com", "phone": "9000000008", "join_date": "2026-02-15", "membership_type": "General"},
    {"member_id": 9, "name": "Riya Kapoor", "email": "riya@example.com", "phone": "9000000009", "join_date": "2026-03-01", "membership_type": "Student"},
    {"member_id": 10, "name": "Manav Jain", "email": "manav@example.com", "phone": "9000000010", "join_date": "2026-03-05", "membership_type": "Faculty"},
]

STAFF = [
    {"staff_id": 1, "name": "Aarav Sharma", "role": "Librarian", "email": "aarav@library.edu"},
    {"staff_id": 2, "name": "Diya Verma", "role": "Assistant", "email": "diya@library.edu"},
    {"staff_id": 3, "name": "Rohan Gupta", "role": "Librarian", "email": "rohan@library.edu"},
    {"staff_id": 4, "name": "Meera Nair", "role": "Assistant", "email": "meera@library.edu"},
    {"staff_id": 5, "name": "Kabir Singh", "role": "Administrator", "email": "kabir@library.edu"},
]

ISSUES = [
    {"issue_id": 1, "book_id": 1, "book_title": "Malgudi Days", "member_id": 1, "member_name": "Aditi Sharma", "staff_id": 1, "staff_name": "Aarav Sharma", "issue_date": "2026-08-01", "due_date": "2026-08-08", "return_date": "2026-08-11", "status": "Returned"},
    {"issue_id": 2, "book_id": 2, "book_title": "1984", "member_id": 2, "member_name": "Rahul Verma", "staff_id": 2, "staff_name": "Diya Verma", "issue_date": "2026-08-02", "due_date": "2026-08-09", "return_date": "2026-08-12", "status": "Returned"},
    {"issue_id": 3, "book_id": 3, "book_title": "Harry Potter", "member_id": 3, "member_name": "Neha Gupta", "staff_id": 3, "staff_name": "Rohan Gupta", "issue_date": "2026-08-03", "due_date": "2026-08-10", "return_date": "2026-08-14", "status": "Returned"},
    {"issue_id": 11, "book_id": 1, "book_title": "Malgudi Days", "member_id": 2, "member_name": "Rahul Verma", "staff_id": 1, "staff_name": "Aarav Sharma", "issue_date": "2026-09-01", "due_date": "2026-09-15", "return_date": None, "status": "Issued"},
    {"issue_id": 12, "book_id": 2, "book_title": "1984", "member_id": 3, "member_name": "Neha Gupta", "staff_id": 2, "staff_name": "Diya Verma", "issue_date": "2026-09-02", "due_date": "2026-09-16", "return_date": None, "status": "Issued"},
    {"issue_id": 13, "book_id": 3, "book_title": "Harry Potter", "member_id": 4, "member_name": "Arjun Mehta", "staff_id": 3, "staff_name": "Rohan Gupta", "issue_date": "2026-09-03", "due_date": "2026-09-17", "return_date": None, "status": "Issued"},
]

FINES = [
    {"fine_id": 1, "issue_id": 1, "member_name": "Aditi Sharma", "book_title": "Malgudi Days", "amount": 15.0, "paid_status": "Unpaid"},
    {"fine_id": 2, "issue_id": 2, "member_name": "Rahul Verma", "book_title": "1984", "amount": 15.0, "paid_status": "Paid"},
    {"fine_id": 3, "issue_id": 3, "member_name": "Neha Gupta", "book_title": "Harry Potter", "amount": 20.0, "paid_status": "Unpaid"},
]

DASHBOARD_STATS = {
    "total_books": 10,
    "total_copies": 43,
    "available_copies": 38,
    "issued_transactions": 5,
    "registered_members": 10,
    "overdue_issues": 3,
    "total_unpaid_fines": 50.0,
    "total_paid_fines": 15.0,
}

RECENT_ISSUES = ISSUES[:6]

OVERDUE_PREVIEW = [
    {"issue_id": 11, "member_name": "Rahul Verma", "book_title": "Malgudi Days", "due_date": "2026-09-15"},
    {"issue_id": 12, "member_name": "Neha Gupta", "book_title": "1984", "due_date": "2026-09-16"},
    {"issue_id": 13, "member_name": "Arjun Mehta", "book_title": "Harry Potter", "due_date": "2026-09-17"},
]

FINE_SUMMARY = {"Paid": 15.0, "Unpaid": 50.0}

OVERDUE_DEMO_ROWS = OVERDUE_PREVIEW

REPORT_DATA = {
    "available-books": [
        {"title": "Malgudi Days", "available_copies": 4},
        {"title": "1984", "available_copies": 3},
        {"title": "Harry Potter", "available_copies": 5},
        {"title": "The Alchemist", "available_copies": 4},
        {"title": "Wings of Fire", "available_copies": 3},
    ],
    "books-by-category": [
        {"category_name": "Fiction", "total_titles": 3, "total_copies": 15, "available_copies": 13},
        {"category_name": "Classic", "total_titles": 2, "total_copies": 7, "available_copies": 6},
        {"category_name": "Fantasy", "total_titles": 1, "total_copies": 6, "available_copies": 5},
    ],
    "current-issues": [
        {"issue_id": 11, "member_name": "Rahul Verma", "book_title": "Malgudi Days", "issue_date": "2026-09-01", "due_date": "2026-09-15", "staff_name": "Aarav Sharma"},
    ],
    "overdue": OVERDUE_PREVIEW,
    "issue-history": ISSUES,
    "borrowing-count": [
        {"member_id": 1, "name": "Aditi Sharma", "borrow_count": 1},
        {"member_id": 2, "name": "Rahul Verma", "borrow_count": 2},
        {"member_id": 3, "name": "Neha Gupta", "borrow_count": 2},
    ],
    "inactive-members": [
        {"member_id": 5, "name": "Isha Nair", "email": "isha@example.com"},
    ],
    "fine-summary": [
        {"paid_status": "Paid", "total": 15.0, "count": 1},
        {"paid_status": "Unpaid", "total": 50.0, "count": 2},
    ],
    "unpaid-fines": [
        {"fine_id": 1, "member_name": "Aditi Sharma", "book_title": "Malgudi Days", "amount": 15.0},
        {"fine_id": 3, "member_name": "Neha Gupta", "book_title": "Harry Potter", "amount": 20.0},
    ],
    "staff-activity": [
        {"staff_id": 1, "name": "Aarav Sharma", "issues_handled": 2},
        {"staff_id": 2, "name": "Diya Verma", "issues_handled": 2},
    ],
    "issued-books": [
        {"title": "Malgudi Days", "total_copies": 5, "available_copies": 4, "issued_copies": 1},
        {"title": "1984", "total_copies": 4, "available_copies": 3, "issued_copies": 1},
    ],
    "books-authors-categories": [
        {"title": "Malgudi Days", "author_name": "R. K. Narayan", "category_name": "Fiction", "price": 299.0},
        {"title": "1984", "author_name": "George Orwell", "category_name": "Classic", "price": 399.0},
    ],
}
