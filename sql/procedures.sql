-- Library Management System - stored procedures, functions, triggers and cursor

-----------------------------------------------------------
-- Procedure: issue_book
-- Purpose: Insert a borrowing transaction.
-- The trigger trg_issue_insert validates stock and decrements available_copies.
-----------------------------------------------------------
CREATE OR REPLACE PROCEDURE issue_book(
    p_issue_id NUMBER,
    p_book_id NUMBER,
    p_member_id NUMBER,
    p_staff_id NUMBER,
    p_due_date DATE
) AS
BEGIN
    INSERT INTO ISSUE (
        issue_id, book_id, member_id, staff_id,
        issue_date, due_date, status
    ) VALUES (
        p_issue_id, p_book_id, p_member_id, p_staff_id,
        SYSDATE, p_due_date, 'Issued'
    );
END;
/

-----------------------------------------------------------
-- Function: overdue_days
-- Purpose: Return late calendar days (zero if not overdue).
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION overdue_days(
    p_due_date DATE,
    p_return_date DATE
) RETURN NUMBER AS
BEGIN
    RETURN GREATEST(
        TRUNC(p_return_date) - TRUNC(p_due_date),
        0
    );
END;
/

-----------------------------------------------------------
-- Function: calculate_fine
-- Purpose: Calculate fine at INR 5 per overdue day.
-----------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_fine(
    p_due_date DATE,
    p_return_date DATE
) RETURN NUMBER AS
BEGIN
    RETURN overdue_days(p_due_date, p_return_date) * 5;
END;
/

-----------------------------------------------------------
-- Procedure: return_book
-- Purpose: Mark an active issue as Returned.
-- The trigger trg_issue_return restores one available copy.
-- A FINE record is inserted only when the calculated amount is positive.
-----------------------------------------------------------
CREATE OR REPLACE PROCEDURE return_book(
    p_issue_id NUMBER
) AS
    v_due_date DATE;
    v_status VARCHAR2(10);
    v_fine NUMBER;
    v_fine_id NUMBER;
BEGIN
    SELECT due_date, status
    INTO v_due_date, v_status
    FROM ISSUE
    WHERE issue_id = p_issue_id
    FOR UPDATE;

    IF v_status = 'Returned' THEN
        RAISE_APPLICATION_ERROR(-20003, 'Book already returned');
    END IF;

    v_fine := calculate_fine(v_due_date, SYSDATE);

    UPDATE ISSUE
    SET return_date = SYSDATE,
        status = 'Returned'
    WHERE issue_id = p_issue_id;

    IF v_fine > 0 THEN
        SELECT NVL(MAX(fine_id), 0) + 1
        INTO v_fine_id
        FROM FINE;

        INSERT INTO FINE (
            fine_id, issue_id, amount, paid_status
        ) VALUES (
            v_fine_id, p_issue_id, v_fine, 'Unpaid'
        );
    END IF;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(-20004, 'Issue ID not found');
END;
/

-----------------------------------------------------------
-- Trigger: trg_issue_insert
-- Purpose: Reject an issue when no copies are available,
--          otherwise decrement BOOK.available_copies by one.
-----------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_issue_insert
BEFORE INSERT ON ISSUE
FOR EACH ROW
DECLARE
    v_available NUMBER;
BEGIN
    SELECT available_copies
    INTO v_available
    FROM BOOK
    WHERE book_id = :NEW.book_id;

    IF v_available <= 0 THEN
        RAISE_APPLICATION_ERROR(-20005, 'No copies available');
    END IF;

    UPDATE BOOK
    SET available_copies = available_copies - 1
    WHERE book_id = :NEW.book_id;
END;
/

-----------------------------------------------------------
-- Trigger: trg_issue_return
-- Purpose: Restore one available copy only when an issue
--          changes from 'Issued' to 'Returned'.
-----------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_issue_return
BEFORE UPDATE OF status ON ISSUE
FOR EACH ROW
BEGIN
    IF :OLD.status = 'Issued'
       AND :NEW.status = 'Returned' THEN
        UPDATE BOOK
        SET available_copies = available_copies + 1
        WHERE book_id = :OLD.book_id;
    END IF;
END;
/

-----------------------------------------------------------
-- Cursor demonstration (anonymous PL/SQL block)
-- Purpose: Fetch every currently issued, overdue transaction.
-----------------------------------------------------------
SET SERVEROUTPUT ON;
DECLARE
    CURSOR overdue_cursor IS
        SELECT i.issue_id, m.name, b.title, i.due_date
        FROM ISSUE i
        JOIN MEMBER m ON m.member_id = i.member_id
        JOIN BOOK b ON b.book_id = i.book_id
        WHERE i.status = 'Issued'
          AND TRUNC(i.due_date) < TRUNC(SYSDATE);
BEGIN
    FOR rec IN overdue_cursor LOOP
        DBMS_OUTPUT.PUT_LINE(
            'Issue ' || rec.issue_id || ' | ' || rec.name ||
            ' | ' || rec.title || ' | Due: ' ||
            TO_CHAR(rec.due_date, 'DD-MON-YYYY')
        );
    END LOOP;
END;
/
