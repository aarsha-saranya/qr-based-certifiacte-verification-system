
import os
import sqlite3

DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(__file__), "certificates.db")
)


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db_connection()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            certificate_id TEXT NOT NULL UNIQUE,
            student_id INTEGER NOT NULL,
            course_name TEXT NOT NULL,
            issued_by TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'valid',
            owner_user_id INTEGER,
            FOREIGN KEY (student_id)
                REFERENCES students(id),
            FOREIGN KEY (owner_user_id)
                REFERENCES users(id)
        );
    """)

    # Update existing databases without deleting old data.
    columns = {
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(certificates)"
        ).fetchall()
    }

    if "status" not in columns:
        conn.execute("""
            ALTER TABLE certificates
            ADD COLUMN status TEXT NOT NULL DEFAULT 'valid'
        """)

    if "owner_user_id" not in columns:
        conn.execute("""
            ALTER TABLE certificates
            ADD COLUMN owner_user_id INTEGER
        """)

    conn.commit()
    conn.close()
