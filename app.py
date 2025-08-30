import os
import sqlite3
import hashlib
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, g, flash, jsonify
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)

# API setup
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY required")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Database
DATABASE = os.getenv("SQLITE_PATH", "users.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        db.commit()

# Auto-init DB
try:
    init_db()
except:
    pass

def hash_password(password):
    salt = secrets.token_hex(16)
    return salt + hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(password, hashed):
    salt = hashed[:32]
    return hashed[32:] == hashlib.sha256((password + salt).encode()).hexdigest()

def sanitize(text):
    return text.strip()[:500] if text and text.strip() else None

# Routes
@app.route("/")
def index():
    return redirect(url_for("dashboard")) if "username" in session else render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = sanitize(request.form.get("username"))
        password = request.form.get("password")
        
        if not username or not password or len(password) < 6:
            flash("Username and password (min 6 chars) required", "error")
            return render_template("signup.html")
        
        try:
            db = get_db()
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                      (username, hash_password(password)))
            db.commit()
            flash("Account created! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username exists!", "error")
        except:
            flash("Error occurred. Try again.", "error")
    
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = sanitize(request.form.get("username"))
        password = request.form.get("password")
        
        if not username or not password:
            flash("Username and password required", "error")
            return render_template("login.html")
        
        try:
            db = get_db()
            user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            
            if user and verify_password(password, user["password"]):
                session["username"] = username
                session["user_id"] = user["id"]
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid credentials!", "error")
        except:
            flash("Error occurred. Try again.", "error")
    
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        flash("Please login", "error")
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("index"))

@app.route("/ask", methods=["POST"])
def ask():
    if "username" not in session:
        flash("Please login", "error")
        return redirect(url_for("dashboard"))
    
    question = sanitize(request.form.get("question"))
    if not question:
        flash("Enter a question", "error")
        return redirect(url_for("dashboard"))
    
    try:
        response = model.generate_content(question)
        return render_template("dashboard.html", 
                             username=session["username"], 
                             question=question,
                             answer=response.text)
    except:
        flash("Couldn't process question. Try again.", "error")
        return redirect(url_for("dashboard"))

@app.route("/api/ask", methods=["POST"])
def api_ask():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    if not data or not data.get("question"):
        return jsonify({"error": "Question is required"}), 400
    
    question = sanitize(data["question"])
    if not question:
        return jsonify({"error": "Invalid question"}), 400
    
    try:
        # Generate unique response for each question
        response = model.generate_content(question)
        return jsonify({
            "success": True,
            "answer": response.text,
            "question": question
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Couldn't process question. Try again."
        }), 500

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
    return jsonify([dict(row) for row in rows])

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
