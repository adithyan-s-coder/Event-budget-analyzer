import mysql.connector

def run_fix():
    print("🚀 Starting Automatic Database Fix...")
    
    try:
        # 1. Connect to MySQL (using your credentials from app.py)
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root123",
            database="event_app"
        )
        cursor = db.cursor()
        print("✅ Connected to database 'event_app'")

        # 2. Add 'user_id' to events table if missing
        print("Checking 'events' table...")
        cursor.execute("SHOW COLUMNS FROM events LIKE 'user_id'")
        if not cursor.fetchone():
            print("Adding 'user_id' column...")
            cursor.execute("ALTER TABLE events ADD COLUMN user_id INT")
            db.commit()
        else:
            print("'user_id' already exists.")

        # 3. Add 'event_id' to expenses table if missing
        print("Checking 'expenses' table...")
        cursor.execute("SHOW COLUMNS FROM expenses LIKE 'event_id'")
        if not cursor.fetchone():
            print("Adding 'event_id' column...")
            cursor.execute("ALTER TABLE expenses ADD COLUMN event_id INT")
            db.commit()
        else:
            print("'event_id' already exists.")

        # 4. Create tasks table if missing
        print("Checking 'tasks' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event_id INT,
                description VARCHAR(255),
                is_done BOOLEAN DEFAULT FALSE
            )
        """)
        db.commit()
        print("✅ 'tasks' table is ready.")

        # 5. Patch existing data so it shows up in dashboard
        print("Patching existing data...")
        
        # Link events to the first user found
        cursor.execute("SELECT id FROM users LIMIT 1")
        user = cursor.fetchone()
        if user:
            cursor.execute("UPDATE events SET user_id = %s WHERE user_id IS NULL", (user[0],))
            print(f"✅ Linked events to User ID {user[0]}")

        # Link expenses to the first event found
        cursor.execute("SELECT id FROM events LIMIT 1")
        event = cursor.fetchone()
        if event:
            cursor.execute("UPDATE expenses SET event_id = %s WHERE event_id IS NULL", (event[0],))
            print(f"✅ Linked expenses to Event ID {event[0]}")

        db.commit()
        print("\n✨ ALL FIXED! Your database is now compatible with the new features.")
        print("👉 Now simply RESTART your 'python app.py' terminal and refresh your browser.")
        
        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        print(f"\n❌ Error: {err}")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")

if __name__ == "__main__":
    run_fix()
