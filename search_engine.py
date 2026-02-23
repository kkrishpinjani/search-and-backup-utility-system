import sqlite3
from typing import Any, Dict, List, Optional, Tuple

ALLOWED_SORT = {
    "name": "name",
    "size": "size_bytes",
    "modified": "modified_ts",
    "ext": "extension",
}

def search_files(
    conn: sqlite3.Connection,
    name_like: Optional[str] = None,
    extension: Optional[str] = None,
    size_range: Optional[Tuple[int, int]] = None,
    date_range: Optional[Tuple[int, int]] = None,
    sort_by: str = "name",
    descending: bool = False,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    where = []
    params: List[Any] = []

    if name_like:
        where.append("name LIKE ?")
        params.append(f"%{name_like}%")

    if extension:
        ext = extension.lower()
        if not ext.startswith("."):
            ext = "." + ext
        where.append("extension = ?")
        params.append(ext)

    if size_range:
        where.append("size_bytes BETWEEN ? AND ?")
        params.extend([size_range[0], size_range[1]])

    if date_range:
        where.append("modified_ts BETWEEN ? AND ?")
        params.extend([date_range[0], date_range[1]])

    sql = "SELECT id, name, path, size_bytes, extension, modified_ts, sha256 FROM files"
    if where:
        sql += " WHERE " + " AND ".join(where)

    sort_col = ALLOWED_SORT.get(sort_by, "name")
    sql += f" ORDER BY {sort_col} {'DESC' if descending else 'ASC'}"
    sql += " LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]

def suggest_files(conn: sqlite3.Connection, q: str, limit: int = 10) -> List[Dict[str, Any]]:
    q = q.strip()
    if not q:
        return []

    prefix_rows = conn.execute(
        """
        SELECT name, path
        FROM files
        WHERE name LIKE ?
        ORDER BY name ASC
        LIMIT ?
        """,
        (f"{q}%", limit),
    ).fetchall()

    suggestions = [dict(r) for r in prefix_rows]
    if len(suggestions) >= limit:
        return suggestions

    remaining = limit - len(suggestions)
    existing_paths = {s["path"] for s in suggestions}

    contains_rows = conn.execute(
        """
        SELECT name, path
        FROM files
        WHERE name LIKE ?
        ORDER BY name ASC
        LIMIT ?
        """,
        (f"%{q}%", limit * 3),
    ).fetchall()

    for r in contains_rows:
        d = dict(r)
        if d["path"] in existing_paths:
            continue
        suggestions.append(d)
        existing_paths.add(d["path"])
        remaining -= 1
        if remaining <= 0:
            break

    return suggestions