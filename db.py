import sqlite3

conn = sqlite3.connect("support.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    group_msg_id INTEGER,
    problem_type TEXT,
    text TEXT,
    status TEXT
)
""")

conn.commit()


def add_ticket(user_id, problem_type, text, group_msg_id):
    cursor.execute(
        "INSERT INTO tickets (user_id, problem_type, text, group_msg_id, status) VALUES (?, ?, ?, ?, ?)",
        (user_id, problem_type, text, group_msg_id, "open")
    )
    conn.commit()


def get_user(group_msg_id):
    cursor.execute(
        "SELECT user_id FROM tickets WHERE group_msg_id=?",
        (group_msg_id,)
    )
    row = cursor.fetchone()
    return row[0] if row else None