import sqlite3

conn = sqlite3.connect("support.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    group_msg_id INTEGER PRIMARY KEY,
    user_id INTEGER
)
""")
conn.commit()


def add_ticket(user_id, group_msg_id):
    cur.execute(
        "INSERT OR REPLACE INTO tickets VALUES (?, ?)",
        (group_msg_id, user_id)
    )
    conn.commit()


def get_user(group_msg_id):
    cur.execute(
        "SELECT user_id FROM tickets WHERE group_msg_id=?",
        (group_msg_id,)
    )
    row = cur.fetchone()
    return row[0] if row else None