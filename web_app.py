from pathlib import Path
from flask import Flask, request, jsonify, render_template
import tkinter as tk
from tkinter import filedialog

import config
import db as dbmod
from scanner import scan_directory
from search_engine import search_files, suggest_files
from backup_engine import create_backup_zip, create_backup_zip_from_paths, list_backups
from restore_engine import restore_backup, list_restores

app = Flask(__name__)

def get_conn():
    conn = dbmod.connect(config.DB_PATH)
    dbmod.init_db(conn, Path(__file__).parent / "schema.sql")
    return conn

@app.get("/api/browse")
def api_browse():
    # This opens a real OS folder picker window
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    root.attributes('-topmost', True) # Bring picker to front
    folder_selected = filedialog.askdirectory()
    root.destroy()
    return jsonify({"path": folder_selected})

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/api/scan")
def api_scan():
    data = request.get_json(force=True)
    root = data.get("root")
    compute_hash = bool(data.get("compute_hash", False))
    if not root:
        return jsonify({"ok": False, "error": "root is required"}), 400

    root_path = Path(root).expanduser()
    if not root_path.exists() or not root_path.is_dir():
        return jsonify({"ok": False, "error": "root must be an existing directory"}), 400

    conn = get_conn()
    count = 0
    try:
        for rec in scan_directory(root_path, compute_hash=compute_hash):
            dbmod.upsert_file(conn, rec)
            count += 1
            if count % 500 == 0:
                conn.commit()
        conn.commit()
        return jsonify({"ok": True, "indexed": count})
    finally:
        conn.close()

@app.get("/api/suggest")
def api_suggest():
    q = (request.args.get("q") or "").strip()
    limit = int(request.args.get("limit", "10"))
    if not q:
        return jsonify({"ok": True, "suggestions": []})

    conn = get_conn()
    try:
        suggestions = suggest_files(conn, q=q, limit=limit)
        return jsonify({"ok": True, "suggestions": suggestions})
    finally:
        conn.close()

@app.post("/api/search")
def api_search():
    data = request.get_json(force=True)

    name_like = data.get("name_like") or None
    extension = data.get("extension") or None

    size_min = data.get("size_min")
    size_max = data.get("size_max")
    size_range = None
    if size_min is not None and size_max is not None and str(size_min) != "" and str(size_max) != "":
        size_range = (int(size_min), int(size_max))

    date_from = data.get("date_from_ts")
    date_to = data.get("date_to_ts")
    date_range = None
    if date_from and date_to:
        date_range = (int(date_from), int(date_to))

    sort_by = data.get("sort_by") or "name"
    descending = bool(data.get("descending", False))
    limit = int(data.get("limit", 50))

    conn = get_conn()
    try:
        rows = search_files(
            conn=conn,
            name_like=name_like,
            extension=extension,
            size_range=size_range,
            date_range=date_range,
            sort_by=sort_by,
            descending=descending,
            limit=limit
        )
        return jsonify({"ok": True, "results": rows})
    finally:
        conn.close()

# ✅ NEW: backup only selected files (from scanned/search results)
@app.post("/api/backup_selection")
def api_backup_selection():
    """
    body:
    {
      "paths": ["C:\\...\\a.txt", "C:\\...\\b.pdf", "C:\\...\\folder1"],
      "root_for_arcname": "C:\\Users\\Vineet\\Desktop\\testdata" (optional),
      "hash_detect": false,
      "notes": "optional"
    }
    """
    data = request.get_json(force=True)
    paths = data.get("paths") or []
    root_for_arcname = data.get("root_for_arcname") or None
    hash_detect = bool(data.get("hash_detect", False))
    notes = data.get("notes") or "Backup from selected files"

    if not isinstance(paths, list) or len(paths) == 0:
        return jsonify({"ok": False, "error": "paths must be a non-empty list"}), 400

    selected = [Path(p) for p in paths]
    root = Path(root_for_arcname) if root_for_arcname else None

    conn = get_conn()
    try:
        backup_id, zip_path = create_backup_zip_from_paths(
            conn=conn,
            selected_paths=selected,
            backup_dir=config.BACKUP_DIR,
            root_for_arcname=root,
            hash_detect=hash_detect,
            notes=notes,
        )
        return jsonify({"ok": True, "backup_id": backup_id, "zip_path": str(zip_path)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    finally:
        conn.close()

@app.post("/api/backup")
def api_backup():
    data = request.get_json(force=True)
    source = data.get("source")
    incremental = bool(data.get("incremental", False))
    hash_detect = bool(data.get("hash_detect", False))
    notes = data.get("notes") or None

    if not source:
        return jsonify({"ok": False, "error": "source is required"}), 400

    src = Path(source).expanduser()
    if not src.exists():
        return jsonify({"ok": False, "error": "source path does not exist"}), 400

    conn = get_conn()
    try:
        backup_id, zip_path = create_backup_zip(
            conn=conn,
            source_path=src,
            backup_dir=config.BACKUP_DIR,
            incremental=incremental,
            hash_detect=hash_detect,
            notes=notes
        )
        return jsonify({"ok": True, "backup_id": backup_id, "zip_path": str(zip_path)})
    finally:
        conn.close()

@app.get("/api/backups")
def api_backups():
    conn = get_conn()
    try:
        rows = list_backups(conn, limit=200)
        return jsonify({"ok": True, "backups": rows})
    finally:
        conn.close()

@app.post("/api/restore")
def api_restore():
    data = request.get_json(force=True)
    backup_id = data.get("backup_id")
    target_dir = data.get("target_dir")
    overwrite_mode = (data.get("overwrite_mode") or "skip").strip()

    if not backup_id or not target_dir:
        return jsonify({"ok": False, "error": "backup_id and target_dir are required"}), 400

    tgt = Path(target_dir).expanduser()
    conn = get_conn()
    try:
        restore_backup(conn, int(backup_id), tgt, overwrite_mode=overwrite_mode)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    finally:
        conn.close()

@app.get("/api/restores")
def api_restores():
    conn = get_conn()
    try:
        rows = list_restores(conn, limit=200)
        return jsonify({"ok": True, "restores": rows})
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)