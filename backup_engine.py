import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple, Set
import zipfile

from utils import now_ts, file_sha256

def _all_files_under(path: Path) -> List[Path]:
    path = path.expanduser().resolve()
    if path.is_file():
        return [path]
    files: List[Path] = []
    for p in path.rglob("*"):
        if p.is_file():
            files.append(p)
    return files

def _common_root(paths: List[Path]) -> Path:
    """
    Best-effort common root for making stable relative paths inside ZIP.
    """
    if not paths:
        return Path.cwd()
    # Use parents for files, the folder itself for dirs
    bases = []
    for p in paths:
        p = p.expanduser().resolve()
        bases.append(p if p.is_dir() else p.parent)
    # pathlib has no commonpath; use os.path.commonpath
    import os
    common = os.path.commonpath([str(b) for b in bases])
    return Path(common)

def create_backup_zip_from_paths(
    conn: sqlite3.Connection,
    selected_paths: List[Path],
    backup_dir: Path,
    root_for_arcname: Optional[Path] = None,
    hash_detect: bool = False,
    notes: Optional[str] = None,
) -> Tuple[int, Path]:
    """
    Create a ZIP backup from user-selected files/folders.
    - selected_paths can include files or folders
    - ZIP will contain relative paths based on root_for_arcname or common root
    """
    if not selected_paths:
        raise ValueError("No files/folders selected for backup")

    created_ts = now_ts()
    zip_name = f"backup_{created_ts}.zip"
    zip_path = (backup_dir / zip_name).resolve()

    # Expand selection into files
    all_files: List[Path] = []
    for sp in selected_paths:
        sp = sp.expanduser().resolve()
        if not sp.exists():
            continue
        all_files.extend(_all_files_under(sp))

    # Remove duplicates
    seen: Set[str] = set()
    uniq_files: List[Path] = []
    for f in all_files:
        key = str(f.resolve())
        if key not in seen:
            seen.add(key)
            uniq_files.append(f)

    if not uniq_files:
        raise ValueError("No readable files found in selected paths")

    base_root = (root_for_arcname.expanduser().resolve() if root_for_arcname else _common_root(selected_paths))

    # Create zip
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in uniq_files:
            try:
                # try relative to base_root; fallback to just filename
                try:
                    arcname = str(f.relative_to(base_root))
                except Exception:
                    arcname = f.name
                zf.write(f, arcname=arcname)
            except (PermissionError, FileNotFoundError, OSError):
                continue

    # Log backup
    cur = conn.execute(
        """
        INSERT INTO backups(created_ts, zip_path, source_type, source_path, incremental, notes)
        VALUES(?,?,?,?,?,?)
        """,
        (created_ts, str(zip_path), "selection", str(base_root), 0, notes),
    )
    backup_id = cur.lastrowid

    # Log backup items
    for f in uniq_files:
        try:
            st = f.stat()
            sha = file_sha256(f) if hash_detect else None

            try:
                arcname = str(f.relative_to(base_root))
            except Exception:
                arcname = f.name

            conn.execute(
                """
                INSERT INTO backup_items(backup_id, file_path, arcname, size_bytes, modified_ts, sha256)
                VALUES(?,?,?,?,?,?)
                """,
                (backup_id, str(f), arcname, int(st.st_size), int(st.st_mtime), sha),
            )
        except Exception:
            continue

    conn.commit()
    return backup_id, zip_path

def create_backup_zip(
    conn: sqlite3.Connection,
    source_path: Path,
    backup_dir: Path,
    incremental: bool = False,
    hash_detect: bool = False,
    notes: Optional[str] = None,
) -> Tuple[int, Path]:
    """
    Kept for backward compatibility (backup a single file/folder path).
    """
    return create_backup_zip_from_paths(
        conn=conn,
        selected_paths=[source_path],
        backup_dir=backup_dir,
        root_for_arcname=source_path if source_path.is_dir() else source_path.parent,
        hash_detect=hash_detect,
        notes=notes,
    )

def list_backups(conn: sqlite3.Connection, limit: int = 20):
    rows = conn.execute(
        "SELECT id, created_ts, zip_path, source_path, incremental, notes FROM backups ORDER BY created_ts DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]