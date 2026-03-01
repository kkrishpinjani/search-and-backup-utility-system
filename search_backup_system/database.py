import sqlite3

DB_NAME = "database.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY,
        name TEXT,
        path TEXT UNIQUE,
        size INTEGER,
        modified_date TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY,
        file_name TEXT,
        backup_path TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()