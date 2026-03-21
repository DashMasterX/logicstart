from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
from pymongo import MongoClient
import os, time, traceback, json
from executor import Executor

# -----------------------------
# CONFIGURAÇÕES DO FLASK
# -----------------------------
app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)

# -----------------------------
# EXECUTOR
# -----------------------------
SAVE_DIR = "codigos_salvos"
HISTORY_FILE = os.path.join(SAVE_DIR, "historico.json")
os.makedirs(SAVE_DIR, exist_ok=True)

MAX_CODE_SIZE = 5000
BLOCKED_KEYWORDS = ["import os", "import sys", "open(", "exec(", "__"]

def verificar_codigo(codigo):
    if len(codigo) > MAX_CODE_SIZE:
        return False, "Código muito grande"
    for palavra in BLOCKED_KEYWORDS:
        if palavra in codigo:
            return False, f"Código bloqueado: contém '{palavra}'"
    return True, None

# -----------------------------
# MONGODB (via variáveis de ambiente)
# -----------------------------
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['logicstart_elite']
users_collection = db['users']
history_collection = db['history']

def verificar_usuario(email, senha):
    return users_collection.find_one({"email": email, "senha": senha})

# -----------------------------
# GOOGLE OAUTH (via variáveis de ambiente)
# -----------------------------
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

blueprint = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    redirect_to="login_google_redirect"
)
app.register_blueprint(blueprint, url_prefix="/login")

# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login/email", methods=["POST"])
def login_email():
    data = request.get_json()
    email, senha = data.get("email"), data.get("senha")
    if not email or not senha:
        return jsonify({"success": False, "error": "Email ou senha não preenchidos"})
    user = verificar_usuario(email, senha)
    if user:
        session['user'] = email
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Email ou senha incorretos"})

@app.route("/login/google")
def login_google_redirect():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    session['user'] = resp.json()['email']
    return jsonify({"success": True, "email": session['user']})

@app.route("/logout")
def logout():
    session.pop('user', None)
    return jsonify({"success": True})

# -----------------------------
# EXECUÇÃO DE CÓDIGO
# -----------------------------
@app.route("/run", methods=["POST"])
def run_code():
    start_time = time.time()
    try:
        data = request.get_json()
        codigo = data.get("code", "")
        ok, msg = verificar_codigo(codigo)
        if not ok:
            return jsonify({"success": False, "error": msg})

        executor = Executor(codigo)
        output = executor.executar()
        execution_time = round(time.time() - start_time, 4)
        return jsonify({"success": True, "result": output, "time": execution_time})
    except Exception:
        erro = traceback.format_exc()
        return jsonify({"success": False, "error": "Erro na execução", "debug": erro})

# -----------------------------
# SALVAR E HISTÓRICO
# -----------------------------
def salvar_historico_mongo(email, codigo):
    history_collection.insert_one({"email": email, "codigo": codigo, "timestamp": int(time.time())})

@app.route("/save", methods=["POST"])
def save_code():
    data = request.get_json()
    codigo = data.get("code", "")
    email = data.get("email", "anonimo")
    if not codigo:
        return jsonify({"success": False, "error": "Código vazio"})
    safe_email = email.replace("@", "_at_").replace(".", "_")
    filename = os.path.join(SAVE_DIR, f"{safe_email}_{int(time.time())}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(codigo)
    salvar_historico_mongo(email, codigo)
    return jsonify({"success": True})

@app.route("/history/<email>")
def ver_historico(email):
    historico = list(history_collection.find({"email": email}, {"_id": 0}))
    return jsonify(historico)

# -----------------------------
# FRONT-END
# -----------------------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    return render_template("index.html")

# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    print(f"🚀 LogicStart Elite iniciando na porta {port}")
    app.run(host="0.0.0.0", port=port)
