
from database import get_db_connection

conn = get_db_connection()

try:
    columns = conn.execute(
        "PRAGMA table_info(certificates)"
    ).fetchall()

    column_names = [row["name"] for row in columns]

    if "owner_user_id" not in column_names:
        conn.execute(
            "ALTER TABLE certificates ADD COLUMN owner_user_id INTEGER"
        )
        print("Added owner_user_id column.")

    # Assign old certificates only when the issuer name matches a user.
    conn.execute("""
        UPDATE certificates
        SET owner_user_id = (
            SELECT users.id
            FROM users
            WHERE lower(trim(users.name)) =
                  lower(trim(certificates.issued_by))
            LIMIT 1
        )
        WHERE owner_user_id IS NULL
          AND issued_by IS NOT NULL
    """)

    conn.commit()

    remaining = conn.execute("""
        SELECT COUNT(*) AS total
        FROM certificates
        WHERE owner_user_id IS NULL
    """).fetchone()

    print("Migration completed.")
    print("Certificates needing manual owner assignment:", remaining["total"])

except Exception:
    conn.rollback()
    raise

finally:
    conn.close()
