import sqlite3
from sqlite3 import Connection

def get_connection() -> Connection:
    conn = sqlite3.connect('posts.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            creator_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            is_private INTEGER NOT NULL,
            tags TEXT
        )
    ''')
    conn.commit()
    conn.close()
