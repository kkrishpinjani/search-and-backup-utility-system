import zipfile
import os
import datetime
from database import connect

def restore_backup(zip_path, restore_path, overwrite):
    if not os.path.exists(zip_path):
        return "Backup not found"

    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for member in zipf.namelist():
            target_path = os.path.join(restore_path, member)

            if os.path.exists(target_path):
                if not overwrite:
                    continue

            zipf.extract(member, restore_path)

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO restore_history (backup_name, restore_path, restored_at)
        VALUES (?, ?, ?)
    """, (zip_path, restore_path,
          datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))

    conn.commit()
    conn.close()

    return "Restore completed"