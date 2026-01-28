import sqlite3

conn = sqlite3.connect("support.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    group_msg_id INTEGER
)
""")

conn.commit()


def add_ticket(user_id: int, group_msg_id: int):
    cursor.execute(
        "INSERT INTO tickets (user_id, group_msg_id) VALUES (?, ?)",
        (user_id, group_msg_id)
    )
    conn.commit()


def get_user(group_msg_id: int):
    cursor.execute(
        "SELECT user_id FROM tickets WHERE group_msg_id=?",
        (group_msg_id,)
    )
    row = cursor.fetchone()
    return row[0] if row else None