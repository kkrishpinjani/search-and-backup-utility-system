import os
import sqlite3
import zipfile
from flask import Flask, render_template, request

app = Flask(__name__)

# ================= BASE DIRECTORY (Portable) =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, "data.db")

conn = sqlite3.connect(DATABASE, check_same_thread=False)
cursor = conn.cursor()

# ================= TABLES =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    path TEXT,
    size INTEGER,
    extension TEXT,
    modified TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS backups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    created_at TEXT
)
""")

conn.commit()

# ================= FOLDERS =================
BACKUP_FOLDER = os.path.join(BASE_DIR, "backups")
EXTRACT_FOLDER = os.path.join(BASE_DIR, "Extracts")

os.makedirs(BACKUP_FOLDER, exist_ok=True)
os.makedirs(EXTRACT_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():

    message = ""
    files = []

    if request.method == "POST":

        # ================= SCAN =================
        if "scan" in request.form:

            uploaded_files = request.files.getlist("folder_files")

            if uploaded_files:
                cursor.execute("DELETE FROM files")

                for file in uploaded_files:
                    if file.filename == "":
                        continue

                    relative_path = file.filename.replace("\\", "/")
                    name = relative_path.split("/")[-1]
                    extension = "." + name.split(".")[-1] if "." in name else ""
                    size = len(file.read())
                    file.seek(0)

                    cursor.execute("""
                        INSERT INTO files (name, path, size, extension, modified)
                        VALUES (?, ?, ?, ?, datetime('now'))
                    """, (name, relative_path, size, extension))

                conn.commit()
                message = "Scan completed successfully."

        # ================= SEARCH =================
        elif "search" in request.form:
            name = request.form.get("name", "")
            cursor.execute("SELECT * FROM files WHERE name LIKE ?", (f"%{name}%",))
            files = cursor.fetchall()

        # ================= BACKUP (ONLY FILE NAME) =================
        elif "backup_selected" in request.form:

            selected_ids = request.form.getlist("selected_files")
            title = request.form.get("backup_title", "").strip()

            if not title:
                message = "Please enter backup title."

            elif not selected_ids:
                message = "No files selected."

            else:
                cursor.execute(
                    f"SELECT * FROM files WHERE id IN ({','.join(['?']*len(selected_ids))})",
                    selected_ids
                )
                selected_files = cursor.fetchall()

                zip_path = os.path.join(BACKUP_FOLDER, f"{title}.zip")

                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for file in selected_files:
                        file_name = file[1]  # ONLY FILE NAME
                        zf.writestr(file_name, f"Backup copy of {file_name}")

                cursor.execute(
                    "INSERT INTO backups (title, created_at) VALUES (?, datetime('now'))",
                    (title,)
                )
                conn.commit()

                message = f"Backup '{title}' created successfully."

        # ================= RESTORE =================
        elif "restore" in request.form:

            title = request.form.get("restore_title", "").strip()

            zip_path = os.path.join(BACKUP_FOLDER, f"{title}.zip")

            if not os.path.exists(zip_path):
                message = "Backup title not found."

            else:
                restore_path = os.path.join(EXTRACT_FOLDER, title)
                os.makedirs(restore_path, exist_ok=True)

                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(restore_path)

                message = f"Backup '{title}' restored inside Extracts folder."

    # ================= BACKUP HISTORY =================
    cursor.execute("SELECT * FROM backups ORDER BY id DESC")
    backup_history = cursor.fetchall()

    return render_template("index.html",
                           message=message,
                           files=files,
                           backup_history=backup_history)


if __name__ == "__main__":
    app.run(debug=True)