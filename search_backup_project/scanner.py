import os
import sqlite3

def scan_directory(path):
    conn = sqlite3.connect("files.db")
    cursor = conn.cursor()

    for root, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)

            cursor.execute("""
                INSERT INTO files (name, path)
                VALUES (?, ?)
            """, (file, full_path))

    conn.commit()
    conn.close()