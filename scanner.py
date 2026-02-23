import os
import datetime
from database import connect

def scan_directory(folder_path):
    conn = connect()
    cursor = conn.cursor()

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            size = os.path.getsize(full_path)
            modified = datetime.datetime.fromtimestamp(
                os.path.getmtime(full_path)
            )

            name, extension = os.path.splitext(file)

            cursor.execute("""
                INSERT INTO files (name, path, size, extension, modified_date)
                VALUES (?, ?, ?, ?, ?)
            """, (name, full_path, size, extension, str(modified)))

    conn.commit()
    conn.close()
    print("Scanning Completed ")