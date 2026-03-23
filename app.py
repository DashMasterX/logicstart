# app.py - LogicStart Elite FULL

from flask import Flask, render_template, request, redirect, session, jsonify
import os, json, time, hashlib
from functools import wraps
from collections import defaultdict

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "ultra-secret")

# Diretório para salvar arquivos do usuário
BASE_DIR = "data"
os.makedirs(BASE_DIR, exist_ok=True)

# Controle simples de rate-limit
RATE_LIMIT = defaultdict(list)

# =========================
# UTILITIES
# =========================

def user():
    return session.get("user_id")

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not user():
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

def user_dir():
    uid = user() or "guest"
    path = os.path.join(BASE_DIR, hashlib.md5(uid.encode()).hexdigest())
    os.makedirs(path, exist_ok=True)
    return path

def log_event(event, data=None):
    print(json.dumps({
        "time": int(time.time()),
        "user": user(),
        "event": event,
        "data": data
    }))

def sanitize_code(code):
    proibidos = ["import os", "import sys", "__", "eval(", "exec("]
    for p in proibidos:
        if p in code:
            raise Exception(f"Uso proibido: {p}")
    return code

# =========================
# LOGIN / LOGOUT
# =========================

@app.route("/")
def home():
    if user():
        return redirect("/ide")
    return redirect("/login")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/login/email", methods=["POST"])
def login_email():
    data = request.get_json()
    email = data.get("email")
    senha = data.get("senha")
    # 👇 ajuste aqui com seu banco de dados real
    if (email == "admin" and senha == "1234") or (email and senha):
        session["user_id"] = email
        log_event("login", {"tipo":"email", "email":email})
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Usuário ou senha inválidos"})

@app.route("/login/google")
def login_google():
    session["user_id"] = "google_user"
    log_event("login_google")
    return redirect("/ide")

@app.route("/login/guest")
def login_guest():
    session["user_id"] = "guest"
    log_event("login_guest")
    return redirect("/ide")

@app.route("/logout")
def logout():
    log_event("logout")
    session.clear()
    return redirect("/login")

# =========================
# IDE
# =========================

@app.route("/ide")
@login_required
def ide():
    # Aqui você pode escolher qual HTML usar
    return render_template("index.html")  # ou "ide.html" se preferir

# =========================
# ARQUIVOS
# =========================

@app.route("/files", methods=["GET"])
@login_required
def files_get():
    path = user_dir()
    arquivos = []
    for f in os.listdir(path):
        if f.endswith(".txt"):
            with open(os.path.join(path,f),"r",encoding="utf-8") as file:
                arquivos.append({"nome": f.replace(".txt",""), "codigo": file.read()})
    return jsonify({"data": arquivos})

@app.route("/files", methods=["POST"])
@login_required
def files_post():
    data = request.get_json()
    nome = data.get("nome","main")
    codigo = data.get("codigo","")
    path = user_dir()
    try:
        with open(os.path.join(path, nome+".txt"), "w", encoding="utf-8") as f:
            f.write(codigo)
        log_event("save_file", nome)
        return jsonify({"status":"ok"})
    except Exception as e:
        return jsonify({"status":"erro", "mensagem":str(e)})

@app.route("/files/<nome>", methods=["GET"])
@login_required
def files_open(nome):
    path = user_dir()
    arquivo_path = os.path.join(path, nome+".txt")
    if not os.path.exists(arquivo_path):
        return jsonify({"status":"erro","mensagem":"Arquivo não encontrado"}), 404
    with open(arquivo_path,"r",encoding="utf-8") as f:
        codigo = f.read()
    return jsonify({"nome": nome, "codigo": codigo})

@app.route("/files/<nome>", methods=["DELETE"])
@login_required
def files_delete(nome):
    path = user_dir()
    arquivo_path = os.path.join(path, nome+".txt")
    if os.path.exists(arquivo_path):
        os.remove(arquivo_path)
        log_event("delete_file", nome)
    return jsonify({"status":"ok"})

# =========================
# EXECUÇÃO
# =========================

@app.route("/executar", methods=["POST"])
@login_required
def executar():
    data = request.get_json()
    codigo = data.get("codigo","")
    try:
        codigo = sanitize_code(codigo)
        # Aqui você conecta seu parser/engine real
        resultado = f"Simulação de execução: {codigo[:50]}..."
        log_event("executar_codigo")
        return jsonify({"status":"ok","data":{"saida":resultado}})
    except Exception as e:
        return jsonify({"status":"erro","mensagem":str(e)})

# =========================
# IA
# =========================

@app.route("/ia/chat", methods=["POST"])
@login_required
def ia_chat():
    data = request.get_json()
    msg = data.get("mensagem","")
    # Aqui você conecta seu sistema IA real
    resposta = f"IA respondeu: {msg[:50]}..."
    log_event("ia_chat", msg)
    return jsonify({"status":"ok","data":resposta})

# =========================
# START
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT",80))
    app.run(host="0.0.0.0", port=port)
