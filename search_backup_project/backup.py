import os
import zipfile
import sqlite3

def create_backup(path):
    if not os.path.exists("backups"):
        os.makedirs("backups")

    file_name = os.path.basename(path)
    zip_path = os.path.join("backups", file_name + ".zip")

    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(path, arcname=file_name)

    conn = sqlite3.connect("files.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO history (file_name, action, location)
        VALUES (?, ?, ?)
    """, (file_name, "Backup", zip_path))
    conn.commit()
    conn.close()

    return zip_path