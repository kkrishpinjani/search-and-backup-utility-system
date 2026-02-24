import os
import zipfile
import sqlite3

def restore_backup(zip_path, restore_location):
    if not os.path.exists(restore_location):
        os.makedirs(restore_location)

    with zipfile.ZipFile(zip_path, "r") as zipf:
        zipf.extractall(restore_location)

    file_name = os.path.basename(zip_path)

    conn = sqlite3.connect("files.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO history (file_name, action, location)
        VALUES (?, ?, ?)
    """, (file_name, "Restore", restore_location))
    conn.commit()
    conn.close()