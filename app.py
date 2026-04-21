import mysql.connector
from flask import Flask, render_template, request, redirect, session, jsonify
from setup_vendors import setup_vendors

app = Flask(__name__)
app.secret_key = "secret123"

# DATABASE CONNECTION
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",
        database="event_app"
    )

# LOGIN
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email=%s AND password=%s",
        (request.form["email"], request.form["password"])
    )
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user:
        session["user"] = user[0]
        return redirect("/dashboard")

    return "Invalid Login"

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s)",
            (request.form["email"], request.form["password"])
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect("/")
    return render_template("register.html")

# GLOBAL DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    
    db = get_db()
    cursor = db.cursor()
    
    # Get user's events
    cursor.execute("SELECT * FROM events WHERE user_id=%s", (session["user"],))
    events = cursor.fetchall()

    # Aggregate stats for all user events
    cursor.execute("""
        SELECT SUM(amount) FROM expenses 
        JOIN events ON expenses.event_id = events.id 
        WHERE events.user_id = %s
    """, (session["user"],))
    total_spent = cursor.fetchone()[0] or 0
    
    total_budget = sum(e[3] for e in events) if events else 0
    remaining = total_budget - total_spent

    # Category summaries across ALL events
    cursor.execute("""
        SELECT category, SUM(amount) FROM expenses 
        JOIN events ON expenses.event_id = events.id 
        WHERE events.user_id = %s
        GROUP BY category
    """, (session["user"],))
    global_cat_summary = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("dashboard.html",
                           events=events,
                           total_budget=total_budget,
                           total_spent=total_spent,
                           remaining=remaining,
                           global_cat_summary=global_cat_summary)

# EVENT DETAILS
@app.route("/event/<int:id>")
def event_details(id):
    if "user" not in session:
        return redirect("/")
    
    db = get_db()
    cursor = db.cursor()
    
    # Verify ownership
    cursor.execute("SELECT * FROM events WHERE id=%s AND user_id=%s", (id, session["user"]))
    event = cursor.fetchone()
    
    if not event:
        return "Access Denied", 403

    # Get expenses for this event
    cursor.execute("SELECT * FROM expenses WHERE event_id=%s", (id,))
    expenses = cursor.fetchall()
    
    # Get tasks for this event
    cursor.execute("SELECT * FROM tasks WHERE event_id=%s", (id,))
    tasks = cursor.fetchall()

    total_budget = event[3]
    total_spent = sum(exp[3] for exp in expenses) if expenses else 0
    remaining = total_budget - total_spent

    # AI Recommendation Logic (Category-specific)
    recommendations = []
    category_limits = {
        "Venue": total_budget * 0.4,
        "Catering": total_budget * 0.3,
        "Photography": total_budget * 0.15
    }

    for category, limit in category_limits.items():
        cursor.execute(
            "SELECT * FROM vendors WHERE category=%s AND price<=%s ORDER BY price DESC LIMIT 1",
            (category, limit)
        )
        vendor = cursor.fetchone()
        if vendor:
            recommendations.append(vendor)

    # Category summaries
    cursor.execute("""
        SELECT category, SUM(amount) FROM expenses 
        WHERE event_id=%s GROUP BY category
    """, (id,))
    cat_summary = cursor.fetchall()

    # GET GUESTS
    cursor.execute("SELECT * FROM guests WHERE event_id=%s", (id,))
    guests = cursor.fetchall()

    # GET TIMELINE
    cursor.execute("SELECT * FROM timeline WHERE event_id=%s ORDER BY time ASC", (id,))
    timeline = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("event_details.html",
                           event=event,
                           expenses=expenses,
                           tasks=tasks,
                           total_budget=total_budget,
                           total_spent=total_spent,
                           remaining=remaining,
                           recommendations=recommendations,
                           cat_summary=cat_summary,
                           guests=guests,
                           timeline=timeline)

# CREATE EVENT
@app.route("/create_event", methods=["GET", "POST"])
def create_event():
    if "user" not in session:
        return redirect("/")
        
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO events (name, type, budget, user_id) VALUES (%s, %s, %s, %s)",
            (request.form["event_name"], request.form["event_type"], request.form["budget"], session["user"])
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect("/dashboard")
    return render_template("create_event.html")

