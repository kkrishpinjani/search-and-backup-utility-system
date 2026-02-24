Personal Search & Backup Utility System

A comprehensive file management utility built with Python (Flask) and SQLite. This system allows users to index local directories, perform advanced metadata searches, create compressed ZIP backups, and restore files with intelligent conflict resolution.

🌟 Key Features

Recursive File Scanning: Deep-scan local directories to index file metadata (name, path, size, extension, modified date).

Advanced Search Engine: Filter files by name, extension, size ranges, and modification dates with real-time suggestions.

Native OS Integration: Includes a built-in folder picker for easy directory selection without manual typing.

Secure ZIP Backups: Standardized compression for selected files and folders with full history logging.

Intelligent Restoration: Restore backups to any location with three conflict modes: Skip, Overwrite, or Rename (auto-versioning).

Hash-Based Detection: Optional SHA256 hashing to identify unique file content and support incremental-ready logic.

🛠️ Tech Stack

Backend: Python 3.10+, Flask

Database: SQLite3 (Relational storage for metadata and history)

Frontend: HTML5, CSS3 (Bootstrap 5), JavaScript (Vanilla ES6+)

OS Bridge: tkinter (Native folder browsing)

📂 Project Structure

Plaintext
├── data/               # Stores app.db and generated ZIP backups
├── static/             # Frontend assets (styles.css, app.js)
├── templates/          # HTML templates (index.html)
├── backup_engine.py    # ZIP creation and metadata logging
├── restore_engine.py   # Extraction logic and conflict handling
├── scanner.py          # Recursive walker and metadata extractor
├── search_engine.py    # Database queries and filters
├── web_app.py          # Flask routes and API endpoints
├── db.py               # Database connection and initialization
├── schema.sql          # SQLite table definitions
├── config.py           # Global paths and configuration
└── utils.py            # Hashing and timestamp helpers

🚀 Getting Started
1. Installation
Ensure you have Python 3.10 or higher installed.

Bash
# Clone the project
cd search_backup_utility

# Create a virtual environment
python -m venv venv

# Activate the environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install requirements (if any)
pip install flask
2. Running the Application
Bash
python web_app.py
The app will start at http://127.0.0.1:5000

📖 Usage Instructions
Index Files: In the Scan section, click the "Browse" button to select a folder. Click Scan to index all files into the database.

Search: Use the Search tab to find files. You can filter by extension (e.g., .pdf) or size.

Backup: Select specific files from your search results and click Backup Selected to create a ZIP archive.

Restore: Navigate to the History tab to see past backups. Select a target directory and a conflict mode to restore your files.

📊 Database Design
The system uses four primary tables to ensure data integrity:

files: Stores indexed metadata for fast searching.

backups: Stores high-level data about each ZIP archive created.

backup_items: Links specific files to their respective ZIP archives.

restores: Logs every restoration event for audit purposes.

🛡️ Academic Integrity
This project was developed independently as part of the Internship Assignment. All core logic for scanning, searching, and ZIP management is original code, designed to meet the specified functional and performance criteria.