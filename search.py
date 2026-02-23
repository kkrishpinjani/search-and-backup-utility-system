from database import connect

def search_by_name(filename):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM files WHERE name LIKE ?", 
                   ('%' + filename + '%',))

    results = cursor.fetchall()

    for row in results:
        print(row)

    conn.close()