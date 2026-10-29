import os
import sqlite3

DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "certificates.db"),
)


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # access columns by name
    conn.execute("PRAGMA foreign_keys = ON")  # enforce table links
    return conn


def init_db():
    conn = get_db_connection()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password TEXT NOT NULL,
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
            student_id INTEGER,
            student_name TEXT,
            course_name TEXT NOT NULL,
            issued_by TEXT,
            issue_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'valid',
            owner_user_id INTEGER,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (owner_user_id) REFERENCES users (id)
        );
    """)

    # Add any columns that older databases are missing.
    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(certificates)").fetchall()
    }
    if "student_name" not in columns:
        conn.execute("ALTER TABLE certificates ADD COLUMN student_name TEXT")
    if "status" not in columns:
        conn.execute(
            "ALTER TABLE certificates ADD COLUMN status TEXT NOT NULL DEFAULT 'valid'"
        )
    if "owner_user_id" not in columns:
        conn.execute("ALTER TABLE certificates ADD COLUMN owner_user_id INTEGER")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    conn = get_db_connection()
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    print("Tables created:", [t["name"] for t in tables])
    conn.close()