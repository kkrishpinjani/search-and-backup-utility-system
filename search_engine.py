from database import get_connection

def search_files(filters):
    conn = get_connection()
    c = conn.cursor()

    query = "SELECT * FROM files WHERE 1=1"
    params = []

    if filters.get("name"):
        query += " AND name LIKE ?"
        params.append(f"%{filters['name']}%")

    if filters.get("extension"):
        query += " AND extension = ?"
        params.append(filters["extension"])

    if filters.get("min_size"):
        query += " AND size >= ?"
        params.append(filters["min_size"])

    if filters.get("max_size"):
        query += " AND size <= ?"
        params.append(filters["max_size"])

    if filters.get("start_date"):
        query += " AND modified_date >= ?"
        params.append(filters["start_date"])

    if filters.get("end_date"):
        query += " AND modified_date <= ?"
        params.append(filters["end_date"])

    allowed_sorts = ["name", "size", "modified_date"]
    sort = filters.get("sort_by")

    if sort in allowed_sorts:
        query += f" ORDER BY {sort} DESC"
    else:
        query += " ORDER BY size DESC"

    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results