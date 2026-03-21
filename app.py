from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, io, sys, time, traceback, json

from executor import Executor

app = Flask(__name__)
CORS(app)

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
# LOGIN
# -----------------------------
@app.route("/login/email", methods=["POST"])
def login_email():
    data = request.get_json()
    email, senha = data.get("email"), data.get("senha")
    if not email or not senha:
        return jsonify({"success": False, "error": "Email ou senha não preenchidos"})
    return jsonify({"success": True})

@app.route("/login/google")
def login_google():
    return jsonify({"success": True})

@app.route("/logout")
def logout():
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
def carregar_historico():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_historico(email, codigo):
    historico = carregar_historico()
    if email not in historico:
        historico[email] = []
    historico[email].append({"codigo": codigo, "timestamp": int(time.time())})
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

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
    salvar_historico(email, codigo)
    return jsonify({"success": True})

@app.route("/history/<email>")
def ver_historico(email):
    historico = carregar_historico()
    return jsonify(historico.get(email, []))

# -----------------------------
# FRONT-END
# -----------------------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    return send_from_directory(".", "index.html")

# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    print(f"🚀 LogicStart Elite iniciando na porta {port}")
    app.run(host="0.0.0.0", port=port)
