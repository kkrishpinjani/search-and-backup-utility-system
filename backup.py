import zipfile
import os
import datetime
from database import connect

def create_backup(file_path):
    if not os.path.exists("backups"):
        os.makedirs("backups")

    backup_name = f"backup_{int(datetime.datetime.now().timestamp())}.zip"
    backup_path = os.path.join("backups", backup_name)

    with zipfile.ZipFile(backup_path, 'w') as zipf:
        zipf.write(file_path, os.path.basename(file_path))

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO backups (backup_name, backup_path, created_at)
        VALUES (?, ?, ?)
    """, (backup_name, backup_path, str(datetime.datetime.now())))

    conn.commit()
    conn.close()

    print("Backup Created ")