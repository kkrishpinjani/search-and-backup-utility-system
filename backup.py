import zipfile
import os
import datetime
from database import connect

def create_backup(selected_ids):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT path FROM files WHERE id IN ({})".format(
            ",".join("?"*len(selected_ids))
        ),
        selected_ids
    )

    paths = [row[0] for row in cursor.fetchall()]

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backups/backup_{timestamp}.zip"

    with zipfile.ZipFile(backup_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for path in paths:
            if os.path.exists(path):
                zipf.write(path, os.path.basename(path))

    cursor.execute("""
        INSERT INTO backup_history (backup_name, source_paths, created_at)
        VALUES (?, ?, ?)
    """, (backup_name, ",".join(paths), timestamp))

    conn.commit()
    conn.close()

    return backup_name