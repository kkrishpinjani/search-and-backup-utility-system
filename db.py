import sqlite3
from pathlib import Path
from typing import Iterable, Optional, Any, Dict

def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(conn: sqlite3.Connection, schema_path: Path) -> None:
    sql = schema_path.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()

def upsert_file(conn: sqlite3.Connection, rec: Dict[str, Any]) -> None:
    # path is UNIQUE; insert or update
    conn.execute(
        """
        INSERT INTO files(name, path, size_bytes, extension, modified_ts, sha256, indexed_ts)
        VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(path) DO UPDATE SET
          name=excluded.name,
          size_bytes=excluded.size_bytes,
          extension=excluded.extension,
          modified_ts=excluded.modified_ts,
          sha256=excluded.sha256,
          indexed_ts=excluded.indexed_ts
        """,
        (
            rec["name"],
            rec["path"],
            rec["size_bytes"],
            rec.get("extension"),
            rec["modified_ts"],
            rec.get("sha256"),
            rec["indexed_ts"],
        ),
    )