from flask import Flask, render_template, request, jsonify
from database import create_tables, connect
from scanner import scan_directory
from search import search_files
from backup import create_backup
from restore import restore_backup

app = Flask(__name__)
create_tables()


@app.route("/", methods=["GET", "POST"])
def home():

    results = []
    message = ""

    conn = connect()
    cursor = conn.cursor()

    if request.method == "POST":

        # ================= SCAN =================
        if "scan" in request.form:
            folder = request.form.get("folder")

            if folder:
                try:
                    files, dirs = scan_directory(folder)
                    message = (
                        f"Scan completed successfully! "
                        f"📁 {dirs} directories and 📄 {files} files scanned."
                    )
                except Exception as e:
                    message = f"Scan Error: {str(e)}"

        # ================= SEARCH =================
        if "search" in request.form:
            results = search_files(
                request.form.get("name"),
                request.form.get("extension"),
                request.form.get("min_size"),
                request.form.get("max_size"),
                request.form.get("start_date"),
                request.form.get("end_date"),
                request.form.get("sort_by")
            )

        # ================= BACKUP =================
        if "backup" in request.form:
            selected_ids = request.form.getlist("file_ids")

            if selected_ids:
                try:
                    backup_name = create_backup(selected_ids)
                    message = f"Backup created successfully: {backup_name}"
                except Exception as e:
                    message = f"Backup Error: {str(e)}"
            else:
                message = "Please select files to backup."

        # ================= RESTORE =================
        if "restore" in request.form:
            zip_path = request.form.get("zip_path")
            restore_path = request.form.get("restore_path")
            overwrite = request.form.get("overwrite") == "on"

            try:
                result = restore_backup(zip_path, restore_path, overwrite)
                message = result
            except Exception as e:
                message = f"Restore Error: {str(e)}"

    # ================= LOAD HISTORY =================
    cursor.execute("SELECT * FROM backup_history ORDER BY id DESC")
    backups = cursor.fetchall()

    cursor.execute("SELECT * FROM restore_history ORDER BY id DESC")
    restores = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        results=results,
        backups=backups,
        restores=restores,
        message=message
    )


# ================= GOOGLE STYLE SUGGESTION =================
@app.route("/suggest")
def suggest():
    query = request.args.get("q", "")

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM files
        WHERE name LIKE ?
        LIMIT 5
    """, (f"%{query}%",))

    results = [row[0] for row in cursor.fetchall()]
    conn.close()

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)