# ADD EXPENSE
@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    if "user" not in session:
        return redirect("/")
        
    db = get_db()
    cursor = db.cursor()
    
    if request.method == "POST":
        cursor.execute(
            "INSERT INTO expenses (category, item, amount, event_id) VALUES (%s, %s, %s, %s)",
            (request.form["category"], request.form["item"], request.form["amount"], request.form["event_id"])
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect(f"/event/{request.form['event_id']}")
    
    # For GET: fetch events to populate dropdown
    cursor.execute("SELECT id, name FROM events WHERE user_id=%s", (session["user"],))
    user_events = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template("add_expense.html", user_events=user_events)

# TASK MANAGEMENT
@app.route("/add_task/<int:event_id>", methods=["POST"])
def add_task(event_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO tasks (event_id, description) VALUES (%s, %s)", 
                   (event_id, request.form["description"]))
    db.commit()
    cursor.close()
    db.close()
    return redirect(f"/event/{event_id}")

@app.route("/toggle_task/<int:id>/<int:event_id>")
def toggle_task(id, event_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE tasks SET is_done = NOT is_done WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect(f"/event/{event_id}")

@app.route("/delete_task/<int:id>/<int:event_id>")
def delete_task(id, event_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect(f"/event/{event_id}")

# DELETE ACTIONS
@app.route("/delete_event/<int:id>")
def delete_event(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM events WHERE id=%s AND user_id=%s", (id, session["user"]))
    db.commit()
    cursor.close()
    db.close()
    return redirect("/dashboard")

@app.route("/delete_expense/<int:id>/<int:event_id>")
def delete_expense(id, event_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect(f"/event/{event_id}")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# VENDORS MARKETPLACE
@app.route("/vendors")
def vendors():
    if "user" not in session:
        return redirect("/")
        
    category = request.args.get("category")
    db = get_db()
    cursor = db.cursor()
    
    if category and category != "All":
        cursor.execute("SELECT * FROM vendors WHERE category=%s", (category,))
    else:
        cursor.execute("SELECT * FROM vendors")
        
    vendors_list = cursor.fetchall()
    
    # Get distinct categories for filter buttons
    cursor.execute("SELECT DISTINCT category FROM vendors")
    categories = [cat[0] for cat in cursor.fetchall()]
    
    cursor.close()
    db.close()
    
    return render_template("vendors.html", vendors=vendors_list, categories=categories, active_cat=category or "All")

# GUEST MANAGEMENT
@app.route("/add_guest/<int:event_id>", methods=["POST"])
def add_guest(event_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO guests (event_id, name, notes) VALUES (%s, %s, %s)",
                   (event_id, request.form["name"], request.form["notes"]))
    db.commit()
    cursor.close()
    db.close()
    return redirect(f"/event/{event_id}")

@app.route("/update_guest_status/<int:id>/<int:event_id>/<string:status>")
def update_guest_status(id, event_id, status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE guests SET status=%s WHERE id=%s", (status, id))
    db.commit()
    cursor.close()
    db.close()
    return redirect(f"/event/{event_id}")

@app.route("/delete_guest/<int:id>/<int:event_id>")
def delete_guest(id, event_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM guests WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect(f"/event/{event_id}")

# TIMELINE MANAGEMENT
@app.route("/add_timeline/<int:event_id>", methods=["POST"])
def add_timeline(event_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO timeline (event_id, time, activity, notes) VALUES (%s, %s, %s, %s)",
                   (event_id, request.form["time"], request.form["activity"], request.form["notes"]))
    db.commit()
    cursor.close()
    db.close()
    return redirect(f"/event/{event_id}")

@app.route("/delete_timeline/<int:id>/<int:event_id>")
def delete_timeline(id, event_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM timeline WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect(f"/event/{event_id}")

# QUICK LINK VENDOR
@app.route("/link_vendor/<int:v_id>/<int:e_id>")
def link_vendor(v_id, e_id):
    db = get_db()
    cursor = db.cursor()
    
    # 1. Fetch Vendor Details
    cursor.execute("SELECT name, category, price FROM vendors WHERE id=%s", (v_id,))
    vendor = cursor.fetchone()
    
    if vendor:
        # 2. Add as Expense (Auto-deduct price)
        cursor.execute(
            "INSERT INTO expenses (category, item, amount, event_id, vendor_id) VALUES (%s, %s, %s, %s, %s)",
            (vendor[1], vendor[0], vendor[2], e_id, v_id)
        )
        db.commit()
        
    cursor.close()
    db.close()
    return redirect(f"/event/{e_id}")

if __name__ == "__main__":
    # Initialize vendors data if needed or for demo purposes
    try:
        setup_vendors()
    except Exception as e:
        print(f"Vendor setup failed: {e}")
    app.run(debug=True)