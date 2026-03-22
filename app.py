import os
import time
import uuid
from functools import wraps

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_session import Session
from flask_dance.contrib.google import make_google_blueprint, google
from pymongo import MongoClient
from executor import Executor

# =========================
# CONFIG
# =========================
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "pro_max_secret")
    MONGO_URI = os.environ.get("MONGO_URI")

    SESSION_TYPE = "filesystem"  # pode trocar pra redis depois
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True

# =========================
# INIT
# =========================
app = Flask(__name__)
app.config.from_object(Config)

CORS(app, supports_credentials=True)
Session(app)

# =========================
# DB
# =========================
client = MongoClient(Config.MONGO_URI)
db = client["logicstart_pro_max"]

users = db["users"]
history = db["history"]
tokens = db["tokens"]

# =========================
# GOOGLE
# =========================
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    redirect_to="google_callback",
    scope=["profile", "email"]
)

app.register_blueprint(google_bp, url_prefix="/login")

# =========================
# HELPERS
# =========================
def create_token(email):
    token = str(uuid.uuid4())
    tokens.insert_one({
        "token": token,
        "email": email,
        "created": int(time.time())
    })
    return token

def get_user_by_token(token):
    t = tokens.find_one({"token": token})
    return t["email"] if t else None

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return jsonify({"error": "not authenticated"}), 401
        return f(*args, **kwargs)
    return wrapper

# =========================
# AUTO LOGIN (🔥 DIFERENCIAL)
# =========================
@app.before_request
def auto_login():
    token = request.headers.get("Authorization")

    if token and not session.get("user"):
        email = get_user_by_token(token)
        if email:
            session["user"] = email
            session["guest"] = False

# =========================
# AUTH EMAIL
# =========================
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    senha = data.get("senha")

    user = users.find_one({"email": email, "senha": senha})

    if not user:
        return jsonify({"success": False}), 401

    session["user"] = email
    session["guest"] = False

    token = create_token(email)

    return jsonify({
        "success": True,
        "token": token
    })

# =========================
# GOOGLE CALLBACK
# =========================
@app.route("/google_callback")
def google_callback():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")

    if not resp.ok:
        return "Erro Google"

    email = resp.json()["email"]

    if not users.find_one({"email": email}):
        users.insert_one({"email": email, "google": True})

    session["user"] = email
    session["guest"] = False

    return redirect("/ide")

# =========================
# GUEST
# =========================
@app.route("/auth/guest")
def guest():
    session["user"] = f"guest_{int(time.time())}"
    session["guest"] = True
    return redirect("/ide")

# =========================
# LOGOUT
# =========================
@app.route("/auth/logout")
def logout():
    session.clear()
    return redirect("/")

# =========================
# EXECUTOR (🔒 PROTEGIDO)
# =========================
BLOCKED = ["import os", "import sys", "__", "exec(", "open("]

def safe(code):
    for b in BLOCKED:
        if b in code:
            return False
    return True

@app.route("/api/run", methods=["POST"])
@login_required
def run():
    code = request.json.get("code", "")

    if not safe(code):
        return jsonify({"error": "blocked code"})

    executor = Executor(code)
    result = executor.executar()

    return jsonify({"result": result})

# =========================
# SAVE
# =========================
@app.route("/api/save", methods=["POST"])
@login_required
def save():
    if session.get("guest"):
        return jsonify({"error": "guest blocked"}), 403

    code = request.json.get("code")

    history.insert_one({
        "email": session["user"],
        "code": code,
        "time": int(time.time())
    })

    return jsonify({"success": True})

# =========================
# HISTORY
# =========================
@app.route("/api/history")
@login_required
def history_api():
    if session.get("guest"):
        return jsonify([])

    data = list(history.find({"email": session["user"]}, {"_id": 0}))
    return jsonify(data)

# =========================
# SESSION INFO
# =========================
@app.route("/auth/session")
def session_info():
    return jsonify({
        "user": session.get("user"),
        "guest": session.get("guest", False)
    })

# =========================
# PAGES
# =========================
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/ide")
def ide():
    if not session.get("user"):
        return redirect("/")
    return render_template("ide.html")

# =========================
# HEALTH
# =========================
@app.route("/health")
def health():
    return {"status": "ok", "time": int(time.time())}

# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    print("🍎 LogicStart Pro Max rodando")
    app.run(host="0.0.0.0", port=port)
