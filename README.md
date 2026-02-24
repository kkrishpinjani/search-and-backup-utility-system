# Personal Search & Backup Utility

## 📌 Project Overview

The **Personal Search & Backup Utility** is a web-based file management system that allows users to:

* Scan and index files from a selected directory
* Search files using multiple filters (name, extension, size, date)
* Get intelligent search recommendations (autocomplete suggestions)
* Select files/folders from search results and create backups
* Generate backups in **ZIP format**
* Restore backups to any target directory with overwrite handling
* Maintain backup and restore history using a database

The application provides a clean and responsive web interface built with **Flask** and **Bootstrap**.

This project was developed as part of an internship assignment focusing on file system utilities, backup systems, and database integration.

---

## 🚀 Features

### 1. File Scanning & Indexing

* Recursively scans directories
* Stores metadata:

  * File name
  * Full path
  * Size
  * Extension
  * Last modified time
  * Optional SHA-256 hash
* Only files from the **latest scanned directory** are used for search and recommendations

---

### 2. Advanced File Search

Supports multiple filters:

* Name contains (partial search)
* Extension filter
* File size range
* Modified date range
* Sorting:

  * Name
  * Size
  * Extension
  * Date
* Ascending / Descending
* Result limit

---

### 3. Search Recommendations (Autocomplete)

* Real-time suggestions while typing
* Shows file name + path
* Suggestions restricted to the **current scanned directory**

---

### 4. Backup System

* Backup created from **selected files/folders** in search results
* Backup format: **ZIP**
* Preserves directory structure
* Optional hash detection
* Backup metadata stored in database
* Notes can be added to backups

---

### 5. Restore System

* Restore any backup ZIP to a specified directory
* Handles file conflicts using modes:

  * `skip` — keep existing files
  * `overwrite` — replace files
  * `rename` — create new name (file(1).ext)
* Restore history stored in database

---

### 6. History Management

* Backup history
* Restore history
* Metadata includes:

  * Timestamp
  * Source path
  * Target path
  * ZIP location
  * Notes
  * Mode used

---

### 7. Modern Web Interface

* Bootstrap-based UI
* Responsive layout
* Card-based design
* Highlight selected rows
* Result counters
* Alerts and feedback messages

---

## 🏗️ Technology Stack

| Component     | Technology                       |
| ------------- | -------------------------------- |
| Backend       | Python                           |
| Web Framework | Flask                            |
| Frontend      | HTML, CSS, JavaScript, Bootstrap |
| Database      | SQLite                           |
| Backup Format | ZIP                              |
| Hashing       | SHA-256 (optional)               |

---

## 📂 Project Structure

```
search_backup_utility/
│
├── web_app.py              # Flask application
├── scanner.py              # File scanning & indexing
├── search_engine.py        # Search logic
├── backup_engine.py        # Backup creation
├── restore_engine.py       # Restore functionality
├── db.py                   # Database connection
├── schema.sql              # Database schema
│
├── templates/
│   └── index.html          # Web UI
│
├── static/
│   ├── app.js              # Frontend logic
│   └── styles.css          # Styling
│
├── data/
│   ├── app.db              # SQLite database
│   └── backups/            # Generated ZIP files
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone or Download Project

```
git clone <repository-url>
cd search_backup_utility
```

Or extract ZIP file.

---

### 2. Create Virtual Environment

Windows:

```
python -m venv .venv
.\.venv\Scripts\activate
```

---

### 3. Install Dependencies

```
pip install -r requirements.txt
```

If requirements file is missing:

```
pip install flask
```

---

### 4. Run Application

```
python web_app.py
```

Open browser:

```
http://127.0.0.1:5000
```

---

## 📖 Usage Guide

### Step 1 — Scan Directory

1. Enter folder path
2. Click **Scan**
3. Files will be indexed

Example:

```
D:\testdata_backup_demo
```

---

### Step 2 — Search Files

* Enter name or filters
* Click **Search**
* Select files using checkboxes

---

### Step 3 — Create Backup

* Select files from results
* Click **Create ZIP from selected**
* Backup ID will be generated

---

### Step 4 — Restore Backup

* Enter Backup ID
* Enter target directory
* Select overwrite mode
* Click **Restore**

---

## 🧪 Test Data Creation (Optional)

PowerShell example:

```
mkdir D:\testdata_demo
"hello" > D:\testdata_demo\a.txt
"world" > D:\testdata_demo\b.txt
mkdir D:\testdata_demo\sub
"test" > D:\testdata_demo\sub\c.log
```

---

## 🗄️ Database Schema Overview

### Files Table

Stores indexed file metadata.

### Backups Table

Stores backup information and ZIP path.

### Backup Items Table

Maps files included in backups.

### Restores Table

Stores restore operations history.

---

## 🔒 Design Decisions

* SQLite chosen for lightweight local storage
* ZIP used for portability and compression
* Flask for simplicity and rapid development
* Modular architecture for maintainability
* Context-based indexing for accurate search scope

---

## 🚧 Future Enhancements

* Scheduled backups
* Encryption support
* Full-text search
* Docker deployment
* Cloud storage integration

---

## 👨‍💻 Author

Developed by:

**Vineet Savle**

Internship Project — Personal Search & Backup Utility

---

## 📜 License

This project is developed for educational and internship evaluation purposes.
