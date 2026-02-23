import sqlite3

DB_NAME = "project.db"

def connect():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        path TEXT,
        size INTEGER,
        extension TEXT,
        modified_date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        backup_name TEXT,
        backup_path TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()