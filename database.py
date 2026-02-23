import sqlite3

DB_NAME = "files.db"

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
        modified TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS backup_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        backup_name TEXT,
        source_paths TEXT,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restore_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        backup_name TEXT,
        restore_path TEXT,
        restored_at TEXT
    )
    """)

    conn.commit()
    conn.close()