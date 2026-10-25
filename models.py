import sqlite3
from database import get_db_connection
from utils import generate_certificate_id


def get_or_create_student(conn, name, email):
    student = conn.execute(
        "SELECT id FROM students WHERE email = ?", (email,)
    ).fetchone()
    if student:
        return student["id"]

    cursor = conn.execute(
        "INSERT INTO students (name, email) VALUES (?, ?)", (name, email)
    )
    return cursor.lastrowid


def add_certificate(name, email, course_name, issued_by, issue_date):
    conn = get_db_connection()
    try:
        student_id = get_or_create_student(conn, name, email)

        for _ in range(5):  # retry in the rare case of an ID collision
            certificate_id = generate_certificate_id()
            try:
                conn.execute(
                    """INSERT INTO certificates
                       (certificate_id, student_id, course_name, issued_by, issue_date)
                       VALUES (?, ?, ?, ?, ?)""",
                    (certificate_id, student_id, course_name, issued_by, issue_date),
                )
                conn.commit()
                return certificate_id
            except sqlite3.IntegrityError:
                continue  # duplicate ID, generate a new one

        raise RuntimeError("Could not generate a unique certificate ID")
    finally:
        conn.close()


def get_certificate(certificate_id):
    conn = get_db_connection()
    row = conn.execute(
        """SELECT c.certificate_id, s.name, s.email, c.course_name,
                  c.issued_by, c.issue_date, c.created_at
           FROM certificates c
           JOIN students s ON c.student_id = s.id
           WHERE c.certificate_id = ?""",
        (certificate_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_certificates():
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT c.certificate_id, s.name, s.email, c.course_name,
                  c.issued_by, c.issue_date, c.created_at
           FROM certificates c
           JOIN students s ON c.student_id = s.id
           ORDER BY c.id DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    new_id = add_certificate(
        "Asha Rao", "asha@example.com", "Python Workshop", "ABC College", "2026-10-22"
    )
    print("Created:", new_id)
    print("Retrieved:", get_certificate(new_id))
    print("Total certificates:", len(get_all_certificates()))