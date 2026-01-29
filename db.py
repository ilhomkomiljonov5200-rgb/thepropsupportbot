import sqlite3
from datetime import datetime


class Database:
    def __init__(self, path: str = "support.db"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

        self._create_tables()


    # =================================================
    # TABLES
    # =================================================
    def _create_tables(self):
        # USERS
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            full_name TEXT,
            lang TEXT DEFAULT 'uz',
            created_at TEXT
        )
        """)

        # ✅ ticket number = id
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            thread_id INTEGER,
            status TEXT DEFAULT 'open',
            created_at TEXT
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER,
            sender TEXT,
            text TEXT,
            created_at TEXT
        )
        """)

        self.conn.commit()


    # =================================================
    # USERS
    # =================================================
    def add_user(self, user_id: int, full_name: str):
        self.cur.execute("""
        INSERT OR IGNORE INTO users (user_id, full_name, created_at)
        VALUES (?, ?, ?)
        """, (user_id, full_name, datetime.now().isoformat()))
        self.conn.commit()


    def set_lang(self, user_id: int, lang: str):
        self.cur.execute("""
        UPDATE users SET lang=? WHERE user_id=?
        """, (lang, user_id))
        self.conn.commit()


    def get_lang(self, user_id: int):
        row = self.cur.execute("""
        SELECT lang FROM users WHERE user_id=?
        """, (user_id,)).fetchone()
        return row["lang"] if row else "uz"


    # =================================================
    # TICKETS
    # =================================================
    def create_ticket(self, user_id: int, thread_id: int) -> int:
        self.cur.execute("""
        INSERT INTO tickets (user_id, thread_id, created_at)
        VALUES (?, ?, ?)
        """, (user_id, thread_id, datetime.now().isoformat()))

        self.conn.commit()

        # ✅ 1,2,3,4...
        return self.cur.lastrowid


    def close_ticket(self, ticket_id: int):
        self.cur.execute("""
        UPDATE tickets SET status='closed' WHERE id=?
        """, (ticket_id,))
        self.conn.commit()


    def get_open_ticket(self, user_id: int):
        row = self.cur.execute("""
        SELECT id FROM tickets
        WHERE user_id=? AND status='open'
        ORDER BY id DESC LIMIT 1
        """, (user_id,)).fetchone()

        return row["id"] if row else None


    # =================================================
    # REPLY SYSTEM HELPERS
    # =================================================
    def get_ticket_info(self, ticket_id: int):
        return self.cur.execute("""
        SELECT * FROM tickets WHERE id=?
        """, (ticket_id,)).fetchone()


    def get_user_by_ticket(self, ticket_id: int):
        row = self.cur.execute("""
        SELECT user_id FROM tickets WHERE id=?
        """, (ticket_id,)).fetchone()
        return row["user_id"] if row else None


    def get_thread_by_ticket(self, ticket_id: int):
        row = self.cur.execute("""
        SELECT thread_id FROM tickets WHERE id=?
        """, (ticket_id,)).fetchone()
        return row["thread_id"] if row else None


    def add_admin_reply(self, ticket_id: int, text: str):
        self.add_message(ticket_id, "admin", text)


    # =================================================
    # MESSAGES
    # =================================================
    def add_message(self, ticket_id: int, sender: str, text: str):
        self.cur.execute("""
        INSERT INTO messages (ticket_id, sender, text, created_at)
        VALUES (?, ?, ?, ?)
        """, (ticket_id, sender, text, datetime.now().isoformat()))
        self.conn.commit()


    def get_ticket_messages(self, ticket_id: int):
        return self.cur.execute("""
        SELECT * FROM messages WHERE ticket_id=?
        ORDER BY id
        """, (ticket_id,)).fetchall()


    # =================================================
    # STATS
    # =================================================
    def stats(self):
        users = self.cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        tickets = self.cur.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
        open_tickets = self.cur.execute(
            "SELECT COUNT(*) FROM tickets WHERE status='open'"
        ).fetchone()[0]

        return {
            "users": users,
            "tickets": tickets,
            "open": open_tickets
        }
