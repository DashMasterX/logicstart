# app.py | LogicStart Elite - Nível Empresa Apple Pro Max / Microsoft Justos

from flask import Flask, render_template, request, redirect, url_for, session, flash
from executor import Executor
from security_pro_max import SecurityProMax
from nodes import Mostrar, Guardar
import os

# =============================
# CONFIGURAÇÃO
# =============================
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Sessões seguras

# Segurança Pro Max
security = SecurityProMax()

# =============================
# PÁGINAS PRINCIPAIS
# =============================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        if email and senha:
            session["user"] = email
            return redirect(url_for("ide"))
        else:
            flash("Preencha todos os campos", "error")
    return render_template("login.html")

@app.route("/ide", methods=["GET", "POST"])
def ide():
    if "user" not in session:
        return redirect(url_for("login"))

    resultado = ""
    codigo = ""
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        if not codigo:
            resultado = "⚠ Nenhum código inserido"
        else:
            try:
                # Verifica código com segurança
                security.verificar_codigo(codigo)

                # Converte código simples em nodes de teste (exemplo)
                nodes = [
                    Mostrar("Olá mundo"),
                    Guardar("x", "10"),
                    Mostrar("x")
                ]

                # Executa nodes
                executor = Executor(nodes)
                resultado = executor.executar()

            except Exception as e:
                resultado = f"❌ Erro: {e}"

    return render_template("ide.html", resultado=resultado, codigo=codigo)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# =============================
# RODANDO O APP
# =============================
if __name__ == "__main__":
    # Porta 80 para Square Cloud
    app.run(host="0.0.0.0", port=80)
