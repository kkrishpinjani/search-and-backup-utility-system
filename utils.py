import hashlib
import os
import time
from pathlib import Path
from typing import Optional

def now_ts() -> int:
    return int(time.time())

def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def safe_ext(name: str) -> Optional[str]:
    # returns ".txt" style or None
    _, ext = os.path.splitext(name)
    return ext.lower() if ext else None

def human_size(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    x = float(n)
    for u in units:
        if x < 1024.0:
            return f"{x:.1f}{u}"
        x /= 1024.0
    return f"{x:.1f}PB"