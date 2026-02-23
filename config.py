from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"

DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"
UPLOAD_DIR = DATA_DIR / "uploads"

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Optional: 200 MB max upload (change as needed)
MAX_CONTENT_LENGTH = 200 * 1024 * 1024