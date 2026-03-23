from flask import Flask, request, jsonify, render_template, redirect, session
from functools import wraps
import os, json, hashlib, time
from collections import defaultdict

from parser_novo import ParserNovo
from executor_nodes import ExecutorNodes

# =========================
# CONFIG
# =========================
app = Flask(__name__)

app.secret_key = "super-secret-key-fixa"

app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

USERS_FILE = "users.json"
RATE_LIMIT = defaultdict(list)

# =========================
# UTILS
# =========================
def now():
    return int(time.time())

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def user():
    return session.get("user")

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    return json.load(open(USERS_FILE))

def save_users(data):
    json.dump(data, open(USERS_FILE, "w"), indent=2)

# =========================
# SEGURANÇA
# =========================
def rate_limit():
    ip = request.remote_addr or "unknown"
    t = now()

    RATE_LIMIT[ip] = [x for x in RATE_LIMIT[ip] if t - x < 10]

    if len(RATE_LIMIT[ip]) > 30:
        return False

    RATE_LIMIT[ip].append(t)
    return True

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not user():
            return redirect("/login")
        if not rate_limit():
            return "Muitas requisições", 429
        return f(*args, **kwargs)
    return wrapper

def sanitize(code):
    proibido = ["import os","import sys","__","eval(","exec("]
    for p in proibido:
        if p in code:
            raise Exception(f"Bloqueado: {p}")
    return code

# =========================
# ROTAS WEB (ALINHADAS COM SEUS HTML)
# =========================

# INDEX (sua página inicial)
@app.route("/")
def index():
    return render_template("index.html")

# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip()
        senha = request.form.get("senha","").strip()

        users = load_users()

        if email in users and users[email]["password"] == hash_password(senha):
            session["user"] = email
            return redirect("/ide")

        return render_template("login.html", erro="Login inválido")

    return render_template("login.html")

# REGISTRO
@app.route("/register", methods=["POST"])
def register():
    email = request.form.get("email","").strip()
    senha = request.form.get("senha","").strip()

    users = load_users()

    if email in users:
        return render_template("login.html", erro="Usuário já existe")

    users[email] = {
        "password": hash_password(senha),
        "created": now()
    }

    save_users(users)

    return redirect("/login")

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# IDE (SUA PÁGINA ide.html)
@app.route("/ide")
@login_required
def ide():
    return render_template("ide.html", user=user())

# =========================
# EXECUÇÃO (LIGA COM IDE)
# =========================
@app.route("/run", methods=["POST"])
@login_required
def run():
    try:
        data = request.get_json()
        code = sanitize(data.get("code",""))

        parser = ParserNovo(code)
        nodes = parser.parse()

        executor = ExecutorNodes(nodes)
        result = executor.executar()

        return jsonify({
            "ok": True,
            "result": result
        })

    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        })

# =========================
# STATUS (DEBUG)
# =========================
@app.route("/status")
def status():
    return jsonify({
        "logado": bool(user()),
        "user": user()
    })

# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    app.run(host="0.0.0.0", port=port)
