from flask import Flask, render_template, request, jsonify
from database import init_db, get_connection
from scanner import scan_all_drives
from backup_manager import create_backup
from restore_manager import restore_backup

app = Flask(__name__)
init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    message = None

    if request.method == "POST":

        if "scan" in request.form:
            scan_all_drives()
            message = "Scan Completed ✅"

        if "backup_path" in request.form:
            message = create_backup(request.form["backup_path"])

        if "restore_id" in request.form:
            message = restore_backup(request.form["restore_id"])

    conn = get_connection()
    backups = conn.execute(
        "SELECT * FROM backups ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template("index.html",
                           message=message,
                           backups=backups)

@app.route("/search")
def search():

    name = request.args.get("name", "")
    extension = request.args.get("ext", "")
    size = request.args.get("size", "")

    query = "SELECT name, path, size, modified_date FROM files WHERE 1=1"
    params = []

    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")

    if extension:
        query += " AND name LIKE ?"
        params.append(f"%{extension}")

    if size:
        query += " AND size <= ?"
        params.append(size)

    query += " LIMIT 50"

    conn = get_connection()
    results = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([
        {
            "name": r[0],
            "path": r[1],
            "size": r[2],
            "modified_date": r[3]
        }
        for r in results
    ])

if __name__ == "__main__":
    app.run(debug=True)