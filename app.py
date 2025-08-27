import os
import sqlite3
import hashlib
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, g, flash, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Generate a secure secret key
if not os.getenv("SECRET_KEY"):
    app.secret_key = secrets.token_hex(32)
else:
    app.secret_key = os.getenv("SECRET_KEY")

# =========================
# ✅ Gemini API Setup
# =========================
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# ✅ Database Setup
# =========================
# Allow overriding the SQLite file path via environment variable.
# This helps when running on platforms like Render.
DATABASE = os.getenv("SQLITE_PATH", "users.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        db.commit()

# Ensure the database schema exists when the app is imported (e.g., under Gunicorn)
if os.getenv("INITIALIZE_DB", "1") == "1":
    try:
        init_db()
    except Exception as e:
        # Avoid crashing on import; log instead. Startup will still proceed.
        print(f"Database init warning: {e}")

def hash_password(password):
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return salt + hash_obj.hexdigest()

def verify_password(password, hashed_password):
    """Verify password against hash"""
    salt = hashed_password[:32]
    hash_obj = hashlib.sha256((password + salt).encode())
    return hashed_password[32:] == hash_obj.hexdigest()

def sanitize_input(text):
    """Basic input sanitization"""
    if not text or len(text.strip()) == 0:
        return None
    return text.strip()[:500]  # Limit length

# =========================
# ✅ Routes
# =========================
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = sanitize_input(request.form.get("username"))
        password = request.form.get("password")
        
        if not username or not password:
            flash("Username and password are required", "error")
            return render_template("signup.html")
        
        if len(password) < 6:
            flash("Password must be at least 6 characters long", "error")
            return render_template("signup.html")
        
        hashed_password = hash_password(password)
        
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            db.commit()
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists!", "error")
        except Exception as e:
            flash("An error occurred. Please try again.", "error")
            print(f"Signup error: {e}")
    
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = sanitize_input(request.form.get("username"))
        password = request.form.get("password")
        
        if not username or not password:
            flash("Username and password are required", "error")
            return render_template("login.html")
        
        db = get_db()
        try:
            user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            
            if user and verify_password(password, user["password"]):
                session["username"] = username
                session["user_id"] = user["id"]
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid credentials!", "error")
        except Exception as e:
            flash("An error occurred. Please try again.", "error")
            print(f"Login error: {e}")
    
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        flash("Please login to access the dashboard", "error")
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("index"))

@app.route("/ask", methods=["POST"])
def ask():
    if "username" not in session:
        flash("Please login to ask questions", "error")
        return redirect(url_for("login"))
    
    question = sanitize_input(request.form.get("question"))
    
    if not question:
        flash("Please enter a question", "error")
        return redirect(url_for("dashboard"))
    
    try:
        response = model.generate_content(question)
        return render_template("dashboard.html", 
                             username=session["username"], 
                             question=question,
                             answer=response.text)
    except Exception as e:
        flash("Sorry, I couldn't process your question. Please try again.", "error")
        print(f"AI API error: {e}")
        return redirect(url_for("dashboard"))

# =========================
# ✅ Admin/Debug: View Users
# =========================
@app.route("/users")
def users_page():
    if "username" not in session:
        return redirect(url_for("login"))
    db = get_db()
    users = db.execute("SELECT id, username, created_at FROM users ORDER BY id DESC").fetchall()
    return render_template("users.html", users=users)

@app.route("/api/users")
def users_api():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    db = get_db()
    rows = db.execute("SELECT id, username, created_at FROM users ORDER BY id DESC").fetchall()
    data = [dict(row) for row in rows]
    return jsonify(data)

# Lightweight health check endpoint for Render
@app.route("/health")
def health_check():
    return "ok", 200

# =========================
# ✅ Run App
# =========================
if __name__ == "__main__":
    init_db()
    app.run(debug=False, host="0.0.0.0", port=5000)
