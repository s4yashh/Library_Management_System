-- Library Management System - Oracle schema
-- Source: Review 2 submission (BCSE302L DBMS Lab, VIT)

CREATE TABLE AUTHOR (
    author_id NUMBER PRIMARY KEY,
    author_name VARCHAR2(50) NOT NULL,
    country VARCHAR2(30) DEFAULT 'India'
);

CREATE TABLE CATEGORY (
    category_id NUMBER PRIMARY KEY,
    category_name VARCHAR2(40) NOT NULL UNIQUE
);

CREATE TABLE BOOK (
    book_id NUMBER PRIMARY KEY,
    title VARCHAR2(100) NOT NULL,
    author_id NUMBER REFERENCES AUTHOR(author_id),
    category_id NUMBER REFERENCES CATEGORY(category_id),
    price NUMBER(8,2) CHECK (price > 0),
    total_copies NUMBER CHECK (total_copies >= 0),
    available_copies NUMBER CHECK (
        available_copies >= 0
        AND available_copies <= total_copies
    )
);

CREATE TABLE MEMBER (
    member_id NUMBER PRIMARY KEY,
    name VARCHAR2(50) NOT NULL,
    email VARCHAR2(60) NOT NULL UNIQUE,
    phone VARCHAR2(15),
    join_date DATE DEFAULT SYSDATE,
    membership_type VARCHAR2(15)
        CHECK (membership_type IN ('Student', 'Faculty', 'General'))
);

CREATE TABLE STAFF (
    staff_id NUMBER PRIMARY KEY,
    name VARCHAR2(50) NOT NULL,
    role VARCHAR2(30) NOT NULL,
    email VARCHAR2(60) UNIQUE
);

CREATE TABLE ISSUE (
    issue_id NUMBER PRIMARY KEY,
    book_id NUMBER NOT NULL REFERENCES BOOK(book_id),
    member_id NUMBER NOT NULL REFERENCES MEMBER(member_id),
    staff_id NUMBER REFERENCES STAFF(staff_id),
    issue_date DATE DEFAULT SYSDATE,
    due_date DATE NOT NULL,
    return_date DATE,
    status VARCHAR2(10) DEFAULT 'Issued'
        CHECK (status IN ('Issued', 'Returned'))
);

CREATE TABLE FINE (
    fine_id NUMBER PRIMARY KEY,
    issue_id NUMBER NOT NULL UNIQUE REFERENCES ISSUE(issue_id),
    amount NUMBER(8,2) NOT NULL CHECK (amount > 0),
    paid_status VARCHAR2(10) DEFAULT 'Unpaid'
        CHECK (paid_status IN ('Paid', 'Unpaid'))
);
