from flask import Flask, render_template, request, redirect, url_for, jsonify
from executor_nodes import ExecutorNodes
from nodes import Mostrar, Guardar

app = Flask(__name__, template_folder="templates")  # Certifique-se que a pasta 'templates' existe

# -------------------------
# Sessão simples
# -------------------------
SESSAO = {"logado": False}

# -------------------------
# Rota inicial
# -------------------------
@app.route("/")
def index():
    return redirect(url_for("login"))

# -------------------------
# Login
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()
        if (email == "admin" and senha == "1234") or (email == "" and senha == ""):
            SESSAO["logado"] = True
            return redirect(url_for("ide"))
        else:
            error = "Usuário ou senha inválidos"
    return render_template("login.html", error=error)

# -------------------------
# IDE
# -------------------------
@app.route("/ide")
def ide():
    if not SESSAO.get("logado"):
        return redirect(url_for("login"))
    return render_template("ide.html", resultado="", codigo="", error="")

# -------------------------
# Rota para executar código
# -------------------------
@app.route("/run", methods=["POST"])
def run_code():
    if not SESSAO.get("logado"):
        return jsonify({"success": False, "error": "Não logado"})

    data = request.get_json()
    codigo = data.get("code", "").strip()

    if not codigo:
        return jsonify({"success": False, "error": "Nenhum código fornecido"})

    try:
        # Aqui você pode colocar o seu parser real
        # Por enquanto, exemplo de nodes simples:
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
# Logout
# -------------------------
@app.route("/logout")
def logout():
    SESSAO["logado"] = False
    return redirect(url_for("login"))

# -------------------------
# Rodar app no Square Cloud porta 80
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
