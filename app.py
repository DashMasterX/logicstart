import os
import time
import traceback
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_session import Session
from flask_dance.contrib.google import make_google_blueprint, google
from pymongo import MongoClient
from executor import Executor  # seu executor de código Python seguro

# -----------------------------
# APP CONFIG
# -----------------------------
app = Flask(__name__)
CORS(app)

# Sessão segura
app.secret_key = os.environ.get("SECRET_KEY", "supersecreto")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["PREFERRED_URL_SCHEME"] = "https"
Session(app)

# -----------------------------
# DATABASE
# -----------------------------
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["logicstart_elite"]
users = db["users"]
history = db["history"]

# -----------------------------
# GOOGLE LOGIN
# -----------------------------
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

google_bp = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scope=["profile", "email"],
    redirect_to="pos_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

# -----------------------------
# EXECUTOR CONFIG
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
    data = request.get_json()
    email = data.get("email")
    senha = data.get("senha")

    if not email or not senha:
        return jsonify({"success": False, "error": "Preencha todos os campos"})

    user = users.find_one({"email": email, "senha": senha})
    if user:
        session["user"] = email
        session["guest"] = False
        return jsonify({"success": True})

    return jsonify({"success": False, "error": "Login inválido"})

# -----------------------------
# LOGIN GOOGLE
# -----------------------------
@app.route("/pos_login")
def pos_login():
    try:
        if not google.authorized:
            return redirect(url_for("google.login"))

        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            return f"Erro Google: {resp.text}", 500

        email = resp.json()["email"]

        if not users.find_one({"email": email}):
            users.insert_one({"email": email, "google": True})

        session["user"] = email
        session["guest"] = False

        return redirect("/ide")

    except Exception as e:
        return f"Erro login Google: {str(e)}", 500

# -----------------------------
# ENTRAR COMO CONVIDADO
# -----------------------------
@app.route("/guest")
def guest_login():
    session["user"] = "Convidado"
    session["guest"] = True
    return redirect("/ide")

# -----------------------------
# EXECUTAR CÓDIGO
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

    except Exception:
        return jsonify({
            "success": False,
            "error": "Erro ao executar",
            "debug": traceback.format_exc()
        })

# -----------------------------
# SALVAR CÓDIGO
# -----------------------------
@app.route("/save", methods=["POST"])
def save_code():
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

# -----------------------------
# HISTÓRICO
# -----------------------------
@app.route("/history")
def get_history():
    user = session.get("user")
    if not user:
        return jsonify([])
    dados = list(history.find({"email": user}, {"_id": 0}))
    return jsonify(dados)

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

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    print(f"🚀 LogicStart Elite Pro Max rodando na porta {port}")
    app.run(host="0.0.0.0", port=port)
