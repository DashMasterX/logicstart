import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Permite HTTP temporariamente (desenvolvimento)

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
from pymongo import MongoClient
import time, traceback
from executor import Executor  # Certifique-se de ter o executor seguro

# -----------------------------
# APP CONFIG
# -----------------------------
app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_secret_key")

# -----------------------------
# DATABASE (MongoDB)
# -----------------------------
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
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
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_url="/google_callback"
)
app.register_blueprint(google_bp, url_prefix="/login")

# -----------------------------
# SEGURANÇA DO EXECUTOR
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
# ROTAS DE LOGIN
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

@app.route("/login/guest")
def login_guest():
    session["user"] = f"guest_{int(time.time())}"
    session["guest"] = True
    return redirect("/ide")

@app.route("/google_callback")
def google_callback():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Erro ao acessar dados do Google", 500

    email = resp.json()["email"]

    if not users.find_one({"email": email}):
        users.insert_one({"email": email, "google": True})

    session["user"] = email
    session["guest"] = False
    return redirect("/ide")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -----------------------------
# SESSÃO
# -----------------------------
@app.route("/session")
def session_status():
    return jsonify({"user": session.get("user"), "guest": session.get("guest", False)})

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

# -----------------------------
# START SERVER
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    print(f"🚀 LogicStart Elite Pro Max rodando na porta {port}")
    app.run(host="0.0.0.0", port=port)
