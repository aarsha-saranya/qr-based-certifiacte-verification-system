<<<<<<< HEAD

import secrets
import sqlite3

from database import get_db_connection


def add_certificate(
    name,
    email,
    course_name,
    issued_by,
    issue_date,
    owner_user_id
):
    conn = get_db_connection()

    try:
        # Confirm that the issuing account exists.
        user = conn.execute(
            "SELECT id FROM users WHERE id = ?",
            (owner_user_id,)
        ).fetchone()

        if not user:
            raise ValueError("Invalid issuing account.")

        # Find or create the student record.
        student = conn.execute(
            "SELECT id FROM students WHERE email = ?",
            (email,)
        ).fetchone()

        if student:
            student_id = student["id"]
            conn.execute(
                "UPDATE students SET name = ? WHERE id = ?",
                (name, student_id)
            )
        else:
            cursor = conn.execute(
                "INSERT INTO students (name, email) VALUES (?, ?)",
                (name, email)
            )
            student_id = cursor.lastrowid

        # Generate a unique certificate ID.
        while True:
            certificate_id = (
                "CERT-" + secrets.token_hex(6).upper()
            )

            exists = conn.execute(
                "SELECT id FROM certificates WHERE certificate_id = ?",
                (certificate_id,)
            ).fetchone()

            if not exists:
                break

        conn.execute("""
            INSERT INTO certificates (
                certificate_id,
                student_id,
                course_name,
                issued_by,
                issue_date,
                owner_user_id,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'valid')
        """, (
            certificate_id,
            student_id,
            course_name,
            issued_by,
            issue_date,
            owner_user_id
        ))

        conn.commit()
        return certificate_id

    except Exception:
        conn.rollback()
        raise

=======
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
>>>>>>> 21ecc1c83ddf9d9674b32ef06d00a701d297e60c
    finally:
        conn.close()


def get_certificate(certificate_id):
    conn = get_db_connection()
<<<<<<< HEAD

    try:
        row = conn.execute("""
            SELECT
                c.certificate_id,
                c.course_name,
                c.issued_by,
                c.issue_date,
                c.status,
                c.owner_user_id,
                c.created_at,
                s.name,
                s.email
            FROM certificates c
            JOIN students s ON s.id = c.student_id
            WHERE c.certificate_id = ?
        """, (certificate_id,)).fetchone()

        return dict(row) if row else None

    finally:
        conn.close()


def get_all_certificates(owner_user_id):
    conn = get_db_connection()

    try:
        rows = conn.execute("""
            SELECT
                c.certificate_id,
                c.course_name,
                c.issued_by,
                c.issue_date,
                c.status,
                c.created_at,
                s.name,
                s.email
            FROM certificates c
            JOIN students s ON s.id = c.student_id
            WHERE c.owner_user_id = ?
            ORDER BY c.id DESC
        """, (owner_user_id,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()
=======
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
>>>>>>> 21ecc1c83ddf9d9674b32ef06d00a701d297e60c
