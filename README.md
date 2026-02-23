# 🚀 Personal Search & Backup Utility

A Flask-based Web Application that allows users to:

- Scan any local directory
- Search files with advanced filters
- Create ZIP backups of selected files
- Restore backups to a chosen directory
- View backup & restore history
- Get smart file name suggestions (Google-style)

---

## 🛠 Technologies Used

- Python 3
- Flask
- SQLite
- HTML, CSS (Glass UI)
- JavaScript (Search Suggestions)

---

## 📂 Features

### 1️⃣ Scan Directory
- Scan any local folder path
- Counts total files & directories
- Stores file metadata in database

### 2️⃣ Advanced Search
Search by:
- File name
- Extension
- Size range
- Date range
- Sorting (Name, Size, Date)
- Live search suggestions

### 3️⃣ Backup (ZIP)
- Select multiple files
- Creates timestamped ZIP file
- Saves backup history

### 4️⃣ Restore
- Select ZIP file
- Choose restore directory
- Optional overwrite
- Saves restore history

### 5️⃣ History
- Separate panels for:
  - Backup History
  - Restore History

---

## ▶ How To Run

### 1️⃣ Install Dependencies

```bash
pip install flask


2️⃣ Run Application

python app.py

3️⃣ Open in Browser

http://127.0.0.1:5000

