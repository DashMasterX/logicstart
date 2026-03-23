# app.py - LogicStart Elite IDE FINAL

from flask import Flask, request, jsonify, render_template, redirect, session
from pymongo import MongoClient
from datetime import datetime
import os, hashlib, json

# ================= CONFIG =================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "ultra-secret")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

mongo = MongoClient(MONGO_URI)
db = mongo["logicstart"]
files_col = db["files"]
logs_col = db["logs"]

# ================= UTILS =================
def user_id():
    return session.get("user_id", "guest")

def ok(data=None):
    return jsonify({"status":"ok","data":data})

def erro(msg, code=400):
    return jsonify({"status":"erro","mensagem":msg}), code

def log_event(acao, detalhe=""):
    logs_col.insert_one({
        "user_id": user_id(),
        "acao": acao,
        "detalhe": detalhe,
        "timestamp": datetime.utcnow()
    })

# ================= LOGIN =================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","")
        senha = request.form.get("senha","")
        # login simples de demo
        if (email=="admin" and senha=="1234") or (email=="" and senha==""):
            session["user_id"] = email or "guest"
            log_event("login", email)
            return redirect("/ide")
        return render_template("login.html", error="Usuário ou senha inválidos")
    return render_template("login.html", error="")

@app.route("/logout")
def logout():
    log_event("logout")
    session.clear()
    return redirect("/login")

# ================= IDE =================
@app.route("/ide")
def ide():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("ide.html")

# ================= ARQUIVOS =================
@app.route("/files", methods=["GET"])
def listar_arquivos():
    arquivos = list(files_col.find({"user_id": user_id()}, {"_id":0}))
    return ok(arquivos)

@app.route("/files", methods=["POST"])
def salvar_arquivo():
    data = request.get_json()
    nome = data.get("nome")
    codigo = data.get("codigo","")
    if not nome: return erro("Nome do arquivo obrigatório")
    files_col.update_one(
        {"user_id": user_id(), "nome": nome},
        {"$set":{"codigo":codigo,"updated_at":datetime.utcnow()}},
        upsert=True
    )
    log_event("salvar_arquivo", nome)
    return ok(f"Arquivo '{nome}' salvo!")

@app.route("/files/<nome>", methods=["GET"])
def abrir_arquivo(nome):
    arq = files_col.find_one({"user_id": user_id(), "nome": nome}, {"_id":0})
    if not arq: return erro("Arquivo não encontrado", 404)
    return ok(arq)

@app.route("/files/<nome>", methods=["DELETE"])
def deletar_arquivo(nome):
    files_col.delete_one({"user_id": user_id(), "nome": nome})
    log_event("deletar_arquivo", nome)
    return ok(f"Arquivo '{nome}' deletado")

# ================= EXECUÇÃO =================
@app.route("/executar", methods=["POST"])
def executar():
    data = request.get_json()
    codigo = data.get("codigo","")
    try:
        from executor_nodes import ExecutorNodes
        from parser_novo import ParserNovo
        parser = ParserNovo(codigo)
        nodes = parser.parse()
        executor = ExecutorNodes(nodes)
        resultado = executor.executar()
        log_event("executar_codigo")
        return ok({"saida":resultado})
    except Exception as e:
        log_event("erro_execucao", str(e))
        return erro(str(e), 500)

# ================= IA =================
@app.route("/ia/chat", methods=["POST"])
def ia_chat():
    data = request.get_json()
    mensagem = data.get("mensagem","")
    try:
        from IA import IA
        ia = IA(api_key=OPENAI_KEY)
        resposta = ia.perguntar(user_id(), mensagem)
        log_event("ia_chat", mensagem)
        return ok(resposta)
    except Exception as e:
        return erro(f"Erro IA: {e}", 500)

@app.route("/ia/gerar", methods=["POST"])
def ia_gerar():
    data = request.get_json()
    pedido = data.get("pedido","")
    try:
        from IA import IA
        ia = IA(api_key=OPENAI_KEY)
        codigo = ia.gerar(user_id(), pedido)
        log_event("ia_gerar", pedido)
        return ok(codigo)
    except Exception as e:
        return erro(f"Erro IA: {e}", 500)

@app.route("/ia/corrigir", methods=["POST"])
def ia_corrigir():
    data = request.get_json()
    codigo = data.get("codigo","")
    try:
        from IA import IA
        ia = IA(api_key=OPENAI_KEY)
        novo = ia.corrigir(user_id(), codigo)
        log_event("ia_corrigir")
        return ok(novo)
    except Exception as e:
        return erro(f"Erro IA: {e}", 500)

@app.route("/ia/explicar", methods=["POST"])
def ia_explica():
    data = request.get_json()
    codigo = data.get("codigo","")
    try:
        from IA import IA
        ia = IA(api_key=OPENAI_KEY)
        texto = ia.explicar(user_id(), codigo)
        log_event("ia_explicar")
        return ok(texto)
    except Exception as e:
        return erro(f"Erro IA: {e}", 500)

# ================= LOGS =================
@app.route("/logs", methods=["GET"])
def logs():
    registros = list(logs_col.find({"user_id": user_id()}, {"_id":0}).sort("timestamp",-1).limit(50))
    return ok(registros)

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 LogicStart Elite IDE rodando na porta {port}")
    app.run(host="0.0.0.0", port=port)
