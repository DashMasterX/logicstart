# app.py

from flask import Flask, request, jsonify, render_template, redirect, session
from executor_nodes import ExecutorNodes
from parser_novo import ParserNovo

import os, time, json, hashlib
from functools import wraps
from collections import defaultdict

# =========================
# CONFIG
# =========================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY","ultra-secret")

BASE_DIR = "data"
os.makedirs(BASE_DIR, exist_ok=True)

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

RATE_LIMIT = defaultdict(list)

# =========================
# SEGURANÇA
# =========================
def rate_limit():
    ip = request.remote_addr
    now = time.time()

    RATE_LIMIT[ip] = [t for t in RATE_LIMIT[ip] if now - t < 10]

    if len(RATE_LIMIT[ip]) > 20:
        return False

    RATE_LIMIT[ip].append(now)
    return True

def sanitize_code(code):
    proibidos = ["import os", "import sys", "__", "eval(", "exec("]
    for p in proibidos:
        if p in code:
            raise Exception(f"Uso proibido: {p}")
    return code

# =========================
# UTILS
# =========================
def user():
    return session.get("user_id")

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not user():
            return jsonify({"status":"erro","mensagem":"Não autenticado"})
        if not rate_limit():
            return jsonify({"status":"erro","mensagem":"Muitas requisições"})
        return f(*args, **kwargs)
    return wrapper

def user_dir():
    uid = user()
    path = os.path.join(BASE_DIR, hashlib.md5(uid.encode()).hexdigest())
    os.makedirs(path, exist_ok=True)
    return path

def log(event, data=None):
    print(json.dumps({
        "time": int(time.time()),
        "event": event,
        "user": user(),
        "data": data
    }))

# =========================
# WEB
# =========================
@app.route("/")
def index():
    return redirect("/ide" if user() else "/login")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","")
        senha = request.form.get("senha","")

        if (email=="admin" and senha=="1234") or (email=="" and senha==""):
            session["user_id"] = email or "guest"
            log("login", email)
            return redirect("/ide")

    return render_template("login.html")

@app.route("/logout")
def logout():
    log("logout")
    session.clear()
    return redirect("/login")

@app.route("/ide")
def ide():
    if not user():
        return redirect("/login")
    return render_template("index.html")

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

        parser = ParserNovo(codigo)
        nodes = parser.parse()

        executor = ExecutorNodes(nodes)
        resultado = executor.executar()

        salvar_historico(codigo)

        log("run", {"len": len(codigo)})

        return jsonify({
            "status":"ok",
            "data":{"saida":resultado}
        })

    except Exception as e:
        log("erro", str(e))
        return jsonify({
            "status":"erro",
            "mensagem":str(e)
        })

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
                arquivos.append({
                    "nome":f.replace(".txt",""),
                    "codigo":file.read()
                })

    return jsonify({"data":arquivos})

@app.route("/files", methods=["POST"])
@login_required
def files_post():
    data = request.get_json()

    nome = data.get("nome","main")
    codigo = data.get("codigo","")

    path = user_dir()

    try:
        with open(os.path.join(path, nome+".txt"),"w",encoding="utf-8") as f:
            f.write(codigo)

        log("save", nome)

        return jsonify({"status":"ok"})

    except Exception as e:
        return jsonify({"status":"erro","mensagem":str(e)})

# =========================
# HISTÓRICO
# =========================
def salvar_historico(codigo):
    path = user_dir()
    file = os.path.join(path,"history.log")

    with open(file,"a",encoding="utf-8") as f:
        f.write(f"{int(time.time())}|{codigo[:200]}\n")

@app.route("/history")
@login_required
def history():
    path = user_dir()
    file = os.path.join(path,"history.log")

    if not os.path.exists(file):
        return jsonify([])

    with open(file,encoding="utf-8") as f:
        linhas = f.readlines()[-20:]

    return jsonify(linhas)

# =========================
# IA
# =========================
@app.route("/ia/chat", methods=["POST"])
@login_required
def ia_chat():
    data = request.get_json()
    msg = data.get("mensagem","")

    resposta = openai_call(msg)

    return jsonify({"status":"ok","data":resposta})

@app.route("/ia/gerar", methods=["POST"])
@login_required
def ia_gerar():
    data = request.get_json()
    pedido = data.get("pedido","")

    prompt = f"Crie código na linguagem LogicStart:\n{pedido}"
    resposta = openai_call(prompt)

    return jsonify({"status":"ok","data":resposta})

# =========================
# OPENAI
# =========================
def openai_call(prompt):
    if not OPENAI_KEY:
        return "⚠ Configure OPENAI_API_KEY"

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7
        )

        return res.choices[0].message.content

    except Exception as e:
        return f"Erro IA: {e}"

# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT",80))
    app.run(host="0.0.0.0", port=port)
