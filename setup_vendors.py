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
        cursor.execute("DROP TABLE IF EXISTS vendors")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                category VARCHAR(100),
                price INT,
                rating FLOAT DEFAULT 0.0,
                description TEXT,
                image_url VARCHAR(512),
                email VARCHAR(255),
                phone VARCHAR(20)
            )
        """)

        # Vendor Reviews Table
        print("Checking 'vendor_reviews' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendor_reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                vendor_id INT,
                user_id INT,
                rating INT,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Bookings Table
        print("Checking 'bookings' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                event_id INT,
                vendor_id INT,
                total_amount INT,
                advance_paid INT DEFAULT 0,
                status VARCHAR(50) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            ("Aura Studio", "Photography", 15000, 4.9, "Cinematic wedding photography and creative portraits.", "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&q=80&w=300", "contact@aurastudio.com", "+91 98765 43210"),
            ("SnapPixel", "Photography", 8500, 4.7, "Budget-friendly event coverage with high-quality digital delivery.", "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?auto=format&fit=crop&q=80&w=300", "info@snappixel.in", "+91 91234 56789"),
            
            # Decorators
            ("Neon Bloom", "Decoration", 25000, 4.8, "Modern floral arrangements and neon-themed event styling.", "https://images.unsplash.com/photo-1519225421980-715cb0215aed?auto=format&fit=crop&q=80&w=300", "hello@neonbloom.com", "+91 99887 76655"),
            ("Royal Decor", "Decoration", 45000, 5.0, "Luxury stage setups and traditional Indian wedding themes.", "https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&q=80&w=300", "royal@decor.com", "+91 90000 11111"),
            
            # Catering
            ("Spice Route", "Catering", 500, 4.6, "Per-plate authentic multi-cuisine buffet services.", "https://images.unsplash.com/photo-1555244162-803834f70033?auto=format&fit=crop&q=80&w=300", "spice@route.com", "+91 88888 77777"),
            ("Gourmet Gala", "Catering", 1200, 4.9, "Premium fine-dining experience for corporate events.", "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&q=80&w=300", "gala@gourmet.com", "+91 77777 66666"),
            
            # Music/Entertainment
            ("DJ Vibe", "Music", 12000, 4.7, "Professional DJ services with sound and lighting included.", "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&q=80&w=300", "dj@vibe.com", "+91 99999 00000"),
            ("Melody Band", "Music", 35000, 4.8, "Live acoustic band for intimate gatherings and weddings.", "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&q=80&w=300", "melody@band.com", "+91 98888 77777"),

            # Venues
            ("Grand Palace", "Venue", 150000, 4.9, "Palatial venue for grand weddings and large scale corporate events.", "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&q=80&w=300", "events@grandpalace.com", "+91 91111 22222"),
            ("Green Garden", "Venue", 50000, 4.5, "Beautiful outdoor lawn perfect for summer weddings and parties.", "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?auto=format&fit=crop&q=80&w=300", "info@greengarden.com", "+91 92222 33333"),

            # Makeup Artists
            ("Glow Up", "Makeup", 12000, 4.8, "Professional bridal makeup and styling for all skin types.", "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&q=80&w=300", "glow@upmakeup.com", "+91 93333 44444"),
            ("Artistry by Ana", "Makeup", 8000, 4.6, "Specialized in minimalist and elegant party makeup looks.", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&q=80&w=300", "ana@artistry.com", "+91 94444 55555"),

            # Invitations
            ("Paper Craft", "Invitations", 100, 4.7, "Custom designed luxury wedding cards and digital invites.", "https://images.unsplash.com/photo-1544928147-79a2dbc1f389?auto=format&fit=crop&q=80&w=300", "design@papercraft.com", "+91 95555 66666"),

            # Transportation
            ("Luxury Rides", "Transportation", 20000, 4.8, "Premium fleet of luxury cars for bridal arrivals and guest transit.", "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&q=80&w=300", "rides@luxury.com", "+91 96666 77777")
        ]

        cursor.executemany(
            "INSERT INTO vendors (name, category, price, rating, description, image_url, email, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            vendor_data
        )

        # Add some mock reviews
        print("Adding mock reviews...")
        mock_reviews = [
            (1, 1, 5, "Amazing photography! Highly recommended."),
            (2, 1, 4, "Great service, very professional."),
            (3, 1, 5, "Best decorators in town!"),
        ]
        cursor.executemany(
            "INSERT INTO vendor_reviews (vendor_id, user_id, rating, comment) VALUES (%s, %s, %s, %s)",
            mock_reviews
        )

        db.commit()
        print("✅ Database refreshed with new tables and vendor data!")
        cursor.close()
        db.close()
    except Exception as e:
        print(f"❌ Error setting up vendors: {e}")

if __name__ == "__main__":
    setup_vendors()
