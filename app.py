import os
import time
import traceback

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
from pymongo import MongoClient
from executor import Executor

# -----------------------------
# CONFIG APP
# -----------------------------
app = Flask(__name__)
CORS(app)

app.secret_key = os.environ.get("SECRET_KEY", "logicstart_super_secret")

# 🔥 CONFIG ESTÁVEL (SEM BUG DE LOGIN)
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE="Lax"
)

# -----------------------------
# DATABASE (MONGO)
# -----------------------------
MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI não configurado")

client = MongoClient(MONGO_URI)
db = client["logicstart_empire"]

users = db["users"]
history = db["history"]

# -----------------------------
# GOOGLE LOGIN
# -----------------------------
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise Exception("Google OAuth não configurado")

google_bp = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    redirect_to="pos_login",
    scope=["profile", "email"]
)

app.register_blueprint(google_bp, url_prefix="/login")

# -----------------------------
# SEGURANÇA EXECUTOR
# -----------------------------
MAX_CODE_SIZE = 5000
BLOCKED = ["import os", "import sys", "open(", "exec(", "__"]

def verificar_codigo(codigo):
    if len(codigo) > MAX_CODE_SIZE:
        return False, "Código muito grande"

    for b in BLOCKED:
        if b in codigo:
            return False, f"Bloqueado: {b}"

    return True, None

# -----------------------------
# LOGIN EMAIL
# -----------------------------
@app.route("/login/email", methods=["POST"])
def login_email():
    try:
        data = request.get_json()
        email = data.get("email")
        senha = data.get("senha")

        if not email or not senha:
            return jsonify({"success": False, "error": "Preencha tudo"})

        user = users.find_one({"email": email, "senha": senha})

        if user:
            session["user"] = email
            return jsonify({"success": True})

        return jsonify({"success": False, "error": "Login inválido"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# -----------------------------
# GOOGLE LOGIN FINAL
# -----------------------------
@app.route("/pos_login")
def pos_login():
    try:
        if not google.authorized:
            return redirect(url_for("google.login"))

        resp = google.get("/oauth2/v2/userinfo")

        if not resp.ok:
            return f"Erro Google: {resp.text}"

        data = resp.json()
        email = data.get("email")

        if not email:
            return f"Erro: email não encontrado"

        # 🔥 cria usuário automático
        if not users.find_one({"email": email}):
            users.insert_one({
                "email": email,
                "google": True,
                "created_at": int(time.time())
            })

        session["user"] = email

        return redirect("/ide")

    except Exception as e:
        return f"Erro login Google: {str(e)}"

# -----------------------------
# SESSÃO
# -----------------------------
@app.route("/session")
def session_status():
    return jsonify({
        "user": session.get("user"),
        "logged": True if session.get("user") else False
    })

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -----------------------------
# EXECUTOR
# -----------------------------
@app.route("/run", methods=["POST"])
def run_code():
    start = time.time()

    try:
        data = request.get_json()
        codigo = data.get("code", "")

        ok, erro = verificar_codigo(codigo)
        if not ok:
            return jsonify({"success": False, "error": erro})

        executor = Executor(codigo)
        output = executor.executar()

        return jsonify({
            "success": True,
            "result": output,
            "time": round(time.time() - start, 4)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro ao executar",
            "debug": str(e)
        })

# -----------------------------
# SALVAR CÓDIGO
# -----------------------------
@app.route("/save", methods=["POST"])
def save_code():
    try:
        data = request.get_json()
        codigo = data.get("code")

        user = session.get("user")

        if not user:
            return jsonify({"success": False, "error": "Não logado"})

        if not codigo:
            return jsonify({"success": False, "error": "Código vazio"})

        history.insert_one({
            "email": user,
            "codigo": codigo,
            "timestamp": int(time.time())
        })

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# -----------------------------
# HISTÓRICO
# -----------------------------
@app.route("/history")
def get_history():
    try:
        user = session.get("user")

        if not user:
            return jsonify([])

        dados = list(history.find({"email": user}, {"_id": 0}))
        return jsonify(dados)

    except Exception as e:
        return jsonify([])

# -----------------------------
# FRONTEND
# -----------------------------
@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/ide")
def ide_page():
    if not session.get("user"):
        return redirect("/")
    return render_template("ide.html")

# -----------------------------
# HEALTH CHECK (IMPÉRIO 🔥)
# -----------------------------
@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "time": int(time.time())
    })

# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    print(f"🚀 LogicStart Empire rodando na porta {port}")
    app.run(host="0.0.0.0", port=port)
