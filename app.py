from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from pathlib import Path
from datetime import datetime
from functools import wraps
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Demo only; configure a secret for deployment.
DB = Path(__file__).with_name("grievances.db")
ADMIN_USER = "admin"
ADMIN_PASSWORD = "Admin@123"  # Demo credentials only. Change before real use.
STATUSES = ["Submitted", "In Progress", "Resolved", "Rejected"]

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def initialize():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS grievances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grievance_id TEXT UNIQUE,
            student_name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            category TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Submitted',
            remarks TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )""")

def admin_only(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            flash("Please log in as an administrator first.", "error")
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    with connect() as db:
        total = db.execute("SELECT COUNT(*) FROM grievances").fetchone()[0]
        resolved = db.execute("SELECT COUNT(*) FROM grievances WHERE status='Resolved'").fetchone()[0]
    return render_template("index.html", total=total, resolved=resolved)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    form = {}
    if request.method == "POST":
        keys = ["student_name", "email", "department", "category", "subject", "description", "location"]
        form = {key: request.form.get(key, "").strip() for key in keys}
        if not all(form[k] for k in ["student_name", "email", "department", "category", "subject", "description"]):
            flash("Please complete all required fields.", "error")
        else:
            with connect() as db:
                cur = db.execute("""INSERT INTO grievances
                    (grievance_id, student_name, email, department, category, subject, description, location, created_at)
                    VALUES ('PENDING', ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (form["student_name"], form["email"], form["department"], form["category"],
                     form["subject"], form["description"], form["location"], datetime.now().strftime("%Y-%m-%d %H:%M")))
                pk = cur.lastrowid
                gid = f"GRV{pk:05d}"
                db.execute("UPDATE grievances SET grievance_id=? WHERE id=?", (gid, pk))
                db.commit()
            flash(f"Grievance submitted! Your tracking ID is {gid}.", "success")
            return redirect(url_for("track", grievance_id=gid))
    return render_template("submit.html", form=form)

@app.route("/track", methods=["GET", "POST"])
def track():
    gid = request.values.get("grievance_id", "").strip().upper()
    grievance = None
    if gid:
        with connect() as db:
            grievance = db.execute("SELECT * FROM grievances WHERE grievance_id=?", (gid,)).fetchone()
        if not grievance:
            flash("No grievance found for that ID.", "error")
    return render_template("track.html", grievance=grievance, grievance_id=gid)

@app.route("/my-complaints", methods=["GET", "POST"])
def my_complaints():
    email = request.values.get("email", "").strip().lower()
    rows = []
    if email:
        with connect() as db:
            rows = db.execute("SELECT * FROM grievances WHERE lower(email)=? ORDER BY id DESC", (email,)).fetchall()
    return render_template("my_complaints.html", rows=rows, email=email)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        user = request.form.get("username", "")
        password = request.form.get("password", "")
        if secrets.compare_digest(user, ADMIN_USER) and secrets.compare_digest(password, ADMIN_PASSWORD):
            session.clear()
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("Incorrect username or password.", "error")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin")
@admin_only
def admin():
    selected = request.args.get("status", "")
    with connect() as db:
        if selected in STATUSES:
            rows = db.execute("SELECT * FROM grievances WHERE status=? ORDER BY id DESC", (selected,)).fetchall()
        else:
            selected = ""
            rows = db.execute("SELECT * FROM grievances ORDER BY id DESC").fetchall()
        counts = {s: db.execute("SELECT COUNT(*) FROM grievances WHERE status=?", (s,)).fetchone()[0] for s in STATUSES}
        total = db.execute("SELECT COUNT(*) FROM grievances").fetchone()[0]
    return render_template("admin.html", rows=rows, selected=selected, counts=counts, total=total)

@app.route("/admin/edit/<int:pk>", methods=["GET", "POST"])
@admin_only
def edit(pk):
    with connect() as db:
        grievance = db.execute("SELECT * FROM grievances WHERE id=?", (pk,)).fetchone()
        if not grievance:
            flash("Grievance not found.", "error")
            return redirect(url_for("admin"))
        if request.method == "POST":
            status = request.form.get("status", "")
            remarks = request.form.get("remarks", "").strip()
            if status not in STATUSES:
                flash("Choose a valid status.", "error")
            elif status == "Rejected" and not remarks:
                flash("Add a reason before rejecting a grievance.", "error")
            else:
                db.execute("UPDATE grievances SET status=?, remarks=? WHERE id=?", (status, remarks, pk))
                db.commit()
                flash("Grievance updated.", "success")
                return redirect(url_for("admin"))
    return render_template("edit.html", grievance=grievance, statuses=STATUSES)

initialize()

if __name__ == "__main__":
    app.run(debug=True)  # Local development only; do not use debug mode in production.
