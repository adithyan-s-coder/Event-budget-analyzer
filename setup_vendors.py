import mysql.connector

def setup_vendors():
    print("Initializing Vendors Marketplace...")
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root123",
            database="event_app"
        )
        cursor = db.cursor()

        # Existing Vendor Setup
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                category VARCHAR(100),
                price INT,
                rating FLOAT DEFAULT 0.0,
                description TEXT,
                image_url VARCHAR(512)
            )
        """)

        # 3. Create Guest List Table
        print("Checking 'guests' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event_id INT,
                name VARCHAR(255),
                status VARCHAR(50) DEFAULT 'Confirmed',
                notes TEXT
            )
        """)

        # 4. Create Timeline Table
        print("Checking 'timeline' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeline (
                id INT AUTO_INCREMENT PRIMARY KEY,
                event_id INT,
                time VARCHAR(50),
                activity VARCHAR(255),
                notes TEXT
            )
        """)

        # 5. Update Expenses for Vendor Linking
        cursor.execute("SHOW COLUMNS FROM expenses LIKE 'vendor_id'")
        if not cursor.fetchone():
            print("Adding 'vendor_id' to expenses...")
            cursor.execute("ALTER TABLE expenses ADD COLUMN vendor_id INT")

        # 2. Clear and Populate with Mock Data (Vendors)
        cursor.execute("DELETE FROM vendors") 
        
        vendor_data = [
            # Photographers
            ("Aura Studio", "Photography", 15000, 4.9, "Cinematic wedding photography and creative portraits.", "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&q=80&w=300"),
            ("SnapPixel", "Photography", 8500, 4.7, "Budget-friendly event coverage with high-quality digital delivery.", "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?auto=format&fit=crop&q=80&w=300"),
            
            # Decorators
            ("Neon Bloom", "Decoration", 25000, 4.8, "Modern floral arrangements and neon-themed event styling.", "https://images.unsplash.com/photo-1519225421980-715cb0215aed?auto=format&fit=crop&q=80&w=300"),
            ("Royal Decor", "Decoration", 45000, 5.0, "Luxury stage setups and traditional Indian wedding themes.", "https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&q=80&w=300"),
            
            # Catering
            ("Spice Route", "Catering", 500, 4.6, "Per-plate authentic multi-cuisine buffet services.", "https://images.unsplash.com/photo-1555244162-803834f70033?auto=format&fit=crop&q=80&w=300"),
            ("Gourmet Gala", "Catering", 1200, 4.9, "Premium fine-dining experience for corporate events.", "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&q=80&w=300"),
            
            # Music/Entertainment
            ("DJ Vibe", "Music", 12000, 4.7, "Professional DJ services with sound and lighting included.", "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&q=80&w=300"),
            ("Melody Band", "Music", 35000, 4.8, "Live acoustic band for intimate gatherings and weddings.", "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&q=80&w=300")
        ]

        cursor.executemany(
            "INSERT INTO vendors (name, category, price, rating, description, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
            vendor_data
        )

        db.commit()
        print("✅ Database refreshed with new tables and vendor data!")
        cursor.close()
        db.close()
    except Exception as e:
        print(f"❌ Error setting up vendors: {e}")

if __name__ == "__main__":
    setup_vendors()
