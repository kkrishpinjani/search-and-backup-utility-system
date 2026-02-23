import sqlite3
from database import connect

def search_files(name, extension, min_size, max_size, start_date, end_date, sort_by):
    conn = connect()
    cursor = conn.cursor()

    query = "SELECT * FROM files WHERE 1=1"
    params = []

    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")

    if extension:
        query += " AND extension = ?"
        params.append(extension)

    if min_size:
        query += " AND size >= ?"
        params.append(min_size)

    if max_size:
        query += " AND size <= ?"
        params.append(max_size)

    if start_date:
        query += " AND modified >= ?"
        params.append(start_date)

    if end_date:
        query += " AND modified <= ?"
        params.append(end_date)

    if sort_by:
        query += f" ORDER BY {sort_by}"

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return results