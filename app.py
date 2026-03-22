import os
import time
import traceback
from functools import wraps

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
from pymongo import MongoClient
from executor import Executor

# =============================
# CONFIGURAÇÃO BASE
# =============================
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "super_secret")
    MONGO_URI = os.environ.get("MONGO_URI")
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"

# =============================
# APP INIT
# =============================
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# =============================
# DATABASE
# =============================
if not Config.MONGO_URI:
    raise Exception("MONGO_URI não configurado")

client = MongoClient(Config.MONGO_URI)
db = client["logicstart_microsoft"]

users = db["users"]
history = db["history"]

# =============================
# GOOGLE AUTH
# =============================
if not Config.GOOGLE_CLIENT_ID:
    raise Exception("Google OAuth não configurado")

google_bp = make_google_blueprint(
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    redirect_to="auth_google_callback",
    scope=["profile", "email"]
)

app.register_blueprint(google_bp, url_prefix="/auth/google")

# =============================
# HELPERS
# =============================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return jsonify({"error": "Não autenticado"}), 401
        return f(*args, **kwargs)
    return wrapper

def is_guest():
    return session.get("guest", False)

# =============================
# AUTH - EMAIL
# =============================
@app.route("/auth/login", methods=["POST"])
def auth_login():
    try:
        data = request.get_json()
        email = data.get("email")
        senha = data.get("senha")

        if not email or not senha:
            return jsonify({"success": False, "error": "Dados inválidos"}), 400

        user = users.find_one({"email": email, "senha": senha})

        if not user:
            return jsonify({"success": False, "error": "Credenciais inválidas"}), 401

        session["user"] = email
        session["guest"] = False

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# =============================
# AUTH - GOOGLE CALLBACK
# =============================
@app.route("/auth/google/callback")
def auth_google_callback():
    try:
        if not google.authorized:
            return redirect(url_for("google.login"))

        resp = google.get("/oauth2/v2/userinfo")

        if not resp.ok:
            return "Erro Google", 500

        data = resp.json()
        email = data.get("email")

        if not email:
            return "Email não encontrado", 400

        if not users.find_one({"email": email}):
            users.insert_one({
                "email": email,
                "google": True,
                "created_at": int(time.time())
            })

        session["user"] = email
        session["guest"] = False

        return redirect("/ide")

    except Exception as e:
        return f"Erro: {str(e)}"

# =============================
# AUTH - GUEST
# =============================
@app.route("/auth/guest")
def auth_guest():
    session["user"] = f"guest_{int(time.time())}"
    session["guest"] = True
    return redirect("/ide")

# =============================
# SESSION
# =============================
@app.route("/auth/session")
def auth_session():
    return jsonify({
        "user": session.get("user"),
        "guest": is_guest(),
        "logged": bool(session.get("user"))
    })

@app.route("/auth/logout")
def auth_logout():
    session.clear()
    return redirect("/")

# =============================
# EXECUTOR
# =============================
MAX_CODE_SIZE = 5000
BLOCKED = ["import os", "import sys", "open(", "exec(", "__"]

def validate_code(code):
    if len(code) > MAX_CODE_SIZE:
        return False, "Código muito grande"

    for b in BLOCKED:
        if b in code:
            return False, f"Bloqueado: {b}"

    return True, None

@app.route("/api/run", methods=["POST"])
@login_required
def run_code():
    try:
        data = request.get_json()
        code = data.get("code", "")

        ok, error = validate_code(code)
        if not ok:
            return jsonify({"success": False, "error": error})

        executor = Executor(code)
        result = executor.executar()

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception:
        return jsonify({
            "success": False,
            "error": "Erro interno",
            "debug": traceback.format_exc()
        })

# =============================
# SAVE
# =============================
@app.route("/api/save", methods=["POST"])
@login_required
def save_code():
    if is_guest():
        return jsonify({"success": False, "error": "Guest não pode salvar"}), 403

    data = request.get_json()
    code = data.get("code")

    if not code:
        return jsonify({"success": False, "error": "Código vazio"})

    history.insert_one({
        "email": session["user"],
        "code": code,
        "timestamp": int(time.time())
    })

    return jsonify({"success": True})

# =============================
# HISTORY
# =============================
@app.route("/api/history")
@login_required
def get_history():
    if is_guest():
        return jsonify([])

    data = list(history.find({"email": session["user"]}, {"_id": 0}))
    return jsonify(data)

# =============================
# PAGES
# =============================
@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/ide")
def ide_page():
    if not session.get("user"):
        return redirect("/")
    return render_template("ide.html")

# =============================
# HEALTH CHECK
# =============================
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "time": int(time.time())
    })

# =============================
# START
# =============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    print(f"🚀 LogicStart Microsoft rodando na porta {port}")
    app.run(host="0.0.0.0", port=port)
