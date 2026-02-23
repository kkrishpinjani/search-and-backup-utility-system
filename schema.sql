PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  path TEXT NOT NULL UNIQUE,
  size_bytes INTEGER NOT NULL,
  extension TEXT,
  modified_ts INTEGER NOT NULL,
  sha256 TEXT,
  indexed_ts INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_files_name ON files(name);
CREATE INDEX IF NOT EXISTS idx_files_ext ON files(extension);
CREATE INDEX IF NOT EXISTS idx_files_size ON files(size_bytes);
CREATE INDEX IF NOT EXISTS idx_files_modified ON files(modified_ts);

CREATE TABLE IF NOT EXISTS backups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_ts INTEGER NOT NULL,
  zip_path TEXT NOT NULL,
  source_type TEXT NOT NULL,           -- 'file' or 'folder'
  source_path TEXT NOT NULL,
  incremental INTEGER NOT NULL DEFAULT 0,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS backup_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  backup_id INTEGER NOT NULL,
  file_path TEXT NOT NULL,
  arcname TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  modified_ts INTEGER NOT NULL,
  sha256 TEXT,
  FOREIGN KEY (backup_id) REFERENCES backups(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_backup_items_backup ON backup_items(backup_id);

CREATE TABLE IF NOT EXISTS restores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  backup_id INTEGER NOT NULL,
  restored_ts INTEGER NOT NULL,
  target_dir TEXT NOT NULL,
  overwrite_mode TEXT NOT NULL,        -- 'skip', 'overwrite', 'rename'
  summary TEXT,
  FOREIGN KEY (backup_id) REFERENCES backups(id)
);