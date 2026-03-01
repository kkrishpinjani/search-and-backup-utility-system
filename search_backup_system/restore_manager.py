import zipfile
import os
from database import get_connection

def restore_backup(backup_id):

    conn = get_connection()
    backup = conn.execute(
        "SELECT backup_path FROM backups WHERE id=?",
        (backup_id,)
    ).fetchone()
    conn.close()

    if not backup:
        return "Backup not found ❌"

    restore_folder = "restored_files"
    os.makedirs(restore_folder, exist_ok=True)

    with zipfile.ZipFile(backup[0], "r") as zipf:
        zipf.extractall(restore_folder)

    return "Restore Completed ✅"