# app.py - LogicStart Elite Web Enterprise
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from executor_nodes import ExecutorNodes
from nodes import Mostrar, Guardar

app = Flask(__name__)
app.secret_key = "logicstart-secret-key"

# -------------------------
# Rotas padrão
# -------------------------
@app.route("/")
def index():
    if session.get("logado"):
        return redirect(url_for("ide"))
    return redirect(url_for("login"))

@app.route("/login")
def login():
    return render_template("login.html")

# -------------------------
# Login via email
# -------------------------
@app.route("/login/email", methods=["POST"])
def login_email():
    data = request.get_json()
    email = data.get("email", "").strip()
    senha = data.get("senha", "").strip()

    if (email == "admin" and senha == "1234") or (email == "" and senha == ""):
        session["logado"] = True
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Usuário ou senha inválidos"})

# -------------------------
# Login Google (placeholder)
# -------------------------
@app.route("/login/google")
def login_google():
    # Aqui você pode integrar OAuth Google
    session["logado"] = True
    return redirect(url_for("ide"))

# -------------------------
# Login Guest
# -------------------------
@app.route("/login/guest")
def login_guest():
    session["logado"] = True
    return redirect(url_for("ide"))

# -------------------------
# IDE
# -------------------------
@app.route("/ide", methods=["GET", "POST"])
def ide():
    if not session.get("logado"):
        return redirect(url_for("login"))

    resultado = ""
    codigo = ""
    error = ""

    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        if not codigo:
            error = "⚠ Nenhum código inserido"
        else:
            try:
                # Para demo: nodes simples
                nodes = [
                    Guardar("x", "10"),
                    Mostrar("Olá mundo"),
                    Mostrar("x")
                ]
                executor = ExecutorNodes(nodes)
                resultado = executor.executar()
            except Exception as e:
                resultado = f"Erro: {e}"

    return render_template("ide.html", resultado=resultado, codigo=codigo, error=error)

# -------------------------
# API para executar código via fetch no IDE
# -------------------------
@app.route("/run", methods=["POST"])
def run():
    if not session.get("logado"):
        return jsonify({"success": False, "error": "Não logado"}), 401

    data = request.get_json()
    codigo = data.get("code", "").strip()
    if not codigo:
        return jsonify({"success": False, "error": "Código vazio"})

    try:
        nodes = [
            Guardar("x", "10"),
            Mostrar("Olá mundo"),
            Mostrar("x")
        ]
        executor = ExecutorNodes(nodes)
        resultado = executor.executar()
        return jsonify({"success": True, "result": resultado})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# -------------------------
# API para salvar código via fetch
# -------------------------
@app.route("/save", methods=["POST"])
def save():
    if not session.get("logado"):
        return jsonify({"success": False, "error": "Não logado"}), 401

    data = request.get_json()
    codigo = data.get("code", "").strip()
    if not codigo:
        return jsonify({"success": False, "error": "Código vazio"})

    # Aqui você pode implementar salvar em arquivo ou DB
    return jsonify({"success": True})

# -------------------------
# Logout
# -------------------------
@app.route("/logout")
def logout():
    session["logado"] = False
    return redirect(url_for("login"))

# -------------------------
# Rodar app na Square Cloud porta 80
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
