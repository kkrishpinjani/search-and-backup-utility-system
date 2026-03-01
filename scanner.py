import os
import string
from datetime import datetime
from database import get_connection

def scan_directory(directory):
    conn = get_connection()
    c = conn.cursor()

    for root, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.path.normpath(os.path.join(root, file))
            try:
                size = os.path.getsize(full_path)
                modified = datetime.fromtimestamp(
                    os.path.getmtime(full_path)
                )

                c.execute("""
                INSERT OR REPLACE INTO files
                (name, path, size, modified_date)
                VALUES (?, ?, ?, ?)
                """, (file, full_path, size, modified))
            except:
                continue

    conn.commit()
    conn.close()

def scan_all_drives():
    for drive in string.ascii_uppercase:
        path = f"{drive}:\\"
        if os.path.exists(path):
            try:
                scan_directory(path)
            except:
                continue