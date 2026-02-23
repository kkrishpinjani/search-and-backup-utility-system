import os
import sqlite3
from pathlib import Path
import zipfile

from utils import now_ts

def restore_backup(
    conn: sqlite3.Connection,
    backup_id: int,
    target_dir: Path,
    overwrite_mode: str = "skip",  # 'skip' | 'overwrite' | 'rename'
) -> Path:
    row = conn.execute("SELECT id, zip_path FROM backups WHERE id = ?", (backup_id,)).fetchone()
    if not row:
        raise ValueError(f"Backup id {backup_id} not found")

    zip_path = Path(row["zip_path"]).expanduser().resolve()
    target_dir = target_dir.expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    restored = 0
    skipped = 0
    renamed = 0
    overwritten = 0

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            dest = (target_dir / member.filename).resolve()
            dest.parent.mkdir(parents=True, exist_ok=True)

            if dest.exists():
                if overwrite_mode == "skip":
                    skipped += 1
                    continue
                elif overwrite_mode == "overwrite":
                    overwritten += 1
                elif overwrite_mode == "rename":
                    # find a new name
                    base = dest.stem
                    suf = dest.suffix
                    i = 1
                    while True:
                        cand = dest.with_name(f"{base}({i}){suf}")
                        if not cand.exists():
                            dest = cand
                            renamed += 1
                            break
                        i += 1
                else:
                    raise ValueError("overwrite_mode must be skip|overwrite|rename")

            with zf.open(member, "r") as src, open(dest, "wb") as out:
                out.write(src.read())
            restored += 1

    summary = f"restored={restored}, skipped={skipped}, overwritten={overwritten}, renamed={renamed}"
    conn.execute(
        "INSERT INTO restores(backup_id, restored_ts, target_dir, overwrite_mode, summary) VALUES(?,?,?,?,?)",
        (backup_id, now_ts(), str(target_dir), overwrite_mode, summary),
    )
    conn.commit()
    return target_dir

def list_restores(conn: sqlite3.Connection, limit: int = 20):
    rows = conn.execute(
        """
        SELECT r.id, r.restored_ts, r.target_dir, r.overwrite_mode, r.summary, b.zip_path
        FROM restores r
        JOIN backups b ON b.id = r.backup_id
        ORDER BY r.restored_ts DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]