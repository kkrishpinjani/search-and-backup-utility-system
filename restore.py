import zipfile
import os

def restore_backup(backup_path, extract_to):
    with zipfile.ZipFile(backup_path, 'r') as zipf:
        zipf.extractall(extract_to)

    print("Restore Completed ")