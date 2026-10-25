import sqlite3

DATABASE = "certificates.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    conn.execute("PRAGMA foreign_keys = ON")  # enforce table links
    return conn


def init_db():
    conn = get_db_connection()
    conn.executescript("""
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
            FOREIGN KEY (student_id) REFERENCES students (id)
        );
    """)
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