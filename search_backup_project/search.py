import sqlite3

def search_by_name(name):
    conn = sqlite3.connect("files.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM files
        WHERE LOWER(name) LIKE ?
    """, ('%' + name.lower() + '%',))

    results = cursor.fetchall()
    conn.close()

    return results