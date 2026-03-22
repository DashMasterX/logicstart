# app.py - LogicStart Elite Web Integrado
from flask import Flask, render_template, request, redirect, url_for, jsonify
from executor_nodes import ExecutorNodes
from parser_novo import ParserNovo  # <-- parser atualizado
from nodes import Mostrar, Guardar

app = Flask(__name__)

# -------------------------
# Sessão simples
# -------------------------
SESSAO = {"logado": False}

# -------------------------
# Rota principal
# -------------------------
@app.route("/")
def index():
    if SESSAO.get("logado"):
        return redirect(url_for("ide"))
    return redirect(url_for("login"))

# -------------------------
# Login padrão
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        email = request.form.get("email","").strip()
        senha = request.form.get("senha","").strip()
        if (email == "admin" and senha == "1234") or (email == "" and senha == ""):
            SESSAO["logado"] = True
            return redirect(url_for("ide"))
        else:
            error = "Usuário ou senha inválidos"
    return render_template("login.html", error=error)

# -------------------------
# Login Guest
# -------------------------
@app.route("/login/guest")
def login_guest():
    SESSAO["logado"] = True
    return redirect(url_for("ide"))

# -------------------------
# IDE
# -------------------------
@app.route("/ide", methods=["GET", "POST"])
def ide():
    if not SESSAO.get("logado"):
        return redirect(url_for("login"))

    resultado = ""
    codigo = ""
    error = ""

    if request.method == "POST":
        codigo = request.form.get("codigo","").strip()
        if not codigo:
            error = "⚠ Nenhum código inserido"
        else:
            try:
                parser = ParserNovo(codigo)
                nodes = parser.parse()
                executor = ExecutorNodes(nodes)
                resultado = executor.executar()
            except Exception as e:
                resultado = f"Erro: {e}"

    return render_template("ide.html", resultado=resultado, codigo=codigo, error=error)

# -------------------------
# Logout
# -------------------------
@app.route("/logout")
def logout():
    SESSAO["logado"] = False
    return redirect(url_for("login"))

# -------------------------
# API para executar código via fetch (IDE JS)
# -------------------------
@app.route("/run", methods=["POST"])
def run():
    if not SESSAO.get("logado"):
        return jsonify({"success": False, "error":"Usuário não logado"})
    
    data = request.get_json()
    codigo = data.get("code","").strip()
    if not codigo:
        return jsonify({"success": False, "error":"Nenhum código inserido"})
    
    try:
        parser = ParserNovo(codigo)
        nodes = parser.parse()
        executor = ExecutorNodes(nodes)
        resultado = executor.executar()
        return jsonify({"success": True, "result": resultado})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# -------------------------
# API para salvar código
# -------------------------
@app.route("/save", methods=["POST"])
def save():
    if not SESSAO.get("logado"):
        return jsonify({"success": False, "error":"Usuário não logado"})
    
    data = request.get_json()
    codigo = data.get("code","").strip()
    try:
        with open("codigo_salvo.txt","w",encoding="utf-8") as f:
            f.write(codigo)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# -------------------------
# Rodar app na Square Cloud na porta 80
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
