# Personal Search & Backup Utility System

## Features
- Recursively scans directories and stores file metadata (name, path, size, extension, modified time, optional SHA256)
- Search by name, extension, size range, date range + sort options
- Create ZIP backups (full or incremental)
- Restore backups with overwrite handling (skip/overwrite/rename)
- Backup and restore history logs (SQLite)

## Requirements
- Python 3.10+

## Setup
```bash
cd search_backup_utility
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

 python web_app.py 