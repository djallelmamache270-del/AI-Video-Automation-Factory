import sqlite3

conn = sqlite3.connect("factory.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    videos_created INTEGER DEFAULT 0,
    is_premium BOOLEAN DEFAULT FALSE
)
""")

conn.commit()
conn.close()
print("🎉 Success! The users table has been created inside factory.db")
