
from database import get_db_connection

conn = get_db_connection()

for table in ["users", "certificates"]:
    print(f"\nColumns in {table}:")
    try:
        rows = conn.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()

        for row in rows:
            print(row["name"])
    except Exception as e:
        print("Error:", e)

conn.close()
