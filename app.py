# app.py - LogicStart Elite Web Nível Empresa
from flask import Flask, render_template, request, redirect, url_for, jsonify
from executor_nodes import ExecutorNodes
from parser_complexo import parse_codigo  # parser próprio
from nodes import Guardar, Mostrar

app = Flask(__name__)

# -------------------------
# Sessão simples
# -------------------------
SESSAO = {"logado": False}

# -------------------------
# Rotas
# -------------------------
@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        data = request.get_json() or {}
        email = data.get("email", "").strip()
        senha = data.get("senha", "").strip()

        # Login demo
        if (email == "admin" and senha == "1234") or (email == "" and senha == ""):
            SESSAO["logado"] = True
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Usuário ou senha inválidos"})

    return render_template("login.html", error=error)

@app.route("/login/guest")
def login_guest():
    SESSAO["logado"] = True
    return redirect(url_for("ide"))

@app.route("/ide", methods=["GET", "POST"])
def ide():
    if not SESSAO.get("logado"):
        return redirect(url_for("login"))

    resultado = ""
    codigo = ""
    error = ""

    if request.method == "POST":
        data = request.get_json() or {}
        codigo = data.get("code", "").strip()

        if not codigo:
            return jsonify({"success": False, "error": "⚠ Nenhum código inserido"})

        try:
            # ----------- PARSER COMPLEXO -----------
            nodes = parse_codigo(codigo)

            # ----------- EXECUTOR NÍVEL EMPRESA -----------
            executor = ExecutorNodes(nodes)
            resultado = executor.executar()

            return jsonify({"success": True, "result": resultado})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return render_template("ide.html", resultado=resultado, codigo=codigo, error=error)

@app.route("/logout")
def logout():
    SESSAO["logado"] = False
    return redirect(url_for("login"))

# -------------------------
# Rodar app na Square Cloud porta 80
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
