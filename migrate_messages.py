import sqlite3

try:
    conn = sqlite3.connect('instance/portfolio.db')
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE contact_message ADD COLUMN ai_category VARCHAR(50);")
    cursor.execute("ALTER TABLE contact_message ADD COLUMN ai_draft TEXT;")
    conn.commit()
    conn.close()
    print("Migration successful: Added AI columns to database.")
except Exception as e:
    print(f"Migration error (already run?): {e}")
