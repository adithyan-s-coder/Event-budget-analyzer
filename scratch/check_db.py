import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",
        database="event_app"
    )
    cursor = db.cursor()
    cursor.execute("DESCRIBE vendors")
    for col in cursor.fetchall():
        print(col)
    db.close()
except Exception as e:
    print(f"Error: {e}")
