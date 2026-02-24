from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sqlite3

from database import create_tables
from scanner import scan_directory
from search import search_by_name
from backup import create_backup
from restore import restore_backup

app = Flask(__name__)
app.secret_key = "super_secret_key"

create_tables()


@app.route("/")
def home():
    return render_template("index.html")


# ================= SCAN =================
@app.route("/scan", methods=["POST"])
def scan():
    path = request.form.get("path")

    if not path or not os.path.isdir(path):
        flash("❌ Invalid directory path")
        return redirect(url_for("home"))

    scan_directory(path)
    flash("✅ Directory scanned successfully")
    return redirect(url_for("home"))


# ================= SEARCH =================
@app.route("/search", methods=["POST"])
def search():
    name = request.form.get("name")

    if not name:
        flash("❌ Enter file name")
        return redirect(url_for("home"))

    results = search_by_name(name)

    if results:
        flash(f"✅ Found {len(results)} file(s)")
    else:
        flash("⚠️ No file found")

    return redirect(url_for("home"))


# ================= BACKUP =================
@app.route("/backup", methods=["POST"])
def backup():
    name = request.form.get("path")

    if not name:
        flash("❌ Enter file name or full path")
        return redirect(url_for("home"))

    # If full path given
    if os.path.isfile(name):
        zip_path = create_backup(name)
        flash(f"✅ Backup created at {zip_path}")
        return redirect(url_for("home"))

    # Else search in DB
    results = search_by_name(name)

    if results:
        full_path = results[0][2]
        zip_path = create_backup(full_path)
        flash(f"✅ Backup created at {zip_path}")
    else:
        flash("❌ File not found. Scan directory first.")

    return redirect(url_for("home"))


# ================= RESTORE =================
@app.route("/restore", methods=["POST"])
def restore():
    zip_name = request.form.get("zip_path")
    restore_location = request.form.get("restore_location")

    if not zip_name:
        flash("❌ Enter backup file name (example: test1.txt.zip)")
        return redirect(url_for("home"))

    zip_path = os.path.join("backups", zip_name)

    if not os.path.isfile(zip_path):
        flash("❌ Backup zip file not found inside backups folder")
        return redirect(url_for("home"))

    if not restore_location:
        flash("❌ Enter restore location")
        return redirect(url_for("home"))

    restore_backup(zip_path, restore_location)
    flash("✅ Restore completed successfully")
    return redirect(url_for("home"))


# ================= HISTORY =================
@app.route("/history")
def history():
    conn = sqlite3.connect("files.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT file_name, action, location, timestamp
        FROM history
        ORDER BY timestamp DESC
    """)

    records = cursor.fetchall()
    conn.close()

    return render_template("history.html", records=records)


if __name__ == "__main__":
    app.run(debug=True)