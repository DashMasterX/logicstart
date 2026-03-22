# app.py - LogicStart Elite Pro Max Web
from flask import Flask, render_template, request, redirect, url_for
from executor_nodes import ExecutorNodes
from security_pro_max import SecurityProMax
from nodes import Mostrar, Guardar

app = Flask(__name__)

# =========================
# Segurança Pro Max
# =========================
security = SecurityProMax()

# =========================
# Usuário logado (simples, para demo)
# =========================
SESSAO = {"logado": False}

# =========================
# Rotas
# =========================
@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()
        if email == "admin" and senha == "1234":
            SESSAO["logado"] = True
            return redirect(url_for("ide"))
        elif email == "" and senha == "":
            # Guest login
            SESSAO["logado"] = True
            return redirect(url_for("ide"))
        else:
            error = "Usuário ou senha inválidos"
    return render_template("login.html", error=error)

@app.route("/ide", methods=["GET", "POST"])
def ide():
    if not SESSAO.get("logado"):
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
                # Verifica segurança Pro Max
                security.verificar_codigo(codigo)

                # Para demo: converte em nodes simples
                # Aqui você pode substituir pelo seu parser real
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

@app.route("/logout")
def logout():
    SESSAO["logado"] = False
    return redirect(url_for("login"))

# =========================
# Rodar app na Square Cloud porta 80
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
