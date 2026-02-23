from pathlib import Path
from typing import Iterator, Dict, Any
import os

from utils import now_ts, safe_ext, file_sha256

def scan_directory(root: Path, compute_hash: bool = False) -> Iterator[Dict[str, Any]]:
    root = root.expanduser().resolve()
    indexed_ts = now_ts()

    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            fpath = (Path(dirpath) / fname)
            try:
                st = fpath.stat()
                rec = {
                    "name": fpath.name,
                    "path": str(fpath),
                    "size_bytes": int(st.st_size),
                    "extension": safe_ext(fpath.name),
                    "modified_ts": int(st.st_mtime),
                    "indexed_ts": indexed_ts,
                }
                if compute_hash:
                    rec["sha256"] = file_sha256(fpath)
                yield rec
            except (PermissionError, FileNotFoundError, OSError):
                # skip unreadable files
                continue