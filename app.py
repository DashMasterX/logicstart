from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import io
import sys
import time
import traceback
import json

app = Flask(__name__)
CORS(app)

# Diretórios
SAVE_DIR = "codigos_salvos"
HISTORY_FILE = os.path.join(SAVE_DIR, "historico.json")
os.makedirs(SAVE_DIR, exist_ok=True)

# -------------------------
# Segurança
# -------------------------
MAX_CODE_SIZE = 5000
BLOCKED_KEYWORDS = ["import os", "import sys", "open(", "exec(", "__"]

def verificar_codigo(codigo):
    if len(codigo) > MAX_CODE_SIZE:
        return False, "Código muito grande"
    for palavra in BLOCKED_KEYWORDS:
        if palavra in codigo:
            return False, f"Código bloqueado: contém '{palavra}'"
    return True, None

# -------------------------
# Login
# -------------------------
@app.route("/login/email", methods=["POST"])
def login_email():
    data = request.get_json()
    email = data.get("email")
    senha = data.get("senha")
    if not email or not senha:
        return jsonify({"success": False, "error": "Email ou senha não preenchidos"})
    return jsonify({"success": True})

@app.route("/login/google")
def login_google():
    return jsonify({"success": True})

@app.route("/logout")
def logout():
    return jsonify({"success": True})

# -------------------------
# Execução de código
# -------------------------
@app.route("/run", methods=["POST"])
def run_code():
    start_time = time.time()
    try:
        data = request.get_json()
        codigo = data.get("code", "")
        ok, msg = verificar_codigo(codigo)
        if not ok:
            return jsonify({"success": False, "error": msg})

        buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer
        try:
            exec(codigo, {"__builtins__": {}})
        finally:
            sys.stdout = old_stdout

        output = buffer.getvalue()
        execution_time = round(time.time() - start_time, 4)
        return jsonify({"success": True, "result": output if output else "✔ Executado com sucesso", "time": execution_time})
    except Exception:
        erro = traceback.format_exc()
        return jsonify({"success": False, "error": "Erro na execução", "debug": erro})

# -------------------------
# Salvar código e histórico
# -------------------------
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

# -------------------------
# Front-end
# -------------------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    return send_from_directory(".", "index.html")

# -------------------------
# Start
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    print(f"🚀 LogicStart IDE profissional iniciando na porta {port}")
    app.run(host="0.0.0.0", port=port)
