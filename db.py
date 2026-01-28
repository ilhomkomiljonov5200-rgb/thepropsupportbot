import sqlite3

conn = sqlite3.connect("support.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message_id INTEGER
)
""")
conn.commit()


def add_ticket(user_id, message_id):
    cur.execute(
        "INSERT INTO tickets (user_id, message_id) VALUES (?, ?)",
        (user_id, message_id)
    )
    conn.commit()


def get_user(message_id):
    cur.execute(
        "SELECT user_id FROM tickets WHERE message_id=?",
        (message_id,)
    )
    row = cur.fetchone()
    return row[0] if row else None