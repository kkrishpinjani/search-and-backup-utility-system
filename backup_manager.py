import os
import zipfile
from datetime import datetime
from database import get_connection

def create_backup(file_path):

    try:
        file_path = os.path.normpath(file_path)

        if not os.path.isfile(file_path):
            return f"File not found ❌"

        os.makedirs("backups", exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"backup_{timestamp}.zip"
        zip_path = os.path.join("backups", zip_name)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, arcname=os.path.basename(file_path))

        conn = get_connection()
        conn.execute(
            "INSERT INTO backups (file_name, backup_path, created_at) VALUES (?, ?, ?)",
            (os.path.basename(file_path), zip_path, datetime.now())
        )
        conn.commit()
        conn.close()

        return "Backup Created Successfully ✅"

    except PermissionError:
        return "Permission Denied ❌ (Run as Administrator)"

    except Exception as e:
        return f"Error: {str(e)}"