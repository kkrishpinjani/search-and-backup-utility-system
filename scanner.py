import os
import datetime
from database import connect

def scan_directory(directory):
    conn = connect()
    cursor = conn.cursor()

    # Clear old scan data
    cursor.execute("DELETE FROM files")

    file_count = 0
    dir_count = 0

    for root, dirs, files in os.walk(directory):
        dir_count += len(dirs)

        for file in files:
            try:
                path = os.path.join(root, file)
                size = os.path.getsize(path)
                extension = os.path.splitext(file)[1]
                modified = datetime.datetime.fromtimestamp(
                    os.path.getmtime(path)
                )

                cursor.execute("""
                    INSERT INTO files (name, path, size, extension, modified)
                    VALUES (?, ?, ?, ?, ?)
                """, (file, path, size, extension, modified))

                file_count += 1

            except Exception:
                # Skip files that cause permission errors
                continue

    conn.commit()
    conn.close()

    return file_count, dir_count